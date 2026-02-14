import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/layout/Layout';

const AdminDashboardPage: React.FC = () => {
  return (
    <Layout>
      <h1 className="mb-24">Панель администратора</h1>
      <div className="grid grid-3">
        <Link to="/admin/competitions" style={{ textDecoration: 'none' }}>
          <div className="card text-center">
            <h2>Олимпиады</h2>
            <p className="text-muted mt-16">Управление олимпиадами, статусами и настройками</p>
          </div>
        </Link>
        <Link to="/admin/users" style={{ textDecoration: 'none' }}>
          <div className="card text-center">
            <h2>Пользователи</h2>
            <p className="text-muted mt-16">Управление аккаунтами и ролями</p>
          </div>
        </Link>
        <Link to="/admin/audit-log" style={{ textDecoration: 'none' }}>
          <div className="card text-center">
            <h2>Журнал действий</h2>
            <p className="text-muted mt-16">Просмотр активности и изменений в системе</p>
          </div>
        </Link>
      </div>

      <div className="card mt-16">
        <h2 className="mb-16">Краткая статистика</h2>
        <div className="grid grid-3">
          <div className="text-center">
            <p className="text-muted">Всего олимпиад</p>
            <p style={{ fontSize: 28, fontWeight: 700 }}>--</p>
          </div>
          <div className="text-center">
            <p className="text-muted">Всего пользователей</p>
            <p style={{ fontSize: 28, fontWeight: 700 }}>--</p>
          </div>
          <div className="text-center">
            <p className="text-muted">Всего сканов</p>
            <p style={{ fontSize: 28, fontWeight: 700 }}>--</p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default AdminDashboardPage;
