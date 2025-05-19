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
from mongo_db.connection import get_mongo_client
from mongo_db.service import (
    get_user,
    update_user_memory,
)
from agent_service.user.schemas import (
    UserAgentFinalOutput,
    UserInfo,
    UpdateUserMemory,
)
from agent_service.user.prompts import (
    get_user_agent_prompt,
    get_user_agent_memory_prompt,
)

weave.init(project_name="user_agent")
set_trace_processors([WeaveTracingProcessor()])

logger = get_logger(__name__)


@function_tool(description_override="유저의 정보를 업데이트합니다.")
@weave.op()
async def update_user_memory_info(
    wrapper: RunContextWrapper[UserInfo], user_extra_info: str
) -> str:
    mongo_client = get_mongo_client()
    user_info = await get_user(mongo_client, wrapper.context.platform_id)
    if len(user_info.user_memory) > 0:
        old_user_memory = user_info.user_memory
    else:
        old_user_memory = "없음"

    result = await acompletion(
        model="o3-mini",
        messages=[
            {"role": "system", "content": get_user_agent_memory_prompt()},
            {"role": "user", "content": f"기존 유저 정보: {old_user_memory} 새로운 유저 정보: {user_extra_info}"},
        ],
        api_key=settings.openai_api_key,
        response_format=UpdateUserMemory,
    )
    memory_info = result.choices[0].message.content
    memory_info = UpdateUserMemory(**json.loads(memory_info))
    

        
    await update_user_memory(
        mongo_client, wrapper.context.platform_id, memory_info.update_user_memory
    )
    return "유저 정보 업데이트에 성공했습니다."


@function_tool(description_override="유저 정보를 조회합니다.")
@weave.op()
async def get_user_memory_info(wrapper: RunContextWrapper[UserInfo]) -> str:
    mongo_client = get_mongo_client()
    user_info = await get_user(mongo_client, wrapper.context.platform_id)
    if user_info is None:
        return "유저 정보 조회에 실패했습니다."
    return str(user_info.user_memory)

def get_user_agent(model: str = "openai/gpt-4.1-nano") -> Agent:
    return Agent(
        name="schedule_agent",
        handoff_description="유저의 정보를 업데이트하고 조회합니다.",
        instructions=get_user_agent_prompt(),
        tools=[
            update_user_memory_info,
            get_user_memory_info,
        ],
        model=get_litellm_model(model),
    )


@weave.op()
async def user_agent_runner(
    input: str, user_info: UserInfo = None, model: str = "openai/gpt-4o-mini"
):
    if user_info is None:
        user_info = UserInfo(platform_id="test")
    user_agent = get_user_agent(model)
    try:
        result = await Runner.run(user_agent, input, max_turns=5, context=user_info)
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
    result = await user_agent_runner(
        "내 핸드폰 번호 삭제해줘",
        user_info,
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

# PYTHONPATH=. python agent_service/user/user_agent.py
