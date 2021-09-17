#!python3

import argparse
from pathlib import Path
import os
import skimage.io
import skimage.metrics
import skimage.color
import skimage.util
import skimage.transform
import skimage.filters
import numpy as np
import itertools
from sewar.full_ref import vifp, uqi
import report

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
        # further reading:
        # https://en.wikipedia.org/wiki/Structural_similarity
        "ssim": skimage.metrics.structural_similarity(reference, candidate, multichannel=True),
        
        # Mean Squared Error (MSE) is one of the most commonly used image quality measures, but receives strong criticism as
        # it doesn't reflect the way the human visual systems perceive images very well. An image pair with
        # high MSE might still look very similar to a human.
        # "mse": skimage.metrics.mean_squared_error(reference, candidate),
        # Peak Signal to Noise Ratio (PSNR) is based on MSE and brought to a logarithmic scale in the decibel unit
        "psnr": skimage.metrics.peak_signal_noise_ratio(reference, candidate),
        
        # Normalized Root MSE (NRMSE)
        # "nrmse": skimage.metrics.normalized_root_mse(reference, candidate),
        
        # Mean Absolute Error (MAE)
        # "mae": np.absolute(np.subtract(reference, candidate)).mean(),
        
        # Visual Information Fidelity Measure (VIF)
        # https://ieeexplore.ieee.org/abstract/document/1576816/
        # The higher the better. The reference image would yield a value of 1.0, values above 1.0
        # typically stem from higher contrast images, which are considerered better quality in this metric
        # "vif": vifp(reference, candidate),
        
        # Universal Quality Index (UQI)
        # "uqi": uqi(reference, candidate),
    }
    
def evaluate_passed(metrics):
    # TODO: the values here are just suggestions, we have to evaluate which values
    # are strict enough to ensure visual similarity, while allowing subtle differences
    return {
        # Choose a relaxed value for SSIM
        "ssim": metrics["ssim"] > 0.85,
        # PSNR for image compression in 8bit is typically in the range [30, 50]
        "psnr": metrics["psnr"] > 20.0, 
    }

def print_report(name, metrics_report):
    print(name)

    for name, value in metrics_report["metrics"].items():
        passed = ''
        if name in metrics_report['passed']:
            passed = f"[{'Passed' if metrics_report['passed'][name] else 'Failed'}]"
        print(f"{name: <8} {value :<12.6f} {passed}")

    print("")

def compare_images(reference, candidate):
    diff = skimage.util.compare_images(reference, candidate, method='diff')
    threshold = diff > 0.05

    return {
        "reference": reference,
        "candidate": candidate,
        "diff": skimage.util.img_as_ubyte(diff),
        "threshold": skimage.util.img_as_ubyte(threshold)
    }

def evaluate(reference, candidate):
    metrics = evaluate_metrics(reference, candidate)

    return {
        "metrics": metrics,
        "passed": evaluate_passed(metrics),
        "images": compare_images(reference, candidate),
    }

def normalize_images(reference, candidate):
    # Ensure images match in channel count
    if reference.shape[2] == 4:
        reference = skimage.color.rgba2rgb(reference)
        reference = skimage.util.img_as_ubyte(reference)
    if candidate.shape[2] == 4:
        candidate = skimage.color.rgba2rgb(candidate)
        candidate = skimage.util.img_as_ubyte(candidate)
    # Ensure images match in resolution
    if candidate.shape != reference.shape:
        print(f"\n  Resizing {candidate_path} from {candidate.shape[:2]} to {reference.shape[:2]}")
        candidate = skimage.transform.resize(candidate, (reference.shape[0], reference.shape[1]),
                    anti_aliasing=False)
        candidate = skimage.util.img_as_ubyte(candidate)
        print()
    return reference, candidate

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate screenshots for certification')
    parser.add_argument("--rep", "-r", help="Path to the certification repository (defaults to \"..\")", default="..")
    parser.add_argument("--name", "-n", help="Name of the certification submission", default="")
    parser.add_argument("--output", "-o", help="Output directory for results")
    parser.add_argument("dir", help="Path to the test results package (the candidate submission)")
    args = parser.parse_args()

    cert_path = Path(args.rep)
    screenshots_dir = Path(args.dir)
    output_path = None
    if args.output:
        output_path = Path(args.output)
        os.makedirs(output_path, exist_ok=True)
        os.makedirs(output_path / "reference", exist_ok=True)
        os.makedirs(output_path / "candidate", exist_ok=True)
        os.makedirs(output_path / "diffs", exist_ok=True)
        os.makedirs(output_path / "thresholds", exist_ok=True)
    # scan the filesystem for test case images
    image_pairs = gather_image_pairs(cert_path, screenshots_dir)

    if not image_pairs:
        print(f"Didn't find matching image pairs for paths '{cert_path}' and '{screenshots_dir}'")

    results = {}
    for reference_path, candidate_path in image_pairs:
        reference_image = skimage.io.imread(reference_path)
        candidate_image = skimage.util.img_as_ubyte(skimage.io.imread(candidate_path))
        reference_image, candidate_image = normalize_images(reference_image, candidate_image)
        # Extract the test case name from the reference file
        name = reference_path.name.replace("rr-", "", 1).replace(".png", "")
        # Compute metrics and compare images
        results[name] = evaluate(reference_image, candidate_image)
        # CLI output
        print_report(name, results[name])

        # write images to the output directory
        if output_path:
            # add image paths to results
            results[name]["image_paths"] = {}
            results[name]["image_paths"]["candidate"] = candidate_path
            results[name]["image_paths"]["reference"] = reference_path

            # save the input images to the output directory
            reference_image_path = Path("reference") / f"rr-{name}.png"
            skimage.io.imsave(output_path / reference_image_path, results[name]["images"]["reference"])
            results[name]["image_paths"]["reference"] = reference_image_path
            
            candidate_image_path = Path("candidate") / f"c-{name}.png"
            skimage.io.imsave(output_path / candidate_image_path, results[name]["images"]["candidate"])
            results[name]["image_paths"]["candidate"] = candidate_image_path

            # save the diff image
            diff_image_path = Path("diffs") / f"d-{name}.png"
            skimage.io.imsave(output_path / diff_image_path, results[name]["images"]["diff"], check_contrast=False)
            results[name]["image_paths"]["diff"] = diff_image_path

            # save the threshold image
            thresholds_image_path = Path("thresholds") / f"t-{name}.png"
            skimage.io.imsave(output_path / thresholds_image_path, results[name]["images"]["threshold"], check_contrast=False)
            results[name]["image_paths"]["threshold"] = thresholds_image_path
    # generate a PDF containing all results
    if output_path:
        report.generate_report_document(results, output_path, args.name)
        report.generate_report_json(results, output_path)
