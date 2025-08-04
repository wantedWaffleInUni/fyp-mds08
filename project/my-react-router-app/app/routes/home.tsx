import React from "react";

const Home = () => {
  const navigateToEncrypt = () => {
    window.location.href = '/encrypt';
  };

  const navigateToDecrypt = () => {
    window.location.href = '/decrypt';
  };

  return (
    <div style={{ 
      padding: "2rem", 
      maxWidth: "800px", 
      margin: "0 auto",
      textAlign: "center"
    }}>
      <h1 style={{ 
        marginBottom: "2rem", 
        color: "#333",
        fontSize: "2.5rem"
      }}>
        Image Encryption System
      </h1>
      
      <p style={{ 
        fontSize: "1.2rem", 
        color: "#666", 
        marginBottom: "3rem",
        lineHeight: "1.6"
      }}>
        Secure your images with advanced hybrid encryption using chaotic maps and neural networks.
        Choose an operation below to get started.
      </p>

      <div style={{ 
        display: "flex", 
        gap: "2rem", 
        justifyContent: "center",
        flexWrap: "wrap"
      }}>
        <button
          onClick={navigateToEncrypt}
          style={{
            display: "block",
            padding: "2rem",
            background: "linear-gradient(135deg, #007bff, #0056b3)",
            color: "#fff",
            textDecoration: "none",
            borderRadius: "12px",
            minWidth: "200px",
            boxShadow: "0 4px 15px rgba(0, 123, 255, 0.3)",
            transition: "transform 0.2s, box-shadow 0.2s",
            border: "none",
            cursor: "pointer",
            fontSize: "16px"
          }}
          onMouseEnter={(e: React.MouseEvent<HTMLButtonElement>) => {
            e.currentTarget.style.transform = "translateY(-5px)";
            e.currentTarget.style.boxShadow = "0 8px 25px rgba(0, 123, 255, 0.4)";
          }}
          onMouseLeave={(e: React.MouseEvent<HTMLButtonElement>) => {
            e.currentTarget.style.transform = "translateY(0)";
            e.currentTarget.style.boxShadow = "0 4px 15px rgba(0, 123, 255, 0.3)";
          }}
        >
          <h2 style={{ marginBottom: "1rem", fontSize: "1.5rem" }}>🔒 Encrypt</h2>
          <p style={{ fontSize: "1rem", opacity: 0.9 }}>
            Upload an image and encrypt it with your secret key
          </p>
        </button>

        <button
          onClick={navigateToDecrypt}
          style={{
            display: "block",
            padding: "2rem",
            background: "linear-gradient(135deg, #28a745, #1e7e34)",
            color: "#fff",
            textDecoration: "none",
            borderRadius: "12px",
            minWidth: "200px",
            boxShadow: "0 4px 15px rgba(40, 167, 69, 0.3)",
            transition: "transform 0.2s, box-shadow 0.2s",
            border: "none",
            cursor: "pointer",
            fontSize: "16px"
          }}
          onMouseEnter={(e: React.MouseEvent<HTMLButtonElement>) => {
            e.currentTarget.style.transform = "translateY(-5px)";
            e.currentTarget.style.boxShadow = "0 8px 25px rgba(40, 167, 69, 0.4)";
          }}
          onMouseLeave={(e: React.MouseEvent<HTMLButtonElement>) => {
            e.currentTarget.style.transform = "translateY(0)";
            e.currentTarget.style.boxShadow = "0 4px 15px rgba(40, 167, 69, 0.3)";
          }}
        >
          <h2 style={{ marginBottom: "1rem", fontSize: "1.5rem" }}>🔓 Decrypt</h2>
          <p style={{ fontSize: "1rem", opacity: 0.9 }}>
            Decrypt an image using the original key and metadata
          </p>
        </button>
      </div>

      <div style={{ 
        marginTop: "3rem", 
        padding: "2rem", 
        background: "#f8f9fa", 
        borderRadius: "12px",
        textAlign: "left"
      }}>
        <h3 style={{ marginBottom: "1rem", color: "#333" }}>How it works:</h3>
        <ul style={{ 
          listStyle: "none", 
          padding: 0,
          lineHeight: "1.8"
        }}>
          <li style={{ marginBottom: "0.5rem" }}>
            <strong>🔒 Encryption:</strong> Upload an image, provide a key, and get an encrypted image plus metadata
          </li>
          <li style={{ marginBottom: "0.5rem" }}>
            <strong>💾 Save:</strong> Download both the encrypted image and metadata file
          </li>
          <li style={{ marginBottom: "0.5rem" }}>
            <strong>🔓 Decryption:</strong> Upload the encrypted image, metadata, and original key to recover the image
          </li>
        </ul>
      </div>
    </div>
  );
};

export default Home;
