
from pydantic import BaseModel, Field

class StationSearchResult(BaseModel):
    """지하철 역 정보를 나타내는 스키마, 많은 정보를 주면 역 추출이름의 실패해서 주석처리"""
    # station_id: int = Field(description="역 고유 아이디")
    # line_name: str = Field(description="지하철 노선명")
    # subway_id: int = Field(description="지하철 노선 아이디")
    station_name: str = Field(description="역 이름")
    confidence: float = Field(description="검색 결과의 신뢰도")

class SubwayArrivalInfo(BaseModel):
    """지하철 도착 정보를 나타내는 스키마"""

    up_down_line: str = Field(description="상행/하행 구분")
    subline_name: str = Field(description="지하철 노선명")
    way_to_go: str = Field(description="열차 노선명(행선지)")
    destination_station_name: str = Field(description="도착 역 이름")
    order_index: int = Field(description="도착 순서")
    arrival_time: str = Field(description="도착 예정 시간")
    now_train_status: str = Field(description="현재 열차 상태")
    now_train_location: str = Field(description="현재 열차 위치")
    train_number: str = Field(description="열차 번호")


class SubwayAgentFinalOutput(BaseModel):
    """지하철 에이전트 최종 출력 스키마"""

    answer: str
    status: str

class SubwayAgentOutputGuardrail(BaseModel):
    is_hallucination: bool = Field(description="지하철 도착 정보가 환각인지 여부")
    answer: str = Field(description="지하철 도착 정보")

subway_line_dict = {
    "1001": "1호선",
    "1002": "2호선",
    "1003": "3호선",
    "1004": "4호선",
    "1005": "5호선",
    "1006": "6호선",
    "1007": "7호선",
    "1008": "8호선",
    "1009": "9호선",
    "1061": "중앙선",
    "1063": "경의중앙선",
    "1065": "공항철도",
    "1067": "경춘선",
    "1075": "수의분당선",
    "1077": "신분당선",
    "1092": "우이신설선",
    "1093": "서해선",
    "1081": "경강선",
    "1032": "GTX-A"
}