from flask import Flask, request, jsonify, send_file, send_from_directory
import cv2
import numpy as np
import os
from encryption import encrypt_image, decrypt_image
from utils import npcr, uaci
from flask_cors import CORS
from flask import after_this_request


# Get the absolute path to the current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static')
CORS(app)
UPLOAD_FOLDER = STATIC_DIR
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print(f"Base directory: {BASE_DIR}")
print(f"Static directory: {STATIC_DIR}")
print(f"Static directory exists: {os.path.exists(STATIC_DIR)}")

@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response



@app.route('/test-html')
def test_html():
    return send_file('test.html')

@app.route('/test-static')
def test_static():
    # Create a simple test image
    test_img = np.ones((100, 100), dtype=np.uint8) * 128
    test_path = os.path.join(UPLOAD_FOLDER, 'test.png')
    cv2.imwrite(test_path, test_img)
    print(f"Test image created at: {test_path}")
    print(f"File exists: {os.path.exists(test_path)}")
    
    # List all files in static directory
    static_files = os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []
    
    return jsonify({
        'message': 'Test image created',
        'test_url': '/static/test.png',
        'full_url': f'http://localhost:5000/static/test.png',
        'file_path': test_path,
        'file_exists': os.path.exists(test_path),
        'static_directory': UPLOAD_FOLDER,
        'static_files': static_files,
        'current_working_dir': os.getcwd()
    })

@app.route('/encrypt', methods=['POST'])
def encrypt_route():
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Check if key is present
        if 'key' not in request.form:
            return jsonify({'error': 'No encryption key provided'}), 400
        
        key = request.form['key']
        if not key.strip():
            return jsonify({'error': 'Empty encryption key'}), 400
        
        # Read and process image
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        print(f"Processing image with shape: {img.shape}")
        print(f"Using key: {key[:10]}...")  # Show first 10 chars for debugging
        
        # Encrypt the image
        encrypted, permutation, key_stream = encrypt_image(img, key)
        
        # Save encrypted image
        encrypted_path = os.path.join(UPLOAD_FOLDER, 'encrypted.png')
        success = cv2.imwrite(encrypted_path, encrypted)
        
        if not success:
            return jsonify({'error': 'Failed to save encrypted image'}), 500
        
        print(f"Encrypted image saved successfully: {encrypted_path}")
        print(f"File size: {os.path.getsize(encrypted_path)} bytes")
        print(f"Encrypted image shape: {encrypted.shape}")
        
        return jsonify({
            'success': True,
            'image_url': f'/static/encrypted.png',
            'message': 'Image encrypted successfully'
        })
        
    except Exception as e:
        print(f"Encryption error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Encryption failed. Please try again.',
            'details': str(e) if app.debug else 'Internal server error'
        }), 500

@app.route('/decrypt', methods=['POST'])
def decrypt_route():
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Check if key is present
        if 'key' not in request.form:
            return jsonify({'error': 'No decryption key provided'}), 400
        
        key = request.form['key']
        if not key.strip():
            return jsonify({'error': 'Empty decryption key'}), 400
        
        # Read and process image
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        cipher_img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if cipher_img is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        print(f"Decrypting image with shape: {cipher_img.shape}")
        print(f"Using key: {key[:10]}...")  # Show first 10 chars for debugging
        
        # Decrypt the image
        decrypted = decrypt_image(cipher_img, key)
        
        # Save decrypted image
        decrypted_path = os.path.join(UPLOAD_FOLDER, 'decrypted.png')
        success = cv2.imwrite(decrypted_path, decrypted)
        
        if not success:
            return jsonify({'error': 'Failed to save decrypted image'}), 500
        
        print(f"Decrypted image saved successfully: {decrypted_path}")
        print(f"Decrypted image shape: {decrypted.shape}")
        
        return jsonify({
            'success': True,
            'image_url': f'/static/decrypted.png',
            'message': 'Image decrypted successfully'
        })
        
    except Exception as e:
        print(f"Decryption error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Decryption failed. Please try again.',
            'details': str(e) if app.debug else 'Internal server error'
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_route():
    try:
        if 'original' not in request.files or 'encrypted' not in request.files:
            return jsonify({'error': 'Both original and encrypted images are required'}), 400
        
        file1 = request.files['original']
        file2 = request.files['encrypted']
        
        img1 = cv2.imdecode(np.frombuffer(file1.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imdecode(np.frombuffer(file2.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
        
        if img1 is None or img2 is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        npcr_value = npcr(img1, img2)
        uaci_value = uaci(img1, img2)
        
        return jsonify({
            'success': True,
            'npcr': npcr_value,
            'uaci': uaci_value,
        })
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Analysis failed. Please try again.',
            'details': str(e) if app.debug else 'Internal server error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
