#!/usr/bin/env python3
"""
MongoDB migration script to create questions from question_schema.json
"""
import asyncio
import sys
import os
import json
from typing import Dict, Any, List

# Add the current directory to the Python path (since we're running from /app in the container)
sys.path.append('/app')

from motor.motor_asyncio import AsyncIOMotorClient
from app.models.question import Question


def parse_question_schema(file_path: str) -> List[Dict[str, Any]]:
    """Parse question_schema.json and extract all questions"""
    questions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Process each visit type
        for visit_type, categories in data.items():
            print(f"Processing visit type: {visit_type}")
            
            # Process each category within the visit type
            for category, questions_list in categories.items():
                print(f"  Processing category: {category}")
                
                # Process each question in the category
                for question_data in questions_list:
                    question = {
                        'qid': question_data['qid'],
                        'description': question_data['description'],
                        'casting': question_data['casting'],
                        'visit_type': visit_type,
                        'category': category
                    }
                    
                    # Add subitems if they exist
                    if 'subitems' in question_data:
                        question['subitems'] = question_data['subitems']
                    
                    questions.append(question)
        
        print(f"Total questions extracted: {len(questions)}")
        return questions
        
    except Exception as e:
        print(f"Error parsing question schema: {e}")
        return questions


async def migrate_questions():
    """Create questions from question_schema.json"""
    # Connect to MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_url)
    db = client["patient_dashboard"]
    
    # Check if questions already exist
    existing_questions = await db.questions.find().to_list(length=None)
    if existing_questions:
        print("Questions already exist in the database. Skipping migration.")
        return
    
    # Parse question schema file
    schema_file = 'assets/question_schema.json'
    if not os.path.exists(schema_file):
        print(f"Warning: {schema_file} not found")
        return
    
    print(f"Parsing {schema_file}...")
    questions_data = parse_question_schema(schema_file)
    
    if questions_data:
        # Insert questions
        result = await db.questions.insert_many(questions_data)
        print(f"Created {len(result.inserted_ids)} questions")
        
        # Show some sample questions
        print("\nSample questions created:")
        for i, question in enumerate(questions_data[:5]):
            print(f"  {i+1}. {question['qid']} - {question['description']}")
        
        if len(questions_data) > 5:
            print(f"  ... and {len(questions_data) - 5} more questions")
    else:
        print("No question data found to insert")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(migrate_questions()) 