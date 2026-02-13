import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../../store/authStore';
import Button from '../common/Button';

const Header: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const renderNavLinks = () => {
    if (!user) return null;

    switch (user.role) {
      case 'participant':
        return (
          <>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/competitions">Competitions</Link>
          </>
        );
      case 'admitter':
        return <Link to="/admission">Admission</Link>;
      case 'scanner':
        return <Link to="/scans">Scans</Link>;
      case 'admin':
        return (
          <>
            <Link to="/admin">Dashboard</Link>
            <Link to="/admin/competitions">Competitions</Link>
            <Link to="/admin/users">Users</Link>
            <Link to="/admin/audit-log">Audit Log</Link>
          </>
        );
      default:
        return null;
    }
  };

  return (
    <header className="header">
      <div className="header-inner">
        <Link to="/" className="header-logo">
          OlimpQR
        </Link>
        <nav className="header-nav">
          {isAuthenticated ? (
            <>
              {renderNavLinks()}
              <span className="text-muted">{user?.email}</span>
              <Button variant="secondary" onClick={handleLogout}>
                Logout
              </Button>
            </>
          ) : (
            <>
              <Link to="/login">Login</Link>
              <Link to="/register">Register</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;
