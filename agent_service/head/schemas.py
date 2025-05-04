from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class Message(BaseModel):
    message_id: str = Field(description="메시지 ID")
    message_type: str = Field(description="메시지 유형")
    message_content: str = Field(description="메시지 내용")
    created_at_iso_format: str = Field(description="메시지 생성 시간")


class GlobalContext(BaseModel):
    user_info: Optional[Dict] = Field(default=None, description="사용자 정보")
    message_history: List[Message] = Field(default=[], description="메시지 히스토리")