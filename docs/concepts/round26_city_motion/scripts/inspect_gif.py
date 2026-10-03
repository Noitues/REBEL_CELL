"""Decode a GIF and write a contact sheet of chosen frames (for review)."""
import sys
from PIL import Image
path, out = sys.argv[1], sys.argv[2]
idx = [int(v) for v in sys.argv[3].split(',')]
scale = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
im = Image.open(path)
print(path, im.size, im.n_frames)
fr = {}
for k in range(im.n_frames):
    im.seek(k)
    if k in idx:
        fr[k] = im.convert('RGB').copy()
w, h = int(im.size[0] * scale), int(im.size[1] * scale)
cols = 2
rows = (len(idx) + 1) // 2
sh = Image.new('RGB', (w * cols, h * rows))
for n, k in enumerate(idx):
    sh.paste(fr[k].resize((w, h), Image.LANCZOS), ((n % cols) * w, (n // cols) * h))
sh.save(out)
