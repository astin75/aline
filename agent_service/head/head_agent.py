import asyncio
from typing import List
from datetime import datetime
from agents import Agent, Runner, WebSearchTool, set_trace_processors, function_tool
from litellm import acompletion
import weave
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor

from configs import settings
from custom_logger import get_logger
from common.schemas import AgentCommonStatus
from common.utils import (
    create_or_update_prompt,
    get_litellm_model,
    handle_message_queue,
)
from agent_service.head.prompts import get_head_agent_prompt, get_bot_guide
from agent_service.weather.weather_agent import get_weater_agent
from agent_service.news.news_agent import get_news_agent
from agent_service.subway.subway_agent import get_subway_agent
from agent_service.head.schemas import GlobalContext, Message

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
    input: List[dict], model: str = "openai/gpt-4.1-nano"
) -> str:
    weather_agent = get_weater_agent(model)
    news_agent = get_news_agent(model)
    subway_agent = get_subway_agent(model)
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
            google_web_search,
            get_aline_bot_guide,
        ],
        model=get_litellm_model(model),
    )
    result = await Runner.run(head_agent, input, max_turns=10)

    if result.last_agent.name == "get_aline_bot_guide":
        return result.final_output.guide
    else:
        return result.final_output



@weave.op()
async def main():
    user_id = "d07a9e1e-988e-41ae-9faa-5ac0c0d8d80f"  # str(uuid.uuid4())
    create_or_update_prompt(
        weave, "head_agent_prompt", instructions, "head_agent_prompt"
    )
    message_history = []
    input_items = []
    # global_context = GlobalContext(
    #    user_info={'user_name': '홍길동', 'age': 20, 'gender': 'male'},
    #    message_history=[],
    # )
    from dataclasses import dataclass

    @dataclass
    class GlobalContext:
        user_info: dict
        message_history: list

    # global_context = GlobalContext(
    #     user_info={'user_name': '홍길동', 'age': 20, 'gender': 'male'},
    #     message_history=[],
    # )
    # with weave.attributes({"session_id": user_id}):
    for i in range(7):
        input_items = []

        for message in message_history:
            input_items.append({"role": message["role"], "content": message["content"]})

        user_input = input("Enter your question: ")
        # input_items.append({"role":"user", "content": f"{global_context.user_info}"})
        input_items.append({"role": "user", "content": user_input})
        context = GlobalContext(
            user_info={"user_name": "홍길동", "age": 20, "gender": "male"},
            message_history=[],
        )
        result = await head_agent_runner(input_items, context)
        message_history = handle_message_queue(message_history, user_input, result)
        print(result)

    for message in message_history:
        print(message)
        print("--------------------------------")


if __name__ == "__main__":
    asyncio.run(main())


# PYTHONPATH=. python agent_service/head/head_agent.py
