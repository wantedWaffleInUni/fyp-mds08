from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask.json.provider import DefaultJSONProvider
import os
import uuid
import cv2
import numpy as np
from PIL import Image
import io
import base64
from werkzeug.utils import secure_filename
from encryption.chaos_encryptor import ChaosEncryptor
from encryption.fodhnn_encryptor import FODHNNEncryptor
from encryption.another_2d import LASMEncryptorFB
from utils import calculate_entropy, calculate_npcr, calculate_uaci

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from flask.json.provider import DefaultJSONProvider
import numpy as np

class NumpyJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)

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
def encrypt_image():
    """Encrypt an uploaded image using chaotic encryption"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Extract image data and key
        image_data = data['image']
        key = data.get('key', 'default_key_123')
        algorithm = str(data.get('algorithm', 'chaos')).lower()
        nonce = data.get('nonce')
        
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
            # Generate a nonce if not provided
            if not nonce:
                nonce = uuid.uuid4().hex
            encryptor = FODHNNEncryptor()
            encrypted_img = encryptor.encrypt_image(original_img, key, nonce)

        elif algorithm == '2dlasm':
            if not nonce:
                nonce = uuid.uuid4().hex
            encryptor = LASMEncryptorFB()
            encrypted_img = encryptor.encrypt_image(original_img, key, nonce)


        else:
            encryptor = ChaosEncryptor()
            encrypted_img = encryptor.encrypt_image(original_img, key)
        
        # Save encrypted image
        encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_filename)
        cv2.imwrite(encrypted_path, encrypted_img)
        
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
            'nonce': nonce if algorithm == 'fodhnn' or algorithm == '2dlasm' else None,
            'metrics': {
                'entropy_original': entropy_original,
                'entropy_encrypted': entropy_encrypted,
                'npcr': npcr_value,
                'uaci': uaci_value
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Encryption failed: {str(e)}'}), 500

@app.route('/api/decrypt', methods=['POST'])
def decrypt_image():
    """Decrypt an uploaded encrypted image"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Extract image data and key
        image_data = data['image']
        key = data.get('key', 'default_key_123')
        algorithm = str(data.get('algorithm', 'chaos')).lower()
        nonce = data.get('nonce')
        
        # Generate unique filename
        encrypted_filename = f"encrypted_{uuid.uuid4()}.png"
        decrypted_filename = f"decrypted_{uuid.uuid4()}.png"
        
        # Save encrypted image
        encrypted_path = save_image_from_base64(image_data, encrypted_filename)
        if not encrypted_path:
            return jsonify({'error': 'Failed to save encrypted image'}), 500
        
        # Read image for processing
        encrypted_img = cv2.imread(encrypted_path)
        if encrypted_img is None:
            return jsonify({'error': 'Failed to read image'}), 500
        
        # Initialize encryptor and decrypt
        if algorithm == 'fodhnn':
            if not nonce:
                return jsonify({'error': 'Nonce is required for FODHNN decryption'}), 400
            encryptor = FODHNNEncryptor()
            decrypted_img = encryptor.decrypt_image(encrypted_img, key, nonce)

        elif algorithm == '2dlasm':
            if not nonce:
                return jsonify({'error': 'Nonce is required for 2DLASM decryption'}), 400
            encryptor = LASMEncryptorFB()
            decrypted_img = encryptor.decrypt_image(encrypted_img, key, nonce)

        else:
            encryptor = ChaosEncryptor()
            decrypted_img = encryptor.decrypt_image(encrypted_img, key)
        
        # Save decrypted image
        decrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], decrypted_filename)
        cv2.imwrite(decrypted_path, decrypted_img)
        
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

@app.route('/')
def index():
    """API documentation"""
    return jsonify({
        'name': 'Chaotic Image Encryption API',
        'version': '1.0.0',
        'endpoints': {
            'POST /api/encrypt': 'Encrypt an image using chaotic encryption',
            'POST /api/decrypt': 'Decrypt an encrypted image',
            'GET /api/download/<filename>': 'Download a processed image',
            'GET /api/health': 'Health check'
        }
    })

if __name__ == '__main__':
    app.json = NumpyJSONProvider(app)
    app.run(debug=True, host='0.0.0.0', port=5001)
