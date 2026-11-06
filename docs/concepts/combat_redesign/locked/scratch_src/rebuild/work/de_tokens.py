import numpy as np, itertools
T = {'CELL_PINK': 'FF3DA8', 'HARM': 'FF4433', 'GAIN': '7BE07B', 'SOAK': '3A7EF3', 'PLAN': 'FFE200', 'SCHEDULE': 'FF8C1A', 'BOSS_GOLD': 'FFC428',
     'NET_CYAN': '5CE1FF', 'TRACE_VIOLET': 'A03CFF', 'CRT_AMBER': 'FFB000', 'RESIST_GOLD': 'FFD24D', 'FOCUS': 'D4FF00',
     'COLD': 'D9877C', 'FAR': '96767A', 'HARM_UP': 'FF6452', 'SOLACE': '96FF46', 'SOLACE_V1': '3DFF8B', 'MERIDIAN': 'FF8C1A', 'TOWER': '2F5BFF', 'WAVE': 'FF8A1F', 'SPIN3': 'FFD21F'}


def lab(h):
    c = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = M @ c / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


for a, b in itertools.combinations(T, 2):
    d = np.linalg.norm(lab(T[a]) - lab(T[b]))
    if d < 25:
        print('%-12s %-12s %5.1f' % (a, b, d))
for k in T:
    print(k, np.round(lab(T[k]), 1))
