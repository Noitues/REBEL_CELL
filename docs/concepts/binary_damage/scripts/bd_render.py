"""Binary damage shards: concept renderer (Pillow only, seeded).

Composites 2D VFX frames over the Blender backdrop (bd_backdrop.py) and writes the GIFs,
strips, greyscale sheet, reduce-effects still and contact sheet into ../

  python bd_render.py <backdrop.png>

Everything is drawn at 2x (SS) and downsampled for anti-aliasing. All randomness is
random.Random(seed) per variant, so reruns match byte for byte.
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageEnhance, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(OUT, "..", "..", ".."))
FONT_MONO = os.path.join(REPO, "assets", "fonts", "ShareTechMono-Regular.ttf")
FONT_HEAD = os.path.join(REPO, "assets", "fonts", "Anton-Regular.ttf")
BACKDROP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "backdrop.png")

SS = 2
W, H = 640, 480                 # final frame size
SW, SH = W * SS, H * SS
FPS = 30
DT = 1.0 / FPS
EFFECT_FRAMES = 18              # 0.6 s (T2 cap)
PRE_FRAMES = 3                  # attack projectile arriving
HOLD_FRAMES = 10                # end state held so the loop reads

# palette (ART_BIBLE 3)
PINK = (255, 61, 168); CYAN = (92, 225, 255); GAIN = (123, 224, 123); HARM = (255, 68, 51)
VIOLET = (200, 90, 255); DEPLOY = (176, 140, 255); ACID = (212, 255, 0)
TEXT_HI = (242, 246, 255); TEXT_MID = (175, 192, 214); METAL = (52, 56, 62); DESK = (27, 29, 33)
WHITE = (255, 255, 255)

CX, CY = int(SW * 0.42), int(SH * 0.47)    # spinner centre (left of centre: the burst has room)
R_OUT, R_IN, R_HUB = 200, 120, 88
R_HP = 236                          # HP arc radius
HP_A0, HP_A1 = 148.0, 32.0          # arc runs left (full end) -> right, screen degrees (y down)
HP_MAX, HP_SEGS = 60, 20
HIT_ANGLE = -30.0                   # impact on the upper-right rim

_font_cache = {}


def font(path, size):
    k = (path, size)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, size)
    return _font_cache[k]


def pol(r, a_deg, cx=CX, cy=CY):
    a = math.radians(a_deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_in3(t):
    return t * t * t


def ease_out2(t):
    return 1 - (1 - t) * (1 - t)


# ---------------------------------------------------------------- static scene layers
def make_backdrop():
    im = Image.open(BACKDROP).convert("RGB")
    # crop a 4:3 window and scale to SS size
    w, h = im.size
    cw = int(h * 4 / 3)
    im = im.crop(((w - cw) // 2, 0, (w - cw) // 2 + cw, h)).resize((SW, SH), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.35)          # desaturate (feedback 3)
    im = ImageEnhance.Brightness(im).enhance(0.8)     # combat dims the city (ART_BIBLE 9.1)
    im = im.filter(ImageFilter.GaussianBlur(3 * SS))
    scrim = Image.new("RGB", (SW, SH), (2, 3, 10))
    im = Image.blend(im, scrim, 0.22)
    # a soft vignette around the wheel region
    vig = Image.new("L", (SW, SH), 0)
    ImageDraw.Draw(vig).ellipse((CX - 520, CY - 480, CX + 520, CY + 560), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    dark = Image.new("RGB", (SW, SH), (0, 0, 0))
    return Image.composite(im, dark, vig.point(lambda v: 90 + v * 165 // 255))


SLICES = [PINK, CYAN, PINK, VIOLET, GAIN, PINK, CYAN, DEPLOY]


def draw_spinner(img):
    """Coloured slice ring with bezel, glass rim and hub; matches the current game wheel."""
    d = ImageDraw.Draw(img, "RGBA")
    # drop shadow
    sh = Image.new("L", (SW, SH), 0)
    ImageDraw.Draw(sh).ellipse((CX - R_OUT - 20, CY - R_OUT - 4, CX + R_OUT + 20, CY + R_OUT + 44), fill=170)
    sh = sh.filter(ImageFilter.GaussianBlur(24))
    img.paste((0, 0, 0), (0, 0), sh)
    d = ImageDraw.Draw(img, "RGBA")
    # bezel
    d.ellipse((CX - R_OUT - 18, CY - R_OUT - 18, CX + R_OUT + 18, CY + R_OUT + 18), fill=DESK + (255,), outline=METAL + (255,), width=6)
    # slices
    n = len(SLICES)
    for i, c in enumerate(SLICES):
        a0 = -90 + i * 360 / n; a1 = a0 + 360 / n
        dark = tuple(int(v * 0.55) for v in c)
        d.pieslice((CX - R_OUT, CY - R_OUT, CX + R_OUT, CY + R_OUT), a0, a1, fill=dark + (255,))
        d.arc((CX - R_OUT + 6, CY - R_OUT + 6, CX + R_OUT - 6, CY + R_OUT - 6), a0 + 1, a1 - 1, fill=c + (255,), width=10)
    for i in range(n):
        a = -90 + i * 360 / n
        d.line([pol(R_IN - 4, a), pol(R_OUT + 2, a)], fill=(8, 8, 12, 255), width=7)
    # tick ring (30 ticks)
    for k in range(30):
        a = -90 + k * 12
        d.line([pol(R_OUT + 4, a), pol(R_OUT + 14, a)], fill=TEXT_MID + (150,), width=3)
    # inner ring + hub
    d.ellipse((CX - R_IN, CY - R_IN, CX + R_IN, CY + R_IN), fill=(10, 12, 18, 255), outline=CYAN + (120,), width=3)
    d.ellipse((CX - R_HUB, CY - R_HUB, CX + R_HUB, CY + R_HUB), fill=(14, 18, 26, 255), outline=PINK + (200,), width=5)
    # glass sheen: a pale crescent on the upper left
    sheen = Image.new("L", (SW, SH), 0)
    sd = ImageDraw.Draw(sheen)
    sd.ellipse((CX - R_OUT, CY - R_OUT, CX + R_OUT, CY + R_OUT), fill=40)
    sd.ellipse((CX - R_OUT + 40, CY - R_OUT + 50, CX + R_OUT + 40, CY + R_OUT + 50), fill=0)
    sheen = sheen.filter(ImageFilter.GaussianBlur(10))
    img.paste(WHITE, (0, 0), sheen)
    d = ImageDraw.Draw(img, "RGBA")
    f = font(FONT_MONO, 24)
    for j, s in enumerate(["COLLECTIONS", "AGENT"]):
        tw = d.textlength(s, font=f)
        d.text((CX - tw / 2, CY - 28 + j * 30), s, font=f, fill=TEXT_HI)
    # pointer notch at the top
    d.polygon([(CX, CY - R_OUT - 8), (CX - 16, CY - R_OUT - 40), (CX + 16, CY - R_OUT - 40)], fill=TEXT_HI)


def seg_angles(i):
    span = (HP_A0 - HP_A1) / HP_SEGS
    a0 = HP_A0 - i * span
    return a0 - span + 1.6, a0 - 1.6      # pieslice/arc wants ascending


def seg_centre(i):
    a0, a1 = seg_angles(i)
    return pol(R_HP, (a0 + a1) / 2)


def draw_hp(img, hp_shown, lag_hp, flash_segs, flash_a, heal=False, chip=None, chip_a=0.0):
    """Segmented HP arc under the wheel. Segments above hp_shown up to lag_hp draw white (the
    trailing lag segment); flash_segs get an extra white flash of alpha flash_a."""
    d = ImageDraw.Draw(img, "RGBA")
    per = HP_MAX / HP_SEGS
    box = (CX - R_HP, CY - R_HP, CX + R_HP, CY + R_HP)
    for i in range(HP_SEGS):
        a0, a1 = seg_angles(i)
        top = (i + 1) * per
        if hp_shown >= top - 1e-6:
            col = GAIN + (255,)
        elif hp_shown > i * per:
            col = GAIN + (255,)   # partial: draw full, marker below trims
        elif lag_hp > i * per:
            col = (255, 255, 255, 220)
        else:
            col = (60, 70, 80, 200)
        d.arc(box, a0, a1, fill=col, width=24)
        if i in flash_segs and flash_a > 0:
            d.arc((box[0] - 6, box[1] - 6, box[2] + 6, box[3] + 6), a0 - 1, a1 + 1, fill=(255, 255, 255, int(255 * flash_a)), width=30)
    # number
    f = font(FONT_HEAD, 56)
    s = "%d/%d" % (round(hp_shown), HP_MAX)
    tw = d.textlength(s, font=f)
    x, y = CX - tw / 2, CY + R_HP + 20
    d.text((x + 3, y + 3), s, font=f, fill=(0, 0, 0, 200))
    d.text((x, y), s, font=f, fill=GAIN if heal else TEXT_HI)
    if chip and chip_a > 0:
        draw_chip(img, chip, x + tw + 24, y + 6, chip_a, heal)


def draw_chip(img, text, x, y, a, heal=False, scale=1.0):
    d = ImageDraw.Draw(img, "RGBA")
    f = font(FONT_HEAD, int(44 * scale))
    tw = d.textlength(text, font=f)
    pad = 12 * scale
    col = GAIN if heal else HARM
    d.rounded_rectangle((x, y, x + tw + 2 * pad, y + 58 * scale), radius=8 * scale, fill=(10, 10, 14, int(230 * a)), outline=col + (int(255 * a),), width=int(4 * scale))
    d.text((x + pad, y + 2 * scale), text, font=f, fill=col + (int(255 * a),))
    return tw + 2 * pad


# ---------------------------------------------------------------- glyph sprites
_sprite_cache = {}


def text_sprite(s, size, col):
    k = (s, size, col)
    if k not in _sprite_cache:
        f = font(FONT_MONO, size)
        l, t, r, b = f.getbbox(s)
        im = Image.new("RGBA", (r - l + 8, b - t + 8), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((4 - l, 4 - t), s, font=f, fill=col + (255,), stroke_width=max(1, size // 22), stroke_fill=col + (255,))
        _sprite_cache[k] = im
    return _sprite_cache[k]


def stamp(layer, s, size, col, x, y, rot, alpha, sx=1.0):
    if alpha <= 0.01 or size < 4:
        return
    sp = text_sprite(s, size, col)
    if sx != 1.0:
        sp = sp.resize((max(1, int(sp.width * sx)), sp.height), Image.BILINEAR)
    sp = sp.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = sp.getchannel("A").point(lambda v: int(v * alpha))
        sp = sp.copy(); sp.putalpha(a)
    layer.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))


# ---------------------------------------------------------------- particles
class Shard:
    def __init__(s, **kw):
        s.__dict__.update(kw)


def free_pos(sh, t):
    """Closed-form flight with linear drag k and gravity g (screen y down)."""
    k, g = sh.drag, sh.grav
    e = math.exp(-k * t)
    x = sh.x0 + sh.vx / k * (1 - e)
    y = sh.y0 + (sh.vy + g / k) / k * (1 - e) - g / k * t
    return x, y


def shard_state(sh, t):
    """Returns (x, y, alpha, scale, rot) or None when not alive."""
    lt = t - sh.t0
    if lt < 0:
        return None
    if sh.mode == "attract":
        fx, fy = free_pos(sh, min(lt, sh.ta))
        if lt <= sh.ta:
            a = 1.0 if lt < 0.08 else lerp(1.0, 0.55, clamp((lt - 0.08) / max(0.01, sh.ta - 0.08)))
            return fx, fy, a, 1.0, sh.rot0 + sh.spin * lt
        u = (lt - sh.ta) / sh.da
        if u >= 1:
            return None
        w = ease_in3(u)
        # bend the path: a sideways bulge so the suck reads as a curve, not a straight cut
        tx, ty = sh.tx, sh.ty
        a_f = math.atan2(fy - CY, fx - CX); a_t = math.atan2(ty - CY, tx - CX)
        da_ = (a_t - a_f + math.pi) % (2 * math.pi) - math.pi
        mx, my = pol(max(R_OUT * 1.5, math.hypot(fx - CX, fy - CY) * 1.05) + sh.bulge[0], math.degrees(a_f + da_ * 0.5))
        x = (1 - w) ** 2 * fx + 2 * (1 - w) * w * mx + w * w * tx
        y = (1 - w) ** 2 * fy + 2 * (1 - w) * w * my + w * w * ty
        return x, y, lerp(0.55, 0.95, u), lerp(1.0, 0.45, w), sh.rot0 + sh.spin * (sh.ta + (lt - sh.ta) * 0.3)
    if sh.mode == "die":          # bounced / spent shards: fly, fade, gone
        if lt > sh.life:
            return None
        x, y = free_pos(sh, lt)
        return x, y, (1 - lt / sh.life) ** 1.5 * sh.a0, 1.0, sh.rot0 + sh.spin * lt
    if sh.mode == "inflow":       # heal: from outside to the bar
        u = lt / sh.da
        if u >= 1:
            return None
        w = ease_in3(u) * 0.6 + u * 0.4
        x = (1 - w) ** 2 * sh.x0 + 2 * (1 - w) * w * sh.mx + w * w * sh.tx
        y = (1 - w) ** 2 * sh.y0 + 2 * (1 - w) * w * sh.my + w * w * sh.ty
        a = 0.5 + 0.5 * clamp(u / 0.2)
        return x, y, a, lerp(1.0, 0.6, w * w), sh.rot0 + sh.spin * lt
    if sh.mode == "streak":       # crit code streaks: straight, velocity-aligned, then shatter
        if lt > sh.tb:
            return None
        x, y = free_pos(sh, lt)
        return x, y, 1.0, 1.0, sh.rot0
    return None


def arrival_time(sh):
    if sh.mode == "attract":
        return sh.t0 + sh.ta + sh.da
    if sh.mode == "inflow":
        return sh.t0 + sh.da
    return None


def drained_segments(hp_from, hp_to):
    per = HP_MAX / HP_SEGS
    lo, hi = min(hp_from, hp_to), max(hp_from, hp_to)
    return [i for i in range(HP_SEGS) if (i + 1) * per > lo + 1e-6 and i * per < hi - 1e-6]


def attract_targets(rng, segs):
    """Arrival points spread over the affected segments (slightly inside the arc)."""
    i = rng.choice(segs)
    a0, a1 = seg_angles(i)
    return pol(R_HP + rng.uniform(-6, 6), rng.uniform(a0, a1))


def spawn_hit(rng, dmg, t0=0.0, chars="01", colour=PINK, spread=75, speed=(650, 1450), count=None, size=None,
              ta_base=0.19, da=0.19, px=None, py=None, normal=None, segs=None):
    n = count if count is not None else int(8 + 1.4 * dmg)
    sz = size if size is not None else int(min(76, 36 + 1.8 * dmg))
    hx, hy = (px, py) if px is not None else pol(R_OUT + 4, HIT_ANGLE)
    nrm = normal if normal is not None else HIT_ANGLE
    out = []
    for i in range(n):
        ang = math.radians(nrm + rng.uniform(-spread, spread))
        sp = rng.uniform(*speed)
        tx, ty = attract_targets(rng, segs)
        side = rng.choice([-1, 1])
        out.append(Shard(mode="attract", ch=rng.choice(chars), size=int(sz * rng.uniform(0.7, 1.15)), col=colour,
                         x0=hx + rng.uniform(-10, 10), y0=hy + rng.uniform(-10, 10),
                         vx=math.cos(ang) * sp, vy=math.sin(ang) * sp, drag=4.5, grav=520.0,
                         rot0=rng.uniform(-30, 30), spin=rng.uniform(-900, 900),
                         t0=t0 + rng.uniform(0, 0.03), ta=ta_base + (i / max(1, n - 1)) * 0.10 + rng.uniform(0, 0.02),
                         da=da, tx=tx, ty=ty, bulge=(rng.uniform(0, 70), 0)))
    return out


# ---------------------------------------------------------------- variants
VARIANTS = {}


def variant(fn):
    VARIANTS[fn.__name__] = fn
    return fn


@variant
def hit(rng):
    segs = drained_segments(48, 41)
    return dict(hp_from=48, hp_to=41, chip="-7", shards=spawn_hit(rng, 7, segs=segs), segs=segs,
                flash_a=0.5, shake=2, label="01  HIT  -7", proj=PINK)


@variant
def big_hit(rng):
    segs = drained_segments(48, 30)
    return dict(hp_from=48, hp_to=30, chip="-18", shards=spawn_hit(rng, 18, speed=(450, 2000), spread=100, segs=segs),
                segs=segs, flash_a=0.6, shake=2, label="02  BIG HIT  -18", proj=PINK, proj_w=16)


@variant
def crit(rng):
    segs = drained_segments(48, 34)
    hx, hy = pol(R_OUT + 4, HIT_ANGLE)
    shards = []
    codes = ["0110 1001", "1011 0010", "0101 1110", "1100 1010", "0011 0111", "1001 0110", "1110 0001"]
    n_rays = 7
    for i in range(n_rays):
        ang = HIT_ANGLE - 105 + i * 210 / (n_rays - 1) + rng.uniform(-8, 8)
        sp = rng.uniform(1300, 1700)
        a = math.radians(ang)
        code = codes[i % len(codes)]
        shards.append(Shard(mode="streak", code=code, size=40, col=PINK, x0=hx, y0=hy,
                            vx=math.cos(a) * sp, vy=math.sin(a) * sp, drag=7.0, grav=0.0,
                            rot0=-ang, spin=0, t0=0.0, tb=0.17, ang=ang))
    # each streak shatters into its own glyphs at tb, which then tumble and get sucked in
    kids = []
    for st in shards:
        x, y = free_pos(st, st.tb)
        a = math.radians(st.ang)
        chars = [c for c in st.code if c != " "]
        for j, c in enumerate(chars):
            off = (j - len(chars) / 2) * 22
            sp = rng.uniform(120, 380)
            b = a + rng.uniform(-1.2, 1.2)
            tx, ty = attract_targets(rng, segs)
            kids.append(Shard(mode="attract", ch=c, size=int(40 * rng.uniform(0.8, 1.1)), col=PINK,
                              x0=x + math.cos(a) * off, y0=y + math.sin(a) * off,
                              vx=math.cos(b) * sp, vy=math.sin(b) * sp, drag=4.0, grav=400.0,
                              rot0=-st.ang, spin=rng.uniform(-700, 700), t0=st.tb,
                              ta=0.06 + rng.uniform(0, 0.12), da=0.2, tx=tx, ty=ty,
                              bulge=(rng.uniform(0, 70), 0)))
    return dict(hp_from=48, hp_to=34, chip="-14", shards=shards + kids, segs=segs, flash_a=0.6, shake=2,
                label="03  CRIT  -14", proj=PINK, proj_w=14, cracks=True, cracks_rng=random.Random(rng.random()))


@variant
def blocked(rng):
    segs = drained_segments(48, 46)
    # shield sits 60 px out from the rim, facing the attacker
    shx, shy = pol(R_OUT + 70, HIT_ANGLE)
    shards = []
    for i in range(22):     # bounce off the shield face: back the way they came, dim, never arrive
        ang = math.radians(HIT_ANGLE + rng.uniform(-80, 80))
        sp = rng.uniform(450, 1050)
        shards.append(Shard(mode="die", ch=rng.choice("01"), size=int(38 * rng.uniform(0.75, 1.1)), col=PINK,
                            x0=shx + rng.uniform(-40, 40), y0=shy + rng.uniform(-40, 40),
                            vx=math.cos(ang) * sp, vy=math.sin(ang) * sp, drag=4.0, grav=900.0,
                            rot0=rng.uniform(-40, 40), spin=rng.uniform(-1200, 1200),
                            t0=rng.uniform(0, 0.05), life=rng.uniform(0.3, 0.45), a0=0.8))
    # the few that get through: smaller, dimmer, from the wheel side of the shield
    px, py = pol(R_OUT + 6, HIT_ANGLE)
    through = spawn_hit(rng, 2, count=4, size=30, speed=(150, 350), spread=40, px=px, py=py,
                        t0=0.08, ta_base=0.12, da=0.22, segs=segs)
    return dict(hp_from=48, hp_to=46, chip="-2", shards=shards + through, segs=segs, flash_a=0.35, shake=1,
                label="04  BLOCKED  -2  (5 soaked)", proj=PINK, shield=(shx, shy))


@variant
def heal(rng):
    segs = drained_segments(30, 36)
    shards = []
    n = 16
    for i in range(n):
        tx, ty = attract_targets(rng, segs)
        # start outside the wheel, below and to the sides, off the arc
        side = -1 if i % 2 == 0 else 1
        sx = CX + side * rng.uniform(300, 470)
        sy = CY + rng.uniform(40, 320)
        mx = lerp(sx, tx, 0.5) + side * rng.uniform(20, 80)
        my = max(sy, ty) + rng.uniform(40, 140)
        shards.append(Shard(mode="inflow", ch=rng.choice("01" * 3 + "+"), size=int(50 * rng.uniform(0.8, 1.15)), col=GAIN,
                            x0=sx, y0=sy, mx=mx, my=my, tx=tx, ty=ty, rot0=0.0,
                            spin=rng.uniform(-80, 80), t0=(i / (n - 1)) * 0.24, da=rng.uniform(0.26, 0.32)))
    return dict(hp_from=30, hp_to=36, chip="+6", shards=shards, segs=segs, flash_a=0.45, shake=0,
                label="05  HEAL  +6", proj=None, heal=True)


# ---------------------------------------------------------------- frame renderer
def render_frame(base, v, f, reduce=False):
    """f counts from -PRE_FRAMES; the effect runs f = 0 .. EFFECT_FRAMES-1."""
    t = f * DT
    img = base.copy().convert("RGBA")
    heal_v = v.get("heal", False)
    shards = v["shards"]
    arrivals = sorted(a for a in (arrival_time(s) for s in shards) if a is not None)
    n_arr = len(arrivals)
    got = sum(1 for a in arrivals if a <= t) if not reduce else n_arr
    frac = got / n_arr if n_arr else 1.0
    if reduce:
        frac = 1.0
    hp_from, hp_to = v["hp_from"], v["hp_to"]
    hp_shown = lerp(hp_from, hp_to, frac) if t >= 0 else hp_from
    # white lag: damage lag trails the drop by ~0.12 s; heal has none
    if heal_v:
        lag = hp_shown
    else:
        last = arrivals[-1] if arrivals else 0
        lag = hp_from if t < last + 0.04 else lerp(hp_from, hp_to, clamp((t - last - 0.04) / 0.1))
        if reduce:
            lag = hp_to
    recent = [a for a in arrivals if t - DT < a <= t]
    flash_a = 0.0 if reduce else min(0.6, 0.25 * len(recent) + (0.3 if recent else 0.0))
    chip_a = 1.0 if reduce else clamp((t - (arrivals[0] if arrivals else 0)) / 0.08)
    if t < 0:
        chip_a = 0
    draw_hp(img, hp_shown, lag, set(v["segs"]) if recent else set(), flash_a, heal=heal_v,
            chip=v["chip"], chip_a=chip_a)

    fx = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))   # additive particle layer
    fd = ImageDraw.Draw(fx, "RGBA")
    hx, hy = pol(R_OUT + 4, HIT_ANGLE)
    if not reduce:
        # incoming attack streak (the existing hit_line, trimmed)
        if v.get("proj") and -PRE_FRAMES <= f <= 0:
            u = (f + PRE_FRAMES) / PRE_FRAMES
            sx, sy = pol(R_OUT + 900, HIT_ANGLE + 12)   # attacker off-frame, beyond the hit side
            ex, ey = lerp(sx, hx, u), lerp(sy, hy, u)
            bx, by = lerp(sx, hx, max(0, u - 0.45)), lerp(sy, hy, max(0, u - 0.45))
            fd.line([(bx, by), (ex, ey)], fill=v["proj"] + (230,), width=v.get("proj_w", 10))
            fd.ellipse((ex - 12, ey - 12, ex + 12, ey + 12), fill=WHITE + (255,))
        # local impact flash (<= 60 % alpha, element only, 2 frames)
        if 0 <= f <= 1 and not heal_v:
            r = 60 + 50 * f
            fd.ellipse((hx - r, hy - r, hx + r, hy + r), fill=WHITE + (int(150 if f == 0 else 70),))
        # crit: shattered-glass crack lines on the wheel glass (bible crit shape), 4 frames
        if v.get("cracks") and 0 <= f <= 5:
            cr = random.Random(11)
            a_fade = 1 - f / 6
            for k in range(9):
                ang = math.radians(HIT_ANGLE + 180 + cr.uniform(-70, 70))
                pts = [(hx, hy)]
                x, y = hx, hy
                for _ in range(4):
                    step = cr.uniform(25, 55)
                    ang += cr.uniform(-0.4, 0.4)
                    x += math.cos(ang) * step; y += math.sin(ang) * step
                    pts.append((x, y))
                fd.line(pts, fill=(255, 235, 245, int(230 * a_fade)), width=4)
        # blocked: translucent hex shield, pops in, ripples, fades
        if v.get("shield") and 0 <= f < EFFECT_FRAMES:
            sxc, syc = v["shield"]
            u = f / EFFECT_FRAMES
            a = (1.0 if u < 0.45 else 1 - (u - 0.45) / 0.55) * 0.9
            sc = 0.8 + 0.2 * ease_out2(clamp(f / 3))
            rr = 34 * sc
            nrm = math.radians(HIT_ANGLE)
            tan = (-math.sin(nrm), math.cos(nrm))
            cells = [(0, 0), (1, 0), (-1, 0), (2, 0), (-2, 0), (0.5, 1), (-0.5, 1), (1.5, 1), (-1.5, 1)]
            for (cx_, cy_) in cells:
                off = cx_ * rr * 1.75
                back = cy_ * rr * 1.5
                px = sxc + tan[0] * off - math.cos(nrm) * back
                py = syc + tan[1] * off - math.sin(nrm) * back
                dist = abs(cx_) + cy_
                ripple = clamp(1 - abs(f * 0.6 - dist)) if f < 8 else 0
                pts = [(px + rr * math.cos(math.radians(60 * k + 30)), py + rr * math.sin(math.radians(60 * k + 30))) for k in range(6)]
                fd.polygon(pts, fill=CYAN + (int(55 * a + 90 * ripple),), outline=CYAN + (int(230 * a),), width=4)
        # shards: trails first (two ghosts), then the glyph
        for s in shards:
            if s.mode == "streak":
                st = shard_state(s, t)
                if st is None:
                    continue
                x, y, a, scl, rot = st
                for g, ga in ((2, 0.25), (1, 0.5)):
                    pst = shard_state(s, t - g * DT * 0.5)
                    if pst:
                        stamp(fx, s.code, s.size, s.col, pst[0], pst[1], rot, ga)
                stamp(fx, s.code, s.size, WHITE, x, y, rot, 1.0)
                continue
            st = shard_state(s, t)
            if st is None:
                continue
            x, y, a, scl, rot = st
            sz = int(s.size * scl)
            for g, ga in ((2, 0.10), (1, 0.22)):
                pst = shard_state(s, t - g * DT * 0.5)
                if pst:
                    stamp(fx, s.ch, int(s.size * pst[3]), s.col, pst[0], pst[1], pst[4], pst[2] * ga)
            stamp(fx, s.ch, sz, s.col, x, y, rot, a)
            # a hot white core on fresh shards so they read bright in greyscale
            if t - s.t0 < 0.1:
                stamp(fx, s.ch, max(4, sz - 4), WHITE, x, y, rot, a * (1 - (t - s.t0) / 0.1))

    # glow: blur the particle layer and add it, then the sharp layer on top
    glow = fx.filter(ImageFilter.GaussianBlur(6 * SS))
    rgb = img.convert("RGB")
    gl = Image.new("RGB", (SW, SH), (0, 0, 0)); gl.paste(glow.convert("RGB"), (0, 0), glow.getchannel("A"))
    rgb = ImageChops.add(rgb, ImageEnhance.Brightness(gl).enhance(0.85))
    # (one additive pass: two blew dense bursts out into blobs)
    img = rgb.convert("RGBA"); img.alpha_composite(fx)
    # shake: 1-2 px (T2), frames 0-1, whole element
    sh = 0 if reduce else v.get("shake", 0)
    if sh and 0 <= f <= 1:
        img = ImageChops.offset(img, sh * SS * (1 if f == 0 else -1), -sh * SS * (1 if f == 0 else 0))
    out = img.convert("RGB").resize((W, H), Image.LANCZOS)
    return out


def caption(im, text, sub):
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((0, 0, W, 30), fill=(0, 0, 0, 170))
    d.text((10, 5), text, font=font(FONT_MONO, 18), fill=TEXT_HI)
    f = font(FONT_MONO, 16)
    d.text((W - 10 - d.textlength(sub, font=f), 7), sub, font=f, fill=PINK)
    return im


def build_variant(name, base, seed):
    rng = random.Random(seed)
    v = VARIANTS[name](rng)
    frames = []
    for f in range(-PRE_FRAMES, EFFECT_FRAMES + HOLD_FRAMES):
        im = render_frame(base, v, min(f, EFFECT_FRAMES + 2))
        ms = int(round(f * 1000 / FPS))
        sub = ("%+d ms" % ms) if f < EFFECT_FRAMES else "end state"
        frames.append((f, caption(im, v["label"] + "   T2", sub)))
    return v, frames


def save_gif(frames, path):
    pal = [im.convert("P", palette=Image.ADAPTIVE, colors=128, dither=Image.Dither.NONE) for _, im in frames]
    durs = [33] * len(pal)
    durs[-1] = 600
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=durs, loop=0, optimize=True, disposal=1)


STRIP_PICK = [-1, 0, 2, 4, 6, 9, 12, 15]


def save_strip(frames, path, grey=False):
    by = dict(frames)
    tw, th = 400, 300
    strip = Image.new("RGB", (tw * len(STRIP_PICK) + 8 * (len(STRIP_PICK) + 1), th + 48), (8, 8, 12))
    d = ImageDraw.Draw(strip)
    for i, f in enumerate(STRIP_PICK):
        im = by[f].resize((tw, th), Image.LANCZOS)
        if grey:
            im = ImageOps.grayscale(im).convert("RGB")
        x = 8 + i * (tw + 8)
        strip.paste(im, (x, 8))
        d.text((x + 4, th + 14), "f%02d  %+d ms" % (f, round(f * 1000 / FPS)), font=font(FONT_MONO, 22), fill=TEXT_HI)
    strip.save(path, optimize=True)
    return strip


def main():
    base = make_backdrop().convert("RGBA")
    draw_spinner(base)
    base = base.convert("RGB")
    names = [("hit", "01_hit"), ("big_hit", "02_big_hit"), ("crit", "03_crit"), ("blocked", "04_blocked"), ("heal", "05_heal")]
    peaks = {"hit": 5, "big_hit": 5, "crit": 3, "blocked": 4, "heal": 7}
    greys, strips = [], []
    for i, (name, fn) in enumerate(names):
        v, frames = build_variant(name, base, 1000 + i)
        save_gif(frames, os.path.join(OUT, fn + ".gif"))
        strips.append(save_strip(frames, os.path.join(OUT, fn + "_strip.png")))
        greys.append((v["label"], ImageOps.grayscale(dict(frames)[peaks[name]]).convert("RGB")))
        print("wrote", fn)
    # 06 greyscale: one peak frame each
    gw = W * len(greys) + 10 * (len(greys) + 1)
    g = Image.new("RGB", (gw, H + 60), (8, 8, 8))
    d = ImageDraw.Draw(g)
    for i, (lab, im) in enumerate(greys):
        g.paste(im, (10 + i * (W + 10), 10))
        d.text((10 + i * (W + 10), H + 20), lab + " (greyscale, peak frame)", font=font(FONT_MONO, 20), fill=(230, 230, 230))
    g.save(os.path.join(OUT, "06_greyscale.png"), optimize=True)
    # 07 reduce effects: the end state, a static chip, no particles, no flash, no shake
    rng = random.Random(1000)
    v = VARIANTS["hit"](rng)
    im = render_frame(base, v, EFFECT_FRAMES + 2, reduce=True)
    im = caption(im, "07  REDUCE EFFECTS: end state only", "no particles")
    panel = Image.new("RGB", (W + 360, H), (10, 10, 14))
    panel.paste(im, (0, 0))
    big = Image.new("RGBA", ((360) * SS, H * SS), (10, 10, 14, 255))
    bd = ImageDraw.Draw(big)
    bd.text((24 * SS, 24 * SS), "the same chips, other outcomes", font=font(FONT_MONO, 36), fill=TEXT_MID)
    y = 80 * SS
    for txt, heal_c, note in [("-7", False, "hit"), ("-18", False, "big hit"), ("-14", False, "crit (+ CRIT tag)"),
                              ("-2", False, "blocked (+ hex 5)"), ("+6", True, "heal")]:
        w = draw_chip(big, txt, 24 * SS, y, 1.0, heal_c, scale=1.2)
        bd.text((24 * SS + w + 24, y + 20), note, font=font(FONT_MONO, 34), fill=TEXT_HI)
        y += 80 * SS
    panel.paste(big.convert("RGB").resize((360, H), Image.LANCZOS), (W, 0))
    panel.save(os.path.join(OUT, "07_reduce_effects.png"), optimize=True)
    # contact sheet: five strips stacked, greyscale row, reduce still
    cw = strips[0].width
    rows = [s for s in strips]
    gs = g.resize((cw, int(g.height * cw / g.width)), Image.LANCZOS)
    rs = panel.resize((int(panel.width * 0.9), int(panel.height * 0.9)), Image.LANCZOS)
    total_h = 70 + sum(r.height + 10 for r in rows) + gs.height + 20 + rs.height + 20
    cs = Image.new("RGB", (cw, total_h), (6, 6, 10))
    d = ImageDraw.Draw(cs)
    d.text((16, 14), "REBEL_CELL  binary damage shards  (T2, 0.6 s @ 30 fps)   01 hit / 02 big hit / 03 crit / 04 blocked / 05 heal / 06 greyscale / 07 reduce effects",
           font=font(FONT_MONO, 34), fill=PINK)
    y = 70
    for r in rows:
        cs.paste(r, (0, y)); y += r.height + 10
    cs.paste(gs, (0, y)); y += gs.height + 20
    cs.paste(rs, (16, y))
    cs = cs.resize((cw // 2, total_h // 2), Image.LANCZOS)
    cs.save(os.path.join(OUT, "contact_sheet.jpg"), quality=86)
    print("done")


if __name__ == "__main__":
    main()
