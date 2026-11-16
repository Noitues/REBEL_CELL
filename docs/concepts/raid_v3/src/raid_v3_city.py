"""raid_v3_city: the RAID screen in Deface v3, on the 3D city (set 2).  Designer rulings 2026-11-15 applied.

    python raid_v3_city.py [plan place shop playback site aftermath sheet]      (default: all)

Backplate: the clean Solace night city render (tide_concepts/p2_base/city_default.png, 1920x1080, native, darkened and
desaturated under the glass).  Its camera is orthographic, so world -> screen is affine; city_geo fits it from the per-pixel
world positions and gives the ground height and per-pixel ground visibility.  The raid district is the low-rise street block
south-west of the Solace HQ ring (set 2 put it on the park plaza; the designer moved it): a 10 x 10 cell grid on the city's own
6 BU lot lattice (edges at 3 mod 6 BU in world x and z), drawn faintly on the ground (hidden under towers at a ghost alpha).
Rulings: units = bible 4.8 threat icon v4 (shape = type, fill = corp colour = health, dashed status ring with pips, stack
badge); INCOMING = the intercepted work order (memo under glass); CREW = option B (full roster, pencil cell + tick); operatives
on the city = R3 class beacons (2D stand-in); drag = Takeover's (spring lag, liner left in CREW, yellow arrow + circle); site
core 8 and the v39 EVACUATE text.
Toolkit: raid_kit (stickers, pencil, HUD), raid_v3 (report paper), crew_options (unchanged), city_geo (new).  Everything is drawn
on a transparent supersampled overlay, which is downsampled and composited on the native-resolution city.
"""
import json, math, os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import raid_kit as K
import raid_v3 as R
import city_geo as CG
from raid_kit import (Wax, PEN_Y, PEN_R, SL, IR, TR, S, text, Layer, comp, INK, PAPER, HARM, CYAN, TEXT_HI, TEXT_MID, ANTON, MONO,
                      W, H, SS, F_all, glass, stick, S_GAIN, S_HARM, S_HI, S_PLAN, S_MID, TEAL, TEAL_D, TEAL_HI)

OUT = 'D:/rc_art/art-pass/docs/concepts/raid_v3/'
DOT = ('\u00b7', S_MID)
CITY = None


def city():
    global CITY
    if CITY is None:
        CITY = CG.City()
    return CITY


def blank():
    return Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))


# =============================================================================================== the district grid (world space)
class CityGrid:
    """cells on the city's 6 BU lot lattice; (i, j) = (world x, world z) steps; i grows down-right on screen, j down-left"""

    def __init__(self, X0, Z0, nc, nr):
        self.X0, self.Z0, self.nc, self.nr = X0, Z0, nc, nr
        C = city()
        hs = [C.ground_h(X0 + 6 * i + 3, Z0 + 6 * j + 3) for i in range(nc) for j in range(nr)]
        self.h = float(np.median(hs))                         # one ground height for the district (the street level)
        self._clear = None

    def world(self, i, j):
        return self.X0 + 6.0 * i, self.Z0 + 6.0 * j

    def sp1080(self, i, j, lift=0.0):
        """the point on city_default.png (the camera the world positions were captured at)"""
        x, z = self.world(i, j)
        sx, sy = city().proj(x, self.h + lift, z)
        return float(sx), float(sy)

    def sp(self, i, j, lift=0.0):
        """the point on the raid screen (the raid camera: VIEW_ZOOM closer, window at VIEW_O)"""
        return view(*self.sp1080(i, j, lift))

    def quad1080(self, c, r):
        return [self.sp1080(c, r), self.sp1080(c + 1, r), self.sp1080(c + 1, r + 1), self.sp1080(c, r + 1)]

    def cc(self, c, r, lift=0.0):
        return self.sp(c + 0.5, r + 0.5, lift)

    def quad(self, c, r, inset=0.0):
        return [self.sp(c + inset, r + inset), self.sp(c + 1 - inset, r + inset), self.sp(c + 1 - inset, r + 1 - inset),
                self.sp(c + inset, r + 1 - inset)]

    def name(self, c, r):
        return 'abcdefghijklmnop'[c] + str(r + 1)

    def clear(self):
        """per cell: the fraction of its screen footprint that shows open ground at this cell (not under a tree or a tower)"""
        if self._clear is None:
            C = city()
            out = np.zeros((self.nc, self.nr))
            for i in range(self.nc):
                for j in range(self.nr):
                    q = self.quad1080(i, j)
                    xs, ys = [p[0] for p in q], [p[1] for p in q]
                    bx0, by0 = max(0, int(min(xs))), max(0, int(min(ys)))
                    bx1, by1 = min(C.W, int(max(xs)) + 1), min(C.H, int(max(ys)) + 1)
                    if bx1 <= bx0 or by1 <= by0:
                        continue
                    m = Image.new('L', (bx1 - bx0, by1 - by0), 0)
                    ImageDraw.Draw(m).polygon([(x - bx0, y - by0) for x, y in q], fill=255)
                    mm = np.asarray(m) > 0
                    Pc = C.P[by0:by1, bx0:bx1][mm]
                    x, z = self.world(i + 0.5, j + 0.5)
                    ok = (np.abs(Pc[:, 0] - x) < 4.5) & (np.abs(Pc[:, 2] - z) < 4.5) & (Pc[:, 1] - self.h < 1.6)
                    out[i, j] = ok.mean() if len(Pc) else 0.0
            self._clear = out
        return self._clear


# the raid camera: the same orthographic camera as city_default, VIEW_ZOOM x closer.  The pixels come from the 4k render of the same
# frame (p3_work/city_albedo4k.png, 3840x2160, aligned to city_default at 0,0 px): 2x is native, past that it is upscaled (Lanczos
# + a light unsharp) from a float-box crop, so the world -> screen map stays exact: screen = (p1080 - VIEW_O) * VIEW_ZOOM.
VIEW_ZOOM = 3.5
VIEW_O = (0.0, 0.0)                       # set below from the district: the window's top-left on city_default.png (1080 coords)
CITY4K = 'D:/rc_scratch/tide_concepts/p3_work/city_albedo4k.png'
UI_S = 0.76                               # the side columns (CREW, rows, core tape / work order, shop, SEND IT) drawn at this scale
MAP_C = (960.0, 470.0)                    # where the district centre sits on screen (between the scaled columns, above the HUD line)


def view(x, y):
    return (x - VIEW_O[0]) * VIEW_ZOOM, (y - VIEW_O[1]) * VIEW_ZOOM


# the street district: the low-rise blocks south-west of the HQ ring.  Avenue b (world x -189..-183) runs the whole length, avenue
# e (x -171..-165) from row 3; cross streets 1 (north) and 6-7 (south); blocks on c3-c5, a2-a5, f1-g2.
G = CityGrid(-195.0, -135.0, 7, 7)


# the high-resolution city: a native Godot capture centred on the raid window (city_hi, see hi_grade.py); its frame on city_default
HI_DIR = 'D:/rc_scratch/raid_v3/city_hi/'
HIF = json.load(open(HI_DIR + 'hi_frame.json')) if os.path.exists(HI_DIR + 'hi_frame.json') else None


def hi_box():
    """the raid window as a box in hi-capture px (hi px = centre + (city_default px - its centre) * K)"""
    k = HIF['K']
    x0 = HIF['w'] / 2 + (VIEW_O[0] - HIF['cx0']) * k
    y0 = HIF['h'] / 2 + (VIEW_O[1] - HIF['cy0']) * k
    return (x0, y0, x0 + W / VIEW_ZOOM * k, y0 + H / VIEW_ZOOM * k)


def _frame():
    """the camera window: the district centre on MAP_C, clamped to the source plate (the hi capture, else the 4k plate)"""
    gx, gy = G.sp1080(G.nc / 2, G.nr / 2)
    ww, wh = W / VIEW_ZOOM, H / VIEW_ZOOM
    if HIF:
        bx0, by0 = HIF['cx0'] - HIF['w'] / 2 / HIF['K'], HIF['cy0'] - HIF['h'] / 2 / HIF['K']
        bx1, by1 = HIF['cx0'] + HIF['w'] / 2 / HIF['K'], HIF['cy0'] + HIF['h'] / 2 / HIF['K']
        return min(max(gx - MAP_C[0] / VIEW_ZOOM, bx0), bx1 - ww), min(max(gy - MAP_C[1] / VIEW_ZOOM, by0), by1 - wh)
    ox = min(max(gx - MAP_C[0] / VIEW_ZOOM, 0.0), 1920.0 - ww)
    oy = min(max(gy - MAP_C[1] / VIEW_ZOOM, 0.0), 1080.0 - wh)
    return min(round(ox * 2), math.floor((1920.0 - ww) * 2)) / 2, min(round(oy * 2), math.floor((1080.0 - wh) * 2)) / 2


VIEW_O = _frame()


