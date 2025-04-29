from configs import settings
import weave
from openai import OpenAI
from weave.flow.eval_imperative import EvaluationLogger
weave.init(project_name="weather_agent")
# Initialize the logger (model/dataset names are optional metadata)
eval_logger = EvaluationLogger(model="weather_agent", dataset="weather_evaluation")

# Example input data (this can be any data structure you want)
eval_samples = [
    {"inputs": {"a": 1, "b": 2}, "expected": 3},
    {"inputs": {"a": 2, "b": 3}, "expected": 5},
    {"inputs": {"a": 3, "b": 4}, "expected": 7},
]


# Example model logic.  This does not have to be decorated with @weave.op,
# but if you do, it will be traced and logged.
@weave.op
def user_model(a: int, b: int) -> int:
    oai = OpenAI()
    _ = oai.chat.completions.create(
        messages=[{"role": "user", "content": f"What is {a}+{b}?"}], model="gpt-4o-mini"
    )
    return a + b


# Iterate through examples, predict, and log
for sample in eval_samples:
    inputs = sample["inputs"]
    model_output = user_model(**inputs)  # Pass inputs as kwargs

    # Log the prediction input and output
    pred_logger = eval_logger.log_prediction(inputs=inputs, output=model_output)

    # Calculate and log a score for this prediction
    expected = sample["expected"]
    correctness_score = model_output == expected
    pred_logger.log_score(
        scorer="correctness",  # Simple string name for the scorer
        score=correctness_score,
    )

    # Finish logging for this specific prediction
    pred_logger.finish()

# Log a final summary for the entire evaluation.
# Weave auto-aggregates the 'correctness' scores logged above.
summary_stats = {"subjective_overall_score": 0.8}
eval_logger.log_summary(summary_stats)

print("Evaluation logging complete. View results in the Weave UI.")

# PYTHONPATH=. python agent_service/weather/tt.py
