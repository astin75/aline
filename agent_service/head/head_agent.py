import asyncio
from typing import List
from agents import Agent, Runner, set_trace_processors, function_tool
from litellm import acompletion
import weave
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor

from configs import settings
from custom_logger import get_logger
from common.utils import (
    create_or_update_prompt,
    get_litellm_model,
)
from agent_service.head.prompts import get_head_agent_prompt, get_bot_guide
from agent_service.weather.weather_agent import get_weater_agent
from agent_service.news.news_agent import get_news_agent
from agent_service.subway.subway_agent import get_subway_agent
from agent_service.user.user_agent import get_user_agent
from agent_service.user.schemas import UserInfo

weave.init(project_name="head_agent")
set_trace_processors([WeaveTracingProcessor()])

instructions = get_head_agent_prompt()

logger = get_logger(__name__)


@function_tool(
    name_override="google_web_search", description_override="Google 웹 검색 도구"
)
@weave.op()
async def google_web_search(query: str) -> str:
    tools = [{"googleSearch": {}}]

    response = await acompletion(
        model="gemini/gemini-2.0-flash",
        messages=[{"role": "user", "content": query}],
        api_key=settings.gemini_api_key,
        tools=tools,
    )
    return response.choices[0].message.content


@function_tool(
    description_override="봇에 대한 가이드를 조회하는 도구, 봇의 기능, 사용법을 알려줍니다.",
)
@weave.op()
async def get_aline_bot_guide(query: str) -> str:
    guide = get_bot_guide()
    return guide


@weave.op()
async def head_agent_runner(
    input: List[dict], user_info: UserInfo, model: str = "openai/gpt-4.1-nano"
) -> str:
    weather_agent = get_weater_agent(model)
    news_agent = get_news_agent(model)
    subway_agent = get_subway_agent(model)
    user_agent = get_user_agent(model)
    head_agent = Agent(
        name="head_agent",
        instructions=instructions,
        tools=[
            weather_agent.as_tool(
                tool_name=weather_agent.name,
                tool_description=weather_agent.handoff_description,
            ),
            news_agent.as_tool(
                tool_name=news_agent.name,
                tool_description=news_agent.handoff_description,
            ),
            subway_agent.as_tool(
                tool_name=subway_agent.name,
                tool_description=subway_agent.handoff_description,
            ),
            user_agent.as_tool(
                tool_name=user_agent.name,
                tool_description="""
                1. 사용자의 정보를 조회하고 기억 혹은 업데이트하는 도구
                2. 스케줄기능: 여러에이전트 조합 + 시간 기반으로 Push 알림 기능을 만들 거나 조회 할 수 있습니다.
                3. 사용자가 본인의 정보를 조회하고 싶을때 사용합니다.
                """,
            ),
            google_web_search,
            get_aline_bot_guide,
        ],
        model=get_litellm_model("openai/gpt-4o-mini"),
    )
    result = await Runner.run(head_agent, input, context=user_info, max_turns=10)

    if result.last_agent.name == "get_aline_bot_guide":
        return result.final_output.guide
    else:
        return result.final_output


@weave.op()
async def main():
    create_or_update_prompt(
        weave, "head_agent_prompt", instructions, "head_agent_prompt"
    )
    message_history = []
    input_items = []
    user_info = UserInfo(
        platform_id="test",
    )
    for i in range(3):
        input_items = []

        for message in message_history:
            input_items.append({"role": message["role"], "content": message["content"]})

        user_input = input("Enter your question: ")
        input_items.append({"role": "user", "content": user_input})

        result = await head_agent_runner(input_items, user_info)
        # message_history = handle_message_queue(message_history, user_input, result)
        # print(result)

    for message in message_history:
        print(message)
        print("--------------------------------")


if __name__ == "__main__":
    asyncio.run(main())


# PYTHONPATH=. python agent_service/head/head_agent.py
