from typing import Optional
from beanie import Document
from pydantic import BaseModel


class Patient(Document):
    id: int
    name: str
    # Add more fields as needed
    
    class Settings:
        name = "patients"
        indexes = [
            "id"
        ]


class PatientResponse(BaseModel):
    id: int
    name: str 