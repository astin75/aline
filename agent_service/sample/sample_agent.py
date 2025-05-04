import asyncio
import aiohttp
import requests
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

weave.init(project_name="sample_agent")
set_trace_processors([WeaveTracingProcessor()])

logger = get_logger(__name__)
