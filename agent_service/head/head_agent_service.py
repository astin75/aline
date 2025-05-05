from api.service.conversation_service import create_or_get_conversation, create_message, get_conversation_messages
from agent_service.head.head_agent import head_agent_runner
from database.db import get_session_with
from database.db_models import User, Conversation

async def chat_with_head_agent(user: User, message: str) -> str:
    async with get_session_with() as session:
        conversation = await create_or_get_conversation(session, user.id)
        messages = await get_conversation_messages(session, conversation.id)
        message_history = convert_message_history(messages)
        message_history.append({"role": "user", "content": message})           
        message_history = get_message_queue(message_history)
        result = await head_agent_runner(message_history)
        await create_message(session, conversation.id, "user", message)
        await create_message(session, conversation.id, "assistant", result)
        return result


def get_message_queue(
    message_history: list[dict],
    memory_size: int = 10,
) -> list[dict]:
    limit_size = int(memory_size *2)
    if len(message_history) >= limit_size:
        message_history = message_history[-limit_size:]
    return message_history

def convert_message_history(conversation: Conversation) -> list[dict]:
    message_history = []
    for message in conversation:
        message_history.append({"role": message.sender, "content": message.message_text})
    return message_history
