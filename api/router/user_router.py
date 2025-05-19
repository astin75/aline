from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from mongo_db.connection import get_mongo_client
from mongo_db.service import get_user, create_or_update_user, get_user_list
from mongo_db.schema import User


user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.post("/create", response_model=User)
async def create_user(user: User, mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)):
    user.created = datetime.now()
    user.updated = datetime.now()
    await create_or_update_user(mongo_client, user)
    return user


@user_router.get("/list", response_model=List[User])
async def get_users(mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)):
    users = await get_user_list(mongo_client)
    return users


@user_router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)):
    user = await get_user(mongo_client, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return user


@user_router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str, user_update: User, mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)
):
    db_user = await get_user(mongo_client, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    update_data = user_update.model_dump(exclude_unset=True)
    update_data["updated"] = datetime.now()

    for key, value in update_data.items():
        setattr(db_user, key, value)

    await update_user(mongo_client, user_id, db_user)
    return db_user


@user_router.delete("/{user_id}")
async def delete_user(user_id: str, mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)):
    user = await get_user(mongo_client, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    await delete_user(mongo_client, user_id)
    return {"message": "사용자가 성공적으로 삭제되었습니다"}
