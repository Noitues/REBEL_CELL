"""Copy the final plate into the repo folder and build the side-by-side (golden plate | rationalist). python rat_pack.py <tag>"""
import os
import shutil
import sys

from PIL import Image

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, ".."))
GOLD = os.path.normpath(os.path.join(HERE, "..", "..", "..", "golden_plates", "hq_aurelian_overview.png"))
tag = sys.argv[1]
src = os.path.join(r"D:/rc_scratch/hq_styles/aurelian_rationalist", tag, "plate.png")
shutil.copy(src, os.path.join(OUT, "aurelian_rationalist.png"))
a = Image.open(GOLD).convert("RGB").resize((1280, 720), Image.LANCZOS)
b = Image.open(src).convert("RGB").resize((1280, 720), Image.LANCZOS)
im = Image.new("RGB", (2560, 720))
im.paste(a, (0, 0))
im.paste(b, (1280, 0))
im.save(os.path.join(OUT, "aurelian_rationalist_sbs.jpg"), quality=88)
