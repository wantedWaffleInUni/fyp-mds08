# demo_batch.py
import os, sys, time, math, json, argparse, csv
from datetime import datetime
import numpy as np
import cv2

# --- matplotlib headless for Windows without Tk ---
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from encryption.twoD_LASM_encryptor import LASMEncryptor
from utils import analyze_encryption_quality, generate_histogram_data

DEFAULT_OUT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_results")
VALID_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}

def maybe_downscale(img, max_pixels: int):
    H, W = img.shape[:2]
    L = H * W
    if L <= max_pixels:
        return img
    scale = (max_pixels / L) ** 0.5
    newW, newH = max(1, int(W * scale)), max(1, int(H * scale))
    print(f"[demo] Downscaling from {W}x{H} to {newW}x{newH} for speed.")
    return cv2.resize(img, (newW, newH), interpolation=cv2.INTER_AREA)

def roundtrip(enc, img, key, nonce):
    t0 = time.perf_counter()
    C = enc.encrypt_image(img, key, nonce)
    t1 = time.perf_counter()
    P = enc.decrypt_image(C, key, nonce)
    t2 = time.perf_counter()
    return C, P, (t1 - t0), (t2 - t1)

def fmt(v, d=3):
    if v is None: return ""
    if isinstance(v, (float, np.floating)):
        if math.isinf(v): return "inf"
        if math.isnan(v): return "nan"
    return f"{float(v):.{d}f}"

def save_histogram(image: np.ndarray, out_path: str, title: str):
    h = generate_histogram_data(image)
    bins = np.array(h["bins"])
    vals = np.array(h["values"], dtype=float)
    plt.figure()
    plt.bar(bins, vals, width=1.0)
    plt.title(title)
    plt.xlabel("Intensity (0–255)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close()

def sanitize_for_json(obj):
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]
    if isinstance(obj, (float, np.floating)):
        if math.isinf(obj) or math.isnan(obj):
            return None
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    return obj

def make_run_dir(out_root: str, label: str | None, mem_window: int, max_pixels: int, src_dir: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{ts}_mw{mem_window}_max{max_pixels}"
    if label:
        base += f"_{label}"
    run_dir = os.path.join(out_root, base)
    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, "SOURCE_DIR.txt"), "w", encoding="utf-8") as f:
        f.write(os.path.abspath(src_dir))
    return run_dir

def iter_images(images_dir: str, recursive: bool):
    images_dir = os.path.abspath(images_dir)
    if recursive:
        for root, _, files in os.walk(images_dir):
            for fn in files:
                ext = os.path.splitext(fn)[1].lower()
                if ext in VALID_EXTS:
                    yield os.path.join(root, fn)
    else:
        for fn in sorted(os.listdir(images_dir)):
            p = os.path.join(images_dir, fn)
            if os.path.isfile(p) and os.path.splitext(fn)[1].lower() in VALID_EXTS:
                yield p

def save_image_set(run_dir_img: str, bgr_q, gray_q, C_bgr, P_bgr, C_g, P_g):
    os.makedirs(run_dir_img, exist_ok=True)
    cv2.imwrite(os.path.join(run_dir_img, "plain_bgr_quick.png"), bgr_q)
    cv2.imwrite(os.path.join(run_dir_img, "cipher_bgr.png"), C_bgr)
    cv2.imwrite(os.path.join(run_dir_img, "plain_recovered_bgr.png"), P_bgr)
    cv2.imwrite(os.path.join(run_dir_img, "plain_gray_quick.png"), gray_q)
    cv2.imwrite(os.path.join(run_dir_img, "cipher_gray.png"), C_g)
    cv2.imwrite(os.path.join(run_dir_img, "plain_recovered_gray.png"), P_g)

