import weave
from agents.extensions.models.litellm_model import LitellmModel
from datetime import datetime, timedelta, timezone
from configs import settings
from custom_logger import get_logger

logger = get_logger(__name__)


def create_or_update_prompt(
    weave_client: weave, name: str, content: str, description: str
):
    """
    Create or update a prompt in weave.
    """
    try:
        ref_prompt = weave_client.ref(name).get()
        if ref_prompt.content["content"] != content:
            prompt = weave.StringPrompt(
                {"name": name, "content": content, "description": description}
            )
            weave.publish(prompt, name=name)
            logger.info(f"Prompt {name} updated")
    except Exception as e:
        prompt = weave.StringPrompt(
            {"name": name, "content": content, "description": description}
        )
        weave.publish(prompt, name=name)
        logger.info(f"Prompt {name} created")


def create_or_update_dataset(weave_client: weave, name: str, rows: list[dict]):
    """
    Create or update a dataset in weave.
    """
    with_idx = [{"idx": i, **row} for i, row in enumerate(rows)]
    try:
        ref_dataset = weave_client.ref(name).get()
        if ref_dataset.rows != with_idx:
            dataset = weave.Dataset(name=name, rows=with_idx)
            weave.publish(dataset, name=name)
            logger.info(f"Dataset {name} updated")
    except Exception as e:
        dataset = weave.Dataset(name=name, rows=with_idx)
        weave.publish(dataset, name=name)
        logger.info(f"Dataset {name} created")


def is_time_difference_over_n_hours(iso_str: str, n: int) -> bool:
    # 입력값을 datetime 객체로 파싱 (입력은 UTC 기준이어야 함)
    input_utc_dt = datetime.fromisoformat(iso_str).replace(tzinfo=timezone.utc)

    # 현재 한국 시간 (KST = UTC+9)
    now_kst = datetime.now(timezone(timedelta(hours=9)))

    # 시간 차이 계산
    time_diff = abs((now_kst - input_utc_dt).total_seconds())

    return time_diff > n * 3600


def get_litellm_model(model_name: str) -> LitellmModel:
    """
    litellm 으로 모델 과 api key를 설정합니다.
    providers docs :  https://docs.litellm.ai/docs/providers
    """

    if model_name.startswith("openai"):
        api_key = settings.openai_api_key
    elif model_name.startswith("gemini"):
        api_key = settings.gemini_api_key
    else:
        logger.error(f"Invalid model name: {model_name}")
        raise

    return LitellmModel(
        model=model_name,
        api_key=api_key,
    )


def handle_message_queue(
    message_history: list[dict],
    intput: str,
    output: str,
    memory_size: int = 5,
) -> list[dict]:
    limit_size = int(memory_size)
    if len(message_history) >= limit_size:
        message_history = message_history[2:]
    message_history.append({"role": "user", "content": intput})
    message_history.append({"role": "assistant", "content": output})
    return message_history
