import React, { useRef, useState } from "react";

interface ImageUploaderProps {
  onFileSelect: (file: File) => void;
}

const ImageUploader: React.FC<ImageUploaderProps> = ({ onFileSelect }) => {
  const [dragActive, setDragActive] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setPreviewUrl(URL.createObjectURL(file));
      onFileSelect(file);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setPreviewUrl(URL.createObjectURL(file));
      onFileSelect(file);
    }
  };

  const handleClick = () => {
    inputRef.current?.click();
  };

  return (
    <div>
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        style={{
          border: dragActive ? "2px solid #007bff" : "2px dashed #ccc",
          borderRadius: "8px",
          padding: "2rem",
          textAlign: "center",
          cursor: "pointer",
          background: dragActive ? "#f0f8ff" : "#fafafa",
        }}
      >
        <input
          type="file"
          accept="image/*"
          ref={inputRef}
          style={{ display: "none" }}
          onChange={handleChange}
        />
        {previewUrl ? (
          <img
            src={previewUrl}
            alt="Preview"
            style={{ maxWidth: "200px", maxHeight: "200px", marginBottom: "1rem" }}
          />
        ) : (
          <p>Drag & drop an image here, or click to select</p>
        )}
      </div>
      {previewUrl && (
        <div style={{ marginTop: "1rem", textAlign: "center" }}>
          <span style={{ color: "#888" }}>Image ready for encryption</span>
        </div>
      )}
    </div>
  );
};

export default ImageUploader;
