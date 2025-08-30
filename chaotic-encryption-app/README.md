# 🔐 Chaotic Image Encryption

A full-stack web application for secure image encryption using chaotic maps and FODHNN (Fractional Order Discrete Hopfield Neural Network). This project demonstrates the advantages of chaotic encryption over traditional methods like AES/RSA for image security.

## 🌟 Features

- **Dual Encryption Algorithms**: 
  - **Chaotic Encryption**: Uses logistic maps and chaotic sequences for pixel-level encryption
  - **FODHNN Encryption**: Fractional Order Discrete Hopfield Neural Network for advanced security
- **Real-time Metrics**: Calculates entropy, NPCR, and UACI for encryption quality assessment
- **Modern UI**: Beautiful, responsive React frontend with drag-and-drop functionality
- **Multiple Formats**: Supports PNG, JPG, JPEG, GIF, BMP images
- **Secure Processing**: Server-side encryption with automatic file cleanup
- **Download Support**: Easy download of encrypted/decrypted images
- **API Testing**: Complete Postman collection for API testing
- **Comprehensive Testing**: Unit tests and hypothesis-based testing

## 🏗️ Architecture

```
chaotic-encryption-app/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API communication
│   │   ├── utils/          # Utility functions
│   │   └── App.jsx         # Main application
│   ├── public/             # Static assets
│   └── package.json
├── backend/                 # Flask backend API
│   ├── app.py              # Main Flask application
│   ├── encryption/         # Encryption modules
│   │   ├── chaos_encryptor.py    # Chaotic encryption
│   │   ├── fodhnn_encryptor.py   # FODHNN encryption
│   │   └── __init__.py
│   ├── utils.py            # Utility functions
│   ├── tests/              # Test files
│   ├── test_images/        # Test image assets
│   ├── test_results/       # Test output files
│   └── requirements.txt    # Python dependencies
├── start.js                # Universal startup script
├── start.sh                # Unix startup script
├── apitest.json            # Postman collection
└── README.md
```

## 🚀 Quick Start

### Universal Startup (Recommended)

**For all platforms (Windows, macOS, Linux):**
```bash
cd chaotic-encryption-app
node start.js
```

### Platform-Specific Startup

**macOS/Linux:**
```bash
cd chaotic-encryption-app
./start.sh
```

**Windows (PowerShell):**
```powershell
cd chaotic-encryption-app
pwsh -ExecutionPolicy Bypass -File start.ps1
```

### Manual Startup

If the scripts don't work, start manually:

**Backend:**
```bash
cd chaotic-encryption-app/backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

**Frontend:**
```bash
cd chaotic-encryption-app/frontend
npm install
npm start
```

### Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- pip (Python package manager)

## 📖 Usage

### Encryption Process

1. **Upload Image**: Drag and drop or select an image file
2. **Choose Algorithm**: Select between Chaotic or FODHNN encryption
3. **Enter Key**: Provide an encryption key (optional, default will be used)
4. **Encrypt**: Click the encrypt button to process the image
5. **View Results**: See the encrypted image and quality metrics
6. **Download**: Save the encrypted image to your device

### Decryption Process

1. **Upload Encrypted Image**: Select the previously encrypted image
2. **Choose Algorithm**: Select the same algorithm used for encryption
3. **Enter Key**: Provide the exact same key used for encryption
4. **Enter Nonce** (FODHNN only): Provide the nonce from encryption
5. **Decrypt**: Click the decrypt button to restore the original image
6. **Download**: Save the decrypted image

## 🔬 Encryption Algorithms

### 1. Chaotic Encryption
Based on logistic maps and chaotic sequences:

- **Formula**: x_{n+1} = r * x_n * (1 - x_n)
- **Parameters**: r ∈ [3.5, 4.0], x_0 ∈ [0, 1]
- **Purpose**: Generates chaotic sequences for key generation

**Encryption Steps:**
1. **Key Generation**: Convert string key to chaotic map parameters
2. **Permutation**: Shuffle image pixels using chaotic sequences
3. **XOR Operation**: Apply chaotic sequence XOR to pixel values
4. **Metrics Calculation**: Compute entropy, NPCR, and UACI

### 2. FODHNN Encryption
Fractional Order Discrete Hopfield Neural Network:

- **Type**: Neural network-based encryption
- **Features**: Nonce-based security, fractional order dynamics
- **Advantage**: Enhanced security through neural network complexity

**Encryption Steps:**
1. **Nonce Generation**: Create unique nonce for each encryption
2. **Neural Processing**: Apply FODHNN transformation
3. **Fractional Dynamics**: Use fractional order calculus
4. **Metrics Calculation**: Compute quality metrics

### Security Features
- **Non-linear transformation**: Unpredictable pixel-level changes
- **High sensitivity**: Small key changes produce completely different results
- **Statistical security**: High entropy and low correlation in encrypted images
- **Algorithm diversity**: Multiple encryption methods for different security needs

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
Encrypt an image using chaotic or FODHNN encryption.

**Request:**
```json
{
  "image": "base64_encoded_image",
  "key": "encryption_key",
  "algorithm": "chaos"  // or "fodhnn"
}
```

**Response:**
```json
{
  "success": true,
  "original_image": "base64_original",
  "encrypted_image": "base64_encrypted",
  "encrypted_filename": "encrypted_uuid.png",
  "algorithm": "chaos",
  "nonce": "nonce_value",  // Only for FODHNN
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
  "key": "decryption_key",
  "algorithm": "chaos",  // or "fodhnn"
  "nonce": "nonce_value"  // Required for FODHNN
}
```

**Response:**
```json
{
  "success": true,
  "decrypted_image": "base64_decrypted",
  "decrypted_filename": "decrypted_uuid.png",
  "algorithm": "chaos"
}
```

### GET /api/download/{filename}
Download a processed image file.

### GET /api/health
Health check endpoint.

## 🧪 Testing

### API Testing
Use the provided Postman collection:
```bash
# Import apitest.json into Postman
# Collection includes tests for both algorithms
```

### Backend Testing
```bash
cd backend
source venv/bin/activate
python -m pytest tests/
```

### Algorithm Testing
```bash
cd backend
source venv/bin/activate
python test_encryption.py  # Test chaotic encryption
python test_fodhnn.py      # Test FODHNN encryption
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 🔧 Configuration

### Environment Variables

**Frontend (.env):**
```
REACT_APP_API_URL=http://localhost:5001/api
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

### Port Configuration
- **Backend**: http://localhost:5001
- **Frontend**: http://localhost:3000
- **API Base**: http://localhost:5001/api

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
- **Nonce Security**: FODHNN nonces must be kept secure
- **File Cleanup**: Temporary files are automatically deleted
- **CORS**: Configured for frontend-backend communication
- **Input Validation**: File type and size validation implemented
- **Error Handling**: Secure error messages without sensitive data

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
- Use the provided Postman collection for API testing

## 🔮 Future Enhancements

- [ ] ML-based encryption prediction
- [ ] Additional chaotic maps (Henon, Lorenz)
- [ ] Batch processing
- [ ] Advanced visualization tools
- [ ] Performance optimization
- [ ] Mobile app version
- [ ] Additional neural network architectures
- [ ] Real-time encryption quality monitoring

---

**Built with ❤️ for secure image encryption research and education.**
