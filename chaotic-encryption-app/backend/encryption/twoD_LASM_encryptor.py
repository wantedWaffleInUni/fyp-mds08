import hashlib
from dataclasses import dataclass
from typing import Tuple

import numpy as np
import cv2


# =========================
# Utilities / helpers
# =========================
def _as_uint8(img: np.ndarray) -> np.ndarray:
    if img.dtype == np.uint8:
        return img
    return np.clip(img, 0, 255).astype(np.uint8)

def _flatten_per_channel(img: np.ndarray) -> Tuple[np.ndarray, int, int, int]:
    """Return (flat, H, W, C) where flat shape = (C, H*W)."""
    if img.ndim == 2:
        H, W = img.shape
        return img.reshape(1, H * W), H, W, 1
    H, W, C = img.shape
    flat = np.moveaxis(img, -1, 0).reshape(C, H * W)
    return flat, H, W, C

def _unflatten_per_channel(flat: np.ndarray, H: int, W: int, C: int) -> np.ndarray:
    if C == 1:
        return flat.reshape(H, W).astype(np.uint8)
    arr = flat.reshape(C, H, W)
    return np.moveaxis(arr, 0, -1).astype(np.uint8)


# =========================
# LASM chaotic sequence
# =========================
def generate_2d_lasm_sequence(x0: float, y0: float, a: float, shape: Tuple[int, int]):
    M, N = shape
    total = M * N
    x_seq = np.zeros(total)
    y_seq = np.zeros(total)
    x, y = x0, y0
    for i in range(total):
        x_new = np.sin(np.pi * (a * y + (1 - a) * x))
        y_new = np.sin(np.pi * (a * x_new + (1 - a) * y))
        x, y = x_new, y_new
        x_seq[i] = x
        y_seq[i] = y
    return x_seq.reshape(shape), y_seq.reshape(shape)


# =========================
# Mask generator (strong)
# =========================
def byte_mask_from_S(S: np.ndarray, salt: int = 0x9E3779B9) -> np.uint8:
    """
    Turn float chaos S in [0,1) into a well-mixed uint8 mask.
    - 32-bit quantization
    - mix with coordinates
    - avalanche-style integer hashing
    """
    H, W = S.shape
    u = (np.floor(S * (1 << 32)).astype(np.uint32) ^ np.uint32(salt))

    I = np.fromfunction(lambda i, j: (i.astype(np.uint32) << 16) ^ j.astype(np.uint32),
                        (H, W), dtype=int)
    u ^= I

    u ^= (u >> 15)
    u *= np.uint32(0x85EBCA6B)
    u ^= (u >> 13)
    u *= np.uint32(0xC2B2AE35)
    u ^= (u >> 16)

    return (u & 0xFF).astype(np.uint8)


# =========================
# Encryptor (LASM-based)
# =========================
@dataclass
class LASMKeyParams:
    a1: float; a2: float
    x01: float; y01: float   # seeds for round 1 (perm)
    x02: float; y02: float   # seeds for round 2 (diff)


from .encryptor_interface import EncryptorInterface

