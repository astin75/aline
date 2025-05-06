from sqlmodel import Session
from api.service.conversation_service import (
    create_or_get_conversation,
    create_message,
    get_conversation_messages,
    init_conversation,
)
from agent_service.head.head_agent import head_agent_runner
from agent_service.user.schemas import UserContextInfo
from database.db import get_session_with
from database.db_models import User, Conversation


async def chat_with_head_agent(user: User, message: str) -> str:
    async with get_session_with() as session:
        if await initialize_conversation(session, user, message):
            return "대화가 초기화되었습니다."
        conversation = await create_or_get_conversation(session, user.id)
        messages = await get_conversation_messages(session, conversation.id)
        message_history = convert_message_history(messages)
        message_history.append({"role": "user", "content": message})
        message_history = get_message_queue(message_history)
        result = await head_agent_runner(message_history, UserContextInfo(user_id=user.id, user_extra_info={}))
        await create_message(session, conversation.id, "user", message)
        await create_message(session, conversation.id, "assistant", result)
        return result


def get_message_queue(
    message_history: list[dict],
    memory_size: int = 5,
) -> list[dict]:
    limit_size = int(memory_size * 2)
    if len(message_history) >= limit_size:
        message_history = message_history[-limit_size:]
    return message_history


def convert_message_history(conversation: Conversation) -> list[dict]:
    message_history = []
    for message in conversation:
        message_history.append(
            {"role": message.sender, "content": message.message_text}
        )
    return message_history


async def initialize_conversation(session: Session, user: User, message: str) -> bool:
    if "초기화" in message:
        await init_conversation(session, user.id)
        return True
    return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(chat_with_head_agent(User(id=1, name="test"), "안녕"))

# PYTHONPATH=. python agent_service/head/head_agent_service.py