"""Pack a final plate into the repo folder.
python rat_pack.py <tag>        v1: aurelian_rationalist.png + aurelian_rationalist_sbs.jpg (golden plate | rationalist)
python rat_pack.py <tag> v5     v5: aurelian_rationalist_v5.png + aurelian_v4_v5.jpg (v4 | v5)
python rat_pack.py <tag> v4     v4: aurelian_rationalist_v4.png + aurelian_v2_v3_v4.jpg (v3 is the 960 px preview v3g, upscaled)
python rat_pack.py <tag> v2     v2: aurelian_rationalist_v2.png + aurelian_rationalist_v1_v2.jpg (v1 | v2); v1 files are not touched"""
import os
import shutil
import sys

from PIL import Image

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, ".."))
GOLD = os.path.normpath(os.path.join(HERE, "..", "..", "..", "golden_plates", "hq_aurelian_overview.png"))
tag = sys.argv[1]
v2 = len(sys.argv) > 2 and sys.argv[2] == "v2"
v4 = len(sys.argv) > 2 and sys.argv[2] == "v4"
v5 = len(sys.argv) > 2 and sys.argv[2] == "v5"
src = os.path.join(r"D:/rc_scratch/hq_styles/aurelian_rationalist", tag, "plate.png")
b = Image.open(src).convert("RGB").resize((1280, 720), Image.LANCZOS)
if v5:
    shutil.copy(src, os.path.join(OUT, "aurelian_rationalist_v5.png"))
    a4 = Image.open(os.path.join(OUT, "aurelian_rationalist_v4.png")).convert("RGB").resize((1280, 720), Image.LANCZOS)
    im5 = Image.new("RGB", (2560, 720))
    im5.paste(a4, (0, 0))
    im5.paste(b, (1280, 0))
    im5.save(os.path.join(OUT, "aurelian_v4_v5.jpg"), quality=88)
    sys.exit(0)
if v4:
    shutil.copy(src, os.path.join(OUT, "aurelian_rationalist_v4.png"))
    t2 = Image.open(os.path.join(OUT, "aurelian_rationalist_v2.png")).convert("RGB").resize((960, 540), Image.LANCZOS)
    t3 = Image.open(r"D:/rc_scratch/hq_styles/aurelian_rationalist/v3g/plate.png").convert("RGB").resize((960, 540), Image.LANCZOS)
    t4 = b.resize((960, 540), Image.LANCZOS)
    im3 = Image.new("RGB", (2880, 540))
    for i, t in enumerate((t2, t3, t4)):
        im3.paste(t, (960 * i, 0))
    im3.save(os.path.join(OUT, "aurelian_v2_v3_v4.jpg"), quality=88)
    sys.exit(0)
if v2:
    shutil.copy(src, os.path.join(OUT, "aurelian_rationalist_v2.png"))
    a = Image.open(os.path.join(OUT, "aurelian_rationalist.png")).convert("RGB").resize((1280, 720), Image.LANCZOS)
    name = "aurelian_rationalist_v1_v2.jpg"
else:
    shutil.copy(src, os.path.join(OUT, "aurelian_rationalist.png"))
    a = Image.open(GOLD).convert("RGB").resize((1280, 720), Image.LANCZOS)
    name = "aurelian_rationalist_sbs.jpg"
im = Image.new("RGB", (2560, 720))
im.paste(a, (0, 0))
im.paste(b, (1280, 0))
im.save(os.path.join(OUT, name), quality=88)
