"""de_pair.py HEX HEX [HEX HEX ...] -- dE76 (CIE Lab D65) and L* for hex pairs."""
import sys
import numpy as np


def lab(h):
    rgb = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    X = (0.4124 * c[0] + 0.3576 * c[1] + 0.1805 * c[2]) / 0.95047
    Y = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    Z = (0.0193 * c[0] + 0.1192 * c[1] + 0.9505 * c[2]) / 1.08883
    f = lambda t: np.cbrt(t) if t > 0.008856 else 7.787 * t + 16 / 116
    return np.array([116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))])


a = sys.argv[1:]
for i in range(0, len(a), 2):
    la, lb = lab(a[i]), lab(a[i + 1])
    print('#%s (L* %.1f) vs #%s (L* %.1f): dE76 %.1f' % (a[i], la[0], a[i + 1], lb[0], float(np.linalg.norm(la - lb))))
