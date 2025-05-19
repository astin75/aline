import asyncio
import aiohttp
import uuid
from concurrent.futures import ThreadPoolExecutor
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from configs import settings
from custom_logger import get_logger
from mongo_db.connection import get_mongo_client
from mongo_db.service import get_user, create_or_update_user
from agent_service.head.head_agent_service import chat_with_head_agent
from agent_service.head.prompts import get_bot_guide

logger = get_logger(__name__)

line_bot_api = LineBotApi(settings.line_channel_access_token)
line_handler = WebhookHandler(settings.line_channel_secret)
executor = ThreadPoolExecutor()


async def process_message(event: MessageEvent):
    
    user_message = event.message.text
    user_platform_id = event.source.user_id
    mongo_client = get_mongo_client()
    user = await get_user(mongo_client, user_platform_id)
    if not user:
        await create_or_update_user(mongo_client, user_platform_id, "line")
        user = await get_user(mongo_client, user_platform_id)
        first_message = f"""
        안녕하세요. 첫 사용자 시군요? 
        {get_bot_guide()}
        """
        await push_message_with_aiohttp(
            user_platform_id, [{"type": "text", "text": first_message}]
        )
        logger.info("신규 사용자 등록, 가이드 메시지 전송")

    result = await chat_with_head_agent(user, user_message)
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=result)
    )


@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    loop = asyncio.get_event_loop()
    asyncio.create_task(process_message(event))


async def push_message_with_aiohttp(user_id: str, messages: list):
    """
    aiohttp를 사용하여 LINE 메시지 API를 통해 사용자에게 메시지를 푸시합니다.

    Args:
        user_id: 수신자의 LINE 사용자 ID
        messages: 보낼 메시지 목록 (dict 형식)

    Returns:
        API 호출 결과
    """
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.line_channel_access_token}",
        "X-Line-Retry-Key": str(uuid.uuid4()),
    }

    payload = {"to": user_id, "messages": messages}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status != 200:
                error_content = await response.text()
                logger.error(f"LINE API 오류: {response.status} - {error_content}")
                return False

            return True
