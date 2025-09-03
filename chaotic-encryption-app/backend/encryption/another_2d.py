# lasm_encryptor_fb.py
# Header-less, FODHNN-compatible LASM encryptor (API parity)
import hashlib
from dataclasses import dataclass
from typing import Tuple

import numpy as np
import cv2


# ---------------------------
# Helpers (match your FODHNN scaffolding)
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
# LASM core (2D Logistic-Adjusted-Sine Map)
# ---------------------------

@dataclass
class LASMKey:
    mu: float
    x0: float
    y0: float

def _lasm2d_next(x: float, y: float, mu: float) -> Tuple[float, float]:
    # Canonical LASM update; outputs re-scaled to [0,1)
    xn = np.sin(np.pi * mu * (y + 3.0) * x * (1.0 - x))
    yn = np.sin(np.pi * mu * (xn + 3.0) * y * (1.0 - y))
    return (xn + 1.0) * 0.5, (yn + 1.0) * 0.5

def _lasm2d_sequence_pair(shape: Tuple[int, int], x0: float, y0: float, mu: float,
                          burn_in: int) -> Tuple[np.ndarray, np.ndarray]:
    """Generate Sx, Sy in [0,1) for given shape using LASM with burn-in."""
    H, W = shape
    x, y = float(x0), float(y0)
    for _ in range(max(0, burn_in)):
        x, y = _lasm2d_next(x, y, mu)
    Sx = np.empty((H, W), dtype=np.float64)
    Sy = np.empty((H, W), dtype=np.float64)
    for i in range(H):
        for j in range(W):
            x, y = _lasm2d_next(x, y, mu)
            Sx[i, j] = x
            Sy[i, j] = y
    # strictly inside [0,1)
    eps = np.nextafter(1.0, 0.0)
    np.clip(Sx, 0.0, eps, out=Sx)
    np.clip(Sy, 0.0, eps, out=Sy)
    return Sx, Sy

def _quantize_mix(S: np.ndarray, salt: int = 0) -> np.ndarray:
    """Quantize chaos to 32/64-bit with avalanche-style mixing + coordinates."""
    H, W = S.shape
    u = np.floor(S * (1 << 32)).astype(np.uint64) ^ np.uint64(salt)
    I = np.fromfunction(lambda i, j: (i.astype(np.uint64) << 32) ^ j.astype(np.uint64), (H, W))
    u ^= I
    # SplitMix64-style avalanche
    u ^= (u >> 30)
    u *= np.uint64(0xBF58476D1CE4E5B9)
    u ^= (u >> 27)
    u *= np.uint64(0x94D049BB133111EB)
    u ^= (u >> 31)
    return u  # uint64

def _mask_bytes_from_S(S: np.ndarray, salt: int = 0) -> np.ndarray:
    u = _quantize_mix(S, salt=salt)
    return (u & np.uint64(0xFF)).astype(np.uint8)


# ---------------------------
# Keystreams + permutation
# ---------------------------

from .encryptor_interface import EncryptorInterface

