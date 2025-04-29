import weave
from custom_logger import get_logger

logger = get_logger(__name__)

def create_or_update_prompt(weave_client: weave, name: str, content: str, description: str):
    """
    Create or update a prompt in weave.
    """
    try:
        ref_prompt = weave_client.ref(name).get() 
        if ref_prompt.content["content"] != content:
            prompt = weave.StringPrompt({
                "name": name,
                "content": content,
                "description": description
            })
            weave.publish(prompt, name=name)
            logger.info(f"Prompt {name} updated")
    except Exception as e:
        prompt = weave.StringPrompt({
            "name": name,
            "content": content,
            "description": description
        })
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
        
