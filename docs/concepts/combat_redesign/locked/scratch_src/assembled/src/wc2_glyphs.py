"""wheel_core R2 glyphs (512 grid masks, registered in crests15.CUSTOM).
Elements: icon_burst, icon_turret (WC2_BURST_*, WC2_TURRET_*), icon_repair (WC2_REPAIR_*), hub_emblem (WC2_CREST).
Shared-library imports (cards own them): wc2_kglyph (copy of cards kglyph.py) gives KA_brace, KA_spin1/2/3 (Spin = arrow ring cut into N).
Rules (R1 rulings 5, X9): white silhouette + 7.5% ink, 2-3 parts + streaks; bullets tilt 35 deg, staggered 4 px at 44 px, 2 streaks each;
repair = ONE strip at 20 deg with pad + perforations (never an X); Breaker crest = cracked ring."""
import sys, math
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw
import bb_lib  # noqa  (sets sys.path)
import crests15
import kglyph2  # noqa: F401  (asm: master library)

S = 512
SS = 2
STAGGER_UNITS = 4.0 * 512 / 44.0      # 4 px at the 44 px slice size


def _new():
    m = Image.new('L', (S * SS, S * SS), 0)
    return m, ImageDraw.Draw(m)


def _bullet_group(streaks=2, w=108, body=250, tip=84):
    """one upright bullet (tip up) with a base band and `streaks` streaks behind it, centred on (256,256)."""
    m, d = _new()
    k = SS
    cx = 256
    top = 256 - (tip + body + 34 + 96) / 2 + 20
    r = w / 2
    # ogive tip: polygon with curved flanks
    pts = []
    for i in range(0, 13):
        t = i / 12
        x = r * (1 - (1 - t) ** 1.8) if False else r * math.sin(t * math.pi / 2)
        y = top + tip * (1 - math.cos(t * math.pi / 2)) * 0 + tip * (1 - t) ** 1.0 * 0
        pts.append((x, y))
    # simple ogive: half-ellipse tip + rectangle body
    d.pieslice([(cx - r) * k, top * k, (cx + r) * k, (top + 2 * tip) * k], 180, 360, fill=255)
    d.rectangle([(cx - r) * k, (top + tip) * k, (cx + r) * k, (top + tip + body) * k], fill=255)
    band_y = top + tip + body + 14
    d.rectangle([(cx - r - 10) * k, band_y * k, (cx + r + 10) * k, (band_y + 34) * k], fill=255)
    sy0 = band_y + 34 + 18
    if streaks == 2:
        for sx in (-0.5, 0.5):
            x = cx + sx * (r * 1.0)
            d.rectangle([(x - 13) * k, sy0 * k, (x + 13) * k, (sy0 + 78) * k], fill=255)
    elif streaks == 1:
        d.rectangle([(cx - 13) * k, sy0 * k, (cx + 13) * k, (sy0 + 78) * k], fill=255)
    return m


def _place(g, ang, cx, cy):
    """rotate bullet group (PIL ccw degrees) about its centre and move its centre to (cx,cy)."""
    r = g.rotate(ang, resample=Image.BICUBIC, center=(256 * SS, 256 * SS))
    out = Image.new('L', g.size, 0)
    out.paste(r, (int((cx - 256) * SS), int((cy - 256) * SS)))
    return out


def _fit(m, margin=14):
    """scale the union so its bbox fills the 512 box (with margin), centred; returns 512 mask."""
    bb = m.getbbox()
    if not bb:
        return m.resize((S, S))
    c = m.crop(bb)
    sc_ = min((S - 2 * margin) * SS / c.width, (S - 2 * margin) * SS / c.height)
    c = c.resize((max(1, int(c.width * sc_)), max(1, int(c.height * sc_))), Image.LANCZOS)
    out = Image.new('L', (S * SS, S * SS), 0)
    out.paste(c, ((S * SS - c.width) // 2, (S * SS - c.height) // 2))
    return out.resize((S, S), Image.LANCZOS)


def _ucomb(*ms):
    out = ms[0]
    for m in ms[1:]:
        out = Image.composite(Image.new('L', out.size, 255), out, m)
    return out


# ------------------------------------------------------------------ BURST (two shots) / TURRET (one shot)
def burst_a():
    """twin bullets splayed outward (35 deg each way), right one 4 px lower; two streaks each"""
    g = _bullet_group(2)
    left = _place(g, 35, 118, 250)
    right = _place(g, -35, 394, 250 + STAGGER_UNITS)
    return _fit(_ucomb(left, right))


def burst_b():
    """twin bullets parallel, both tilted 35 deg clockwise, staggered 4 px along the axis"""
    g = _bullet_group(2)
    a = _place(g, -35, 182, 262)
    ox = math.sin(math.radians(35)) * STAGGER_UNITS * 0 ; 
    b = _place(g, -35, 330, 250 - STAGGER_UNITS)
    return _fit(_ucomb(a, b))


def turret_a():
    g = _bullet_group(2, w=124, body=270, tip=92)
    return _fit(_place(g, -35, 256, 256))


def turret_b():          # tilted the other way for twins' mirror (variant)
    g = _bullet_group(2, w=124, body=270, tip=92)
    return _fit(_place(g, 35, 256, 256))


# ------------------------------------------------------------------ REPAIR C: one wide strip at 20 deg, pad + perforations
def _strip(ang, pad=True, holes=True, thick=210):
    m, d = _new()
    k = SS
    d.rounded_rectangle([(20) * k, (256 - thick / 2) * k, (492) * k, (256 + thick / 2) * k], radius=thick / 2 * k, fill=255)
    if pad:
        d.rounded_rectangle([(166) * k, (256 - 92) * k, (346) * k, (256 + 92) * k], radius=20 * k, fill=0)
        d.rounded_rectangle([(194) * k, (256 - 62) * k, (318) * k, (256 + 62) * k], radius=10 * k, fill=255)
    if holes:
        for x in (70, 442):
            for y in (-52, 0, 52):
                d.ellipse([(x - 15) * k, (256 + y - 15) * k, (x + 15) * k, (256 + y + 15) * k], fill=0)
    return m.rotate(ang, resample=Image.BICUBIC, center=(256 * SS, 256 * SS))


def repair_c():
    return _fit(_strip(20), 6)


def repair_c_plain():     # variant: no perforations, thicker pad (reads at 16 px)
    return _fit(_strip(20, holes=False, thick=230), 6)


# ------------------------------------------------------------------ BREAKER crest = cracked ring
def crest():
    m, d = _new()
    k = SS
    d.ellipse([40 * k, 40 * k, 472 * k, 472 * k], fill=255)
    d.ellipse([132 * k, 132 * k, 380 * k, 380 * k], fill=0)
    zig = [(306, 14), (240, 188), (310, 226), (214, 334), (266, 372), (196, 500)]
    d.line([(x * k, y * k) for x, y in zig], fill=0, width=50 * k, joint='curve')
    for x, y in zig:
        d.ellipse([(x - 25) * k, (y - 25) * k, (x + 25) * k, (y + 25) * k], fill=0)
    d.ellipse([226 * k, 226 * k, 286 * k, 286 * k], fill=255)
    return m.resize((S, S), Image.LANCZOS)


for n, f in dict(WC2_BURST_A=burst_a, WC2_BURST_B=burst_b, WC2_TURRET_A=turret_a, WC2_TURRET_B=turret_b,
                 WC2_REPAIR_C=repair_c, WC2_REPAIR_P=repair_c_plain, WC2_CREST=crest).items():
    crests15.CUSTOM[n] = f
