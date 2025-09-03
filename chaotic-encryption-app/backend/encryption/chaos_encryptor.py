import numpy as np
import cv2
import hashlib
from typing import Tuple

from .encryptor_interface import EncryptorInterface

class ChaosEncryptor(EncryptorInterface):
    """
    Chaotic Image Encryption Module
    
    This module provides chaotic encryption and decryption for images.
    The implementation uses chaotic maps for generating encryption keys
    and applying pixel-level transformations.
    """
    
    def __init__(self):
        """Initialize the chaotic encryptor"""
        self.logistic_r = 3.9  # Logistic map parameter
        self.initial_x = 0.5   # Initial condition for logistic map
        
    def requires_nonce(self) -> bool:
        """Chaos encryptor does not require a nonce."""
        return False
    
    def get_algorithm_name(self) -> str:
        """Get the name of the encryption algorithm."""
        return 'chaos'
        
    def _generate_key_from_string(self, key_string: str) -> Tuple[float, float]:
        """
        Generate chaotic map parameters from a string key
        
        Args:
            key_string: Input key string
            
        Returns:
            Tuple of (r, x0) parameters for chaotic map
        """
        # Use SHA-256 hash of the key string
        hash_obj = hashlib.sha256(key_string.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert hash to numerical values
        r = 3.5 + (int(hash_hex[:8], 16) % 1000) / 10000.0  # r in [3.5, 4.0]
        x0 = (int(hash_hex[8:16], 16) % 10000) / 10000.0   # x0 in [0, 1]
        
        return r, x0
    
    def _logistic_map(self, r: float, x0: float, iterations: int) -> np.ndarray:
        """
        Generate chaotic sequence using logistic map
        
        Args:
            r: Logistic map parameter
            x0: Initial condition
            iterations: Number of iterations
            
        Returns:
            Array of chaotic values
        """
        sequence = np.zeros(iterations)
        x = x0
        
        for i in range(iterations):
            x = r * x * (1 - x)
            sequence[i] = x
            
        return sequence
    
    def _generate_permutation_matrix(self, height: int, width: int, key: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate permutation matrices for row and column shuffling
        
        Args:
            height: Image height
            width: Image width
            key: Encryption key
            
        Returns:
            Tuple of (row_perm, col_perm) permutation arrays
        """
        r, x0 = self._generate_key_from_string(key)
        
        # Generate chaotic sequences
        row_seq = self._logistic_map(r, x0, height)
        col_seq = self._logistic_map(r, x0 + 0.1, width)  # Different initial condition
        
        # Create permutation indices
        row_perm = np.argsort(row_seq)
        col_perm = np.argsort(col_seq)
        
        return row_perm, col_perm
    
    def _permute_image(self, image: np.ndarray, row_perm: np.ndarray, col_perm: np.ndarray) -> np.ndarray:
        """
        Apply permutation to image using chaotic sequences
        
        Args:
            image: Input image
            row_perm: Row permutation array
            col_perm: Column permutation array
            
        Returns:
            Permuted image
        """
        # Apply row permutation
        permuted = image[row_perm, :]
        
        # Apply column permutation
        permuted = permuted[:, col_perm]
        
        return permuted
    
    def _inverse_permute_image(self, image: np.ndarray, row_perm: np.ndarray, col_perm: np.ndarray) -> np.ndarray:
        """
        Apply inverse permutation to image
        
        Args:
            image: Input image
            row_perm: Row permutation array
            col_perm: Column permutation array
            
        Returns:
            Inverse permuted image
        """
        # Create inverse permutation arrays
        row_inv = np.argsort(row_perm)
        col_inv = np.argsort(col_perm)
        
        # Apply inverse permutation
        result = image[row_inv, :]
        result = result[:, col_inv]
        
        return result
    
    def _xor_with_chaotic_sequence(self, image: np.ndarray, key: str) -> np.ndarray:
        """
        XOR image with chaotic sequence
        
        Args:
            image: Input image
            key: Encryption key
            
        Returns:
            XORed image
        """
        r, x0 = self._generate_key_from_string(key)
        
        # Generate chaotic sequence for XOR
        total_pixels = image.shape[0] * image.shape[1] * image.shape[2]
        chaotic_seq = self._logistic_map(r, x0 + 0.2, total_pixels)
        
        # Scale chaotic sequence to [0, 255]
        chaotic_seq = (chaotic_seq * 255).astype(np.uint8)
        
        # Reshape sequence to match image dimensions
        chaotic_seq = chaotic_seq.reshape(image.shape)
        
        # XOR operation
        result = cv2.bitwise_xor(image, chaotic_seq)
        
        return result
    
    def encrypt_image(self, image: np.ndarray, key: str, nonce: str = None) -> np.ndarray:
        """
        Encrypt an image using chaotic encryption
        
        Args:
            image: Input image as numpy array (BGR format)
            key: Encryption key string
            nonce: Not used by chaos encryptor (kept for interface compatibility)
            
        Returns:
            Encrypted image as numpy array
        """
        # Validate inputs using interface methods
        self.validate_image(image)
        self.validate_encryption_params(key, nonce)
        
        # Get image dimensions
        height, width = image.shape[:2]
        
        # Generate permutation matrices
        row_perm, col_perm = self._generate_permutation_matrix(height, width, key)
        
        # Step 1: Apply permutation
        permuted_image = self._permute_image(image, row_perm, col_perm)
        
        # Step 2: XOR with chaotic sequence
        encrypted_image = self._xor_with_chaotic_sequence(permuted_image, key)
        
        return encrypted_image
    
    def decrypt_image(self, image: np.ndarray, key: str, nonce: str = None) -> np.ndarray:
        """
        Decrypt an image using chaotic decryption
        
        Args:
            image: Encrypted image as numpy array (BGR format)
            key: Decryption key string (must be same as encryption key)
            nonce: Not used by chaos encryptor (kept for interface compatibility)
            
        Returns:
            Decrypted image as numpy array
        """
        # Validate inputs using interface methods
        self.validate_image(image)
        self.validate_encryption_params(key, nonce)
        
        # Get image dimensions
        height, width = image.shape[:2]
        
        # Generate permutation matrices (same as encryption)
        row_perm, col_perm = self._generate_permutation_matrix(height, width, key)
        
        # Step 1: XOR with chaotic sequence (same operation as encryption)
        decrypted_image = self._xor_with_chaotic_sequence(image, key)
        
        # Step 2: Apply inverse permutation
        decrypted_image = self._inverse_permute_image(decrypted_image, row_perm, col_perm)
        
        return decrypted_image
    
    def get_encryption_info(self, key: str, nonce: str = None) -> dict:
        """
        Get information about the encryption parameters
        
        Args:
            key: Encryption key
            nonce: Not used by chaos encryptor
            
        Returns:
            Dictionary with encryption parameters
        """
        # Use the interface method and add chaos-specific info
        info = super().get_encryption_info(key, nonce)
        
        r, x0 = self._generate_key_from_string(key)
        info.update({
            'logistic_r': r,
            'initial_x': x0
        })
        
        return info
