"""palette.py -- independent dE76 (CIE Lab, D65) of the documented palette (VISUAL_PLAN E + the 2026-11-04 additions, slice inks, card type
plates, the Spin 3 band, skin inks, light neutrals).  Prints every pair under 20 and the minimum per group, plus L* of each colour."""
import itertools
import numpy as np

hx = lambda s: np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], float)


def lab(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    X = (0.4124 * c[0] + 0.3576 * c[1] + 0.1805 * c[2]) / 0.95047
    Y = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    Z = (0.0193 * c[0] + 0.1192 * c[1] + 0.9505 * c[2]) / 1.08883
    f = lambda t: np.cbrt(t) if t > 0.008856 else 7.787 * t + 16 / 116
    return np.array([116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))])


G = {
    'token': {'CELL_PINK': 'FF3DA8', 'HARM': 'FF4433', 'GAIN': '7BE07B', 'SOAK': '3A7EF3', 'PLAN': 'FFE200', 'SCHEDULE': 'FF8C1A',
              'BOSS_GOLD': 'D69A1A', 'NET_CYAN': '5CE1FF', 'TRACE_VIOLET': 'A03CFF', 'CRT_AMBER': 'FFB000', 'RESIST_GOLD': 'FFD24D', 'FOCUS': 'D4FF00'},
    'neutral': {'PAPER': 'F2EEE4', 'ENAMEL': 'D9E1EA', 'TEXT_HI': 'F2F6FF', 'TEXT_MID': 'AFC0D6'},
    'mark': {'CREAM_HP': 'DBD1B7', 'K_TYPE': 'CBD2DB', 'HIT_PAPER': 'DED8CA', 'STEEL_HI_E': 'C4CBD8', 'HARM_UP(HOT)': 'FF6452', 'COLD_CHEV': 'D9877C', 'FAR_CHEV': '96767A'},
    'slice': {'BURST': 'F06EAE', 'SHIELD': '5E9BE0', 'TURRET': 'AEB24E', 'REPAIR': '3FB59A'},
    'card': {'TOWER': '006E66', 'WAVE': 'B4AAFF', 'SPIN3_BAND': 'FF00F0'},
    'skin': {'sol_leaf': '96FF46', 'sol_leaf_deep': '4FA83A', 'sol_celadon': 'B8DCCC', 'mer_rust': 'B0602C', 'mer_rust_hi': 'D88A4E'},
}
L = {}
for g, d in G.items():
    for k, v in d.items():
        L[(g, k)] = lab(hx(v))
print('L* per colour:', ', '.join('%s %.1f' % (k, v[0]) for (g, k), v in L.items()))
rows = []
for (a, la), (b, lb) in itertools.combinations(L.items(), 2):
    if a[0] == b[0] and a[0] in ('neutral', 'mark', 'skin', 'card'):
        continue
    if a[0] in ('neutral',) and b[0] in ('mark',) or a[0] == 'mark' and b[0] == 'neutral':
        continue
    rows.append((float(np.linalg.norm(la - lb)), a, b))
rows.sort()
print('\npairs under 20 dE76 (mark x neutral and same-group neutral / mark / skin / card pairs skipped):')
for d, a, b in rows:
    if d < 20:
        print('  %5.1f  %s:%s  vs  %s:%s' % (d, a[0], a[1], b[0], b[1]))
print('\nminimum per group pair:')
mins = {}
for d, a, b in rows:
    key = tuple(sorted((a[0], b[0])))
    if key not in mins:
        mins[key] = (d, a[1], b[1])
for k, v in sorted(mins.items()):
    print('  %-20s %5.1f  %s vs %s' % ('x'.join(k), *v))
