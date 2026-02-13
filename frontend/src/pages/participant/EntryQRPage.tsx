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
        const { data } = await api.get<Registration>(`/registrations/${id}`);
        setRegistration(data);
      } catch {
        setError('Failed to load registration.');
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
        <div className="alert alert-error">{error || 'Registration not found.'}</div>
      </Layout>
    );
  }

  const token = registration.entry_token || registration.id;

  return (
    <Layout>
      <div className="card" style={{ maxWidth: 500, margin: '0 auto' }}>
        <h1 className="text-center mb-24">Entry QR Code</h1>
        <QRCodeDisplay value={token} size={300} />
        <div className="text-center mt-16">
          <p className="text-muted mb-16">
            Registration ID: {registration.id}
          </p>
          <p className="text-muted mb-16">
            Status: {registration.status}
          </p>
          <div className="alert alert-warning">
            <strong>Important:</strong> Save this QR code. The entry token may be shown only once.
            Present this QR code at the admission desk on the competition day.
          </div>
          <p className="mt-16" style={{ fontSize: 12, wordBreak: 'break-all', color: '#6b7280' }}>
            Token: {token}
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default EntryQRPage;
