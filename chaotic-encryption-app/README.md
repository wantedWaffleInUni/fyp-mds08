# 🔐 Chaotic Image Encryption

A full-stack web application for secure image encryption using chaotic maps. This project demonstrates the advantages of chaotic encryption over traditional methods like AES/RSA for image security.

## 🌟 Features

- **Chaotic Encryption**: Uses logistic maps and chaotic sequences for pixel-level encryption
- **Real-time Metrics**: Calculates entropy, NPCR, and UACI for encryption quality assessment
- **Modern UI**: Beautiful, responsive React frontend with drag-and-drop functionality
- **Multiple Formats**: Supports PNG, JPG, JPEG, GIF, BMP images
- **Secure Processing**: Server-side encryption with automatic file cleanup
- **Download Support**: Easy download of encrypted/decrypted images

## 🏗️ Architecture

```
chaotic-encryption-app/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API communication
│   │   └── App.jsx         # Main application
│   └── package.json
├── backend/                 # Flask backend API
│   ├── app.py              # Main Flask application
│   ├── encryption/         # Chaotic encryption module
│   ├── utils.py            # Utility functions
│   └── requirements.txt    # Python dependencies
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- pip (Python package manager)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd chaotic-encryption-app/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask server:**
   ```bash
   python app.py
   ```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd chaotic-encryption-app/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

The frontend will be available at `http://localhost:3000`

## 📖 Usage

### Encryption Process

1. **Upload Image**: Drag and drop or select an image file
2. **Enter Key**: Provide an encryption key (optional, default will be used)
3. **Encrypt**: Click the encrypt button to process the image
4. **View Results**: See the encrypted image and quality metrics
5. **Download**: Save the encrypted image to your device

### Decryption Process

1. **Upload Encrypted Image**: Select the previously encrypted image
2. **Enter Key**: Provide the exact same key used for encryption
3. **Decrypt**: Click the decrypt button to restore the original image
4. **Download**: Save the decrypted image

## 🔬 Encryption Algorithm

The application uses a chaotic encryption algorithm based on:

### Logistic Map
- **Formula**: x_{n+1} = r * x_n * (1 - x_n)
- **Parameters**: r ∈ [3.5, 4.0], x_0 ∈ [0, 1]
- **Purpose**: Generates chaotic sequences for key generation

### Encryption Steps
1. **Key Generation**: Convert string key to chaotic map parameters
2. **Permutation**: Shuffle image pixels using chaotic sequences
3. **XOR Operation**: Apply chaotic sequence XOR to pixel values
4. **Metrics Calculation**: Compute entropy, NPCR, and UACI

### Security Features
- **Non-linear transformation**: Unpredictable pixel-level changes
- **High sensitivity**: Small key changes produce completely different results
- **Statistical security**: High entropy and low correlation in encrypted images

## 📊 Quality Metrics

### Entropy
- **Range**: 0-8 bits per pixel
- **Target**: >7.5 for excellent encryption
- **Purpose**: Measures randomness in pixel values

### NPCR (Number of Pixel Change Rate)
- **Range**: 0-100%
- **Target**: >99.5% for excellent diffusion
- **Purpose**: Percentage of pixels that changed during encryption

### UACI (Unified Average Changing Intensity)
- **Range**: 0-100%
- **Target**: 33.0-34.0% for ideal encryption
- **Purpose**: Average intensity difference between original and encrypted

## 🛠️ API Endpoints

### POST /api/encrypt
Encrypt an image using chaotic encryption.

**Request:**
```json
{
  "image": "base64_encoded_image",
  "key": "encryption_key"
}
```

**Response:**
```json
{
  "success": true,
  "original_image": "base64_original",
  "encrypted_image": "base64_encrypted",
  "encrypted_filename": "encrypted_uuid.png",
  "metrics": {
    "entropy_original": 7.1234,
    "entropy_encrypted": 7.9876,
    "npcr": 99.67,
    "uaci": 33.45
  }
}
```

### POST /api/decrypt
Decrypt an encrypted image.

**Request:**
```json
{
  "image": "base64_encoded_encrypted_image",
  "key": "decryption_key"
}
```

**Response:**
```json
{
  "success": true,
  "decrypted_image": "base64_decrypted",
  "decrypted_filename": "decrypted_uuid.png"
}
```

### GET /api/download/{filename}
Download a processed image file.

### GET /api/health
Health check endpoint.

## 🔧 Configuration

### Environment Variables

**Frontend (.env):**
```
REACT_APP_API_URL=http://localhost:5000/api
```

**Backend:**
```python
# In app.py
UPLOAD_FOLDER = 'static'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### File Size Limits
- **Maximum image size**: 16MB
- **Supported formats**: PNG, JPG, JPEG, GIF, BMP
- **Output format**: PNG (for consistency)

## 🚀 Deployment

### Frontend Deployment (Vercel/Netlify)

1. **Build the application:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy to Vercel:**
   ```bash
   vercel --prod
   ```

3. **Set environment variables:**
   - `REACT_APP_API_URL`: Your backend API URL

### Backend Deployment (Render/Railway)

1. **Create requirements.txt** (already included)

2. **Create Procfile:**
   ```
   web: gunicorn app:app
   ```

3. **Deploy to Render:**
   - Connect your GitHub repository
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `gunicorn app:app`

## 🔒 Security Considerations

- **Key Management**: Users are responsible for key security
- **File Cleanup**: Temporary files are automatically deleted
- **CORS**: Configured for frontend-backend communication
- **Input Validation**: File type and size validation implemented
- **Error Handling**: Secure error messages without sensitive data

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the documentation
- Review the code comments

## 🔮 Future Enhancements

- [ ] ML-based encryption prediction
- [ ] Additional chaotic maps (Henon, Lorenz)
- [ ] Batch processing
- [ ] Advanced visualization tools
- [ ] Performance optimization
- [ ] Mobile app version

---

**Built with ❤️ for secure image encryption research and education.**
