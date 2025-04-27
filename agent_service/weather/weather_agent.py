import json
import asyncio
import requests
import time
from datetime import datetime
from functools import lru_cache
from agents import (
    Agent, Runner, function_tool,
    GuardrailFunctionOutput, input_guardrail, TResponseInputItem, RunContextWrapper,
    InputGuardrailTripwireTriggered
)
from agents import set_default_openai_key
from configs import settings
from custom_logger import get_logger
from agent_service.weather.schemas import OpenWeatherCityInfos, NonKoreanOutput
from agent_service.weather.prompts import get_weather_prompt

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
def get_forecast_weather(city_name: str):
    if not check_correct_city_name(city_name):
        return "올바른 도시 이름을 입력해주세요."
    url = f"{BASE_URL}/forecast"
    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric",
    }
    response = requests.get(url, params=params)
    print(response.text, "response.text")
    return response.json()


@function_tool
def get_historical_weather(city_name: str, target_datetime: str):
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

guardrails_non_korean = Agent(
    name="guardrails_non_korean",
    instructions=f"날씨정보 요청은 대한민국 도시만 가능합니다.",
    output_type=NonKoreanOutput,
    model="gpt-4.1-nano",
)


@input_guardrail
async def non_korean_guardrail( 
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrails_non_korean, input, context=ctx.context)
    print(result.final_output, "result.final_output")
    return GuardrailFunctionOutput(
        output_info=result.final_output, 
        tripwire_triggered=not result.final_output.is_korea_city,
    )

weather_agent = Agent(
    name="weather_agent",
    handoff_description="날씨 정보를 제공하는 에이전트",
    instructions=instructions,
    tools=[get_current_weather, get_forecast_weather, get_historical_weather],
    input_guardrails=[non_korean_guardrail],
    model="gpt-4.1-nano",
)


async def main():
    set_default_openai_key(settings.openai_api_key)
    try:
        result = await Runner.run(
            starting_agent=weather_agent,
            input="내일 seoul 오후 3시 날씨 알려줘",
        )
        print(result.input)
        print(result.final_output)
    except InputGuardrailTripwireTriggered:
        print("Non korean guardrail tripped")


if __name__ == "__main__":
    asyncio.run(main())

# PYTHONPATH=. python agent_service/weather/weather_agent.py