def ground_vis_ss():
    """per-pixel ground visibility at SS (1 = the ground is what the camera sees here), from the 1080 world positions, cropped
    to the raid window and scaled up (the mask is coarser than the picture: 2 px steps)"""
    if HIF:                                                 # native: from the hi capture's own world positions
        gv = Image.open(HI_DIR + 'ground_vis_hi.png')
        return gv.resize((W * SS, H * SS), Image.BILINEAR, box=hi_box()).filter(ImageFilter.GaussianBlur(SS))
    C = city()
    gv = (~C.occlusion_screen(tol=1.6)).astype(np.uint8) * 255
    ox, oy = VIEW_O
    box = (ox, oy, ox + W / VIEW_ZOOM, oy + H / VIEW_ZOOM)
    return Image.fromarray(gv).resize((W * SS, H * SS), Image.BILINEAR, box=box).filter(ImageFilter.GaussianBlur(SS * 1.5))


_GV = {}


def masked_ground(img, L, ghost=0.22):
    """composite a ground layer, hidden where something stands in front (kept at the ghost alpha)"""
    if 'gv' not in _GV:
        _GV['gv'] = ground_vis_ss()
    gv = _GV['gv']
    a = L.im.split()[3]
    k = gv.point(lambda v: int(255 * (ghost + (1 - ghost) * v / 255.0)))
    L.im.putalpha(SL.ImageChops.multiply(a, k))
    comp(img, L)


# =============================================================================================== the backplate
def city_plate(dim=1.0):
    """the native-resolution city, desaturated and darkened under the glass: the district reads, the flanks under the panels
    and the towers below calm down"""
    ox, oy = VIEW_O[0] * 2, VIEW_O[1] * 2
    box = (ox, oy, ox + 2 * W / VIEW_ZOOM, oy + 2 * H / VIEW_ZOOM)
    src = Image.open(CITY4K).convert('RGB') if not HIF else None
    if HIF:                                                 # the native capture: Lanczos DOWN from its float box, no upscale
        src = Image.open(HI_DIR + 'city_albedo_hi.png').convert('RGB').resize((W, H), Image.LANCZOS, box=hi_box())
    elif VIEW_ZOOM == 2.0:
        src = src.crop(tuple(int(v) for v in box))
    else:                                                   # past native: Lanczos up from the float box + a light unsharp
        src = src.resize((W, H), Image.LANCZOS, box=box).filter(ImageFilter.UnsharpMask(1.4, 70, 2))
    a = np.asarray(src).astype(np.float32) / 255.0
    lum = (a @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    a = lum + (a - lum) * 0.72
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = G.cc(G.nc / 2 - 0.5, G.nr / 2 - 0.5)
    e = np.sqrt(((xx - cx) / 640.0) ** 2 + ((yy - cy) / 420.0) ** 2)
    k = 0.56 + 0.40 * np.clip(1.25 - e, 0, 1) ** 1.2
    for x0, x1 in ((0, int(520 * UI_S)), (W - int(520 * UI_S), W)):
        m = np.clip(np.minimum(xx - x0 + 60, x1 - xx + 60) / 60.0, 0, 1)
        k = k * (1 - 0.42 * m)
    a = a * (k * dim)[..., None] * np.array([0.93, 0.99, 1.08], np.float32)
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)).convert('RGBA')


def finish(ov, dim=1.0):
    out = city_plate(dim)
    out.alpha_composite(ov.resize((W, H), Image.LANCZOS))
    return out.convert('RGB')


# =============================================================================================== grid on the ground
def draw_grid(img, F, legal=(), labels=True):
    """system: the placement cell grid on the ground, faint the whole raid; legal cells a little stronger while something is held"""
    L = Layer(); d = L.d
    col = (90, 214, 240)
    for i in range(G.nc + 1):
        d.line([tuple(S(v) for v in G.sp(i, 0)), tuple(S(v) for v in G.sp(i, G.nr))], fill=col + (84,), width=S(1.4))
    for j in range(G.nr + 1):
        d.line([tuple(S(v) for v in G.sp(0, j)), tuple(S(v) for v in G.sp(G.nc, j))], fill=col + (84,), width=S(1.4))
    for (c, r) in legal:
        q = G.quad(c, r, 0.07)
        d.polygon([(S(x), S(y)) for x, y in q], fill=col + (30,))
        IR.dash_poly(d, q + [q[0]], col, 1.6, on=5, off=4)
    masked_ground(img, L)
    if labels:
        L = Layer(); d = L.d
        f = TR.font(MONO, 17)
        for i in range(G.nc):
            x, y = G.sp(i + 0.5, -0.45)
            text(d, (x + 6, y - 6), 'abcdefghijklmnop'[i], f, CYAN + (150,))
        for j in range(G.nr):
            x, y = G.sp(-0.45, j + 0.5)
            text(d, (x - 8, y - 6), str(j + 1), f, CYAN + (150,))
        comp(img, L)


def legal_cells(route_cells, occupied):
    cl = G.clear()
    road = set(route_cells)
    out = []
    for c in range(G.nc):
        for r in range(G.nr):
            if (c, r) in road or (c, r) in occupied or cl[c, r] < 0.6:
                continue
            if any(abs(c - a) <= 1 and abs(r - b) <= 1 for a, b in road):
                out.append((c, r))
    return out


def reach_outline(img, cells, col, alpha=130):
    """a faint dashed outline round an operative's reach, on the ground cells"""
    L = Layer(); d = L.d
    cs = set(cells)
    for (c, r) in cs:
        for dc, dr, a, b in ((0, -1, (c, r), (c + 1, r)), (0, 1, (c, r + 1), (c + 1, r + 1)), (-1, 0, (c, r), (c, r + 1)),
                             (1, 0, (c + 1, r), (c + 1, r + 1))):
            if (c + dc, r + dr) not in cs:
                IR.dash_poly(d, [G.sp(*a), G.sp(*b)], col, 2.2, on=6, off=4)
    a_ = L.im.split()[3].point(lambda v: int(v * alpha / 255))
    L.im.putalpha(a_)
    masked_ground(img, L, ghost=0.5)


def cheb(c, r, k):
    return [(c + a, r + b) for a in range(-k, k + 1) for b in range(-k, k + 1) if 0 <= c + a < G.nc and 0 <= r + b < G.nr]


# =============================================================================================== corp units: threat icon v4
SOL_FILL = (120, 226, 214)          # Solace corp colour (teal porcelain) = health
SOL_RIM = (236, 250, 248)           # the white capsule rim
SOL_EMPTY = (22, 30, 38)
PIP = {'S': ((110, 214, 255), 'slowed'), 'H': ((96, 150, 255), 'held'), 'J': ((150, 236, 110), 'jammed')}
_ICON = {}


def _icon_body(kind, r, c):
    """SHAPE = type (bible 4.8 v4): trooper / riot / sniper = plain Solace capsule bodies, bike = FAST (chevron badge),
    heavy = HEAVY block, drone = FLYING diamond with four rotor circles, wrecker = SPECIAL hexagon"""
    m = Image.new('L', (int(c * 2), int(c * 2)), 0); d = ImageDraw.Draw(m)
    if kind in ('trooper', 'riot', 'sniper'):
        d.rounded_rectangle([c - r * 1.08, c - r * 0.68, c + r * 1.08, c + r * 0.68], radius=r * 0.66, fill=255)
        if kind == 'riot':
            d.rounded_rectangle([c - r * 1.32, c - r * 0.92, c - r * 0.92, c + r * 0.92], radius=r * 0.12, fill=255)
        if kind == 'sniper':
            d.rectangle([c + r * 0.9, c - r * 0.12, c + r * 1.55, c + r * 0.12], fill=255)
    elif kind == 'bike':
        d.rounded_rectangle([c - r * 1.0, c - r * 0.55, c + r * 0.85, c + r * 0.55], radius=r * 0.54, fill=255)
    elif kind == 'heavy':
        d.rounded_rectangle([c - r * 1.08, c - r * 0.9, c + r * 1.08, c + r * 0.9], radius=r * 0.16, fill=255)
    elif kind == 'drone':
        d.polygon([(c, c - r * 0.95), (c + r * 0.95, c), (c, c + r * 0.95), (c - r * 0.95, c)], fill=255)
    elif kind == 'wrecker':
        d.polygon([(c + r * 1.06 * math.cos(math.pi / 3 * k), c + r * 1.06 * math.sin(math.pi / 3 * k)) for k in range(6)], fill=255)
    return m


