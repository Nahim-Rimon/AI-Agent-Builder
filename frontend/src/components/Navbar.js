import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link to="/" className="navbar-logo">
          AI Agent Builder
        </Link>
        <div className="navbar-links">
          <Link to="/">Dashboard</Link>
          <button onClick={handleLogout} className="btn-link">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

