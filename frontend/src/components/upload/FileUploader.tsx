import React, { useState, useRef, DragEvent } from 'react';
import Button from '../common/Button';

interface FileUploaderProps {
  onUpload: (file: File) => void;
  uploading?: boolean;
  accept?: string;
  maxSizeMB?: number;
}

const FileUploader: React.FC<FileUploaderProps> = ({
  onUpload,
  uploading = false,
  accept = 'image/*,application/pdf',
  maxSizeMB = 50,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFile(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleFile = (file: File) => {
    setError(null);

    // Validate file size
    const maxSize = maxSizeMB * 1024 * 1024;
    if (file.size > maxSize) {
      setError(`Файл слишком большой. Максимум ${maxSizeMB}МБ`);
      return;
    }

    // Validate file type
    const fileType = file.type;
    const acceptedTypes = accept.split(',').map(t => t.trim());
    const isAccepted = acceptedTypes.some(type => {
      if (type === 'image/*') return fileType.startsWith('image/');
      if (type === 'application/pdf') return fileType === 'application/pdf';
      return fileType === type;
    });

    if (!isAccepted) {
      setError('Неподдерживаемый формат файла');
      return;
    }

    // Show preview for images
    if (fileType.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setPreview(null);
    }

    onUpload(file);
  };

  const clearPreview = () => {
    setPreview(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  };

  return (
    <div className="file-uploader">
      {error && (
        <div className="alert alert-error mb-16">
          {error}
        </div>
      )}

      <div
        className={`upload-zone ${isDragging ? 'dragging' : ''} ${uploading ? 'uploading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          style={{ display: 'none' }}
          onChange={handleFileSelect}
        />
        <input
          ref={cameraInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          style={{ display: 'none' }}
          onChange={handleFileSelect}
        />

        {preview && !uploading ? (
          <div className="preview-container">
            <img src={preview} alt="Preview" className="preview-image" />
            <button
              className="preview-close"
              onClick={(e) => {
                e.stopPropagation();
                clearPreview();
              }}
            >
              ✕
            </button>
          </div>
        ) : (
          <div className="upload-content">
            <div className="upload-icon">
              {uploading ? (
                <div className="spinner-icon">⏳</div>
              ) : (
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              )}
            </div>
            <h3 className="upload-title">
              {uploading ? 'Загрузка...' : 'Перетащите файл сюда'}
            </h3>
            <p className="upload-subtitle">
              {uploading ? 'Пожалуйста, подождите' : 'или нажмите для выбора файла'}
            </p>
            <p className="upload-hint">
              Поддерживаются: JPG, PNG, PDF (макс. {maxSizeMB}МБ)
            </p>
          </div>
        )}
      </div>

      {!uploading && !preview && (
        <div className="upload-actions">
          <Button
            onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}
            variant="primary"
            style={{ flex: 1 }}
          >
            Выбрать файл
          </Button>
          <Button
            onClick={(e) => {
              e.stopPropagation();
              cameraInputRef.current?.click();
            }}
            variant="secondary"
            style={{ flex: 1 }}
          >
            Сделать фото
          </Button>
        </div>
      )}

      <style>{`
        .file-uploader {
          width: 100%;
        }

        .upload-zone {
          border: 3px dashed #cbd5e0;
          border-radius: 12px;
          padding: 48px 24px;
          text-align: center;
          cursor: pointer;
          transition: all 0.3s ease;
          background: #f7fafc;
          position: relative;
          overflow: hidden;
        }

        .upload-zone:hover:not(.uploading) {
          border-color: #4299e1;
          background: #ebf8ff;
          transform: scale(1.02);
        }

        .upload-zone.dragging {
          border-color: #48bb78;
          background: #f0fff4;
          transform: scale(1.05);
          box-shadow: 0 8px 16px rgba(72, 187, 120, 0.2);
        }

        .upload-zone.uploading {
          cursor: not-allowed;
          opacity: 0.7;
        }

        .upload-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 16px;
        }

        .upload-icon {
          color: #4299e1;
          animation: float 3s ease-in-out infinite;
        }

        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }

        .spinner-icon {
          font-size: 48px;
          animation: spin 2s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .upload-title {
          font-size: 20px;
          font-weight: 600;
          color: #2d3748;
          margin: 0;
        }

        .upload-subtitle {
          font-size: 16px;
          color: #718096;
          margin: 0;
        }

        .upload-hint {
          font-size: 14px;
          color: #a0aec0;
          margin: 0;
        }

        .upload-actions {
          display: flex;
          gap: 16px;
          margin-top: 24px;
        }

        .preview-container {
          position: relative;
          width: 100%;
          max-width: 400px;
          margin: 0 auto;
        }

        .preview-image {
          width: 100%;
          height: auto;
          max-height: 300px;
          object-fit: contain;
          border-radius: 8px;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .preview-close {
          position: absolute;
          top: -8px;
          right: -8px;
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: #ef4444;
          color: white;
          border: none;
          font-size: 18px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
          transition: all 0.2s ease;
        }

        .preview-close:hover {
          background: #dc2626;
          transform: scale(1.1);
        }

        @media (max-width: 640px) {
          .upload-zone {
            padding: 32px 16px;
          }

          .upload-actions {
            flex-direction: column;
          }

          .upload-icon svg {
            width: 48px;
            height: 48px;
          }

          .upload-title {
            font-size: 18px;
          }

          .upload-subtitle {
            font-size: 14px;
          }
        }
      `}</style>
    </div>
  );
};

export default FileUploader;
