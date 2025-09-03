import hashlib
from dataclasses import dataclass
from math import tanh as _tanh, gamma
from typing import Tuple, Dict, Any, Optional

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
# FODHNN core (fractional-order discrete Hopfield)
# ---------------------------

@dataclass
class FODHNNKey:
    # fractional order (0,1], NN param p, and initial conditions
    nu: float
    p: float
    x0: float
    y0: float
    z0: float

class FODHNN:
    """
    3-D fractional-order discrete Hopfield NN numerical solution (Caputo-like delta).
    Uses an overflow-free kernel and robust indexing for the fractional sum.
    """
    def __init__(self, key: FODHNNKey, memory_window: int = 256):
        assert 0.0 < key.nu <= 1.0
        self.key = key
        self.W = int(memory_window)

        # Overflow-free kernel: w[0]=1; w[m] = w[m-1] * (nu + m - 1) / m
        w = np.empty(self.W, dtype=np.float64)
        w[0] = 1.0
        for m in range(1, self.W):
            w[m] = w[m - 1] * (key.nu + m - 1.0) / m
        self.w = w

    def iterate(self, n_steps: int, burn_in: int = 1024) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        steps = burn_in + n_steps
        x = np.empty(steps, dtype=np.float64)
        y = np.empty(steps, dtype=np.float64)
        z = np.empty(steps, dtype=np.float64)
        Fx = np.empty(steps, dtype=np.float64)
        Fy = np.empty(steps, dtype=np.float64)
        Fz = np.empty(steps, dtype=np.float64)

        x[0], y[0], z[0] = self.key.x0, self.key.y0, self.key.z0
        Fx[0] = -x[0] + 2.0 * _tanh(x[0]) - 1.2 * _tanh(y[0])
        Fy[0] = -y[0] + (self.key.p + 1.9) * _tanh(x[0]) + 1.71 * _tanh(y[0]) + 1.15 * _tanh(z[0])
        Fz[0] = -z[0] - 4.75 * _tanh(x[0]) + 1.1 * _tanh(z[0])

        for n in range(1, steps):
            L = min(self.W, n)
            w = self.w[:L]

            # Robust index vector for reverse history: [n-1, n-2, ..., n-L]
            idx = np.arange(n - 1, n - 1 - L, -1)

            x[n] = self.key.x0 + float(np.dot(w, Fx[idx]))
            y[n] = self.key.y0 + float(np.dot(w, Fy[idx]))
            z[n] = self.key.z0 + float(np.dot(w, Fz[idx]))

            Fx[n] = -x[n] + 2.0 * _tanh(x[n]) - 1.2 * _tanh(y[n])
            Fy[n] = -y[n] + (self.key.p + 1.9) * _tanh(x[n]) + 1.71 * _tanh(y[n]) + 1.15 * _tanh(z[n])
            Fz[n] = -z[n] - 4.75 * _tanh(x[n]) + 1.1 * _tanh(z[n])

            # Optional safety: bail if diverging
            if not (np.isfinite(x[n]) and np.isfinite(y[n]) and np.isfinite(z[n])):
                raise ValueError("FODHNN state diverged; try a different key/nonce or reduce memory_window")

        return x[burn_in:], y[burn_in:], z[burn_in:]


# ---------------------------
# Keystream + image cipher (per-image nonce, invertible)
# ---------------------------

from .encryptor_interface import EncryptorInterface

