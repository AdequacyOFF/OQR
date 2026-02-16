import React, { useState } from 'react';
import { Html5Qrcode } from 'html5-qrcode';
import api from '../../api/client';
import Layout from '../../components/layout/Layout';
import QRScanner from '../../components/qr/QRScanner';
import QRCodeDisplay from '../../components/qr/QRCodeDisplay';
import Button from '../../components/common/Button';
import Spinner from '../../components/common/Spinner';
import FileUploader from '../../components/upload/FileUploader';

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
  const [scanMode, setScanMode] = useState<'camera' | 'upload'>('camera');
  const [scanning, setScanning] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [approving, setApproving] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [processing, setProcessing] = useState(false);
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
    setProcessing(false);
  };

  const handleFileUpload = async (file: File) => {
    setProcessing(true);
    setError(null);
    setScanning(false);

    try {
      // Create a temporary element ID for QR scanning
      const tempId = 'qr-temp-' + Date.now();
      const tempDiv = document.createElement('div');
      tempDiv.id = tempId;
      tempDiv.style.display = 'none';
      document.body.appendChild(tempDiv);

      try {
        // Scan QR code from uploaded image
        const html5QrCode = new Html5Qrcode(tempId);
        const decodedText = await html5QrCode.scanFile(file, false);

        // Process the scanned QR code
        await handleScan(decodedText);

        // Cleanup
        html5QrCode.clear();
      } finally {
        // Always remove temp div
        document.body.removeChild(tempDiv);
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Не удалось распознать QR-код на изображении';
      setError(message);
      setScanning(true);
    } finally {
      setProcessing(false);
    }
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
          {/* Mode toggle buttons */}
          <div className="scan-mode-toggle mb-24">
            <button
              className={`mode-btn ${scanMode === 'camera' ? 'active' : ''}`}
              onClick={() => setScanMode('camera')}
              disabled={processing}
            >
              Камера
            </button>
            <button
              className={`mode-btn ${scanMode === 'upload' ? 'active' : ''}`}
              onClick={() => setScanMode('upload')}
              disabled={processing}
            >
              Загрузить фото
            </button>
          </div>

          {scanMode === 'camera' ? (
            <>
              <h2 className="mb-16">Сканировать входной QR-код камерой</h2>
              <QRScanner
                onScan={handleScan}
                onError={(err) => console.error('Ошибка QR:', err)}
              />
            </>
          ) : (
            <>
              <h2 className="mb-16">Загрузить фото QR-кода</h2>
              <FileUploader
                onUpload={handleFileUpload}
                uploading={processing}
                accept="image/*"
                maxSizeMB={10}
              />
            </>
          )}
        </div>
      )}

      {verifying && (
        <div className="card">
          <Spinner />
          <p className="text-center mt-16">Проверка участника...</p>
        </div>
      )}

      {processing && (
        <div className="card">
          <Spinner />
          <p className="text-center mt-16">Распознавание QR-кода...</p>
        </div>
      )}

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

      <style>{`
        .scan-mode-toggle {
          display: flex;
          gap: 12px;
          justify-content: center;
          border-bottom: 2px solid #e2e8f0;
          padding-bottom: 16px;
        }

        .mode-btn {
          flex: 1;
          max-width: 200px;
          padding: 12px 24px;
          font-size: 16px;
          font-weight: 600;
          border: 2px solid #cbd5e0;
          border-radius: 8px;
          background: white;
          color: #4a5568;
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }

        .mode-btn:hover:not(:disabled) {
          border-color: #4299e1;
          background: #ebf8ff;
          color: #2b6cb0;
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(66, 153, 225, 0.2);
        }

        .mode-btn.active {
          border-color: #4299e1;
          background: #4299e1;
          color: white;
          box-shadow: 0 4px 12px rgba(66, 153, 225, 0.4);
        }

        .mode-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        @media (max-width: 640px) {
          .scan-mode-toggle {
            flex-direction: column;
          }

          .mode-btn {
            max-width: 100%;
          }
        }
      `}</style>
    </Layout>
  );
};

export default AdmissionPage;
