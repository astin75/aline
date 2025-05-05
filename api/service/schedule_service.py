from datetime import datetime
import uuid
from sqlmodel import Session, select
from database.db_models import ScheduleJob
from custom_logger import get_logger

logger = get_logger(__name__)


async def create_schedule_job(
    session: Session,
    user_id: int,
    job_name: str,
    job_type: str,
    day_of_week: str,
    time_hour: int,
    time_minute: int,
    agent_list: list[str],
    query: str,
) -> ScheduleJob:
    now = datetime.now()
    schedule_job = ScheduleJob(
        user_id=user_id,
        job_name=job_name,
        job_type=job_type,
        day_of_week=day_of_week,
        time_hour=time_hour,
        time_minute=time_minute,
        agent_list=agent_list,
        query=query,
        created=now,
        updated=now,
    )
    session.add(schedule_job)
    await session.commit()
    await session.refresh(schedule_job)
    logger.info(f"스케줄 작업 생성: {schedule_job.model_dump()}")
    return schedule_job

async def get_schedule_job_by_user_id(session: Session, user_id: int) -> list[ScheduleJob]:
    query = select(ScheduleJob).where(ScheduleJob.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

async def delete_schedule_job(session: Session, job_id: int) -> None:
    query = select(ScheduleJob).where(ScheduleJob.id == job_id)
    result = await session.execute(query)
    schedule_job = result.scalar_one_or_none()
    if schedule_job:
        await session.delete(schedule_job)
        await session.commit()
        logger.info(f"스케줄 작업 삭제: {schedule_job.model_dump()}")
        return True
    return False

async def get_schedules_by_hour_and_minute(session: Session, hh: int, mm: int) -> list[ScheduleJob]:
    query = select(ScheduleJob).where(ScheduleJob.time_hour == hh, ScheduleJob.time_minute == mm)
    result = await session.execute(query)
    return result.scalars().all()
