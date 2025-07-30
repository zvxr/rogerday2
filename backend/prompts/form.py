from typing import Dict, Any, List
from app.models.user import UserType
from app.models.form import Form
from app.models.patient import Patient
from app.logger import get_logger

logger = get_logger("prompts")


def format_form_data_for_prompt(form: Form, patient: Patient) -> str:
    """Format form data into a readable string for the prompt"""
    
    # Start with patient information
    prompt_data = f"""
PATIENT INFORMATION:
- Name: {patient.name}
- Date of Birth: {patient.dob}
- Gender: {patient.gender}
- MRN: {patient.mrn}
- Address: {patient.address}
- Phone: {patient.phone}
- Email: {patient.email}

VISIT INFORMATION:
- Form Type: {form.form_type}
- Visit Date: {form.form_date}
- Form ID: {form.form_id}

FORM DATA:
"""
    
    # Add form data by category
    for form_type, categories in form.survey_data.items():
        prompt_data += f"\n{form_type.upper()}:\n"
        
        for category, fields in categories.items():
            prompt_data += f"\n  {category}:\n"
            
            for field_name, field_data in fields.items():
                question = field_data.get('question_description', field_name)
                value = field_data.get('value')
                
                if value is not None and value != '':
                    prompt_data += f"    - {question}: {value}\n"
    
    return prompt_data


def generate_field_clinician_prompt(form: Form, patient: Patient) -> str:
    """Generate prompt for Field Clinicians - quick, mobile-friendly summaries"""
    
    form_data = format_form_data_for_prompt(form, patient)
    
    prompt = f"""You are a medical AI assistant helping field clinicians prepare for patient visits. 

Your task is to create a concise, mobile-friendly summary of this patient's visit data. The summary should be:
- Approximately 400 words or less
- Focused on key clinical information needed before a visit
- Easy to read on a mobile device
- Highlight important findings, medications, and care needs
- Use clear, professional medical language

{form_data}

Please provide a structured summary in MARKDOWN format with appropriate emojis for each section:

# 🏥 Patient Visit Summary

## 👤 Demographics & Context
- Include patient name, age, visit date, location, language, support system

## 🩺 Clinical Status
- Primary diagnosis, vital signs, recent assessments

## 💊 Medications
- Current medication list with dosages

## 🚶 Functional Status
- Mobility, ADLs, activity tolerance

## 🎯 Care Needs
- Monitoring requirements, treatment plan, interventions needed

## ⚠️ Alerts & Important Notes
- Safety concerns, upcoming appointments, caregiver notes

Format the response as clean markdown with emojis, suitable for quick review before a patient visit."""

    return prompt


def generate_quality_administrator_prompt(form: Form, patient: Patient) -> str:
    """Generate prompt for Quality Administrators - detailed documentation review"""
    
    form_data = format_form_data_for_prompt(form, patient)
    
    # Extract H&P summary data for comparison
    h_and_p_data = ""
    if patient.xml_data:
        # Extract key information from XML data for comparison
        import re
        
        # Extract diagnoses
        diagnoses_match = re.search(r'<diagnosis>(.*?)</diagnosis>', patient.xml_data, re.DOTALL | re.IGNORECASE)
        if diagnoses_match:
            h_and_p_data += f"\nH&P DIAGNOSES:\n{diagnoses_match.group(1).strip()}\n"
        
        # Extract medications
        meds_match = re.search(r'<medications>(.*?)</medications>', patient.xml_data, re.DOTALL | re.IGNORECASE)
        if meds_match:
            h_and_p_data += f"\nH&P MEDICATIONS:\n{meds_match.group(1).strip()}\n"
        
        # Extract allergies
        allergies_match = re.search(r'<allergies>(.*?)</allergies>', patient.xml_data, re.DOTALL | re.IGNORECASE)
        if allergies_match:
            h_and_p_data += f"\nH&P ALLERGIES:\n{allergies_match.group(1).strip()}\n"
        
        # Extract vital signs
        vitals_match = re.search(r'<vital_signs>(.*?)</vital_signs>', patient.xml_data, re.DOTALL | re.IGNORECASE)
        if vitals_match:
            h_and_p_data += f"\nH&P VITAL SIGNS:\n{vitals_match.group(1).strip()}\n"
    
    prompt = f"""You are a medical AI assistant helping quality administrators review documentation for insurance claims and compliance.

Your task is to create a comprehensive, detailed analysis comparing the patient's H&P summary with their form responses to identify potential discrepancies, documentation gaps, and compliance issues. The analysis should be:
- Thorough and detailed (800-1200 words)
- Focused on comparing H&P data with form responses
- Identify missing or inconsistent information
- Highlight potential insurance claim issues
- Flag compliance concerns and documentation gaps
- Provide specific recommendations for improvement

H&P SUMMARY DATA:
{h_and_p_data}

FORM RESPONSE DATA:
{form_data}

Please provide a structured analysis in MARKDOWN format with appropriate emojis for each section:

# 📋 Documentation Compliance Review Report

## 🔍 H&P vs Form Response Comparison
- Key diagnoses from H&P and their presence/absence in form responses
- Medication reconciliation between H&P and form data
- Vital signs consistency and documentation
- Allergy information completeness

## ⚠️ Critical Discrepancies & Missing Information
- Diagnoses mentioned in H&P but not addressed in forms
- Medications listed in H&P but not documented in responses
- Missing allergy documentation
- Inconsistent vital signs or assessment data

## 💰 Insurance Claim Risk Assessment
- Documentation gaps that could impact claim approval
- Missing supporting documentation for diagnoses
- Incomplete medication reconciliation
- Insufficient clinical justification for interventions

## 🏛️ Compliance & Regulatory Issues
- HIPAA compliance concerns
- Documentation standards violations
- Missing required assessments
- Incomplete care coordination documentation

## 📊 Documentation Quality Score
- Overall completeness score (0-100%)
- Critical gaps identification
- Documentation accuracy assessment

## 🔧 Specific Recommendations
- Immediate documentation corrections needed
- Missing assessments to be completed
- Follow-up actions required
- System improvements for better compliance

## 🎯 Priority Action Items
- High priority: Critical missing information
- Medium priority: Documentation improvements
- Low priority: Minor formatting or consistency issues

Format the response as detailed markdown with emojis, suitable for quality assurance review. Focus on actionable insights that help ensure proper documentation for insurance claims."""

    return prompt


def generate_summary_prompt(form: Form, patient: Patient, user_type: UserType) -> str:
    """Generate appropriate prompt based on user type"""
    
    logger.info(f"Generating prompt for user_type={user_type.value}, form_type={form.form_type}, patient={patient.name}")
    
    if user_type.value == "field_clinician":
        logger.debug("Using field clinician prompt")
        return generate_field_clinician_prompt(form, patient)
    elif user_type.value == "quality_administrator":
        logger.debug("Using quality administrator prompt")
        return generate_quality_administrator_prompt(form, patient)
    else:
        # Default to field clinician prompt for unknown user types
        logger.warning(f"Unknown user_type={user_type.value}, defaulting to field clinician prompt")
        return generate_field_clinician_prompt(form, patient) 