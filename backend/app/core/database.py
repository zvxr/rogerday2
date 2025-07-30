from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.user import User
from app.models.patient import Patient
from app.models.question import Question
from app.models.form import Form


async def init_db():
    """Initialize database connection and Beanie ODM"""
    client = AsyncIOMotorClient(settings.mongodb_url)
    await init_beanie(
        database=client[settings.database_name],
        document_models=[User, Patient, Question, Form]
    )


async def close_db():
    """Close database connection"""
    # Beanie handles connection cleanup automatically
    pass 