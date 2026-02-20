import React, { useState, useRef, useEffect } from 'react';
import api from '../../api/client';
import Layout from '../../components/layout/Layout';
import QRScanner from '../../components/qr/QRScanner';
import QRCodeDisplay from '../../components/qr/QRCodeDisplay';
import Button from '../../components/common/Button';
import type { ParticipantEvent } from '../../types';

const EVENT_TYPES = [
  { value: 'start_work', label: 'Начало работы' },
  { value: 'submit', label: 'Сдача работы' },
  { value: 'exit_room', label: 'Выход из аудитории' },
  { value: 'enter_room', label: 'Вход в аудиторию' },
];

const InvigilatorPage: React.FC = () => {
  const [scanMode, setScanMode] = useState<'camera' | 'laser'>('laser');
  const [scanning, setScanning] = useState(true);
  const [attemptId, setAttemptId] = useState<string | null>(null);
  const [events, setEvents] = useState<ParticipantEvent[]>([]);
  const [recording, setRecording] = useState(false);
  const [issuingExtra, setIssuingExtra] = useState(false);
  const [extraSheetToken, setExtraSheetToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const laserInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (scanMode === 'laser' && scanning && laserInputRef.current) {
      laserInputRef.current.focus();
    }
  }, [scanMode, scanning]);

  const handleScan = async (token: string) => {
    setScanning(false);
    setError(null);

    // The scanned token is a sheet token - we need to find the attempt
    // For now, we'll use the token to look up via the scan endpoint
    // In a real flow, the invigilator scans the sheet QR which contains the raw token
    // We store the attempt_id from context
    setAttemptId(token); // placeholder - in real app, resolve token to attempt_id
  };

  const handleLaserInput = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      const value = (e.target as HTMLInputElement).value.trim();
      if (value) {
        (e.target as HTMLInputElement).value = '';
        await handleScan(value);
      }
    }
  };

  const fetchEvents = async (aId: string) => {
    try {
      const { data } = await api.get<{ events: ParticipantEvent[] }>(
        `invigilator/attempt/${aId}/events`
      );
      setEvents(data.events);
    } catch {
      // Ignore errors fetching events
    }
  };

  useEffect(() => {
    if (attemptId) {
      fetchEvents(attemptId);
    }
  }, [attemptId]);

  const handleRecordEvent = async (eventType: string) => {
    if (!attemptId) return;
    setRecording(true);
    setError(null);

    try {
      await api.post('invigilator/events', {
        attempt_id: attemptId,
        event_type: eventType,
      });
      await fetchEvents(attemptId);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Ошибка';
      setError(msg);
    } finally {
      setRecording(false);
    }
  };

  const handleIssueExtraSheet = async () => {
    if (!attemptId) return;
    setIssuingExtra(true);
    setError(null);

    try {
      const { data } = await api.post<{ answer_sheet_id: string; sheet_token: string; pdf_url: string }>(
        'invigilator/extra-sheet',
        { attempt_id: attemptId }
      );
      setExtraSheetToken(data.sheet_token);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Ошибка';
      setError(msg);
    } finally {
      setIssuingExtra(false);
    }
  };

  const handleReset = () => {
    setScanning(true);
    setAttemptId(null);
    setEvents([]);
    setExtraSheetToken(null);
    setError(null);
  };

  return (
    <Layout>
      <h1 className="mb-24">Наблюдатель</h1>

      {error && <div className="alert alert-error mb-16">{error}</div>}

      {scanning && (
        <div className="card">
          <div className="scan-mode-toggle mb-24" style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
            <button
              className={`mode-btn ${scanMode === 'laser' ? 'active' : ''}`}
              onClick={() => setScanMode('laser')}
              style={{
                padding: '12px 24px', fontSize: 16, fontWeight: 600,
                border: scanMode === 'laser' ? '2px solid #4299e1' : '2px solid #cbd5e0',
                borderRadius: 8, background: scanMode === 'laser' ? '#4299e1' : 'white',
                color: scanMode === 'laser' ? 'white' : '#4a5568', cursor: 'pointer',
              }}
            >
              Лазер
            </button>
            <button
              className={`mode-btn ${scanMode === 'camera' ? 'active' : ''}`}
              onClick={() => setScanMode('camera')}
              style={{
                padding: '12px 24px', fontSize: 16, fontWeight: 600,
                border: scanMode === 'camera' ? '2px solid #4299e1' : '2px solid #cbd5e0',
                borderRadius: 8, background: scanMode === 'camera' ? '#4299e1' : 'white',
                color: scanMode === 'camera' ? 'white' : '#4a5568', cursor: 'pointer',
              }}
            >
              Камера
            </button>
          </div>

          <h2 className="mb-16">Сканировать QR-код бланка</h2>

          {scanMode === 'laser' ? (
            <input
              ref={laserInputRef}
              type="text"
              placeholder="Ожидание сканирования..."
              onKeyDown={handleLaserInput}
              autoFocus
              style={{
                width: '100%', padding: 16, fontSize: 18, textAlign: 'center',
                border: '2px solid #4299e1', borderRadius: 8,
              }}
            />
          ) : (
            <QRScanner
              onScan={handleScan}
              onError={(err) => console.error('QR error:', err)}
            />
          )}
        </div>
      )}

      {attemptId && (
        <div className="card">
          <h2 className="mb-16">Попытка: {attemptId.substring(0, 8)}...</h2>

          <div className="mb-16">
            <h3 className="mb-8">Записать событие</h3>
            <div className="flex gap-8" style={{ flexWrap: 'wrap' }}>
              {EVENT_TYPES.map((et) => (
                <Button
                  key={et.value}
                  onClick={() => handleRecordEvent(et.value)}
                  loading={recording}
                  variant="secondary"
                >
                  {et.label}
                </Button>
              ))}
            </div>
          </div>

          <div className="mb-16">
            <h3 className="mb-8">История событий</h3>
            {events.length === 0 ? (
              <p className="text-muted">Нет событий</p>
            ) : (
              <table className="table">
                <thead>
                  <tr>
                    <th>Событие</th>
                    <th>Время</th>
                  </tr>
                </thead>
                <tbody>
                  {events.map((ev) => (
                    <tr key={ev.id}>
                      <td>{EVENT_TYPES.find((t) => t.value === ev.event_type)?.label || ev.event_type}</td>
                      <td>{new Date(ev.timestamp).toLocaleTimeString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div className="mb-16">
            <h3 className="mb-8">Дополнительный бланк</h3>
            <Button onClick={handleIssueExtraSheet} loading={issuingExtra}>
              Выдать дополнительный бланк
            </Button>
            {extraSheetToken && (
              <div className="mt-16">
                <div className="alert alert-success mb-8">Дополнительный бланк выдан!</div>
                <QRCodeDisplay value={extraSheetToken} size={150} />
                <p className="text-muted text-center mt-8" style={{ fontSize: 11, wordBreak: 'break-all' }}>
                  {extraSheetToken}
                </p>
              </div>
            )}
          </div>

          <Button variant="secondary" onClick={handleReset}>
            Следующий участник
          </Button>
        </div>
      )}
    </Layout>
  );
};

export default InvigilatorPage;
