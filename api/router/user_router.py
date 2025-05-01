from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_session
from database.db_models import User

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.post("/create", response_model=User)
async def create_user(user: User, session: AsyncSession = Depends(get_session)):
    user.created = datetime.now()
    user.updated = datetime.now()
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@user_router.get("/list", response_model=List[User])
async def get_users(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users


@user_router.get("/{user_id}", response_model=User)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return user


@user_router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int, user_update: User, session: AsyncSession = Depends(get_session)
):
    db_user = await session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    update_data = user_update.model_dump(exclude_unset=True)
    update_data["updated"] = datetime.now()

    for key, value in update_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@user_router.delete("/{user_id}")
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    await session.delete(user)
    await session.commit()
    return {"message": "사용자가 성공적으로 삭제되었습니다"}