class LASMEncryptorFB(EncryptorInterface):
    """
Deterministic (key) LASM-based image cipher with
    header-less decrypt:

      1) Row/col permutation from LASM Sx,Sy (chaos-only; no plaintext in perms).
      2) Two-pass diffusion (forward accumulate + backward undo) with LASM byte keystream.

    API mirrors FODHNNEncryptor:
      encrypt_image(img, key) -> cipher
decrypt_image(cipher, key) -> img
    """

    def __init__(self, burn_in: int = 1024):
        self.burn_in = int(burn_in)
        

    
    def get_algorithm_name(self) -> str:
        """Get the name of the encryption algorithm."""
        return 'lasm_fb'

    # --- parameter derivation ---

    def _derive_key(self, key: str) -> LASMKey:
        """
        Map SHA-256(key) to mu in (0.70,0.95) and seeds x0,y0 in (0,1).
        """
        h = hashlib.sha256(key.encode()).hexdigest()
        u = [_u32(int(h[i:i+8], 16)) for i in range(0, 64, 8)]
        mu = _map_to_interval(u[0], 0.70, 0.95)
        x0 = _clip01(_map_to_interval(u[1], 0.0, 1.0))
        y0 = _clip01(_map_to_interval(u[2], 0.0, 1.0))
        return LASMKey(mu=mu, x0=x0, y0=y0)

    def _keystreams_xyz(self, H: int, W: int, key: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Produce X, Y (for perms) and Z (byte keystream) all deterministic from key.
        X,Y are uint32 (flattened); Z is uint8 length L=H*W.
        """
        k = self._derive_key(key)
        Sx, Sy = _lasm2d_sequence_pair((H, W), k.x0, k.y0, k.mu, burn_in=self.burn_in)
        Ssum = (Sx + Sy) % 1.0

        # Permutation keys (mix separately + salts)
        Xmat = _quantize_mix(Sx, salt=0x9E3779B97F4A7C15)  # golden ratio salt
        Ymat = _quantize_mix(Sy, salt=0x85EBCA6B)         # murmur3 salt

        # Reduce to row/col keys via sums; flatten to feed row/col perms function below
        X = Xmat.flatten().astype(np.uint32) ^ (np.arange(H * W, dtype=np.uint32) * np.uint32(0x9E37))
        Y = Ymat.flatten().astype(np.uint32) ^ (np.arange(H * W, dtype=np.uint32) * np.uint32(0x85EB))

        # Diffusion bytes
        Z = _mask_bytes_from_S(Ssum, salt=0xC2B2AE35).flatten()
        return X, Y, Z

    # --- permutation (identical structure to your FODHNN version) ---

    def _row_col_permutation(self, H: int, W: int, X: np.ndarray, Y: np.ndarray):
        Xr = X.reshape(H, W).astype(np.int64, copy=False)
        Yr = Y.reshape(H, W).astype(np.int64, copy=False)

        row_primary = Xr.sum(axis=1)
        row_tiebreak = Yr[:, 0]
        row_perm = np.lexsort((row_tiebreak, row_primary))

        col_primary = Yr.sum(axis=0)
        col_tiebreak = Xr[0, :]
        col_perm = np.lexsort((col_tiebreak, col_primary))

        return row_perm, col_perm

    def _apply_permutation(self, img: np.ndarray, row_perm: np.ndarray, col_perm: np.ndarray) -> np.ndarray:
        if img.ndim == 2:
            return img[row_perm, :][:, col_perm]
        return img[row_perm, :, :][:, col_perm, :]

    def _invert_permutation(self, img: np.ndarray, row_perm: np.ndarray, col_perm: np.ndarray) -> np.ndarray:
        row_inv = np.argsort(row_perm)
        col_inv = np.argsort(col_perm)
        if img.ndim == 2:
            return img[:, col_inv][row_inv, :]
        return img[:, col_inv, :][row_inv, :, :]

    # --- diffusion (forward/backward, channel-wise) ---

    @staticmethod
    def _diffuse_forward(flat: np.ndarray, z: np.ndarray) -> np.ndarray:
        # out[i] = sum_{j<=i} (flat[j] + ks[j]) mod 256
        C, L = flat.shape
        ks = z.astype(np.uint16, copy=False)
        arr = flat.astype(np.uint16) + ks[None, :]
        out = np.add.accumulate(arr, axis=1) & 0xFF
        return out.astype(np.uint8)

    @staticmethod
    def _diffuse_backward(flat_c: np.ndarray, z: np.ndarray) -> np.ndarray:
        # invertible backward chaining with reversed keystream
        C, L = flat_c.shape
        out = np.empty_like(flat_c, dtype=np.uint8)
        ks = z.astype(np.uint8, copy=False)
        for c in range(C):
            out[c, L-1] = (int(flat_c[c, L-1]) - int(ks[L-1])) & 0xFF
            for i in range(L-2, -1, -1):
                out[c, i] = (int(flat_c[c, i]) - int(flat_c[c, i+1]) - int(ks[i])) & 0xFF
        return out

    @staticmethod
    def _undiffuse_backward(d: np.ndarray, z: np.ndarray) -> np.ndarray:
        # inverse of _diffuse_backward
        C, L = d.shape
        out = np.empty_like(d, dtype=np.uint8)
        ks = z.astype(np.uint8, copy=False)
        for c in range(C):
            out[c, L-1] = (int(d[c, L-1]) + int(ks[L-1])) & 0xFF
            for i in range(L-2, -1, -1):
                out[c, i] = (int(d[c, i]) + int(out[c, i+1]) + int(ks[i])) & 0xFF
        return out

    @staticmethod
    def _undiffuse_forward(c: np.ndarray, z: np.ndarray) -> np.ndarray:
        # inverse of _diffuse_forward
        ks = z.astype(np.int16, copy=False)
        c16 = c.astype(np.int16)
        out = np.empty_like(c16)
        out[:, 0] = c16[:, 0] - ks[0]
        out[:, 1:] = c16[:, 1:] - c16[:, :-1] - ks[1:]
        return (out & 0xFF).astype(np.uint8)

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

    # --- public API (matches FODHNNEncryptor) ---

    def encrypt_image(self, image_bgr_or_gray: np.ndarray, key: str) -> np.ndarray:
        self.validate_image(image_bgr_or_gray)
        self.validate_encryption_params(key)
        img = _as_uint8(image_bgr_or_gray)
        H, W = img.shape[:2]

        X, Y, Z = self._keystreams_xyz(H, W, key)

        # 1) permutation
        row_perm, col_perm = self._row_col_permutation(H, W, X, Y)
        P = self._apply_permutation(img, row_perm, col_perm)

        # 2) diffusion (forward then backward) channel-wise
        flat, H, W, C = _flatten_per_channel(P)
        c1 = self._diffuse_forward(flat, Z)
        c2 = self._diffuse_backward(c1, Z[::-1])  # use reversed Z for second pass
        Cimg = _unflatten_per_channel(c2, H, W, C)
        return Cimg

    def decrypt_image(self, cipher_bgr_or_gray: np.ndarray, key: str) -> np.ndarray:
        self.validate_image(cipher_bgr_or_gray)
        self.validate_encryption_params(key)
        Cimg = _as_uint8(cipher_bgr_or_gray)
        H, W = Cimg.shape[:2]

        X, Y, Z = self._keystreams_xyz(H, W, key)

        # invert diffusion (inverse order)
        flat_c, H, W, C = _flatten_per_channel(Cimg)
        d1 = self._undiffuse_backward(flat_c, Z[::-1])
        p  = self._undiffuse_forward(d1, Z)
        P = _unflatten_per_channel(p, H, W, C)

        # invert permutation
        row_perm, col_perm = self._row_col_permutation(H, W, X, Y)
        R = self._invert_permutation(P, row_perm, col_perm)
        return R
