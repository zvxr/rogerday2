from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.models.user import User
from app.models.question import Question, QuestionResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/{qid}", response_model=QuestionResponse)
async def get_question_by_qid(qid: str, current_user: User = Depends(get_current_user)):
    """Get a specific question by qid"""
    question = await Question.find_one({"qid": qid})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return QuestionResponse(
        qid=question.qid,
        description=question.description,
        casting=question.casting,
        subitems=question.subitems,
        visit_type=question.visit_type,
        category=question.category
    )


@router.get("/", response_model=List[QuestionResponse])
async def get_questions(
    visit_type: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get questions with optional filtering by visit_type and category"""
    query = {}
    if visit_type:
        query["visit_type"] = visit_type
    if category:
        query["category"] = category
    
    questions = await Question.find(query).to_list()
    
    return [
        QuestionResponse(
            qid=q.qid,
            description=q.description,
            casting=q.casting,
            subitems=q.subitems,
            visit_type=q.visit_type,
            category=q.category
        ) for q in questions
    ] 