"""Squint copies: 320 px wide, and the same with a 4 px gaussian blur at 1920 scale (as the Bloom 3D squint). python squint.py in.png out_prefix"""
import sys
from PIL import Image, ImageFilter
im = Image.open(sys.argv[1]).convert("RGB")
w = 320
h = round(im.size[1] * w / im.size[0])
im.resize((w, h), Image.LANCZOS).save(sys.argv[2] + "_320.png")
im.filter(ImageFilter.GaussianBlur(4 * im.size[0] / 1920.0)).resize((w, h), Image.LANCZOS).save(sys.argv[2] + "_320b.png")
