from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.db_models import User, Conversation, Message
from configs import settings
import asyncio
from typing import AsyncGenerator

# Async DB URL
db_url = f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

# Async Engine
engine = create_async_engine(db_url, echo=True)

# Async Session Factory
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Async Session Dependency
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Create tables
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# Entry Point
if __name__ == "__main__":
    asyncio.run(create_db_and_tables())
