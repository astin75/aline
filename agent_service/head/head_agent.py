import asyncio
from typing import List
from agents import Agent, Runner, WebSearchTool, set_trace_processors, function_tool
from litellm import acompletion
import weave
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor

from configs import settings
from custom_logger import get_logger
from common.schemas import AgentCommonStatus
from common.utils import create_or_update_prompt, get_litellm_model
from agent_service.head.prompts import get_head_agent_prompt
from agent_service.weather.weather_agent import get_weater_agent
from agent_service.news.news_agent import get_news_agent

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


@weave.op()
async def head_agent_runner(input: List[dict], model: str = "openai/gpt-4.1-nano"):
    weather_agent = get_weater_agent(model)
    news_agent = get_news_agent(model)

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
            google_web_search,
        ],
        model=get_litellm_model(model),
    )
    result = await Runner.run(head_agent, input, max_turns=3)
    return result.final_output


@weave.op()
async def main():
    user_id = "d07a9e1e-988e-41ae-9faa-5ac0c0d8d80f"  # str(uuid.uuid4())
    create_or_update_prompt(
        weave, "head_agent_prompt", instructions, "head_agent_prompt"
    )
    input_items = []

    with weave.attributes({"session_id": user_id}):
        for i in range(3):
            user_input = input("Enter your question: ")
            input_items.append({"role": "user", "content": user_input})
            result = await head_agent_runner(input_items)
            print(result)
            input_items.append({"role": "assistant", "content": result})


if __name__ == "__main__":
    asyncio.run(main())


# PYTHONPATH=. python agent_service/head/head_agent.py
