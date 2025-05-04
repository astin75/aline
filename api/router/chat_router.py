from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import requests
import aiohttp
from linebot.exceptions import InvalidSignatureError
from database.db import get_session


from api.service.line_service import line_handler

chat_router = APIRouter(prefix="/chat", tags=["chat"])

# @chat_router.post("/{user_id}")
# async def chat(user_id: int, message: str, session: AsyncSession = Depends(get_session)):
#     conversation = await session.get(Conversation, user_id)
#     if not conversation:
#         raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다")
#     return conversation


@chat_router.post("/line-callback")
async def callback(
    request: Request,
    x_line_signature: str = Header(None),
):
    body = await request.body()
    try:
        line_handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="chatbot handle body error.")
    return "OK"
