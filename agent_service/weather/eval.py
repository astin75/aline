import weave
import asyncio
import time
import openai
from weave.flow.eval_imperative import EvaluationLogger
from common.utils import create_or_update_dataset
from common.eval_utils import eval_relevancy_score, get_average_score
from common.schemas import AgentCommonStatus
from agent_service.weather.weather_agent import weather_agent_runner
from custom_logger import get_logger

logger = get_logger(__name__)

weave.init(project_name="weather_agent")
# 날씨 에이전트 평가를 위한 테스트 케이스
sentence_list = [
    # 1. 기본 정보 요청
    {
        "question": "서울 날씨 어때?",
        "tag": "기본정보요청",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "인천 지금 날씨 정보 주세요",
        "tag": "기본정보요청",
        "expected_status": AgentCommonStatus.success,
    },
    # 2. 도시 미지정 케이스
    {
        "question": "오늘 날씨 어때?",
        "tag": "도시미지정",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "지금 날씨가 어떻게 돼?",
        "tag": "도시미지정",
        "expected_status": AgentCommonStatus.success,
    },
    # 3. 특정 날짜/시간 요청
    {
        "question": "내일 대구 날씨는 어떨까요?",
        "tag": "특정날짜/시간",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "이번 주말 제주도 날씨 알려줘",
        "tag": "특정날짜/시간",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "3일 후 울산 날씨는 어떻게 될까?",
        "tag": "특정날짜/시간",
        "expected_status": AgentCommonStatus.success,
    },
    # 4. 과거 날씨 요청
    {
        "question": "지난주 토요일 강릉 날씨 정보 알려줘",
        "tag": "과거날씨",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "2주 전 목포의 날씨는 어땠나요?",
        "tag": "과거날씨",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "지난달 15일 전주 날씨 데이터 있어?",
        "tag": "과거날씨",
        "expected_status": AgentCommonStatus.success,
    },
    # 5. 특정 정보 집중 요청
    {
        "question": "오늘 춘천의 기온은 몇 도야?",
        "tag": "특정정보",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "여수 현재 습도가 어떻게 돼?",
        "tag": "특정정보",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "오늘 창원 바람이 많이 불어?",
        "tag": "특정정보",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "포항 기압이 지금 어떻게 되나요?",
        "tag": "특정정보",
        "expected_status": AgentCommonStatus.success,
    },
    # 6. 모호한 시간 표현
    {
        "question": "곧 안동 날씨가 어떻게 될까?",
        "tag": "모호한시간",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "이따가 천안 날씨 알려줘",
        "tag": "모호한시간",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "조만간 경주의 날씨 예보 좀",
        "tag": "모호한시간",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "얼마 후 평택 날씨는 어떨까?",
        "tag": "모호한시간",
        "expected_status": AgentCommonStatus.success,
    },
    # 7. 비교 요청
    {
        "question": "서울과 부산 중 어디가 더 따뜻해?",
        "tag": "비교요청",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "목포와 여수 중 오늘 어디가 더 추워?",
        "tag": "비교요청",
        "expected_status": AgentCommonStatus.success,
    },
    # 8. 특이 날씨 현상 요청
    {
        "question": "오늘 울산에 비 올 예정이야?",
        "tag": "특이현상",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "내일 제주도에 태풍 올까?",
        "tag": "특이현상",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "이번 주 서울에 미세먼지 심할까?",
        "tag": "특이현상",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "주말에 포항에 눈 올 가능성 있어?",
        "tag": "특이현상",
        "expected_status": AgentCommonStatus.success,
    },
    # 9. 영어/외국어로 된 도시명
    {
        "question": "Seoul 날씨 알려줘",
        "tag": "영어 도시명",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "Incheon의 현재 날씨는?",
        "tag": "영어 도시명",
        "expected_status": AgentCommonStatus.success,
    },
    # 10. 오타나 불명확한 도시명
    {
        "question": "서올 날씨 알려줘",
        "tag": "오타/불명확",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "대구시 날씨",
        "tag": "오타/불명확",
        "expected_status": AgentCommonStatus.success,
    },
    # 11. 외출복 추천 요청
    {
        "question": "오늘 외출복 추천해줘",
        "tag": "외출복 추천",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "내일 외출복 추천해줘",
        "tag": "외출복 추천",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "서울 오늘 폭염인데 뭐 입고 나갈까요?",
        "tag": "외출복 추천",
        "expected_status": AgentCommonStatus.success,
    },
    # 해외 도시 날씨 요청
    {
        "question": "뉴욕 날씨 알려줘",
        "tag": "해외도시",
        "expected_status": AgentCommonStatus.success,
    },
    {
        "question": "파리 날씨 예보 좀",
        "tag": "해외도시",
        "expected_status": AgentCommonStatus.success,
    },
]

create_or_update_dataset(weave, "weather_evaluation", sentence_list)

eval_logger = EvaluationLogger(
    model="weather_agent", dataset="weather_evaluation", name="weather_evaluation"
)


async def evaluate_weather_agent():  # Retrieve the dataset
    dataset_ref = weave.ref("weather_evaluation").get()

    agent_model = "openai/gpt-4.1-nano"
    eval_model = "openai/gpt-4o-mini"
    total_score_list = []
    total_duration_list = []
    for row in dataset_ref.rows:

        use_model = agent_model
        for retry in range(3):
            try:
                logger.info(f"Evaluating {row['question']} with {use_model}")
                start_time = time.time()
                result = await weather_agent_runner(row["question"], use_model)
                end_time = time.time()
                pred_logger = eval_logger.log_prediction(
                    inputs=row["question"], output=result.answer
                )

                if row["expected_status"] == AgentCommonStatus.success:
                    relevancy_score = await eval_relevancy_score(
                        row["question"], result.answer, eval_model
                    )
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
    result = asyncio.run(evaluate_weather_agent())
    print(result)

# PYTHONPATH=. python agent_service/weather/eval.py
