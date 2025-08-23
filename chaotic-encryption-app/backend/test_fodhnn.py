import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis.strategies import integers
import hypothesis.extra.numpy as hnp

from encryption.fodhnn_encryptor import FODHNNEncryptor
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

KEY = "k"
NONCE = "n"

def make_enc():
    # Keep memory_window modest so tests are fast
    return FODHNNEncryptor(memory_window=128)

def random_img(h, w, c):
    if c == 1:
        return np.random.randint(0, 256, size=(h, w), dtype=np.uint8)
    return np.random.randint(0, 256, size=(h, w, c), dtype=np.uint8)

@pytest.mark.parametrize("shape", [(64,64,3), (128,96,3), (32,32,1)])
def test_roundtrip_fixed_shapes(shape):
    enc = make_enc()
    img = random_img(*shape)
    C = enc.encrypt_image(img, KEY, NONCE)
    P = enc.decrypt_image(C, KEY, NONCE)
    assert np.array_equal(P, img)

def test_determinism():
    enc = make_enc()
    img = random_img(64, 64, 3)
    C1 = enc.encrypt_image(img, KEY, NONCE)
    C2 = enc.encrypt_image(img, KEY, NONCE)
    assert np.array_equal(C1, C2)

def test_nonce_sensitivity():
    enc = make_enc()
    img = random_img(64, 64, 3)
    C1 = enc.encrypt_image(img, KEY, NONCE)
    C2 = enc.encrypt_image(img, KEY, NONCE + "x")
    assert not np.array_equal(C1, C2)

def test_key_sensitivity():
    enc = make_enc()
    img = random_img(64, 64, 3)
    C1 = enc.encrypt_image(img, KEY, NONCE)
    C2 = enc.encrypt_image(img, KEY + "x", NONCE)
    assert not np.array_equal(C1, C2)

@pytest.mark.parametrize("shape", [(1,1,1), (1,2,1), (2,1,3), (2,3,3), (17,19,3)])
def test_tiny_and_odd_shapes(shape):
    enc = make_enc()
    img = random_img(*shape)
    C = enc.encrypt_image(img, KEY, NONCE)
    P = enc.decrypt_image(C, KEY, NONCE)
    assert np.array_equal(P, img)
    assert C.shape == img.shape and C.dtype == np.uint8

def test_input_validation():
    enc = make_enc()
    img = random_img(16, 16, 1)
    with pytest.raises(ValueError): enc.encrypt_image(None, KEY, NONCE)
    with pytest.raises(ValueError): enc.encrypt_image(img, "", NONCE)
    with pytest.raises(ValueError): enc.encrypt_image(img, KEY, "")

# Property-based: random sizes & pixels (kept small for speed)
@given(
    h=integers(min_value=2, max_value=48),
    w=integers(min_value=2, max_value=48),
    c=integers(min_value=1, max_value=3),
)
@settings(max_examples=25, deadline=None)
def test_roundtrip_property(h, w, c):
    enc = make_enc()
    shape = (h, w) if c == 1 else (h, w, c)
    img = np.random.randint(0, 256, size=shape, dtype=np.uint8)
    C = enc.encrypt_image(img, KEY, NONCE)
    P = enc.decrypt_image(C, KEY, NONCE)
    assert np.array_equal(P, img)
