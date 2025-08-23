import React, { useEffect, useState } from "react";

interface EncryptedViewerProps {
  imageUrl: string | null;
}

const EncryptedViewer: React.FC<EncryptedViewerProps> = ({ imageUrl }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (imageUrl) {
      console.log("EncryptedViewer: Loading image from URL:", imageUrl);
      setLoading(true);
      setError(null);
    }
  }, [imageUrl]);

  const handleImageLoad = () => {
    console.log("EncryptedViewer: Image loaded successfully");
    setLoading(false);
    setError(null);
  };

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    console.error("EncryptedViewer: Image failed to load:", e);
    setLoading(false);
    setError("Failed to load image");
  };

  return (
    <div style={{ minHeight: 280, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
      {loading && (
        <div style={{ width: 220, margin: "1rem 0" }}>
          <div style={{
            width: "100%",
            height: 8,
            background: "#eee",
            borderRadius: 4,
            overflow: "hidden"
          }}>
            <div
              style={{
                width: "100%",
                height: "100%",
                background: "linear-gradient(90deg, #007bff 40%, #66b3ff 100%)",
                animation: "progressBar 1.2s linear infinite"
              }}
            />
          </div>
          <style>
            {`
              @keyframes progressBar {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
              }
            `}
          </style>
          <div style={{ textAlign: "center", color: "#888", fontSize: 14, marginTop: 8 }}>
            Loading encrypted image...
          </div>
        </div>
      )}
      {error && (
        <div style={{ color: "#dc3545", fontSize: 14, marginTop: 8, textAlign: "center" }}>
          {error}
        </div>
      )}
      {imageUrl && !loading && !error && (
        <img
          src={imageUrl}
          alt="Encrypted"
          width={256}
          height={256}
          style={{
            border: "1px solid #ccc",
            borderRadius: 8,
            marginTop: 8
          }}
          onLoad={handleImageLoad}
          onError={handleImageError}
        />
      )}
      {!imageUrl && !loading && !error && (
        <div style={{ color: "#aaa", fontSize: 16, marginTop: 32 }}>
          No encrypted image to display.
        </div>
      )}
    </div>
  );
};

export default EncryptedViewer;