def icon_img(kind, hp, r=15, ring=True, pips=(), count=None):
    """one threat icon at SS: ink key, white capsule rim, the corp fill = health draining top-down (white line at the level),
    the dashed corp ring (~1.8x) with status pips clockwise from top right, the stack badge"""
    key = (kind, round(hp, 2), r, ring, tuple(pips), count)
    if key in _ICON:
        return _ICON[key]
    R_ = S(r)
    c = S(r * 2.6)
    body = _icon_body(kind, R_, c)
    sz = body.size
    im = Image.new('RGBA', sz, (0, 0, 0, 0))
    keym = body.filter(ImageFilter.MaxFilter(S(2.2) * 2 + 1))
    im = SL.over(im, INK, SL.shift(keym, S(1.5), S(2)))
    im = SL.over(im, INK, keym)
    bb = body.getbbox()
    top, bot = bb[1], bb[3]
    lvl = int(bot - (bot - top) * hp)
    emp = Image.new('L', sz, 0); ImageDraw.Draw(emp).rectangle([0, 0, sz[0], lvl], fill=255)
    fil = Image.new('L', sz, 0); ImageDraw.Draw(fil).rectangle([0, lvl, sz[0], sz[1]], fill=255)
    inner = SL.erode(body, S(1.6))
    im = SL.over(im, SOL_RIM, body)
    im = SL.over(im, SOL_EMPTY, SL.ImageChops.multiply(inner, emp))
    tex = SL.vgrad_tex(sz[0], sz[1], (170, 244, 234), (70, 184, 176)); tex.putalpha(SL.ImageChops.multiply(inner, fil))
    im = Image.alpha_composite(im, tex)
    if 0 < hp < 1:                                         # the white drain line
        ln = Image.new('L', sz, 0); ImageDraw.Draw(ln).rectangle([0, lvl - S(1), sz[0], lvl + S(1)], fill=255)
        im = SL.over(im, (255, 255, 255), SL.ImageChops.multiply(inner, ln))
    d = ImageDraw.Draw(im)
    if kind == 'bike':                                     # FAST: the >> chevron badge
        bx, by = c + R_ * 0.95, c - R_ * 0.55
        d.rounded_rectangle([bx - R_ * 0.55, by - R_ * 0.42, bx + R_ * 0.75, by + R_ * 0.42], radius=R_ * 0.2, fill=INK + (255,),
                            outline=SOL_RIM + (255,), width=S(1.2))
        for k in (0, 1):
            x0 = bx - R_ * 0.3 + k * R_ * 0.42
            d.line([(x0, by - R_ * 0.24), (x0 + R_ * 0.22, by), (x0, by + R_ * 0.24)], fill=(255, 255, 255, 255), width=S(1.6))
    if kind == 'drone':                                    # FLYING: four rotor circles, the 2x2 circle glyph
        for ax, ay in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            x, y = c + ax * R_ * 0.95, c + ay * R_ * 0.95
            rr = R_ * 0.36
            d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=INK + (255,), width=S(2.6))
            d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=SOL_RIM + (255,), width=S(1.2))
        for ax in (-1, 1):
            for ay in (-1, 1):
                x, y = c + ax * R_ * 0.2, c + ay * R_ * 0.2
                d.ellipse([x - R_ * 0.12, y - R_ * 0.12, x + R_ * 0.12, y + R_ * 0.12], fill=INK + (255,))
    if kind == 'wrecker':                                  # SPECIAL: its verb glyph (a wrecking hammer)
        d.rectangle([c - R_ * 0.45, c - R_ * 0.42, c + R_ * 0.45, c - R_ * 0.1], fill=INK + (255,))
        d.rectangle([c - R_ * 0.09, c - R_ * 0.1, c + R_ * 0.09, c + R_ * 0.55], fill=INK + (255,))
    if kind == 'heavy':                                    # HEAVY: armour slats
        for k in (-1, 0, 1):
            y = c + k * R_ * 0.42
            d.line([(c - R_ * 0.7, y), (c + R_ * 0.7, y)], fill=INK + (120,), width=S(1.2))
    if ring:
        RR = R_ * 1.85
        for j in range(18):
            a0 = j * 20
            d.arc([c - RR, c - RR, c + RR, c + RR], a0, a0 + 11, fill=INK + (230,), width=S(4.2))
        for j in range(18):
            a0 = j * 20
            d.arc([c - RR, c - RR, c + RR, c + RR], a0 + 0.5, a0 + 10.5, fill=TEAL_HI + (255,), width=S(2.6))
        for n, code in enumerate(pips):                    # status pips, clockwise from top right
            a = math.radians(-58 + n * 34)
            px, py = c + RR * math.cos(a), c + RR * math.sin(a)
            pr = S(10)
            colp = PIP[code][0]
            d.ellipse([px - pr - S(1.8), py - pr - S(1.8), px + pr + S(1.8), py + pr + S(1.8)], fill=INK + (255,))
            d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=colp + (255,))
            d.text((px, py + S(0.5)), code, font=TR.font(ANTON, 15), fill=INK + (255,), anchor='mm')
        if count:
            s_ = '\u00d7%d' % count
            f = TR.font(ANTON, 19)
            tl = d.textlength(s_, font=f)
            bx, by = c - RR * 0.72, c - RR * 0.72
            d.rounded_rectangle([bx - tl / 2 - S(6), by - S(12), bx + tl / 2 + S(6), by + S(12)], radius=S(5), fill=TEAL + (255,),
                                outline=INK + (255,), width=S(2))
            d.text((bx, by + S(0.5)), s_, font=f, fill=INK + (255,), anchor='mm')
    _ICON[key] = im
    return im


def unit(img, kind, x, y, hp=1.0, count=None, pips=(), alpha=1.0, r=20, lift=28):
    """a threat on the street: the ground disc under it (drains the same way), the icon above it"""
    L = Layer(); d = L.d
    rx, ry = 24, 15
    a = int(255 * alpha)
    d.ellipse([S(x - rx - 2), S(y - ry - 2), S(x + rx + 2), S(y + ry + 2)], fill=INK + (int(a * 0.8),))
    d.pieslice([S(x - rx), S(y - ry), S(x + rx), S(y + ry)], 90 - 180 * hp, 90 + 180 * hp, fill=SOL_FILL + (int(a * 0.75),))
    d.ellipse([S(x - rx), S(y - ry), S(x + rx), S(y + ry)], outline=SOL_RIM + (int(a * 0.8),), width=S(1.3))
    d.line([(S(x), S(y)), (S(x), S(y - lift + 6))], fill=SOL_RIM + (int(a * 0.6),), width=S(1.2))
    comp(img, L)
    im = icon_img(kind, hp, r, True, pips, count)
    if alpha < 1:
        im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    img.alpha_composite(im, (int(S(x) - im.width / 2), int(S(y - lift) - im.height / 2)))


