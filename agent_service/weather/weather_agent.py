import asyncio
import aiohttp
import requests
import time
from datetime import datetime
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
from agent_service.weather.schemas import NonKoreanOutput, Coordinates
from agent_service.weather.prompts import get_weather_prompt, weather_agent_guardrail_prompt
weave.init(
    project_name="weather_agent")
set_trace_processors([WeaveTracingProcessor()])

logger = get_logger(__name__)

BASE_URL = "https://api.openweathermap.org/data/2.5"
ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
API_KEY = settings.open_weather_api_key

instructions = get_weather_prompt()
guardrail_prompt = weather_agent_guardrail_prompt()

def datetime_to_unix(dt: datetime) -> int:
    """ datetime to unix timestamp """
    return int(time.mktime(dt.timetuple()))


@function_tool
@weave.op()
def get_weather_with_time(lat: float, lon: float, target_datetime: str):
    if target_datetime == 'present':
        timestamp = datetime_to_unix(datetime.now())
    else:
        timestamp = datetime_to_unix(datetime.fromisoformat(target_datetime))
    params = {
        "lat": lat,
        "lon": lon,
        "dt": timestamp,
        "appid": API_KEY,
        "units": "metric",
    }
    response = requests.get(ONECALL_URL, params=params)
    return response.json()

@function_tool
@weave.op()
async def search_address_to_coordinate(address: str) -> Coordinates | str:
    url = "https://maps.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
        "x-ncp-apigw-api-key-id": settings.naver_map_client_id,
        "x-ncp-apigw-api-key": settings.naver_map_client_secret,
        "Accept": "application/json",
    }
    params = {"query": address}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status != 200:
                logger.error(f"Something went wrong! {response.status} {await response.text()}")
                return f"{address} 주소를 찾을 수 없습니다."

            data = await response.json()

            if data["meta"]["totalCount"] == 0:
                logger.error(f"No results found for address: {address}")
                return f"{address} 주소를 찾을 수 없습니다."

            item = data["addresses"][0]
            result = {
                "roadAddress": item.get("roadAddress"),
                "jibunAddress": item.get("jibunAddress"),
                "englishAddress": item.get("englishAddress"),
                "x": item.get("x"),  # 경도
                "y": item.get("y"),  # 위도
            }

            return Coordinates(lon=result["x"], lat=result["y"])





@input_guardrail
async def non_korean_guardrail( 
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    guardrails_non_korean = Agent(
        name="guardrails_non_korean",
        instructions=guardrail_prompt,
        output_type=NonKoreanOutput,
        model="gpt-4.1-nano",
    )
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
        tools=[get_weather_with_time, search_address_to_coordinate],
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
    
    result = await weather_agent_runner("여수 현재 습도가 어떻게 돼?")
    print(result)
if __name__ == "__main__":
    asyncio.run(main())

# PYTHONPATH=. python agent_service/weather/weather_agent.py
