from fastapi import APIRouter, HTTPException, Header, Request
from linebot.exceptions import InvalidSignatureError
from mongo_db.schema import User
from agent_service.head.head_agent_service import chat_with_head_agent
from mongo_db.service import get_user
from api.service.line_service import line_handler

chat_router = APIRouter(prefix="/chat", tags=["chat"])

@chat_router.post("/chat")
async def chat(
    message: str,
    user_id: str = None,
):
    if user_id:
        user = await get_user(user_id)
    else:
        user = User(platform_id="test-1234")
    return await chat_with_head_agent(user, message)


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
