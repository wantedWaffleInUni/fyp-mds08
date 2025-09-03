# EncryptorInterface

The `EncryptorInterface` is an abstract base class that defines a common interface for all image encryption algorithms in the chaotic encryption system. This interface ensures consistency, provides common validation methods, and enables polymorphic usage of different encryptors.

## Overview

The interface standardizes the following aspects across all encryptor implementations:

- **Method signatures**: Consistent `encrypt_image()` and `decrypt_image()` methods
- **Parameter handling**: Support for both key-only and key+nonce encryption schemes
- **Validation**: Common input validation for images and parameters
- **Metadata**: Standardized encryption information extraction
- **Error handling**: Consistent error messages and validation

## Interface Methods

### Abstract Methods (Must Implement)

#### `encrypt_image(image, key, nonce=None)`

Encrypts an input image using the specified algorithm.

**Parameters:**

- `image`: Input image as numpy array (BGR, RGB, or grayscale format)
- `key`: Encryption key string (required)
- `nonce`: Optional nonce for algorithms that require it

**Returns:**

- Encrypted image as numpy array with same shape and dtype as input

#### `decrypt_image(image, key, nonce=None)`

Decrypts an encrypted image using the specified algorithm.

**Parameters:**

- `image`: Encrypted image as numpy array
- `key`: Decryption key string (must match encryption key)
- `nonce`: Optional nonce for algorithms that require it (must match encryption nonce)

**Returns:**

- Decrypted image as numpy array with same shape and dtype as input

#### `requires_nonce()`

Indicates whether the encryptor requires a nonce parameter.

**Returns:**

- `True` if nonce is required, `False` if only key is needed

#### `get_algorithm_name()`

Returns the name identifier for the encryption algorithm.

**Returns:**

- String identifier (e.g., 'chaos', 'fodhnn', '2dlasm')

### Concrete Methods (Provided by Interface)

#### `get_encryption_info(key, nonce=None)`

Returns metadata about the encryption parameters and algorithm.

**Returns:**

- Dictionary containing algorithm info, nonce requirement, key hash, and nonce hash (if applicable)

#### `validate_encryption_params(key, nonce=None)`

Validates encryption parameters before processing.

**Raises:**

- `ValueError` if parameters are invalid

#### `validate_image(image)`

Validates input image before processing.

**Raises:**

- `ValueError` if image is invalid

## Implemented Encryptors

### 1. ChaosEncryptor

- **Algorithm**: Chaotic Logistic Map
- **Nonce Required**: No
- **Key Type**: String
- **Features**: Permutation + XOR with chaotic sequences

### 2. FODHNNEncryptor

- **Algorithm**: Fractional-Order Discrete Hopfield Neural Network
- **Nonce Required**: Yes
- **Key Type**: String + Nonce
- **Features**: Permutation + Two-pass diffusion

### 3. LASMEncryptor

- **Algorithm**: 2D Logistic Arnold Sine Map
- **Nonce Required**: Yes
- **Key Type**: String + Nonce
- **Features**: Permutation + 2D diffusion

### 4. LASMEncryptorFB

- **Algorithm**: 2D Logistic-Adjusted-Sine Map (FODHNN-compatible)
- **Nonce Required**: Yes
- **Key Type**: String + Nonce
- **Features**: Permutation + Two-pass diffusion

### 5. HybridEncryptorFB

- **Algorithm**: Hybrid Arnold + 2DSCL + Chen
- **Nonce Required**: Yes
- **Key Type**: String + Nonce
- **Features**: Arnold Cat Map + 2D Sine-Cosine-Logistic + Chen diffusion

### 5. BulbanEncryptor

- **Algorithm**: Generalized Bulban Chaotic Map
- **Nonce Required**: Yes
- **Key Type**: String + Nonce
- **Features**: Bulban chaotic sequence + row/column shifts + diffusion

## Usage Examples

### Basic Usage

