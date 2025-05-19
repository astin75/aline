from typing import List
from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from mongo_db.connection import get_mongo_client
from mongo_db.service import get_conversation, get_conversation_list, delete_conversation
from mongo_db.schema import Conversation

conversation_router = APIRouter(prefix="/conversation", tags=["conversation"])


@conversation_router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation_endpoint(
    conversation_id: str, mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)
):
    """특정 대화 ID로 해당 대화의 모든 메시지를 조회합니다."""
    # 대화가 존재하는지 확인
    conversation = await get_conversation(mongo_client, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다")

    return conversation


@conversation_router.get("/user/{user_id}", response_model=List[Conversation])
async def get_user_conversations(
    user_id: str, mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)
):
    """특정 사용자의 모든 대화 목록을 조회합니다."""
    conversations = await get_conversation_list(mongo_client, user_id)
    return conversations


@conversation_router.delete("/{conversation_id}")
async def remove_conversation(
    conversation_id: str, mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)
):
    """특정 대화 ID로 해당 대화와 관련된 모든 메시지를 삭제합니다."""
    try:
        await delete_conversation(mongo_client, conversation_id)
        return {"message": "대화가 성공적으로 삭제되었습니다"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
