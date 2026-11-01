"""Usage: python px.py <image> x,y [x,y ...] : prints the RGB (0-255) at the points."""
import sys
from PIL import Image
sys.dont_write_bytecode = True
im = Image.open(sys.argv[1]).convert("RGB")
for a in sys.argv[2:]:
    x, y = [int(v) for v in a.split(",")]
    print(a, im.getpixel((x, y)))
