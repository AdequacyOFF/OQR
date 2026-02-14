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
            <Link to="/dashboard">Главная</Link>
            <Link to="/competitions">Олимпиады</Link>
          </>
        );
      case 'admitter':
        return <Link to="/admission">Допуск</Link>;
      case 'scanner':
        return <Link to="/scans">Сканы</Link>;
      case 'admin':
        return (
          <>
            <Link to="/admin">Главная</Link>
            <Link to="/admin/competitions">Олимпиады</Link>
            <Link to="/admin/users">Пользователи</Link>
            <Link to="/admin/audit-log">Журнал</Link>
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
                Выйти
              </Button>
            </>
          ) : (
            <>
              <Link to="/login">Вход</Link>
              <Link to="/register">Регистрация</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;
