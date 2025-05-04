from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, JSON


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, description="내부 고유 ID")
    platform_id: str = Field(description="플랫폼 사용자 ID (예: 카카오 ID)")
    unique_id: str = Field(unique=True, description="내부적으로 사용하는 고유 식별자")
    platform_type: str = Field(description="플랫폼 종류 (예: kakao, slack 등)")
    email: Optional[str] = Field(default=None, description="이메일 주소")
    user_memory: Optional[dict] = Field(
        default_factory=dict, sa_type=JSON, description="유저의 추가 정보(JSON 형식)"
    )
    created: Optional[datetime] = Field(default=None, description="생성 시각")
    updated: Optional[datetime] = Field(default=None, description="업데이트 시각")


class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, description="대화 ID")
    user_id: int = Field(foreign_key="user.id", description="연결된 유저의 ID")
    started_at: Optional[datetime] = Field(default=None, description="대화 시작 시각")
    ended_at: Optional[datetime] = Field(default=None, description="대화 종료 시각")
    created: Optional[datetime] = Field(default=None, description="생성 시각")
    updated: Optional[datetime] = Field(default=None, description="업데이트 시각")


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, description="메시지 ID")
    conversation_id: int = Field(
        foreign_key="conversation.id", description="연결된 대화 ID"
    )
    sender: str = Field(description="보낸 사람 (user 또는 bot)")
    message_text: str = Field(description="메시지 내용")
    message_type: Optional[str] = Field(
        default="text", description="메시지 유형 (예: text, image 등)"
    )
    created: Optional[datetime] = Field(default=None, description="생성 시각")
    updated: Optional[datetime] = Field(default=None, description="업데이트 시각")
