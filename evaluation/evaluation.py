#!python3

import argparse
from pathlib import Path
import os
from skimage import io
from skimage import metrics
from skimage import color
from skimage.util import img_as_float
import numpy as np

from sewar.full_ref import vifp

parser = argparse.ArgumentParser(description='Generate screenshots for certification')
parser.add_argument("--rep", help="Path to the certification repository", default="..")
parser.add_argument("--dir", help="Path to folder with the generated screenshots")
args = parser.parse_args()

cert_path = Path(args.rep)
screenshots_dir = Path(args.dir)

dirnames = next(os.walk(cert_path / "models"))[1]
for dir in dirnames:
    filenames = next(os.walk(cert_path / "models" / dir))[2]
    for filename in filenames:
        if filename.startswith("rr-"):
            print("Compare: " + filename)
            im1 = img_as_float(io.imread(cert_path / "models" / dir / filename))
            screenshotsName = "c" + filename.lstrip('r')
            im2 = img_as_float(io.imread(screenshots_dir / screenshotsName))
            if im2.shape[2] == 3:
                im1 = color.rgba2rgb(im1)
            print("SSIM:  {:.5f}".format(metrics.structural_similarity(im1, im2, multichannel=True)))
            print("MSE:   {:.5f}".format(metrics.mean_squared_error(im1, im2)))
            print("NRMSE: {:.5f}".format(metrics.normalized_root_mse(im1, im2)))
            print("MAE:   {:.5f}".format(np.absolute(np.subtract(im1, im2)).mean()))
            print("PSNR:  {:.5f}".format(metrics.peak_signal_noise_ratio(im1, im2)))
            print("VIF:   {:.5f}".format(vifp(im1, im2)))


# ssim: this metric compares structural similarity between images (humans are better at perceiving structural differences than subtle pixel changes).
# it compares the images based on luminance Contast and structure.
# ssim provides much better results when applied to small patches of the image than on its entirety. Typically an 11x11 window is used.
# ssim provides scores from -1 (not similar) to 1 (same image).
# ssim provides high scores one of the images is blured or the color space is shifted
# further reading: https://medium.com/srm-mic/all-about-structural-similarity-index-ssim-theory-code-in-pytorch-6551b455541e
# https://en.wikipedia.org/wiki/Structural_similarity
# personally i'd say everything above 0.96 is "close enough".

# to my knowledge the best image comparison metric based on human judgement
# is based on neural networks and can be found in this paper https://arxiv.org/abs/1801.03924
# github: https://github.com/richzhang/PerceptualSimilarity
