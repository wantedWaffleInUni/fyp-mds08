# Hybrid Image Encryption Project

This project implements a hybrid image encryption system using chaotic maps and neural networks, with a React frontend and Python Flask backend.

## Project Structure

```
project/
├── hybrid_encrypt_backend/     # Python Flask backend
│   ├── app.py                 # Main Flask application
│   ├── encryption.py          # Encryption/decryption algorithms
│   ├── utils.py               # Utility functions (NPCR, UACI)
│   ├── requirements.txt       # Python dependencies
│   └── static/                # Static files (encrypted/decrypted images)
├── my-react-router-app/       # React frontend
│   ├── app/                   # React Router app structure
│   ├── components/            # Reusable components
│   ├── package.json           # Node.js dependencies
│   └── react-router.config.ts # React Router configuration
└── README.md                  # This file
```

## Features

- **Hybrid Encryption**: Combines chaotic maps (logistic-sine map) with neural networks (fractional-order discrete neural network)
- **Image Processing**: Supports grayscale image encryption/decryption
- **Web Interface**: Modern React frontend with intuitive UI
- **RESTful API**: Flask backend with CORS support
- **Security Analysis**: NPCR and UACI metrics for encryption quality

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd project/hybrid_encrypt_backend
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the Flask server:

   ```bash
   python app.py
   ```

The backend will start on `http://localhost:5000`

### Frontend Setup

1. Navigate to the React app directory:

   ```bash
   cd project/my-react-router-app
   ```

2. Install Node.js dependencies:

   ```bash
   npm install
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

The frontend will start on `http://localhost:5173`

## Usage

1. **Encryption**:
   - Go to the encryption page
   - Upload an image
   - Enter an encryption key
   - Click "Encrypt Image"
   - Download the encrypted image

2. **Decryption**:
   - Go to the decryption page
   - Upload the encrypted image
   - Enter the same encryption key
   - Click "Decrypt Image"
   - Download the decrypted image

## API Endpoints

- `POST /encrypt` - Encrypt an image
- `POST /decrypt` - Decrypt an image
- `POST /analyze` - Analyze encryption quality (NPCR, UACI)
- `GET /static/<filename>` - Serve static files

## Technical Details

### Encryption Algorithm

1. **Key Derivation**: SHA-256 hash of the key generates parameters for chaotic maps
2. **Permutation**: Logistic-sine map creates a chaotic permutation matrix
3. **Diffusion**: Fractional-order discrete neural network generates key stream
4. **XOR Operation**: Combines permuted image with key stream

### Security Features

- **Chaotic Maps**: Logistic-sine map for pixel permutation
- **Neural Networks**: Fractional-order discrete neural network for diffusion
- **Key Sensitivity**: Small key changes produce completely different results
- **Statistical Analysis**: NPCR and UACI metrics for quality assessment

## Troubleshooting

### Common Issues

1. **Chrome DevTools Error**: The 404 route has been added to handle Chrome DevTools requests
2. **CORS Issues**: Backend includes CORS headers for cross-origin requests
3. **Image Format**: Currently supports grayscale images (converted automatically)

### Error Messages

- "No route matches URL" - Fixed by adding catch-all route
- "Decryption failed" - Check if the encryption key is correct
- "Encryption failed" - Ensure the image format is supported

## Development Notes

- The encryption algorithm automatically resizes images to 256x256 for consistency
- The system uses the same key for both encryption and decryption
- All encrypted images are stored temporarily in the `static/` directory
- The frontend automatically prepends the backend URL to image paths

## Future Improvements

- Support for color images
- Multiple encryption algorithms
- Key management system
- Real-time encryption analysis
- Mobile-responsive design improvements
