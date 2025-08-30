// import React, { useCallback } from 'react';
// import { useDropzone } from 'react-dropzone';
// 
// const ImageUploader = ({ onImageUpload, acceptedFileTypes = ['image/*'] }) => {
//   const onDrop = useCallback((acceptedFiles) => {
//     if (acceptedFiles.length > 0) {
//       const file = acceptedFiles[0];
//       onImageUpload(file);
//     }
//   }, [onImageUpload]);
// 
//   const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
//     onDrop,
//     accept: acceptedFileTypes.reduce((acc, type) => {
//       acc[type] = [];
//       return acc;
//     }, {}),
//     multiple: false,
//     maxSize: 16 * 1024 * 1024, // 16MB
//   });
// 
//   return (
//     <div
//       {...getRootProps()}
//       className={`dropzone ${isDragActive ? 'active' : ''} ${isDragReject ? 'error' : ''}`}
//     >
//       <input {...getInputProps()} />
//       <div className="dropzone-icon">
//         📁
//       </div>
//       <div className="dropzone-text">
//         {isDragActive ? (
//           isDragReject ? (
//             <span>❌ File type not supported</span>
//           ) : (
//             <span>📤 Drop the image here...</span>
//           )
//         ) : (
//           <span>
//             📤 Drag & drop an image here, or click to select
//             <br />
//             <small>Supports: PNG, JPG, JPEG, GIF, BMP (Max 16MB)</small>
//           </span>
//         )}
//       </div>
//     </div>
//   );
// };
// 
// export default ImageUploader;

// components/ImageUploader.jsx
import React, { useCallback, useEffect, useState } from 'react';
import { useDropzone } from 'react-dropzone';

const ImageUploader = ({
  onImageUpload,
  acceptedFileTypes = ['image/*'],
  previewUrl, // optional: parent-managed preview
}) => {
  const [localPreview, setLocalPreview] = useState('');

  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        onImageUpload(file);

        // create an internal preview if parent didn't provide one
        const nextUrl = URL.createObjectURL(file);
        setLocalPreview((prev) => {
          if (prev) URL.revokeObjectURL(prev);
          return nextUrl;
        });
      }
    },
    [onImageUpload]
  );

  // cleanup object URL on unmount/change
  useEffect(() => {
    return () => {
      if (localPreview) URL.revokeObjectURL(localPreview);
    };
  }, [localPreview]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: acceptedFileTypes.reduce((acc, type) => {
      acc[type] = [];
      return acc;
    }, {}),
    multiple: false,
    maxSize: 16 * 1024 * 1024, // 16MB
  });

  const preview = previewUrl || localPreview;

  return (
    <div
      {...getRootProps()}
      className={`dropzone ${isDragActive ? 'active' : ''} ${isDragReject ? 'error' : ''}`}
    >
      <input {...getInputProps()} />

      {preview ? (
        <img src={preview} alt="Selected preview" className="dropzone-preview" />
      ) : (
        <>
          <div className="dropzone-icon">📁</div>
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
                <small>Supports: PNG, JPG, JPEG, GIF, BMP, etc. (Max 16MB)</small>
              </span>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default ImageUploader;
