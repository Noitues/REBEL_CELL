"""The single converged board: Breaker code base (family-C CRT slices + hub core) in the centre, the 3 wave rings as bible ring cells
around it, Meridian wave bezel outside. Rendered with the round41 slice renderer at master scale, then placed at K."""
import sys, os
sys.dont_write_bytecode = True
from cv_lib import *
import slicelib as SL_
import roster_wheel as RW_
import combat_wheel as CW_

SLC = {'BURST': ('ZERO-DAY', 'BURST'), 'SHIELD': ('SANDBOX', 'SHIELD'), 'TURRET': ('EXPLOIT', 'TURRET'), 'REPAIR': ('PATCH', 'REPAIR')}
import programs as _prg
_orig_tex = _prg.texture


def _tex(ctx):
    # Meridian bezel (ownership = kit, bible 2.3) around the programme's own screen (colour = type)
    if getattr(ctx, 'theme', '') == 'meridian' and ctx.prog in _prg.PLAYER:
        return _prg.PLAYER[ctx.prog](ctx)
    return _orig_tex(ctx)


_prg.texture = _tex
MS = 1300           # master canvas size
MC = 650            # master centre


def slice_value(w, cons):
    t = w['t']
    if t == 'BURST':
        return cons['BURST']
    if t == 'TURRET':
        return cons['TURRET']
    if t == 'REPAIR':
        return cons['REPAIR_HEAL']
    if t == 'SHIELD':
        a, b = cons['SHIELD_ABS'][0]
        return w['hp'] * a // b
    return 0


def ring_geom(d):
    r0 = RS['c0'] + RS['T'] * d
    return r0, r0 + RS['T']


HUB = {'name': 'Breaker', 'col': None}


def render_board(f, cons, ss=2, hot_cells=None, units=True, empties=True):
    """f = frame (wheel + units). Returns RGBA at screen size (W,H) with the board placed at C."""
    RW_.CW, RW_.CH, RW_.CX, RW_.CY = MS, MS, MC, MC
    canvas = np.zeros((MS * ss, MS * ss, 4), np.float32)
    # back plate: one dark disc under everything (visible in the gaps)
    yy, xx = np.mgrid[0:MS * ss, 0:MS * ss].astype(np.float32)
    rho = np.hypot(xx + 0.5 - MC * ss, yy + 0.5 - MC * ss) / ss
    bp = np.clip(RS['bz0'] / K - rho + 1, 0, 1)[..., None]
    canvas[..., :3] = np.array([0.020, 0.022, 0.034]) * bp
    canvas[..., 3:] = bp
    del yy, xx, rho
    acc = ORANGE
    # wave bezel (Meridian brushed ring)
    RW_.ring_base(canvas, ss, RS['bz0'] / K, RS['bz1'] / K, (0.17, 0.115, 0.075), acc, rim=1.4, brushed=True, seed=3)
    # code base slices (family C, upright read block)
    SL_.R_IN, SL_.R_OUT = RS['s0'] / K, RS['s1'] / K
    for s in range(6):
        w = f['wheel'][s]
        prog, _ = SLC[w['t']]
        val = slice_value(w, cons)
        SL_.render_slice(canvas, MC * ss, MC * ss, prog, 60 * s - 30, 60, val, (0.3 + 0.137 * s) % 1, 'player', ss,
                         dict(upright=True, rc=0.55, glyph_scale=1.0, tex_gain=0.9), seed=s + 3, glyph=('SHIELD' if w['t'] == 'SHIELD' else None))
    # wave ring cells: occupied = screen of the unit's programme (family C, Meridian bezel), empty = dark glass (drawn on the overlay)
    occ = {}
    cover = set()
    for u in f['units']:
        occ[(u['dep'], u['s'])] = u
        for q in range(u.get('w', 1)):
            cover.add((u['dep'], (u['s'] + q) % 6))
    ad = f.get('adjuster')
    if ad:
        occ[(ad['ring'], ad['s'])] = dict(kind='Adjuster', hp=ad['hp'])
        cover.add((ad['ring'], ad['s']))
    for dep in range(3):
        ri, ro = ring_geom(dep)
        SL_.R_IN, SL_.R_OUT = ri / K, ro / K
        for s in range(6):
            u = occ.get((dep, s))
            if u is None or not units:
                continue
            prog = KIND[u['kind']][0]
            opts = dict(icons=False, glyph_scale=1.0, tex_gain=3.2)
            if u['kind'] == 'Adjuster':
                opts.update(boss=True, phase=1)
            wd = u.get('w', 1)
            SL_.render_slice(canvas, MC * ss, MC * ss, prog, 60 * s - 30, 60 * wd, None, (0.3 + 0.137 * (s + 6 * dep)) % 1,
                             'meridian', ss, opts, seed=s + 7 * dep + 3)
    SL_.R_IN, SL_.R_OUT = 130.0, 360.0
    # master overlay: empty ring cells (dark glass), hub core, code-base frame
    over = Image.new('RGBA', (MS * ss, MS * ss), (0, 0, 0, 0))
    glow = Image.new('RGBA', (MS * ss, MS * ss), (0, 0, 0, 0))
    d, gd = ImageDraw.Draw(over), ImageDraw.Draw(glow)
    for dep in range(3):
        ri, ro = ring_geom(dep)
        for s in range(6):
            if (dep, s) in cover or not empties:
                continue
            poly = RW_.arc_poly(ri / K + 3, ro / K - 3, 60 * s - 28.5, 60 * s + 28.5, ss, 16)
            d.polygon(poly, fill=(9, 14, 26, 232), outline=tuple(int(v * 0.40) for v in acc) + (255,))
    # code base frame: thin player-colour ring at the slice edge
    FC = HUB['col'] or PINK
    for rr, col in ((RS['s1'] / K + 2, FC), (RS['hp0'] / K - 1, FC)):
        bb = [(MC - rr) * ss, (MC - rr) * ss, (MC + rr) * ss, (MC + rr) * ss]
        d.ellipse(bb, outline=tuple(int(v * 0.8) for v in col) + (255,), width=ss)
    RW_.draw_hub(over, d, gd, ss, RS['hub'] / K, FC, RW_.CLASS_STYLE['breaker']['emblem'], HUB['name'], '')
    glow = glow.filter(ImageFilter.GaussianBlur(7 * ss))
    g = np.asarray(glow, np.float32) / 255
    o = np.asarray(over, np.float32) / 255
    canvas[..., :3] += g[..., :3] * g[..., 3:] * 0.9
    canvas[..., 3:] = np.maximum(canvas[..., 3:], g[..., 3:] * 0.9)
    oa = o[..., 3:]
    canvas[..., :3] = canvas[..., :3] * (1 - oa) + o[..., :3] * oa
    canvas[..., 3:] = canvas[..., 3:] * (1 - oa) + oa
    im = Image.fromarray((np.clip(canvas, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA')
    n = int(MS * K)
    im = im.resize((n, n), Image.LANCZOS)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.alpha_composite(im, (int(C[0] - n / 2), int(C[1] - n / 2)))
    return out


if __name__ == '__main__':
    S = load_state()
    f = S['f1']
    bg = backdrop()
    b = render_board(f, S['consts'])
    shadow_paste(bg, b, (0, 0), k=0.0)
    bg.convert('RGB').save(ROOT + 'scratch_board.png')
    print('ok')
