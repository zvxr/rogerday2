from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.models.user import User
from app.models.form import Form, FormResponse
from app.models.patient import Patient
from app.routers.auth import get_current_user
from services.claude import get_claude_service
from prompts.form import generate_summary_prompt
from app.core.cache import get_cache_client
from pydantic import BaseModel
from app.logger import get_logger

logger = get_logger("forms_router")

# Test logging on module import
logger.info("Forms router module loaded")

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


@router.get("/{form_id}/summary", response_model=SummaryResponse)
async def get_form_summary(
    form_id: int, 
    current_user: User = Depends(get_current_user)
):
    """Get a cached visit summary"""
    
    logger.info(f"Getting cached summary for form_id={form_id}, user={current_user.username}")
    
    try:
        # Get the form to get patient_id
        form = await Form.find_one({"form_id": form_id})
        if not form:
            logger.error(f"Form not found: form_id={form_id}")
            raise HTTPException(status_code=404, detail="Form not found")
        
        # Try to get cached summary
        cache_client = await get_cache_client()
        cached_summary = await cache_client.get_summary(
            current_user.username, 
            form.patient_id, 
            form_id
        )
        
        if cached_summary:
            logger.info(f"Returning cached summary for form_id={form_id}")
            return SummaryResponse(**cached_summary)
        else:
            logger.info(f"No cached summary found for form_id={form_id}")
            raise HTTPException(status_code=404, detail="No cached summary found")
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_form_summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving summary: {str(e)}")


@router.post("/{form_id}/summarize", response_model=SummaryResponse)
async def summarize_form(
    form_id: int, 
    current_user: User = Depends(get_current_user)
):
    """Generate a visit summary using Claude AI based on user type"""
    
    logger.info(f"Starting summary generation for form_id={form_id}, user={current_user.username}, user_type={current_user.user_type.value}")
    
    try:
        # Get the form
        logger.debug(f"Fetching form with form_id={form_id}")
        form = await Form.find_one({"form_id": form_id})
        if not form:
            logger.error(f"Form not found: form_id={form_id}")
            raise HTTPException(status_code=404, detail="Form not found")
        
        logger.info(f"Found form: form_id={form_id}, patient_id={form.patient_id}, form_type={form.form_type}")
        
        # Get the patient
        logger.debug(f"Fetching patient with patient_id={form.patient_id}")
        patient = await Patient.find_one({"patient_id": form.patient_id})
        if not patient:
            logger.error(f"Patient not found: patient_id={form.patient_id}")
            raise HTTPException(status_code=404, detail="Patient not found")
        
        logger.info(f"Found patient: patient_id={patient.patient_id}, name={patient.name}")
        
        # Generate the appropriate prompt based on user type
        logger.debug(f"Generating prompt for user_type={current_user.user_type.value}")
        prompt = generate_summary_prompt(form, patient, current_user.user_type)
        logger.debug(f"Generated prompt length: {len(prompt)} characters")
        
        # Get Claude service and generate summary
        logger.debug("Getting Claude service")
        claude_service = get_claude_service()
        
        # Set max tokens based on user type
        max_tokens = 1500 if current_user.user_type.value == "quality_administrator" else 800
        logger.info(f"Generating summary with max_tokens={max_tokens}")
        
        summary = await claude_service.generate_summary(prompt, max_tokens)
        logger.info(f"Summary generated successfully, length: {len(summary)} characters")
        
        # Create response object
        summary_response = SummaryResponse(
            summary=summary,
            user_type=current_user.user_type.value,
            form_id=form_id
        )
        
        # Cache the summary
        logger.debug("Caching generated summary")
        cache_client = await get_cache_client()
        await cache_client.set_summary(
            current_user.username,
            form.patient_id,
            form_id,
            summary_response.dict()
        )
        
        return summary_response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in summarize_form: {str(e)}", exc_info=True)
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