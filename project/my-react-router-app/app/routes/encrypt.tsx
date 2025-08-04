import React, { useState } from "react";
import { encryptImage } from "../services/cryptAPI";
import type { EncryptResponse } from "../types/encryptionTypes";
import ImageUploader from "../../components/ImageUploader";
import EncryptedViewer from "../../components/EncryptedViewer";

const EncryptPage = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [key, setKey] = useState("");
  const [encryptedImgUrl, setEncryptedImgUrl] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<EncryptResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleEncrypt = async () => {
    if (selectedFile && key) {
      setIsLoading(true);
      try {
        const result = await encryptImage(selectedFile, key);
        console.log("Encryption result:", result);
        console.log("Image URL:", result.image_url);
        setEncryptedImgUrl(result.image_url);
        setMetadata(result);
      } catch (error) {
        console.error("Encryption failed:", error);
        alert("Encryption failed. Please try again.");
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleDownloadMetadata = () => {
    if (metadata) {
      const dataStr = JSON.stringify(metadata, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'encryption_metadata.json';
      link.click();
      URL.revokeObjectURL(url);
    }
  };

  const goBack = () => {
    window.location.href = '/';
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
      <button
        onClick={goBack}
        style={{
          padding: "0.5rem 1rem",
          background: "#6c757d",
          color: "#fff",
          border: "none",
          borderRadius: 6,
          cursor: "pointer",
          fontSize: 14,
          marginBottom: "1rem",
          display: "flex",
          alignItems: "center",
          gap: "0.5rem"
        }}
      >
        ← Back to Home
      </button>
      
      <h1 style={{ textAlign: "center", marginBottom: "2rem", color: "#333" }}>
        Image Encryption
      </h1>
      
      <div style={{ marginBottom: "2rem" }}>
        <h3>Step 1: Upload Image</h3>
        <div style={{ maxWidth: 400, marginBottom: "1.5rem" }}>
          <ImageUploader onFileSelect={setSelectedFile} />
        </div>
      </div>

      <div style={{ marginBottom: "2rem" }}>
        <h3>Step 2: Enter Encryption Key</h3>
        <input
          type="text"
          placeholder="Enter encryption key"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          style={{
            width: "100%",
            maxWidth: "400px",
            padding: "0.75rem",
            borderRadius: 8,
            border: "1px solid #ccc",
            fontSize: 16,
            marginBottom: "1rem"
          }}
        />
      </div>

      <div style={{ marginBottom: "2rem" }}>
        <h3>Step 3: Encrypt Image</h3>
        <button
          onClick={handleEncrypt}
          disabled={!selectedFile || !key || isLoading}
          style={{
            padding: "0.75rem 2rem",
            background: selectedFile && key && !isLoading ? "#007bff" : "#ccc",
            color: "#fff",
            border: "none",
            borderRadius: 8,
            fontSize: 16,
            cursor: selectedFile && key && !isLoading ? "pointer" : "not-allowed",
            marginBottom: "1rem"
          }}
        >
          {isLoading ? "Encrypting..." : "Encrypt Image"}
        </button>
      </div>

      {encryptedImgUrl && (
        <div style={{ marginBottom: "2rem" }}>
          <h3>Step 4: Download Results</h3>
          <div style={{ display: "flex", gap: "2rem", alignItems: "flex-start" }}>
            <div>
              <h4>Encrypted Image</h4>
              <EncryptedViewer imageUrl={encryptedImgUrl} />
              <a
                href={encryptedImgUrl}
                download="encrypted_image.png"
                style={{
                  display: "inline-block",
                  padding: "0.5rem 1rem",
                  background: "#28a745",
                  color: "#fff",
                  textDecoration: "none",
                  borderRadius: 4,
                  marginTop: "0.5rem"
                }}
              >
                Download Encrypted Image
              </a>
            </div>
            <div>
              <h4>Encryption Metadata</h4>
              <p style={{ color: "#666", marginBottom: "1rem" }}>
                Save this metadata for decryption later
              </p>
              <button
                onClick={handleDownloadMetadata}
                style={{
                  padding: "0.5rem 1rem",
                  background: "#17a2b8",
                  color: "#fff",
                  border: "none",
                  borderRadius: 4,
                  cursor: "pointer"
                }}
              >
                Download Metadata
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EncryptPage; 