class LASMEncryptor(EncryptorInterface):
    """
    Deterministic (key + nonce) LASM-based image cipher:
      1) Row/col permutation from LASM S1 (key+nonce+shape).
      2) Two-pass diffusion with LASM S2 (vectorized horizontal & vertical).
    Fully invertible without transmitting any logs.
    """

    # def __init__(self):
    #     pass
    """
    Deterministic (key + nonce) LASM-based image cipher.
    """
    def __init__(self, memory_window: int = 256, burn_in: int = 1024):
        self.memory_window = int(memory_window)
        self.burn_in = int(burn_in)
        

    
    def get_algorithm_name(self) -> str:
        """Get the name of the encryption algorithm."""
        return '2dlasm'

    # ---------- key derivation ----------
    def _derive_params(self, key: str) -> LASMKeyParams:
        """
        Derive stable LASM parameters from SHA-256(key).
        The mapping keeps 'a' in a nice chaotic band and seeds in (0,1).
        """
        h = hashlib.sha256(key.encode()).digest()
        def u32(i):  # 4-byte to uint32
            return int.from_bytes(h[4*i:4*(i+1)], "big", signed=False)

        def map01(u):  # map uint32 -> (0,1) open interval
            x = (u + 0.5) / (1 << 32)
            return min(max(x, 1e-9), 1.0 - 1e-9)

        def map_to(u, lo, hi):
            return lo + ((u + 0.5) / (1 << 32)) * (hi - lo)

        # two a's (one for perm, one for diffusion)
        a1 = map_to(u32(0), 0.65, 0.95)
        a2 = map_to(u32(1), 0.65, 0.95)
        x01 = map01(u32(2)); y01 = map01(u32(3))
        x02 = map01(u32(4)); y02 = map01(u32(5))
        return LASMKeyParams(a1, a2, x01, y01, x02, y02)

    def _lasm_maps(self, H: int, W: int, params: LASMKeyParams):
        # round 1 maps (permutation keys)
        S1x, S1y = generate_2d_lasm_sequence(params.x01, params.y01, params.a1, (H, W))
        # round 2 map (diffusion mask base)
        S2x, S2y = generate_2d_lasm_sequence(params.x02, params.y02, params.a2, (H, W))
        S2 = (S2x + S2y) % 1.0
        return (S1x % 1.0, S1y % 1.0), (S2 % 1.0)

    # ---------- permutation ----------
    @staticmethod
    def _row_col_permutation_from_maps(H: int, W: int, S1x: np.ndarray, S1y: np.ndarray):
        # Build integer keys (avoid Python tuples)
        X = (np.floor(S1x * (1 << 32)).astype(np.uint64))
        Y = (np.floor(S1y * (1 << 32)).astype(np.uint64))

        row_primary   = X.sum(axis=1)
        row_tiebreak  = Y[:, 0]
        row_perm = np.lexsort((row_tiebreak, row_primary))

        col_primary   = Y.sum(axis=0)
        col_tiebreak  = X[0, :]
        col_perm = np.lexsort((col_tiebreak, col_primary))

        return row_perm, col_perm

    @staticmethod
    def _apply_permutation(img: np.ndarray, row_perm: np.ndarray, col_perm: np.ndarray) -> np.ndarray:
        if img.ndim == 2:
            return img[row_perm, :][:, col_perm]
        return img[row_perm, :, :][:, col_perm, :]

    @staticmethod
    def _invert_permutation(img: np.ndarray, row_perm: np.ndarray, col_perm: np.ndarray) -> np.ndarray:
        row_inv = np.argsort(row_perm)
        col_inv = np.argsort(col_perm)
        if img.ndim == 2:
            return img[:, col_inv][row_inv, :]
        return img[:, col_inv, :][row_inv, :, :]

    # ---------- diffusion (vectorized 2D, XOR-chained) ----------
    @staticmethod
    def _diffuse_2d_uint8(img2d: np.ndarray, S: np.ndarray) -> np.ndarray:
        # Two independent masks from S
        mask_h = byte_mask_from_S(S, salt=0xA5A5A5A5).astype(np.uint8)
        mask_v = byte_mask_from_S(S, salt=0x5A5A5A5A).astype(np.uint8)

        # horizontal: prefixxor(img ^ mask_h) along axis=1
        A = np.bitwise_xor(img2d, mask_h)
        O_h = np.bitwise_xor.accumulate(A, axis=1)

        # vertical: prefixxor(O_h ^ mask_v) along axis=0
        B = np.bitwise_xor(O_h, mask_v)
        O = np.bitwise_xor.accumulate(B, axis=0)
        return O

    @staticmethod
    def _inv_diffuse_2d_uint8(O2d: np.ndarray, S: np.ndarray) -> np.ndarray:
        mask_h = byte_mask_from_S(S, salt=0xA5A5A5A5).astype(np.uint8)
        mask_v = byte_mask_from_S(S, salt=0x5A5A5A5A).astype(np.uint8)

        # undo vertical
        B = np.empty_like(O2d, dtype=np.uint8)
        B[0, :]  = np.bitwise_xor(O2d[0, :],  mask_v[0, :])
        B[1:, :] = np.bitwise_xor(np.bitwise_xor(O2d[1:, :], O2d[:-1, :]), mask_v[1:, :])

        # undo horizontal
        img = np.empty_like(O2d, dtype=np.uint8)
        img[:, 0]  = np.bitwise_xor(B[:, 0],  mask_h[:, 0])
        img[:, 1:] = np.bitwise_xor(np.bitwise_xor(B[:, 1:], B[:, :-1]), mask_h[:, 1:])
        return img

    # ---------- public API ----------
    def encrypt_image(self, image_bgr_or_gray: np.ndarray, key: str) -> np.ndarray:
        """
        Encrypt a grayscale or BGR image with key.
        Output has the same shape/dtype.
        """
        self.validate_image(image_bgr_or_gray)
        self.validate_encryption_params(key)
        img = _as_uint8(image_bgr_or_gray)
        H, W = img.shape[:2]

        params = self._derive_params(key)
        (S1x, S1y), S2 = self._lasm_maps(H, W, params)

        # 1) permutation (same row/col for all channels)
        row_perm, col_perm = self._row_col_permutation_from_maps(H, W, S1x, S1y)
        P = self._apply_permutation(img, row_perm, col_perm)

        # 2) diffusion (per-channel)
        if P.ndim == 2:
            Cimg = self._diffuse_2d_uint8(P, S2)
        else:
            Cimg = np.empty_like(P)
            for c in range(P.shape[2]):
                Cimg[:, :, c] = self._diffuse_2d_uint8(P[:, :, c], S2)
        return Cimg

    def decrypt_image(self, cipher_bgr_or_gray: np.ndarray, key: str) -> np.ndarray:
        """
        Decrypt image encrypted with encrypt_image using the same key.
        """
        self.validate_image(cipher_bgr_or_gray)
        self.validate_encryption_params(key)
        Cimg = _as_uint8(cipher_bgr_or_gray)
        H, W = Cimg.shape[:2]

        params = self._derive_params(key)
        (S1x, S1y), S2 = self._lasm_maps(H, W, params)

        # invert diffusion
        if Cimg.ndim == 2:
            P = self._inv_diffuse_2d_uint8(Cimg, S2)
        else:
            P = np.empty_like(Cimg)
            for c in range(Cimg.shape[2]):
                P[:, :, c] = self._inv_diffuse_2d_uint8(Cimg[:, :, c], S2)

        # invert permutation
        row_perm, col_perm = self._row_col_permutation_from_maps(H, W, S1x, S1y)
        P0 = self._invert_permutation(P, row_perm, col_perm)
        return P0