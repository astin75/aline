from typing import List, Optional
from datetime import datetime
from sqlmodel import select, Session

from database.db_models import Conversation, Message
from custom_logger import get_logger

logger = get_logger(__name__)


async def create_conversation(session: Session, user_id: int) -> Conversation:
    """새로운 대화 세션을 생성합니다."""
    current_time = datetime.now()
    conversation = Conversation(
        user_id=user_id,
        started_at=current_time,
        created=current_time,
        updated=current_time,
    )
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    logger.info(f"대화 세션 생성: {conversation.id}")
    return conversation

async def get_conversation_by_user_id(session: Session, user_id: int) -> Conversation:
    """특정 대화를 조회합니다."""
    query = select(Conversation).where(Conversation.user_id == user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def get_conversation_messages(
    session: Session, conversation_id: int
) -> List[Message]:
    """특정 대화의 모든 메시지를 조회합니다."""
    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created.desc())
    )
    result = await session.execute(query)
    messages = result.scalars().all()
    return list(messages)


async def create_message(
    session: Session,
    conversation_id: int,
    sender: str,
    message_text: str,
    message_type: str = "text",
) -> Message:
    """새로운 메시지를 생성합니다."""
    current_time = datetime.now()
    message = Message(
        conversation_id=conversation_id,
        sender=sender,
        message_text=message_text,
        message_type=message_type,
        created=current_time,
        updated=current_time,
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


async def create_or_get_conversation(session: Session, user_id: int) -> Conversation:
    """사용자의 활성 대화를 조회하거나 없으면 새로 생성합니다."""
    conversation = await get_conversation_by_user_id(session, user_id)
    if not conversation:
        conversation = await create_conversation(session, user_id)
    return conversation
