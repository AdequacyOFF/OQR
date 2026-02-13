import React from 'react';
import { QRCodeSVG } from 'qrcode.react';

interface QRCodeDisplayProps {
  value: string;
  size?: number;
}

const QRCodeDisplay: React.FC<QRCodeDisplayProps> = ({ value, size = 256 }) => {
  return (
    <div className="qr-container">
      <QRCodeSVG value={value} size={size} />
    </div>
  );
};

export default QRCodeDisplay;
