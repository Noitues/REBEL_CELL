"""The reviewer's measure.py, unchanged boxes, with the plate path as argv[1]."""
import sys
import numpy as np
from PIL import Image

path = sys.argv[1]
im = np.asarray(Image.open(path).convert('RGB')).astype(float) / 255


def lum(rgb):
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


L = lum(im)


def Lstar(y):
    return 116 * np.cbrt(y) - 16 if y > 0.008856 else 903.3 * y


def probe(name, x0, y0, x1, y1, pct=95):
    r = L[y0:y1, x0:x1]
    v = np.percentile(r, pct)
    print(f"{name:34s} L*p{pct}={Lstar(v):5.1f}  mean L*={Lstar(r.mean()):5.1f}")


print(path)
probe('schedule sweep (right rim)', 880, 300, 960, 700)
probe('+2 THIS TURN tape', 560, 120, 750, 180)
probe('HOT red chevrons s0 (top)', 500, 215, 560, 300)
probe('tower pink slice', 470, 380, 600, 470)
probe('tower yellow slice', 600, 560, 700, 660)
probe('enemy cell slate (ring NOW, s1)', 640, 200, 760, 260)
probe('empty ring +2 cell', 120, 600, 250, 700)
probe('unit token disc', 150, 480, 210, 540)
probe('room backdrop (right)', 1200, 450, 1800, 800)
probe('left city backdrop', 0, 200, 60, 900)
probe('HUD mono label text', 1180, 150, 1420, 172, 99)
probe('card paper (Brace)', 930, 1000, 1080, 1060)
probe('SEND IT sticker', 1670, 920, 1880, 1000)
probe('cold chevrons s4 (brown)', 200, 690, 260, 760)
print('image h', im.shape[0])