def process_one(enc: LASMEncryptor, image_path: str, run_dir: str, key: str, nonce: str, max_pixels: int):
    stem = os.path.splitext(os.path.basename(image_path))[0]
    out_dir = os.path.join(run_dir, stem)
    os.makedirs(out_dir, exist_ok=True)

    bgr = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if bgr is None:
        raise RuntimeError(f"cv2 failed to read: {image_path}")
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    bgr_q = maybe_downscale(bgr, max_pixels=max_pixels)
    gray_q = maybe_downscale(gray, max_pixels=max_pixels)

    C_bgr, P_bgr, te_bgr, td_bgr = roundtrip(enc, bgr_q, key, nonce)
    C_g,   P_g,   te_g,   td_g   = roundtrip(enc, gray_q, key, nonce)

    # roundtrip asserts
    assert np.array_equal(P_bgr, bgr_q), f"BGR roundtrip failed for {image_path}"
    assert np.array_equal(P_g,   gray_q), f"GRAY roundtrip failed for {image_path}"

    # Determinism/sensitivity quick checks on gray
    C1 = enc.encrypt_image(gray_q, key, nonce)
    C2 = enc.encrypt_image(gray_q, key, nonce)
    assert np.array_equal(C1, C2), "Cipher not deterministic"
    assert not np.array_equal(C1, enc.encrypt_image(gray_q, key, nonce + "x")), "Nonce change ineffective"
    assert not np.array_equal(C1, enc.encrypt_image(gray_q, key + "x", nonce)), "Key change ineffective"

    # Quality metrics
    m_bgr  = analyze_encryption_quality(bgr_q, C_bgr, P_bgr)
    m_gray = analyze_encryption_quality(gray_q, C_g,   P_g)

    def _adj_line(m):
        o = m.get('adj_corr_original', {})
        e = m.get('adj_corr_encrypted', {})
        return (f"Adj corr (orig H/V/D): {fmt(o.get('H'))}/{fmt(o.get('V'))}/{fmt(o.get('D'))} | "
                f"(cipher H/V/D): {fmt(e.get('H'))}/{fmt(e.get('V'))}/{fmt(e.get('D'))}")

    print("  [BGR]  " + _adj_line(m_bgr))
    print("  [GRAY] " + _adj_line(m_gray))

    # Save images + histograms
    save_image_set(out_dir, bgr_q, gray_q, C_bgr, P_bgr, C_g, P_g)
    save_histogram(bgr_q, os.path.join(out_dir, "hist_bgr_plain.png"),     f"{stem} — BGR (plain→gray)")
    save_histogram(C_bgr, os.path.join(out_dir, "hist_bgr_cipher.png"),    f"{stem} — BGR cipher (gray)")
    save_histogram(P_bgr, os.path.join(out_dir, "hist_bgr_decrypted.png"), f"{stem} — BGR decrypted (gray)")
    save_histogram(gray_q, os.path.join(out_dir, "hist_gray_plain.png"),     f"{stem} — GRAY plain")
    save_histogram(C_g,    os.path.join(out_dir, "hist_gray_cipher.png"),    f"{stem} — GRAY cipher")
    save_histogram(P_g,    os.path.join(out_dir, "hist_gray_decrypted.png"), f"{stem} — GRAY decrypted")

    # Save per-image metrics
    with open(os.path.join(out_dir, "metrics_bgr.json"), "w", encoding="utf-8") as f:
        json.dump(sanitize_for_json(m_bgr), f, indent=2)
    with open(os.path.join(out_dir, "metrics_gray.json"), "w", encoding="utf-8") as f:
        json.dump(sanitize_for_json(m_gray), f, indent=2)

    with open(os.path.join(out_dir, "summary.txt"), "w", encoding="utf-8") as f:
        f.write(f"Image: {image_path}\n")
        f.write(f"Quick BGR shape: {list(bgr_q.shape)}; Quick GRAY shape: {list(gray_q.shape)}\n")
        f.write(f"BGR enc {te_bgr:.3f}s, dec {td_bgr:.3f}s | GRAY enc {te_g:.3f}s, dec {td_g:.3f}s\n")
        f.write(f"\n[BGR]\n Entropy orig/cipher/decr: {fmt(m_bgr.get('entropy_original'))}/"
                f"{fmt(m_bgr.get('entropy_encrypted'))}/{fmt(m_bgr.get('entropy_decrypted'))}"
                f"\n NPCR: {fmt(m_bgr.get('npcr'))}%  UACI: {fmt(m_bgr.get('uaci'))}%"
                f"\n HistSim: {fmt(m_bgr.get('histogram_similarity'))}  PSNR: {fmt(m_bgr.get('psnr'))} dB\n")
        f.write(f"\n[GRAY]\n Entropy orig/cipher/decr: {fmt(m_gray.get('entropy_original'))}/"
                f"{fmt(m_gray.get('entropy_encrypted'))}/{fmt(m_gray.get('entropy_decrypted'))}"
                f"\n NPCR: {fmt(m_gray.get('npcr'))}%  UACI: {fmt(m_gray.get('uaci'))}%"
                f"\n HistSim: {fmt(m_gray.get('histogram_similarity'))}  PSNR: {fmt(m_gray.get('psnr'))} dB\n")

        ob, eb = m_bgr.get('adj_corr_original', {}), m_bgr.get('adj_corr_encrypted', {})
        og, eg = m_gray.get('adj_corr_original', {}), m_gray.get('adj_corr_encrypted', {})
        db = m_bgr.get('adj_corr_decrypted', {}) or {}
        dg = m_gray.get('adj_corr_decrypted', {}) or {}

        f.write(f"  Adj corr BGR (orig H/V/D): {fmt(ob.get('H'))}/{fmt(ob.get('V'))}/{fmt(ob.get('D'))}\n")
        f.write(f"  Adj corr BGR (ciph H/V/D): {fmt(eb.get('H'))}/{fmt(eb.get('V'))}/{fmt(eb.get('D'))}\n")
        f.write(f"  Adj corr BGR (decr H/V/D): {fmt(db.get('H'))}/{fmt(db.get('V'))}/{fmt(db.get('D'))}\n")
        f.write(f"  Adj corr GRAY (orig H/V/D): {fmt(og.get('H'))}/{fmt(og.get('V'))}/{fmt(og.get('D'))}\n")
        f.write(f"  Adj corr GRAY (ciph H/V/D): {fmt(eg.get('H'))}/{fmt(eg.get('V'))}/{fmt(eg.get('D'))}\n")
        f.write(f"  Adj corr GRAY (decr H/V/D): {fmt(dg.get('H'))}/{fmt(dg.get('V'))}/{fmt(dg.get('D'))}\n")

    timings = {"bgr_encrypt_s": te_bgr, "bgr_decrypt_s": td_bgr, "gray_encrypt_s": te_g, "gray_decrypt_s": td_g}

    def flat_adj(prefix, m):
        o = m.get('adj_corr_original', {})
        e = m.get('adj_corr_encrypted', {})
        d = m.get('adj_corr_decrypted', {}) or {}
        return {
            f"{prefix}_adj_H_orig":   fmt(o.get('H')),
            f"{prefix}_adj_V_orig":   fmt(o.get('V')),
            f"{prefix}_adj_D_orig":   fmt(o.get('D')),
            f"{prefix}_adj_H_cipher": fmt(e.get('H')),
            f"{prefix}_adj_V_cipher": fmt(e.get('V')),
            f"{prefix}_adj_D_cipher": fmt(e.get('D')),
            f"{prefix}_adj_H_decr":   fmt(d.get('H')),
            f"{prefix}_adj_V_decr":   fmt(d.get('V')),
            f"{prefix}_adj_D_decr":   fmt(d.get('D')),
        }

    row = {
        "image": os.path.abspath(image_path),
        "quick_shape_bgr": "x".join(map(str, bgr_q.shape[:2])),
        "quick_shape_gray": "x".join(map(str, gray_q.shape[:2])),
        "entropy_orig_bgr": fmt(m_bgr.get("entropy_original")),
        "entropy_cipher_bgr": fmt(m_bgr.get("entropy_encrypted")),
        "entropy_decr_bgr": fmt(m_bgr.get("entropy_decrypted")),
        "npcr_bgr_%": fmt(m_bgr.get("npcr")),
        "uaci_bgr_%": fmt(m_bgr.get("uaci")),
        "histsim_bgr": fmt(m_bgr.get("histogram_similarity")),
        "psnr_bgr_db": fmt(m_bgr.get("psnr")),
        "entropy_orig_g": fmt(m_gray.get("entropy_original")),
        "entropy_cipher_g": fmt(m_gray.get("entropy_encrypted")),
        "entropy_decr_g": fmt(m_gray.get("entropy_decrypted")),
        "npcr_g_%": fmt(m_gray.get("npcr")),
        "uaci_g_%": fmt(m_gray.get("uaci")),
        "histsim_g": fmt(m_gray.get("histogram_similarity")),
        "psnr_g_db": fmt(m_gray.get("psnr")),
        **flat_adj("bgr", m_bgr),
        **flat_adj("gray", m_gray),
        **{k: fmt(v) for k, v in timings.items()}
    }
    return row, timings

