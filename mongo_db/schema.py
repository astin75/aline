from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class User(BaseModel):
    platform_id: str = Field(description="플랫폼 사용자 ID (예: 라인 ID)")
    platform_type: Optional[str] = Field(default=None, description="플랫폼 종류 (예: kakao, slack 등)")
    email: Optional[str] = Field(default=None, description="이메일 주소")
    user_memory: Optional[str] = Field(default=None, description="유저의 추가 정보")
    created: Optional[datetime] = Field(default=None, description="생성 시각")
    updated: Optional[datetime] = Field(default=None, description="업데이트 시각")


class Message(BaseModel):
    role: str = Field(description="보낸 사람 (user 또는 bot)")
    content: str = Field(description="메시지 내용")
    message_type: Optional[str] = Field(
        default="text", description="메시지 유형 (예: text, image 등)"
    )
    created: Optional[datetime] = Field(default=None, description="생성 시각")
    updated: Optional[datetime] = Field(default=None, description="업데이트 시각")

class Conversation(BaseModel):
    conversation_id: str = Field(description="대화 ID")
    platform_id: str = Field(description="연결된 유저의 ID")
    created: Optional[datetime] = Field(default=None, description="생성 시각")
    updated: Optional[datetime] = Field(default=None, description="업데이트 시각")
    messages: Optional[List[Message]] = Field(default_factory=list, description="메시지 목록")


class ScheduleJob(BaseModel):
    schedule_id: str = Field(description="스케줄 작업 ID")
    user_id: str = Field(description="연결된 유저의 ID")
    job_name: Optional[str] = Field(default=None, description="작업 이름")
    day_of_week: Optional[List[str]] = Field(
        default=None,
        description="요일 (예: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)"
    )
    time_hour: Optional[int] = Field(default=None, description="시간 (예: 09)")
    time_minute: Optional[int] = Field(default=None, description="분 (예: 00)")
    agent_list: Optional[List[str]] = Field(
        default=None,
        description="작업 유형 리스트 (예: [news, subway, weather, web_search])",
    )
    query: Optional[str] = Field(default=None, description="작업 쿼리")
    is_once: Optional[bool] = Field(default=None, description="한번만 실행 여부")
    created: Optional[datetime] = Field(default=None, description="생성 시각")
    updated: Optional[datetime] = Field(default=None, description="업데이트 시각")
    sended_at: Optional[datetime] = Field(default=None, description="송신 시각")
