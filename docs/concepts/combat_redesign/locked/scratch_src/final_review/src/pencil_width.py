"""Run lengths of PLAN-yellow (#FFE200, dE76 < 35) pixels along given vertical or horizontal
scan lines of a plate. Usage: python pencil_width.py <png> v:x:y0:y1 h:y:x0:x1 ..."""
import sys
import numpy as np
from PIL import Image

def lab(rgb):
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)

def runs(mask):
    out, n = [], 0
    for v in mask:
        if v:
            n += 1
        elif n:
            out.append(n); n = 0
    if n:
        out.append(n)
    return out

def main():
    im = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float) / 255
    L = lab(im)
    ref = lab(np.array([[0xFF, 0xE2, 0x00]], float) / 255)[0]
    yel = np.linalg.norm(L - ref, axis=-1) < 35
    dark = L[..., 0] < 20
    for spec in sys.argv[2:]:
        k, a, b0, b1 = spec.split(':')
        a, b0, b1 = int(a), int(b0), int(b1)
        if k == 'v':
            m, d = yel[b0:b1, a], dark[b0:b1, a]
        else:
            m, d = yel[a, b0:b1], dark[a, b0:b1]
        print(spec, 'yellow runs', runs(m), ' dark(L*<20) runs', runs(d)[:12])

if __name__ == '__main__':
    main()
