import React, { useState } from 'react';
import api from '../../api/client';
import Layout from '../../components/layout/Layout';
import QRScanner from '../../components/qr/QRScanner';
import QRCodeDisplay from '../../components/qr/QRCodeDisplay';
import Button from '../../components/common/Button';
import Spinner from '../../components/common/Spinner';

interface VerifyResponse {
  registration_id: string;
  participant_name: string;
  email: string;
  competition_name: string;
  status: string;
}

interface ApproveResponse {
  attempt_id: string;
  sheet_token: string;
  pdf_url: string;
}

const AdmissionPage: React.FC = () => {
  const [scanning, setScanning] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [approving, setApproving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [verifyData, setVerifyData] = useState<VerifyResponse | null>(null);
  const [approveData, setApproveData] = useState<ApproveResponse | null>(null);
  const [scannedToken, setScannedToken] = useState<string | null>(null);

  const handleScan = async (data: string) => {
    setScanning(false);
    setError(null);
    setVerifying(true);
    setScannedToken(data);

    try {
      const { data: result } = await api.post<VerifyResponse>('/admission/verify', {
        entry_token: data,
      });
      setVerifyData(result);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Verification failed.';
      setError(message);
    } finally {
      setVerifying(false);
    }
  };

  const handleApprove = async () => {
    if (!verifyData) return;
    setApproving(true);
    setError(null);

    try {
      const { data: result } = await api.post<ApproveResponse>('/admission/approve', {
        registration_id: verifyData.registration_id,
      });
      setApproveData(result);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Approval failed.';
      setError(message);
    } finally {
      setApproving(false);
    }
  };

  const handleReset = () => {
    setScanning(true);
    setVerifyData(null);
    setApproveData(null);
    setError(null);
    setScannedToken(null);
  };

  return (
    <Layout>
      <h1 className="mb-24">Admission</h1>

      {error && <div className="alert alert-error mb-16">{error}</div>}

      {scanning && (
        <div className="card">
          <h2 className="mb-16">Scan Entry QR Code</h2>
          <QRScanner
            onScan={handleScan}
            onError={(err) => console.error('QR Error:', err)}
          />
        </div>
      )}

      {verifying && <Spinner />}

      {verifyData && !approveData && (
        <div className="card">
          <h2 className="mb-16">Participant Verification</h2>
          <table className="table mb-16">
            <tbody>
              <tr>
                <td><strong>Name</strong></td>
                <td>{verifyData.participant_name}</td>
              </tr>
              <tr>
                <td><strong>Email</strong></td>
                <td>{verifyData.email}</td>
              </tr>
              <tr>
                <td><strong>Competition</strong></td>
                <td>{verifyData.competition_name}</td>
              </tr>
              <tr>
                <td><strong>Status</strong></td>
                <td>{verifyData.status}</td>
              </tr>
              <tr>
                <td><strong>Token</strong></td>
                <td style={{ fontSize: 12, wordBreak: 'break-all' }}>{scannedToken}</td>
              </tr>
            </tbody>
          </table>
          <div className="flex gap-8">
            <Button onClick={handleApprove} loading={approving}>
              Approve Entry
            </Button>
            <Button variant="secondary" onClick={handleReset}>
              Cancel
            </Button>
          </div>
        </div>
      )}

      {approveData && (
        <div className="card">
          <div className="alert alert-success mb-16">
            Entry approved successfully!
          </div>
          <h2 className="mb-16">Answer Sheet</h2>
          <div className="mb-16">
            <a
              href={approveData.pdf_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn"
              style={{ display: 'inline-block', textDecoration: 'none' }}
            >
              Download Answer Sheet PDF
            </a>
          </div>
          <h3 className="mb-16">Sheet Token QR</h3>
          <QRCodeDisplay value={approveData.sheet_token} size={200} />
          <p className="text-muted text-center mt-16" style={{ fontSize: 12, wordBreak: 'break-all' }}>
            Sheet Token: {approveData.sheet_token}
          </p>
          <div className="mt-16">
            <Button variant="secondary" onClick={handleReset}>
              Scan Next
            </Button>
          </div>
        </div>
      )}
    </Layout>
  );
};

export default AdmissionPage;
