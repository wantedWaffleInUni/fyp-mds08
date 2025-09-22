from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
# from flask.json.provider import DefaultJSONProvider
import os
import uuid
import cv2
import numpy as np
from PIL import Image
import io
import base64
from werkzeug.utils import secure_filename
import hashlib
import secrets
from functools import wraps
from datetime import datetime, timedelta
import json
from encryption.fodhnn_encryptor import FODHNNEncryptor
from encryption.another_2d import LASMEncryptorFB
from encryption.acm_2dscl import HybridEncryptorFB
from encryption.bulban_encryptor import BulbanEncryptor


from utils import calculate_entropy, calculate_npcr, calculate_uaci

def save_encrypted_image(image: np.ndarray, filepath: str) -> bool:
    """
    Save encrypted image with optimized compression for high-entropy data.
    
    For encrypted images with high entropy, we use multiple strategies:
    1. Try maximum PNG compression first
    2. If that fails, try JPEG with high quality
    3. As a last resort, save as uncompressed binary with .enc extension
    
    Args:
        image: Encrypted image as numpy array
        filepath: Path where to save the image
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Strategy 1: Maximum PNG compression
        success = cv2.imwrite(filepath, image, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        
        if success:
            return True
            
        # Strategy 2: JPEG with high quality (better for some high-entropy data)
        jpeg_path = filepath.replace('.png', '.jpg')
        success = cv2.imwrite(jpeg_path, image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if success:
            # Rename the file back to original extension
            os.rename(jpeg_path, filepath)
            return True
        
        # Strategy 3: Save as binary format (most efficient for high-entropy data)
        binary_path = filepath.replace('.png', '.enc')
        with open(binary_path, 'wb') as f:
            # Write image dimensions first
            f.write(image.shape[0].to_bytes(4, 'big'))  # height
            f.write(image.shape[1].to_bytes(4, 'big'))  # width
            if len(image.shape) == 3:
                f.write(image.shape[2].to_bytes(4, 'big'))  # channels
            else:
                f.write((1).to_bytes(4, 'big'))  # grayscale = 1 channel
            # Write raw image data
            f.write(image.tobytes())
        
        # Rename to original extension
        os.rename(binary_path, filepath)
        return True
        
    except Exception as e:
        print(f"Error saving encrypted image: {e}")
        return False

def load_encrypted_image(filepath: str) -> np.ndarray:
    """
    Load encrypted image that may have been saved in different formats.
    
    Args:
        filepath: Path to the encrypted image file
        
    Returns:
        np.ndarray: Loaded image array, or None if failed
    """
    try:
        # First try standard OpenCV loading
        image = cv2.imread(filepath)
        if image is not None:
            return image
            
        # If that fails, try loading as binary format
        with open(filepath, 'rb') as f:
            height = int.from_bytes(f.read(4), 'big')
            width = int.from_bytes(f.read(4), 'big')
            channels = int.from_bytes(f.read(4), 'big')
            
            if channels == 1:
                shape = (height, width)
            else:
                shape = (height, width, channels)
                
            # Read raw image data
            data = f.read()
            image = np.frombuffer(data, dtype=np.uint8).reshape(shape)
            return image
            
    except Exception as e:
        print(f"Error loading encrypted image: {e}")
        return None

app = Flask(__name__)

cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# One source of truth for CORS
CORS(
    app,
    resources={r"/api/*": {"origins": cors_origins}},
    supports_credentials=True,
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    max_age=3600,
)

# Configuration
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def _h(s): return hashlib.sha256(s.encode()).hexdigest()


# API Key Management System
class APIKeyManager:
    def __init__(self):
        self.api_keys = {}
        self.load_api_keys()


    def load_api_keys(self):
        """Load API keys from environment variables or create default ones"""
        # Load from environment variables
        api_keys_env = os.getenv('API_KEYS', '')
        if api_keys_env:
            try:
                self.api_keys = json.loads(api_keys_env)
            except json.JSONDecodeError:
                print("Warning: Invalid API_KEYS format in environment variables")
                self.api_keys = {}
        
        # If no keys in environment, create default development keys
        if not self.api_keys:
            self.api_keys = {
                _h('dev_key_1'): {
                    'name': 'Development Key 1',
                    'permissions': ['encrypt', 'decrypt', 'download'],
                    'rate_limit': 100,
                    'created_at': datetime.now().isoformat(),
                    'last_used': None
                },
                _h('dev_key_2'): {
                    'name': 'Development Key 2',
                    'permissions': ['encrypt', 'decrypt'],
                    'rate_limit': 50,
                    'created_at': datetime.now().isoformat(),
                    'last_used': None
                }
            }
            print("Warning: Using default development API keys. Set API_KEYS environment variable for production!")
    
    def validate_api_key(self, api_key):
        """Validate API key and return key info"""
        if not api_key:
            return None
        
        # Hash the provided key for comparison
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Check if key exists
        if key_hash in self.api_keys:
            key_info = self.api_keys[key_hash]
            # Update last used timestamp
            key_info['last_used'] = datetime.now().isoformat()
            return key_info
        
        return None
    
    def has_permission(self, key_info, required_permission):
        """Check if API key has required permission"""
        if not key_info:
            return False
        return required_permission in key_info.get('permissions', [])
    
    def generate_new_key(self, name, permissions, rate_limit=100):
        """Generate a new API key"""
        new_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(new_key.encode()).hexdigest()
        
        self.api_keys[key_hash] = {
            'name': name,
            'permissions': permissions,
            'rate_limit': rate_limit,
            'created_at': datetime.now().isoformat(),
            'last_used': None
        }
        
        return new_key

# Initialize API key manager
api_key_manager = APIKeyManager()

# Authentication Decorator
def require_api_key(required_permission=None):
    """Decorator to require API key authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get API key from header
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                return jsonify({
                    'error': 'API key required',
                    'message': 'Please provide an API key in the X-API-Key header'
                }), 401
            
            # Validate API key
            key_info = api_key_manager.validate_api_key(api_key)
            if not key_info:
                return jsonify({
                    'error': 'Invalid API key',
                    'message': 'The provided API key is invalid or expired'
                }), 401
            
            # Check permissions if required
            if required_permission and not api_key_manager.has_permission(key_info, required_permission):
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': f'API key does not have permission for: {required_permission}'
                }), 403
            
            # Add key info to request context for logging
            request.api_key_info = key_info
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Simple in-memory rate limiting (use Redis in production)
rate_limit_storage = {}

