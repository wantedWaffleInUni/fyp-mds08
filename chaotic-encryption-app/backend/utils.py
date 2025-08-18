import numpy as np
import cv2
from scipy import stats
from typing import Tuple

def calculate_entropy(image: np.ndarray) -> float:
    """
    Calculate the entropy of an image
    
    Args:
        image: Input image as numpy array
        
    Returns:
        Entropy value (bits per pixel)
    """
    if image is None:
        return 0.0
    
    # Convert to grayscale if color image
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Calculate histogram
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist = hist.flatten()
    
    # Remove zero values to avoid log(0)
    hist = hist[hist > 0]
    
    # Normalize histogram
    hist = hist / hist.sum()
    
    # Calculate entropy
    entropy = -np.sum(hist * np.log2(hist))
    
    return entropy

def calculate_npcr(original: np.ndarray, encrypted: np.ndarray) -> float:
    """
    Calculate Number of Pixel Change Rate (NPCR)
    
    NPCR measures the percentage of different pixels between two images
    
    Args:
        original: Original image
        encrypted: Encrypted image
        
    Returns:
        NPCR value (percentage)
    """
    if original.shape != encrypted.shape:
        raise ValueError("Images must have the same dimensions")
    
    # Convert to grayscale if color images
    if len(original.shape) == 3:
        orig_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        enc_gray = cv2.cvtColor(encrypted, cv2.COLOR_BGR2GRAY)
    else:
        orig_gray = original
        enc_gray = encrypted
    
    # Calculate difference
    diff = cv2.absdiff(orig_gray, enc_gray)
    
    # Count non-zero pixels (different pixels)
    different_pixels = np.count_nonzero(diff)
    total_pixels = orig_gray.size
    
    # Calculate NPCR
    npcr = (different_pixels / total_pixels) * 100
    
    return npcr

def calculate_uaci(original: np.ndarray, encrypted: np.ndarray) -> float:
    """
    Calculate Unified Average Changing Intensity (UACI)
    
    UACI measures the average intensity difference between two images
    
    Args:
        original: Original image
        encrypted: Encrypted image
        
    Returns:
        UACI value (percentage)
    """
    if original.shape != encrypted.shape:
        raise ValueError("Images must have the same dimensions")
    
    # Convert to grayscale if color images
    if len(original.shape) == 3:
        orig_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        enc_gray = cv2.cvtColor(encrypted, cv2.COLOR_BGR2GRAY)
    else:
        orig_gray = original
        enc_gray = encrypted
    
    # Calculate absolute difference
    diff = cv2.absdiff(orig_gray, enc_gray)
    
    # Calculate UACI
    uaci = (np.sum(diff) / (orig_gray.size * 255)) * 100
    
    return uaci

def calculate_histogram_similarity(original: np.ndarray, encrypted: np.ndarray) -> float:
    """
    Calculate histogram similarity between two images
    
    Args:
        original: Original image
        encrypted: Encrypted image
        
    Returns:
        Similarity value (0-1, where 1 is identical histograms)
    """
    if len(original.shape) == 3:
        orig_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        enc_gray = cv2.cvtColor(encrypted, cv2.COLOR_BGR2GRAY)
    else:
        orig_gray = original
        enc_gray = encrypted
    
    # Calculate histograms
    hist_orig = cv2.calcHist([orig_gray], [0], None, [256], [0, 256])
    hist_enc = cv2.calcHist([enc_gray], [0], None, [256], [0, 256])
    
    # Normalize histograms
    hist_orig = hist_orig.flatten() / hist_orig.sum()
    hist_enc = hist_enc.flatten() / hist_enc.sum()
    
    # Calculate correlation coefficient
    correlation = np.corrcoef(hist_orig, hist_enc)[0, 1]
    
    return correlation if not np.isnan(correlation) else 0.0

def calculate_psnr(original: np.ndarray, decrypted: np.ndarray) -> float:
    """
    Calculate Peak Signal-to-Noise Ratio (PSNR)
    
    Args:
        original: Original image
        decrypted: Decrypted image
        
    Returns:
        PSNR value (dB)
    """
    if original.shape != decrypted.shape:
        raise ValueError("Images must have the same dimensions")
    
    # Convert to float for calculation
    orig_float = original.astype(np.float64)
    dec_float = decrypted.astype(np.float64)
    
    # Calculate MSE
    mse = np.mean((orig_float - dec_float) ** 2)
    
    if mse == 0:
        return float('inf')
    
    # Calculate PSNR
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    
    return psnr

def analyze_encryption_quality(original: np.ndarray, encrypted: np.ndarray, decrypted: np.ndarray = None) -> dict:
    """
    Comprehensive analysis of encryption quality
    
    Args:
        original: Original image
        encrypted: Encrypted image
        decrypted: Decrypted image (optional)
        
    Returns:
        Dictionary with all quality metrics
    """
    results = {
        'entropy_original': calculate_entropy(original),
        'entropy_encrypted': calculate_entropy(encrypted),
        'npcr': calculate_npcr(original, encrypted),
        'uaci': calculate_uaci(original, encrypted),
        'histogram_similarity': calculate_histogram_similarity(original, encrypted)
    }
    
    if decrypted is not None:
        results['psnr'] = calculate_psnr(original, decrypted)
        results['entropy_decrypted'] = calculate_entropy(decrypted)
    
    return results

def generate_histogram_data(image: np.ndarray) -> dict:
    """
    Generate histogram data for visualization
    
    Args:
        image: Input image
        
    Returns:
        Dictionary with histogram data
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    
    return {
        'bins': list(range(256)),
        'values': hist.flatten().tolist()
    }
