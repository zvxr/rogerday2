import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { patientsAPI, formsAPI } from '../services/api';
import './Visit.css';

const Visit = () => {
  const { patientId } = useParams();
  const [patient, setPatient] = useState(null);
  const [forms, setForms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [patientData, formsData] = await Promise.all([
          patientsAPI.getPatient(patientId),
          formsAPI.getFormsByPatient(patientId)
        ]);
        setPatient(patientData);
        setForms(formsData);
        
        // Generate summary for the most recent form
        if (formsData.length > 0) {
          const mostRecentForm = formsData[0]; // Assuming forms are ordered by date
          generateSummary(mostRecentForm.form_id);
        }
      } catch (err) {
        setError('Failed to load visit data');
        console.error('Error fetching visit data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [patientId]);

  const getFormTypeDisplayName = (formType) => {
    const typeMap = {
      'PTVIS': 'Physical Therapy Visit',
      'PTEVAL': 'Physical Therapy Evaluation',
      'SOC': 'Start of Care',
      'RN': 'Registered Nurse',
      'DC': 'Discharge'
    };
    return typeMap[formType] || formType;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const getAnsweredQuestionsCount = (surveyData) => {
    let count = 0;
    for (const formType in surveyData) {
      for (const category in surveyData[formType]) {
        for (const fieldName in surveyData[formType][category]) {
          const fieldData = surveyData[formType][category][fieldName];
          if (fieldData.value !== null && fieldData.value !== undefined && fieldData.value !== '') {
            count++;
          }
        }
      }
    }
    return count;
  };

  const getAnsweredQuestions = (surveyData) => {
    const questions = [];
    for (const formType in surveyData) {
      for (const category in surveyData[formType]) {
        for (const fieldName in surveyData[formType][category]) {
          const fieldData = surveyData[formType][category][fieldName];
          if (fieldData.value !== null && fieldData.value !== undefined && fieldData.value !== '') {
            questions.push({
              question: fieldData.question_description || fieldName,
              answer: fieldData.value
            });
          }
        }
      }
    }
    return questions;
  };

  const generateSummary = async (formId) => {
    try {
      setSummaryLoading(true);
      setSummaryError(null);
      const summaryData = await formsAPI.summarizeForm(formId);
      setSummary(summaryData);
    } catch (err) {
      setSummaryError('Failed to generate summary. Please try again.');
      console.error('Error generating summary:', err);
    } finally {
      setSummaryLoading(false);
    }
  };

  if (loading) {
    return <div className="visit-container">Loading visit data...</div>;
  }

  if (error) {
    return <div className="visit-container error">{error}</div>;
  }

  if (!patient) {
    return <div className="visit-container error">Patient not found</div>;
  }

  return (
    <div className="visit-container">
      <h1>Visit Details</h1>
      
      {/* Visit Summary Section */}
      <details className="summary-section" open>
        <summary>Visit Summary</summary>
        <div className="summary-content">
          {summaryLoading && (
            <div className="summary-loading">
              <div className="spinner"></div>
              <p>Summarizing visit data...</p>
            </div>
          )}
          {summaryError && (
            <div className="summary-error">
              {summaryError}
            </div>
          )}
          {summary && !summaryLoading && (
            <div className="summary-text">
              <div className="summary-header">
                <span className="summary-type">{getFormTypeDisplayName(summary.user_type)}</span>
                <span className="summary-form-id">Form ID: {summary.form_id}</span>
              </div>
              <div className="summary-body">
                {summary.summary.split('\n').map((paragraph, index) => (
                  <p key={index}>{paragraph}</p>
                ))}
              </div>
            </div>
          )}
        </div>
      </details>
      
      {/* Patient Information Section */}
      <details className="patient-section">
        <summary>Patient Information</summary>
        <div className="patient-details">
          <div className="patient-grid">
            <div><strong>Name:</strong> {patient.name}</div>
            <div><strong>Date of Birth:</strong> {formatDate(patient.dob)}</div>
            <div><strong>Gender:</strong> {patient.gender}</div>
            <div><strong>MRN:</strong> {patient.mrn}</div>
            <div><strong>Address:</strong> {patient.address}</div>
            <div><strong>Phone:</strong> {patient.phone}</div>
            <div><strong>Email:</strong> {patient.email}</div>
          </div>
        </div>
      </details>

      {/* Forms Section */}
      <details className="forms-section">
        <summary>Forms ({forms.length})</summary>
        <div className="forms-list">
          {forms.map((form) => (
            <details key={form.form_id} className="form-item">
              <summary>
                <div className="form-summary">
                  <span className="form-type">{getFormTypeDisplayName(form.form_type)}</span>
                  <span className="form-date">{formatDate(form.form_date)}</span>
                  <span className="form-count">{getAnsweredQuestionsCount(form.survey_data)} questions answered</span>
                </div>
              </summary>
              <div className="form-details">
                <div className="questions-grid">
                  <div className="grid-header">
                    <div className="question-header">Question</div>
                    <div className="answer-header">Answer</div>
                  </div>
                  {getAnsweredQuestions(form.survey_data).map((item, index) => (
                    <div key={index} className="question-row">
                      <div className="question">{item.question}</div>
                      <div className="answer">{String(item.answer)}</div>
                    </div>
                  ))}
                </div>
              </div>
            </details>
          ))}
        </div>
      </details>
    </div>
  );
};

export default Visit; 