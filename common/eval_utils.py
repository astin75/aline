import json
from configs import settings
from litellm import acompletion
from common.schemas import RelevancyScore
from custom_logger import get_logger

logger = get_logger(__name__)


async def eval_relevancy_score(
    input: str, output: str, model: str = "gpt-4o-mini"
) -> RelevancyScore:
    prompts = f"""
    Given the following 'input' and 'output', rate the relevancy of the 'output' to the 'input' on 
    a scale from 0.0 to 1.0.

    input: {input}
    output: {output}
    Relevancy Score (0.0 - 1.0):    
    
    0.0~0.2: Not relevant
    0.2~0.4: Somewhat relevant
    0.4~0.6: Moderately relevant
    0.6~0.8: Somewhat relevant
    0.8~1.0: Very relevant    
    """
    response = await acompletion(
        model=model,
        messages=[{"role": "user", "content": prompts}],
        api_key=settings.openai_api_key,
        temperature=0.0,
        response_format=RelevancyScore,
    )
    json_response = json.loads(response.choices[0].message.content)
    return RelevancyScore(**json_response)


def get_average_score(scores: list[float]) -> float:
    assert len(scores) > 0, "scores must be a non-empty list"
    result = sum(scores) / len(scores)
    return round(result, 2)
