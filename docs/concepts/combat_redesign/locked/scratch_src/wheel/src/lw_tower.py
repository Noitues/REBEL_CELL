"""lw_tower: the LOCKED player spinner = xerox flyer A (spot inks, toner, paper) + the linocut black key line and scissor-cut halo
+ Ben-Day bullseye rings on TURRET (replacing the xerox checker, which looked like the red hatch grid) + O-28 icon seats on every slice.
Layers (each one function, see NOTES.md):
  page()         pink scissor-cut halo, black key ring, paper disc
  draw_wedge()   jagged scissor-cut wedge: black key + drop, paper sliver, off-register ink, texture, stencil highlight
  draw_seat()    O-28 icon seat: solid slice-ink disc, paper scissor ring, black key ring (survives the hatch)
  draw_icon()    white stencil glyph with black key line, drop
  draw_break_state()  pending-loss hatch (hatch colour = cause) clears the seat, so the seat carries the slice type
  draw_hub()     pink starburst, black key, paper disc, bolt, ONE clean name tile
render_tower() is the assembler; HP ring, pips, brace, soak, margin marks and trim are the xerox/F1 functions, unchanged (game marks)."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from scipy import ndimage as ndi
from xf_gfx import *
import xf_slices as XS
import xf_tower as XT
import f1_tower as FT
from f1_lib import pol
from xf_tower import CT, TW, R_HUB, R_IN, R_OUT, ICON_R, hatch_cached, icon_masks
from xf_tower import draw_hp_ring, draw_pips, draw_brace_plate, draw_soak_mark, margin_marks

XT.VAR[0] = 'A'
WHITE_ = XT.WHITE_
PAGE_V = 0.86
KEY_W = 3.0           # black key line width (px)
SEAT_R = 28.6         # solid ink disc
SEAT_PAPER = 31.0     # scissor paper ring outer radius
SEAT_KEY = 33.6       # black key ring outer radius
SEAT_CLEAR = 37.0     # hatch / texture clearance radius
R_HALO, R_KEY, R_PAPER = 197.2, 192.0, 189.2

# ------------------------------------------------------------------ scissor-cut geometry
def jag_arc(c, r, a0, a1, rng, seg=(7, 14), amp=0.8):
    L = abs(math.radians(a1 - a0)) * r
    n = max(2, int(L / (0.5 * (seg[0] + seg[1]))))
    out = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        rr = r + (rng.uniform(-amp, amp) if 0 < i < n else 0.0)
        out.append(pol(c, rr, a))
    return out


def jag_path(p0, p1, rng, seg=(7, 14), amp=0.8):
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    n = max(2, int(L / (0.5 * (seg[0] + seg[1]))))
    nx, ny = -(p1[1] - p0[1]) / L, (p1[0] - p0[0]) / L
    out = []
    for i in range(n + 1):
        t = i / n
        j = rng.uniform(-amp, amp) if 0 < i < n else 0.0
        out.append((p0[0] + (p1[0] - p0[0]) * t + nx * j, p0[1] + (p1[1] - p0[1]) * t + ny * j))
    return out


def jag_ring(c, r, rng, seg=(7, 14), amp=1.0):
    return jag_arc(c, r, 0, 360, rng, seg, amp)[:-1]


def wedge_pts(s, rng, r0=R_IN, r1=R_OUT, half=26.0):
    am = 60 * s
    return (jag_arc(CT, r1, am - half, am + half, rng, (9, 17), 0.9)
            + jag_path(pol(CT, r1, am + half), pol(CT, r0, am + half), rng, (9, 15), 0.8)[1:]
            + jag_arc(CT, r0, am + half, am - half, rng, (8, 14), 0.7)[1:]
            + jag_path(pol(CT, r0, am - half), pol(CT, r1, am - half), rng, (9, 15), 0.8)[1:-1])


# ------------------------------------------------------------------ textures: xerox dots / scales / plus, Ben-Day bullseye rings
def tex_rings(cv, ic, p=9.0, w=2.8):
    X, Y = cv.grid()
    d = np.hypot(X - ic[0], Y - ic[1])
    dd = np.abs(((d + p / 2) % p) - p / 2)
    return np.clip(0.5 - (dd - w / 2) / 0.5, 0, 1).astype(np.float32)


def texture(kind, cv, am, ic):
    if kind == 'rings':
        return tex_rings(cv, ic)
    u, v = XS.frame(cv, 0 if kind == 'plus' else am, CT)
    if kind == 'dots':
        return XS.tex_dots(u, v)
    if kind == 'plus':
        return XS.tex_plus(u, v)
    return XS.tex_scales(u, v)


TEXKIND = {'BURST': 'dots', 'SHIELD': 'scales', 'TURRET': 'rings', 'REPAIR': 'plus'}
PAL = XS.PAL['A']


# ------------------------------------------------------------------ page: halo + key + paper
def page(cv, seed):
    ss = cv.ss
    rng = np.random.default_rng(seed + 100)
    c2 = (CT[0] + 0.9, CT[1] + 0.8)
    halo = poly(cv, jag_ring(c2, R_HALO, rng, (7, 15), 1.5))
    ink(cv, halo, MAG, 0.10, seed + 4)
    # chisel nicks across the halo
    nm = np.zeros((cv.H, cv.W), np.float32)
    for k in range(40):
        a = k * 9.0 + rng.uniform(-2.5, 2.5)
        p0, p1 = pol(CT, 192.5, a), pol(CT, 196.5 + rng.uniform(-0.4, 0.8), a + rng.uniform(-3, 3))
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy) + 1e-6
        nx, ny = -dy / L * 0.8, dx / L * 0.8
        nm = np.maximum(nm, poly(cv, [(p0[0] + nx, p0[1] + ny), (p1[0], p1[1]), (p0[0] - nx, p0[1] - ny)]))
    cv.paint(nm, TONER, 0.9)
    key = poly(cv, jag_ring(CT, R_KEY, rng, (6, 12), 0.8))
    cv.paint(key, TONER)
    pg = poly(cv, jag_ring(CT, R_PAPER, rng, (6, 12), 0.5))
    pg = rough(pg, cv, 0.5, 6.0, seed)
    X, Y = cv.grid()
    n = vnoise(cv.H, cv.W, 40 * ss, seed + 1, 3)
    rr = np.hypot(X - CT[0], Y - CT[1])
    shade = (0.93 + 0.07 * n) * (1 - 0.05 * np.clip((rr - 120) / 70, 0, 1))
    cv.paint(pg, SHEET[None, None, :] * PAGE_V * shade[..., None])
    sp = toner_noise(cv, seed + 7, 0.9, 0.86)
    cv.paint(blur(sp, 0.3 * ss) * pg, TONER, 0.34)
    return pg, None


# ------------------------------------------------------------------ slices
def wedge_mask(cv, s, seed):
    rng = np.random.default_rng(seed + 31 * s + 5)
    return poly(cv, wedge_pts(s, rng))


def draw_wedge(cv, w, seed):
    ss = cv.ss
    s = w['sector']
    am = 60 * s
    m = wedge_mask(cv, s, seed)
    # 1. black key plate + block drop toward the shadow side
    kb = grow(m, KEY_W * ss)
    cv.paint(extrude(kb, 3.6 * ss, 4.4 * ss), TONER)
    cv.paint(kb, TONER)
    # 2. the paper keyline: the sheet showing inside the key
    cv.paint(m, WHITE_ * 0.97)
    # 3. spot ink, slapped on off-register (paper sliver on one side, ink spilling over the key on the other)
    fillc, texc, texop = XS.palette('A', w['t'])
    mg = shift(m, -2.8 * ss, -2.3 * ss) * grow(m, 1.6 * ss)
    mg = np.clip(mg, 0, 1)
    ink(cv, mg, fillc, 0.11, seed + 21)
    # 4. texture, tone-on-tone, cleared around the seat and off the key edge
    ic = pol(CT, ICON_R, am)
    X, Y = cv.grid()
    to_icon = np.hypot(X - ic[0], Y - ic[1])
    tx = texture(TEXKIND[w['t']], cv, am, ic)
    tx = tx * np.clip((to_icon - (SEAT_KEY + 2.5)) / 5.0, 0, 1) * shrink(mg * m, 3.6 * ss)
    ink(cv, tx, texc, 0.04, seed + 22, texop)
    # 5. stencil highlight on the lit edge
    hl = np.clip(m - shift(m, 4.6 * ss, 5.0 * ss), 0, 1) * mg
    hl = hl * np.clip((to_icon - (SEAT_KEY + 2)) / 6.0, 0, 1)
    cv.paint(rough(hl, cv, 0.4, 5.0, seed + 23), WHITE_ * 0.9, 0.92)
    return m


# ------------------------------------------------------------------ O-28 icon seat + icon
def draw_seat(cv, w, seed):
    ss = cv.ss
    am = 60 * w['sector']
    ic = pol(CT, ICON_R, am)
    rng = np.random.default_rng(seed + 400 + w['sector'])
    fillc, texc, _ = XS.palette('A', w['t'])
    key = poly(cv, jag_ring(ic, SEAT_KEY, rng, (6, 10), 0.5))
    pap = poly(cv, jag_ring(ic, SEAT_PAPER, rng, (6, 10), 0.45))
    dsc = poly(cv, jag_ring((ic[0] - 0.8, ic[1] - 0.7), SEAT_R, rng, (6, 10), 0.35))
    cv.paint(extrude(key, 2.4 * ss, 2.8 * ss), TONER)
    cv.paint(key, TONER)
    cv.paint(pap, WHITE_ * 0.97)
    ink(cv, dsc, fillc, 0.05, seed + 41 + w['sector'])
    # darker offset print inside the disc (the misregistered second pass)
    inner = shrink(dsc, 1.0 * ss)
    cv.paint(np.clip(inner - shift(inner, -2.6 * ss, -2.4 * ss), 0, 1) * inner, texc, 0.55)


def draw_icon(cv, w):
    ss = cv.ss
    am = 60 * w['sector']
    c = pol(CT, ICON_R, am)
    white, dark = icon_masks(w, ss)
    n = white.shape[0]
    x0, y0 = int(round(c[0] * ss - n / 2)), int(round(c[1] * ss - n / 2))
    wm = np.clip((ndi.gaussian_filter(white, 0.5 * ss * 0.5) - 0.45) * 6, 0, 1)
    wf = to_cv_array(cv, wm, x0, y0)
    df = to_cv_array(cv, np.clip(dark, 0, 1), x0, y0)
    full = np.clip(wf + df, 0, 1)
    cv.paint(extrude(grow(full, 1.6 * ss), 2.0 * ss, 2.2 * ss), TONER)
    cv.paint(grow(full, 1.8 * ss), TONER)
    if df.max() > 0:
        cv.paint(df, TONER)
        hf = hatch_cached(cv, (45,), 3.0, 0.8, 5)
        cv.paint(hf * df, SHEET, 0.5)
    cv.paint(wf, WHITE_)
    return full


def draw_break_state(cv, w, m, seed):
    """pending loss: cross-hatch in the cause colour, black casing, X.  The hatch stops outside the seat, so the seat (slice ink) carries the type."""
    ss = cv.ss
    hp, ha = w['hp'], w.get('hp_after', w['hp'])
    am = 60 * w['sector']
    if hp > 0 and ha == 0:
        col = SOAKC if w.get('soaked') else HARMC
        ix, iy = pol(CT, ICON_R, am)
        X, Y = cv.grid()
        clear = np.clip((np.hypot(X - ix, Y - iy) - SEAT_CLEAR) * ss * 0.5, 0, 1)
        reg = m * clear
        cv.paint(reg, TONER, 0.26)
        hf = hatch_cached(cv, (45, 135), 6.4, 1.6, 77)
        cv.paint(np.clip(grow(hf, 0.85 * ss), 0, 1) * reg, TONER, 0.92)
        cv.paint(hf * reg, col, 1.0)
        edge = np.clip(m - shrink(m, 2.4 * ss), 0, 1)
        cv.paint(edge, col)
        x, y = pol(CT, R_OUT - 22, am + 17)
        xm = np.zeros((cv.H, cv.W), np.float32)
        for sg in (1, -1):
            xm = np.maximum(xm, poly(cv, [(x - 7, y - sg * 7 - 2.4), (x - 7, y - sg * 7 + 2.4), (x + 7, y + sg * 7 + 2.4), (x + 7, y + sg * 7 - 2.4)]))
        cv.paint(grow(xm, 1.6 * ss), TONER)
        cv.paint(xm, col)
    else:
        XT.draw_break_state(cv, w, m, seed)


# ------------------------------------------------------------------ hub
def draw_hub(cv, name='BREAKER', seed=0):
    ss = cv.ss
    c = CT
    rng = np.random.default_rng(seed + 5)
    pts = []
    n = 13
    for k in range(n * 2):
        rr = (R_HUB - 0.2) if k % 2 == 0 else (R_HUB - 6.2)
        rr *= 1 + rng.uniform(-0.03, 0.03)
        a = math.radians(k * 180.0 / n + 3)
        pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    burst = poly(cv, pts)
    cv.paint(grow(burst, 2.6 * ss), TONER)                      # black key
    ink(cv, plate_shift(burst, cv, -2.6, -2.2), MAG, 0.06, seed + 2)
    cv.paint(shrink(burst, 0.4 * ss) * 0, TONER)
    disc = poly(cv, jag_ring(c, 36.6, rng, (6, 10), 0.5))
    cv.paint(grow(disc, 2.2 * ss), TONER)
    cv.paint(disc, WHITE_ * 0.97)
    sp = toner_noise(cv, seed + 9, 0.9, 0.9)
    cv.paint(blur(sp, 0.3 * ss) * disc, TONER, 0.3)
    by = c[1] - (13.0 if name else 0.0)
    s_ = 1.0 if name else 1.5
    bolt = [(c[0] + 2.5 * s_, by - 9 * s_), (c[0] - 5.0 * s_, by + 1.0 * s_), (c[0] - 0.5 * s_, by + 1.0 * s_), (c[0] - 3.0 * s_, by + 9.5 * s_), (c[0] + 5.5 * s_, by - 2.0 * s_), (c[0] + 0.5 * s_, by - 2.0 * s_)]
    bm = poly(cv, bolt)
    cv.paint(plate_shift(bm, cv, 1.8, 1.6), MAG)
    ink(cv, bm, TONER, 0.0, seed + 4)
    if name:
        tw_, th_ = 58.0, 17.0
        ty = c[1] + 12.0
        t = rect_rot(cv, c[0] - tw_ / 2, ty - th_ / 2, c[0] + tw_ / 2, ty + th_ / 2, -2.0)
        cv.paint(shift(t, 1.6 * ss, 1.8 * ss), MAG)
        cv.paint(grow(t, 0.4 * ss), TONER)
        ink(cv, t, TONER, 0.0, seed + 50)
        xtext(cv, name, c[0], ty + 0.6, 15.5, ANTON, fill=WHITE_, rot=-2.0, wob=0.05, track=1.6, seed=seed + 60, grain=0.0)


def rect_rot(cv, x0, y0, x1, y1, rot):
    return XT.rect_rot(cv, x0, y0, x1, y1, rot)


# ------------------------------------------------------------------ assembler
def render_tower(f, name='BREAKER', S=int(__import__('os').environ.get('XF_SS', '3')), seed=11, skip_trim_units=None, hot=True, with_trim=True, ghost=None):
    cv = Cv(0, 0, TW, TW, S)
    page(cv, seed)
    wedges = []
    for w in f['wheel']:
        wedges.append((w, draw_wedge(cv, w, seed)))
    for w, m in wedges:
        draw_break_state(cv, w, m, seed)
    for w, m in wedges:
        draw_seat(cv, w, seed)
    for w, m in wedges:
        draw_icon(cv, w)
    for w, m in wedges:
        if w.get('brace'):
            draw_brace_plate(cv, w['sector'])
        if w.get('soak'):
            draw_soak_mark(cv, w['sector'])
    for w, m in wedges:
        draw_pips(cv, w)
    margin_marks(cv, seed)
    draw_hp_ring(cv, f)
    draw_hub(cv, name, seed)
    im = cv.to_image()
    if with_trim:
        tc = FT.Canvas(TW, TW, 3, seed=seed)
        FT.draw_trim(tc, f, skip_trim_units, hot)
        im.alpha_composite(tc.down())
    return im, cv


if __name__ == '__main__':
    import json
    import asm_r2 as A
    A.setup()
    J = json.load(open('D:/rc_scratch/combat_redesign/locked/wheel/state_e10.json'))
    key = sys.argv[1] if len(sys.argv) > 1 else 'f1'
    im, _ = render_tower(J[key])
    bg = Image.new('RGBA', im.size, (24, 22, 36, 255))
    bg.alpha_composite(im)
    bg.resize((bg.width * 2, bg.height * 2), Image.LANCZOS).save('D:/rc_scratch/combat_redesign/locked/wheel/out/lw_tower_%s.png' % key)
    print('ok')
