import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db import get_session_with
from api.service.schedule_service import get_schedules_by_hour_and_minute
from api.service.user_service import get_user
from agent_service.head.head_agent_service import chat_with_head_agent
from custom_logger import get_logger

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()

def get_now_time_hour_and_minute():
    now = datetime.now()
    return now.hour, now.minute

async def job_runner():
    async with get_session_with() as session:
        hh, mm = get_now_time_hour_and_minute()
        result = await get_schedules_by_hour_and_minute(session, hh, mm)
        logger.info(f"현재 시간: {hh}:{mm}, 스케줄 작업 수: {len(result)}")

        for schedule in result:
            user = await get_user(session, schedule.user_id)
            if user:
                input_query = f"""
                agent_list: {schedule.agent_list}
                query: {schedule.query}
                """
                result = await chat_with_head_agent(user, input_query)

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

# PYTHONPATH=. python schedule_service/main.py
