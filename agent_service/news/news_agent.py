import asyncio
from datetime import datetime

from agents import (
    Agent, Runner, function_tool,
    GuardrailFunctionOutput, input_guardrail, output_guardrail, TResponseInputItem, RunContextWrapper,
    InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered, MaxTurnsExceeded, set_trace_processors, set_default_openai_key
)
import weave
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor

from configs import settings
from custom_logger import get_logger
from common.utils import create_or_update_prompt, get_litellm_model
from agent_service.news.prompts import get_news_prompt, news_agent_input_guardrail_prompt, news_agent_output_guardrail_prompt, news_agent_retry_prompt
from agent_service.news.schemas import NewsAgentTimeGuardrail, NewsAgentOutputGuardrail
logger = get_logger(__name__)
weave.init(
    project_name="news_agent")
set_trace_processors([WeaveTracingProcessor()])


instructions = get_news_prompt()
input_guardrail_prompt = news_agent_input_guardrail_prompt()
output_guardrail_prompt = news_agent_output_guardrail_prompt()
retry_prompt = news_agent_retry_prompt()

from agent_service.news.ynx_rss import YnxRss

ynx_rss = YnxRss(update_interval_hours=4)



@function_tool
@weave.op()
def get_news_with_section(section: str) -> str:
    """
    RSS 내용을 반환합니다.
    """
    return ynx_rss.get_rss_contents(section)
    
@input_guardrail
async def input_guardrail_news_agent(ctx: RunContextWrapper[None], agent: Agent, 
                                     input: str | list[TResponseInputItem]) -> NewsAgentTimeGuardrail:
    guardrail_agent = Agent(
        name="input_guardrail_news_agent",
        instructions=input_guardrail_prompt,
        output_type=NewsAgentTimeGuardrail,
        model="gpt-4.1-nano",
    )
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_specific_time,
    )
@output_guardrail
async def output_guardrail_news_agent(ctx: RunContextWrapper[None], agent: Agent,
                                      output: str | list[TResponseInputItem]) -> NewsAgentOutputGuardrail:
    guardrail_agent = Agent(
        name="output_guardrail_news_agent",
        instructions=output_guardrail_prompt,
        output_type=NewsAgentOutputGuardrail,
        model="gpt-4.1-nano",
    )
    result = await Runner.run(guardrail_agent, output, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_news_exist,
    )
    
async def news_agent_runner(input: str , model: str = "openai/gpt-4.1-nano"):
    
    news_agent = Agent(
        name="news_agent",
        handoff_description="뉴스 정보를 제공하는 에이전트",
        instructions=instructions,
        tools=[get_news_with_section],
        input_guardrails=[input_guardrail_news_agent],
        output_guardrails=[output_guardrail_news_agent],
        model=get_litellm_model(model),
    )
    try:
        result = await Runner.run(news_agent, input, max_turns=3)
        return result.final_output
    except InputGuardrailTripwireTriggered as e:
        return e.guardrail_result.output.output_info.reason
    except OutputGuardrailTripwireTriggered as e:
        return e.guardrail_result.output.output_info.reason
    except MaxTurnsExceeded:
        return "죄송합니다. 에이전트가 최대 턴 수를 초과했습니다."

async def main():
    create_or_update_prompt(weave, "main_news_agent_prompt", instructions, "뉴스 정보를 제공하는 main prompt")
    create_or_update_prompt(weave, "input_guardrail_news_agent_prompt", input_guardrail_prompt, "input guardrail prompt")
    create_or_update_prompt(weave, "output_guardrail_news_agent_prompt", output_guardrail_prompt, "output guardrail prompt")
    create_or_update_prompt(weave, "news_agent_retry_prompt", retry_prompt, "news agent retry prompt")
    result = await news_agent_runner(" 최신 뉴스 중에서 코로나 관련 소식만 알려줘", "openai/gpt-4.1-nano")
    print(result)
    
if __name__ == "__main__":
    asyncio.run(main())
# PYTHONPATH=. python agent_service/news/news_agent.py