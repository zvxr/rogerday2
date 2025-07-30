from typing import Optional, Dict, Any, List
from beanie import Document
from pydantic import BaseModel


class Question(Document):
    qid: str  # Primary key - question ID
    description: str
    casting: Dict[str, Any]
    subitems: Optional[Dict[str, List[Dict[str, Any]]]] = None
    visit_type: Optional[str] = None  # SOC, ROC, etc.
    category: Optional[str] = None  # Patient_Tracking, etc.
    
    class Settings:
        name = "questions"
        indexes = [
            "qid",
            "visit_type",
            "category"
        ]


class QuestionResponse(BaseModel):
    qid: str
    description: str
    casting: Dict[str, Any]
    subitems: Optional[Dict[str, List[Dict[str, Any]]]] = None
    visit_type: Optional[str] = None
    category: Optional[str] = None


class QuestionCreate(BaseModel):
    qid: str
    description: str
    casting: Dict[str, Any]
    subitems: Optional[Dict[str, List[Dict[str, Any]]]] = None
    visit_type: Optional[str] = None
    category: Optional[str] = None 