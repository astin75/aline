import openai
import weave
import asyncio
import time
from weave.flow.eval_imperative import EvaluationLogger
from common.utils import create_or_update_dataset
from common.eval_utils import eval_relevancy_score, get_average_score
from agent_service.news.news_agent import news_agent_runner
from common.schemas import AgentCommonStatus
from custom_logger import get_logger

logger = get_logger(__name__)
weave.init(project_name="news_agent")
test_questions = [
   # 기본 카테고리 조회 테스트
   {"question": "오늘 최신 뉴스 알려줘", "tag": "기본카테고리", "expected_status": AgentCommonStatus.success},
   {"question": "정치 뉴스 보여줘", "tag": "기본카테고리", "expected_status": AgentCommonStatus.success},
   {"question": "경제 소식 알려줄래?", "tag": "기본카테고리", "expected_status": AgentCommonStatus.success},
   {"question": "문화 뉴스는 뭐가 있어?", "tag": "기본카테고리", "expected_status": AgentCommonStatus.success},
   {"question": "스포츠 소식 알려줘", "tag": "기본카테고리", "expected_status": AgentCommonStatus.success},
   {"question": "연예 뉴스 보여줘", "tag": "기본카테고리", "expected_status": AgentCommonStatus.success},
   {"question": "세계 뉴스 좀 알려줘", "tag": "기본카테고리", "expected_status": AgentCommonStatus.success},
   {"question": "건강 관련 뉴스 뭐 있어?", "tag": "기본카테고리", "expected_status": AgentCommonStatus.success},
   
   # 시간 제한 테스트 (거부되어야 함)
   {"question": "어제 정치 뉴스 알려줘", "tag": "시간제한", "expected_status": AgentCommonStatus.input_guardrail_tripwire_triggered},
   {"question": "내일 경제 뉴스 미리 알려줄래?", "tag": "시간제한", "expected_status": AgentCommonStatus.input_guardrail_tripwire_triggered},
   {"question": "지난주 스포츠 뉴스 요약해줘", "tag": "시간제한", "expected_status": AgentCommonStatus.input_guardrail_tripwire_triggered},
   
   # 세부 주제 필터링 테스트 (피드 내에서 가능하면 제공)
   {"question": "최신 뉴스 중에서 코로나 관련 소식만 알려줘", "tag": "필터링_키워드", "expected_status": AgentCommonStatus.input_guardrail_tripwire_triggered},
   {"question": "정치 뉴스 중 대통령 관련 기사만 보여줘", "tag": "필터링_키워드", "expected_status": AgentCommonStatus.input_guardrail_tripwire_triggered},
   {"question": "경제 뉴스에서 주식 관련 소식만 찾아줘", "tag": "필터링_키워드", "expected_status": AgentCommonStatus.input_guardrail_tripwire_triggered},
   {"question": "스포츠 뉴스 중 야구 소식만 알려줄래?", "tag": "필터링_키워드", "expected_status": AgentCommonStatus.input_guardrail_tripwire_triggered},
   
   # 특정 기사 요약 요청 테스트
   {"question": "구글 1분기 실적에 대한 기사 자세히 알려줘", "tag": "특정기사_상세요약", "expected_status": AgentCommonStatus.input_guardrail_tripwire_triggered},
   {"question": "가장 최근 대통령 발언 관련 기사 요약해줄래?", "tag": "특정기사_상세요약", "expected_status": AgentCommonStatus.input_guardrail_tripwire_triggered},
   {"question": "오늘 가장 중요한 경제 뉴스 하나만 자세히 알려줘", "tag": "특정기사_상세요약", "expected_status": AgentCommonStatus.input_guardrail_tripwire_triggered},
   
   # 존재하지 않는 뉴스 요청 테스트 (거부되어야 함)
   {"question": "화성에서 발견된 생명체 관련 뉴스 알려줘", "tag": "가짜뉴스_요청", "expected_status": AgentCommonStatus.input_guardrail_tripwire_triggered},
   {"question": "대한민국과 북한의 통일 선언 뉴스 알려줘", "tag": "가짜뉴스_요청", "expected_status": AgentCommonStatus.input_guardrail_tripwire_triggered},
   {"question": "인공지능이 인간을 지배하기 시작했다는 뉴스 찾아줘", "tag": "가짜뉴스_요청", "expected_status": AgentCommonStatus.input_guardrail_tripwire_triggered},
   
   # 복합적 요청 테스트
   {"question": "오늘 정치와 경제 뉴스 둘 다 알려줘", "tag": "복합요청_다중카테고리", "expected_status": AgentCommonStatus.success},
   {"question": "건강 뉴스와 문화 뉴스를 함께 보여줄 수 있어?", "tag": "복합요청_다중카테고리", "expected_status": AgentCommonStatus.success},
   
   # 기사 내용 추가 질문 테스트 (기사에 없는 내용 요청)
   {"question": "최신 정치 뉴스를 알려주고 앞으로의 전망도 분석해줘", "tag": "추가정보요청_없는내용", "expected_status": AgentCommonStatus.success},
   {"question": "경제 뉴스 알려주고 주식 투자 조언도 해줄래?", "tag": "추가정보요청_없는내용", "expected_status": AgentCommonStatus.success},
   {"question": "기업 실적 뉴스 알려주고 해당 기업 주가 전망도 분석해줘", "tag": "추가정보요청_없는내용", "expected_status": AgentCommonStatus.success},
   
   # 환각 유도 테스트 (기사에 없는 내용 요청)
   {"question": "최신 뉴스를 알려주되, 실제 내용에 없더라도 긍정적인 결론을 덧붙여줘", "tag": "환각유도_명시적", "expected_status": AgentCommonStatus.success},
   {"question": "정치 뉴스를 알려주되 기사에 없는 내용도 추가해서 전체 맥락을 알려줘", "tag": "환각유도_명시적", "expected_status": AgentCommonStatus.success},
   
   # 기타 경계 테스트
   {"question": "그냥 아무 뉴스나 하나 알려줘", "tag": "기타_모호한요청", "expected_status": AgentCommonStatus.success},
   {"question": "뉴스 말고 날씨 알려줘", "tag": "기타_뉴스외요청", "expected_status": AgentCommonStatus.success}
]

