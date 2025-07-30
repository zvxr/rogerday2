#!/usr/bin/env python3
"""
MongoDB migration script to create initial users
"""
import asyncio
import sys
import os

# Add the current directory to the Python path (since we're running from /app in the container)
sys.path.append('/app')

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.security import get_password_hash
from app.models.user import User, UserType


async def migrate_users():
    """Create initial users in the database"""
    # Connect to MongoDB (use service name in Docker, localhost for local development)
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_url)
    db = client["patient_dashboard"]
    
    # Check if users already exist
    existing_users = await db.users.find().to_list(length=None)
    if existing_users:
        print("Users already exist in the database. Skipping migration.")
        return
    
    # Create users with hashed passwords
    users_data = [
        {
            "user_id": 1,
            "username": "Bob",
            "hashed_password": get_password_hash("test"),
            "user_type": UserType.FIELD_CLINICIAN
        },
        {
            "user_id": 2,
            "username": "Alice",
            "hashed_password": get_password_hash("test"),
            "user_type": UserType.QUALITY_ADMINISTRATOR
        }
    ]
    
    # Insert users
    result = await db.users.insert_many(users_data)
    print(f"Created {len(result.inserted_ids)} users:")
    for user in users_data:
        print(f"  - {user['username']} ({user['user_type']})")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(migrate_users()) 