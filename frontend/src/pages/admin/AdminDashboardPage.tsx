import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/layout/Layout';

const AdminDashboardPage: React.FC = () => {
  return (
    <Layout>
      <h1 className="mb-24">Admin Dashboard</h1>
      <div className="grid grid-3">
        <Link to="/admin/competitions" style={{ textDecoration: 'none' }}>
          <div className="card text-center">
            <h2>Competitions</h2>
            <p className="text-muted mt-16">Manage competitions, statuses, and settings</p>
          </div>
        </Link>
        <Link to="/admin/users" style={{ textDecoration: 'none' }}>
          <div className="card text-center">
            <h2>Users</h2>
            <p className="text-muted mt-16">Manage user accounts and roles</p>
          </div>
        </Link>
        <Link to="/admin/audit-log" style={{ textDecoration: 'none' }}>
          <div className="card text-center">
            <h2>Audit Log</h2>
            <p className="text-muted mt-16">View system activity and changes</p>
          </div>
        </Link>
      </div>

      <div className="card mt-16">
        <h2 className="mb-16">Quick Stats</h2>
        <div className="grid grid-3">
          <div className="text-center">
            <p className="text-muted">Total Competitions</p>
            <p style={{ fontSize: 28, fontWeight: 700 }}>--</p>
          </div>
          <div className="text-center">
            <p className="text-muted">Total Users</p>
            <p style={{ fontSize: 28, fontWeight: 700 }}>--</p>
          </div>
          <div className="text-center">
            <p className="text-muted">Total Scans</p>
            <p style={{ fontSize: 28, fontWeight: 700 }}>--</p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default AdminDashboardPage;
