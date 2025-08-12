import React, { useState } from "react";
import { encryptImage } from "../services/cryptAPI";
import ImageUploader from "../../components/ImageUploader";
import EncryptedViewer from "../../components/EncryptedViewer";

const EncryptPage = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [key, setKey] = useState("");
  const [encryptedImgUrl, setEncryptedImgUrl] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleEncrypt = async () => {
    if (selectedFile && key) {
      setIsLoading(true);
      try {
        const result = await encryptImage(selectedFile, key);
        console.log("Encryption result:", result);
        console.log("Image URL:", result.image_url);
        setEncryptedImgUrl(result.image_url);
        // Note: Backend no longer returns permutation and key_stream
        setMetadata({ image_url: result.image_url });
      } catch (error) {
        console.error("Encryption failed:", error);
        alert("Encryption failed. Please try again.");
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
                download="encrypted.png"
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
              <h4>Encryption Info</h4>
              <p style={{ color: "#666", marginBottom: "1rem" }}>
                The encryption key is used for both encryption and decryption.
                Make sure to save your key securely!
              </p>
              <div style={{ 
                padding: "1rem", 
                background: "#f8f9fa", 
                borderRadius: "4px",
                border: "1px solid #dee2e6"
              }}>
                <strong>Important:</strong> Keep your encryption key safe. 
                You'll need the same key to decrypt this image later.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EncryptPage; 