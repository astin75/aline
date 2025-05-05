from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database.db import get_session
from database.db_models import Conversation, Message
from api.service.conversation_service import get_conversation_messages
conversation_router = APIRouter(prefix="/conversation", tags=["conversation"])


@conversation_router.get("/{conversation_id}", response_model=List[Message])
async def get_conversation(
    conversation_id: int, session: AsyncSession = Depends(get_session)
):
    """특정 대화 ID로 해당 대화의 모든 메시지를 조회합니다."""
    # 대화가 존재하는지 확인
    conversation = await session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다")

    # 대화의 모든 메시지 조회
    messages = await get_conversation_messages(conversation_id)
    return messages


@conversation_router.get("/user/{user_id}", response_model=List[Conversation])
async def get_user_conversations(
    user_id: int, session: AsyncSession = Depends(get_session)
):
    """특정 사용자의 모든 대화 목록을 조회합니다."""
    result = await session.execute(
        select(Conversation).where(Conversation.user_id == user_id)
    )
    conversations = result.scalars().all()
    return conversations


@conversation_router.delete("/{conversation_id}")
async def remove_conversation(
    conversation_id: int, session: AsyncSession = Depends(get_session)
):
    """특정 대화 ID로 해당 대화와 관련된 모든 메시지를 삭제합니다."""
    conversation = await session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다")

    await session.delete(conversation)
    await session.commit()
    return {"message": "대화가 성공적으로 삭제되었습니다"}
