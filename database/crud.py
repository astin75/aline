from database.db import get_session
from database.db_models import User, Conversation, Message
from datetime import datetime
from typing import List, Optional
from sqlmodel import select, delete
import asyncio


async def create_conversation(user_id: int) -> Conversation:
    """새로운 대화 세션을 생성합니다."""
    current_time = datetime.now()
    async for session in get_session():
        try:
            conversation = Conversation(
                user_id=user_id,
                started_at=current_time,
                created=current_time,
                updated=current_time,
            )
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
            return conversation
        finally:
            await session.close()


async def create_message(
    conversation_id: int, sender: str, message_text: str, message_type: str = "text"
) -> Message:
    """새로운 메시지를 생성합니다."""
    current_time = datetime.now()
    async for session in get_session():
        try:
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
        finally:
            await session.close()


async def get_conversation_messages(conversation_id: int) -> List[Message]:
    """특정 대화의 모든 메시지를 조회합니다."""
    async for session in get_session():
        try:
            query = select(Message).where(Message.conversation_id == conversation_id)
            result = await session.execute(query)
            messages = result.scalars().all()
            return list(messages)
        finally:
            await session.close()


async def end_conversation(conversation_id: int) -> Optional[Conversation]:
    """대화를 종료합니다."""
    current_time = datetime.now()
    async for session in get_session():
        try:
            conversation = await session.get(Conversation, conversation_id)
            if conversation:
                conversation.ended_at = current_time
                conversation.updated = current_time
                await session.commit()
                await session.refresh(conversation)
                return conversation
            return None
        finally:
            await session.close()


async def delete_conversation(conversation_id: int) -> bool:
    """대화와 관련된 모든 메시지를 삭제합니다."""
    async for session in get_session():
        try:
            # 먼저 관련된 메시지들을 삭제
            delete_messages = delete(Message).where(
                Message.conversation_id == conversation_id
            )
            await session.execute(delete_messages)

            # 대화 삭제
            delete_conv = delete(Conversation).where(Conversation.id == conversation_id)
            await session.execute(delete_conv)

            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            print(f"오류 발생: {str(e)}")
            return False
        finally:
            await session.close()


async def create_conversation_with_messages(
    user_id: int, user_messages: List[str], bot_messages: List[str]
) -> Conversation:
    """대화를 생성하고 여러 메시지를 추가합니다."""
    current_time = datetime.now()
    async for session in get_session():
        try:
            # 대화 생성
            conversation = Conversation(
                user_id=user_id,
                started_at=current_time,
                created=current_time,
                updated=current_time,
            )
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)

            # 메시지 추가 (사용자와 봇 메시지 번갈아가며)
            for i in range(min(len(user_messages), len(bot_messages))):
                # 사용자 메시지
                user_message = Message(
                    conversation_id=conversation.id,
                    sender="user",
                    message_text=user_messages[i],
                    created=current_time,
                    updated=current_time,
                )
                session.add(user_message)

                # 봇 메시지
                bot_message = Message(
                    conversation_id=conversation.id,
                    sender="bot",
                    message_text=bot_messages[i],
                    created=current_time,
                    updated=current_time,
                )
                session.add(bot_message)

            await session.commit()
            return conversation
        finally:
            await session.close()


async def main():
    try:
        # # 대화 생성 예시
        # print("대화 생성 중...")
        # conversation = await create_conversation(user_id=2)
        # print(f"대화 ID: {conversation.id} 생성됨")

        # # 메시지 추가 예시
        # user_messages = ["안녕", "잘가"]
        # bot_messages = ["반가워", "너도"]

        # for i in range(len(user_messages)):
        #     user_msg = await create_message(conversation.id, "user", user_messages[i])
        #     print(f"사용자: {user_msg.message_text}")

        #     bot_msg = await create_message(conversation.id, "bot", bot_messages[i])
        #     print(f"봇: {bot_msg.message_text}")

        # 대화 조회 예시
        print("\n대화 내용 조회:")
        messages = await get_conversation_messages(4)
        for msg in messages:
            print(f"{msg.sender}: {msg.message_text} @@@@@@@@@@@@@@@@@@@")

        # 대화 삭제 예시
        print("\n대화 삭제 중...")
        if await delete_conversation(4):
            print(f"대화 ID: {1} 삭제 성공")
        else:
            print(f"대화 ID: {1} 삭제 실패")

    except Exception as e:
        print(f"오류 발생: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
