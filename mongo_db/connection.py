from motor.motor_asyncio import AsyncIOMotorClient

mongo_client = AsyncIOMotorClient(
    host="localhost",
    port=27017,
    username="aline_user",
    password="aline_password",
    authSource="admin",
)


def get_mongo_client() -> AsyncIOMotorClient:
    """MongoDB 클라이언트 반환"""
    return mongo_client
