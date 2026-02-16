import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../api/client';
import type { Registration } from '../../types';
import Layout from '../../components/layout/Layout';
import QRCodeDisplay from '../../components/qr/QRCodeDisplay';
import Spinner from '../../components/common/Spinner';
import Button from '../../components/common/Button';

const EntryQRPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [registration, setRegistration] = useState<Registration | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    const loadRegistration = async () => {
      try {
        const { data } = await api.get<Registration>(`registrations/${id}`);
        setRegistration(data);
      } catch {
        setError('Не удалось загрузить регистрацию.');
      } finally {
        setLoading(false);
      }
    };

    loadRegistration();
  }, [id]);

  const handleRefreshToken = async () => {
    if (!id) return;
    setRefreshing(true);
    setError(null);
    setSuccess(null);

    try {
      const { data } = await api.post<Registration>(`registrations/${id}/refresh-token`);
      setRegistration(data);
      setSuccess('QR-код успешно обновлён!');
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Не удалось обновить QR-код.';
      setError(message);
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <Spinner />
      </Layout>
    );
  }

  if (error || !registration) {
    return (
      <Layout>
        <div className="alert alert-error">{error || 'Регистрация не найдена.'}</div>
      </Layout>
    );
  }

  const token = registration.entry_token || registration.id;

  return (
    <Layout>
      <div className="card" style={{ maxWidth: 500, margin: '0 auto' }}>
        <h1 className="text-center mb-24">Входной QR-код</h1>

        {error && <div className="alert alert-error mb-16">{error}</div>}
        {success && <div className="alert alert-success mb-16">{success}</div>}

        <QRCodeDisplay value={token} size={300} />
        <div className="text-center mt-16">
          <p className="text-muted mb-16">
            ID регистрации: {registration.id}
          </p>
          <p className="text-muted mb-16">
            Статус: {registration.status}
          </p>
          <div className="alert alert-warning">
            <strong>Важно:</strong> Сохраните этот QR-код.
            Предъявите этот QR-код на стойке регистрации в день олимпиады.
          </div>

          <div className="mt-16">
            <Button
              variant="secondary"
              onClick={handleRefreshToken}
              loading={refreshing}
            >
              Обновить QR-код
            </Button>
            <p className="text-muted mt-8" style={{ fontSize: 12 }}>
              Используйте, если токен просрочился (действителен 24 часа)
            </p>
          </div>

          <p className="mt-16" style={{ fontSize: 12, wordBreak: 'break-all', color: 'var(--text-muted)' }}>
            Токен: {token}
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default EntryQRPage;
