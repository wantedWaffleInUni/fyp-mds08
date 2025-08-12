import cv2
import numpy as np
import os

# Create a simple test image
def create_test_image():
    # Create a 100x100 test image
    test_img = np.ones((100, 100), dtype=np.uint8) * 128
    test_path = os.path.join('static', 'test.png')
    
    # Ensure static directory exists
    os.makedirs('static', exist_ok=True)
    
    # Save the image
    cv2.imwrite(test_path, test_img)
    print(f"Test image created at: {test_path}")
    print(f"File exists: {os.path.exists(test_path)}")
    print(f"File size: {os.path.getsize(test_path)} bytes")
    
    return test_path

if __name__ == "__main__":
    create_test_image()
