import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { removeToken } from '../utils/auth';

const Navbar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    removeToken();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="container">
        <Link to="/dashboard">Patient Dashboard</Link>
        <Link to="/patients">Patients</Link>
        <button onClick={handleLogout} style={{ 
          background: 'none', 
          border: 'none', 
          color: 'white', 
          cursor: 'pointer',
          fontSize: '16px'
        }}>
          Logout
        </button>
      </div>
    </nav>
  );
};

export default Navbar; 