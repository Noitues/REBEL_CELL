"""wheel_core R2: every element's drawing code, self-contained.  Function index (also in NOTES):
 hub_disc / hub_inner_rings / hub_label / hub_emblem ........ hub_factory(disc, rings, label, emblem)
 slice_frame ................................................ FRAME2[...]  (tile params for wc_tower)
 slice_screen ............................................... tex_phosphor()
 slice_gutters .............................................. spokes()  (post_frame)
 icon_burst / icon_turret / icon_shield / icon_repair ....... icons2(kinds)
 codebase_frame ............................................. frame2()
 slice_hp_bars + 4 pip states ............................... bars2()  -> pip(L, st, r, a0, a1)
 slice_break_x / slice_soak_break_x ......................... break_x()
 threat_trim ................................................ trim2()
 hp_ring .................................................... hp_ring2()
 gun_tracers / gun_result_* / gun_muzzle_beads / shield_pop . guns2()
 gun_idle_stub .............................................. idle_stub()
 gun_tracers_preview ........................................ guns_preview()
 brace_plate ................................................ brace_plate2()
 slice_soak_marks / slice_soak_rim_arc ...................... soak_mark2() / soak_rim2()
 slice_cracked_mark / slice_broken_state .................... cracked2() / broken2()
 spin_ghost_preview ......................................... spin_ghost()
"""
import sys, math, json
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import wc_base as WB
from wc_base import *            # B (build10) names: C, RS, L2, ppx, pt, CB, J, GOLD, STEEL, ...
import wc_tower as T
import wc2_glyphs  # noqa: F401
import slicelib as SL
import crests15
KE = T.KE
CYAN = (92, 225, 255); INK = (12, 10, 22); HARM = (255, 68, 51); GAIN = (123, 224, 123)
SOAKC = __import__('asm_tokens').SOAK; LANE1 = (120, 170, 255); LANE2 = (236, 240, 255)
BGOLD = (255, 196, 40); STEELC = (150, 162, 182); STEELH = (226, 233, 246); PLAN = (255, 226, 0)
WHT = (255, 255, 255); SOCKD = (10, 12, 18); SOCKL = (120, 135, 152)


def m(x):            # screen px -> tower-canvas master px
    return x / KE


def sc(x, ss):
    return x / KE * ss


# ======================================================================== tile: frame, screen, gutters
FRAME2 = {
    'A': dict(gap_side=m(4.0), gap_in=m(4.0), bw=6.0, r_t_out=m(9), r_t_in=m(9), r_s_out=9, r_s_in=8, edge_w=m(2.2), edge_gain=0.98,
              ink_w=m(3.0), hair_gain=0.45, led=False, plate=0.70, bevel=0.6),
    # variant: 2.2 px edge sits one px inside an ink inset line (double keyline), r9
    'B': dict(gap_side=m(4.0), gap_in=m(4.0), bw=6.5, r_t_out=m(9), r_t_in=m(9), r_s_out=9, r_s_in=8, edge_w=m(2.2), edge_gain=0.85,
              ink_w=m(3.0), hair_gain=0.0, led=False, plate=0.70, glass=0.45, bevel=0.8),
}


def tex_phosphor(lift=0.08, pitch_px=3.0, base=0.085):
    """slice_screen A: 3 px phosphor mesh shared with unit CRT bowls, <= 8 % value lift, no halo / rainbow."""
    def fn(ctx):
        ss, Wt, Ht = ctx.ss, ctx.W, ctx.H
        col = np.array(ctx.col, np.float32) / 255.0
        yy, xx = np.mgrid[0:Ht, 0:Wt].astype(np.float32)
        pitch = pitch_px / KE * ss
        gx = np.cos(2 * np.pi * xx / pitch) * 0.5 + 0.5
        gy = np.cos(2 * np.pi * yy / pitch) * 0.5 + 0.5
        mesh = (gx * gy) ** 1.5
        lum = base + lift * mesh
        rgb = lum[..., None] * (0.35 + 0.65 * col)[None, None, :] * 3.0
        return Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
    return fn


def tile2(frame='A', tex=None):
    t = dict(FRAME2[frame])
    t.update(tex=tex or tex_phosphor(), tex_gain=1.0, glow_k=(0.0, 0.0))
    return t


# ======================================================================== hub
def _layer(over):
    return Image.new('RGBA', over.size, (0, 0, 0, 0))


def _ring(d, cx, cy, r, col, w, ss, a0=None, a1=None):
    box = [cx - sc(r, ss), cy - sc(r, ss), cx + sc(r, ss), cy + sc(r, ss)]
    wd = max(1, int(round(sc(w, ss))))
    if a0 is None:
        d.ellipse(box, outline=col, width=wd)
    else:
        d.arc(box, a0, a1, fill=col, width=wd)


