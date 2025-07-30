import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { patientsAPI, authAPI } from '../services/api';
import Navbar from '../components/Navbar';

const Patients = () => {
  const [patients, setPatients] = useState([]);
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [patientsData, userData] = await Promise.all([
          patientsAPI.getPatients(),
          authAPI.getCurrentUser()
        ]);
        
        setPatients(patientsData);
        setUserInfo(userData);
      } catch (err) {
        setError('Failed to load data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div>
        <Navbar />
        <div className="container">
          <div className="dashboard">
            <h1>Patients</h1>
            <p>Loading patients...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Navbar />
      <div className="container">
        <div className="dashboard">
          <h1>Patients</h1>
          
          {error && <div className="error">{error}</div>}
          
          <div className="patient-list">
            {patients.length === 0 ? (
              <p>No patients found.</p>
            ) : (
              patients.map((patient) => (
                <div key={patient.patient_id} className="patient-item">
                  <details>
                    <summary className="patient-summary">
                      <div className="patient-header">
                        <h3>{patient.name}</h3>
                        <Link 
                          to={userInfo?.user_type === 'quality_administrator' 
                            ? `/review/${patient.patient_id}` 
                            : `/visit/${patient.patient_id}`} 
                          className={userInfo?.user_type === 'quality_administrator' 
                            ? 'review-button' 
                            : 'visit-button'}
                        >
                          {userInfo?.user_type === 'quality_administrator' ? 'Review' : 'Visit'}
                        </Link>
                      </div>
                    </summary>
                    <div className="patient-details">
                      <p><strong>Patient ID:</strong> {patient.patient_id}</p>
                      <p><strong>Date of Birth:</strong> {patient.dob ? new Date(patient.dob).toLocaleDateString() : 'Not available'}</p>
                      <p><strong>Gender:</strong> {patient.gender}</p>
                      <p><strong>MRN:</strong> {patient.mrn}</p>
                      <p><strong>Address:</strong> {patient.address}</p>
                      <p><strong>Phone:</strong> {patient.phone}</p>
                      <p><strong>Email:</strong> {patient.email}</p>
                      {patient.xml_data && (
                        <details>
                          <summary>View XML Data</summary>
                          <pre style={{ 
                            background: '#f5f5f5', 
                            padding: '10px', 
                            overflow: 'auto', 
                            maxHeight: '200px',
                            fontSize: '12px'
                          }}>
                            {patient.xml_data}
                          </pre>
                        </details>
                      )}
                    </div>
                  </details>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Patients; 