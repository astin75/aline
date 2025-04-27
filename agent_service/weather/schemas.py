from typing import Optional
from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    lon: float = Field(description="경도")
    lat: float = Field(description="위도")


class OpenWeatherCityInfo(BaseModel):
    id: int = Field(description="도시 ID")
    name: str = Field(description="도시 이름")
    state: str = Field(description="지역")
    country: str = Field(description="국가")
    coord: Coordinates = Field(description="좌표 정보")


class OpenWeatherCityInfos(BaseModel):
    KR: dict[str, OpenWeatherCityInfo]
    US: dict[str, OpenWeatherCityInfo]


class NonKoreanOutput(BaseModel):
    is_korea_city: bool = Field(description="한국 도시인지 여부")
    reason: str = Field(description="한국 도시가 아닌 이유")