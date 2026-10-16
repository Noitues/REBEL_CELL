"""Crop the locked round 33 MAINFRAME red blade sign (mainframe_red_v4.png, read-only) into a texture for the city
build: D:/rc_scratch/city_all_corps/mainframe_blade.png (the vertical sign panel only)."""
import os
import sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import city_preset as CP
src = os.path.join(CP.CONCEPTS, "round33_mainframe_sign", "mainframe_red_v4.png")
im = Image.open(src).convert("RGB")
box = (int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (48, 28, 212, 686)
c = im.crop(box)
c.save(os.path.join(CP.SCR, "mainframe_blade.png"))
print(c.size)