def _disc(d, cx, cy, r, col, ss):
    d.ellipse([cx - sc(r, ss), cy - sc(r, ss), cx + sc(r, ss), cy + sc(r, ss)], fill=col)


def _engraved(over, name, px, cx, cy, ss, col, flat=False):
    """glyph cut into the glass: ink under-shadow top-left, light lip bottom-right, cyan floor."""
    g = SL.glyph_rgba(name, int(sc(px, ss)), 2, fill=col)
    a = g.split()[3]
    sh = Image.new('RGBA', g.size, INK + (255,)); sh.putalpha(a)
    lip = Image.new('RGBA', g.size, (200, 245, 255, 150)); lip.putalpha(a.point(lambda v: v * 150 // 255))
    ox, oy = int(cx - g.width / 2), int(cy - g.height / 2)
    if flat:
        over.alpha_composite(SL.glyph_rgba(name, int(sc(px, ss)), max(2, int(sc(px, ss) * 0.075)), fill=(255, 255, 255)), (ox, oy)); return
    d1 = max(1, int(sc(1.0, ss)))
    over.alpha_composite(lip, (ox + d1, oy + d1))
    over.alpha_composite(sh, (ox - d1, oy - d1))
    flat = Image.new('RGBA', g.size, col + (255,)); flat.putalpha(a.point(lambda v: 255 if v > 200 else 0))
    over.alpha_composite(flat, (ox, oy))


def hub_factory(disc='A', rings='A', label='A', emblem='A', label_gap=6.0, crest_px=22.0):
    flat = emblem == 'B'
    def fn(over, d, ss, cx, cy, nowords):
        HR = RS['hub']
        lay = _layer(over); ld = ImageDraw.Draw(lay)
        # hub_disc A: ink halo 4 px at 60 %, near-black glass with a faint radial lift, NET_CYAN rim 2.6 px
        if disc == 'A':
            _disc(ld, cx, cy, HR + 4.0, INK + (153,), ss)
            for i in range(14):
                t = i / 13
                v = (6 + 10 * t, 8 + 12 * t, 14 + 16 * t)
                _disc(ld, cx, cy, HR * (1 - t * 0.9), tuple(int(c) for c in v) + (255,), ss)
            _ring(ld, cx, cy, HR - 1.3, CYAN + (255,), 2.6, ss)
        else:   # variant B: dome with scanlines
            _disc(ld, cx, cy, HR + 4.0, INK + (153,), ss)
            _disc(ld, cx, cy, HR, (7, 9, 15, 255), ss)
            for y in range(int(-HR) + 4, int(HR) - 3, 4):
                hw = math.sqrt(max(0, HR * HR - y * y)) - 3
                ld.line([(cx - sc(hw, ss), cy + sc(y, ss)), (cx + sc(hw, ss), cy + sc(y, ss))], fill=(92, 225, 255, 20), width=max(1, int(sc(1, ss))))
            _ring(ld, cx, cy, HR - 1.3, CYAN + (255,), 2.6, ss)
        # hub_inner_rings A: one 1.4 px bevel arc, light top-left (+12 value) / shade bottom-right (-12 value)
        if rings == 'A':
            _ring(ld, cx, cy, 33, (255, 255, 255, 40), 1.4, ss, 175, 305)
            _ring(ld, cx, cy, 33, (0, 0, 0, 120), 1.4, ss, 355, 125)
        elif rings == 'B':   # variant: bevel arc plus a faint full hairline ring
            _ring(ld, cx, cy, 33, (255, 255, 255, 14), 1.4, ss)
            _ring(ld, cx, cy, 33, (255, 255, 255, 46), 1.4, ss, 175, 305)
            _ring(ld, cx, cy, 33, (0, 0, 0, 120), 1.4, ss, 355, 125)
        over.alpha_composite(lay)
        # emblem + label
        if nowords:
            _engraved(over, 'WC2_CREST', 34.0, cx, cy, ss, CYAN, flat)
            return
        cap = 17 * 0.74
        group = crest_px + label_gap + cap
        top = -group / 2 + 1.0
        _engraved(over, 'WC2_CREST', crest_px, cx, cy + sc(top + crest_px / 2, ss), ss, CYAN, flat)
        fb = anton(int(17 / KE * ss))
        lay = _layer(over); ld = ImageDraw.Draw(lay)
        base_y = top + crest_px + label_gap + cap
        ld.text((cx, cy + sc(base_y, ss)), 'BREAKER', font=fb, fill=(246, 249, 255, 255), anchor='ms',
                stroke_width=max(2, int(sc(2.0, ss))), stroke_fill=INK + (255,))
        over.alpha_composite(lay)
    return fn


def frame2(kind='A'):
    """codebase_frame A: ONE cyan 2 px ring (ink under); only the spokes break it."""
    def fn(over, d, ss, cx, cy):
        lay = _layer(over); ld = ImageDraw.Draw(lay)
        R = 158.4
        _ring(ld, cx, cy, R, INK + (255,), 2 + 4.4, ss)
        _ring(ld, cx, cy, R, CYAN + (255,), 2.0, ss)
        if kind == 'B':     # variant: ring carries a 1 px inner hairline echo (engraved base rim)
            _ring(ld, cx, cy, R - 4.0, CYAN + (70,), 1.0, ss)
        over.alpha_composite(lay)
    return fn


def spokes(L):
    """slice_gutters B: one continuous 8 px INK strip per sector boundary, hub edge -> code-base ring outer edge (the wave rings take over)."""
    for s in range(6):
        a = 60 * s + 30
        L.line([ppx(C, 43, a), ppx(C, 162, a)], INK, 8)


# ======================================================================== icons
def icons2(burst='B', turret='A', repair='P', size=44):
    kinds = {'BURST': 'WC2_BURST_' + burst, 'TURRET': 'WC2_TURRET_' + turret, 'REPAIR': 'WC2_REPAIR_' + repair}

    def fn(canvas, ss, cx, cy, s, t):
        if t == 'SHIELD' or t not in kinds:
            WB.icons_cur(canvas, ss, cx, cy, s, t)          # icon_shield keeps the CURRENT E10 split heater
        else:
            T.icon_on_canvas(canvas, ss, cx, cy, 60 * s, kinds[t], size, rc_f=0.52)
    return fn


def cfg2(tile=None, hub=None, frame=None, icons=None, post=None, icon_dims=(46, 46)):
    c = WB.cur_cfg()
    c['tile'] = tile or tile2()
    c['hub'] = hub or hub_factory()
    c['frame'] = frame or frame2()
    c['icons'] = icons or icons2()
    c['icon_dims'] = icon_dims
    c['post_frame'] = post or spokes
    return c


# ======================================================================== HP grammar
BAR_R, BAR_W, BAR_LEN, BAR_GAP = 129.0, 7.0, 38.0, 3.0


def cap_line(L, pts, col, w):
    L.line(pts, col, w)
    for p in (pts[0], pts[-1]):
        L.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=col)


def capsule(L, r, a0, a1, col, w, ink=2.2):
    pts = L.arc_pts(C, r, a0, a1, 8)
    cap_line(L, pts, INK, w + ink * 2)
    cap_line(L, pts, col, w)


def pip(L, st, r, a0, a1, w=BAR_W):
    """one HP segment in the shared grammar.  st: lit | harm | soak | mend | gone.  a0 < a1 are the capsule's END-CAP-INCLUDED angles."""
    cr = lambda px: math.degrees(px / r)
    b0, b1 = a0 + cr(w / 2), a1 - cr(w / 2)
    am = (a0 + a1) / 2
    if st == 'lit':
        capsule(L, r, b0, b1, GAIN, w)
    elif st == 'harm':
        capsule(L, r, b0, b1, HARM, w)
        p = [ppx(C, r - w * 0.62, am - cr(2.8)), ppx(C, r + w * 0.62, am + cr(2.8))]
        L.line(p, INK, 4.4); L.line(p, WHT, 2.0)
    elif st == 'soak':
        capsule(L, r, b0, b1, SOAKC, w, ink=3.2)          # fix 7: 1 px more INK keyline
        p = [ppx(C, r + 3.9, am - cr(4.0)), ppx(C, r - 0.6, am), ppx(C, r + 3.9, am + cr(4.0))]
        L.line(p, INK, 5.4)                                # fix 7: notch 4.0 -> 5.4 px (>= 3 px resolved at 320)
    elif st == 'mend':
        capsule(L, r, b0, b1, GAIN, w)
        pts = L.arc_pts(C, r, b0, b1, 8); cap_line(L, pts, (8, 16, 12), w - 4.0)
        x, y = ppx(C, r, am)
        L.line([(x - 3.2, y), (x + 3.2, y)], GAIN, 1.8); L.line([(x, y - 3.2), (x, y + 3.2)], GAIN, 1.8)
    else:   # gone: dark socket + solid 1.4 px hairline
        pts = L.arc_pts(C, r, b0, b1, 8)
        cap_line(L, pts, SOCKL, w)
        cap_line(L, pts, SOCKD, w - 2.8)


def pip_states(w):
    mx, hp, ha, sk = w['mx'], w['hp'], w.get('hp_after', w['hp']), w.get('soaked', 0)
    out = []
    for i in range(mx):
        if i < ha and i < hp: out.append('lit')
        elif i < ha: out.append('mend')
        elif i < hp: out.append('soak' if (hp - 1 - i) < sk else 'harm')
        else: out.append('gone')
    return out


def bars2(r=BAR_R):
    def draw(L, w, s):
        sts = pip_states(w)
        n = len(sts)
        cr = lambda px: math.degrees(px / r)
        tot = n * BAR_LEN + (n - 1) * BAR_GAP
        a = 60 * s - cr(tot) / 2
        for i, st in enumerate(sts):
            a0 = a + cr(i * (BAR_LEN + BAR_GAP))
            pip(L, st, r, a0, a0 + cr(BAR_LEN))
    return draw


# ======================================================================== break X (preview), soak break X
def x_mark(L, x, y, r, col, lw=6.0, ink=2.4):
    for sg in (1, -1):
        L.line([(x - r, y - sg * r), (x + r, y + sg * r)], INK, lw + ink * 2)
    for sg in (1, -1):
        L.line([(x - r, y - sg * r), (x + r, y + sg * r)], col, lw)


def hatch(L, s, a_lo, a_hi, r0, r1, alpha_dim=0.35, col=INK, icon_r=27, rc=95.5, hcol=HARM):
    """45 deg hatch + flat dim over the wedge screen, with a clear disc around the icon so the icon stays full value."""
    k = L.k
    lay = Image.new('RGBA', L.im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    band = L.band(C, r0, r1, a_lo, a_hi)
    pp = [(x * k, y * k) for x, y in band]
    d.polygon(pp, fill=col + (int(255 * alpha_dim),))
    mk = Image.new('L', L.im.size, 0); md = ImageDraw.Draw(mk)
    xs = [p[0] for p in band]; ys = [p[1] for p in band]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    t = x0 - (y1 - y0)
    while t < x1 + (y1 - y0):
        md.line([(t * k, y1 * k), ((t + (y1 - y0)) * k, y0 * k)], fill=255, width=int(2 * k))
        t += 7.0
    pm = Image.new('L', L.im.size, 0); ImageDraw.Draw(pm).polygon(pp, fill=255)
    ix, iy = ppx(C, rc, 60 * s)
    ImageDraw.Draw(pm).ellipse([(ix - icon_r) * k, (iy - icon_r) * k, (ix + icon_r) * k, (iy + icon_r) * k], fill=0)
    mk = Image.fromarray(np.minimum(np.asarray(mk), np.asarray(pm)))
    h = Image.new('RGBA', L.im.size, hcol + (255,)); h.putalpha(mk.point(lambda v: int(v * 0.62)))
    lay.alpha_composite(h)
    # carve the icon disc out of the flat dim too
    a = np.asarray(lay.split()[3]).copy()
    cm = Image.new('L', L.im.size, 255); ImageDraw.Draw(cm).ellipse([(ix - icon_r) * k, (iy - icon_r) * k, (ix + icon_r) * k, (iy + icon_r) * k], fill=0)
    lay.putalpha(Image.fromarray((a * (np.asarray(cm) / 255.0)).astype(np.uint8)))
    L.im.alpha_composite(lay)


def break_x(kind='A', soak=False):
    def fn(L, s, phase='both'):
        col = SOAKC if soak else HARM
        am = 60 * s
        if phase in ('both', 'pre') and kind in ('A', 'N'):
            hatch(L, s, am - 25.5, am + 25.5, RS['s0'] + 3, RS['s1'] - 2, hcol=col)
        if phase == 'pre':
            return
        x, y = ppx(C, 106, am + 20)
        x_mark(L, x, y, 8.0, col, ink=3.4 if soak else 2.4)     # fix 7: soak X keyline 1 px more
        if soak and kind in ('N', 'B'):     # O3: one 5 px INK diamond notch at the crossing only (1 px INK keyline); the four arms stay continuous
            d_ = 2.5
            L.poly([(x, y - d_), (x + d_, y), (x, y + d_), (x - d_, y)], fill=INK, outline=INK, w=1.0)
    return fn


# ======================================================================== threat trim
def trim2(kind='A', R=139.5):
    def trim(L, f):
        seen = {}
        for u in f['units']:
            fz = u['fate']
            if fz['kind'] != 'lands' or u['consumed'] or u['trigdead']:
                continue
            for (sec, sl, hit, tohp) in fz['hits']:
                seen.setdefault(sec, set()).add(fz['k'])
        def arc(a0, a1, k):
            pts = L.arc_pts(C, R, a0, a1)
            if k == 0:
                L.glow(lambda dd: dd.line(L.P(pts), fill=HARM + (255,), width=int(11 * L.k), joint='curve'), blur=4, strength=0.35)
                L.line(pts, INK, 6 + 4.4); L.line(pts, HARM, 6)
            elif k == 1:
                L.line(pts, INK, 4 + 4.4); L.line(pts, LANE1, 4)
            else:
                L.line(pts, INK, 3 + 4.4); L.line(pts, LANE2, 3, dash=(5, 5))
        for sec, ks in seen.items():
            mm = 60 * sec
            zones = {2: (-26.5, -9.5), 1: (-8.5, 8.5), 0: (9.5, 26.5)}
            if kind == 'B':    # variant: thirds share a single ink rail (one continuous keyline), colours on top
                L.line(L.arc_pts(C, R, mm - 27, mm + 27), INK, 4 + 4.4 if False else 9.5)
            for k in sorted(ks):
                arc(mm + zones[k][0], mm + zones[k][1], k)
    return trim


# ======================================================================== HP ring
def hp_ring2(kind='A', r0=149.5, r1=155.5, off=6.0):
    def ring(L, hp, hp_after, mx):
        L.poly(L.band(C, r0 - 1.6, r1 + 1.6, 0, 359.9), fill=(4, 5, 9, 255))
        rc, w = (r0 + r1) / 2, r1 - r0
        n_per = 5
        g1, g2 = 1.6, 4.8
        seg = (360 / (mx / n_per) - g2 - (n_per - 1) * g1) / n_per
        for i in range(mx):
            grp, j = divmod(i, n_per)
            a0 = off + grp * 360 / (mx / n_per) + g2 / 2 + j * (seg + g1)
            st = 'lit' if i < hp_after else ('harm' if i < hp else 'gone')
            if kind == 'B' and st == 'gone':
                continue
            pip(L, st, rc, a0, a0 + seg, w)
    return ring


# ======================================================================== guns
def cell_centre(f, uid):
    for u in f['units']:
        if u['id'] == uid:
            sec = sectors(u)
            ang = [60 * q for q in sec]
            base = ang[0]
            rel = [((a - base + 180) % 360) - 180 for a in ang]
            mid = base + sum(rel) / len(rel)
            ri, ro = CB.ring_geom(u['dep'] if 'dep' in u else 0)
            return mid, ri, ro
    return None


def dash_line(L, p0, p1, col, w, dash=(12, 6), ink_w=None, alpha=255):
    """tracer: ink dashes (slightly longer) under cyan dashes so each dash is edged."""
    ink_w = ink_w or w + 4.4
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dx, dy)
    ux, uy = dx / ln, dy / ln
    t = 0.0
    segs = []
    while t < ln:
        e = min(ln, t + dash[0]); segs.append((t, e)); t = e + dash[1]
    lay = L.im if alpha == 255 else Image.new('RGBA', L.im.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    k = L.k
    for (a, b) in segs:
        dl.line([((p0[0] + ux * (a - 2.2)) * k, (p0[1] + uy * (a - 2.2)) * k), ((p0[0] + ux * (b + 2.2)) * k, (p0[1] + uy * (b + 2.2)) * k)],
                fill=INK + (int(alpha),), width=int(ink_w * k))
    for (a, b) in segs:
        dl.line([((p0[0] + ux * a) * k, (p0[1] + uy * a) * k), ((p0[0] + ux * b) * k, (p0[1] + uy * b) * k)], fill=col + (int(alpha),), width=int(w * k))
    if alpha != 255:
        L.im.alpha_composite(lay)


def spark(L, x, y, size=18, alpha=255):
    pts = []
    for i in range(16):
        a = math.radians(i * 22.5 - 90)
        rr = size / 2 if i % 2 == 0 else size / 2 * 0.40
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    L.poly(pts, fill=WHT, outline=INK, w=2.4)


def chevron_result(L, x, y, ang_back, col, size=22, wall=False):
    """armor / ward bounce: one bold chevron, deflected 35 deg off the tracer axis, pointing back toward the tower; ink under."""
    a = math.radians(ang_back)
    ux, uy = math.sin(a), -math.cos(a)               # pointing direction
    px_, py_ = -uy, ux
    h = size / 2
    tip = (x + ux * h * 0.6, y + uy * h * 0.6)
    p = [(x - ux * h * 0.5 + px_ * h, y - uy * h * 0.5 + py_ * h), tip, (x - ux * h * 0.5 - px_ * h, y - uy * h * 0.5 - py_ * h)]
    L.line(p, INK, 9.6); L.line(p, col, 5.2)
    if wall:
        q = [(x - ux * h * 1.1 + px_ * h * 1.0, y - uy * h * 1.1 + py_ * h * 1.0), (x - ux * h * 1.1 - px_ * h * 1.0, y - uy * h * 1.1 - py_ * h * 1.0)]
        L.line(q, INK, 8); L.line(q, col, 3.6)


def pop_cur(L, x, y):
    for i in range(8):
        a = math.radians(i * 45)
        p = [(x + 6 * math.cos(a), y + 6 * math.sin(a)), (x + 13 * math.cos(a), y + 13 * math.sin(a))]
        L.line(p, INK, 5.4); L.line(p, CYAN, 2.4)
    L.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(8, 20, 30), outline=CYAN, w=2.2)


def pop_arcs(L, x, y, size=22):
    """cyan ring breaking in 4 arcs, dark core"""
    r = size / 2 - 2.5
    L.ellipse([x - r + 3, y - r + 3, x + r - 3, y + r - 3], fill=(6, 12, 22, 255), outline=INK, w=1.2)
    for i in range(4):
        a0 = i * 90 + 14; a1 = i * 90 + 76
        rr = r + 1.2 * (1 if i % 2 == 0 else 0)
        pts = [(x + rr * math.cos(math.radians(a)), y + rr * math.sin(math.radians(a))) for a in np.linspace(a0, a1, 9)]
        L.line(pts, INK, 7.6); L.line(pts, CYAN, 3.2)
    L.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(92, 225, 255, 140))


