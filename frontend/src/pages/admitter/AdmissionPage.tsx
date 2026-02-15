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
  participant_school: string;
  participant_grade: number;
  competition_name: string;
  competition_id: string;
  can_proceed: boolean;
  message: string;
}

interface ApproveResponse {
  attempt_id: string;
  variant_number: number;
  pdf_url: string;
  sheet_token: string;
}

const AdmissionPage: React.FC = () => {
  const [scanning, setScanning] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [approving, setApproving] = useState(false);
  const [downloading, setDownloading] = useState(false);
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
      const { data: result } = await api.post<VerifyResponse>('admission/verify', {
        token: data,
      });
      setVerifyData(result);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Ошибка проверки.';
      setError(message);
    } finally {
      setVerifying(false);
    }
  };

  const handleApprove = async () => {
    if (!verifyData || !scannedToken) return;
    setApproving(true);
    setError(null);

    try {
      const { data: result } = await api.post<ApproveResponse>(
        `admission/${verifyData.registration_id}/approve`,
        {
          raw_entry_token: scannedToken,
        }
      );
      setApproveData(result);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Ошибка подтверждения.';
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

  const handleDownloadPdf = async () => {
    if (!approveData) return;
    setDownloading(true);
    setError(null);

    try {
      // Fetch PDF with authentication header
      const response = await api.get(approveData.pdf_url, {
        responseType: 'blob',
      });

      // Create blob and download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `answer_sheet_${approveData.attempt_id}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Ошибка скачивания PDF.';
      setError(message);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <Layout>
      <h1 className="mb-24">Допуск участников</h1>

      {error && <div className="alert alert-error mb-16">{error}</div>}

      {scanning && (
        <div className="card">
          <h2 className="mb-16">Сканировать входной QR-код</h2>
          <QRScanner
            onScan={handleScan}
            onError={(err) => console.error('Ошибка QR:', err)}
          />
        </div>
      )}

      {verifying && <Spinner />}

      {verifyData && !approveData && (
        <div className="card">
          <h2 className="mb-16">Проверка участника</h2>

          {!verifyData.can_proceed && (
            <div className="alert alert-error mb-16">
              {verifyData.message}
            </div>
          )}

          <table className="table mb-16">
            <tbody>
              <tr>
                <td><strong>ФИО</strong></td>
                <td>{verifyData.participant_name}</td>
              </tr>
              <tr>
                <td><strong>Школа</strong></td>
                <td>{verifyData.participant_school}</td>
              </tr>
              <tr>
                <td><strong>Класс</strong></td>
                <td>{verifyData.participant_grade}</td>
              </tr>
              <tr>
                <td><strong>Олимпиада</strong></td>
                <td>{verifyData.competition_name}</td>
              </tr>
              <tr>
                <td><strong>Статус</strong></td>
                <td>{verifyData.message}</td>
              </tr>
            </tbody>
          </table>
          <div className="flex gap-8">
            <Button
              onClick={handleApprove}
              loading={approving}
              disabled={!verifyData.can_proceed}
            >
              Подтвердить допуск
            </Button>
            <Button variant="secondary" onClick={handleReset}>
              Отмена
            </Button>
          </div>
        </div>
      )}

      {approveData && (
        <div className="card">
          <div className="alert alert-success mb-16">
            Участник успешно допущен!
          </div>
          <h2 className="mb-16">Бланк ответов</h2>
          <div className="mb-16">
            <Button onClick={handleDownloadPdf} loading={downloading}>
              Скачать бланк ответов PDF
            </Button>
          </div>
          <h3 className="mb-16">QR-код бланка</h3>
          <QRCodeDisplay value={approveData.sheet_token} size={200} />
          <p className="text-muted text-center mt-16" style={{ fontSize: 12, wordBreak: 'break-all' }}>
            Токен бланка: {approveData.sheet_token}
          </p>
          <div className="mt-16">
            <Button variant="secondary" onClick={handleReset}>
              Следующий участник
            </Button>
          </div>
        </div>
      )}
    </Layout>
  );
};

export default AdmissionPage;
