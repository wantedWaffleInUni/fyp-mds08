import React, { useEffect, useState } from "react";

interface DecryptedViewerProps {
  decryptedImgUrl: string | null;
}

const DecryptedViewer: React.FC<DecryptedViewerProps> = ({ decryptedImgUrl }) => {
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (decryptedImgUrl) {
      setLoading(true);
    }
  }, [decryptedImgUrl]);

  const handleImageLoad = () => {
    setLoading(false);
  };

  return (
    <div style={{ minHeight: 280, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
      <h4>Decrypted Image</h4>
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
                background: "linear-gradient(90deg, #28a745 40%, #a8e6a3 100%)",
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
            Loading decrypted image...
          </div>
        </div>
      )}
      {decryptedImgUrl && (
        <img
          src={decryptedImgUrl}
          alt="Decrypted"
          width={256}
          height={256}
          style={{
            display: loading ? "none" : "block",
            border: "1px solid #ccc",
            borderRadius: 8,
            marginTop: 8
          }}
          onLoad={handleImageLoad}
        />
      )}
      {!decryptedImgUrl && !loading && (
        <div style={{ color: "#aaa", fontSize: 16, marginTop: 32 }}>
          No decrypted image to display.
        </div>
      )}
    </div>
  );
};

export default DecryptedViewer;
