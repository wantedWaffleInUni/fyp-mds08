#!/usr/bin/env python3
"""
Test script for chaotic encryption functionality
"""

import cv2
import numpy as np
from encryption.chaos_encryptor import ChaosEncryptor
from utils import calculate_entropy, calculate_npcr, calculate_uaci

def create_test_image(width=256, height=256):
    """Create a simple test image"""
    # Create a gradient image
    image = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            image[i, j] = [i % 256, j % 256, (i + j) % 256]
    return image

def test_encryption():
    """Test the encryption and decryption process"""
    print("🔐 Testing Chaotic Image Encryption")
    print("=" * 50)
    
    # Create test image
    print("📸 Creating test image...")
    test_image = create_test_image(128, 128)
    print(f"   Image shape: {test_image.shape}")
    print(f"   Image dtype: {test_image.dtype}")
    
    # Initialize encryptor
    print("\n🔧 Initializing encryptor...")
    encryptor = ChaosEncryptor()
    
    # Test key
    test_key = "test_encryption_key_123"
    print(f"   Test key: {test_key}")
    
    # Get encryption info
    info = encryptor.get_encryption_info(test_key)
    print(f"   Logistic r: {info['logistic_r']:.6f}")
    print(f"   Initial x: {info['initial_x']:.6f}")
    print(f"   Key hash: {info['key_hash']}")
    
    # Encrypt image
    print("\n🔒 Encrypting image...")
    encrypted_image = encryptor.encrypt_image(test_image, test_key)
    print("   ✅ Encryption completed")
    
    # Decrypt image
    print("\n🔓 Decrypting image...")
    decrypted_image = encryptor.decrypt_image(encrypted_image, test_key)
    print("   ✅ Decryption completed")
    
    # Calculate metrics
    print("\n📊 Calculating metrics...")
    entropy_original = calculate_entropy(test_image)
    entropy_encrypted = calculate_entropy(encrypted_image)
    entropy_decrypted = calculate_entropy(decrypted_image)
    npcr_value = calculate_npcr(test_image, encrypted_image)
    uaci_value = calculate_uaci(test_image, encrypted_image)
    
    print(f"   Original entropy: {entropy_original:.4f}")
    print(f"   Encrypted entropy: {entropy_encrypted:.4f}")
    print(f"   Decrypted entropy: {entropy_decrypted:.4f}")
    print(f"   NPCR: {npcr_value:.2f}%")
    print(f"   UACI: {uaci_value:.2f}%")
    
    # Verify decryption
    print("\n✅ Verification...")
    if np.array_equal(test_image, decrypted_image):
        print("   ✅ Perfect decryption - images are identical")
    else:
        print("   ❌ Decryption failed - images are different")
        diff = np.mean(np.abs(test_image.astype(float) - decrypted_image.astype(float)))
        print(f"   Average difference: {diff:.2f}")
    
    # Quality assessment
    print("\n🎯 Quality Assessment:")
    if entropy_encrypted > 7.5:
        print("   🟢 Excellent entropy (>7.5)")
    elif entropy_encrypted > 7.0:
        print("   🟡 Good entropy (>7.0)")
    else:
        print("   🔴 Poor entropy (<7.0)")
    
    if npcr_value > 99.5:
        print("   🟢 Excellent NPCR (>99.5%)")
    elif npcr_value > 99.0:
        print("   🟡 Good NPCR (>99.0%)")
    else:
        print("   🔴 Poor NPCR (<99.0%)")
    
    if 33.0 <= uaci_value <= 34.0:
        print("   🟢 Excellent UACI (33.0-34.0%)")
    elif 32.0 <= uaci_value <= 35.0:
        print("   🟡 Good UACI (32.0-35.0%)")
    else:
        print("   🔴 Poor UACI (outside 32.0-35.0%)")
    
    print("\n🎉 Test completed successfully!")

if __name__ == "__main__":
    test_encryption()
