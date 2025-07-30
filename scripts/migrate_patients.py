#!/usr/bin/env python3
"""
MongoDB migration script to create patients from XML files
"""
import asyncio
import sys
import os
import re
from datetime import datetime
from typing import Dict, Any

# Add the current directory to the Python path (since we're running from /app in the container)
sys.path.append('/app')

from motor.motor_asyncio import AsyncIOMotorClient
from app.models.patient import Patient


def parse_xml_file(file_path: str) -> Dict[str, Any]:
    """Parse XML file and extract patient information"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract basic demographics
    name_match = re.search(r'- Name: (.+)', content)
    dob_match = re.search(r'- Date of Birth: (\d{1,2}/\d{1,2}/\d{4})', content)
    gender_match = re.search(r'- Gender: (\w+)', content)
    mrn_match = re.search(r'- MRN: (\d+)', content)
    
    # Extract contact information
    address_match = re.search(r'- (?:Home Address|Current Address): (.+)', content)
    
    # Try multiple phone number patterns
    phone = None
    phone_patterns = [
        r'- Phone(?: Numbers)?:.*?(\d{3}-\d{3}-\d{4})',
        r'Phone: (\d{3}-\d{3}-\d{4})',
        r'(\d{3}-\d{3}-\d{4})'
    ]
    for pattern in phone_patterns:
        phone_match = re.search(pattern, content, re.DOTALL)
        if phone_match:
            phone = phone_match.group(1)
            break
    
    email_match = re.search(r'- Email: ([^\s,]+)', content)
    
    # Extract SSN for MRN if not found
    ssn_match = re.search(r'(\d{3}-\d{2}-\d{4})', content)
    
    # Parse date of birth
    dob = None
    if dob_match:
        try:
            dob = datetime.strptime(dob_match.group(1), '%m/%d/%Y')
        except ValueError:
            # Try alternative format
            try:
                dob = datetime.strptime(dob_match.group(1), '%m/%d/%Y')
            except ValueError:
                pass
    
    # Use SSN as MRN if MRN not found
    mrn = None
    if mrn_match:
        mrn = int(mrn_match.group(1))
    elif ssn_match:
        # Use SSN without dashes as MRN
        mrn = int(ssn_match.group(1).replace('-', ''))
    
    # Clean up phone number
    phone = None
    if phone_match:
        phone = phone_match.group(1)
    
    # Clean up email
    email = None
    if email_match:
        email = email_match.group(1).strip()
    else:
        # Try alternative email patterns
        email_patterns = [
            r'Email: ([^\s,]+)',
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        ]
        for pattern in email_patterns:
            email_match = re.search(pattern, content)
            if email_match:
                email = email_match.group(1).strip()
                break
    
    return {
        'name': name_match.group(1).strip() if name_match else 'Unknown',
        'dob': dob,
        'gender': gender_match.group(1) if gender_match else 'Unknown',
        'mrn': mrn,
        'address': address_match.group(1).strip() if address_match else 'Unknown',
        'phone': phone or 'Unknown',
        'email': email or 'unknown@example.com',
        'xml_data': content
    }


async def migrate_patients():
    """Create patients from XML files"""
    # Connect to MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_url)
    db = client["patient_dashboard"]
    
    # Check if patients already exist
    existing_patients = await db.patients.find().to_list(length=None)
    if existing_patients:
        print("Patients already exist in the database. Skipping migration.")
        return
    
    # Parse XML files
    xml_files = [
        ('assets/hp_summary_example_christopher.xml', 1),
        ('assets/hp_summary_example_connie.xml', 2)
    ]
    
    patients_data = []
    
    for xml_file, patient_id in xml_files:
        if os.path.exists(xml_file):
            print(f"Parsing {xml_file}...")
            patient_info = parse_xml_file(xml_file)
            
            # Add patient ID
            patient_info['patient_id'] = patient_id
            
            patients_data.append(patient_info)
            print(f"  - Extracted: {patient_info['name']}")
        else:
            print(f"Warning: {xml_file} not found")
    
    if patients_data:
        # Insert patients
        result = await db.patients.insert_many(patients_data)
        print(f"Created {len(result.inserted_ids)} patients:")
        for patient in patients_data:
            print(f"  - {patient['name']} (ID: {patient['patient_id']}, MRN: {patient['mrn']})")
    else:
        print("No patient data found to insert")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(migrate_patients()) 