from pydantic import BaseModel, Field

class EvaluationScore(BaseModel):
    score: float = Field(description="Score of the evaluation")
    
class RelevancyScore(EvaluationScore):
    pass