from typing import Optional, Union
from datetime import date, datetime
from beanie import Document
from pydantic import BaseModel, EmailStr, Field, field_validator


class Patient(Document):
    patient_id: int
    name: str
    dob: Optional[Union[date, datetime]] = None
    gender: str
    mrn: int = Field(ge=0)  # Medical Record Number as bigint
    address: str
    phone: str
    email: EmailStr
    xml_data: Optional[str] = None  # Store the full XML content
    
    @field_validator('dob', mode='before')
    @classmethod
    def validate_dob(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.date()
        return v
    
    class Settings:
        name = "patients"
        indexes = [
            "patient_id",
            "mrn",
            "name"
        ]


class PatientResponse(BaseModel):
    patient_id: int
    name: str
    dob: Optional[Union[date, datetime]] = None
    gender: str
    mrn: int
    address: str
    phone: str
    email: EmailStr
    xml_data: Optional[str] = None
    
    @field_validator('dob', mode='before')
    @classmethod
    def validate_dob(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.date()
        return v


class PatientCreate(BaseModel):
    name: str
    dob: date
    gender: str
    mrn: int = Field(ge=0)
    address: str
    phone: str
    email: EmailStr
    xml_data: Optional[str] = None 