import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

const ImageUploader = ({ onImageUpload, acceptedFileTypes = ['image/*'] }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      onImageUpload(file);
    }
  }, [onImageUpload]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: acceptedFileTypes.reduce((acc, type) => {
      acc[type] = [];
      return acc;
    }, {}),
    multiple: false,
    maxSize: 16 * 1024 * 1024, // 16MB
  });

  return (
    <div
      {...getRootProps()}
      className={`dropzone ${isDragActive ? 'active' : ''} ${isDragReject ? 'error' : ''}`}
    >
      <input {...getInputProps()} />
      <div className="dropzone-icon">
        📁
      </div>
      <div className="dropzone-text">
        {isDragActive ? (
          isDragReject ? (
            <span>❌ File type not supported</span>
          ) : (
            <span>📤 Drop the image here...</span>
          )
        ) : (
          <span>
            📤 Drag & drop an image here, or click to select
            <br />
            <small>Supports: PNG, JPG, JPEG, GIF, BMP (Max 16MB)</small>
          </span>
        )}
      </div>
    </div>
  );
};

export default ImageUploader;
