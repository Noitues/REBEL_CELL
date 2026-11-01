# Shared data + helpers for the bits FX options (960x540 working size). Run prep.py first.
import numpy as np, os, math
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
D = np.load(os.path.join(HERE, '..', 'work', 'layers.npz'))
P, BARE, FIT, MF, BGFULL, DISK = D['P'], D['bare'], D['fit'], D['M'], D['bgfull'], D['disk']
H, W = P.shape[:2]
CX, CY, RD, RCORE = 267.5, 267.5, 259.0, 88.0
yy, xx = np.mgrid[0:H, 0:W]
R = np.hypot(xx - CX, yy - CY)
TH = np.arctan2(yy - CY, xx - CX)

# colour tokens (BRIEF 3.3) as RGB
def hx(s): return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))
INK = hx('#0C0A16'); HARM = hx('#FF4433'); SCHED = hx('#FF8C1A'); CREAM = hx('#FFF4D6')
LANE1 = hx('#78AAFF'); CYAN = hx('#5CE1FF'); GAIN = hx('#7BE07B'); TRACE = hx('#A03CFF')

# ------------------------------------------------------------------ easing
def cl(x, a=0.0, b=1.0): return np.minimum(np.maximum(x, a), b)
def eic(x): x = cl(x); return x ** 3
def eoc(x): x = cl(x); return 1 - (1 - x) ** 3
def eio(x): x = cl(x); return np.where(x < .5, 4 * x ** 3, 1 - (-2 * x + 2) ** 3 / 2)
def smooth(x): x = cl(x); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t

def font(sz): return ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', int(sz))

# ------------------------------------------------------------------ compositing
def over(base, rgb, a):
    """base HxWx3 float, rgb HxWx3 float, a HxW float 0..1 -> new base."""
    return base + (rgb - base) * a[..., None]

def over_rgba(base, img):
    """img: PIL RGBA (same size) composited over float base."""
    a = np.asarray(img.getchannel('A')).astype(np.float32) / 255.0
    rgb = np.asarray(img.convert('RGB')).astype(np.float32)
    return over(base, rgb, a)

