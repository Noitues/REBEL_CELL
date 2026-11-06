"""Independent spot probes on a plate: per box, L* of the mean luminance, p50 and p95 L*.
Writes an overlay so the boxes can be checked by eye.
Usage: python probe_boxes.py <png> <overlay_out> name:x0,y0,x1,y1 ..."""
import sys
import numpy as np
from PIL import Image, ImageDraw

def lum(rgb):
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]

def Lstar(y):
    y = np.asarray(y, float)
    return np.where(y > 0.008856, 116 * np.cbrt(y) - 16, 903.3 * y)

def main():
    src, ov = sys.argv[1], sys.argv[2]
    img = Image.open(src).convert('RGB')
    L = lum(np.asarray(img).astype(float) / 255)
    d = ImageDraw.Draw(img)
    res = {}
    for spec in sys.argv[3:]:
        name, box = spec.split(':')
        x0, y0, x1, y1 = (int(v) for v in box.split(','))
        r = L[y0:y1, x0:x1]
        m, p50, p95 = float(Lstar(r.mean())), float(Lstar(np.percentile(r, 50))), float(Lstar(np.percentile(r, 95)))
        res[name] = (m, r.mean())
        print(f'{name:14s} box {box:20s} meanL* {m:5.1f}  p50 {p50:5.1f}  p95 {p95:5.1f}  Y {r.mean():.4f}')
        d.rectangle((x0, y0, x1, y1), outline=(0, 255, 255), width=2)
        d.text((x1 + 3, y0), name, fill=(0, 255, 255))
    img.save(ov)

if __name__ == '__main__':
    main()
