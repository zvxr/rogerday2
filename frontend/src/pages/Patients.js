import React, { useState, useEffect } from 'react';
import { patientsAPI } from '../services/api';
import Navbar from '../components/Navbar';

const Patients = () => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const data = await patientsAPI.getPatients();
        setPatients(data);
      } catch (err) {
        setError('Failed to load patients. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchPatients();
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
                <div key={patient.id} className="patient-item">
                  <h3>Patient ID: {patient.id}</h3>
                  <p><strong>Name:</strong> {patient.name}</p>
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