from typing import Literal
from dataclasses import dataclass 
from pydantic import BaseModel, Field
from common.schemas import AgentCommonStatus


class UserAgentFinalOutput(BaseModel):
    answer: str = Field(description="답변")
    status: AgentCommonStatus = Field(description="상태")

class UserInfo(BaseModel):
    platform_id: str = Field(description="플랫폼 ID")
    
class UpdateUserMemory(BaseModel):
    old_user_memory: str = Field(description="기존 유저 메모리")
    update_user_memory: str = Field(description="업데이트 유저 메모리")