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
    file = request.files['image']
    key = request.form['key']
    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    encrypted, permutation, key_stream = encrypt_image(img, key)

    encrypted_path = os.path.join(UPLOAD_FOLDER, 'encrypted.png')
    print(f"Saving encrypted image to: {encrypted_path}")
    cv2.imwrite(encrypted_path, encrypted)
    
    # Debug: Check if file was created
    if os.path.exists(encrypted_path):
        print(f"Encrypted image saved successfully: {encrypted_path}")
        print(f"File size: {os.path.getsize(encrypted_path)} bytes")
    else:
        print(f"Failed to save encrypted image: {encrypted_path}")

    # return jsonify({
    #     'image_url': f'/static/encrypted.png',
    #     'permutation': permutation,
    #     'key_stream': key_stream,
    # })

    return jsonify({'image_url': f'/static/encrypted.png'})



# @app.route('/decrypt', methods=['POST'])
# def decrypt_route():
#     file = request.files['image']
#     key = request.form['key']
#     permutation = list(map(int, request.form.getlist('permutation[]')))
#     key_stream = list(map(int, request.form.getlist('key_stream[]')))

#     img_bytes = file.read()
#     nparr = np.frombuffer(img_bytes, np.uint8)
#     cipher_img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

#     decrypted = decrypt_image(cipher_img, key, permutation, key_stream)
#     decrypted_path = os.path.join(UPLOAD_FOLDER, 'decrypted.png')
#     cv2.imwrite(decrypted_path, decrypted)

#     return jsonify({'image_url': f'/static/decrypted.png'})

@app.route('/decrypt', methods=['POST'])
def decrypt_route():
    file = request.files['image']
    key = request.form['key']

    cipher_img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
    decrypted = decrypt_image(cipher_img, key)
    # (Optional) if you standardized to 256×256 at encrypt time, just return that.
    cv2.imwrite(os.path.join(UPLOAD_FOLDER, 'decrypted.png'), decrypted)
    return jsonify({'image_url': f'/static/decrypted.png'})


@app.route('/analyze', methods=['POST'])
def analyze_route():
    file1 = request.files['original']
    file2 = request.files['encrypted']
    img1 = cv2.imdecode(np.frombuffer(file1.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imdecode(np.frombuffer(file2.read(), np.uint8), cv2.IMREAD_GRAYSCALE)

    return jsonify({
        'npcr': npcr(img1, img2),
        'uaci': uaci(img1, img2),
    })

if __name__ == '__main__':
    app.run(debug=True)
