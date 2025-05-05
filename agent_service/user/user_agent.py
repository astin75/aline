import asyncio
import json
from litellm import acompletion
from agents import (
    Agent,
    Runner,
    function_tool,
    RunContextWrapper,
    MaxTurnsExceeded,
    set_trace_processors,
)
import weave
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor

from configs import settings
from custom_logger import get_logger
from common.schemas import AgentCommonStatus
from common.utils import create_or_update_prompt, get_litellm_model
from database.db import get_session_with
from api.service.schedule_service import (
    get_schedule_job_by_user_id,
    create_schedule_job,
    delete_schedule_job,
)
from api.service.user_service import (
    update_user_extra_info,
    get_user_extra_info,
)
from agent_service.user.schemas import (
    UserAgentSetConfigList,
    ScheduleJob,
    UserAgentFinalOutput,
    UserContextInfo,
)
from agent_service.user.prompts import (
    get_user_agent_config_prompt,
    get_user_agent_prompt,
    get_user_agent_memory_prompt,
)

weave.init(project_name="user_agent")
set_trace_processors([WeaveTracingProcessor()])

logger = get_logger(__name__)


@function_tool()
@weave.op()
async def set_agent_config(
    wrapper: RunContextWrapper[UserContextInfo], query: str
) -> UserAgentSetConfigList:
    """
    뉴스, 우장산역 도착정보, 비트코인 가격, 오늘 날씨를 순차적으로 조회하여 최종 답변 하나를 세션 별로 정리 하여 반환 합니다.
    """
    async with get_session_with() as session:
        schedule_job = await get_schedule_job_by_user_id(
            session, wrapper.context.user_id
        )
        if len(schedule_job) > 0:
            return "스케줄은 1개 이상 일 수 없습니다. 에이전트를 종료하세요."

    result = await acompletion(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": get_user_agent_config_prompt()},
            {"role": "user", "content": query},
        ],
        api_key=settings.openai_api_key,
        response_format=UserAgentSetConfigList,
    )
    result_json = result.choices[0].message.content
    result_json = json.loads(result_json)
    schedule_job = UserAgentSetConfigList(**result_json)
    querys = ""
    agent_list = []
    for config in schedule_job.configs:
        querys += config.query
        agent_list.append(config.agent_name)
        async with get_session_with() as session:
            await create_schedule_job(
                session,
                wrapper.context.user_id,
                schedule_job.schedule_info.job_name,
                schedule_job.schedule_info.job_type,
                schedule_job.schedule_info.day_of_week,
                schedule_job.schedule_info.time_hour,
                schedule_job.schedule_info.time_minute,
                agent_list,
                querys,
            )
    return schedule_job


@function_tool(description_override="유저의 스케줄 정보를 리스트 형태로 전달합니다.")
@weave.op()
async def get_user_schedule_list(
    wrapper: RunContextWrapper[UserContextInfo],
) -> list[ScheduleJob]:
    async with get_session_with() as session:
        result = await get_schedule_job_by_user_id(session, wrapper.context.user_id)
    if result is None:
        return "등록된 스케줄이 없습니다."
    return result


@function_tool(description_override="유저의 별도 요청이 있을때만 삭제해주세요.")
@weave.op()
async def delete_user_schedule(schedule_id: int) -> str:
    async with get_session_with() as session:
        result = await delete_schedule_job(session, schedule_id)
    if result is None:
        return "스케줄 삭제에 실패했습니다."
    return "스케줄 삭제에 성공했습니다."


@function_tool(description_override="유저의 정보를 업데이트합니다.")
@weave.op()
async def memory_user_extra_info(
    wrapper: RunContextWrapper[UserContextInfo], user_extra_info: str
) -> str:
    async with get_session_with() as session:
        old_user_memory = await get_user_extra_info(session, wrapper.context.user_id)
        if len(old_user_memory) > 0:
            old_user_memory = "없음"
 
        result = await acompletion(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": get_user_agent_memory_prompt()},
                {"role": "user", "content": f"기존 유저 정보: {old_user_memory} 새로운 유저 정보: {user_extra_info}"},
            ],
            api_key=settings.openai_api_key,
        )
        memory_info = result.choices[0].message.content
 
            
        result = await update_user_extra_info(
            session, wrapper.context.user_id, memory_info
        )
    if result is None:
        return "유저 정보 업데이트에 실패했습니다."
    return "유저 정보 업데이트에 성공했습니다."


@function_tool(description_override="유저 정보를 조회합니다.")
@weave.op()
async def get_user_memory_info(wrapper: RunContextWrapper[UserContextInfo]) -> str:
    async with get_session_with() as session:
        result = await get_user_extra_info(session, wrapper.context.user_id)
    if result is None:
        return "유저 정보 조회에 실패했습니다."
    return str(result)

def get_user_agent(model: str = "openai/gpt-4.1-nano") -> Agent:
    return Agent(
        name="user_agent",
        instructions=get_user_agent_prompt(),
        tools=[
            set_agent_config,
            get_user_schedule_list,
            delete_user_schedule,
            memory_user_extra_info,
            get_user_memory_info,
        ],
        model=get_litellm_model(model),
    )


@weave.op()
async def user_agent_runner(
    input: str, user_info: UserContextInfo = None, model: str = "openai/gpt-4o-mini"
):
    if user_info is None:
        user_info = UserContextInfo(user_id=5, user_extra_info={})
    user_agent = get_user_agent(model)
    try:
        result = await Runner.run(user_agent, input, max_turns=3, context=user_info)
        return UserAgentFinalOutput(
            answer=result.final_output, status=AgentCommonStatus.success
        )
    except MaxTurnsExceeded:
        return UserAgentFinalOutput(
            answer="죄송합니다. 에이전트가 최대 턴 수를 초과했습니다.",
            status=AgentCommonStatus.max_turns_exceeded,
        )


async def main():
    create_or_update_prompt(
        weave, "user_agent", get_user_agent_prompt(), "user_agent main prompt"
    )
    user_info = UserContextInfo(user_id=5, user_extra_info={})
    result = await user_agent_runner(
        "비트코인가격 매일 아침 6시 조회 그리고 지하철 도착정보 오전 7시 조회",
        user_info,
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

# PYTHONPATH=. python agent_service/user/user_agent.py
