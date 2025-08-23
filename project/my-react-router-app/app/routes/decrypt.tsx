import React, { useState } from "react";
import { decryptImageWithoutMetadata } from "../services/cryptAPI";
import ImageUploader from "../../components/ImageUploader";
import EncryptedViewer from "../../components/EncryptedViewer";

const DecryptPage = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [key, setKey] = useState("");
  const [decryptedImgUrl, setDecryptedImgUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleDecrypt = async () => {
    if (selectedFile && key) {
      setIsLoading(true);
      try {
        const res = await decryptImageWithoutMetadata(selectedFile, key);
        setDecryptedImgUrl(res.image_url);
      } catch (error) {
        console.error("Decryption failed:", error);
        alert("Decryption failed. Please check your key and encrypted image.");
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
        <h3>Step 2: Enter Decryption Key</h3>
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
        <h3>Step 3: Decrypt Image</h3>
        <button
          onClick={handleDecrypt}
          disabled={!selectedFile || !key || isLoading}
          style={{
            padding: "0.75rem 2rem",
            background: selectedFile && key && !isLoading ? "#28a745" : "#ccc",
            color: "#fff",
            border: "none",
            borderRadius: 8,
            fontSize: 16,
            cursor: selectedFile && key && !isLoading ? "pointer" : "not-allowed",
            marginBottom: "1rem"
          }}
        >
          {isLoading ? "Decrypting..." : "Decrypt Image"}
        </button>
      </div>

      {decryptedImgUrl && (
        <div style={{ marginBottom: "2rem" }}>
          <h3>Step 4: Download Decrypted Image</h3>
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