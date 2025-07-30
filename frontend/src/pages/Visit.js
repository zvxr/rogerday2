import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { patientsAPI, formsAPI } from '../services/api';
import ReactMarkdown from 'react-markdown';
import './Visit.css';

const Visit = () => {
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
                  const mostRecentForm = formsData[0]; // Assuming forms are ordered by date
                  loadSummary(mostRecentForm.form_id);
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

  const loadSummary = async (formId) => { // New function to load cached or generate summary
    try {
      setSummaryLoading(true);
      setSummaryError(null);
      
      // First try to get cached summary
      try {
        console.log(`Attempting to load cached summary for form ${formId}...`);
        const cachedSummary = await formsAPI.getFormSummary(formId);
        setSummary(cachedSummary);
        console.log('✅ Cache HIT: Using cached summary');
        return; // Exit early if we got cached data
      } catch (cacheError) {
        // If no cached summary (404), generate a new one
        if (cacheError.response && cacheError.response.status === 404) {
          console.log('❌ Cache MISS: No cached summary found, generating new one...');
          const summaryData = await formsAPI.summarizeForm(formId);
          setSummary(summaryData);
          console.log('✅ Generated and cached new summary');
        } else {
          // If it's not a 404, it's a real error
          console.error('❌ Error loading cached summary:', cacheError);
          throw cacheError;
        }
      }
    } catch (err) {
      setSummaryError('Failed to load summary. Please try again.');
      console.error('Error loading summary:', err);
    } finally {
      setSummaryLoading(false);
    }
  };

  const refreshSummary = async () => { // New function to force refresh summary
    if (forms.length > 0) {
      const mostRecentForm = forms[0];
      console.log('🔄 Force refreshing summary...');
      await generateSummary(mostRecentForm.form_id);
      console.log('✅ Summary refreshed and cached');
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
      <div className="visit-header">
        <h1>Visit Details</h1>
        <div className="header-buttons">
          <button className="refresh-button" onClick={refreshSummary} disabled={summaryLoading}>
            🔄 Refresh
          </button>
          <button className="back-button" onClick={() => navigate(-1)}>
            ← Back
          </button>
        </div>
      </div>
      
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