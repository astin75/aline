import json
import asyncio
import requests
import time
from datetime import datetime
from functools import lru_cache
from agents import (
    Agent, Runner, function_tool,
    GuardrailFunctionOutput, input_guardrail, TResponseInputItem, RunContextWrapper,
    InputGuardrailTripwireTriggered, MaxTurnsExceeded, set_trace_processors, set_default_openai_key
)
import weave
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor
from configs import settings
from custom_logger import get_logger
from common.utils import create_or_update_prompt
from agent_service.weather.schemas import OpenWeatherCityInfos, NonKoreanOutput
from agent_service.weather.prompts import get_weather_prompt, weather_agent_guardrail_prompt
weave.init(
    project_name="weather_agent")
set_trace_processors([WeaveTracingProcessor()])

logger = get_logger(__name__)

BASE_URL = "https://api.openweathermap.org/data/2.5"
ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
API_KEY = settings.open_weather_api_key


@lru_cache(maxsize=1)
def load_city_list():
    with open("assets/weather_city_info.json", "r") as f:
        city_info = json.load(f)
    logger.info(f"city_info loaded")
    return OpenWeatherCityInfos(**city_info)


def check_correct_city_name(city_name: str) -> bool:
    """ check if the city name is in the city list """
    city_list = load_city_list()
    if city_name not in city_list.KR:
        return False
    return True


def datetime_to_unix(dt: datetime) -> int:
    """ datetime to unix timestamp """
    return int(time.mktime(dt.timetuple()))


@function_tool
@weave.op()
def get_current_weather(city_name: str):
    if not check_correct_city_name(city_name):
        return "올바른 도시 이름을 입력해주세요."
    url = f"{BASE_URL}/weather"
    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric",
    }
    response = requests.get(url, params=params)
    return response.json()


@function_tool
@weave.op()
def get_weather_with_time(city_name: str, target_datetime: str):
    if not check_correct_city_name(city_name):
        return "올바른 도시 이름을 입력해주세요."
    city_info = load_city_list().KR[city_name]
    dt = datetime.fromisoformat(target_datetime)
    timestamp = datetime_to_unix(dt)
    params = {
        "lat": city_info.coord.lat,
        "lon": city_info.coord.lon,
        "dt": timestamp,
        "appid": API_KEY,
        "units": "metric",
    }
    response = requests.get(ONECALL_URL, params=params)
    return response.json()


instructions = get_weather_prompt(
    kor_city_list=list(load_city_list().KR.keys()),
)
guardrail_prompt = weather_agent_guardrail_prompt()

guardrails_non_korean = Agent(
    name="guardrails_non_korean",
    instructions=guardrail_prompt,
    output_type=NonKoreanOutput,
    model="gpt-4.1-nano",
)


@input_guardrail
async def non_korean_guardrail( 
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrails_non_korean, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output, 
        tripwire_triggered=not result.final_output.is_korea_city,
    )

async def weather_agent_runner(input: str , model: str = "gpt-4.1-nano"):
    weather_agent = Agent(
        name="weather_agent",
        handoff_description="날씨 정보를 제공하는 에이전트",
        instructions=instructions,
        tools=[get_current_weather, get_weather_with_time],
        input_guardrails=[non_korean_guardrail],
        model=model,
    )    
    try:
        result = await Runner.run(weather_agent, input, max_turns=3)
        return result.final_output
    except InputGuardrailTripwireTriggered:
        return "한국 도시 이름을 입력해주세요."
    except MaxTurnsExceeded:
        return "최대 턴 수를 초과했습니다."


async def main():
    set_default_openai_key(settings.openai_api_key)
    create_or_update_prompt(weave, "main_weather_agent_prompt", instructions, "날씨 정보를 제공하는 main prompt")
    create_or_update_prompt(weave, "guardrail_weather_agent_prompt", guardrail_prompt, "guardrail prompt")
    
    try:
        result = await Runner.run(
            starting_agent=weather_agent,
            input="서울과 부산 중 어디가 더 따뜻해?",
        )
        print(result.final_output)
    except InputGuardrailTripwireTriggered:
        print("Non korean guardrail tripped")


if __name__ == "__main__":
    asyncio.run(main())

# PYTHONPATH=. python agent_service/weather/weather_agent.py
