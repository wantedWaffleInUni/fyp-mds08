import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Convert file to base64
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
  });
};

// API functions
export const encryptImage = async (imageFile, key = 'default_key_123', algorithm = 'chaos', nonce) => {
  try {
    const imageData = await fileToBase64(imageFile);
    
    const payload = {
      image: imageData,
      key: key,
      algorithm: (algorithm || 'chaos').toLowerCase(),
    };
    if (payload.algorithm === 'fodhnn' || '2dlasm' && nonce) {
      payload.nonce = nonce;
    }
    const response = await api.post('/encrypt', payload);
    
    return response.data;
  } catch (error) {
    console.error('Encryption error:', error);
    throw new Error(error.response?.data?.error || 'Encryption failed');
  }
};

export const decryptImage = async (imageFile, key = 'default_key_123', algorithm = 'chaos', nonce) => {
  try {
    const imageData = await fileToBase64(imageFile);
    
    const payload = {
      image: imageData,
      key: key,
      algorithm: (algorithm || 'chaos').toLowerCase(),
    };
    if (payload.algorithm === 'fodhnn' || '2dlasm') {
      if (!nonce) {
        throw new Error('Nonce is required for FODHNN decryption');
      }
      payload.nonce = nonce;
    }
    const response = await api.post('/decrypt', payload);
    
    return response.data;
  } catch (error) {
    console.error('Decryption error:', error);
    throw new Error(error.response?.data?.error || 'Decryption failed');
  }
};

export const downloadImage = async (filename) => {
  try {
    const response = await api.get(`/download/${filename}`, {
      responseType: 'blob',
    });
    
    return response.data;
  } catch (error) {
    console.error('Download error:', error);
    throw new Error('Download failed');
  }
};

export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check error:', error);
    throw new Error('API health check failed');
  }
};

export default api;
