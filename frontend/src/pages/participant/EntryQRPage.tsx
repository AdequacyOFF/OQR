import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../api/client';
import type { Registration } from '../../types';
import Layout from '../../components/layout/Layout';
import QRCodeDisplay from '../../components/qr/QRCodeDisplay';
import Spinner from '../../components/common/Spinner';

const EntryQRPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [registration, setRegistration] = useState<Registration | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
        <QRCodeDisplay value={token} size={300} />
        <div className="text-center mt-16">
          <p className="text-muted mb-16">
            ID регистрации: {registration.id}
          </p>
          <p className="text-muted mb-16">
            Статус: {registration.status}
          </p>
          <div className="alert alert-warning">
            <strong>Важно:</strong> Сохраните этот QR-код. Входной токен может быть показан только один раз.
            Предъявите этот QR-код на стойке регистрации в день олимпиады.
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
