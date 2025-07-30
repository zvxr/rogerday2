import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';

const Dashboard = () => {
  return (
    <div>
      <Navbar />
      <div className="container">
        <div className="dashboard">
          <h1>Welcome to Patient Dashboard</h1>
          <p>This is your main dashboard. You can navigate to different sections using the menu above.</p>
          
          <div style={{ marginTop: '30px' }}>
            <h2>Quick Actions</h2>
            <div style={{ display: 'flex', gap: '20px', marginTop: '15px' }}>
              <Link to="/patients" className="btn">
                View Patients
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 