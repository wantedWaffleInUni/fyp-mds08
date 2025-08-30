# acm_2dscl.py
# Header-less, compatible hybrid chaotic encryptor (API parity)

import hashlib
from dataclasses import dataclass
from typing import Tuple
from math import tanh as _tanh  # kept for parity; unused
import numpy as np
import cv2


# ---------------------------
# Helpers
# ---------------------------

def _u32(x: int) -> int:
    return x & 0xFFFFFFFF

def _map_to_interval(u32: int, lo: float, hi: float) -> float:
    return lo + (u32 / 0x100000000) * (hi - lo)

def _clip01(x: float, eps: float = 1e-9) -> float:
    return min(max(x, eps), 1.0 - eps)

def _as_uint8(img: np.ndarray) -> np.ndarray:
    if img.dtype == np.uint8:
        return img
    return np.clip(img, 0, 255).astype(np.uint8)

def _flatten_per_channel(img: np.ndarray) -> Tuple[np.ndarray, int, int, int]:
    """Return (flat, H, W, C) where flat shape = (C, H*W)."""
    if img.ndim == 2:
        H, W = img.shape
        C = 1
        flat = img.reshape(1, H * W)
        return flat, H, W, C
    H, W, C = img.shape
    flat = np.moveaxis(img, -1, 0).reshape(C, H * W)
    return flat, H, W, C

def _unflatten_per_channel(flat: np.ndarray, H: int, W: int, C: int) -> np.ndarray:
    if C == 1:
        return flat.reshape(H, W).astype(np.uint8)
    arr = flat.reshape(C, H, W)
    arr = np.moveaxis(arr, 0, -1)
    return arr.astype(np.uint8)


# ---------------------------
# Hybrid chaotic core (Arnold + 2DSCL + Chen)
# ---------------------------

@dataclass
class HybridKey:
    # Arnold Cat Map parameters
    p: int
    q: int
    arnold_iterations: int

    # 2D Sine-Cosine-Logistic parameters
    lambda_param: float
    k: float
    a: float
    b: float
    c: float

    # Chen's chaotic system parameters
    a_chen: float
    b_chen: float
    c_chen: float
    x0: float
    y0: float
    z0: float