def pop_shards(L, x, y, size=22):
    """hex shard burst: 6 hexagonal shards flying off a dark core"""
    L.ellipse([x - 5.5, y - 5.5, x + 5.5, y + 5.5], fill=(6, 12, 22, 255), outline=CYAN, w=2.0)
    for i in range(6):
        a = math.radians(i * 60 + 18)
        cx_, cy_ = x + (size / 2 - 3.2) * math.cos(a), y + (size / 2 - 3.2) * math.sin(a)
        rr = 3.9 if i % 2 == 0 else 3.0
        hexp = [(cx_ + rr * math.cos(math.radians(60 * j + 30 + i * 11)), cy_ + rr * math.sin(math.radians(60 * j + 30 + i * 11))) for j in range(6)]
        L.poly(hexp, fill=CYAN, outline=INK, w=2.0)


def muzzle(L, p, kind='A'):
    x, y = p
    L.ellipse([x - 5.2, y - 5.2, x + 5.2, y + 5.2], fill=INK)
    L.ellipse([x - 3, y - 3, x + 3, y + 3], fill=CYAN)


MUZ_R = 160.5


def gun_geom(f, g, i, n):
    s = g['sector']
    off = 24 + (i - (n - 1) / 2) * 9
    return s, off


def guns2(alpha=255, only=None, result_alpha=None, pop='arcs', wall=False, beads=True, words=True, dim_others=None, idle='A'):
    """gun_tracers A + results + muzzle beads A.  alpha: tracer opacity (preview 55 %)."""
    def g(L, f):
        for gn in f['guns']:
            s = gn['sector']
            shots = [sh for sh in gn['shots'] if sh['uid'] is not None]
            if not shots:
                idle_stub(L, s, f, idle, words)
                continue
            n = len(shots)
            al = alpha
            ra = alpha if result_alpha is None else result_alpha
            if dim_others is not None:
                changed = any(sh['result'] == 'ward' for sh in shots)
                al = alpha if changed else dim_others
                ra = al
            for i, sh in enumerate(shots):
                s_, off = gun_geom(f, gn, i, n)
                p0 = pt(MUZ_R, 60 * s, off)
                cc = cell_centre(f, sh['uid'])
                ri, ro = CB.ring_geom(sh['dep'])
                if cc is None:
                    p1 = pt((ri + ro) / 2, 60 * s, off * 0.6)
                else:
                    p1 = ppx(C, (ri + ro) / 2, cc[0])
                dash_line(L, p0, p1, CYAN, 3.0, (12, 6), alpha=al)
                x, y = p1
                lay = L if ra == 255 else None
                if ra != 255:
                    sub = L2(); sub_res(sub, sh, x, y, p0, pop, wall)
                    im = sub.im; im.putalpha(im.split()[3].point(lambda v: int(v * ra / 255)))
                    L.im.alpha_composite(im)
                else:
                    sub_res(L, sh, x, y, p0, pop, wall)
                if beads:
                    sub_bead = L2() if al != 255 else L
                    muzzle(sub_bead, p0)
                    if al != 255:
                        im = sub_bead.im; im.putalpha(im.split()[3].point(lambda v: int(v * al / 255))); L.im.alpha_composite(im)
    return g


