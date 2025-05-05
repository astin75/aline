from datetime import datetime
import uuid
from sqlmodel import Session, select
from database.db_models import User
from custom_logger import get_logger

logger = get_logger(__name__)


async def create_user(session: Session, platform_id: str, platform_type: str) -> User:
    user = User(
        platform_id=platform_id,
        platform_type=platform_type,
        unique_id=str(uuid.uuid4()),
        created=datetime.now(),
        updated=datetime.now(),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    logger.info(f"신규 사용자 등록: {user.model_dump()}")
    return user


async def get_user(session: Session, user_id: int) -> User | None:
    user = await session.get(User, user_id)
    if not user:
        logger.error(f"사용자가 존재하지 않습니다: {user_id}")
        return None
    return user


async def get_user_by_platform_id(session: Session, platform_id: str) -> User | None:
    result = await session.execute(select(User).where(User.platform_id == platform_id))
    user = result.first()
    if not user:
        logger.error(f"사용자가 존재하지 않습니다: {platform_id}")
        return None
    return user[0] if user else None

