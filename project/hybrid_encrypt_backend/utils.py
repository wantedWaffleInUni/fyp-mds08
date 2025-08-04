import numpy as np

def npcr(img1, img2):
    return float(np.sum(img1 != img2) / img1.size * 100)

def uaci(img1, img2):
    return float(np.mean(np.abs(img1.astype(np.int16) - img2.astype(np.int16)) / 255) * 100)
