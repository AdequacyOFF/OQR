import React, { useEffect, useState } from 'react';
import api from '../../api/client';
import type { AuditLogEntry } from '../../types';
import Layout from '../../components/layout/Layout';
import Spinner from '../../components/common/Spinner';

const AuditLogPage: React.FC = () => {
  const [entries, setEntries] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [entityTypeFilter, setEntityTypeFilter] = useState('');
  const [actionFilter, setActionFilter] = useState('');

  useEffect(() => {
    loadEntries();
  }, []);

  const loadEntries = async () => {
    setLoading(true);
    try {
      const { data } = await api.get<AuditLogEntry[]>('/admin/audit-log');
      setEntries(data);
    } catch {
      setError('Failed to load audit log.');
    } finally {
      setLoading(false);
    }
  };

  const entityTypes = [...new Set(entries.map((e) => e.entity_type))];
  const actions = [...new Set(entries.map((e) => e.action))];

  const filteredEntries = entries.filter((entry) => {
    if (entityTypeFilter && entry.entity_type !== entityTypeFilter) return false;
    if (actionFilter && entry.action !== actionFilter) return false;
    return true;
  });

  if (loading) {
    return (
      <Layout>
        <Spinner />
      </Layout>
    );
  }

  return (
    <Layout>
      <h1 className="mb-24">Audit Log</h1>

      {error && <div className="alert alert-error mb-16">{error}</div>}

      <div className="flex gap-16 mb-16">
        <div className="form-group" style={{ minWidth: 180 }}>
          <label>Entity Type</label>
          <select
            className="input"
            value={entityTypeFilter}
            onChange={(e) => setEntityTypeFilter(e.target.value)}
          >
            <option value="">All</option>
            {entityTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>
        <div className="form-group" style={{ minWidth: 180 }}>
          <label>Action</label>
          <select
            className="input"
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
          >
            <option value="">All</option>
            {actions.map((action) => (
              <option key={action} value={action}>
                {action}
              </option>
            ))}
          </select>
        </div>
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Entity Type</th>
            <th>Entity ID</th>
            <th>Action</th>
            <th>User ID</th>
            <th>IP Address</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          {filteredEntries.length === 0 ? (
            <tr>
              <td colSpan={7} className="text-center text-muted">
                No entries found.
              </td>
            </tr>
          ) : (
            filteredEntries.map((entry) => (
              <tr key={entry.id}>
                <td>{new Date(entry.timestamp).toLocaleString()}</td>
                <td>{entry.entity_type}</td>
                <td style={{ fontSize: 12 }}>{entry.entity_id.slice(0, 8)}...</td>
                <td>{entry.action}</td>
                <td style={{ fontSize: 12 }}>
                  {entry.user_id ? `${entry.user_id.slice(0, 8)}...` : '-'}
                </td>
                <td>{entry.ip_address || '-'}</td>
                <td style={{ fontSize: 12, maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {JSON.stringify(entry.details)}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </Layout>
  );
};

export default AuditLogPage;
