#!python3

import argparse
from pathlib import Path
import os
import skimage.io
import skimage.metrics
import skimage.color
import skimage.util
import numpy as np
import itertools
from sewar.full_ref import vifp, uqi

def gather_image_pairs(ref_path: Path, cert_path: Path):
    reference_paths = sorted(list((ref_path / "models").glob("*/rr-*.png")))
    certification_candidate_paths = list(cert_path.glob("c-*.png"))
    return [ 
        (r, c) 
        for r, c in itertools.product(reference_paths, certification_candidate_paths) 
        if r.name.replace("rr-", "c-", 1) == c.name
    ]

def evaluate_metrics(reference, candidate):
    return {
        # Structural similarity index between two images
        # (humans are better at perceiving structural differences than subtle pixel changes).
        # it compares the images based on luminance Contast and structure.
        # ssim provides much better results when applied to small patches of the image than on its entirety. Typically an 11x11 window is used.
        # ssim provides scores from -1 (not similar) to 1 (same image).
        # ssim provides high scores one of the images is blured or the color space is shifted
        # further reading: https://medium.com/srm-mic/all-about-structural-similarity-index-ssim-theory-code-in-pytorch-6551b455541e
        # https://en.wikipedia.org/wiki/Structural_similarity
        "ssim": skimage.metrics.structural_similarity(reference, candidate, multichannel=True),
        # Mean Squared Error (MSE) is one of the most commonly used image quality measures, but receives strong criticism as
        # it doesn't reflect the way the human visual systems perceive images very well. An image pair with
        # high MSE might still look very similar to a human.
        "mse": skimage.metrics.mean_squared_error(reference, candidate),
        # Peak Signal to Noise Ratio (PSNR) is based on MSE and brought to a logarithmic scale in the decibel unit
        "psnr": skimage.metrics.peak_signal_noise_ratio(reference, candidate),
        # Normalized Root MSE (NRMSE)
        "nrmse": skimage.metrics.normalized_root_mse(reference, candidate),
        # Mean Absolute Error (MAE)
        "mae": np.absolute(np.subtract(reference, candidate)).mean(),
        # Visual Information Fidelity Measure (VIF)
        # https://ieeexplore.ieee.org/abstract/document/1576816/
        # The higher the better. The reference image would yield a value of 1.0, values above 1.0
        # typically stem from higher contrast images, which are considerered better quality in this metric
        "vif": vifp(reference, candidate),
        # Universal Quality Index (UQI)
        "uqi": uqi(reference, candidate),
    }
    
def evaluate_passed(metrics):
    # TODO: the values here are just suggestions, we have to evaluate which values
    # are strict enough to ensure visual similarity but not be too strict at the same time
    return {
        # Choose a relaxed value for SSIM
        "ssim": metrics["ssim"] > 0.95,
        # PSNR for image compression in 8bit is typically in the range [30, 50]
        "psnr": metrics["psnr"] > 35.0,
    }

def print_report(metrics_report):
    print(metrics_report['name'])

    for name, value in metrics_report["metrics"].items():
        passed = ''
        if name in metrics_report['passed']:
            passed = f"[{'Passed' if metrics_report['passed'][name] else 'Failed'}]"
        print(f"{name: <8} {value :<12.6f} {passed}")

    print("")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate screenshots for certification')
    parser.add_argument("--rep", help="Path to the certification repository", default="..")
    parser.add_argument("--dir", help="Path to folder with the generated screenshots")
    args = parser.parse_args()

    cert_path = Path(args.rep)
    screenshots_dir = Path(args.dir)
    
    image_pairs = gather_image_pairs(cert_path, screenshots_dir)
    for reference_path, candidate_path in image_pairs:
        
        im1 = skimage.util.img_as_float(skimage.io.imread(reference_path))
        im2 = skimage.util.img_as_float(skimage.io.imread(candidate_path))
        if im2.shape[2] == 3:
            im1 = skimage.color.rgba2rgb(im1)

        name = reference_path.name.replace("rr-", "", 1).replace(".png", "")
        metrics = evaluate_metrics(im1, im2)
        passed = evaluate_passed(metrics)

        report = {
            "name": name,
            "metrics": metrics,
            "passed": passed
        }
        
        print_report(report)
