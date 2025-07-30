from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.models.user import User
from app.models.form import Form, FormResponse
from app.models.patient import Patient
from app.routers.auth import get_current_user
from services.claude import get_claude_service
from prompts.form import generate_summary_prompt
from pydantic import BaseModel

router = APIRouter(prefix="/forms", tags=["forms"])


@router.get("/", response_model=List[FormResponse])
async def get_forms(
    patient_id: Optional[int] = None,
    form_type: Optional[str] = None,
    exclude_null: Optional[bool] = False,
    current_user: User = Depends(get_current_user)
):
    """Get forms with optional filtering by patient_id and form_type"""
    query = {}
    if patient_id:
        query["patient_id"] = patient_id
    if form_type:
        query["form_type"] = form_type
    
    forms = await Form.find(query).to_list()
    
    def filter_null_values(survey_data):
        """Filter out null values from survey data"""
        if not exclude_null:
            return survey_data
        
        filtered_data = {}
        for form_type, categories in survey_data.items():
            filtered_data[form_type] = {}
            for category, fields in categories.items():
                filtered_data[form_type][category] = {}
                for field_name, field_data in fields.items():
                    if field_data.get('value') is not None and field_data.get('value') != '':
                        filtered_data[form_type][category][field_name] = field_data
        return filtered_data
    
    return [
        FormResponse(
            form_id=f.form_id,
            patient_id=f.patient_id,
            form_date=f.form_date,
            form_type=f.form_type,
            survey_data=filter_null_values(f.survey_data)
        ) for f in forms
    ]


class SummaryResponse(BaseModel):
    summary: str
    user_type: str
    form_id: int


@router.post("/{form_id}/summarize", response_model=SummaryResponse)
async def summarize_form(
    form_id: int, 
    current_user: User = Depends(get_current_user)
):
    """Generate a visit summary using Claude AI based on user type"""
    
    # Get the form
    form = await Form.find_one({"form_id": form_id})
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # Get the patient
    patient = await Patient.find_one({"patient_id": form.patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    try:
        # Generate the appropriate prompt based on user type
        prompt = generate_summary_prompt(form, patient, current_user.user_type)
        
        # Get Claude service and generate summary
        claude_service = get_claude_service()
        
        # Set max tokens based on user type
        max_tokens = 1500 if current_user.user_type.value == "quality_administrator" else 800
        
        summary = await claude_service.generate_summary(prompt, max_tokens)
        
        return SummaryResponse(
            summary=summary,
            user_type=current_user.user_type.value,
            form_id=form_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@router.get("/{form_id}", response_model=FormResponse)
async def get_form_by_id(
    form_id: int, 
    exclude_null: Optional[bool] = False,
    current_user: User = Depends(get_current_user)
):
    """Get a specific form by form_id"""
    form = await Form.find_one({"form_id": form_id})
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    def filter_null_values(survey_data):
        """Filter out null values from survey data"""
        if not exclude_null:
            return survey_data
        
        filtered_data = {}
        for form_type, categories in survey_data.items():
            filtered_data[form_type] = {}
            for category, fields in categories.items():
                filtered_data[form_type][category] = {}
                for field_name, field_data in fields.items():
                    if field_data.get('value') is not None and field_data.get('value') != '':
                        filtered_data[form_type][category][field_name] = field_data
        return filtered_data
    
    return FormResponse(
        form_id=form.form_id,
        patient_id=form.patient_id,
        form_date=form.form_date,
        form_type=form.form_type,
        survey_data=filter_null_values(form.survey_data)
    )


@router.get("/patient/{patient_id}", response_model=List[FormResponse])
async def get_forms_by_patient(
    patient_id: int, 
    exclude_null: Optional[bool] = False,
    current_user: User = Depends(get_current_user)
):
    """Get all forms for a specific patient"""
    forms = await Form.find({"patient_id": patient_id}).to_list()
    
    def filter_null_values(survey_data):
        """Filter out null values from survey data"""
        if not exclude_null:
            return survey_data
        
        filtered_data = {}
        for form_type, categories in survey_data.items():
            filtered_data[form_type] = {}
            for category, fields in categories.items():
                filtered_data[form_type][category] = {}
                for field_name, field_data in fields.items():
                    if field_data.get('value') is not None and field_data.get('value') != '':
                        filtered_data[form_type][category][field_name] = field_data
        return filtered_data
    
    return [
        FormResponse(
            form_id=f.form_id,
            patient_id=f.patient_id,
            form_date=f.form_date,
            form_type=f.form_type,
            survey_data=filter_null_values(f.survey_data)
        ) for f in forms
    ] 