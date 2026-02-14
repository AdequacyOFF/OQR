import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/client';
import type { ScanItem } from '../../types';
import Layout from '../../components/layout/Layout';
import Button from '../../components/common/Button';
import Spinner from '../../components/common/Spinner';

const ScansPage: React.FC = () => {
  const navigate = useNavigate();
  const fileRef = useRef<HTMLInputElement>(null);
  const [scans, setScans] = useState<ScanItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadScans();
  }, []);

  const loadScans = async () => {
    setLoading(true);
    try {
      const { data } = await api.get<{ items: ScanItem[]; total: number }>('scans');
      setScans(data.items || []);
    } catch {
      setError('Не удалось загрузить сканы.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      await api.post('scans/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      await loadScans();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Ошибка загрузки.';
      setError(message);
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = '';
    }
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
      <div className="flex-between mb-24">
        <h1>Сканы</h1>
        <div>
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            style={{ display: 'none' }}
            onChange={handleUpload}
          />
          <Button onClick={() => fileRef.current?.click()} loading={uploading}>
            Загрузить скан
          </Button>
        </div>
      </div>

      {error && <div className="alert alert-error mb-16">{error}</div>}

      {scans.length === 0 ? (
        <p className="text-muted">Сканов пока нет.</p>
      ) : (
        <table className="table table-clickable">
          <thead>
            <tr>
              <th>ID</th>
              <th>Балл OCR</th>
              <th>Точность</th>
              <th>Проверен</th>
              <th>Дата</th>
            </tr>
          </thead>
          <tbody>
            {scans.map((scan) => (
              <tr key={scan.id} onClick={() => navigate(`/scans/${scan.id}`)}>
                <td style={{ fontSize: 12 }}>{scan.id.slice(0, 8)}...</td>
                <td>{scan.ocr_score !== null ? scan.ocr_score : '-'}</td>
                <td>
                  {scan.ocr_confidence !== null
                    ? `${(scan.ocr_confidence * 100).toFixed(1)}%`
                    : '-'}
                </td>
                <td>{scan.verified_by ? 'Да' : 'Нет'}</td>
                <td>{new Date(scan.created_at).toLocaleDateString('ru-RU')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Layout>
  );
};

export default ScansPage;
