import asyncio
import json
from litellm import acompletion
import time
from datetime import datetime
from agents import (
    Agent,
    Runner,
    function_tool,
    GuardrailFunctionOutput,
    input_guardrail,
    TResponseInputItem,
    RunContextWrapper,
    InputGuardrailTripwireTriggered,
    MaxTurnsExceeded,
    set_trace_processors,
)
import weave
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor

from configs import settings
from custom_logger import get_logger
from common.schemas import AgentCommonStatus
from common.utils import create_or_update_prompt, get_litellm_model
from agent_service.user.schemas import (
    UserAgentSetConfigList,
    UserAgentSetConfig,
    ScheduleJob,
    UserAgentFinalOutput,
)
from agent_service.user.prompts import (
    get_user_agent_config_prompt,
    get_user_agent_prompt,
)

weave.init(project_name="user_agent")
set_trace_processors([WeaveTracingProcessor()])

logger = get_logger(__name__)

@function_tool()
@weave.op()
async def set_agent_config(query: str) -> UserAgentSetConfigList:
    """
    뉴스, 우장산역 도착정보, 비트코인 가격, 오늘 날씨를 순차적으로 조회하여 최종 답변 하나를 세션 별로 정리 하여 반환 합니다.
    """
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
    return UserAgentSetConfigList(**result_json)


def get_user_agent(model: str = "openai/gpt-4.1-nano") -> Agent:
    return Agent(
        name="user_agent",
        instructions=get_user_agent_prompt(),
        tools=[set_agent_config],
        model=get_litellm_model(model),
    )

@weave.op()
async def user_agent_runner(input: str, model: str = "openai/gpt-4.1-nano"):
    user_agent = get_user_agent(model)
    try:
        result = await Runner.run(user_agent, input, max_turns=3)
        return UserAgentFinalOutput(
            answer=result.final_output, status=AgentCommonStatus.success
        )
    except MaxTurnsExceeded:
        return UserAgentFinalOutput(
            answer="죄송합니다. 에이전트가 최대 턴 수를 초과했습니다.",
            status=AgentCommonStatus.max_turns_exceeded,
        )

async def main():
    result = await user_agent_runner(" 비트코인 가격을 매일 아침 6시에 조회하여 알람 해줘")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())

# PYTHONPATH=. python agent_service/user/user_agent.py
