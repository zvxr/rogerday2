from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.user import User
from app.models.patient import Patient, PatientResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/", response_model=List[PatientResponse])
async def get_patients(current_user: User = Depends(get_current_user)):
    """Get patients - returns different data based on user type"""
    # Get all patients from database
    patients = await Patient.find_all().to_list()
    
    if current_user.user_type.value == "field_clinician":
        # Field clinicians get basic patient info (no XML data)
        return [
            PatientResponse(
                patient_id=p.patient_id,
                name=p.name,
                dob=p.dob,
                gender=p.gender,
                mrn=p.mrn,
                address=p.address,
                phone=p.phone,
                email=p.email,
                xml_data=None  # Don't include XML data for field clinicians
            ) for p in patients
        ]
    elif current_user.user_type.value == "quality_administrator":
        # Quality administrators get full patient info including XML data
        return [
            PatientResponse(
                patient_id=p.patient_id,
                name=p.name,
                dob=p.dob,
                gender=p.gender,
                mrn=p.mrn,
                address=p.address,
                phone=p.phone,
                email=p.email,
                xml_data=p.xml_data  # Include XML data for quality administrators
            ) for p in patients
        ]
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, current_user: User = Depends(get_current_user)):
    """Get a specific patient by ID"""
    patient = await Patient.find_one({"patient_id": patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Return different data based on user type
    if current_user.user_type.value == "field_clinician":
        return PatientResponse(
            patient_id=patient.patient_id,
            name=patient.name,
            dob=patient.dob,
            gender=patient.gender,
            mrn=patient.mrn,
            address=patient.address,
            phone=patient.phone,
            email=patient.email,
            xml_data=None  # Don't include XML data for field clinicians
        )
    else:
        return PatientResponse(
            patient_id=patient.patient_id,
            name=patient.name,
            dob=patient.dob,
            gender=patient.gender,
            mrn=patient.mrn,
            address=patient.address,
            phone=patient.phone,
            email=patient.email,
            xml_data=patient.xml_data  # Include XML data for quality administrators
        ) 