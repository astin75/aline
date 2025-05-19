from motor.motor_asyncio import AsyncIOMotorClient
from mongo_db.connection import get_mongo_client
from mongo_db.service import (
    get_conversation,
    get_conversation_list,
    delete_conversation,
    create_conversation,
)
from mongo_db.schema import Conversation, User
from agent_service.head.head_agent import head_agent_runner
from agent_service.user.schemas import UserInfo


async def chat_with_head_agent(user: User, message: str) -> str:
    mongo_client = get_mongo_client()

    # 대화 조회
    conversation = await get_conversation_list(mongo_client, user.platform_id)
    if not conversation:
        await create_conversation(mongo_client, user.platform_id)
        conversation = await get_conversation_list(mongo_client, user.platform_id)
    messages = await get_conversation(mongo_client, conversation[0].conversation_id)

    # 대화 초기화
    if await initialize_conversation(mongo_client,
                                     conversation[0].conversation_id,
                                     user.platform_id):
        return "대화가 초기화되었습니다."
    
    # 메시지 큐 생성
    message_history = convert_message_history(messages)
    message_history.append({"role": "user", "content": message})
    message_history = get_message_queue(message_history)

    # 대화 실행
    result = await head_agent_runner(message_history, UserInfo(platform_id=user.platform_id))
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
    for message in conversation.messages:
        message_history.append(
            {"role": message.role, "content": message.content}
        )
    return message_history


async def initialize_conversation(mongo_client: AsyncIOMotorClient, 
                                  conversation_id: str,
                                  platform_id: str) -> bool:
    await delete_conversation(mongo_client, conversation_id)
    await create_conversation(mongo_client, platform_id)

if __name__ == "__main__":
    import asyncio
    asyncio.run(chat_with_head_agent(User(id=1, name="test"), "안녕"))

# PYTHONPATH=. python agent_service/head/head_agent_service.py