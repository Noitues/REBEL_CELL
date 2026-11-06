"""region squint: 1/16 BOX + blur 1.0 of a p1 plate; room region = hull cells (not HUD column / hand), board region = r<=520 from (536,540), nameplate/sticker spots reported"""
import sys, numpy as np
sys.dont_write_bytecode = True
from PIL import Image, ImageFilter
def squint(img):
    s = img.resize((img.width // 16, img.height // 16), Image.BOX).filter(ImageFilter.GaussianBlur(1.0))
    a = np.asarray(s, np.float32) / 255.0
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
def regions():
    ys, xs = np.mgrid[0:67, 0:120]
    cx, cy = xs * 16 + 8, ys * 16 + 8
    hull = np.hypot((cx - 1500) / 330.0, (cy - 600) / 270.0) <= 1.0
    hud = (cx >= 1050) & (cy <= 400)
    hand = (cx >= 960) & (cy >= 830)
    room = hull & ~hud & ~hand
    board = np.hypot(cx - 536, cy - 540) <= 520
    return room, board
def stats(l, m):
    v = l[m]
    return dict(n=int(m.sum()), mean=round(float(v.mean()), 3), p95=round(float(np.percentile(v, 95)), 3), loud=round(float((v > 0.38).mean()), 3))
def measure(img):
    l = squint(img); room, board = regions()
    return dict(room=stats(l, room), board=stats(l, board), whole=dict(mean=round(float(l.mean()), 4), p95=round(float(np.percentile(l, 95)), 4), loud=round(float((l > 0.38).mean()), 4)), maxpos=[int(np.argmax(l) % 120 * 16 + 8), int(np.argmax(l) // 120 * 16 + 8)], max=round(float(l.max()), 3))
if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(p, measure(Image.open(p).convert('RGB')))
