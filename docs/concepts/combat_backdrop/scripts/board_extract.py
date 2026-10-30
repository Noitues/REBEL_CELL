"""Extract an alpha for the E10 board (wheel, HUD, cards, stickers) from the flattened plate.

The plate has no separate board layer, so the mask is rebuilt: hand-placed rectangles for the opaque HUD
panels, stickers and cards; a disc for the wheel; and pixel tests (very dark, saturated, or hard edge)
for the thin outer rings and anything else the shapes miss. Output: scratch/board_rgba.png and a debug view.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

SRC = 'D:/rc_tmp/combat_critic/plates/waves_e10/p1_decide.png'
OUT = 'D:/rc_scratch/solace_concepts/'
im = Image.open(SRC).convert('RGB')
a = np.asarray(im).astype(np.float32) / 255
H, W = a.shape[:2]
v = a.max(2)
mn = a.min(2)
s = (v - mn) / (v + 1e-6)
lum = a @ np.array([0.299, 0.587, 0.114], np.float32)

# 1. pixel tests
gy, gx = np.gradient(ndi.gaussian_filter(lum, 0.8))
grad = np.hypot(gx, gy)
pix = (v < 0.14) | ((s > 0.62) & (v > 0.5)) | (grad > 0.075)
pix = ndi.binary_opening(pix, iterations=1)
pix = ndi.binary_closing(pix, iterations=2)

# 2. geometry
geo = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(geo)
cx, cy = 535, 545
d.ellipse([cx - 468, cy - 468, cx + 468, cy + 468], fill=255)           # opaque wheel body
for box in [(1060, 8, 1908, 378),                                     # HUD stack
            (1660, 970, 1904, 1078),                                  # SEND IT
            (1741, 922, 1889, 961),                                   # UNDO
            (24, 970, 332, 1064)]:                                    # name sticker
    d.rounded_rectangle(box, radius=14, fill=255)
d.polygon([(992, 852), (1130, 834), (1420, 832), (1604, 854), (1608, 1080), (990, 1080)], fill=255)  # cards
geo = np.asarray(geo) > 0

# 3. the thin outer rings: pixel test restricted to the wheel's outer annulus + glow margin
yy, xx = np.mgrid[0:H, 0:W]
r = np.hypot(xx - cx, yy - cy)
pix2 = (v < 0.14) | ((s > 0.62) & (v > 0.5))
ring = (r < 540) & pix2
m = geo | ring
m = ndi.binary_dilation(m, iterations=2)
m = ndi.binary_fill_holes(m)
alpha = ndi.gaussian_filter(m.astype(np.float32), 1.0)
alpha = np.clip((alpha - 0.2) / 0.6, 0, 1)

rgba = np.dstack([a, alpha])
Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA').save(OUT + 'board_rgba.png')
# debug: board over magenta
dbg = a * alpha[..., None] + np.array([1, 0, 1]) * (1 - alpha[..., None])
Image.fromarray((dbg * 255).astype(np.uint8)).save(OUT + 'board_debug.png')
print('coverage', float(alpha.mean()))
