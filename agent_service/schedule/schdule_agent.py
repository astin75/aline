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
from uuid import uuid4
from configs import settings
from custom_logger import get_logger
from common.schemas import AgentCommonStatus
from common.utils import create_or_update_prompt, get_litellm_model, get_now_kst, get_now_timestamp
from mongo_db.connection import get_mongo_client
from mongo_db.service import (
    create_schedule_job,
    delete_schedule_job,
    get_schedule_job_list,
)
from mongo_db.schema import ScheduleJob
from agent_service.user.schemas import UserInfo
from agent_service.schedule.schemas import (
    UserAgentFinalOutput,
    ScheduleJobSetInfo,
)
from agent_service.schedule.prompts import (
    get_user_agent_prompt,
    get_user_agent_config_prompt,
)

weave.init(project_name="schedule_agent")
set_trace_processors([WeaveTracingProcessor()])

logger = get_logger(__name__)


@function_tool()
@weave.op()
async def set_schedule(
    wrapper: RunContextWrapper[UserInfo], query: str
) -> str:
    """
    뉴스, 우장산역 도착정보, 비트코인 가격, 오늘 날씨를 순차적으로 조회하여 최종 답변 하나를 세션 별로 정리 하여 반환 합니다.
    """
    mongo_client = get_mongo_client()
    query = f"""사용자 요청: {query} 현재 시간: {get_now_kst()}"""
    result = await acompletion(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": get_user_agent_config_prompt()},
            {"role": "user", "content": query},
        ],
        api_key=settings.openai_api_key,
        response_format=ScheduleJobSetInfo,
    )
    result_json = result.choices[0].message.content
    result_json = json.loads(result_json)
    schedule_set_info = ScheduleJobSetInfo(**result_json)
    lower_day_of_week = [day.lower() for day in schedule_set_info.day_of_week]
    schedule_id = f"{wrapper.context.platform_id}_{get_now_timestamp()}"
    schedule_job = ScheduleJob(
        schedule_id=schedule_id,
        user_id=wrapper.context.platform_id,
        job_name=schedule_set_info.job_name,
        day_of_week=lower_day_of_week,
        time_hour=schedule_set_info.time_hour,
        time_minute=schedule_set_info.time_minute,
        is_once=schedule_set_info.is_once,
        query=schedule_set_info.query,
        agent_list=schedule_set_info.agent_list,
    )
    await create_schedule_job(mongo_client, schedule_job)
    return f"스케줄 설정이 완료되었습니다. {schedule_id}"


@function_tool(description_override="유저의 스케줄 정보를 리스트 형태로 전달합니다.")
@weave.op()
async def get_schedule_list(
    wrapper: RunContextWrapper[UserInfo],
) -> list[ScheduleJob]:
    mongo_client = get_mongo_client()
    result = await get_schedule_job_list(mongo_client, wrapper.context.platform_id)
    if len(result) == 0:
        return "등록된 스케줄이 없습니다."
    return result


@function_tool(description_override="유저의 별도 요청이 있을때만 삭제해주세요.")
@weave.op()
async def delete_schedule(schedule_id: int) -> str:
    mongo_client = get_mongo_client()
    result = await delete_schedule_job(mongo_client, schedule_id)
    if result is None:
        return "스케줄 삭제에 실패했습니다."
    return "스케줄 삭제에 성공했습니다."


def get_schedule_agent(model: str = "openai/gpt-4.1-nano") -> Agent:
    return Agent(
        name="schedule_agent",
        instructions=get_user_agent_prompt(),
        tools=[
            set_schedule,
            get_schedule_list,
            delete_schedule,
        ],
        model=get_litellm_model(model),
    )


@weave.op()
async def schedule_agent_runner(
    input: str, user_info: UserInfo = None, model: str = "openai/gpt-4o-mini"
):
    if user_info is None:
        user_info = UserInfo(platform_id="test")
    schedule_agent = get_schedule_agent(model)
    try:
        result = await Runner.run(schedule_agent, input, max_turns=3, context=user_info)
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
    user_info = UserInfo(platform_id="test")
    result = await schedule_agent_runner(
        "비트코인 가격 5분뒤 알려줘",
        user_info,
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

# PYTHONPATH=. python agent_service/schedule/schdule_agent.py