def check_rate_limit(api_key, key_info):
    """Check if API key has exceeded rate limit"""
    current_time = datetime.now()
    hour_key = current_time.strftime('%Y-%m-%d-%H')
    rate_key = f"{api_key}_{hour_key}"
    
    # Get current request count
    current_count = rate_limit_storage.get(rate_key, 0)
    rate_limit = key_info.get('rate_limit', 100)
    
    if current_count >= rate_limit:
        return False, rate_limit
    
    # Increment counter
    rate_limit_storage[rate_key] = current_count + 1
    
    # Clean up old entries (keep only last 24 hours)
    cutoff_time = current_time - timedelta(hours=24)
    cutoff_key = cutoff_time.strftime('%Y-%m-%d-%H')
    
    keys_to_remove = [k for k in rate_limit_storage.keys() if k.split('_')[-1] < cutoff_key]
    for k in keys_to_remove:
        del rate_limit_storage[k]
    
    return True, rate_limit - current_count - 1

def require_rate_limit(f):
    """Decorator to enforce rate limiting"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        key_info = getattr(request, 'api_key_info', None)
        
        if api_key and key_info:
            allowed, remaining = check_rate_limit(api_key, key_info)
            if not allowed:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'API key has exceeded the rate limit of {key_info.get("rate_limit", 100)} requests per hour'
                }), 429
            
            # Add rate limit info to response headers
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(key_info.get('rate_limit', 100))
                response.headers['X-RateLimit-Remaining'] = str(remaining)
            return response
        
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image_from_base64(base64_string, filename):
    """Save base64 image string to file"""
    try:
        # Remove data URL prefix if present
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        return filepath
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

def image_to_base64(image_path):
    """Convert image file to base64 string"""
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        print(f"Error converting image to base64: {e}")
        return None

@app.route('/api/encrypt', methods=['POST'])
@require_api_key('encrypt')
@require_rate_limit
def encrypt_image():
    """Encrypt an uploaded image using chaotic encryption"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Extract image data and key
        image_data = data['image']
        key = data.get('key', 'default_key_123')
        algorithm = str(data.get('algorithm', '2dlasm')).lower()
        
        # Generate unique filename
        original_filename = f"original_{uuid.uuid4()}.png"
        encrypted_filename = f"encrypted_{uuid.uuid4()}.png"
        
        # Save original image
        original_path = save_image_from_base64(image_data, original_filename)
        if not original_path:
            return jsonify({'error': 'Failed to save original image'}), 500
        
        # Read image for processing
        original_img = cv2.imread(original_path)
        if original_img is None:
            return jsonify({'error': 'Failed to read image'}), 500
        
        # Initialize encryptor and encrypt
        if algorithm == 'fodhnn':
            encryptor = FODHNNEncryptor()
        
        elif algorithm == 'acm-2dscl':
            encryptor = HybridEncryptorFB()
        
        elif algorithm == 'bulban':
            # Convert to grayscale if image is colored
            if original_img.ndim == 3:
                original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
            encryptor = BulbanEncryptor()

        else:
            encryptor = LASMEncryptorFB()

        encrypted_img = encryptor.encrypt_image(original_img, key)
        
        # Save encrypted image with optimized compression for high-entropy data
        encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_filename)
        success = save_encrypted_image(encrypted_img, encrypted_path)
        if not success:
            return jsonify({'error': 'Failed to save encrypted image'}), 500
        
        # Calculate metrics
        entropy_original = calculate_entropy(original_img)
        entropy_encrypted = calculate_entropy(encrypted_img)
        npcr_value = calculate_npcr(original_img, encrypted_img)
        uaci_value = calculate_uaci(original_img, encrypted_img)
        
        # Convert images to base64 for response
        original_b64 = image_to_base64(original_path)
        encrypted_b64 = image_to_base64(encrypted_path)
        
        # Clean up original file
        os.remove(original_path)
        
        return jsonify({
            'success': True,
            'original_image': original_b64,
            'encrypted_image': encrypted_b64,
            'encrypted_filename': encrypted_filename,
            'algorithm': algorithm,
            'metrics': {
                'entropy_original': float(entropy_original),
                'entropy_encrypted': float(entropy_encrypted),
                'npcr': float(npcr_value),
                'uaci': float(uaci_value)
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Encryption failed: {str(e)}'}), 500

@app.route('/api/decrypt', methods=['POST'])
@require_api_key('decrypt')
@require_rate_limit
def decrypt_image():
    """Decrypt an uploaded encrypted image"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Extract image data and key
        image_data = data['image']
        key = data.get('key', 'default_key_123')
        algorithm = str(data.get('algorithm', '2dlasm')).lower()
        
        # Generate unique filename
        encrypted_filename = f"encrypted_{uuid.uuid4()}.png"
        decrypted_filename = f"decrypted_{uuid.uuid4()}.png"
        
        # Save encrypted image
        encrypted_path = save_image_from_base64(image_data, encrypted_filename)
        if not encrypted_path:
            return jsonify({'error': 'Failed to save encrypted image'}), 500
        
        # Read image for processing (supports both standard and binary formats)
        encrypted_img = load_encrypted_image(encrypted_path)
        if encrypted_img is None:
            return jsonify({'error': 'Failed to read image'}), 500
        
        # Initialize encryptor and decrypt
        if algorithm == 'fodhnn':
            encryptor = FODHNNEncryptor()

        elif algorithm == 'acm_2dscl':
            encryptor = HybridEncryptorFB()

        elif algorithm == 'bulban':
            if encrypted_img.ndim == 3:
                encrypted_img = cv2.cvtColor(encrypted_img, cv2.COLOR_BGR2GRAY)
            encryptor = BulbanEncryptor()

        else:
            encryptor = LASMEncryptorFB()

        decrypted_img = encryptor.decrypt_image(encrypted_img, key)

        
        # Save decrypted image with optimized compression
        decrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], decrypted_filename)
        success = save_encrypted_image(decrypted_img, decrypted_path)
        if not success:
            return jsonify({'error': 'Failed to save decrypted image'}), 500
        
        # Convert image to base64 for response
        decrypted_b64 = image_to_base64(decrypted_path)
        
        # Clean up encrypted file
        os.remove(encrypted_path)
        
        return jsonify({
            'success': True,
            'decrypted_image': decrypted_b64,
            'decrypted_filename': decrypted_filename,
            'algorithm': algorithm
        })
        
    except Exception as e:
        return jsonify({'error': f'Decryption failed: {str(e)}'}), 500

@app.route('/api/download/<filename>')
@require_api_key('download')
@require_rate_limit
def download_file(filename):
    """Download a processed image file"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 404

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Chaotic Encryption API is running'})

@app.route('/api/cors-info')
def cors_info():
    """CORS debugging endpoint"""
    return jsonify({
        'cors_origins': cors_origins,
        'environment': os.getenv('FLASK_ENV', 'development (default)'),
        'request_origin': request.headers.get('Origin', 'No Origin header'),
        'allowed_methods': ['GET', 'POST', 'OPTIONS'],
        'allowed_headers': ['Content-Type', 'Authorization', 'X-API-Key']
    })

@app.route('/')
def index():
    """API documentation"""
    return jsonify({
        'name': 'Chaotic Image Encryption API',
        'version': '1.0.0',
        'authentication': 'API key required in X-API-Key header',
        'endpoints': {
            'POST /api/encrypt': 'Encrypt an image using chaotic encryption (requires encrypt permission)',
            'POST /api/decrypt': 'Decrypt an encrypted image (requires decrypt permission)',
            'GET /api/download/<filename>': 'Download a processed image (requires download permission)',
            'GET /api/health': 'Health check (no authentication required)',
            'GET /api/keys': 'Manage API keys (requires admin permission)',
            'POST /api/keys': 'Create new API key (requires admin permission)'
        }
    })

# API Key Management Endpoints
@app.route('/api/keys', methods=['GET'])
@require_api_key('admin')
def list_api_keys():
    """List all API keys (admin only)"""
    keys_info = []
    for key_hash, info in api_key_manager.api_keys.items():
        keys_info.append({
            'name': info['name'],
            'permissions': info['permissions'],
            'rate_limit': info['rate_limit'],
            'created_at': info['created_at'],
            'last_used': info['last_used']
        })
    
    return jsonify({'api_keys': keys_info})

@app.route('/api/keys', methods=['POST'])
@require_api_key('admin')
def create_api_key():
    """Create a new API key (admin only)"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    name = data.get('name', 'New API Key')
    permissions = data.get('permissions', ['encrypt', 'decrypt'])
    rate_limit = data.get('rate_limit', 100)
    
    new_key = api_key_manager.generate_new_key(name, permissions, rate_limit)
    
    return jsonify({
        'success': True,
        'api_key': new_key,
        'message': 'API key created successfully. Store it securely - it will not be shown again.'
    })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)
