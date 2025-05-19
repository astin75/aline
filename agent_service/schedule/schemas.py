from typing import Literal, Optional, List
from dataclasses import dataclass 
from pydantic import BaseModel, Field
from common.schemas import AgentCommonStatus

class ScheduleJobSetInfo(BaseModel):
    job_name: str = Field(description="작업 이름")
    day_of_week: List[str] = Field(description="""요일 리스트, "Monday", "Tuesday", "Wednesday", "Thursday", 
                                   "Friday", "Saturday", "Sunday" """)
    time_hour: int = Field(description="시간 HH")
    time_minute: int = Field(description="분 MM")
    is_once: bool = Field(description="일회성 알람 여부")
    query: str = Field(description="에이전트 쿼리")
    agent_list: List[str] = Field(description="작업 유형 리스트 (예: [news, subway, weather, web_search])")
    
class UserAgentFinalOutput(BaseModel):
    answer: str = Field(description="답변")
    status: AgentCommonStatus = Field(description="상태")