def sub_res(L, sh, x, y, p0, pop, wall):
    back = math.degrees(math.atan2(p0[0] - x, -(p0[1] - y)))      # direction from impact back toward the muzzle
    r = sh['result']
    if r == 'hit':
        spark(L, x, y, 18)
    elif r == 'armor':
        chevron_result(L, x, y, back + 35, STEELC if False else STEELH, 22, wall)
    elif r == 'ward':
        chevron_result(L, x, y, back + 35, BGOLD, 22, wall)
    elif r == 'shield':
        {'cur': pop_cur, 'arcs': pop_arcs, 'shards': pop_shards}[pop](L, x, y)


def idle_stub(L, s, f, kind='A', words=True):
    """gun_idle_stub: cyan 1.4 px stub at 40 % ending in an empty-target mark.  A open ring, B bar cap, C two dim dashes"""
    a = 60 * s
    if kind == 'C':
        for (r0, r1) in ((166, 174), (180, 188)):
            lay = L2(); pts = [ppx(C, r0, a), ppx(C, r1, a)]
            lay.line(pts, CYAN, 1.4); im = lay.im; im.putalpha(im.split()[3].point(lambda v: int(v * 0.6)))
            L.im.alpha_composite(im)
        return
    lay = L2()
    p0, p1 = ppx(C, 164, a), ppx(C, 186, a)
    lay.line([p0, p1], CYAN, 1.4)
    if kind == 'A':
        x, y = ppx(C, 192, a)
        lay.ellipse([x - 5, y - 5, x + 5, y + 5], outline=CYAN, w=1.4)
    else:
        q = [pt(187, a, -7), pt(187, a, 7)]
        lay.line(q, CYAN, 1.4)
    im = lay.im; im.putalpha(im.split()[3].point(lambda v: int(v * 0.6)))
    L.im.alpha_composite(im)
    if words and NOW['words']:
        xx_, yy_ = ppx(C, RS['c0'] + 48, a)
        L.rect([xx_ - 56, yy_ - 13, xx_ + 56, yy_ + 13], fill=(5, 13, 28, 237), outline=CYAN, w=2, r=8)
        L.text((xx_, yy_ + 1), 'NO TARGET', 18, 'mono', fill=CYAN)


