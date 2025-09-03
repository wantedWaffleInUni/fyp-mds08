from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import numpy as np


class EncryptorInterface(ABC):
    """
    Abstract base class defining the interface for all image encryptor classes.
    
    This interface ensures that all encryptor implementations provide:
    - Image encryption and decryption methods
    - Support for both key-only and key+nonce encryption schemes
    - Consistent error handling and validation
    - Metadata extraction capabilities
    """
    
    @abstractmethod
    def encrypt_image(self, image: np.ndarray, key: str) -> np.ndarray:
        """
        Encrypt an image using the specified algorithm.
        
        Args:
            image: Input image as numpy array (BGR, RGB, or grayscale format)
            key: Encryption key string (required)
            
        Returns:
            Encrypted image as numpy array with same shape and dtype as input
            
        Raises:
            ValueError: If image is None or key is empty
            NotImplementedError: If the encryptor doesn't support the requested operation
        """
        pass
    
    @abstractmethod
    def decrypt_image(self, image: np.ndarray, key: str) -> np.ndarray:
        """
        Decrypt an image using the specified algorithm.
        
        Args:
            image: Encrypted image as numpy array (BGR, RGB, or grayscale format)
            key: Decryption key string (must match encryption key)
            
        Returns:
            Decrypted image as numpy array with same shape and dtype as input
            
        Raises:
            ValueError: If image is None or key is empty
            NotImplementedError: If the encryptor doesn't support the requested operation
        """
        pass
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """
        Get the name of the encryption algorithm.
        
        Returns:
            String identifier for the algorithm (e.g., 'chaos', 'fodhnn', '2dlasm')
        """
        pass
    
    def get_encryption_info(self, key: str) -> Dict[str, Any]:
        """
        Get information about the encryption parameters and metadata.
        
        Args:
            key: Encryption key
            
        Returns:
            Dictionary with encryption parameters, algorithm info, and metadata
        """
        info = {
            'algorithm': self.get_algorithm_name(),
            'key_hash': self._hash_key(key)
        }
        
        return info
    
    def validate_encryption_params(self, key: str) -> None:
        """
        Validate encryption parameters before processing.
        
        Args:
            key: Encryption key to validate
            
        Raises:
            ValueError: If parameters are invalid
        """
        if not key or not key.strip():
            raise ValueError("Encryption key cannot be empty")
    
    def validate_image(self, image: np.ndarray) -> None:
        """
        Validate input image before processing.
        
        Args:
            image: Image to validate
            
        Raises:
            ValueError: If image is invalid
        """
        if image is None:
            raise ValueError("Input image cannot be None")
            
        if image.size == 0:
            raise ValueError("Input image is empty")
            
        if image.ndim not in (2, 3):
            raise ValueError(f"Image must be 2D (grayscale) or 3D (color), got {image.ndim}D")
            
        if image.ndim == 3 and image.shape[2] not in (1, 3):
            raise ValueError(f"Color image must have 1 or 3 channels, got {image.shape[2]}")
    
    def _hash_key(self, key: str) -> str:
        """
        Create a hash of the key for metadata purposes.
        
        Args:
            key: Key to hash
            
        Returns:
            Hexadecimal hash string (first 16 characters)
        """
        import hashlib
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def __str__(self) -> str:
        """String representation of the encryptor."""
        return f"{self.__class__.__name__}(algorithm={self.get_algorithm_name()})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the encryptor."""
        return f"{self.__class__.__name__}(algorithm={self.get_algorithm_name()})"
