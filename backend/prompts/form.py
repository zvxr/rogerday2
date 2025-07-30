from typing import Dict, Any, List
from app.models.user import UserType
from app.models.form import Form
from app.models.patient import Patient


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

Please provide a structured summary that includes:
1. Key patient demographics and visit context
2. Primary clinical findings and assessments
3. Current medications and treatments
4. Functional status and mobility
5. Care needs and recommendations
6. Any alerts or important notes

Format the response as a clean, scannable summary suitable for quick review before a patient visit."""

    return prompt


def generate_quality_administrator_prompt(form: Form, patient: Patient) -> str:
    """Generate prompt for Quality Administrators - detailed documentation review"""
    
    form_data = format_form_data_for_prompt(form, patient)
    
    prompt = f"""You are a medical AI assistant helping quality administrators review documentation for insurance claims and compliance.

Your task is to create a comprehensive, detailed analysis of this patient's visit documentation. The analysis should be:
- Thorough and detailed (800-1200 words)
- Focused on documentation quality and completeness
- Identify potential issues for insurance claims
- Highlight compliance concerns
- Provide recommendations for documentation improvement

{form_data}

Please provide a structured analysis that includes:
1. Documentation completeness assessment
2. Clinical accuracy and consistency review
3. Insurance claim readiness evaluation
4. Compliance and regulatory considerations
5. Risk factors and documentation gaps
6. Specific recommendations for improvement
7. Quality metrics and scoring

Format the response as a detailed report suitable for quality assurance review."""

    return prompt


def generate_summary_prompt(form: Form, patient: Patient, user_type: UserType) -> str:
    """Generate appropriate prompt based on user type"""
    
    if user_type == UserType.field_clinician:
        return generate_field_clinician_prompt(form, patient)
    elif user_type == UserType.quality_administrator:
        return generate_quality_administrator_prompt(form, patient)
    else:
        # Default to field clinician prompt for unknown user types
        return generate_field_clinician_prompt(form, patient) 