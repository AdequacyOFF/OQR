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
        api.get<{ competitions: Competition[]; total: number }>('competitions'),
        api.get<{ items: Registration[]; total: number }>('registrations'),
      ]);
      setCompetitions(compRes.data.competitions || []);
      setRegistrations(regRes.data.items || []);
    } catch {
      setError('Не удалось загрузить данные.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (competitionId: string) => {
    setRegisteringId(competitionId);
    try {
      const { data } = await api.post<Registration>('registrations', {
        competition_id: competitionId,
      });
      setRegistrations((prev) => [...prev, data]);
      if (data.entry_token) {
        navigate(`/registrations/${data.id}/qr`);
      }
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Ошибка регистрации.';
      setError(message);
    } finally {
      setRegisteringId(null);
    }
  };

  const isRegistered = (competitionId: string) =>
    registrations.some((r) => r.competition_id === competitionId);

  const getStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      draft: 'Черновик',
      registration_open: 'Регистрация открыта',
      in_progress: 'Проходит',
      finished: 'Завершена',
      published: 'Результаты опубликованы',
    };
    return labels[status] || status;
  };

  const getRegStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      registered: 'Зарегистрирован',
      admitted: 'Допущен',
      completed: 'Завершен',
      cancelled: 'Отменен',
    };
    return labels[status] || status;
  };

  if (loading) {
    return (
      <Layout>
        <Spinner />
      </Layout>
    );
  }

  return (
    <Layout>
      <h1 className="mb-24">Личный кабинет</h1>

      {error && <div className="alert alert-error mb-16">{error}</div>}

      <h2 className="mb-16">Доступные олимпиады</h2>
      <div className="grid grid-2 mb-24">
        {competitions.length === 0 ? (
          <p className="text-muted">Нет доступных олимпиад.</p>
        ) : (
          competitions.map((comp) => (
            <div key={comp.id} className="card">
              <h3>{comp.name}</h3>
              <p className="text-muted">
                Дата: {new Date(comp.date).toLocaleDateString('ru-RU')}
              </p>
              <p className="text-muted">Статус: {getStatusLabel(comp.status)}</p>
              <p className="text-muted">Макс. балл: {comp.max_score}</p>
              <div className="mt-16">
                {isRegistered(comp.id) ? (
                  <Button variant="secondary" disabled>
                    Зарегистрирован
                  </Button>
                ) : comp.status === 'registration_open' ? (
                  <Button
                    onClick={() => handleRegister(comp.id)}
                    loading={registeringId === comp.id}
                  >
                    Зарегистрироваться
                  </Button>
                ) : (
                  <span className="text-muted">Регистрация закрыта</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      <h2 className="mb-16">Мои регистрации</h2>
      {registrations.length === 0 ? (
        <p className="text-muted">Нет регистраций.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Олимпиада</th>
              <th>Статус</th>
              <th>Дата</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {registrations.map((reg) => {
              const comp = competitions.find((c) => c.id === reg.competition_id);
              return (
                <tr key={reg.id}>
                  <td>{comp?.name || reg.competition_id}</td>
                  <td>{getRegStatusLabel(reg.status)}</td>
                  <td>{new Date(reg.created_at).toLocaleDateString('ru-RU')}</td>
                  <td>
                    <Button
                      variant="secondary"
                      className="btn-sm"
                      onClick={() => navigate(`/registrations/${reg.id}/qr`)}
                    >
                      Показать QR
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
