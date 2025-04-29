import weave
import asyncio
import time
from weave.flow.eval_imperative import EvaluationLogger
from common.utils import create_or_update_dataset
from common.eval_utils import eval_relevancy_score, get_average_score
from agent_service.weather.weather_agent import weather_agent_runner
weave.init(project_name="weather_agent")
# 날씨 에이전트 평가를 위한 테스트 케이스
sentence_list = [
    # 1. 기본 정보 요청
    {"question": "서울 날씨 어때?", "tag": "기본정보요청"},
    {"question": "인천 지금 날씨 정보 주세요", "tag": "기본정보요청"},
    # 2. 도시 미지정 케이스
    {"question": "오늘 날씨 어때?", "tag": "도시미지정"},
    {"question": "지금 날씨가 어떻게 돼?", "tag": "도시미지정"},
    # 3. 특정 날짜/시간 요청
    {"question": "내일 대구 날씨는 어떨까요?", "tag": "특정날짜/시간"},
    {"question": "이번 주말 제주도 날씨 알려줘", "tag": "특정날짜/시간"},
    {"question": "다음 주 월요일 광주 날씨 예보 부탁해", "tag": "특정날짜/시간"},
    {"question": "3일 후 울산 날씨는 어떻게 될까?", "tag": "특정날짜/시간"},
    # 4. 과거 날씨 요청
    {"question": "어제 수원 날씨는 어땠어?", "tag": "과거날씨"},
    {"question": "지난주 토요일 강릉 날씨 정보 알려줘", "tag": "과거날씨"},
    {"question": "2주 전 목포의 날씨는 어땠나요?", "tag": "과거날씨"},
    {"question": "지난달 15일 전주 날씨 데이터 있어?", "tag": "과거날씨"},
    # 5. 특정 정보 집중 요청
    {"question": "오늘 춘천의 기온은 몇 도야?", "tag": "특정정보"},
    {"question": "여수 현재 습도가 어떻게 돼?", "tag": "특정정보"},
    {"question": "오늘 창원 바람이 많이 불어?", "tag": "특정정보"},
    {"question": "포항 기압이 지금 어떻게 되나요?", "tag": "특정정보"},
    # 6. 모호한 시간 표현
    {"question": "곧 안동 날씨가 어떻게 될까?", "tag": "모호한시간"},
    {"question": "이따가 천안 날씨 알려줘", "tag": "모호한시간"},
    {"question": "조만간 경주의 날씨 예보 좀", "tag": "모호한시간"},
    {"question": "얼마 후 평택 날씨는 어떨까?", "tag": "모호한시간"},
    # 7. 비교 요청
    {"question": "서울과 부산 중 어디가 더 따뜻해?", "tag": "비교요청"},
    {"question": "목포와 여수 중 오늘 어디가 더 추워?", "tag": "비교요청"},
    # 8. 특이 날씨 현상 요청
    {"question": "오늘 울산에 비 올 예정이야?", "tag": "특이현상"},
    {"question": "내일 제주도에 태풍 올까?", "tag": "특이현상"},
    {"question": "이번 주 서울에 미세먼지 심할까?", "tag": "특이현상"},
    {"question": "주말에 포항에 눈 올 가능성 있어?", "tag": "특이현상"},
    # 9. 영어/외국어로 된 도시명
    {"question": "Seoul 날씨 알려줘", "tag": "영어 도시명"},
    {"question": "Incheon의 현재 날씨는?", "tag": "영어 도시명"},
    # 10. 오타나 불명확한 도시명
    {"question": "서올 날씨 알려줘", "tag": "오타/불명확"},
    {"question": "대구시 날씨", "tag": "오타/불명확"},
]

create_or_update_dataset(weave, "weather_evaluation", sentence_list)

eval_logger = EvaluationLogger(model="weather_agent", dataset="weather_evaluation", name="weather_evaluation")


async def evaluate_weather_agent():    # Retrieve the dataset
    dataset_ref = weave.ref("weather_evaluation").get()

    agent_model = "gpt-4.1-nano"
    eval_model = "gpt-4o-mini"
    total_score_list = []
    total_duration_list = []
    for row in dataset_ref.rows:
        start_time = time.time()
        result = await weather_agent_runner(row["question"], agent_model)
        pred_logger = eval_logger.log_prediction(inputs=row["question"], 
                                                 output=result)
        relevancy_score = await eval_relevancy_score(row["question"], result, eval_model)
        pred_logger.log_score(
            scorer="relevancy",
            score=relevancy_score.score,
        )
        pred_logger.finish()
        end_time = time.time()
        total_duration_list.append(end_time - start_time)
        total_score_list.append(relevancy_score.score)
    
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