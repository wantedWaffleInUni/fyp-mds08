from flask import Flask, request, jsonify, send_from_directory
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
CORS(app)

# Configuration
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# from flask.json.provider import DefaultJSONProvider
# import numpy as np

# class NumpyJSONProvider(DefaultJSONProvider):
#     def default(self, o):
#         if isinstance(o, (np.floating,)):
#             return float(o)
#         if isinstance(o, (np.integer,)):
#             return int(o)
#         if isinstance(o, np.ndarray):
#             return o.tolist()
#         return super().default(o)

SHOWCASE_DIR = os.path.join(app.root_path, "showcase")

@app.route("/showcase/<path:filename>")
def showcase_file(filename):
    return send_from_directory(SHOWCASE_DIR, filename)

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
        
        elif algorithm == 'acm_2dscl':
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
    app.run(debug=True, host='0.0.0.0', port=5001)