def shift(a, dx, dy):
    """integer translate with zero fill; works on HxW or HxWxC."""
    dx, dy = int(round(dx)), int(round(dy))
    out = np.zeros_like(a)
    ys0, ys1 = max(0, dy), min(H, H + dy); xs0, xs1 = max(0, dx), min(W, W + dx)
    out[ys0:ys1, xs0:xs1] = a[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    return out

def bg_at(w):
    """w=0 bare room, w=1 dimmed plate background."""
    return BARE + (BGFULL - BARE) * w

# ------------------------------------------------------------------ masks
CORE_A = cl((RCORE + 1.0 - R) / 2.0)                      # soft core disc
RING_A = cl((RD + 1.0 - R) / 2.0) * (1 - CORE_A)            # soft ring annulus (wheel minus hub)
WHEEL_A = cl((RD + 1.0 - R) / 2.0)
HUD_A = MF * (1 - WHEEL_A)
_rows = np.arange(H)[:, None]; _cols = np.arange(W)[None, :]
TOP_A = HUD_A * ((_rows < 205) & (_cols > 520))
BOT_A = HUD_A * ((_rows > 395) & (_cols > 490))
TAG_A = HUD_A * ((_cols < 130) & (_rows > 470))

def hud_in(base, t, t0=1.05, span=0.15):
    """T5: HUD slides in over the last 0.15 s (top, cards, tag, 20 ms stagger)."""
    for k, (A, dx, dy) in enumerate([(TOP_A, 0, -40), (BOT_A, 0, 60), (TAG_A, -40, 0)]):
        u = float(eoc((t - t0 - 0.02 * k) / (span - 0.04)))
        if u <= 0: continue
        a = shift(A, dx * (1 - u), dy * (1 - u)) * u
        rgb = shift(P, dx * (1 - u), dy * (1 - u))
        base = over(base, rgb, a)
    return base

def hud_out(base, t, span=0.2):
    """T6: UI fades in the first 0.2 s."""
    for k, (A, dx, dy) in enumerate([(TOP_A, 0, -24), (BOT_A, 0, 36), (TAG_A, -24, 0)]):
        u = float(eic((t - 0.02 * k) / span))
        if u >= 1: continue
        a = shift(A, dx * u, dy * u) * (1 - u)
        base = over(base, shift(P, dx * u, dy * u), a)
    return base

# core sprite (T5): hub flies in 1.35x -> 1.0 with a 4 % overshoot and a spin settle, 0.25..0.55 s
_core_img = Image.fromarray(np.dstack([P, CORE_A * 255]).astype(np.uint8), 'RGBA')
def core_state(t):
    u = float(cl((t - 0.25) / 0.30))
    s = 1 + 0.35 * (1 - float(eoc(u)))
    s -= 0.014 * math.sin(math.pi * float(cl((u - 0.55) / 0.45)))      # 4 % of the 0.35 travel
    rot = 7.0 * (1 - float(eoc(u)))
    a = float(cl(u * 2.2))
    return s, rot, a

def core_layer(base, t):
    s, rot, a = core_state(t)
    if t < 0.25: return base
    c = _core_img.crop((int(CX - 100), int(CY - 100), int(CX + 100), int(CY + 100)))
    n = int(200 * s)
    c = c.resize((n, n), Image.BICUBIC).rotate(rot, resample=Image.BICUBIC)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lay.paste(c, (int(round(CX - n / 2)), int(round(CY - n / 2))))
    arr = np.asarray(lay).astype(np.float32)
    return over(base, arr[..., :3], arr[..., 3] / 255 * a)

def dim_w(t):  # room dims 0.20..0.60 s in T5
    return float(smooth((t - 0.20) / 0.40))

# ------------------------------------------------------------------ cell grid (6 px cells over the wheel disc)
CS = 6
GH, GW = H // CS, W // CS
_gy, _gx = np.mgrid[0:GH, 0:GW]
_ccx = _gx * CS + CS / 2.0; _ccy = _gy * CS + CS / 2.0
_rc = np.hypot(_ccx - CX, _ccy - CY)
CELL_IN = _rc <= RD + 3
CID = (_gy * GW + _gx)                                  # id per cell
PIX_CELL = np.kron(CID, np.ones((CS, CS), int))          # id per pixel
CELL_IDX = np.flatnonzero(CELL_IN.ravel())
NC = len(CELL_IDX)
_sat = P.max(-1) - P.min(-1); _lum = P.mean(-1)
_sal = ((_sat > 75) | (_lum > 150)) & DISK
def _blk(a): return a.reshape(GH, CS, GW, CS).mean((1, 3))
_salfrac = _blk(_sal.astype(np.float32)).ravel()[CELL_IDX]
_wsum = np.stack([_blk(_sal * P[..., c]).ravel()[CELL_IDX] for c in range(3)], 1)
CELL_SAL = _salfrac > 0.16
_col = _wsum / np.maximum(_salfrac, 1e-3)[:, None]
_g = _col.max(1, keepdims=True)
CELL_COL = np.clip(_col * np.clip(215.0 / np.maximum(_g, 1), 1, 1.8), 0, 255)  # lift toward saturated
CELL_X = _ccx.ravel()[CELL_IDX]; CELL_Y = _ccy.ravel()[CELL_IDX]
CELL_R = _rc.ravel()[CELL_IDX]; CELL_TH = np.arctan2(CELL_Y - CY, CELL_X - CX)
CELL_CORE = CELL_R < RCORE
# map: cell id (grid) -> compact index
_compact = -np.ones(GH * GW, int); _compact[CELL_IDX] = np.arange(NC)
PIX_COMPACT = _compact[PIX_CELL]                          # -1 outside grid cells
RNG = np.random.RandomState(50)
CELL_RND = RNG.rand(NC); CELL_RND2 = RNG.rand(NC)

# sources: the lab floor of the bio cutaway (960 px space)
def sources(n, seed):
    r = np.random.RandomState(seed)
    sx = 745 + r.randn(n) * 55; sy = 285 + r.randn(n) * 30
    return np.clip(sx, 620, 880), np.clip(sy, 200, 370)
SRC_X, SRC_Y = sources(NC, 7)
SWIRL = (np.random.RandomState(9).rand(NC) * 0.9 + 0.4) * 110

def bezier(sx, sy, tx, ty, off, p):
    """quadratic bezier src->tgt; control point offset perpendicular to the chord. p scalar/array."""
    mx, my = (sx + tx) / 2, (sy + ty) / 2
    dx, dy = tx - sx, ty - sy
    L = np.maximum(np.hypot(dx, dy), 1)
    cx_ = mx - dy / L * off; cy_ = my + dx / L * off
    q = 1 - p
    return q * q * sx + 2 * q * p * cx_ + p * p * tx, q * q * sy + 2 * q * p * cy_ + p * p * ty

def pix_alpha_from_cells(ca):
    """per-cell alpha (NC,) -> per-pixel alpha map (zero outside grid cells)."""
    ext = np.concatenate([ca, [0.0]])
    return ext[PIX_COMPACT] * 1.0

# ------------------------------------------------------------------ stats
def luma(a): return float((a * np.array([.2126, .7152, .0722])).sum(-1).mean() / 255.0)

def to_pil(a): return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
