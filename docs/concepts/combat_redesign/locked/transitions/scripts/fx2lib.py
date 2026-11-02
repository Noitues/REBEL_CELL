"""fx2lib: shared data + helpers for the recoloured bits FX option A on the final locked board (960x540 working size).
Layers come from staged.py (layers/<corp>_p1.npz, 1920x1080 RGBA), downsampled here once and cached."""
import numpy as np, os, math, json
from PIL import Image, ImageDraw, ImageFont

HERE = 'D:/rc_scratch/combat_redesign/locked/transitions_work/'
CORP = os.environ.get('CORP', 'neutral')
W, H = 960, 540
BARE_PATH = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_bio_bare.png'


def _load():
    cache = HERE + 'layers/%s_p1_960.npz' % CORP
    if os.path.exists(cache):
        return dict(np.load(cache)), json.load(open(HERE + 'layers/%s_p1.json' % CORP))
    Z = np.load(HERE + 'layers/%s_p1.npz' % CORP)
    out = {}
    for k in Z.files:
        im = Image.fromarray(Z[k])
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        if im.size != (1920, 1080):          # a layer smaller than the screen (the guns) was composited at the origin
            pad = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); pad.paste(im, (0, 0)); im = pad
        # premultiplied downsample so transparent edges do not darken
        a = np.asarray(im).astype(np.float32) / 255.0
        pm = np.dstack([a[..., :3] * a[..., 3:4], a[..., 3:4]])
        ch = [np.asarray(Image.fromarray(pm[..., c]).resize((W, H), Image.BOX)) for c in range(4)]
        pm2 = np.dstack(ch)
        al = pm2[..., 3:4]
        rgb = np.where(al > 1e-4, pm2[..., :3] / np.maximum(al, 1e-4), 0)
        out[k] = np.dstack([rgb * 255, al * 255]).astype(np.float32)
    out['bare'] = np.asarray(Image.open(BARE_PATH).convert('RGB').resize((W, H), Image.LANCZOS)).astype(np.float32)
    np.savez_compressed(cache, **out)
    return out, json.load(open(HERE + 'layers/%s_p1.json' % CORP))


LY, META = _load()
NCARD = len(META['cards'])
BGD = LY['bg'][..., :3]                    # the plate's room (graded, dimmed)
BARE = LY['bare']
CX, CY = META['C'][0] / 2.0, META['C'][1] / 2.0
yy, xx = np.mgrid[0:H, 0:W]
R = np.hypot(xx - CX, yy - CY)
TH = np.arctan2(yy - CY, xx - CX)


def hx(s): return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


INK = hx('#0C0A16')
PINK = hx('#FF3DA8')                        # player pink (CELL_PINK, the halo, SEND IT)
SPOT = dict(BURST=hx('#FF3DA8'), SHIELD=hx('#2A58F0'), TURRET=hx('#FFD21F'), REPAIR=hx('#4BD67E'))
COBALT = hx('#2F5BFF'); ORANGE = hx('#FF8A1F'); VIOLET = hx('#A03CFF')     # WPAP card types TOWER / WAVE, Trace tab
SILVER = (232, 238, 244); SILVER_LO = (118, 128, 142)                         # lw_skin.NeutralTape (THIS TURN tape, every corp)
CORP_INK = {
    # ring 0, ring 1, ring 2 glyph + keyline colours, then the 1-in-5 accent, all from the skin palette (lw_skin / cs_skin)
    'neutral': dict(rings=[(217, 225, 234), (166, 180, 198), (128, 144, 166)], acc=(188, 200, 214)),
    'solace': dict(rings=[(150, 255, 70), (96, 210, 110), (64, 178, 132)], acc=(226, 238, 216)),
}[CORP]

# radii at 960 px (locked board NOTES: tower 196, ring 0 214-271, ring 1 271-328, ring 2 328-385, band 391-417, lanes 436-470, rim 489-500)
R_TOWER, R0, R1, R2, R3, RD = 98.0, 135.5, 164.0, 192.5, 252.0, 252.0


# ------------------------------------------------------------------ easing
def cl(x, a=0.0, b=1.0): return np.minimum(np.maximum(x, a), b)
def eic(x): x = cl(x); return x ** 3
def eoc(x): x = cl(x); return 1 - (1 - x) ** 3
def eio(x): x = cl(x); return np.where(x < .5, 4 * x ** 3, 1 - (-2 * x + 2) ** 3 / 2)
def smooth(x): x = cl(x); return x * x * (3 - 2 * x)