class FODHNNEncryptor(EncryptorInterface):
    """
    Deterministic (key + nonce) FODHNN-based image cipher:
      1) Row/col permutation from X,Y keystreams (key+nonce+shape).
      2) Two-pass diffusion with Z keystream (forward & backward chaining).
    Fully invertible without transmitting any swap logs.
    """

    def __init__(self, memory_window: int = 256, burn_in: int = 1024):
        self.memory_window = int(memory_window)
        self.burn_in = int(burn_in)
        
    def requires_nonce(self) -> bool:
        """FODHNN encryptor requires a nonce."""
        return True
    
    def get_algorithm_name(self) -> str:
        """Get the name of the encryption algorithm."""
        return 'fodhnn'

    # --- parameter derivation ---

    def _derive_key(self, key: str, nonce: str) -> FODHNNKey:
        """
        Derive (nu, p, x0, y0, z0) from SHA-256(key|nonce).
        Keep x0,y0,z0 strictly inside (0,1) and nu in (0.6, 0.95].
        """
        h = hashlib.sha256((key + "|" + nonce).encode()).hexdigest()
        u = [_u32(int(h[i:i+8], 16)) for i in range(0, 64, 8)]

        nu = _map_to_interval(u[0], 0.70, 0.95)  # fractional order
        p  = _map_to_interval(u[1], 0.05, 0.25)  # modest coupling
        x0 = _clip01(_map_to_interval(u[2], 0.0, 1.0))
        y0 = _clip01(_map_to_interval(u[3], 0.0, 1.0))
        z0 = _clip01(_map_to_interval(u[4], 0.0, 1.0))
        return FODHNNKey(nu=nu, p=p, x0=x0, y0=y0, z0=z0)

    def _keystreams_xyz(self, H: int, W: int, key: str, nonce: str,
                         burn_in: int = 1024) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        L = H * W
        k = self._derive_key(key, nonce)
        fod = FODHNN(k, memory_window=self.memory_window)
        x, y, z = fod.iterate(L, burn_in=burn_in)

        # Convert to indices/bytes
        # X and Y will form permutation keys; Z will form diffusion bytes.
        # Scale and wrap deterministically:
        scale = 2**16  # large to reduce ties
        X = (np.mod((x * W + np.arange(1, L + 1)) * 1e7, scale)).astype(np.uint32)
        Y = (np.mod((y * W + np.arange(1, L + 1)) * 1e7, scale)).astype(np.uint32)
        Z = ((z - np.floor(z)) * 255.0).astype(np.uint8)  # keystream bytes
        return X, Y, Z

    # --- permutation ---

    def _row_col_permutation(self, H, W, X, Y):
        Xr = X.reshape(H, W)
        Yr = Y.reshape(H, W)

        row_primary = Xr.sum(axis=1).astype(np.int64)
        row_tiebreak = Yr[:, 0].astype(np.int64)
        row_perm = np.lexsort((row_tiebreak, row_primary))  # stable tie-break

        col_primary = Yr.sum(axis=0).astype(np.int64)
        col_tiebreak = Xr[0, :].astype(np.int64)
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

    # --- diffusion (forward/backward chained XOR+ADD, per-channel) ---

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
        C, L = flat_c.shape
        out = np.empty_like(flat_c, dtype=np.uint8)
        ks = z.astype(np.uint8, copy=False)
        for c in range(C):
            out[c, L-1] = (int(flat_c[c, L-1]) - int(ks[L-1])) & 0xFF
            for i in range(L-2, -1, -1):
                out[c, i] = (int(flat_c[c, i]) - int(flat_c[c, i+1]) - int(ks[i])) & 0xFF
        return out

    # --- public API ---

    def _validate_image(self, img: np.ndarray):
        if img is None:
            raise ValueError("image is None")
        if img.ndim not in (2, 3):
            raise ValueError(f"image ndim must be 2 or 3, got {img.ndim}")
        if img.ndim == 3 and img.shape[2] not in (1, 3):
            raise ValueError(f"image channel count must be 1 or 3, got {img.shape[2]}")
        if img.size == 0:
            raise ValueError("image is empty")

    def encrypt_image(self, image_bgr_or_gray: np.ndarray, key: str, nonce: str = None) -> np.ndarray:
        """
        Encrypt BGR or grayscale image with (key, nonce).
        """
        self.validate_image(image_bgr_or_gray)
        self.validate_encryption_params(key, nonce)

        img = _as_uint8(image_bgr_or_gray)
        H, W = img.shape[:2]
        X, Y, Z = self._keystreams_xyz(H, W, key, nonce, burn_in=self.burn_in)

        # 1) permutation
        row_perm, col_perm = self._row_col_permutation(H, W, X, Y)
        P = self._apply_permutation(img, row_perm, col_perm)

        # 2) diffusion (forward then backward) channel-wise
        flat, H, W, C = _flatten_per_channel(P)
        flat_c = self._diffuse_forward(flat, Z)
        flat_c = self._diffuse_backward(flat_c, Z[::-1])  # use reversed Z for the second pass
        Cimg = _unflatten_per_channel(flat_c, H, W, C)
        return Cimg

    @staticmethod
    def _undiffuse_backward(d: np.ndarray, z: np.ndarray) -> np.ndarray:
        C, L = d.shape
        out = np.empty_like(d, dtype=np.uint8)
        ks = z.astype(np.uint8, copy=False)
        for c in range(C):
            # Recover the last element first
            out[c, L-1] = (int(d[c, L-1]) + int(ks[L-1])) & 0xFF
            # Then walk backward, using the ALREADY recovered out[c, i+1]
            for i in range(L-2, -1, -1):
                out[c, i] = (int(d[c, i]) + int(out[c, i+1]) + int(ks[i])) & 0xFF
        return out


    @staticmethod
    def _undiffuse_forward(c: np.ndarray, z: np.ndarray) -> np.ndarray:
        # a[0] = c[0]-ks[0]; a[i] = c[i]-c[i-1]-ks[i]
        ks = z.astype(np.int16, copy=False)
        c16 = c.astype(np.int16)
        out = np.empty_like(c16)
        out[:, 0] = c16[:, 0] - ks[0]
        out[:, 1:] = c16[:, 1:] - c16[:, :-1] - ks[1:]
        return (out & 0xFF).astype(np.uint8)

    def decrypt_image(self, cipher_bgr_or_gray: np.ndarray, key: str, nonce: str = None) -> np.ndarray:
        """
        Decrypt BGR or grayscale image with (key, nonce).
        """
        self.validate_image(cipher_bgr_or_gray)
        self.validate_encryption_params(key, nonce)

        Cimg = _as_uint8(cipher_bgr_or_gray)
        H, W = Cimg.shape[:2]
        X, Y, Z = self._keystreams_xyz(H, W, key, nonce, burn_in=self.burn_in)

        # invert diffusion (inverse order)
        flat_c, H, W, C = _flatten_per_channel(Cimg)
        c = self._undiffuse_backward(flat_c, Z[::-1])
        p = self._undiffuse_forward(c, Z)
        P = _unflatten_per_channel(p, H, W, C)
        row_perm, col_perm = self._row_col_permutation(H, W, X, Y)
        P0 = self._invert_permutation(P, row_perm, col_perm)
        return P0

