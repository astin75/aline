import asyncio
from typing import List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from mongo_db.connection import get_mongo_client
from mongo_db.schema import User, Conversation, Message, ScheduleJob

from common.utils import get_now_kst
from custom_logger import get_logger
from uuid import uuid4

logger = get_logger(__name__)


async def create_or_update_user(mongo_client: AsyncIOMotorClient, user: User) -> None:
    """유저 정보 생성 또는 업데이트"""
    collection = mongo_client["database"]["users"]

    # 기존 데이터 확인
    existing_user = await collection.find_one({"platform_id": user.platform_id})

    if existing_user:
        user.updated = get_now_kst()
        # 기존 데이터가 있는 경우 updated 필드만 업데이트
        await collection.update_one(
            {"platform_id": user.platform_id},
            {"$set": user.model_dump(exclude_none=True)},
        )
    else:
        user.created = get_now_kst()
        user.updated = get_now_kst()
        # 새로운 데이터인 경우 전체 데이터 저장
        await collection.update_one(
            {"platform_id": user.platform_id},
            {"$set": user.model_dump()},
            upsert=True,
        )


async def get_user(mongo_client: AsyncIOMotorClient, platform_id: str) -> User:
    collection = mongo_client["database"]["users"]
    user = await collection.find_one({"platform_id": platform_id})
    if user is None:
        logger.info(f"유저 정보가 없습니다. platform_id: {platform_id}")
        raise
    return User(**user)


async def update_user_memory(
    mongo_client: AsyncIOMotorClient, platform_id: str, memory: str
) -> None:
    collection = mongo_client["database"]["users"]
    await collection.update_one(
        {"platform_id": platform_id},
        {"$set": {"user_memory": memory}},
    )

async def create_conversation(
    mongo_client: AsyncIOMotorClient, platform_id: str
) -> None:
    conversation = Conversation(
        conversation_id=str(uuid4()),
        platform_id=platform_id,
    )
    collection = mongo_client["database"]["conversations"]
    user_info = await get_user(mongo_client, platform_id)
    if user_info is None:
        logger.info(f"유저 정보가 없습니다. platform_id: {platform_id}")
        raise
    conversation.created = get_now_kst()
    conversation.updated = get_now_kst()
    conversation.messages = []
    await collection.update_one(
        {"conversation_id": conversation.conversation_id},
        {"$set": conversation.model_dump()},
        upsert=True,
    )

async def get_user_list(
    mongo_client: AsyncIOMotorClient,
) -> List[User]:
    collection = mongo_client["database"]["users"]
    cursor = collection.find()
    output_list = []
    async for user in cursor:
        output_list.append(User(**user))
    return output_list

async def get_conversation(
    mongo_client: AsyncIOMotorClient, conversation_id: str
) -> Conversation:
    collection = mongo_client["database"]["conversations"]
    conversation = await collection.find_one({"conversation_id": conversation_id})
    if conversation is None:
        return None
    return Conversation(**conversation)


async def get_conversation_list(
    mongo_client: AsyncIOMotorClient, platform_id: str
) -> List[Conversation]:
    collection = mongo_client["database"]["conversations"]
    cursor = collection.find({"platform_id": platform_id})
    output_list = []
    async for conversation in cursor:
        output_list.append(Conversation(**conversation))
    return output_list

async def append_message(
    mongo_client: AsyncIOMotorClient, conversation_id: str, message: Message
) -> None:
    collection = mongo_client["database"]["conversations"]
    conversation = await get_conversation(mongo_client, conversation_id)
    if conversation is None:
        logger.info(f"대화 정보가 없습니다. conversation_id: {conversation_id}")
        raise

    message.created = get_now_kst()
    message.updated = get_now_kst()

    await collection.update_one(
        {"conversation_id": conversation_id},
        {
            "$push": {"messages": message.model_dump()},
            "$set": {"updated": message.updated},
        },
    )


