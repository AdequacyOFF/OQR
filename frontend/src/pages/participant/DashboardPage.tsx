import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/client';
import type { Competition, Registration } from '../../types';
import Layout from '../../components/layout/Layout';
import Button from '../../components/common/Button';
import Spinner from '../../components/common/Spinner';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [competitions, setCompetitions] = useState<Competition[]>([]);
  const [registrations, setRegistrations] = useState<Registration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [registeringId, setRegisteringId] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [compRes, regRes] = await Promise.all([
        api.get<Competition[]>('/competitions'),
        api.get<Registration[]>('/registrations'),
      ]);
      setCompetitions(compRes.data);
      setRegistrations(regRes.data);
    } catch {
      setError('Failed to load data.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (competitionId: string) => {
    setRegisteringId(competitionId);
    try {
      const { data } = await api.post<Registration>('/registrations', {
        competition_id: competitionId,
      });
      setRegistrations((prev) => [...prev, data]);
      if (data.entry_token) {
        navigate(`/registrations/${data.id}/qr`);
      }
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Registration failed.';
      setError(message);
    } finally {
      setRegisteringId(null);
    }
  };

  const isRegistered = (competitionId: string) =>
    registrations.some((r) => r.competition_id === competitionId);

  if (loading) {
    return (
      <Layout>
        <Spinner />
      </Layout>
    );
  }

  return (
    <Layout>
      <h1 className="mb-24">Dashboard</h1>

      {error && <div className="alert alert-error mb-16">{error}</div>}

      <h2 className="mb-16">Competitions</h2>
      <div className="grid grid-2 mb-24">
        {competitions.length === 0 ? (
          <p className="text-muted">No competitions available.</p>
        ) : (
          competitions.map((comp) => (
            <div key={comp.id} className="card">
              <h3>{comp.name}</h3>
              <p className="text-muted">
                Date: {new Date(comp.date).toLocaleDateString()}
              </p>
              <p className="text-muted">Status: {comp.status}</p>
              <p className="text-muted">Max Score: {comp.max_score}</p>
              <div className="mt-16">
                {isRegistered(comp.id) ? (
                  <Button variant="secondary" disabled>
                    Registered
                  </Button>
                ) : comp.status === 'registration_open' ? (
                  <Button
                    onClick={() => handleRegister(comp.id)}
                    loading={registeringId === comp.id}
                  >
                    Register
                  </Button>
                ) : (
                  <span className="text-muted">Registration closed</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      <h2 className="mb-16">My Registrations</h2>
      {registrations.length === 0 ? (
        <p className="text-muted">No registrations yet.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Competition</th>
              <th>Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {registrations.map((reg) => {
              const comp = competitions.find((c) => c.id === reg.competition_id);
              return (
                <tr key={reg.id}>
                  <td>{comp?.name || reg.competition_id}</td>
                  <td>{reg.status}</td>
                  <td>{new Date(reg.created_at).toLocaleDateString()}</td>
                  <td>
                    <Button
                      variant="secondary"
                      className="btn-sm"
                      onClick={() => navigate(`/registrations/${reg.id}/qr`)}
                    >
                      View QR
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </Layout>
  );
};

export default DashboardPage;
