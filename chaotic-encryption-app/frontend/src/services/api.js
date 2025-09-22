import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';
const API_KEY = process.env.REACT_APP_API_KEY || 'dev_key_1'; // Use environment variable for production

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY, // Add API key to all requests
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
export const encryptImage = async (imageFile, key = 'default_key_123', algorithm = '2dlasm') => {
  try {
    const imageData = await fileToBase64(imageFile);
    
    const payload = {
      image: imageData,
      key: key,
      algorithm: (algorithm || '2dlasm').toLowerCase(),
    };
    const response = await api.post('/encrypt', payload);
    
    return response.data;
  } catch (error) {
    console.error('Encryption error:', error);
    throw new Error(error.response?.data?.error || 'Encryption failed');
  }
};

export const decryptImage = async (imageFile, key = 'default_key_123', algorithm = '2dlasm') => {
  try {
    const imageData = await fileToBase64(imageFile);
    
    const payload = {
      image: imageData,
      key: key,
      algorithm: (algorithm || '2dlasm').toLowerCase(),
    };
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
