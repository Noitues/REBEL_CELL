"""Connected blobs of pixels at L* >= T inside the board circle (centre 535,545, r < R).
Usage: python bright_blobs.py <png> [T=96] [R=505]"""
import sys
import numpy as np
from PIL import Image

def lum(rgb):
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]

def main():
    p = sys.argv[1]
    T = float(sys.argv[2]) if len(sys.argv) > 2 else 96.0
    R = float(sys.argv[3]) if len(sys.argv) > 3 else 505.0
    im = np.asarray(Image.open(p).convert('RGB')).astype(float) / 255
    Y = lum(im)
    Ls = np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)
    h, w = Ls.shape
    yy, xx = np.mgrid[0:h, 0:w]
    inside = (xx - 535) ** 2 + (yy - 545) ** 2 < R * R
    m = (Ls >= T) & inside
    # simple flood fill labelling (4-connected)
    lab = np.zeros(m.shape, int)
    blobs = []
    nid = 0
    ys, xs = np.nonzero(m)
    for y0, x0 in zip(ys, xs):
        if lab[y0, x0]:
            continue
        nid += 1
        stack = [(y0, x0)]
        lab[y0, x0] = nid
        pts = []
        while stack:
            y, x = stack.pop()
            pts.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = nid
                    stack.append((ny, nx))
        a = np.array(pts)
        blobs.append((len(pts), a[:, 1].min(), a[:, 0].min(), a[:, 1].max(), a[:, 0].max(),
                      tuple(int(v) for v in (im[a[:, 0], a[:, 1]].mean(0) * 255))))
    blobs.sort(reverse=True)
    print(p, 'pixels >= L*', T, 'inside r', R, ':', int(m.sum()), 'blobs', len(blobs))
    for b in blobs[:25]:
        print('  n %4d  bbox %4d,%4d,%4d,%4d  mean rgb %s' % b)

if __name__ == '__main__':
    main()