```python
from encryption import ChaosEncryptor, FODHNNEncryptor

# Create encryptors
chaos_enc = ChaosEncryptor()
fodhnn_enc = FODHNNEncryptor()

# Encrypt with ChaosEncryptor (no nonce)
encrypted_chaos = chaos_enc.encrypt_image(image, "my_key")
decrypted_chaos = chaos_enc.decrypt_image(encrypted_chaos, "my_key")

# Encrypt with FODHNNEncryptor (nonce required)
encrypted_fodhnn = fodhnn_enc.encrypt_image(image, "my_key", "my_nonce")
decrypted_fodhnn = fodhnn_enc.decrypt_image(encrypted_fodhnn, "my_key", "my_nonce")
```

### Polymorphic Usage

```python
from encryption import EncryptorInterface, ChaosEncryptor, FODHNNEncryptor, LASMEncryptor, LASMEncryptorFB, HybridEncryptorFB, BulbanEncryptor

# Create a list of different encryptors
encryptors: list[EncryptorInterface] = [
    ChaosEncryptor(),
    FODHNNEncryptor(),
    LASMEncryptor(),
    LASMEncryptorFB(),
    HybridEncryptorFB(),
    BulbanEncryptor()
]

# Use them polymorphically
for encryptor in encryptors:
    encrypted = encryptor.encrypt_image(image, key)
    decrypted = encryptor.decrypt_image(encrypted, key)
    
    success = np.array_equal(image, decrypted)
    print(f"{encryptor.get_algorithm_name()}: {'✅' if success else '❌'}")
```

### Validation and Error Handling

```python
from encryption import ChaosEncryptor

encryptor = ChaosEncryptor()

# Validate inputs before processing
try:
    encryptor.validate_image(image)
    encryptor.validate_encryption_params(key)
    
    # Proceed with encryption
    encrypted = encryptor.encrypt_image(image, key)
except ValueError as e:
    print(f"Validation error: {e}")
```

## Adding New Encryptors

To add a new encryptor class:

1. **Inherit from `EncryptorInterface`**:

   ```python
   from .encryptor_interface import EncryptorInterface
   
   class MyNewEncryptor(EncryptorInterface):
   ```

2. **Implement all abstract methods**:
   - `encrypt_image()`
   - `decrypt_image()`
   - `requires_nonce()`
   - `get_algorithm_name()`

3. **Use interface validation methods**:

   ```python
   def encrypt_image(self, image, key, nonce=None):
       self.validate_image(image)
       self.validate_encryption_params(key, nonce)
       # ... implementation
   ```

4. **Add to `__init__.py`**:

   ```python
   from .my_new_encryptor import MyNewEncryptor
   
   __all__ = [
       'EncryptorInterface',
       'ChaosEncryptor',
       'FODHNNEncryptor',
       'LASMEncryptor',
       'MyNewEncryptor'
   ]
   ```

## Benefits

- **Consistency**: All encryptors follow the same interface
- **Maintainability**: Common functionality is centralized
- **Extensibility**: Easy to add new encryption algorithms
- **Type Safety**: Interface provides clear contracts
- **Testing**: Common validation and utility methods
- **Documentation**: Clear expectations for implementers

## Testing

Run the comprehensive test suite to verify interface implementation:

```bash
cd backend
python test_interface.py
```

Run a quick import and instantiation test:

```bash
cd backend
python quick_test.py
```

## Current Status

All encryptor classes now implement the `EncryptorInterface` and use key-only encryption:

- ✅ **ChaosEncryptor** - Chaotic Logistic Map (key-only)
- ✅ **FODHNNEncryptor** - Fractional-Order Discrete Hopfield Neural Network (key-only)
- ✅ **LASMEncryptor** - 2D Logistic Arnold Sine Map (key-only)
- ✅ **LASMEncryptorFB** - 2D Logistic-Adjusted-Sine Map (key-only)
- ✅ **HybridEncryptorFB** - Hybrid Arnold + 2DSCL + Chen (key-only)
- ✅ **BulbanEncryptor** - Generalized Bulban Chaotic Map (key-only)
