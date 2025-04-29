# 날씨 에이전트 파일 구조

## `agent_service/weather/eval.py`
- 날씨 에이전트의 성능을 평가하는 평가 스크립트
- 다양한 테스트 케이스(sentence_list)를 포함
- ContextRelevancyScorer를 사용하여 응답의 관련성 평가
- weave를 사용하여 평가 결과 추적 및 저장

## `agent_service/weather/weather_agent.py`
- 날씨 정보를 제공하는 메인 에이전트 구현
- OpenWeatherMap API를 활용한 날씨 데이터 조회
- 주요 기능:
  - 현재 날씨 조회 (`get_current_weather`)
  - 특정 시간대 날씨 조회 (`get_weather_with_time`)
  - 도시명 검증 (`check_correct_city_name`)
- 한국어 도시명 가드레일 구현
- weave를 통한 에이전트 추적 설정

## `agent_service/weather/prompts.py`
- 날씨 에이전트 관련 프롬프트 정의
- 두 가지 주요 프롬프트:
  - 날씨 정보 제공을 위한 메인 프롬프트 (`get_weather_prompt`)
  - 한국어 도시명 검증을 위한 가드레일 프롬프트 (`weather_agent_guardrail_prompt`)
- 응답 형식 및 지침 정의

## `agent_service/weather/schemas.py`
- 날씨 에이전트에서 사용하는 데이터 모델 정의
- 주요 모델:
  - `Coordinates`: 위도/경도 정보
  - `OpenWeatherCityInfo`: 도시 기본 정보
  - `OpenWeatherCityInfos`: 한국/미국 도시 정보
  - `NonKoreanOutput`: 한국 도시 검증 결과
