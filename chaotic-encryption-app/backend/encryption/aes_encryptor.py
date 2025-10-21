from typing import Tuple
import numpy as np
from .encryptor_interface import EncryptorInterface


class AESEncryptor(EncryptorInterface):
    """
    AES-256 CTR-mode encryptor for images.

    Notes:
    - Derives a 32-byte key from the provided string using SHA-256.
    - Uses a deterministic counter (no nonce) derived from the key for
      reproducible encryption/decryption with just the key string.
    - Operates on raw image bytes and preserves the original shape and dtype.
    """

    def get_algorithm_name(self) -> str:
        return 'aes'

    def _derive_key_and_counter(self, key: str) -> Tuple[bytes, int]:
        import hashlib
        key_bytes = hashlib.sha256(key.encode()).digest()  # 32 bytes
        # Deterministic 16-byte initial counter from the key (first 16 bytes)
        iv_bytes = key_bytes[:16]
        initial_value = int.from_bytes(iv_bytes, byteorder='big')
        return key_bytes, initial_value

    def _crypt(self, image: np.ndarray, key: str) -> np.ndarray:
        # Validate inputs
        self.validate_image(image)
        self.validate_encryption_params(key)

        key_bytes, initial_value = self._derive_key_and_counter(key)

        # Convert image to contiguous bytes
        original_shape = image.shape
        original_dtype = image.dtype
        data = image.tobytes()

        # AES-CTR
        from Crypto.Cipher import AES
        # No nonce; use empty nonce and deterministic counter
        cipher = AES.new(key_bytes, AES.MODE_CTR, nonce=b'', initial_value=initial_value)
        out = cipher.encrypt(data)

        # Convert back to ndarray with same shape and dtype
        result = np.frombuffer(out, dtype=original_dtype).reshape(original_shape)
        return result

    def encrypt_image(self, image: np.ndarray, key: str) -> np.ndarray:
        return self._crypt(image, key)

    def decrypt_image(self, image: np.ndarray, key: str) -> np.ndarray:
        # CTR encryption is symmetric; applying the same operation decrypts
        return self._crypt(image, key)


