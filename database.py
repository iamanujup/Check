from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

mongo = AsyncIOMotorClient(MONGO_URI)
db = mongo[DB_NAME]
collection = db["CachedQuizzes"]


async def get_cached_quiz(token):
    return await collection.find_one({"_id": token})


async def save_quiz(token, questions):
    await collection.replace_one(
        {"_id": token},
        {"_id": token, "questions": questions},
        upsert=True,
    )