def guns_preview(kind='A', idle='A', pop='shards'):
    if kind == 'A':
        return guns2(alpha=140, result_alpha=140, idle=idle, pop=pop)
    if kind == 'B':
        return guns2(alpha=140, result_alpha=255, idle=idle, pop=pop)
    return guns2(alpha=215, result_alpha=215, dim_others=100, idle=idle, pop=pop)


# ======================================================================== brace plate, soak marks, soak rim arc
def _slab(L, s, r0, r1, half, fill, rivets=True, sides=False, glyph=False):
    a0, a1 = 60 * s - half, 60 * s + half
    pts = L.band(C, r0, r1, a0, a1)
    L.poly(pts, fill=fill, outline=INK, w=4.4)
    L.poly(pts, fill=fill, outline=None)
    if sides:
        for sg in (-1, 1):
            aa = (60 * s - half, 60 * s - half + 3.6) if sg < 0 else (60 * s + half - 3.6, 60 * s + half)
            leg = L.band(C, r0 - 12, r1, aa[0], aa[1])
            L.poly(leg, fill=fill, outline=INK, w=4.4); L.poly(leg, fill=fill)
    if rivets:
        for sg in (-1, 1):
            x, y = ppx(C, (r0 + r1) / 2, 60 * s + sg * (half - 5.0))
            L.ellipse([x - 2.6, y - 2.6, x + 2.6, y + 2.6], fill=INK)
            L.ellipse([x - 0.9, y - 0.9, x + 0.9, y + 0.9], fill=(190, 240, 255))