async def delete_conversation(
    mongo_client: AsyncIOMotorClient, conversation_id: str
) -> None:
    collection = mongo_client["database"]["conversations"]
    await collection.delete_one({"conversation_id": conversation_id})

async def create_schedule_job(
    mongo_client: AsyncIOMotorClient, schedule_job: ScheduleJob
) -> None:
    collection = mongo_client["database"]["schedule_jobs"]
    schedule_job.created = get_now_kst()
    schedule_job.updated = get_now_kst()
    await collection.update_one(
        {"schedule_id": schedule_job.schedule_id},
        {"$set": schedule_job.model_dump()},
        upsert=True,
    )

async def get_schedule_job(
    mongo_client: AsyncIOMotorClient, schedule_id: str
) -> ScheduleJob:
    collection = mongo_client["database"]["schedule_jobs"]
    schedule_job = await collection.find_one({"schedule_id": schedule_id})
    return ScheduleJob(**schedule_job)

async def get_schedule_job_list(
    mongo_client: AsyncIOMotorClient, platform_id: str
) -> List[ScheduleJob]:
    collection = mongo_client["database"]["schedule_jobs"]
    cursor = collection.find({"user_id": platform_id})
    output_list = []
    async for schedule_job in cursor:
        output_list.append(ScheduleJob(**schedule_job))
    return output_list

async def get_schedule_job_list_by_time(
    mongo_client: AsyncIOMotorClient, time_hour: int, time_minute: int
) -> List[ScheduleJob]:
    collection = mongo_client["database"]["schedule_jobs"]
    cursor = collection.find({"time_hour": time_hour, "time_minute": time_minute})
    output_list = []
    async for schedule_job in cursor:
        output_list.append(ScheduleJob(**schedule_job))
    return output_list


async def update_schedule_job(
    mongo_client: AsyncIOMotorClient, schedule_id: str, schedule_job: ScheduleJob
) -> None:
    collection = mongo_client["database"]["schedule_jobs"]
    schedule = await get_schedule_job(mongo_client, schedule_id)
    if schedule is None:
        logger.info(f"스케줄 작업 정보가 없습니다. schedule_id: {schedule_id}")
        raise
    schedule_job.updated = get_now_kst()
    print(schedule_job.model_dump(exclude_none=True))
    await collection.update_one(
        {"schedule_id": schedule_id},
        {"$set": schedule_job.model_dump(exclude_none=True)},
    )

async def update_schedule_job_sended_at(
    mongo_client: AsyncIOMotorClient, schedule_id: str, sended_at: datetime
) -> None:
    collection = mongo_client["database"]["schedule_jobs"]
    await collection.update_one(
        {"schedule_id": schedule_id},
        {"$set": {"sended_at": sended_at}},
    )

async def delete_schedule_job(
    mongo_client: AsyncIOMotorClient, schedule_id: str
) -> None:
    collection = mongo_client["database"]["schedule_jobs"]
    await collection.delete_one({"schedule_id": schedule_id})

async def main():
    now = get_now_kst()
    mongo_client = get_mongo_client()
    schedule_id = str(uuid4())
    schedule_job = ScheduleJob(
        schedule_id=schedule_id,
        user_id="test",
        job_name="test",
        day_of_week=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        time_hour=10,
        time_minute=0,
        agent_list=["news", "subway", "weather", "web_search"],
        query="test",
        is_once=False,
    )
    await create_schedule_job(mongo_client, schedule_job)
    print(now.strftime('%A'))
    schedule_job = await get_schedule_job(mongo_client, schedule_job.schedule_id)
    print(schedule_job)

    temp_schedule_job = ScheduleJob(
        schedule_id=schedule_id,
        user_id="test",
        time_hour=11,
        time_minute=0,
    )
    await update_schedule_job(mongo_client, schedule_job.schedule_id, temp_schedule_job)
    print(schedule_job)
    
    # await delete_schedule_job(mongo_client, schedule_job.schedule_id)
    # print(schedule_job)    

if __name__ == "__main__":
    asyncio.run(main())


# PYTHONPATH=. uv run mongo_db/service.py
