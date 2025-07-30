from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.user import User
from app.models.patient import PatientResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/", response_model=List[PatientResponse])
async def get_patients(current_user: User = Depends(get_current_user)):
    """Get patients - returns different data based on user type"""
    # For now, return stub data based on user type
    if current_user.user_type.value == "field_clinician":
        # Field clinicians get quick summaries
        return [
            {"id": 1, "name": "John Doe - Quick Summary"},
            {"id": 2, "name": "Jane Smith - Quick Summary"},
        ]
    elif current_user.user_type.value == "quality_administrator":
        # Quality administrators get detailed information
        return [
            {"id": 1, "name": "John Doe - Detailed Documentation"},
            {"id": 2, "name": "Jane Smith - Detailed Documentation"},
            {"id": 3, "name": "Bob Johnson - Detailed Documentation"},
        ]
    else:
        raise HTTPException(status_code=400, detail="Invalid user type") 