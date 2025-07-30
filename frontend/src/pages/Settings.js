import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { authAPI } from '../services/api';

const Settings = () => {
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUserInfo = async () => {
      try {
        const userData = await authAPI.getCurrentUser();
        
        // Map user types to human-readable names
        const userTypeMap = {
          'field_clinician': 'Field Clinician',
          'quality_administrator': 'Quality Administrator'
        };

        setUserInfo({
          username: userData.username,
          userType: userTypeMap[userData.user_type] || userData.user_type
        });
      } catch (err) {
        setError('Failed to load user information');
      } finally {
        setLoading(false);
      }
    };

    fetchUserInfo();
  }, []);

  if (loading) {
    return (
      <div>
        <Navbar />
        <div className="container">
          <div className="dashboard">
            <h1>Settings</h1>
            <p>Loading user information...</p>
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
          <h1>Settings</h1>
          
          {error && <div className="error">{error}</div>}
          
          {userInfo && (
            <div className="settings-container">
              <div className="setting-item">
                <h3>Username</h3>
                <p>{userInfo.username}</p>
              </div>
              
              <div className="setting-item">
                <h3>User Type</h3>
                <p>{userInfo.userType}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings; 