def brace_plate2(kind='A'):
    def fn(L, s):
        if kind == 'A':       # slab across the rim
            _slab(L, s, 134.0, 142.5, 24, CYAN)
        elif kind == 'B':     # slab with two jaw legs clamping the wedge sides
            _slab(L, s, 134.0, 142.5, 25, CYAN, sides=True)
        else:                 # slab + the card's clamp-plate glyph mounted at its centre
            _slab(L, s, 134.0, 142.5, 24, CYAN)
            x, y = ppx(C, 120, 60 * s)
            L.glyph('KA_brace', 20, (x, y), CYAN)
    return fn


def soak_mark2(kind='A'):
    """one SOAK mark per soaking slice (the pip is the other); never over the icon."""
    def fn(L, s):
        if kind == 'A':         # hub-side inward chevron, in the free band under the icon
            p = [pt(66, 60 * s, -13), pt(57, 60 * s, 0), pt(66, 60 * s, 13)]
            L.line(p, INK, 11.4); L.line(p, SOAKC, 6)     # fix 7: keyline 2.2 -> 2.7 px
        elif kind == 'B':       # funnel (the HUD destination shape) hub side
            fl = [pt(70, 60 * s, -19), pt(70, 60 * s, 19), pt(56, 60 * s, 6), pt(56, 60 * s, -6)]
            L.poly(fl, fill=SOAKC, outline=INK, w=3.4)
        else:                   # chevron beside the icon (rim side of the wedge), pointing inward
            p = [pt(103, 60 * s, 31), pt(95, 60 * s, 39), pt(103, 60 * s, 47)]
            p = [pt(100, 60 * s, 33), pt(92, 60 * s, 33 + 0), pt(100, 60 * s, 33)]
            p = [pt(103, 60 * s, -48), pt(93, 60 * s, -38), pt(103, 60 * s, -28)]
            L.line(p, INK, 10.4); L.line(p, SOAKC, 6)
    return fn


