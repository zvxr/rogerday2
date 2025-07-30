import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { patientsAPI, formsAPI } from '../services/api';
import ReactMarkdown from 'react-markdown';
import './Review.css';

const Review = () => {
  const { patientId } = useParams();
  const navigate = useNavigate();
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
        
        // Load summary for the most recent form (cached or generate)
        if (formsData.length > 0) {
          const mostRecentForm = formsData[0];
          loadSummary(mostRecentForm.form_id);
        }
      } catch (err) {
        setError('Failed to load review data');
        console.error('Error fetching review data:', err);
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
      setSummaryError('Failed to generate review summary. Please try again.');
      console.error('Error generating review summary:', err);
    } finally {
      setSummaryLoading(false);
    }
  };

  const loadSummary = async (formId) => {
    try {
      setSummaryLoading(true);
      setSummaryError(null);
      
      // First try to get cached summary
      try {
        console.log(`Attempting to load cached review summary for form ${formId}...`);
        const cachedSummary = await formsAPI.getFormSummary(formId);
        setSummary(cachedSummary);
        console.log('✅ Cache HIT: Using cached review summary');
        return;
      } catch (cacheError) {
        if (cacheError.response && cacheError.response.status === 404) {
          console.log('❌ Cache MISS: No cached review summary found, generating new one...');
          const summaryData = await formsAPI.summarizeForm(formId);
          setSummary(summaryData);
          console.log('✅ Generated and cached new review summary');
        } else {
          console.error('❌ Error loading cached review summary:', cacheError);
          throw cacheError;
        }
      }
    } catch (err) {
      setSummaryError('Failed to load review summary. Please try again.');
      console.error('Error loading review summary:', err);
    } finally {
      setSummaryLoading(false);
    }
  };

  const refreshSummary = async () => {
    if (forms.length > 0) {
      const mostRecentForm = forms[0];
      console.log('🔄 Force refreshing review summary...');
      await generateSummary(mostRecentForm.form_id);
      console.log('✅ Review summary refreshed and cached');
    }
  };

  if (loading) {
    return <div className="review-container">Loading review data...</div>;
  }

  if (error) {
    return <div className="review-container error">{error}</div>;
  }

  if (!patient) {
    return <div className="review-container error">Patient not found</div>;
  }

  return (
    <div className="review-container">
      <div className="review-header">
        <h1>Documentation Review</h1>
        <div className="header-buttons">
          <button className="refresh-button" onClick={refreshSummary} disabled={summaryLoading}>
            🔄 Refresh
          </button>
          <button className="back-button" onClick={() => navigate(-1)}>
            ← Back
          </button>
        </div>
      </div>
      
      {/* Documentation Review Summary Section */}
      <details className="summary-section" open>
        <summary>Documentation Review Summary</summary>
        <div className="summary-content">
          {summaryLoading && (
            <div className="summary-loading">
              <div className="spinner"></div>
              <p>Analyzing documentation for compliance...</p>
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
                <span className="summary-type">Quality Administrator Review</span>
                <span className="summary-form-id">Form ID: {summary.form_id}</span>
              </div>
              <div className="summary-body">
                <ReactMarkdown>{summary.summary}</ReactMarkdown>
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

      {/* Previous Visits Section */}
      <details className="forms-section">
        <summary>Previous Visits ({forms.length})</summary>
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
                  {getAnsweredQuestions(form.survey_data).map((q, index) => (
                    <div key={index} className="question-item">
                      <div className="question"><strong>Question:</strong> {q.question}</div>
                      <div className="answer"><strong>Answer:</strong> {q.answer}</div>
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

export default Review; 