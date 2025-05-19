import asyncio
from typing import List
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from mongo_db.connection import get_mongo_client
from mongo_db.schema import ScheduleJob
from mongo_db.service import (
    get_user,
    get_schedule_job_list_by_time,
    update_schedule_job_sended_at,
    delete_schedule_job,
)
from api.service.line_service import push_message_with_aiohttp
from agent_service.head.head_agent_service import chat_with_head_agent
from custom_logger import get_logger

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


def get_now_time_hour_and_minute():
    now = datetime.now()
    return now.hour, now.minute


async def job_runner():
    mongo_client = get_mongo_client()

    hh, mm = get_now_time_hour_and_minute()
    now_time = datetime.now()
    day_name = now_time.strftime("%A")
    day_name = day_name.lower()
    hh = 9
    mm = 0
    result = await get_schedule_job_list_by_time(mongo_client, hh, mm)
    send_list: List[ScheduleJob] = []
    for schedule in result:
        if not schedule.is_once and day_name not in schedule.day_of_week:
            continue
        
        if schedule.sended_at is None:
            send_list.append(schedule)
        elif schedule.sended_at.day < now_time.day:
            send_list.append(schedule)

    for schedule in send_list:
        user = await get_user(mongo_client, schedule.user_id)
        if user:
            input_query = f"""
            agent_list: {schedule.agent_list}
            query: {schedule.query}
            """
            print(input_query)
            result = await chat_with_head_agent(user, input_query)
            # await push_message_with_aiohttp(
            #     user.platform_id, [{"type": "text", "text": result}]
            # )
            if schedule.is_once:
                await delete_schedule_job(mongo_client, schedule.schedule_id)
            else:
                await update_schedule_job_sended_at(
                    mongo_client, schedule.schedule_id, datetime.now()
                )
            


async def main():
    scheduler.add_job(job_runner, "interval", seconds=2)
    scheduler.start()
    count = 0
    while True:
        await asyncio.sleep(1)
        count += 1
        if count > 60:
            break
    scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

# PYTHONPATH=. python schedule_service/service.py