def soak_rim2(kind='A'):
    def fn(L, s):
        if kind == 'A':         # removed
            return
        if kind == 'B':         # replaces the type-colour frame edge on the outer rim (no extra arc)
            pts = L.arc_pts(C, 141.0, 60 * s - 26, 60 * s + 26)
            L.line(pts, INK, 2.2 + 4.4); L.line(pts, SOAKC, 2.2)
        else:                   # inner rail inside the screen, under the bars (2 arcs in 12 px: rail + bars)
            pts = L.arc_pts(C, 121.0, 60 * s - 22, 60 * s + 22)
            L.line(pts, INK, 3.0 + 4.4); L.line(pts, SOAKC, 3.0)
    return fn


# ======================================================================== cracked / broken slice states
def cracked2(kind='A'):
    def fn(L, s):
        am = 60 * s
        if kind == 'A':         # white zigzag crack across the rim corner, off the icon
            pts = [ppx(C, 142, am + 21), ppx(C, 135, am + 18), ppx(C, 131, am + 23), ppx(C, 124, am + 19.5), ppx(C, 120, am + 24)]
            L.line(pts, INK, 6.4); L.line(pts, WHT, 2.4)
        elif kind == 'B':       # glass fracture: star of three thin cracks from the rim corner
            o = ppx(C, 140, am + 22)
            for (rr, aa) in ((118, 17), (126, 14), (112, 27)):
                e = ppx(C, rr, am + aa)
                mid = ((o[0] + e[0]) / 2 + 2, (o[1] + e[1]) / 2 - 2)
                L.line([o, mid, e], INK, 5.0); L.line([o, mid, e], WHT, 1.8)
        else:                   # chipped frame: a notch bitten out of the rim corner
            pts = [ppx(C, 144, am + 15), ppx(C, 137, am + 19.5), ppx(C, 141, am + 23), ppx(C, 134, am + 27)]
            L.line(pts, INK, 6.4); L.line(pts, WHT, 2.4)
    return fn


