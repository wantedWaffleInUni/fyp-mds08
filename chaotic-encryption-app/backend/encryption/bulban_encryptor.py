"""
BulbanEncryptor.py
Deterministic image cipher based on the generalized Bulban chaotic map.
This file is a self-contained library module with no executable demo.
"""

import numpy as np
import math
import secrets
from typing import Tuple


# -------------------------------------------------
# 1. Generalized Bulban map
# -------------------------------------------------
def _bulban_next(x: float, a: float = 0.5) -> float:
    """Single iteration of the Bulban chaotic map."""
    four_a = 4 * a
    if x <= four_a + 1e-12:
        x = four_a + 1e-12
    return x * math.sqrt(a / (x - four_a))


def _chaos_sequence(x0: float, length: int) -> np.ndarray:
    """Generate a deterministic chaotic sequence of given length."""
    seq = np.empty(length)
    x = x0
    for i in range(length):
        x = _bulban_next(x)
        seq[i] = x
    return seq


# -------------------------------------------------
# 2. Main cipher class
# -------------------------------------------------
from .encryptor_interface import EncryptorInterface

class BulbanEncryptor(EncryptorInterface):
    """
    Deterministic (key + nonce) Bulban-map image cipher.

    Methods
    -------
    encrypt_image(image, key, nonce) -> np.ndarray
    decrypt_image(image, key, nonce) -> np.ndarray
    """
    
    def requires_nonce(self) -> bool:
        """BulbanEncryptor requires a nonce."""
        return True
    
    def get_algorithm_name(self) -> str:
        """Get the name of the encryption algorithm."""
        return 'bulban'

    # -------------------------------------------------
    # Public API
    # -------------------------------------------------
    def encrypt_image(self,
                      image: np.ndarray,
                      key: str,
                      nonce: str = None) -> np.ndarray:
        """Encrypt a grayscale image."""
        self.validate_image(image)
        self.validate_encryption_params(key, nonce)
        padded, h0, w0 = self._pad_image(image)
        X, DMr, DNr = self._derive_params(key, nonce, *padded.shape)
        cipher = self._encrypt_round(padded, X, DMr, DNr)
        return cipher[:h0, :w0]

    def decrypt_image(self,
                      cipher: np.ndarray,
                      key: str,
                      nonce: str = None) -> np.ndarray:
        """Decrypt a grayscale image."""
        self.validate_image(cipher)
        self.validate_encryption_params(key, nonce)
        padded, h0, w0 = self._pad_image(cipher)
        X, DMr, DNr = self._derive_params(key, nonce, *padded.shape)
        plain = self._decrypt_round(padded, X, DMr, DNr)
        return plain[:h0, :w0]

    # -------------------------------------------------
    # Internal helpers
    # -------------------------------------------------
    @staticmethod
    def _pad_image(img: np.ndarray) -> Tuple[np.ndarray, int, int]:
        """Zero-pad dimensions to multiples of 4."""
        h, w = img.shape
        new_h = math.ceil(h / 4) * 4
        new_w = math.ceil(w / 4) * 4
        padded = np.zeros((new_h, new_w), dtype=img.dtype)
        padded[:h, :w] = img
        return padded, h, w

    def _derive_params(self, key: str, nonce: str, M: int, N: int):
        """Derive deterministic key material from (key, nonce)."""
        seed = (key + "|" + nonce).encode()
        rng = np.random.default_rng(int.from_bytes(seed, 'big'))
        X = rng.random(6) * 100 + 2.0
        X[np.abs(X - 2.0) < 1e-12] += 0.1
        X[np.abs(X - 2.5) < 1e-12] += 0.1
        DMr = int((X[:3].mean() * 1e5) % max(M // 4, 1))
        DNr = int((X[3:6].mean() * 1e5) % max(N // 4, 1))
        return X, DMr, DNr

    # -------------------------------------------------
    # Core encryption / decryption
    # -------------------------------------------------
    def _encrypt_round(self, img: np.ndarray, X: np.ndarray, DMr: int, DNr: int) -> np.ndarray:
        """Single encryption round: shuffle + diffuse."""
        M0, N0 = img.shape
        rng = np.random.default_rng(int.from_bytes(X.tobytes(), 'big'))
        top = rng.integers(0, 256, (1, N0), dtype=np.uint8)
        bottom = rng.integers(0, 256, (1, N0), dtype=np.uint8)
        img = np.vstack([top, img, bottom])
        M, N = img.shape
        img = img.astype(np.int16)

        # Row shifts
        PR = _chaos_sequence(X[0], M)
        PR = (PR * 1e5).astype(np.int64) % N
        for i in range(M):
            img[i] = np.roll(img[i], PR[i])

        # Column shifts
        PC = _chaos_sequence(X[1], N)
        PC = (PC * 1e5).astype(np.int64) % M
        for j in range(N):
            img[:, j] = np.roll(img[:, j], PC[j])

        # Diffusion masks
        DRp = (_chaos_sequence(X[2], N) * 255).astype(np.uint8)
        DRn = (_chaos_sequence(X[3], N) * 255).astype(np.uint8)
        DCp = (_chaos_sequence(X[4], M) * 255).astype(np.uint8)
        DCn = (_chaos_sequence(X[5], M) * 255).astype(np.uint8)

        # Forward diffusion
        up = min(M // 2 + DMr + 1, M)
        for i in range(1, up):
            img[i] = (img[i] + (img[i - 1] ^ DRp)) % 256
        low = max(M // 2 - DMr, 0)
        for i in range(M - 2, low - 1, -1):
            img[i] = (img[i] + (img[i + 1] ^ DRn)) % 256

        left = min(N // 2 + DNr + 1, N)
        for j in range(1, left):
            img[:, j] = (img[:, j] + (img[:, j - 1] ^ DCp)) % 256
        right = max(N // 2 - DNr, 0)
        for j in range(N - 2, right - 1, -1):
            img[:, j] = (img[:, j] + (img[:, j + 1] ^ DCn)) % 256

        return img.astype(np.uint8)

    def _decrypt_round(self, cipher: np.ndarray, X: np.ndarray, DMr: int, DNr: int) -> np.ndarray:
        """Inverse of _encrypt_round."""
        M, N = cipher.shape
        img = cipher.astype(np.int16)

        DCp = (_chaos_sequence(X[4], M) * 255).astype(np.uint8)
        DCn = (_chaos_sequence(X[5], M) * 255).astype(np.uint8)

        right = max(N // 2 - DNr, 0)
        for j in range(right, N - 1):
            img[:, j] = (img[:, j] - (img[:, j + 1] ^ DCn)) % 256
        left = min(N // 2 + DNr + 1, N)
        for j in range(left - 1, 0, -1):
            img[:, j] = (img[:, j] - (img[:, j - 1] ^ DCp)) % 256

        DRp = (_chaos_sequence(X[2], N) * 255).astype(np.uint8)
        DRn = (_chaos_sequence(X[3], N) * 255).astype(np.uint8)

        low = max(M // 2 - DMr, 0)
        for i in range(low, M - 1):
            img[i] = (img[i] - (img[i + 1] ^ DRn)) % 256
        up = min(M // 2 + DMr + 1, M)
        for i in range(up - 1, 0, -1):
            img[i] = (img[i] - (img[i - 1] ^ DRp)) % 256

        # Reverse shifts
        PC = _chaos_sequence(X[1], N)
        PC = (PC * 1e5).astype(np.int64) % M
        for j in range(N):
            img[:, j] = np.roll(img[:, j], -PC[j])

        PR = _chaos_sequence(X[0], M)
        PR = (PR * 1e5).astype(np.int64) % N
        for i in range(M):
            img[i] = np.roll(img[i], -PR[i])

        return img[1:-1, :].astype(np.uint8)