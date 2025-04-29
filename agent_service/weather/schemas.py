from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    lon: float = Field(description="경도")
    lat: float = Field(description="위도")

class NonKoreanOutput(BaseModel):
    is_korea_city: bool = Field(description="한국 도시인지 여부")
    reason: str = Field(description="한국 도시가 아닌 이유")