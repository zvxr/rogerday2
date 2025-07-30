from typing import Optional, Dict, Any, Union
from datetime import date, datetime
from enum import Enum
from beanie import Document
from pydantic import BaseModel, Field, field_validator


class FormType(str, Enum):
    PTVIS = "PTVIS"  # Physical Therapy Visit
    PTEVAL = "PTEVAL"  # Physical Therapy Evaluation
    SOC = "SOC"  # Start of Care
    RN = "RN"  # Registered Nurse
    DC = "DC"  # Discharge


class Form(Document):
    form_id: int  # Internal ID
    patient_id: int  # Patient associated with visit
    form_date: Union[date, datetime]  # Date for the visit
    form_type: FormType  # Type of form
    survey_data: Dict[str, Any]  # JSON object with form data
    
    @field_validator('form_date', mode='before')
    @classmethod
    def validate_form_date(cls, v):
        if isinstance(v, datetime):
            return v.date()
        return v
    
    class Settings:
        name = "forms"
        indexes = [
            "form_id",
            "patient_id",
            "form_date",
            "form_type"
        ]


class FormResponse(BaseModel):
    form_id: int
    patient_id: int
    form_date: Union[date, datetime]
    form_type: FormType
    survey_data: Dict[str, Any]
    
    @field_validator('form_date', mode='before')
    @classmethod
    def validate_form_date(cls, v):
        if isinstance(v, datetime):
            return v.date()
        return v


class FormCreate(BaseModel):
    patient_id: int
    form_date: Union[date, datetime]
    form_type: FormType
    survey_data: Dict[str, Any]
    
    @field_validator('form_date', mode='before')
    @classmethod
    def validate_form_date(cls, v):
        if isinstance(v, datetime):
            return v.date()
        return v 