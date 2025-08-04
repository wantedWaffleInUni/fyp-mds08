import numpy as np
import cv2
import hashlib

def logistic_sine_map_2d(x0, y0, r=3.99, a=0.5, size=256):
    x, y = x0, y0
    chaos = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            x = np.sin(np.pi * a * x) + r * x * (1 - x)
            y = np.sin(np.pi * a * y) + r * y * (1 - y)
            x %= 1
            y %= 1
            chaos[i, j] = (x + y) % 1
    return chaos

def fractional_nn(seed, alpha=0.9, steps=65536):
    x = [seed]
    for _ in range(1, steps):
        x_new = (1 - alpha) * x[-1] + alpha * np.tanh(4 * x[-1])
        x.append(x_new)
    return np.array(x) % 1

def key_to_params(key: str):
    hash_digest = hashlib.sha256(key.encode()).hexdigest()
    x0 = int(hash_digest[:8], 16) / 2**32
    y0 = int(hash_digest[8:16], 16) / 2**32
    fseed = int(hash_digest[16:24], 16) / 2**32
    return (x0, y0), fseed

def encrypt_image(img, key):
    img = cv2.resize(img, (256, 256))
    shape = img.shape
    flat_img = img.flatten()

    (x0, y0), fseed = key_to_params(key)
    chaos_map = logistic_sine_map_2d(x0, y0, size=256)
    permutation = np.argsort(chaos_map.flatten())
    permuted = flat_img[permutation]

    fodnn_stream = fractional_nn(fseed, steps=256 * 256)
    key_stream = np.floor(fodnn_stream * 256).astype(np.uint8)
    cipher_flat = np.bitwise_xor(permuted, key_stream)
    cipher_img = cipher_flat.reshape(shape)

    return cipher_img, permutation.tolist(), key_stream.tolist()

def decrypt_image(cipher_img, key, permutation, key_stream):
    shape = cipher_img.shape
    cipher_flat = cipher_img.flatten()
    diffused = np.bitwise_xor(cipher_flat, np.array(key_stream, dtype=np.uint8))
    inverse_perm = np.argsort(np.array(permutation))
    decrypted_flat = diffused[inverse_perm]
    return decrypted_flat.reshape(shape)