_FC = {}
def font(sz):
    sz = int(sz)
    if sz not in _FC:
        _FC[sz] = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', sz)
    return _FC[sz]


# ------------------------------------------------------------------ compositing (float RGB base, float RGBA layers 0..255)
def over(base, rgb, a):
    return base + (rgb - base) * a[..., None]


def lay(base, L, k=1.0):
    """composite an RGBA float layer with an extra alpha factor k (scalar or HxW)"""
    return over(base, L[..., :3], L[..., 3] / 255.0 * k)


def over_rgba(base, img):
    a = np.asarray(img.getchannel('A')).astype(np.float32) / 255.0
    rgb = np.asarray(img.convert('RGB')).astype(np.float32)
    return over(base, rgb, a)


def shift(a, dx, dy):
    dx, dy = int(round(dx)), int(round(dy))
    out = np.zeros_like(a)
    ys0, ys1 = max(0, dy), min(H, H + dy); xs0, xs1 = max(0, dx), min(W, W + dx)
    out[ys0:ys1, xs0:xs1] = a[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    return out


def full_plate():
    b = BGD.copy()
    for k in ['scrim', 'base', 'tower', 'enemy1', 'guns', 'enemy2', 'hud', 'you'] + ['card%d' % i for i in range(NCARD)] + ['name', 'send']:
        b = lay(b, LY[k])
    return b


PLATE_LAYERS = full_plate()
PUB = {'neutral': 'p1_decide.png', 'solace': 'p1_decide_solace.png'}[CORP]
# the end key is the published final plate itself (box-downsampled), so T5's last frame / T6's first frame are the real plate
PLATE = np.asarray(Image.open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/' + PUB).convert('RGB').resize((W, H), Image.BOX)).astype(np.float32)


def bg_at(w):
    return BARE + (BGD - BARE) * w


def dim_w(t):
    return float(smooth((t - 0.20) / 0.40))


# ------------------------------------------------------------------ HUD groups: (layers, dx, dy) at full offset
HUD_GROUPS = [(['scrim', 'hud', 'you'], 0, -40), (['name'], -40, 0)]
SEND_GROUP = (['send'], 0, 50)


def card_colour(i):
    import sys
    name = META['hand'][i] if i < len(META['hand']) else None
    fam = CARD_FAM.get(name, 'TOWER')
    return COBALT if fam == 'TOWER' else ORANGE


CARD_FAM = {'Nudge': 'TOWER', 'Spin2': 'TOWER', 'Spin3': 'TOWER', 'Brace': 'TOWER', 'Strike': 'TOWER', 'Firewall': 'TOWER',
            'Trigger': 'WAVE', 'Twist': 'WAVE', 'Pull': 'WAVE', 'Shove': 'WAVE', 'Hold': 'WAVE'}
CARD_TRACE = {'Trigger'}


def card_box(i):
    c = META['cards'][i]
    return c['cx'] / 2.0, c['cy'] / 2.0, c['ang']


def luma(a): return float((a * np.array([.2126, .7152, .0722])).sum(-1).mean() / 255.0)
def to_pil(a): return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def bezier(sx, sy, tx, ty, off, p):
    mx, my = (sx + tx) / 2, (sy + ty) / 2
    dx, dy = tx - sx, ty - sy
    L = np.maximum(np.hypot(dx, dy), 1)
    cx_ = mx - dy / L * off; cy_ = my + dx / L * off
    q = 1 - p
    return q * q * sx + 2 * q * p * cx_ + p * p * tx, q * q * sy + 2 * q * p * cy_ + p * p * ty


# glyph sources: three spots in the lab half of the bio cutaway, one per ring (staggered so the rings start from different parts of the building)
SRC_CENTRES = [(720, 300), (800, 360), (650, 380), (760, 250)]


def sources(n, seed, which):
    r = np.random.RandomState(seed)
    cx, cy = SRC_CENTRES[which]
    sx = cx + r.randn(n) * 40; sy = cy + r.randn(n) * 24
    return np.clip(sx, 560, 920), np.clip(sy, 190, 470)