def unit_bits(img, kind, x, y, seed=3, r=20, spread=60, lift=28):
    """a kill: the icon cracks and breaks into 0/1 bits in its own colours (teal fill, white rim), a few white-hot"""
    im = icon_img(kind, 0.15, r, False)
    w, h = im.size
    rng = np.random.default_rng(seed)
    y = y - lift
    for qx, qy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        q = im.crop((qx * w // 2, qy * h // 2, (qx + 1) * w // 2, (qy + 1) * h // 2)).rotate(rng.uniform(-35, 35), expand=True, resample=Image.BICUBIC)
        q.putalpha(q.split()[3].point(lambda v: int(v * 0.7)))
        dx, dy = (qx - 0.5) * S(16), (qy - 0.5) * S(16)
        img.alpha_composite(q, (int(S(x) + dx - q.width / 2), int(S(y) + dy - q.height / 2)))
    L = Layer(); d = L.d
    f = TR.font(MONO, 18)
    for k in range(30):
        a = rng.uniform(0, 2 * math.pi); rr = rng.uniform(12, spread)
        bx, by = x + rr * math.cos(a), y + rr * math.sin(a) * 0.8
        col = (255, 250, 244) if rr < 22 else (SOL_FILL if k % 3 else SOL_RIM)
        al = int(255 * (1.0 - 0.6 * (rr - 12) / max(1, spread - 12)))
        d.text((S(bx), S(by)), '1' if rng.random() < 0.5 else '0', font=f, fill=col + (al,), anchor='mm', stroke_width=S(1), stroke_fill=col + (al,))
    comp(img, L)


# =============================================================================================== operatives on the city: R3 class beacons
def beacon(img, oid, c, r, alpha=1.0, height=8.5):
    """2D stand-in for the R3 class beacon (bible 4.8): a cone opening up from the pad on the cell to a cap ring, the class
    emblem as a scanlined holo disc in the role colour (no light behind it)"""
    top, bot = K.OPS[oid]['col']
    gx, gy = G.cc(c, r)
    cx, cy = G.cc(c, r, lift=height)
    k = (abs(G.sp(1, 0)[0] - G.sp(0, 0)[0]) / 6.0) * math.sqrt(2)      # screen px per BU, horizontal, for a world circle
    ky = (abs(G.sp(1, 0)[1] - G.sp(0, 0)[1]) / 6.0) * math.sqrt(2)
    pr_x, pr_y = 1.6 * k, 1.6 * ky                                   # sized to the cell (3 BU half-width)
    cr_x, cr_y = 2.8 * k, 2.8 * ky
    a = alpha
    L = Layer(); d = L.d
    # the pad on the ground
    d.ellipse([S(gx - pr_x - 3), S(gy - pr_y - 2), S(gx + pr_x + 3), S(gy + pr_y + 2)], fill=INK + (int(200 * a),))
    d.ellipse([S(gx - pr_x), S(gy - pr_y), S(gx + pr_x), S(gy + pr_y)], fill=bot + (int(150 * a),), outline=top + (int(255 * a),), width=S(2))
    comp(img, L)
    # the cone: a vertical gradient of the role colour, brighter towards the cap
    L = Layer()
    m = Image.new('L', (W * SS, H * SS), 0)
    ImageDraw.Draw(m).polygon([(S(gx - pr_x), S(gy)), (S(cx - cr_x), S(cy)), (S(cx + cr_x), S(cy)), (S(gx + pr_x), S(gy))], fill=255)
    ImageDraw.Draw(m).ellipse([S(cx - cr_x), S(cy - cr_y), S(cx + cr_x), S(cy + cr_y)], fill=255)
    y0, y1 = S(cy - cr_y), S(gy)
    gr = np.zeros((H * SS,), np.float32)
    yy = np.arange(H * SS, dtype=np.float32)
    gr = np.clip((y1 - yy) / max(1, (y1 - y0)), 0, 1) * 0.42 + 0.10
    bx0, bx1 = S(cx - cr_x - 4), S(cx + cr_x + 4)
    ma = np.asarray(m, np.float32)[:, bx0:bx1] / 255.0 * gr[:, None] * a
    lay = np.zeros((H * SS, bx1 - bx0, 4), np.uint8)
    lay[..., :3] = top
    lay[..., 3] = (ma * 255).astype(np.uint8)
    L.im.paste(Image.fromarray(lay, 'RGBA'), (bx0, 0))
    d = L.d
    for s in (-1, 1):                                          # the cone edges
        d.line([(S(gx + s * pr_x), S(gy)), (S(cx + s * cr_x), S(cy))], fill=top + (int(170 * a),), width=S(1.4))
    comp(img, L)
    # the cap ring (and a soft glow of the ring itself)
    L = Layer(); d = L.d
    d.ellipse([S(cx - cr_x), S(cy - cr_y), S(cx + cr_x), S(cy + cr_y)], outline=top + (int(255 * a),), width=S(4))
    gl = L.im.filter(ImageFilter.GaussianBlur(S(4)))
    img.alpha_composite(gl)
    d.ellipse([S(cx - cr_x), S(cy - cr_y), S(cx + cr_x), S(cy + cr_y)], outline=(255, 255, 255, int(220 * a)), width=S(1.3))
    comp(img, L)
    # the emblem: a scanlined holo disc with the class glyph, floating inside the cone under the cap
    ex, ey = cx, cy + 30
    er = 21
    em = Image.new('RGBA', (S(er * 2 + 4), S(er * 2 + 4)), (0, 0, 0, 0))
    ed = ImageDraw.Draw(em)
    o = S(er + 2)
    ed.ellipse([o - S(er), o - S(er), o + S(er), o + S(er)], fill=bot + (int(150 * a),), outline=top + (int(255 * a),), width=S(2))
    gm = IR.glyph_mask(K.OPS[oid]['g'], S(er * 1.25))
    em.paste(Image.new('RGBA', gm.size, (255, 255, 255, int(235 * a))), (o - gm.width // 2, o - gm.height // 2), gm)
    sl = np.asarray(em).copy()
    sl[::S(2.5) if S(2.5) > 1 else 2, :, 3] = (sl[::S(2.5) if S(2.5) > 1 else 2, :, 3] * 0.35).astype(np.uint8)
    em = Image.fromarray(sl, 'RGBA')
    img.alpha_composite(em, (int(S(ex) - em.width / 2), int(S(ey) - em.height / 2)))
    return (cx, cy + 30)


# =============================================================================================== the raid layout (STATIC ALLEY)
def route_cells(spec):
    """a route from a list of (c, r) corner cells: straight runs between them"""
    out = []
    for (a, b), (c, d) in zip(spec, spec[1:]):
        n = max(abs(c - a), abs(d - b))
        for k in range(n + (1 if (c, d) == spec[-1] else 0)):
            out.append((a + (c - a) * k // max(1, n), b + (d - b) * k // max(1, n)))
    return out


SAFE = (2, 6)
RA = route_cells([(0, 0), (1, 0), (1, 6)])                 # A: in from the north-west along street 1, then down avenue b
RB = route_cells([(6, 5), (3, 5), (3, 6)])                 # B: in from the south-east along street 6, then one cell down to 7
ENT_A, ENT_B = (-2, 0), (8, 5)                              # where each stack waits, off the district
BARR = (1, 3)
BARR_UP, BARR_UP2 = (1, 2), (1, 1)                          # the cells before the wall on A (held trooper, the kill)
PLACED = {'KAI': (2, 1), 'VEX': (4, 4), 'MOTH': (0, 6)}
WHERE = {k: G.name(*v) for k, v in PLACED.items()}
HOVER = (4, 6)
BEST = [((4, 6), '+3'), ((5, 6), '+2'), ((6, 4), '+1')]
N_BARR, N_HOVER = G.name(*BARR), G.name(*HOVER)
STICK = dict(safe=0.66, barricade=0.56, site=0.66, core=0.56)   # map stickers sized to about one cell (145 x 93 px at 3.5x)


def cell_w():
    """the screen width of one cell diamond"""
    return abs(G.sp(1, 0)[0] - G.sp(0, 1)[0])


def leak_at():
    """where the B leak note sits: under the Safehouse, left of RUNE's reach"""
    x, y = G.cc(*SAFE)
    return x - 50, y + 104


def edge_pt(entry, first):
    """the point on the district edge where the route enters (the first route cell's outer side)"""
    dx = (first[0] > entry[0]) - (first[0] < entry[0])
    dy = (first[1] > entry[1]) - (first[1] < entry[1])
    return G.sp(first[0] + 0.5 - 0.5 * dx, first[1] + 0.5 - 0.5 * dy)


def route_line(cells, entry, end, k=0.5):
    """the route through the cell centres: from the waiting stack, cell to cell, to the edge of the end cell"""
    pts = [G.cc(*entry)] + [G.cc(*c) for c in cells]
    a, b = pts[-1], G.cc(*end)
    pts.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k))
    return pts


def route_ground(img, cells, entry, end, col=None, part='tint'):
    """system: the cells a route travels, tinted on the ground, with a small chevron per cell in the travel direction; the
    entry cell (where the stack waits, off the district) tinted stronger with a solid edge"""
    col = col or (255, 60, 70)
    L = Layer(); d = L.d
    Lc = Layer(); dc_ = Lc.d
    path = [entry] + list(cells)
    for n, cell in enumerate(path):
        q = G.quad(cell[0], cell[1], 0.06)
        first = n == 0
        d.polygon([(S(x), S(y)) for x, y in q], fill=col + (70 if first else 52,))
        if first:
            d.line([(S(x), S(y)) for x, y in q + [q[0]]], fill=col + (220,), width=S(2.4))
        nxt = path[n + 1] if n + 1 < len(path) else end
        sc, sr = (nxt[0] > cell[0]) - (nxt[0] < cell[0]), (nxt[1] > cell[1]) - (nxt[1] < cell[1])
        pc, pr_ = abs(sr), abs(sc)                                 # the other lattice axis: the chevron lies flat on the ground
        oc, orr = cell[0] + 0.5, cell[1] + 0.5
        for t in (-0.18, 0.16):                                   # two chevrons per cell, in the travel direction
            v = [G.sp(oc + sc * (t - 0.12) + pc * 0.24, orr + sr * (t - 0.12) + pr_ * 0.24), G.sp(oc + sc * t, orr + sr * t),
                 G.sp(oc + sc * (t - 0.12) - pc * 0.24, orr + sr * (t - 0.12) - pr_ * 0.24)]
            dc_.line([(S(x), S(y)) for x, y in v], fill=INK + (170,), width=S(7), joint='curve')
            dc_.line([(S(x), S(y)) for x, y in v], fill=col + (255,), width=S(3.6), joint='curve')
    if part == 'tint':
        masked_ground(img, L, ghost=0.55)
    else:                                                       # the chevrons go over the route pencil
        masked_ground(img, Lc, ghost=0.8)


def end_cell(img, cell, col=(255, 110, 196)):
    """system: the cell a route ends on (Safehouse / site), tinted in its sticker colour with a solid edge"""
    L = Layer(); d = L.d
    q = G.quad(cell[0], cell[1], 0.04)
    d.polygon([(S(x), S(y)) for x, y in q], fill=col + (70,))
    d.line([(S(x), S(y)) for x, y in q + [q[0]]], fill=col + (240,), width=S(2.6))
    masked_ground(img, L, ghost=0.6)


ROUNDS = R.ROUNDS


def map_objects(img, barricade=True, safe=False, placed=PLACED):
    """runner objects on the glass over their cells: the Safehouse, the barricade; the operatives are beacons on the city"""
    tops = {}
    for oid, (c, r) in sorted(placed.items(), key=lambda kv: G.cc(*kv[1])[1]):        # on the city, under the glass
        tops[oid] = beacon(img, oid, c, r)
    if barricade:
        bx, by = G.cc(*BARR)
        # laid across the street: A runs along +j here (screen down-left), the barricade across it, one cell long
        stick(img, K.dev_sticker('BARRICADE'), bx, by - 6, -33, scale=STICK['barricade'])
    if safe:
        safehouse(img)
    return tops


def safehouse(img):
    """the Safehouse sticker on its cell (drawn after the route pencil, so the routes run into it)"""
    x, y = G.cc(*SAFE)
    stick(img, K.place_sticker('SAFE', 'HOUSE', (255, 110, 196), (222, 24, 136)), x, y - 12, -3, scale=STICK['safe'])


def routes_ground(img, a=True, b=True, part='tint'):
    if a:
        route_ground(img, RA, ENT_A, SAFE, part=part)
    if b:
        route_ground(img, RB, ENT_B, SAFE, part=part)
    if part == 'tint':
        end_cell(img, SAFE)


def routes(pr, a=True, b=True):
    if a:
        K.route(pr, route_line(RA, ENT_A, SAFE), off=0)
        K.entry_mark(pr, *edge_pt(ENT_A, RA[0]), 'A')
    if b:
        K.route(pr, route_line(RB, ENT_B, SAFE), off=0)
        K.entry_mark(pr, *edge_pt(ENT_B, RB[0]), 'B')


def wall_hp(py, a, b, size=26):
    """the barricade's health: a small pencil value beside its sticker (the only pencil on the wall)"""
    bx, by = G.cc(*BARR)
    K.pen_arrow_num(py, a, b, bx - 100, by + 8, size)


def plan_pencil(py, pr, leak=True):
    wall_hp(py, 6, 3)
    if leak:
        lx, ly = leak_at()
        pr.text('2 leak', lx, ly, 32, angle=-6)
        sx, sy = G.cc(*SAFE)
        pr.arrow([(lx + 12, ly - 22), (lx + 22, ly - 40), (sx - 8, sy + 46)], width=6, head=14)
        K.pen_arrow_num(pr, 8, 6, sx - 150, sy + 10, 30)


def ui(img, fn, anchor, s=None):
    """a side column (or a chip) drawn on its own layer at full size, then shrunk by UI_S towards its anchor on the screen"""
    s = s or UI_S
    L = blank()
    fn(L)
    sm = L.resize((int(round(L.width * s)), int(round(L.height * s))), Image.LANCZOS)
    img.alpha_composite(sm, (int(round(anchor[0] * SS * (1 - s))), int(round(anchor[1] * SS * (1 - s)))))


def left_col(img, F, where, core=8, lose=0, credits=7, cost=0, rnd=(1, 4), title='RAID: STATIC ALLEY', kills=None, held=None,
             weapons=None, counts=None, undo=True, cmax=8):
    K.core_tape(img, F, title, core, cmax, lose)
    K.rows(img, F, rnd[0], rnd[1], credits, cost)
    crew_b(img, F, where, held=held, kills=kills, weapons=weapons)
    n_on = sum(1 for v in where.values() if v and not v.startswith('away'))
    K.left_foot(img, F, counts or [('ON MAP', n_on), ('BENCH', 4 - len([v for v in where.values() if v])), ('DEVICES', 1)], undo=undo)


def crew_b(img, F, where, held=None, kills=None, weapons=None):
    """CREW option B (designer): the full roster stays in full colour; a placed operative gets its cell + a tick in pencil
    under it; 'away:X' = at another site (grey vinyl, red pencil reason); held = peeled (a faint liner is left in its slot)"""
    L = Layer(); text(L.d, (26, 182), 'CREW', F['m20'], TEXT_MID + (255,), anchor='lm'); comp(img, L)
    py, pr = Wax(PEN_Y, 91), Wax(PEN_R, 92)
    for oid, (x, y, ang) in K.CREW_POS.items():
        st = where.get(oid)
        o = K.OPS[oid]
        away = bool(st and st.startswith('away'))
        if oid == held:
            K.liner(img, K.op_sticker(oid), x, y, ang)
            continue
        stick(img, K.op_sticker(oid, grey=away), x, y, ang)
        wst = (weapons or {}).get(oid, o['stars'])
        stick(img, K.wpn_sticker(o['wpn'], wst, grey=away), x + K.WPN_OFF[0], y + K.WPN_OFF[1], K.WPN_OFF[2], scale=0.82)
        if away:
            pr.text('at ' + st.split(':')[1], x - 4, y + 104, 30, angle=-6)
        elif st:
            py.text('on ' + st, x - 6, y + 104, 32, angle=-5)
            py.tick(x + 58, y + 102, 13, 6)
        if kills and oid in kills:
            kx, ky = x - 40, y + 104
            py.x(kx, ky, 11, 6)
            py.text(str(kills[oid]), kx + 36, ky + 2, 36, angle=-6)
    py.ink_ss(img); pr.ink_ss(img)


# ---------------------------------------------------------------- right: INCOMING = the intercepted work order (memo under glass)
MEMO_BOX = (1404, 18, 1898, 480)


def mini_icon(im, kind, x, y, r=8):
    ic = icon_img(kind, 1.0, r, ring=False)
    im.alpha_composite(ic, (int(x - ic.width / 2), int(y - ic.height / 2)))


def work_order(img, F, site, heat, rounds, now=0, ref='SOL-WO-2611-07', target='Cell safehouse'):
    x0, y0, x1, y1 = MEMO_BOX
    L = Layer(); d = L.d
    glass(d, (x0, y0, x1, y1), alpha=215)
    text(d, (x0 + 18, y0 + 24), 'INCOMING', F['a30'], TEXT_HI + (255,), anchor='lm')
    text(d, (x0 + 136, y0 + 26), 'intercepted', F['m18'], TEXT_MID + (255,), anchor='lm')
    text(d, (x1 - 18, y0 + 25), 'HEAT %d' % heat, F['a26'], TEXT_MID + (255,), anchor='rm')
    comp(img, L)
    # the memo (paper, at SS), slightly askew under the glass
    pw, ph = 452, 396
    pim = Image.new('RGBA', (S(pw), S(ph)), (0, 0, 0, 0))
    d = ImageDraw.Draw(pim)
    d.rectangle([0, 0, S(pw), S(ph)], fill=(236, 230, 214, 255))
    rng = np.random.default_rng(11)
    for _ in range(700):
        d.point((rng.uniform(0, S(pw)), rng.uniform(0, S(ph))), fill=(212, 204, 186, 255))
    T = lambda xy, s, f, col, anchor='lm': d.text((S(xy[0]), S(xy[1])), s, font=f, fill=col, anchor=anchor)
    T((20, 30), 'SOLACE', TR.font(ANTON, 32), TEAL_D + (255,))
    T((132, 33), 'Civic Assurance \u00b7 Field Operations', TR.font(MONO, 15), (40, 96, 100, 255))
    d.rectangle([S(20), S(52), S(pw - 20), S(54.5)], fill=TEAL_D + (255,))
    T((20, 70), 'WORK ORDER', TR.font(MONO, 15), (96, 90, 80, 255))
    T((pw - 20, 70), ref, TR.font(MONO, 15), (96, 90, 80, 255), 'rm')
    T((20, 98), 'RAID ORDER \u00b7 %s' % site, TR.font(ANTON, 26), INK + (255,))
    T((20, 126), 'TARGET  %s' % target, TR.font(MONO, 16), (60, 56, 50, 255))
    tw_ = d.textlength('TARGET  %s' % target, font=TR.font(MONO, 16)) / SS
    d.rectangle([S(28 + tw_), S(118), S(28 + tw_ + 96), S(134)], fill=(18, 16, 20, 255))
    y = 154
    fh, fg = TR.font(ANTON, 21), TR.font(MONO, 17)
    rowh = 50 if len(rounds) > 3 else 60
    for k, (head, groups) in enumerate(rounds):
        col = INK if k == now else (70, 66, 60)
        T((20, y), head, fh, col + (255,))
        gx = 30
        for path, kind, label, n in groups:
            gy = y + 24
            if path:
                T((gx, gy), path, TR.font(ANTON, 19), (170, 24, 32, 255))
                gx += 16
            mini_icon(pim, kind, S(gx + 12), S(gy), r=7)
            s_ = '%s \u00d7%d' % (label, n)
            T((gx + 26, gy), s_, fg, (40, 44, 52, 255))
            gx += 26 + d.textlength(s_, font=fg) / SS + 18
        d.line([(S(20), S(y + 42)), (S(pw - 20), S(y + 42))], fill=(214, 206, 190, 255), width=S(1))
        y += rowh
    T((20, ph - 22), 'AUTHORISED', TR.font(MONO, 14), (110, 104, 96, 255))
    d.rectangle([S(116), S(ph - 30), S(250), S(ph - 15)], fill=(18, 16, 20, 255))
    T((pw - 20, ph - 22), 'INTERNAL \u00b7 DO NOT FORWARD', TR.font(MONO, 14), (110, 104, 96, 255), 'rm')
    # INTERCEPTED: red rubber stamp, worn
    st = Image.new('L', (S(228), S(56)), 0); sd = ImageDraw.Draw(st)
    sd.rectangle([S(3), S(3), S(225), S(53)], outline=255, width=S(3.5))
    sd.text((S(114), S(30)), 'INTERCEPTED', font=TR.font(ANTON, 36), fill=255, anchor='mm')
    noise = (np.random.default_rng(9).random((st.height, st.width)) > 0.25).astype(np.uint8) * 255
    st = SL.ImageChops.multiply(st, Image.fromarray(noise)).rotate(7, expand=True, resample=Image.BICUBIC)
    pim.paste(Image.new('RGBA', st.size, (196, 30, 40, 220)), (S(pw - 246), S(ph - 74)), st)
    pim = pim.rotate(-1.1, expand=True, resample=Image.BICUBIC)
    cx, cy = (x0 + x1) / 2, y0 + 60 + ph / 2 + 2
    sh = Image.new('RGBA', pim.size, (2, 2, 4, 0))
    sh.putalpha(pim.split()[3].filter(ImageFilter.GaussianBlur(S(5))).point(lambda v: int(v * 0.7)))
    img.alpha_composite(sh, (int(S(cx) - pim.width / 2 + S(4)), int(S(cy) - pim.height / 2 + S(6))))
    img.alpha_composite(pim, (int(S(cx) - pim.width / 2), int(S(cy) - pim.height / 2)))
    # the paper clip, then the glass over it: a cool tint, one sheen band, the cyan frame corners
    L = Layer(); d = L.d
    clx, cly = x0 + 52, y0 + 56
    for (a_, b_) in (((clx - 7, cly - 14), (clx + 7, cly + 34)), ((clx - 2, cly - 8), (clx + 3, cly + 24))):
        d.rounded_rectangle([S(a_[0]), S(a_[1]), S(b_[0]), S(b_[1])], radius=S(7), outline=(150, 156, 166, 255), width=S(2.2))
    d.rectangle([S(x0 + 2), S(y0 + 46), S(x1 - 2), S(y1 - 2)], fill=(40, 120, 150, 26))
    comp(img, L)
    a = np.zeros((H * SS, W * SS), np.float32)
    yy, xx = np.mgrid[S(y0):S(y1), S(x0):S(x1)].astype(np.float32) / SS
    u = (xx - x0) + 0.7 * (yy - y0)
    a[S(y0):S(y1), S(x0):S(x1)] = np.exp(-((u - 250) / 70.0) ** 2) * 0.10 + np.exp(-((u - 330) / 16.0) ** 2) * 0.06
    lay = Image.new('RGBA', (W * SS, H * SS), (210, 240, 255, 0))
    lay.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    img.alpha_composite(lay)
    L = Layer(); d = L.d
    c_ = 18
    for (x, y_, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(S(x), S(y_ + dy * c_)), (S(x), S(y_)), (S(x + dx * c_), S(y_))], fill=CYAN + (255,), width=S(4))
    comp(img, L)
    # the Cell's pencil marks the round that is now (on the glass)
    py = Wax(PEN_Y, 71)
    ry = cy - ph / 2 + 154 + now * (50 if len(rounds) > 3 else 60)
    py.stroke(py.wobble([(x0 + 12, ry - 12), (x0 + 8, ry + 2), (x0 + 12, ry + 38)], 0.6), 6, taper=False)
    py.ink_ss(img)


def right_col(img, F, site='STATIC ALLEY', rounds=ROUNDS, state='ready', peeled=None, system='START ROUND 1', locked=False,
              target='Cell safehouse'):
    work_order(img, F, site, 25, rounds, target=target)
    K.shop_sheet(img, F, peeled=peeled)
    if locked:
        L = Layer()
        L.d.rectangle([S(1404), S(492), S(1898), S(834)], fill=(6, 8, 12, 150))
        text(L.d, (1651, 752), 'shop opens after the round', F['m20'], TEXT_HI + (255,))
        comp(img, L)
    K.send_it(img, F, system=system, state=state)


def cursor(img, x, y, scale=1.0):
    """the OS pointer (tip at x, y)"""
    pts = [(0, 0), (0, 25), (6, 19), (10.5, 29), (14.5, 27), (10, 17.5), (18, 17.5)]
    L = Layer(); d = L.d
    P = [(S(x + px * scale), S(y + py_ * scale)) for px, py_ in pts]
    d.polygon([(a + S(2), b + S(3)) for a, b in P], fill=(0, 0, 0, 110))
    d.polygon(P, fill=(255, 255, 255, 255), outline=INK + (255,), width=S(1.6))
    comp(img, L)


# ---------------------------------------------------------------- 1. plan
def units_at_rest(img, alpha=1.0):
    unit(img, 'trooper', *G.cc(*ENT_A), 1.0, count=5, alpha=alpha)
    unit(img, 'bike', *G.cc(*ENT_B), 1.0, count=3, alpha=alpha)


def plate_plan():
    F = F_all(); img = blank()
    draw_grid(img, F)
    routes_ground(img)
    map_objects(img)
    py, pr = Wax(PEN_Y, 1), Wax(PEN_R, 2)
    routes(pr)
    plan_pencil(py, pr)
    py.ink_ss(img); pr.ink_ss(img)
    routes_ground(img, part='chev')
    safehouse(img)
    units_at_rest(img)
    ui(img, lambda L: left_col(L, F, WHERE, lose=2), (0, 0))
    ui(img, lambda L: right_col(L, F), (W, 0))
    K.hud_line(img, F, 'FORECAST', [('A holds at ' + N_BARR, S_GAIN), DOT, ('B 2 leak', S_HARM), DOT, ('Core 8 → 6', S_HARM), DOT,
                                    ('6/8 killed', S_HI)])
    return img


# ---------------------------------------------------------------- 2. place: RUNE held, Takeover's drag (spring lag)
def pen_hatch_quad(p, q, step=14, w=5):
    p.stroke(p.wobble(q + [q[0]], 1.0), w, taper=False)
    cx = sum(x for x, _ in q) / 4; cy = sum(y for _, y in q) / 4
    for a, b in zip(q, q[1:] + q[:1]):
        L_ = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L_, (b[1] - a[1]) / L_
        for t in np.arange(8, L_ - 6, step):
            x, y = a[0] + ux * t, a[1] + uy * t
            ix, iy = cx - x, cy - y; n = math.hypot(ix, iy); ix, iy = ix / n, iy / n
            p.stroke([(x + ix * 2, y + iy * 2), (x + ix * 10 + ux * 5, y + iy * 10 + uy * 5)], 2.6, taper=False)


def plate_place():
    F = F_all(); img = blank()
    occ = set(PLACED.values()) | {BARR, SAFE}
    legal = legal_cells(RA + RB, occ)
    draw_grid(img, F, legal=legal)
    routes_ground(img)
    map_objects(img)
    py, pr = Wax(PEN_Y, 3), Wax(PEN_R, 4)
    routes(pr)
    plan_pencil(py, pr, leak=False)
    # the preview: reach (Chebyshev 1) hatched on the district's cells, the hovered cell circled, kills-if-placed
    hc, hr = HOVER
    c0, c1, r0, r1 = max(hc - 1, 0), min(hc + 2, G.nc), max(hr - 1, 0), min(hr + 2, G.nr)
    pen_hatch_quad(py, [G.sp(c0, r0), G.sp(c1, r0), G.sp(c1, r1), G.sp(c0, r1)])
    hx, hy = G.cc(*HOVER)
    py.circle(hx, hy, 54, 34, width=6, start=-2.2, over=0.5, tilt=0)
    ps = Wax(PEN_Y, 33)                                  # inked after the red: the strike
    for (c, r), s_ in BEST:
        x, y = G.cc(c, r)
        if (c, r) == HOVER:
            py.text(s_, x - 6, y - 62, 40, angle=-6)
        else:
            py.text(s_, x, y + 2, 30, angle=-6)
    # B no longer leaks: the red "2 leak" struck through in yellow, 0 under it; "safe" by the Safehouse
    lx, ly = leak_at()
    pr.text('2 leak', lx, ly, 32, angle=-6)
    py.text('0', lx + 4, ly + 40, 38, angle=-6)
    sx, sy = G.cc(*SAFE)
    py.text('safe', sx - 140, sy + 10, 32, angle=-6)
    # the held sticker trails the pointer (spring lag): still catching up, below right of the pointer, tilted into the motion;
    # the yellow plan arrow runs from it to the hovered cell
    cxp, cyp = hx + 10, hy + 8
    hold = (hx + 175, hy + 150)
    py.arrow([(hold[0] - 58, hold[1] - 46), (hold[0] - 96, hold[1] - 92), (hx + 62, hy + 12), (hx + 40, hy + 2)], width=6, head=16)
    py.ink_ss(img); pr.ink_ss(img)
    ps.stroke(ps.wobble([(lx - 50, ly + 8), (lx + 50, ly - 8)], 0.6), 6, taper=False)
    ps.ink_ss(img)
    routes_ground(img, part='chev')
    safehouse(img)
    units_at_rest(img)
    ui(img, lambda L: left_col(L, F, WHERE, held='RUNE'), (0, 0))
    hs = 0.86 * UI_S                                     # the held sticker keeps its CREW size (lifted a touch)
    L = Layer(); d = L.d                                 # motion streaks on the trailing side
    for k, (ox, oy) in enumerate(((60, 66), (76, 44), (42, 82))):
        d.line([(S(hold[0] + ox), S(hold[1] + oy)), (S(hold[0] + ox + 34), S(hold[1] + oy + 42))], fill=(235, 230, 255, 80 - k * 18), width=S(3))
    comp(img, L)
    stick(img, K.op_sticker('RUNE', curl=0.30), hold[0], hold[1], 9, scale=hs, lift=1.0)
    stick(img, K.wpn_sticker('SHOTGUN', 1), hold[0] + 72 * hs - 8, hold[1] - 66 * hs - 10, 16, scale=0.72 * UI_S, lift=1.0)
    cursor(img, cxp, cyp)
    ui(img, lambda L: right_col(L, F), (W, 0))
    K.hud_line(img, F, 'IF PLACED ' + N_HOVER, [('B 2 leak', S_HARM), ('→', S_MID), ('0 leak', S_GAIN), DOT, ('Core safe', S_GAIN), DOT,
                                        ('8/8 killed', S_HI)])
    return img


# ---------------------------------------------------------------- 3. shop
def plate_shop():
    F = F_all(); img = blank()
    draw_grid(img, F)
    routes_ground(img)
    map_objects(img)
    py, pr = Wax(PEN_Y, 5), Wax(PEN_R, 6)
    routes(pr)
    plan_pencil(py, pr)
    py.ink_ss(img); pr.ink_ss(img)
    routes_ground(img, part='chev')
    safehouse(img)
    units_at_rest(img)

    def left(L):
        left_col(L, F, WHERE, lose=2, cost=3)
        sx, sy, sa = K.CREW_POS['RUNE']
        wx, wy = sx + K.WPN_OFF[0], sy + K.WPN_OFF[1]
        stick(L, K.wpn_sticker('SHOTGUN', 1, cost=3, curl=0.16), wx - 8, wy - 54, 3, scale=0.84, lift=0.7)
        p = Wax(PEN_Y, 7)
        p.text('MERGE', 214, 744, 32, angle=-5)
        K.pen_star(p, 296, 742); p.text('+', 322, 744, 30); K.pen_star(p, 348, 742)
        p.arrow([(368, 744), (386, 742), (404, 743)], width=5, head=10)
        K.pen_star(p, 428, 742); K.pen_star(p, 454, 740)
        p.arrow([(534, 428), (546, 452), (534, 474)], width=5, head=12)
        p.ink_ss(L)
    ui(img, left, (0, 0))
    ui(img, lambda L: right_col(L, F, peeled='SHOTGUN'), (W, 0))
    K.hud_line(img, F, 'BUY', [('SHOTGUN on RUNE', S_PLAN), ('merges, 1 → 2 stars', S_GAIN), DOT, ('3 credits: 7 → 4', S_HI)])
    return img


# ---------------------------------------------------------------- 4. playback (tick 3 of 8)
def tracer(img, p0, p1, col):
    K.tracer(img, p0, p1, col)


def plate_playback():
    F = F_all(); img = blank()
    draw_grid(img, F)
    routes_ground(img)
    placed = dict(PLACED, RUNE=HOVER)
    for oid in ('KAI', 'VEX'):
        k = K.OPS[oid]['reach']
        reach_outline(img, cheb(*placed[oid], k), K.OPS[oid]['col'][0], alpha=120)
    tops = map_objects(img, placed=placed)
    # the units still to enter (faint), the held trooper at the wall, the slowed bike
    unit(img, 'trooper', *G.cc(*ENT_A), 1.0, count=3, alpha=0.38)
    unit(img, 'bike', *G.cc(*ENT_B), 1.0, count=1, alpha=0.38)
    hx, hy = G.cc(*BARR_UP)
    bx, by = G.cc(5, 5)
    L = Layer()                                         # glide: a short smear behind the bike (it came along from g6)
    ux, uy = G.cc(6, 5)[0] - bx, G.cc(6, 5)[1] - by
    for k in range(5):
        L.d.line([(S(bx + ux * (0.35 + k * 0.12)), S(by - 28 + uy * (0.35 + k * 0.12))), (S(bx + ux * (0.45 + k * 0.12)), S(by - 28 + uy * (0.45 + k * 0.12)))],
                 fill=(170, 230, 230, 140 - k * 24), width=S(3))
    comp(img, L)
    pr0 = Wax(PEN_R, 10)                                  # the routes first: the live icons ride on top of the pencil
    routes(pr0)
    pr0.ink_ss(img)
    routes_ground(img, part='chev')
    unit(img, 'trooper', hx, hy, 0.5, pips=('H',), r=22)
    unit(img, 'bike', bx, by, 0.5, pips=('S',), r=22)
    # FX: tracers from the beacons, the kill bursting into bits, damage pops
    kx, ky = tops['KAI']; vx, vy = tops['VEX']
    tracer(img, (kx, ky), (hx + 8, hy - 28), K.OPS['KAI']['col'][1])
    ex, ey = G.cc(*BARR_UP2)
    tracer(img, (kx, ky), (ex + 4, ey - 24), K.OPS['KAI']['col'][1])
    tracer(img, (vx, vy), (bx - 12, by - 28), K.OPS['VEX']['col'][1])
    unit_bits(img, 'trooper', ex, ey, spread=52)
    py, pr = Wax(PEN_Y, 9), Wax(PEN_R, 12)
    # the value of each status in pencil beside its ring pip
    py.text('2', hx + 58, hy - 82, 32, angle=-6)
    py.text('1', bx + 58, by - 82, 32, angle=-6)
    wall_hp(py, 6, 4)                                     # the barricade's hp, live
    for (x, y) in ((kx + 52, ky - 34), (vx + 52, vy - 40)):  # kill tallies by KAI and VEX
        py.x(x, y, 11, 6)
    py.ink_ss(img); pr.ink_ss(img)
    safehouse(img)
    K.pop(img, F, hx - 76, hy - 80, '−4')
    K.pop(img, F, bx + 40, by - 108, '−3')
    stick(img, K.word_sticker('HELD + BOMBARD ×2', (255, 110, 196), (222, 24, 136)), hx - 220, hy - 34, -4, scale=0.86)
    ui(img, lambda L: left_col(L, F, dict(WHERE, RUNE=G.name(*HOVER))), (0, 0))
    ui(img, lambda L: right_col(L, F, state='busy', locked=True), (W, 0))
    K.hud_line(img, F, 'TICK 3/8', [('killed 2', S_GAIN), DOT, ('leaked 0', S_HI), DOT, ('1 held at a wall', S_HI), DOT,
                                    ('4 still to enter', S_MID)], ticks=(3, 8))
    return img


# =============================================================================================== 5. the site raid (SITE B2) on the same streets
SITE, SCORE = (1, 5), (0, 5)                                # the site on the b6 crossing, its core one cell west (off the lanes)
SA = [(c, 5) for c in range(6, 1, -1)]                     # A: in from the south-east along street 6
SB = [(1, r) for r in range(0, 5)]                         # B: down avenue b from the north
SC = [(1, 6)]                                              # C: up avenue b from the south-west edge
S_ENT = {'A': (8, 5), 'B': (1, -2), 'C': (1, 8)}
S_KAI, S_VEX = (4, 4), (0, 6)
SROUNDS = [('ROUND 1 (now)  ·  7 units', [('A', 'trooper', 'Trooper', 3), ('B', 'riot', 'Riot', 2), ('C', 'drone', 'Drone', 2)]),
           ('ROUND 2  ·  8 units', [(None, 'trooper', 'Trooper', 4), (None, 'bike', 'Bike', 2), (None, 'drone', 'Drone', 2)]),
           ('ROUND 3  ·  9 units', [(None, 'heavy', 'Heavy', 2), (None, 'riot', 'Riot', 3), (None, 'trooper', 'Trooper', 4)])]


def plate_site():
    F = F_all(); img = blank()
    draw_grid(img, F)
    for cells, lt in ((SA, 'A'), (SB, 'B'), (SC, 'C')):
        route_ground(img, cells, S_ENT[lt], SITE)
    end_cell(img, SITE, col=(150, 236, 130))
    tops = {}
    for oid, cell in (('KAI', S_KAI), ('VEX', S_VEX)):
        tops[oid] = beacon(img, oid, *cell)
    sx, sy = G.cc(*SITE)
    cx, cy = G.cc(*SCORE)
    py, pr = Wax(PEN_Y, 11), Wax(PEN_R, 12)
    for cells, lt in ((SA, 'A'), (SB, 'B'), (SC, 'C')):
        K.route(pr, route_line(cells, S_ENT[lt], SITE), off=0)
        K.entry_mark(pr, *edge_pt(S_ENT[lt], cells[0]), lt)
    pr.ink_ss(img)
    for cells, lt in ((SA, 'A'), (SB, 'B'), (SC, 'C')):
        route_ground(img, cells, S_ENT[lt], SITE, part='chev')
    # the core on the cell west of the site, the site sticker on its cell
    stick(img, K.place_sticker('CORE', None, (255, 110, 196), (222, 24, 136), shape='hex', w=100, h=64), cx, cy - 4, 3, scale=STICK['core'])
    L = Layer(); text(L.d, (cx + 36, cy - 64), '8/8', F['a40'], TEXT_HI + (255,), stroke=2, sfill=INK + (255,)); comp(img, L)
    stick(img, K.place_sticker('B2', 'SITE', (150, 236, 130), (62, 170, 70), shape='socket', w=96, h=84), sx, sy - 10, -3, scale=STICK['site'])
    pr = Wax(PEN_R, 13)
    kx, ky = tops['KAI']; vx, vy = tops['VEX']
    py.text('B2 crew', kx + 96, ky - 20, 32, angle=-6)
    py.arrow([(468, 772), (490, 720), (vx - 30, vy + 64), (vx - 18, vy + 40)], width=6, head=16)      # VEX came in from C2
    py.text('from C2', 470, 800, 34, angle=-6)
    # forecast: B (riot) leaks 1 into the core
    bx_, by_ = G.cc(*SB[0])
    pr.text('1 leak', bx_ + 104, by_ - 6, 34, angle=-5)
    K.pen_arrow_num(pr, 8, 7, cx + 72, cy - 118, 30)
    # who defends: the margin note above left of the map, outside the district
    py.text('who defends B2', 570, 236, 34, angle=-3)
    py.text('KAI    B2', 520, 284, 30, angle=-3); py.tick(624, 282, 12, 6)
    py.text('VEX    C2', 520, 328, 30, angle=-3); py.tick(624, 326, 12, 6)
    py.ink_ss(img); pr.ink_ss(img)
    unit(img, 'trooper', *G.cc(*S_ENT['A']), 1.0, count=3)
    unit(img, 'riot', *G.cc(*S_ENT['B']), 1.0, count=2)
    unit(img, 'drone', *G.cc(*S_ENT['C']), 1.0, count=2)
    ui(img, lambda L: K.chip(L, F, 660, 34, 'Evacuate (give up B2 without a fight, KAI back to HQ)', '', w=600), (960, 20))
    ui(img, lambda L: left_col(L, F, {'KAI': G.name(*S_KAI), 'VEX': G.name(*S_VEX), 'MOTH': 'away:A1', 'RUNE': 'away:D4'}, lose=1,
                               title='RAID: SITE B2', rnd=(1, 3), counts=[('ON MAP', 2), ('AWAY', 2), ('DEVICES', 0)]), (0, 0))
    ui(img, lambda L: right_col(L, F, site='SITE B2', rounds=SROUNDS, target='site B2, core'), (W, 0))
    K.hud_line(img, F, 'FORECAST', [('A 0 leak', S_GAIN), DOT, ('B 1 leak', S_HARM), DOT, ('C 0 leak', S_GAIN), DOT,
                                    ('Core 8 → 7', S_HARM), DOT, ('6/7 killed', S_HI)])
    return img


# =============================================================================================== 6. aftermath: the corp's report
def plate_aftermath():
    F = F_all(); img = blank()
    draw_grid(img, F, labels=False)
    map_objects(img, placed={}, safe=True)
    L = Layer(); L.d.rectangle([S(int(520 * UI_S)), S(0), S(W - int(520 * UI_S)), S(H)], fill=(4, 6, 10, 140)); comp(img, L)
    R.REPORT = [('OPERATION', 'CLEAN SWEEP'), ('TARGET', 'Cell safehouse, grid %s' % G.name(*SAFE)), ('DURATION', '4 rounds'),
                ('UNITS COMMITTED', '34'), ('UNITS LOST', '30'), ('UNITS THROUGH', '0'), ('TARGET DAMAGE', 'none'), ('OUTCOME', None),
                ('NEXT ACTION', 'review Heat, resubmit')]
    paper = R.report_paper(F).rotate(R.PANG, expand=True, resample=Image.BICUBIC)
    sh = Image.new('RGBA', paper.size, (4, 3, 6, 0))
    sh.putalpha(paper.split()[3].filter(ImageFilter.GaussianBlur(S(10))).point(lambda v: int(v * 0.6)))
    x, y = int(S(R.PCX) - paper.width / 2), int(S(R.PCY) - paper.height / 2)
    img.alpha_composite(sh, (x + S(10), y + S(16)))
    img.alpha_composite(paper, (x, y))
    P, RVX, RY0, RDY = R.P, R.RVX, R.RY0, R.RDY
    py = Wax(PEN_Y, 13)
    cx, cy = P(RVX + 18, RY0 + 4 * RDY)
    py.circle(cx, cy, 44, 28, width=7, start=-2.4, over=0.5, tilt=-0.03)
    lx, ly = P(560, RY0 + 4 * RDY - 6)
    py.text('30/34', lx, ly, 60, angle=R.PANG - 6)
    for k, dx in ((5, 40), (6, 104)):
        tx, ty = P(RVX + dx, RY0 + k * RDY)
        py.tick(tx, ty, 13, 6)
    hx, hy = P(590, RY0 + 6 * RDY)
    py.text('HQ untouched', hx, hy, 32, angle=R.PANG - 4)
    py.ink_ss(img)
    hx, hy = P(500, RY0 + 8 * RDY + 70)
    stick(img, K.verb_sticker('HELD', (255, 238, 96), (255, 182, 14), size=110), hx, hy, R.PANG - 7, scale=1.0)
    ui(img, lambda L: left_col(L, F, {}, kills={'KAI': 11, 'VEX': 9, 'MOTH': 4, 'RUNE': 6}, rnd=(4, 4), credits=12,
                               counts=[('KILLED', 30), ('LEAKED', 0)], undo=False), (0, 0))

    def right(Limg):
        Ly = Layer(); d = Ly.d
        x0, y0, x1, y1 = 1404, 18, 1898, 330
        glass(d, (x0, y0, x1, y1))
        text(d, (x0 + 18, y0 + 28), 'RESULT', F['m20'], TEXT_MID + (255,), anchor='lm')
        text(d, (x0 + 18, y0 + 80), 'HELD for 4 rounds', F['a48'], S_GAIN + (255,), anchor='lm')
        text(d, (x0 + 18, y0 + 138), '30 of 34 units killed, 0 leaked', F['a28'], S_HI + (255,), anchor='lm')
        d.line([(S(x0 + 14), S(y0 + 172)), (S(x1 - 14), S(y0 + 172))], fill=(40, 90, 110, 255), width=S(1.5))
        text(d, (x0 + 18, y0 + 206), 'HQ untouched', F['a28'], S_GAIN + (255,), anchor='lm')
        text(d, (x0 + 18, y0 + 250), 'Heat −1', F['a28'], S_GAIN + (255,), anchor='lm')
        text(d, (x0 + 120, y0 + 251), '25 → 24', F['a28'], S_HI + (255,), anchor='lm')
        comp(Limg, Ly)
        K.send_it(Limg, F, system=None, word='CONTINUE', key='Continue [SPACE]')
    ui(img, right, (W, 0))
    return img


# =============================================================================================== sheet
def sheet():
    names = [('r3_plan', 'plan', 'at rest: A down avenue b, B in along street 6, wall on b4, B leaks 2'),
             ('r3_place', 'place', 'RUNE held (spring lag): reach hatched, e7 circled, +3 / +2 / +1, IF PLACED'),
             ('r3_shop', 'shop', 'sticker sheet: SHOTGUN peeled, slapped on RUNE, merge to 2 stars'),
             ('r3_playback', 'playback', 'tick 3/8: v4 icons, ring pips + pencil values, kill bits, pops'),
             ('r3_site', 'site raid', 'B2 on the b6 street crossing: core 8, B2 crew + C2 support, Evacuate chip'),
             ('r3_aftermath', 'aftermath', "Solace after-action report, the Cell's pencil, HELD")]
    tw_, th_ = 700, 394
    pad, cap = 12, 58
    cols = 3
    sh = Image.new('RGB', (cols * tw_ + (cols + 1) * pad, 2 * (th_ + cap) + 3 * pad + 50), (14, 14, 18))
    d = ImageDraw.Draw(sh)
    f = ImageFont.truetype(MONO, 15); fa = ImageFont.truetype(ANTON, 22); fb = ImageFont.truetype(ANTON, 30)
    d.text((pad, 10), 'RAID in DEFACE v3: set 4, the 3D city at 3.5x, smaller side columns (designer review of set 3)', font=fb, fill=TEXT_HI)
    for k, (n, t, c) in enumerate(names):
        im = Image.open(OUT + n + '.png').resize((tw_, th_), Image.LANCZOS)
        x = pad + (k % cols) * (tw_ + pad); y = 54 + pad + (k // cols) * (th_ + cap + pad)
        sh.paste(im, (x, y))
        d.text((x + 4, y + th_ + 4), '%s   %s.png' % (t, n), font=fa, fill=TEXT_HI)
        d.text((x + 4, y + th_ + 34), c, font=f, fill=TEXT_MID)
    sh.save(OUT + 'r3_sheet.jpg', quality=90)
    print('ok', OUT + 'r3_sheet.jpg', flush=True)


PLATES = dict(plan=plate_plan, place=plate_place, shop=plate_shop, playback=plate_playback, site=plate_site, aftermath=plate_aftermath)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    print('camera fit residual (median, p95 px):', city().fit_res, flush=True)
    for n in (sys.argv[1:] or ['plan', 'place', 'shop', 'playback', 'site', 'aftermath', 'sheet']):
        if n == 'sheet':
            sheet(); continue
        ov = PLATES[n]()
        finish(ov, dim=0.8 if n == 'aftermath' else 1.0).save(OUT + 'r3_%s.png' % n)
        print('ok', OUT + 'r3_%s.png' % n, flush=True)
