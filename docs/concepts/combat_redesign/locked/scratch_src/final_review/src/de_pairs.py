"""dE76 (CIE Lab D65) and L* for a few colour pairs the review cares about."""
import numpy as np

def srgb_to_lab(hexs):
    h = hexs.lstrip('#')
    rgb = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = M @ c
    wp = np.array([0.95047, 1.0, 1.08883])
    t = xyz / wp
    f = np.where(t > 216 / 24389, np.cbrt(t), (24389 / 27 * t + 16) / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])

def de(a, b):
    return float(np.linalg.norm(srgb_to_lab(a) - srgb_to_lab(b)))

PAIRS = [
    ('Meridian rust B0602C', '#B0602C', 'SCHEDULE FF8C1A', '#FF8C1A'),
    ('Meridian rust_hi D88A4E', '#D88A4E', 'SCHEDULE FF8C1A', '#FF8C1A'),
    ('Meridian rust_hi D88A4E', '#D88A4E', 'COLD D9877C', '#D9877C'),
    ('Meridian rust_hi D88A4E', '#D88A4E', 'BOSS_GOLD D69A1A', '#D69A1A'),
    ('Solace leaf 96FF46', '#96FF46', 'GAIN 7BE07B', '#7BE07B'),
    ('Solace leaf 96FF46', '#96FF46', 'FOCUS D4FF00', '#D4FF00'),
    ('Spin3 band FF00F0', '#FF00F0', 'CELL_PINK FF3DA8', '#FF3DA8'),
    ('WAVE plate B4AAFF', '#B4AAFF', 'TRACE purple 9A6BFF', '#9A6BFF'),
    ('TOWER plate 006E66', '#006E66', 'REPAIR ink 3FB59A', '#3FB59A'),
    ('P stock F6C8DE', '#F6C8DE', 'PAPER F2EEE4', '#F2EEE4'),
    ('P stock F6C8DE', '#F6C8DE', 'CELL_PINK FF3DA8', '#FF3DA8'),
    ('TURRET olive AEB24E', '#AEB24E', 'BOSS_GOLD D69A1A', '#D69A1A'),
    ('BURST F06EAE', '#F06EAE', 'CELL_PINK FF3DA8', '#FF3DA8'),
    ('SHIELD 5E9BE0', '#5E9BE0', 'SOAK 3A7EF3', '#3A7EF3'),
]

if __name__ == '__main__':
    for n1, h1, n2, h2 in PAIRS:
        print(f'{n1:26s} vs {n2:22s} dE76 {de(h1, h2):5.1f}   L* {srgb_to_lab(h1)[0]:5.1f} / {srgb_to_lab(h2)[0]:5.1f}')
