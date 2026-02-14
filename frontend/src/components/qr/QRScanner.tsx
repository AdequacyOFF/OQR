import { useEffect, useRef, useState } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';

interface QRScannerProps {
  onScan: (data: string) => void;
  onError?: (err: string) => void;
}

const QRScanner: React.FC<QRScannerProps> = ({ onScan, onError }) => {
  const scannerRef = useRef<Html5QrcodeScanner | null>(null);
  const [permissionError, setPermissionError] = useState<string | null>(null);

  useEffect(() => {
    // Check camera permissions first
    const checkPermissions = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: 'environment',
            width: { ideal: 1280 },
            height: { ideal: 720 }
          }
        });
        // Stop the test stream immediately
        stream.getTracks().forEach(track => track.stop());
        return true;
      } catch (err) {
        const error = err as Error;
        if (error.name === 'NotAllowedError') {
          setPermissionError('Доступ к камере запрещен. Разрешите доступ в настройках браузера.');
        } else if (error.name === 'NotFoundError') {
          setPermissionError('Камера не найдена. Проверьте подключение камеры.');
        } else if (error.name === 'NotReadableError') {
          setPermissionError('Камера используется другим приложением. Закройте другие программы, использующие камеру.');
        } else {
          setPermissionError(`Ошибка доступа к камере: ${error.message}`);
        }
        if (onError) {
          onError(error.message);
        }
        return false;
      }
    };

    const initScanner = async () => {
      const hasPermission = await checkPermissions();
      if (!hasPermission) return;

      const scanner = new Html5QrcodeScanner(
        'qr-reader',
        {
          fps: 10,
          qrbox: { width: 250, height: 250 },
          aspectRatio: 1.0,
          // Support both camera and file upload
          showTorchButtonIfSupported: true,
          formatsToSupport: undefined, // Support all formats
        },
        /* verbose= */ false
      );

      scanner.render(
        (decodedText) => {
          onScan(decodedText);
          scanner.clear().catch(() => {});
        },
        (errorMessage) => {
          // Ignore verbose scan errors (happens on every frame without QR)
          if (!errorMessage.includes('NotFoundException')) {
            console.warn('QR Scan error:', errorMessage);
          }
        }
      );

      scannerRef.current = scanner;
    };

    initScanner();

    return () => {
      if (scannerRef.current) {
        scannerRef.current.clear().catch(() => {});
      }
    };
  }, [onScan, onError]);

  if (permissionError) {
    return (
      <div style={{
        padding: '20px',
        background: '#fff3cd',
        border: '1px solid #ffc107',
        borderRadius: '8px',
        maxWidth: 500,
        margin: '0 auto'
      }}>
        <h3 style={{ color: '#856404', marginTop: 0 }}>⚠️ Ошибка доступа к камере</h3>
        <p style={{ color: '#856404' }}>{permissionError}</p>
        <details style={{ marginTop: '10px' }}>
          <summary style={{ cursor: 'pointer', color: '#856404', fontWeight: 'bold' }}>
            Как исправить?
          </summary>
          <ul style={{ color: '#856404', textAlign: 'left' }}>
            <li>Закройте все программы, использующие камеру (Skype, Teams, Zoom и т.д.)</li>
            <li>Проверьте настройки конфиденциальности Windows 11:
              <br />Параметры → Конфиденциальность и безопасность → Камера
            </li>
            <li>Разрешите доступ к камере для браузера в настройках сайта</li>
            <li>Попробуйте другой браузер (Chrome, Edge, Firefox)</li>
            <li>Перезагрузите компьютер, если проблема сохраняется</li>
          </ul>
        </details>
      </div>
    );
  }

  return <div id="qr-reader" style={{ width: '100%', maxWidth: 500 }} />;
};

export default QRScanner;