def parse_args():
    p = argparse.ArgumentParser(description="Batch test LASM over all images in a folder; save results per image.")
    p.add_argument("--images-dir", default="test_images", help="Directory containing test images.")
    p.add_argument("--recursive", action="store_true", help="Recurse into subfolders.")
    p.add_argument("--key", default="super-secret-key")
    p.add_argument("--nonce", default="img-001")
    p.add_argument("--mem-window", type=int, default=128, help="LASM memory window.")
    p.add_argument("--max-pixels", type=int, default=256*256, help="Auto-downscale target pixels.")
    p.add_argument("--out-root", default=DEFAULT_OUT_ROOT, help="Root folder for test_results.")
    p.add_argument("--label", default=None, help="Optional label for the run folder.")
    return p.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.out_root, exist_ok=True)
    run_dir = make_run_dir(args.out_root, args.label, args.mem_window, args.max_pixels, args.images_dir)
    print(f"[demo] Run folder: {run_dir}")

    enc = LASMEncryptor(memory_window=args.mem_window)

    all_rows, all_timings, errors = [], {}, {}
    count = 0
    for img_path in iter_images(args.images_dir, args.recursive):
        count += 1
        print(f"\n[{count}] Processing {img_path}")
        try:
            row, timings = process_one(enc, img_path, run_dir, args.key, args.nonce, args.max_pixels)
            all_rows.append(row)
            all_timings[os.path.basename(img_path)] = timings
        except Exception as e:
            print(f"  !! ERROR on {img_path}: {e}")
            errors[os.path.basename(img_path)] = str(e)

    # Save aggregated CSV/JSON
    if all_rows:
        csv_path = os.path.join(run_dir, "summary.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
            w.writeheader()
            for r in all_rows:
                w.writerow(r)
        with open(os.path.join(run_dir, "summary.json"), "w", encoding="utf-8") as f:
            json.dump(sanitize_for_json(all_rows), f, indent=2)
    with open(os.path.join(run_dir, "timings.json"), "w", encoding="utf-8") as f:
        json.dump(sanitize_for_json(all_timings), f, indent=2)
    with open(os.path.join(run_dir, "params.json"), "w", encoding="utf-8") as f:
        json.dump({
            "images_dir": os.path.abspath(args.images_dir),
            "recursive": args.recursive,
            "memory_window": args.mem_window,
            "max_pixels": args.max_pixels,
            "key_len": len(args.key),
            "nonce": args.nonce
        }, f, indent=2)
    if errors:
        with open(os.path.join(run_dir, "errors.json"), "w", encoding="utf-8") as f:
            json.dump(errors, f, indent=2)

    print(f"\nDone. Processed {len(all_rows)} images, {len(errors)} errors.")
    print(f"Artifacts saved under: {run_dir}")

if __name__ == "__main__":
    main()
