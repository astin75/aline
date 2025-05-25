##  에이전트 구현 패턴
- 에이전트 간 결합도 최소화
- 프롬프트 변경 시, 자동 버저닝
- API 키 및 민감 정보 보호
- 메모리 사용량 모니터링

### 기본 구조
```python
def get_{agent_name}_agent(model: str = "openai/gpt-4.1-nano") -> Agent:
    return Agent(
        name="{agent_name}_agent",
        handoff_description="에이전트 설명",
        instructions=get_{agent_name}_agent_prompt(),
        tools=[...],
        model=get_litellm_model(model),
    )
```

### 필수 컴포넌트
- **weave**: 에이전트 추적 및 모니터링
- **가드레일**: 입력/출력 검증
- **프롬프트**: 에이전트 별 독립적인 프롬프트
- **평가**: 에이전트 별 독립적인 평가


## 현재 구현된 에이전트

### 1 Head Agent
- 전체 에이전트 시스템의 중앙 제어
- 다른 에이전트들의 조율
- 사용자 입력의 최종 처리

### 2 Weather Agent
- 날씨 정보 제공
- OpenWeatherMap API 활용
- 한국어 도시명 검증

### 3 News Agent
- 뉴스 정보 제공
- RSS 피드 처리
- 섹션별 뉴스 필터링

### 4 Subway Agent
- 지하철 도착 정보 제공
- 역 정보 검증
- 실시간 도착 정보 조회

### 5 User Agent
- 사용자 정보 관리
- 사용자 메모리 업데이트
- 개인화된 응답 제공

### 6 Schedule Agent
- 일정 관리
- 알림 설정
- 시간 기반 작업 처리

## 모니터링 및 평가

### Weave 
- 에이전트 성능 추적
- 사용 패턴 분석
- 오류 모니터링

### 평가 메트릭
- 각 에이전트별 독립적인 평가
- 프롬프트 효과성 측정
- 응답 정확도 검증

### 코드 구조
- 명확한 책임 분리
- 모듈화된 설계
- 재사용 가능한 컴포넌트

### 에러 처리
- 적절한 예외 처리
- 로깅을 통한 디버깅
- 사용자 친화적인 에러 메시지

