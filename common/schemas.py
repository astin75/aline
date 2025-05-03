from pydantic import BaseModel, Field
from enum import Enum
class EvaluationScore(BaseModel):
    score: float = Field(description="Score of the evaluation")
    
class RelevancyScore(EvaluationScore):
    pass


class AgentCommonStatus(Enum):
    success = "success"
    input_guardrail_tripwire_triggered = "input_guardrail_tripwire_triggered"
    output_guardrail_tripwire_triggered = "output_guardrail_tripwire_triggered"
    max_turns_exceeded = "max_turns_exceeded"