class HybridEncryptorFB:
    """
    Deterministic (key + nonce) hybrid chaotic image cipher with:
    1) Arnold Cat Map scrambling (for squares) or keyed row/col permutation (for rectangles)
    2) 2D Sine-Cosine-Logistic XOR mask (self-invertible)
    3) Chen's chaotic system diffusion (exactly one round; symmetric)
    """

    def __init__(self, security_threshold: float = 0.95, burn_in: int = 50):
        self.security_threshold = security_threshold  # kept for parity; not used now
        self.burn_in = int(burn_in)
        self.precision = 1e-16

    # --- parameter derivation ---

    def _derive_key(self, key: str, nonce: str, image_shape: Tuple[int, int]) -> HybridKey:
        """
        Map SHA-256(key|nonce|shape) to chaotic parameters.
        """
        shape_str = f"{image_shape[0]}x{image_shape[1]}"
        h = hashlib.sha256((key + "|" + nonce + "|" + shape_str).encode()).hexdigest()
        u = [_u32(int(h[i:i+8], 16)) for i in range(0, min(len(h), 64), 8)]

        while len(u) < 8:
            u.append(0)

        # Arnold Cat Map parameters (small for efficiency)
        p = int(_map_to_interval(u[0], 1, 3))
        q = int(_map_to_interval(u[1], 1, 3))

        # Image complexity-based arnold iterations (simplified + keyed jitter)
        base_complexity = 0.5
        arnold_iterations = max(3, int(base_complexity * 8) + (u[2] % 5))

        # 2DSCL parameters
        lambda_param = _map_to_interval(u[3], 0.1, 0.9)
        k = 0.9 + lambda_param * 0.1
        a = 6 + lambda_param * 8
        b = 6 + lambda_param * 8
        c = 2 + lambda_param * 8

        # Chen's system parameters (classic)
        a_chen = 35.0
        b_chen = 3.0
        c_chen = 28.0
        x0 = -10.058 + lambda_param * 0.1
        y0 = 0.368 + lambda_param * 0.1
        z0 = 37.368 + lambda_param * 0.1

        return HybridKey(
            p=p, q=q, arnold_iterations=arnold_iterations,
            lambda_param=lambda_param, k=k, a=a, b=b, c=c,
            a_chen=a_chen, b_chen=b_chen, c_chen=c_chen,
            x0=x0, y0=y0, z0=z0
        )

    # --- Arnold Cat Map (squares only) ---

    def _arnold_cat_map(self, image: np.ndarray, key: HybridKey, reverse: bool = False) -> np.ndarray:
        """Apply or reverse Arnold Cat Map scrambling (requires square)."""
        M, N = image.shape
        result = image.copy()
        iterations = key.arnold_iterations
        p, q = key.p, key.q

        for _ in range(iterations):
            temp = np.zeros_like(result)
            if not reverse:
                # Forward
                for x in range(M):
                    for y in range(N):
                        new_x = (x + p * y) % M
                        new_y = (q * x + (p * q + 1) * y) % N
                        temp[new_x, new_y] = result[x, y]
            else:
                # Inverse
                for x in range(M):
                    for y in range(N):
                        new_x = ((p * q + 1) * x - p * y) % M
                        new_y = (-q * x + y) % N
                        temp[new_x, new_y] = result[x, y]
            result = temp
        return result

    # --- Rectangle-safe keyed permutation (deterministic & channel-stable) ---

    def _permute_rect(self, img: np.ndarray, key: "HybridKey", reverse: bool = False, ch: int = 0) -> np.ndarray:
        H, W = img.shape
        # Build a stable 64-bit seed from HybridKey parameters + shape + channel
        seed_src = f"{key.p}|{key.q}|{key.arnold_iterations}|{H}|{W}|{ch}|rect-permute-v1".encode()
        seed = np.frombuffer(hashlib.sha256(seed_src).digest()[:8], dtype=np.uint64)[0]

        rng = np.random.default_rng(seed)
        rperm = np.arange(H); rng.shuffle(rperm)
        cperm = np.arange(W); rng.shuffle(cperm)

        if reverse:
            inv_r = np.argsort(rperm); inv_c = np.argsort(cperm)
            return img[inv_r][:, inv_c]
        else:
            return img[rperm][:, cperm]

    # --- 2D Sine-Cosine-Logistic XOR mask (self-invertible) ---

    def _2dscl_mask(self, H: int, W: int, key: HybridKey) -> np.ndarray:
        x_current = key.lambda_param
        y_current = key.lambda_param

        # Warm-up
        for _ in range(self.burn_in):
            x_next = key.k * np.sin(key.a * np.cos(key.b * np.arccos(np.clip(x_current, -1, 1))) * (y_current + key.c))
            y_next = key.k * np.sin(key.a * np.cos(key.b * np.arccos(np.clip(y_current, -1, 1))) * (x_next + key.c))
            x_current, y_current = np.clip(x_next, -1, 1), np.clip(y_next, -1, 1)

        mask = np.empty((H, W), dtype=np.uint8)
        for i in range(H):
            for j in range(W):
                x_next = key.k * np.sin(key.a * np.cos(key.b * np.arccos(np.clip(x_current, -1, 1))) * (y_current + key.c))
                y_next = key.k * np.sin(key.a * np.cos(key.b * np.arccos(np.clip(y_current, -1, 1))) * (x_next + key.c))
                V = (abs(x_next) + abs(y_next) + key.lambda_param) % 1
                mask[i, j] = int(V * 256) & 0xFF
                x_current, y_current = np.clip(x_next, -1, 1), np.clip(y_next, -1, 1)
        return mask

    def _apply_2dscl_enhancement(self, image: np.ndarray, key: HybridKey) -> np.ndarray:
        H, W = image.shape
        mask = self._2dscl_mask(H, W, key)
        # XOR is its own inverse; same function used in decrypt
        return np.bitwise_xor(image, mask, dtype=np.uint8)

    # --- Chen's Chaotic System Diffusion (exactly one round) ---

    def _generate_chen_keystream(self, length: int, key: HybridKey) -> Tuple[np.ndarray, np.ndarray]:
        x, y, z = key.x0, key.y0, key.z0

        # Warm-up
        for _ in range(self.burn_in):
            x_new = key.a_chen * (y - x)
            y_new = (key.c_chen - key.a_chen) * x - x * z + key.c_chen * y
            z_new = x * y - key.b_chen * z
            x, y, z = x_new * 0.01, y_new * 0.01, z_new * 0.01

        keys = []
        shifts = []
        for _ in range(length):
            x_new = key.a_chen * (y - x)
            y_new = (key.c_chen - key.a_chen) * x - x * z + key.c_chen * y
            z_new = x * y - key.b_chen * z

            key_val = (int(abs(x_new) * 1e5) % 254) + 1      # 1..254
            shift_val = int(abs(y_new) * 1e5) % max(1, length)

            keys.append(key_val)
            shifts.append(shift_val)

            x, y, z = x_new * 0.01, y_new * 0.01, z_new * 0.01

        return np.array(keys, dtype=np.uint8), np.array(shifts, dtype=np.int32)

    def _chen_diffusion(self, image: np.ndarray, key: HybridKey, reverse: bool = False) -> np.ndarray:
        M, N = image.shape
        result = image.copy().astype(np.uint8)

        row_keys, row_shifts = self._generate_chen_keystream(M, key)
        col_keys, col_shifts = self._generate_chen_keystream(N, key)

        if not reverse:
            # Forward: rows then columns
            for row in range(M):
                result[row] = np.bitwise_xor(result[row], row_keys[row], dtype=np.uint8)
                result[row] = np.roll(result[row], -row_shifts[row])

            for col in range(N):
                result[:, col] = np.bitwise_xor(result[:, col], col_keys[col], dtype=np.uint8)
                result[:, col] = np.roll(result[:, col], -col_shifts[col])
        else:
            # Reverse: columns then rows (inverse order)
            for col in reversed(range(N)):
                result[:, col] = np.roll(result[:, col], col_shifts[col])
                result[:, col] = np.bitwise_xor(result[:, col], col_keys[col], dtype=np.uint8)

            for row in reversed(range(M)):
                result[row] = np.roll(result[row], row_shifts[row])
                result[row] = np.bitwise_xor(result[row], row_keys[row], dtype=np.uint8)

        return result

    # --- validation ---

    @staticmethod
    def _validate_image(img: np.ndarray):
        if img is None:
            raise ValueError("image is None")
        if img.ndim not in (2, 3):
            raise ValueError(f"image ndim must be 2 or 3, got {img.ndim}")
        if img.ndim == 3 and img.shape[2] not in (1, 3):
            raise ValueError(f"image channel count must be 1 or 3, got {img.shape[2]}")
        if img.size == 0:
            raise ValueError("image is empty")

    # --- public API (parity with your tests) ---

    def encrypt_image(self, image_bgr_or_gray: np.ndarray, key: str, nonce: str) -> np.ndarray:
        self._validate_image(image_bgr_or_gray)
        if not key:
            raise ValueError("key is required")

        img = _as_uint8(image_bgr_or_gray)
        H, W = img.shape[:2]
        hybrid_key = self._derive_key(key, nonce, (H, W))

        if img.ndim == 2:
            return self._encrypt_channel(img, img, hybrid_key, ch=0)
        else:
            chans = []
            for c in range(img.shape[2]):
                channel = img[:, :, c]
                chans.append(self._encrypt_channel(channel, channel, hybrid_key, ch=c))
            return np.stack(chans, axis=2)

    def decrypt_image(self, cipher_bgr_or_gray: np.ndarray, key: str, nonce: str) -> np.ndarray:
        self._validate_image(cipher_bgr_or_gray)
        if not key:
            raise ValueError("key is required")

        cipher = _as_uint8(cipher_bgr_or_gray)
        H, W = cipher.shape[:2]
        hybrid_key = self._derive_key(key, nonce, (H, W))

        if cipher.ndim == 2:
            return self._decrypt_channel(cipher, hybrid_key, ch=0)
        else:
            chans = []
            for c in range(cipher.shape[2]):
                channel = cipher[:, :, c]
                chans.append(self._decrypt_channel(channel, hybrid_key, ch=c))
            return np.stack(chans, axis=2)

    # --- per-channel pipeline (symmetric; no adaptive rounds) ---

    def _encrypt_channel(self, channel: np.ndarray, original_channel: np.ndarray, key: HybridKey, ch: int = 0) -> np.ndarray:
        # 1) Confusion
        if channel.shape[0] == channel.shape[1]:
            confused = self._arnold_cat_map(channel, key, reverse=False)
        else:
            confused = self._permute_rect(channel, key, reverse=False, ch=ch)

        # 2) 2DSCL XOR mask
        enhanced = self._apply_2dscl_enhancement(confused, key)

        # 3) Single Chen diffusion
        return self._chen_diffusion(enhanced, key, reverse=False)

    def _decrypt_channel(self, cipher_channel: np.ndarray, key: HybridKey, ch: int = 0) -> np.ndarray:
        current = cipher_channel.copy()

        # 3) Reverse Chen
        current = self._chen_diffusion(current, key, reverse=True)

        # 2) Reverse 2DSCL (XOR with same mask)
        current = self._apply_2dscl_enhancement(current, key)

        # 1) Reverse confusion
        if current.shape[0] == current.shape[1]:
            return self._arnold_cat_map(current, key, reverse=True)
        else:
            return self._permute_rect(current, key, reverse=True, ch=ch)
