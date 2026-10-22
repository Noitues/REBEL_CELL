"""Squint test: a 320 px wide thumbnail of the v2 plate next to v1, saved on D:."""
import sys
from PIL import Image
sys.dont_write_bytecode = True
a = Image.open("D:/rc_art/art-pass/docs/concepts/hq_styles/aurelian_rationalist/aurelian_rationalist.png").convert("RGB").resize((480, 270), Image.LANCZOS)
b = Image.open("D:/rc_art/art-pass/docs/concepts/hq_styles/aurelian_rationalist/aurelian_rationalist_v2.png").convert("RGB").resize((480, 270), Image.LANCZOS)
im = Image.new("RGB", (960, 270))
im.paste(a, (0, 0)); im.paste(b, (480, 0))
im.save("D:/rc_scratch/hq_styles/aurelian_rationalist/squint.png")
