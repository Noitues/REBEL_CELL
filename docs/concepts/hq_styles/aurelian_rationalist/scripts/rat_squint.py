"""python rat_squint.py <out.png> <plate1> <plate2> ...  : 480 px wide thumbnails side by side (squint test)."""
import sys
from PIL import Image
sys.dont_write_bytecode = True
ims = [Image.open(p).convert("RGB").resize((480, 270), Image.LANCZOS) for p in sys.argv[2:]]
o = Image.new("RGB", (480 * len(ims), 270))
for i, im in enumerate(ims):
    o.paste(im, (480 * i, 0))
o.save(sys.argv[1])
