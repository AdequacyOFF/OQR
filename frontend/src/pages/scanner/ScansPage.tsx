import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/client';
import type { ScanItem } from '../../types';
import Layout from '../../components/layout/Layout';
import Spinner from '../../components/common/Spinner';
import FileUploader from '../../components/upload/FileUploader';

const ScansPage: React.FC = () => {
  const navigate = useNavigate();
  const [scans, setScans] = useState<ScanItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showUploader, setShowUploader] = useState(false);

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

  const handleUpload = async (file: File) => {
    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      await api.post('scans/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      await loadScans();
      setShowUploader(false);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Ошибка загрузки.';
      setError(message);
    } finally {
      setUploading(false);
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
        <button
          className="btn btn-primary"
          onClick={() => setShowUploader(!showUploader)}
        >
          {showUploader ? 'Закрыть' : 'Загрузить скан'}
        </button>
      </div>

      {error && <div className="alert alert-error mb-16">{error}</div>}

      {showUploader && (
        <div className="mb-24">
          <FileUploader
            onUpload={handleUpload}
            uploading={uploading}
            accept="image/*,application/pdf"
            maxSizeMB={50}
          />
        </div>
      )}

      {scans.length === 0 ? (
        <div className="empty-state">
          <p className="text-muted">Сканов пока нет.</p>
          {!showUploader && (
            <button
              className="btn btn-secondary mt-16"
              onClick={() => setShowUploader(true)}
            >
              Загрузить первый скан
            </button>
          )}
        </div>
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
