"""Run the reviewer's measure.py probes (unchanged boxes and maths) on every final plate,
before (090ad870) and after (current published). sRGB -> relative luminance -> CIE L*."""
import sys, os, glob
import numpy as np
from PIL import Image

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final'
BEFORE = 'D:/rc_scratch/combat_redesign/locked/final_review/before'

def lum(rgb):
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]

def Lstar(y):
    return 116 * np.cbrt(y) - 16 if y > 0.008856 else 903.3 * y

PROBES = [
    ('schedule sweep (right rim)', 880, 300, 960, 700, 95),
    ('+2 THIS TURN tape', 560, 120, 750, 180, 95),
    ('HOT red chevrons s0 (top)', 500, 215, 560, 300, 95),
    ('tower pink slice', 470, 380, 600, 470, 95),
    ('tower yellow slice', 600, 560, 700, 660, 95),
    ('enemy cell slate (ring NOW, s1)', 640, 200, 760, 260, 95),
    ('empty ring +2 cell', 120, 600, 250, 700, 95),
    ('unit token disc', 150, 480, 210, 540, 95),
    ('room backdrop (right)', 1200, 450, 1800, 800, 95),
    ('left city backdrop', 0, 200, 60, 900, 95),
    ('HUD mono label text', 1180, 150, 1420, 172, 99),
    ('card paper (Brace)', 930, 1000, 1080, 1060, 95),
    ('SEND IT sticker', 1670, 920, 1880, 1000, 95),
    ('cold chevrons s4 (brown)', 200, 690, 260, 760, 95),
]

def run(path):
    im = np.asarray(Image.open(path).convert('RGB')).astype(float) / 255
    L = lum(im)
    out = {}
    for name, x0, y0, x1, y1, pct in PROBES:
        r = L[y0:y1, x0:x1]
        out[name] = (Lstar(np.percentile(r, pct)), Lstar(r.mean()), pct)
    # lowest non-background row in the hand region (card bottom)
    return out, im.shape

def main():
    plates = sorted(glob.glob(FINAL + '/p*.png'))
    rows = []
    for p in plates:
        b = os.path.join(BEFORE, 'final_' + os.path.basename(p))
        res, shp = run(p)
        resb = run(b)[0] if os.path.exists(b) else None
        print('==', os.path.basename(p), shp, '(before: %s)' % ('090ad870' if resb else 'none'))
        for name, *_ in PROBES:
            a = res[name]
            s = f"  {name:32s} after p{a[2]}={a[0]:5.1f} mean={a[1]:5.1f}"
            if resb:
                bb = resb[name]
                s += f"   | before p{bb[2]}={bb[0]:5.1f} mean={bb[1]:5.1f}"
            print(s)

if __name__ == '__main__':
    main()
