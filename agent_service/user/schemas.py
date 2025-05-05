from typing import Literal
from pydantic import BaseModel, Field
from common.schemas import AgentCommonStatus

class ScheduleJob(BaseModel):
    job_name: str = Field(description="작업 이름")
    day_of_week: Literal[
        "mon", "tue", "wed", "thu", "fri", "sat", "sun", 
        "mon-fri", "sat,sun"
    ] = Field(description="요일")
    time_hour: int = Field(description="시간 HH")
    time_minute: int = Field(description="분 MM")
    job_type: Literal["weekly", "weekday", "weekend"] = Field(description="작업 타입")  


class UserAgentSetConfig(BaseModel):
    agent_name: str = Field(description="에이전트 이름")
    query: str = Field(description="에이전트 쿼리")


class UserAgentSetConfigList(BaseModel):
    configs: list[UserAgentSetConfig] = Field(description="에이전트 설정 리스트")
    schedule_info: ScheduleJob = Field(description="스케줄 정보")

class UserAgentFinalOutput(BaseModel):
    answer: str = Field(description="답변")
    status: AgentCommonStatus = Field(description="상태")

class UserContextInfo(BaseModel):
    user_id: int = Field(description="사용자 ID")
    user_extra_info: dict = Field(description="사용자 추가 정보")
