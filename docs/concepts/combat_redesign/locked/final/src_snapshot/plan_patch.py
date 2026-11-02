"""plan_patch: brings the E10 generator's board onto the VISUAL_PLAN grammar for the hover plates (monkey patches in the working COPY only).
 - no dashed line anywhere: lane +2 = L8 dotted, growth chevrons = hollow outline, tracers = solid pink painted stroke (L2)
 - lane outlines are neutral ENAMEL and carry the time grammar (NOW hot solid / +1 cold thinner / +2 far dotted), no red / blue / white lane colours
 - HP lost at END TURN = L7 cross-hatch (red = enemy hit, pink = we take it), the white slash is retired
 - enemy units use the cool slate set; tokens carry an ENAMEL rim
 - hub rim / tracers in the player's pink
"""
import sys, math
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

PINK = (255, 61, 168)
ENAMEL = (217, 225, 234)
HARM = (255, 68, 51)
INKC = (12, 10, 22)
SLATE = {'Packet': (61, 84, 102), 'Worm': (75, 74, 110), 'Jammer': (45, 93, 105), 'Payload': (91, 85, 96), 'Ring': (85, 97, 122)}

_done = [False]


def hatch_poly(L, pts, col, pitch=4.0, lw=1.5, base=None, alpha=255, edge=0.0, both=True):
    """L7 cross-hatch clipped to the polygon pts (1080p px); base = optional solid fill under the hatch; edge = solid outline width"""
    k = L.k
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, y0 = int(min(xs)) - 3, int(min(ys)) - 3
    x1, y1 = int(max(xs)) + 4, int(max(ys)) + 4
    w, h = (x1 - x0) * k, (y1 - y0) * k
    if w <= 0 or h <= 0:
        return
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).polygon([((x - x0) * k, (y - y0) * k) for x, y in pts], fill=255)
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if base is not None:
        d.rectangle([0, 0, w, h], fill=tuple(base) + (255,))
    c = tuple(col) + (255,)
    step = pitch * k
    n = int((w + h) / step) + 2
    for i in range(n):
        o = i * step
        d.line([(o - h, h), (o, 0)], fill=c, width=max(1, int(lw * k)))                 # 45 deg
        if both:
            d.line([(o - h, 0), (o, h)], fill=c, width=max(1, int(lw * k)))             # 135 deg
    if edge:
        pp = [((x - x0) * k, (y - y0) * k) for x, y in pts]
        d.line(pp + [pp[0]], fill=c, width=max(1, int(edge * k)), joint='curve')
        m2 = Image.new('L', (w, h), 0)
        ImageDraw.Draw(m2).polygon(pp, fill=255)
        mask = m2
    if alpha != 255:
        mask = mask.point(lambda v: int(v * alpha / 255))
    lay.putalpha(Image.fromarray((np.array(lay.split()[3]).astype(np.uint16) * np.array(mask).astype(np.uint16) // 255).astype(np.uint8)))
    L.im.alpha_composite(lay, (x0 * k, y0 * k))


def apply():
    if _done[0]:
        return
    _done[0] = True
    import cv_lib, wr2_lib, wr2_units, wc2, hud2, wr_geo, asm_tokens, build10, cv_board
    from cv_lib import ppx, C

    # ---------------------------------------------------------------- no dashes: Layer.line dash=tuple -> solid, dash='dot' -> L8 dots
    def dotted_k(d, pts, col, w, pitch=9.0, r=2.0):
        t = 0.0
        out = []
        for (a, b) in zip(pts[:-1], pts[1:]):
            ln = math.hypot(b[0] - a[0], b[1] - a[1])
            if ln == 0:
                continue
            ux, uy = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
            s = (-t) % pitch
            while s < ln:
                out.append((a[0] + ux * s, a[1] + uy * s))
                s += pitch
            t += ln
        for (x, y) in out:
            d.ellipse([x - r, y - r, x + r, y + r], fill=col)

    def line(self, pts, col, w=2, dash=None):
        col = tuple(col) + ((255,) if len(col) == 3 else ())
        if dash == 'dot':
            k = self.k
            dotted_k(self.d, self.P(pts), col, w, pitch=9.0 * k, r=max(1.0, w * k * 0.62))
        else:
            self.d.line(self.P(pts), fill=col, width=max(1, int(w * self.k)), joint='curve')
    cv_lib.L2.line = line

    # ---------------------------------------------------------------- lane outlines: neutral ENAMEL + time grammar
    def mixc(c, f):
        return tuple(int(v * f) for v in c)
    lane_cols = [ENAMEL, mixc(ENAMEL, 0.72), mixc(ENAMEL, 0.55)]
    for i, d_ in enumerate((None, None, 'dot')):
        cv_lib.LANE[i]['col'] = lane_cols[i]
        cv_lib.LANE[i]['dash'] = d_
    cv_lib.LANE[0]['w'] = 4; cv_lib.LANE[1]['w'] = 2.6; cv_lib.LANE[2]['w'] = 2.4
    for i in range(3):
        wr2_lib.LANE_COL[i] = lane_cols[i]
    wr2_units.LANE_COL = wr2_lib.LANE_COL
    wr2_units.LW = (4.0, 2.6, 2.4)

    def outline(L, u, col=None, w=None):
        dep = u['dep']
        c = col or wr2_lib.LANE_COL[dep]
        ww = w or wr2_units.LW[dep]
        poly = wr2_units.WU.u_poly(u)
        pp = poly + [poly[0]]
        L.line(pp, INKC, ww + 4.5)
        if dep == 0 and col is None:      # HOT: glow + the solid bold line
            L.glow(lambda dd: dd.line([(x * L.k, y * L.k) for x, y in pp], fill=ENAMEL + (90,), width=int(8 * L.k)), blur=4, strength=0.8)
        if dep < 2 or col is not None:
            L.line(pp, c, ww)
        else:
            L.line(pp, c, ww, dash='dot')
    wr2_units.outline = outline

    def ring_(L, x, y, R, dep, dead=False):
        col = (150, 150, 160) if dead else wr2_lib.LANE_COL[dep]
        w = wr2_units.LW[dep]
        rr = R - w / 2
        if dep < 2:
            wr2_units.WU._ring_full(L, x, y, rr, w, col)
        else:
            pts = [(x + rr * math.cos(math.radians(a)), y + rr * math.sin(math.radians(a))) for a in range(0, 361, 4)]
            L.line(pts, INKC, w + 3)
            L.line(pts, col, w, dash='dot')
    wr2_units.ring = ring_

    # hollow growth chevrons: outlined V, no dash
    _orig_dash_path = wr2_units.dash_path

    def dash_path(L, pts, col, w, dash, gap, closed=False):
        if closed:
            L.line(list(pts) + [pts[0]], col, w, dash='dot')
        else:
            L.line(pts, col, w)
            L.line(pts, (10, 8, 20), max(1.0, w - 3.6))
    wr2_units.dash_path = dash_path

    # ---------------------------------------------------------------- enemy slate set (token disc = the slate wash, ENAMEL rim)
    def disc(L, x, y, R, kind, dead=False):
        if dead:
            L.ellipse([x - R, y - R, x + R, y + R], fill=(58, 54, 66))
            return
        kc = SLATE.get(kind, (85, 97, 122))
        L.ellipse([x - R, y - R, x + R, y + R], fill=tuple(min(255, int(v * 1.0)) for v in kc))
    wr2_units.disc = disc

    _orig_setup = None

    # ---------------------------------------------------------------- guns: painted pink tracer (L2), no dashes
    def dash_line(L, p0, p1, col, w, dash=(12, 6), ink_w=None, alpha=255):
        lay = L if alpha == 255 else None
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        n = max(6, int(ln / 6))
        pts = []
        for i in range(n + 1):
            t = i / n
            wob = math.sin(t * 9.0 + p0[0] * 0.07) * 0.9
            pts.append((p0[0] + dx * t + nx * wob, p0[1] + dy * t + ny * wob))
        if alpha == 255:
            L.line(pts, INKC, 8.2)
            L.line(pts, PINK, 4.6)
        else:
            tmp = cv_lib.L2()
            tmp.line(pts, INKC, 8.2)
            tmp.line(pts, PINK, 4.6)
            im = tmp.im
            im.putalpha(im.split()[3].point(lambda v: int(v * alpha / 255)))
            L.im.alpha_composite(im)
    wc2.dash_line = dash_line

    # ---------------------------------------------------------------- HP lost at END TURN = cross-hatch (L7)
    _orig_pip = wc2.pip

    def pip(L, st, r, a0, a1, w=wc2.BAR_W):
        if st != 'harm':
            return _orig_pip(L, st, r, a0, a1, w)
        cr = lambda px: math.degrees(px / r)
        b0, b1 = a0 + cr(w / 2), a1 - cr(w / 2)
        ww = w + 1.6
        pts = L.arc_pts(C, r, b0, b1, 8)
        L.glow(lambda dd: dd.line([(x * L.k, y * L.k) for x, y in pts], fill=HARM + (120,), width=int((ww + 6) * L.k)), blur=3, strength=0.7)
        wc2.cap_line(L, pts, INKC, ww + 4.4)
        wc2.cap_line(L, pts, HARM, ww)
        wc2.cap_line(L, pts, (40, 8, 8), ww - 3.2)
        # hatch clipped to the capsule body
        poly = _capsule_poly(L, r, b0, b1, (ww - 3.2) / 2)
        hatch_poly(L, poly, HARM, pitch=3.4, lw=1.3)
    wc2.pip = pip
    for nm in ('bars2', 'hp_ring2'):
        pass

    def _capsule_poly(L, r, b0, b1, hw):
        out, back = [], []
        n = 10
        for i in range(n + 1):
            a = b0 + (b1 - b0) * i / n
            out.append(ppx(C, r + hw, a)); back.append(ppx(C, r - hw, a))
        return out + back[::-1]

    # HUD YOU tally 'lose' segment
    _orig_seg = hud2.seg

    def seg(L, x, y, kind, w=hud2.SEGW, h=hud2.SEGH, al=255):
        if kind != 'lose':
            return _orig_seg(L, x, y, kind, w, h, al)
        box = [x, y - h / 2, x + w, y + h / 2]
        L.glow(lambda dd: dd.rounded_rectangle([(x - 2) * L.k, (y - h / 2 - 2) * L.k, (x + w + 2) * L.k, (y + h / 2 + 2) * L.k], radius=4 * L.k, fill=HARM + (95,)), blur=3, strength=0.8)
        L.rect(box, fill=(44, 8, 8, al), outline=INKC + (al,), w=1.6, r=3)
        pts = [(x + 1.4, y - h / 2 + 1.4), (x + w - 1.4, y - h / 2 + 1.4), (x + w - 1.4, y + h / 2 - 1.4), (x + 1.4, y + h / 2 - 1.4)]
        hatch_poly(L, pts, HARM, pitch=3.6, lw=1.3, edge=1.6)
    hud2.seg = seg

    # enemy HP lost = ours = pink hatch
    _orig_rseg = wr2_units.rseg

    def hp_row(L, u, hp, mx, lose=0, shield=0, shmx=0):
        import wr_state as ST
        ly = wr2_units.cell_layout(u)
        r0, r1 = ly['r0'], ly['r1']
        wp, gp = 18.0, 4.0
        ST.PIPS[u['id']] = []
        w = u['w']
        per = max(1, mx // w)
        idx = 0
        for q in range(w):
            a_start, tot, rm = wr2_units.tray_extent(u, q, per, wp, gp)
            tray = wr2_units.arc_band(ly['t_in'], ly['t_out'], a_start - math.degrees(2.2 / rm), a_start + math.degrees((tot + 2.2) / rm))
            L.poly(tray, fill=(8, 10, 20, 255), outline=INKC, w=1.4)
            for i in range(per):
                lit = idx < hp
                lost = lit and idx >= hp - lose
                aa = a_start + math.degrees(i * (wp + gp) / rm)
                ab = aa + math.degrees(wp / rm)
                if lit and not lost:
                    wr2_units.rseg(L, r0, r1, aa, ab, wr2_units.CREAMC, 3.0)
                elif lost:
                    wr2_units.rseg(L, r0, r1, aa, ab, PINK, 3.0)
                    wr2_units.rseg(L, r0 + 1.6, r1 - 1.6, aa + math.degrees(1.6 / rm), ab - math.degrees(1.6 / rm), (46, 8, 30), 1.2, ink=False)
                    poly = L.band(C, r0 + 1.6, r1 - 1.6, aa + math.degrees(1.6 / rm), ab - math.degrees(1.6 / rm))
                    hatch_poly(L, poly, PINK, pitch=3.6, lw=1.4)
                else:
                    wr2_units.rseg(L, r0, r1, aa, ab, (84, 92, 120), 3.0, ink=True, ow=0.8)
                    da_ = math.degrees(1.4 / rm)
                    wr2_units.rseg(L, r0 + 1.4, r1 - 1.4, aa + da_, ab - da_, (14, 16, 30), 1.6, ink=False)
                ST.PIPS[u['id']].append((aa, ab, r0, r1, lit))
                idx += 1
        if shmx:
            wr2_units.shield_bracket(L, u, r0, r1, shield, shmx)
    wr2_units.hp_row = hp_row
    import asm_units
    if hasattr(asm_units, 'WU'):
        pass


def after_setup():
    """call after asm_r2.setup(): slate kind table, pink hub rim"""
    import wr_geo as GEO, asm_tokens as TK, cv_board as CB9
    from e10lib import KCOL
    for k_, v_ in SLATE.items():
        GEO.KIND_TABLE[k_] = v_
        KCOL[k_] = tuple(min(255, int(c * TK.KIND_TOKEN_F)) for c in v_)
    CB9.HUB['col'] = PINK
