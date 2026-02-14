import { useState } from 'react';
import QRScanner from '../../components/qr/QRScanner';

/**
 * Test page for camera functionality
 * Navigate to /test/camera to access
 */
const CameraTestPage = () => {
  const [scannedData, setScannedData] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [scanHistory, setScanHistory] = useState<string[]>([]);

  const handleScan = (data: string) => {
    setScannedData(data);
    setScanHistory(prev => [data, ...prev].slice(0, 10)); // Keep last 10 scans
    console.log('QR Code scanned:', data);
  };

  const handleError = (error: string) => {
    setErrorMessage(error);
    console.error('QR Scanner error:', error);
  };

  return (
    <div style={{
      maxWidth: '800px',
      margin: '0 auto',
      padding: '20px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <h1>🎥 Тест камеры и QR-сканера</h1>

      <div style={{
        background: '#f0f0f0',
        padding: '15px',
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h2>Системная информация</h2>
        <pre style={{ fontSize: '12px', overflow: 'auto' }}>
          {JSON.stringify({
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            mediaDevices: !!navigator.mediaDevices,
            getUserMedia: !!navigator.mediaDevices?.getUserMedia,
            protocol: window.location.protocol,
            hostname: window.location.hostname,
          }, null, 2)}
        </pre>
      </div>

      <div style={{
        background: '#fff',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '20px',
        border: '1px solid #ddd'
      }}>
        <h2>QR Сканер</h2>
        <QRScanner onScan={handleScan} onError={handleError} />
      </div>

      {scannedData && (
        <div style={{
          background: '#d4edda',
          border: '1px solid #c3e6cb',
          borderRadius: '8px',
          padding: '15px',
          marginBottom: '20px'
        }}>
          <h3 style={{ color: '#155724', marginTop: 0 }}>✅ Последний отсканированный код:</h3>
          <pre style={{
            background: '#fff',
            padding: '10px',
            borderRadius: '4px',
            overflow: 'auto',
            color: '#155724'
          }}>
            {scannedData}
          </pre>
        </div>
      )}

      {errorMessage && (
        <div style={{
          background: '#f8d7da',
          border: '1px solid #f5c6cb',
          borderRadius: '8px',
          padding: '15px',
          marginBottom: '20px'
        }}>
          <h3 style={{ color: '#721c24', marginTop: 0 }}>❌ Ошибка:</h3>
          <p style={{ color: '#721c24' }}>{errorMessage}</p>
        </div>
      )}

      {scanHistory.length > 0 && (
        <div style={{
          background: '#fff',
          border: '1px solid #ddd',
          borderRadius: '8px',
          padding: '15px'
        }}>
          <h3>История сканирования (последние 10):</h3>
          <ol style={{ margin: 0, paddingLeft: '20px' }}>
            {scanHistory.map((item, index) => (
              <li key={index} style={{
                padding: '5px 0',
                borderBottom: index < scanHistory.length - 1 ? '1px solid #eee' : 'none',
                wordBreak: 'break-all'
              }}>
                {item}
              </li>
            ))}
          </ol>
        </div>
      )}

      <div style={{
        marginTop: '20px',
        padding: '15px',
        background: '#e7f3ff',
        borderRadius: '8px',
        border: '1px solid #b3d9ff'
      }}>
        <h3 style={{ marginTop: 0 }}>💡 Инструкции по использованию</h3>
        <ul>
          <li>Разрешите доступ к камере при запросе браузера</li>
          <li>Наведите камеру на QR-код</li>
          <li>Код будет автоматически распознан</li>
          <li>Если камера не работает, проверьте <a href="/CAMERA_TROUBLESHOOTING.md">руководство по устранению неполадок</a></li>
        </ul>
      </div>
    </div>
  );
};

export default CameraTestPage;