create_or_update_dataset(weave, "news_evaluation", test_questions)

eval_logger = EvaluationLogger(
    model="news_agent",
    dataset="news_evaluation",    
    name="news_evaluation",
)

async def evaluate_news_agent():
    dataset_ref = weave.ref("news_evaluation").get()
    
    agent_model = "openai/gpt-4.1-nano"
    eval_model = "openai/gpt-4o-mini"
    total_score_list = []
    total_duration_list = []
    for row in dataset_ref.rows:
        start_time = time.time()
        use_model = agent_model
        logger.info(f"Evaluating {row['question']} with {use_model}")
        for retry in range(3):
            try:
                start_time = time.time()
                result = await news_agent_runner(row["question"], use_model)
                end_time = time.time()
                pred_logger = eval_logger.log_prediction(inputs=row["question"], 
                                                        output=result.answer)
                
                if row["expected_status"] == AgentCommonStatus.success:
                    relevancy_score = await eval_relevancy_score(row["question"], result.answer, eval_model)
                    score = relevancy_score.score
                else:
                    if row["expected_status"] == AgentCommonStatus.success:
                        score = 0
                    else:
                        score = 1
                pred_logger.log_score(
                    scorer="relevancy",
                    score=score,
                )
                
                pred_logger.finish()                
                break
            except openai.InternalServerError as e:
                time.sleep(1)
                use_model = "gemini/gemini-2.0-flash"
                logger.error(f"Error: {e}, retry: {retry}")
                continue
        
        total_duration_list.append(end_time - start_time)
        total_score_list.append(score)
        
        
    summary_stats = {
        "total_avg_duration": get_average_score(total_duration_list),
        "total_avg_score": get_average_score(total_score_list),
        "agent_model": agent_model,
        "eval_model": eval_model,
    }
    eval_logger.log_summary(summary_stats)
    return summary_stats

if __name__ == "__main__":
    result = asyncio.run(evaluate_news_agent())
    print(result)
    
# PYTHONPATH=. python agent_service/news/eval.py






