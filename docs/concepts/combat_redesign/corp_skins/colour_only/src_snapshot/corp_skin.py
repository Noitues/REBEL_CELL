"""corp_skin: colour-only corporate skins for the enemy layers of the combat board.
One palette table per corp (TOKENS[corp]); swapping corp = swapping the table.  Shapes, materials, patterns are untouched:
every enemy layer is re-coloured by (1) a luminance ramp for the neutral/cool enamel family (so HOT/COLD/FAR grades keep their order)
and (2) a hue move for the schedule-orange family.  Reds (HARM + hatch), pinks (ours), cyans, violets, boss gold are never touched."""
import numpy as np
from PIL import Image

CENTRE = (536, 540)
INNER_R = 198          # player tower plate / gutter stays untouched inside this radius


def H(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------------------------------------ the token tables
# roles: ink (deepest line/shadow), glass_lo / glass (cell wells, floor), mid (enamel body), hot (HOT enamel line / frame hairline),
#        disc (token disc / ticket paper), rim_lo/rim/rim_hi (outer rim), tape (schedule tape hue), primary/secondary (corp kit, ART_BIBLE 2.4)
TOKENS = {
    'solace': dict(
        name='Solace Biosystems', primary='#96FF46', secondary='#FF4696',
        ink='#050C08', glass_lo='#0B1E14', glass='#1E4A30', mid='#5E9A62', hot='#A8F070', disc='#F0FFE2',
        rim_lo='#0E2A1A', rim='#2C7046', rim_hi='#B8FF8A',
        tape='#96FF46',            # schedule orange family -> lime (hue move only)
        accent2='#F4B6CE',         # secondary, softened (blush porcelain): fine hairline on the rim only, never a stroke on cells, never saturated
        accent2_mix=0.55,
    ),
    'meridian': dict(
        name='Meridian Freight', primary='#FF8C1A', secondary='#FF2E28',
        ink='#08090A', glass_lo='#15181B', glass='#2F353A', mid='#7C858C', hot='#E8E2D2', disc='#F4F0E6',
        rim_lo='#3A1E12', rim='#9A5A1E', rim_hi='#FFA03A',
        tape='#FF8C1A',
        accent2='#B8402A',         # secondary, oxidised (container red-brown): never the bright #FF2E28, that is too close to HARM
        accent2_mix=0.50,
    ),
}


def ramp(t_, role):
    """luminance -> colour stops built from the table"""
    stops = [(0.00, 'ink'), (0.07, 'glass_lo'), (0.24, 'glass'), (0.52, 'mid'), (0.86, 'hot'), (1.00, 'disc')]
    if role == 'rim':
        stops = [(0.00, 'ink'), (0.10, 'rim_lo'), (0.34, 'rim'), (0.70, 'rim_hi'), (1.00, 'disc')]
    xs = [s[0] for s in stops]
    cols = np.array([H(t_[s[1]]) for s in stops], np.float32)
    return xs, cols


def _interp(lum, xs, cols):
    out = np.zeros(lum.shape + (3,), np.float32)
    for c in range(3):
        out[..., c] = np.interp(lum, xs, cols[:, c])
    return out


def _smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(-1); mn = rgb.min(-1); d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
    h = np.zeros_like(mx)
    dd = np.maximum(d, 1e-6)
    h = np.where(mx == r, ((g - b) / dd) % 6, h)
    h = np.where(mx == g, (b - r) / dd + 2, h)
    h = np.where(mx == b, (r - g) / dd + 4, h)
    return h * 60.0, s, mx


def _from_hsv(h, s, v):
    c = v * s
    hp = (h / 60.0) % 6
    x = c * (1 - np.abs(hp % 2 - 1))
    z = np.zeros_like(h)
    conds = [(hp >= 5, (c, z, x)), (hp < 5, (x, z, c)), (hp < 4, (z, x, c)), (hp < 3, (z, c, x)), (hp < 2, (x, c, z)), (hp < 1, (c, x, z))]
    r = np.zeros_like(h); g = np.zeros_like(h); b = np.zeros_like(h)
    for m, (rr, gg, bb) in conds:
        r = np.where(m, rr, r); g = np.where(m, gg, g); b = np.where(m, bb, b)
    m_ = v - c
    return np.stack([r + m_, g + m_, b + m_], -1)


def recolour(img, corp, role='cells', keep_inner=False):
    """img RGBA (non-premultiplied); returns the skinned RGBA.  role: cells | rim | floor | arcs | tickets."""
    t = TOKENS[corp]
    a = np.asarray(img.convert('RGBA'), np.float32)
    rgb = a[..., :3] / 255.0
    al = a[..., 3:4]
    h, s, v = _hsv(rgb)
    lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2])
    # --- family 1: neutral / cool enamel (low chroma, or cool hue band 140..275 with moderate chroma)
    cool = ((h > 135) & (h < 280)).astype(np.float32)
    w_cool = cool * (1 - _smooth(0.50, 0.80, s)) * _smooth(0.04, 0.12, s)
    w_neu = 1 - _smooth(0.10, 0.28, s)
    w = np.maximum(w_cool, w_neu)
    xs, cols = ramp(t, 'rim' if role == 'rim' else 'cells')
    # ramp is indexed by v (the visible brightness incl. saturated cool) so deep glass stays deep
    rc = _interp(np.clip(lum * 1.0 + 0.0, 0, 1), xs, cols) / 255.0
    out = rgb * (1 - w[..., None]) + rc * w[..., None]
    # --- family 2: schedule orange (hue 14..40, strong chroma) -> corp tape hue, value/chroma kept
    th, ts, tv = _hsv(np.array([[H(t['tape'])]], np.float32) / 255.0)
    w_or = ((h > 14) & (h < 40)).astype(np.float32) * _smooth(0.55, 0.75, s) * _smooth(0.35, 0.55, v)
    shifted = _from_hsv(np.full_like(h, th[0, 0]), np.minimum(1.0, s * (ts[0, 0] / 0.82) ** 0.0), v)
    if t['tape'].lower() != '#ff8c1a':
        out = out * (1 - w_or[..., None]) + shifted * w_or[..., None]
    # --- secondary: a fine hairline accent on the rim only (the brightest rim pixels)
    if role == 'rim':
        sec = np.array(H(t['accent2']), np.float32) / 255.0
        wh = _smooth(0.62, 0.9, lum) * t['accent2_mix'] * 0.0     # hook kept: rim_hi already carries the hairline; the secondary is used in tokens below
        out = out * (1 - wh[..., None]) + sec * wh[..., None]
    res = np.concatenate([np.clip(out, 0, 1) * 255.0, al], -1)
    if keep_inner:
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        rho = np.hypot(xx - CENTRE[0], yy - CENTRE[1])
        m = (rho >= INNER_R)[..., None].astype(np.float32)
        res = res * m + a * (1 - m)
    return Image.fromarray(np.clip(res + 0.5, 0, 255).astype(np.uint8), 'RGBA')


CORP = ['solace']


def layer(im, role='cells'):
    return recolour(im, CORP[0], role)


def plate(im):
    return recolour(im, CORP[0], 'floor', keep_inner=True)


def bezel(im):
    return recolour(im, CORP[0], 'rim')
