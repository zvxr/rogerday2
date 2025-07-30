#!/usr/bin/env python3
"""
MongoDB migration script to create forms from form_response_*.json files
"""
import asyncio
import sys
import os
import json
from datetime import date, datetime
from typing import Dict, Any, List

# Add the current directory to the Python path (since we're running from /app in the container)
sys.path.append('/app')

from motor.motor_asyncio import AsyncIOMotorClient
from app.models.form import Form, FormType


def inject_question_descriptions(survey_data: Dict[str, Any], questions_cache: Dict[str, str]) -> Dict[str, Any]:
    """Inject question descriptions into survey data based on question IDs"""
    enhanced_data = {}
    
    for form_type, categories in survey_data.items():
        enhanced_data[form_type] = {}
        
        for category, fields in categories.items():
            enhanced_data[form_type][category] = {}
            
            for field_name, field_value in fields.items():
                # Look up the question description
                description = questions_cache.get(field_name, None)
                
                # Create enhanced field with description
                enhanced_data[form_type][category][field_name] = {
                    "value": field_value,
                    "question_description": description
                }
    
    return enhanced_data


def load_questions_cache() -> Dict[str, str]:
    """Load questions from database to create a cache for descriptions"""
    # This will be called from the async function
    return {}


async def load_questions_cache_async() -> Dict[str, str]:
    """Load questions from database to create a cache for descriptions"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_url)
    db = client["patient_dashboard"]
    
    questions = await db.questions.find({}, {"qid": 1, "description": 1, "casting": 1}).to_list(length=None)
    
    cache = {}
    for question in questions:
        qid = question["qid"]
        description = question["description"]
        casting = question.get("casting", {})
        
        # Add the qid itself
        cache[qid] = description
        
        # Add mappings from casting
        for key, value in casting.items():
            if isinstance(value, str):
                cache[value] = description
    
    client.close()
    return cache


def parse_form_response_file(file_path: str) -> Dict[str, Any]:
    """Parse form response JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return {}


async def migrate_forms():
    """Create forms from form_response_*.json files"""
    # Connect to MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_url)
    db = client["patient_dashboard"]
    
    # Check if forms already exist
    existing_forms = await db.forms.find().to_list(length=None)
    if existing_forms:
        print("Forms already exist in the database. Skipping migration.")
        return
    
    # Load questions cache for descriptions
    print("Loading questions cache...")
    questions_cache = await load_questions_cache_async()
    print(f"Loaded {len(questions_cache)} questions for description lookup")
    
    # Parse form response files
    forms_data = []
    
    # Christopher's SOC form
    christopher_file = 'assets/form_response_example_christopher.json'
    if os.path.exists(christopher_file):
        print(f"Parsing {christopher_file}...")
        christopher_data = parse_form_response_file(christopher_file)
        
        if christopher_data and "SOC" in christopher_data:
            # Inject question descriptions
            enhanced_data = inject_question_descriptions(christopher_data, questions_cache)
            
            forms_data.append({
                'form_id': 1,
                'patient_id': 1,  # Christopher's patient ID
                'form_date': datetime.now(),
                'form_type': 'SOC',
                'survey_data': enhanced_data
            })
            print("Added Christopher's SOC form")
    
    # Connie's PTEVAL form
    connie_file = 'assets/form_response_example_connie.json'
    if os.path.exists(connie_file):
        print(f"Parsing {connie_file}...")
        connie_data = parse_form_response_file(connie_file)
        
        if connie_data and "PTEVAL" in connie_data:
            # Inject question descriptions
            enhanced_data = inject_question_descriptions(connie_data, questions_cache)
            
            forms_data.append({
                'form_id': 2,
                'patient_id': 2,  # Connie's patient ID
                'form_date': datetime.now(),
                'form_type': 'PTEVAL',
                'survey_data': enhanced_data
            })
            print("Added Connie's PTEVAL form")
    
    if forms_data:
        # Insert forms
        result = await db.forms.insert_many(forms_data)
        print(f"Created {len(result.inserted_ids)} forms")
        
        # Show sample forms
        print("\nSample forms created:")
        for i, form in enumerate(forms_data):
            print(f"  {i+1}. Form ID: {form['form_id']}, Patient: {form['patient_id']}, Type: {form['form_type']}")
            
            # Show some sample fields with descriptions
            form_type = form['form_type']
            if form_type in form['survey_data']:
                categories = form['survey_data'][form_type]
                for category, fields in list(categories.items())[:2]:  # Show first 2 categories
                    print(f"    {category}: {len(fields)} fields")
                    for field_name, field_data in list(fields.items())[:3]:  # Show first 3 fields
                        desc = field_data.get('question_description', 'No description')
                        if desc:
                            print(f"      {field_name}: {desc[:50]}...")
                        else:
                            print(f"      {field_name}: No description")
    else:
        print("No form data found to insert")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(migrate_forms()) 