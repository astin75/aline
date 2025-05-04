import asyncio
import aiohttp
import json
from functools import lru_cache
from datetime import datetime
from difflib import SequenceMatcher
from agents import (
    Agent,
    Runner,
    function_tool,
    GuardrailFunctionOutput,
    output_guardrail,
    TResponseInputItem,
    RunContextWrapper,
    OutputGuardrailTripwireTriggered,
    MaxTurnsExceeded,
    set_trace_processors,
)
import weave
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor

from configs import settings
from custom_logger import get_logger
from common.schemas import AgentCommonStatus
from common.utils import create_or_update_prompt, get_litellm_model
from agent_service.subway.schemas import (
    SubwayArrivalInfo,
    SubwayAgentFinalOutput,
    SubwayAgentOutputGuardrail,
    subway_line_dict,
    StationSearchResult,
)
from agent_service.subway.prompts import get_subway_agent_prompt, get_subway_agent_output_guardrail_prompt
weave.init(project_name="subway_agent", settings={"disabled": False})
set_trace_processors([WeaveTracingProcessor()])

logger = get_logger(__name__)
instructions = get_subway_agent_prompt()
output_guardrail_prompt = get_subway_agent_output_guardrail_prompt()

@lru_cache(maxsize=1)
def load_subway_station_info() -> dict:
    """지하철 역 정보를 로드하는 함수"""
    with open("agent_service/subway/subway_station_info.json", "r") as f:
        station_info = json.load(f)
    assert len(station_info) > 0, "지하철 역 정보 로드 실패"
    logger.info(f"지하철 역 정보 로드 완료: {len(station_info)}개의 역 정보 로드")
    return station_info

@function_tool
@weave.op()
async def get_subway_station_info(station_name: str) -> StationSearchResult:
    """지하철 역 정보를 조회하는 함수
    Args:
        station_name (str): 지하철 역 이름
    match_score가 가장 높은 역 정보를 반환
    Returns:
        StationSearchResult: 지하철 역 정보
    """
    station_info = load_subway_station_info()
    best_score = 0
    match_info = None
    for key, value in station_info.items():
        confidence = SequenceMatcher(None, key, station_name).ratio()
        if confidence > best_score:
            best_score = confidence
            match_info = StationSearchResult(
                station_name=key,
                confidence=confidence,
            )
    return match_info


@function_tool
@weave.op()
async def get_subway_arrival_info(station_name: str) -> list[SubwayArrivalInfo]:
    """지하철 도착 정보를 조회하는 함수"""

    base_url = "http://swopenapi.seoul.go.kr/api/subway"
    key = settings.seoul_openapi_key
    size = 5

    url = f"{base_url}/{key}/json/realtimeStationArrival/0/{size}/{station_name}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                reuslt_list = []
                result = await response.json()
                upper_count = 0
                lower_count = 0
                for item in result["realtimeArrivalList"]:
                    if item["updnLine"] == "상행":
                        upper_count += 1
                        now_count = upper_count
                    else:
                        lower_count += 1
                        now_count = lower_count
                    reuslt_list.append(
                        SubwayArrivalInfo(
                            up_down_line=item["updnLine"],
                            subline_name=subway_line_dict[item["subwayId"]],
                            way_to_go=item["trainLineNm"],
                            destination_station_name=item["statnNm"],
                            order_index=now_count,
                            arrival_time=item["recptnDt"],
                            now_train_status=item["arvlMsg2"],
                            now_train_location=item["arvlMsg3"],
                            train_number=item["btrainNo"],
                        )
                    )
                return reuslt_list
            else:
                return "서울시 지하철 도착 정보를 조회할 수 없습니다."


@output_guardrail
async def subway_agent_output_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, output: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    guardrail_agent = Agent(
        name="subway_agent_output_guardrail",
        instructions=output_guardrail_prompt,
        output_type=SubwayAgentOutputGuardrail,
        model="gpt-4.1-nano",
    )
    result = await Runner.run(guardrail_agent, output, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_hallucination,
    )

def get_subway_agent(model: str = "openai/gpt-4.1-nano") -> Agent:
    return Agent(
        name="subway_agent",
        handoff_description="지하철 도착 정보를 제공하는 에이전트",
        instructions=instructions,
        tools=[get_subway_station_info, get_subway_arrival_info],
        output_guardrails=[subway_agent_output_guardrail],
        model=get_litellm_model(model),
    )

@weave.op()
async def subway_agent_runner(input: str, model: str = "openai/gpt-4.1-nano"):
    subway_agent = get_subway_agent(model)

    try:
        result = await Runner.run(subway_agent, input, max_turns=3)

        return SubwayAgentFinalOutput(
            answer=result.final_output, status=AgentCommonStatus.success
        )
    except OutputGuardrailTripwireTriggered as e:
        return SubwayAgentFinalOutput(
            answer=e.guardrail_result.output.output_info.answer,
            status=AgentCommonStatus.output_guardrail_tripwire_triggered,
        )
    except MaxTurnsExceeded:
        return SubwayAgentFinalOutput(
            answer="최대 턴 수를 초과했습니다.",
            status=AgentCommonStatus.max_turns_exceeded,
        )


async def main():
    # create_or_update_prompt(
    #     weave,
    #     "main_subway_agent_prompt",
    #     instructions,
    #     "지하철 도착 정보를 제공하는 main prompt",
    # )

    result = await subway_agent_runner("몽촌토성 지하철 도착 정보")
    print(result)

if __name__ == "__main__":

    asyncio.run(main())

# PYTHONPATH=. python agent_service/subway/subway_agent.py
