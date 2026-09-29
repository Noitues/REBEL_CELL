"""Heat glitch post for still 03 (Pillow): tear bands, block slips, scanline flicker,
a red edge pulse. Seeded. In Godot this is one screen-space shader driven by Heat,
off under Reduce Effects / the Options toggle.
python post_03_glitch.py <in.png> [out.png]"""
import sys, random
from PIL import Image, ImageChops, ImageDraw, ImageFilter

src = sys.argv[1]
dst = sys.argv[2] if len(sys.argv) > 2 else src
r = random.Random(82)
im = Image.open(src).convert("RGB")
W, H = im.size
out = im.copy()
# 1 tear bands: thin horizontal slices shifted sideways
for _ in range(5):
    y = r.randint(0, H - 40); h = r.choice([3, 5, 8, 14, 22]); dx = r.choice([-1, 1]) * r.randint(6, 38)
    band = im.crop((0, y, W, y + h))
    out.paste(band, (dx, y))
    if dx > 0:
        out.paste(im.crop((W - dx, y, W, y + h)), (0, y))
# 2 block slips with a channel split
for _ in range(3):
    x = r.randint(0, W - 300); y = r.randint(0, H - 60); w = r.randint(80, 300); h = r.randint(10, 40)
    blk = out.crop((x, y, x + w, y + h))
    rch, g, b = blk.split()
    rch = ImageChops.offset(rch, 8, 0); b = ImageChops.offset(b, -8, 0)
    out.paste(Image.merge("RGB", (rch, g, b)), (x + r.randint(-20, 20), y))
# 3 scanline flicker: a few rows brightened/dimmed
d = ImageDraw.Draw(out, "RGBA")
for _ in range(4):
    y = r.randint(0, H); h = r.randint(20, 70)
    d.rectangle((0, y, W, y + h), fill=(255, 60, 80, 14) if r.random() < 0.5 else (0, 0, 0, 40))
for y in range(0, H, 3):
    d.line((0, y, W, y), fill=(0, 0, 0, 22))
# 4 red pulse at the edges (Heat is HUNTED)
mask = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(mask)
md.rectangle((0, 0, W, H), fill=80)
md.rectangle((90, 70, W - 90, H - 70), fill=0)
mask = mask.filter(ImageFilter.GaussianBlur(70))
red = Image.new("RGB", (W, H), (255, 40, 60))
out = Image.composite(Image.blend(out, red, 0.25), out, mask)
out.save(dst)
print("glitched", dst)
