"""Round 39: quick review sheet of every bust render in scratch/busts -> scratch/sheet.png."""
import glob
import os

from PIL import Image

S = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch")
fs = sorted(glob.glob(os.path.join(S, "busts", "*.png")))
cols, w, h = 6, 300, 333
out = Image.new("RGBA", (w * cols, h * ((len(fs) + cols - 1) // cols)), (40, 40, 52, 255))
for i, f in enumerate(fs):
    out.alpha_composite(Image.open(f).resize((w, h)), ((i % cols) * w, (i // cols) * h))
out.save(os.path.join(S, "sheet.png"))
print(len(fs))
