import React, { useState } from "react";
import { decryptImage } from "../services/cryptAPI";
import type { EncryptResponse } from "../types/encryptionTypes";
import ImageUploader from "../../components/ImageUploader";
import EncryptedViewer from "../../components/EncryptedViewer";

const DecryptPage = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [key, setKey] = useState("");
  const [decryptedImgUrl, setDecryptedImgUrl] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<EncryptResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [metadataFile, setMetadataFile] = useState<File | null>(null);

  const handleMetadataUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setMetadataFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const metadata = JSON.parse(e.target?.result as string);
          setMetadata(metadata);
        } catch (error) {
          alert("Invalid metadata file. Please upload a valid JSON file.");
        }
      };
      reader.readAsText(file);
    }
  };

  const handleDecrypt = async () => {
    if (selectedFile && key && metadata) {
      setIsLoading(true);
      try {
        const res = await decryptImage(selectedFile, key, metadata.permutation, metadata.key_stream);
        setDecryptedImgUrl(res.image_url);
      } catch (error) {
        console.error("Decryption failed:", error);
        alert("Decryption failed. Please check your key and metadata.");
      } finally {
        setIsLoading(false);
      }
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
        Image Decryption
      </h1>
      
      <div style={{ marginBottom: "2rem" }}>
        <h3>Step 1: Upload Encrypted Image</h3>
        <div style={{ maxWidth: 400, marginBottom: "1.5rem" }}>
          <ImageUploader onFileSelect={setSelectedFile} />
        </div>
      </div>

      <div style={{ marginBottom: "2rem" }}>
        <h3>Step 2: Upload Encryption Metadata</h3>
        <input
          type="file"
          accept=".json"
          onChange={handleMetadataUpload}
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
        {metadata && (
          <div style={{ 
            padding: "1rem", 
            background: "#f8f9fa", 
            borderRadius: 8, 
            marginTop: "0.5rem",
            fontSize: 14,
            color: "#666"
          }}>
            <strong>Metadata loaded:</strong> Permutation and key stream data ready for decryption
          </div>
        )}
      </div>

      <div style={{ marginBottom: "2rem" }}>
        <h3>Step 3: Enter Decryption Key</h3>
        <input
          type="text"
          placeholder="Enter decryption key (same as encryption key)"
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
        <h3>Step 4: Decrypt Image</h3>
        <button
          onClick={handleDecrypt}
          disabled={!selectedFile || !key || !metadata || isLoading}
          style={{
            padding: "0.75rem 2rem",
            background: selectedFile && key && metadata && !isLoading ? "#28a745" : "#ccc",
            color: "#fff",
            border: "none",
            borderRadius: 8,
            fontSize: 16,
            cursor: selectedFile && key && metadata && !isLoading ? "pointer" : "not-allowed",
            marginBottom: "1rem"
          }}
        >
          {isLoading ? "Decrypting..." : "Decrypt Image"}
        </button>
      </div>

      {decryptedImgUrl && (
        <div style={{ marginBottom: "2rem" }}>
          <h3>Step 5: Download Decrypted Image</h3>
          <div>
            <h4>Decrypted Image</h4>
            <EncryptedViewer imageUrl={decryptedImgUrl} />
            <a
              href={decryptedImgUrl}
              download="decrypted_image.png"
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
              Download Decrypted Image
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default DecryptPage; 