def broken2(kind='A'):
    def fn(L, s, glyph_name=None):
        am = 60 * s
        band = L.band(C, RS['s0'] + 3, RS['s1'] - 1, am - 26, am + 26)
        L.poly(band, fill=(5, 6, 11, 240), outline=None)
        ln = L.arc_pts(C, RS['s1'] - 1, am - 26, am + 26)
        outl = band + [band[0]]
        L.line(outl, SOCKL, 1.4)
        if kind == 'A':         # dark socket, ghost icon at 28 %
            if glyph_name:
                lay = L2(); lay.glyph(glyph_name, 44, ppx(C, 95.5, am), (255, 255, 255))
                im = lay.im; im.putalpha(im.split()[3].point(lambda v: int(v * 0.28))); L.im.alpha_composite(im)
        elif kind == 'B':       # socket + one hairline fissure edge to edge (no icon)
            p = [ppx(C, RS['s1'] - 6, am - 14), ppx(C, 112, am - 6), ppx(C, 98, am - 11), ppx(C, 80, am + 3), ppx(C, 62, am + 1)]
            L.line(p, SOCKL, 1.4)
        else:                   # socket with hairline ring where the icon was (empty socket reads 'gone')
            x, y = ppx(C, 95.5, am)
            L.ellipse([x - 17, y - 17, x + 17, y + 17], outline=SOCKL, w=1.4)
    return fn


# ======================================================================== spin ghost
def spin_ghost(kind='A', N=3):
    TYPE_COL = {'BURST': (255, 150, 90), 'SHIELD': (96, 220, 190), 'TURRET': (255, 214, 90), 'REPAIR': (123, 224, 123)}

    def fn(L, f):
        wheel = f['wheel']
        for w in wheel:
            s = (w['sector'] + N) % 6          # destination sector of this slice
            am = 60 * s
            col = TYPE_COL.get(w['t'], (200, 200, 220))
            band = L.band(C, RS['s0'] + 3, RS['s1'] - 1, am - 26, am + 26)
            lay = L2()
            lay.poly(band, fill=None, outline=col, w=3.0)
            gname = {'BURST': 'WC2_BURST_B', 'TURRET': 'WC2_TURRET_A', 'REPAIR': 'WC2_REPAIR_P'}.get(w['t'])
            if kind == 'A':     # small ghost icon on the hub side + edge outline, 38 %
                if gname:
                    lay.glyph(gname, 26, ppx(C, 64, am), (255, 255, 255))
            elif kind == 'B':   # full-size ghost icon over the live wheel
                if gname:
                    lay.glyph(gname, 44, ppx(C, 95.5, am), (255, 255, 255))
            im = lay.im; im.putalpha(im.split()[3].point(lambda v: int(v * 0.55 if kind != 'B' else v * 0.42))); L.im.alpha_composite(im)
        # Spin arrow ring (cards' glyph, cut into N), the only new mark
        gx, gy = ppx(C, 0, 0)
        L.glyph('KA_spin%d' % N, 40 if kind != 'C' else 56, (C[0], C[1] - (14 if kind != 'C' else 0)), PLAN)
    return fn
