import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../api/client';
import type { ScanItem } from '../../types';
import Layout from '../../components/layout/Layout';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Spinner from '../../components/common/Spinner';

const ScanDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [scan, setScan] = useState<ScanItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [correctedScore, setCorrectedScore] = useState<string>('');

  useEffect(() => {
    const loadScan = async () => {
      try {
        const { data } = await api.get<ScanItem>(`scans/${id}`);
        setScan(data);
        if (data.ocr_score !== null) {
          setCorrectedScore(String(data.ocr_score));
        }
      } catch {
        setError('Failed to load scan.');
      } finally {
        setLoading(false);
      }
    };

    loadScan();
  }, [id]);

  const handleVerify = async () => {
    if (!scan) return;
    setVerifying(true);
    setError(null);
    setSuccess(null);

    try {
      const { data } = await api.post<ScanItem>(`scans/${scan.id}/verify`, {
        verified_score: Number(correctedScore),
      });
      setScan(data);
      setSuccess('Scan verified successfully.');
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Verification failed.';
      setError(message);
    } finally {
      setVerifying(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <Spinner />
      </Layout>
    );
  }

  if (!scan) {
    return (
      <Layout>
        <div className="alert alert-error">{error || 'Scan not found.'}</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <h1 className="mb-24">Scan Detail</h1>

      {error && <div className="alert alert-error mb-16">{error}</div>}
      {success && <div className="alert alert-success mb-16">{success}</div>}

      <div className="card mb-16">
        <h2 className="mb-16">Scan Information</h2>
        <table className="table">
          <tbody>
            <tr>
              <td><strong>ID</strong></td>
              <td>{scan.id}</td>
            </tr>
            <tr>
              <td><strong>Attempt ID</strong></td>
              <td>{scan.attempt_id || '-'}</td>
            </tr>
            <tr>
              <td><strong>File Path</strong></td>
              <td>{scan.file_path}</td>
            </tr>
            <tr>
              <td><strong>OCR Score</strong></td>
              <td>{scan.ocr_score !== null ? scan.ocr_score : 'Pending'}</td>
            </tr>
            <tr>
              <td><strong>OCR Confidence</strong></td>
              <td>
                {scan.ocr_confidence !== null
                  ? `${(scan.ocr_confidence * 100).toFixed(1)}%`
                  : 'Pending'}
              </td>
            </tr>
            <tr>
              <td><strong>Verified By</strong></td>
              <td>{scan.verified_by || 'Not verified'}</td>
            </tr>
            <tr>
              <td><strong>Uploaded By</strong></td>
              <td>{scan.uploaded_by}</td>
            </tr>
            <tr>
              <td><strong>Created</strong></td>
              <td>{new Date(scan.created_at).toLocaleString()}</td>
            </tr>
            <tr>
              <td><strong>Updated</strong></td>
              <td>{new Date(scan.updated_at).toLocaleString()}</td>
            </tr>
          </tbody>
        </table>
      </div>

      {scan.ocr_raw_text && (
        <div className="card mb-16">
          <h2 className="mb-16">OCR Raw Text</h2>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: 13, background: '#f9fafb', padding: 12, borderRadius: 6 }}>
            {scan.ocr_raw_text}
          </pre>
        </div>
      )}

      {!scan.verified_by && (
        <div className="card">
          <h2 className="mb-16">Verify Score</h2>
          <Input
            label="Corrected Score"
            type="number"
            value={correctedScore}
            onChange={(e) => setCorrectedScore(e.target.value)}
            placeholder="Enter verified score"
          />
          <Button onClick={handleVerify} loading={verifying}>
            Verify
          </Button>
        </div>
      )}
    </Layout>
  );
};

export default ScanDetailPage;
