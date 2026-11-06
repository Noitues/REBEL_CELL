"""R2 plan / preview marks: trigger_path (R1 A refined), trigger_tower_hit (3 options, NEW), twist_badge (pill on the ring_tags A pennant anchor),
refund_burst (coin token + REFUND tag), resolve_fire_lines (gun tracer at 55 percent + result marks).  Ring tags P = outer_rings R2 pick copy (anchor only)."""
import sys, math, random
sys.dont_write_bytecode = True
from a2_kit import *
import a_plan as P1
from a_plan import wax_v, tag_of
import cv_board as CB
import o_misc as OM
import a2_glyphs as GLY
from a2_stick import kit_plate

PTHREAT = (255, 28, 44)
REFUND_PX, REFUND_W, REFUND_H = 18, 94, 26     # the REFUND tag (rb_patch sets the rebuild's 23 px mono: cap 16.1)
HARM_C = (255, 68, 51)


# ---------------------------------------------------------------------------- ring tags: copy of outer_rings R2 'P' (rect tag, Anton 20, lane colour) so the badge anchors on the real tag
def tag_geom(L, d, w_):
    ri, ro = CB.ring_geom(d)
    x, y = ppx(C, ro - 17, 30)
    depth, wv = OM.tag_words(d, w_)
    if NOW['words']:
        s = depth + ((' ' + wv) if wv else '')
        wd = L.tw(s.replace('+', ''), 20, 'anton') + 18 + (10 if depth.startswith('+') else 0)
    else:
        wd = 44
    return x, y, wd, depth, wv


def ring_tags_p(L, f):
    for d in range(3):
        w_ = f['rings_wave'][d]
        lane = LANE[d]
        x, y, wd, depth, wv = tag_geom(L, d, w_)
        if NOW['words']:
            L.rect([x - wd / 2, y - 13, x + wd / 2, y + 13], fill=(8, 10, 18, 250), outline=lane['col'], w=2.4, r=6)
            tx0 = x - wd / 2 + 9
            if depth.startswith('+'):
                OM.plus_glyph(L, tx0 + 3, y, lane['col'], 4.2, 2.4)
                tx0 += 10
                txt = depth[1:] + ((' ' + wv) if wv else '')
            else:
                txt = depth + ((' ' + wv) if wv else '')
            L.text((tx0, y + 1), txt, 20, 'anton', fill=lane['col'], anchor='lm', stroke=1.4)
        else:
            L.rect([x - wd / 2, y - 13, x + wd / 2, y + 13], fill=(8, 10, 18, 250), outline=INK, w=2.4, r=6)
            OM.lane_swatch(L, x - 16, x + 16, y - 5, d)
            if w_ >= 0:
                OM.tally_bars(L, x, y + 6, w_ + 1, (244, 247, 252), h=8, pitch=5.4, w=2.6)


# ---------------------------------------------------------------------------- twist_badge
def twist_badge(L, f, opt='A'):
    """A: pill, the tag's 26 px height, docked 3 px off the tag's clockwise edge; library Twist glyph 20 px + one chevron per sector turned (twr direction).
    A2: the same pill with a pointed clockwise end (pennant) that continues the tag's silhouette."""
    ring, dirn = f['twr']
    if not dirn:
        return
    import r2_misc as _M2
    ax_, ay_ = _M2.tag_anchor(L, f, ring)      # ASSEMBLY (Y11): the outer_rings tag is the anchor
    y = ay_
    xr = ax_ + 3
    n = abs(dirn)
    wp = 36 + 11 * n
    h = 26
    chev = lambda cx_: [(cx_ - 4, y - 8), (cx_ + 4, y), (cx_ - 4, y + 8)]
    if opt == 'A':
        L.rect([xr, y - h / 2, xr + wp, y + h / 2], fill=(26, 22, 4, 250), outline=YEL, w=2.4, r=h / 2)
    else:
        pts = [(xr, y - h / 2), (xr + wp - 6, y - h / 2), (xr + wp + 4, y), (xr + wp - 6, y + h / 2), (xr, y + h / 2)]
        L.poly(pts, fill=(26, 22, 4, 250), outline=INK, w=4.6)
        L.line(pts + [pts[0]], YEL, 2.4)
    L.glyph(GLY.TWIST, 20, (xr + 15, y), YEL)
    for q in range(n):
        L.line(chev(xr + 33 + q * 9), INK, 7.5)
        L.line(chev(xr + 33 + q * 9), YEL, 4.2)


# ---------------------------------------------------------------------------- refund burst
def refund_place(L, f, opt='A', tok='A', words=True):
    kl = f['kills'][-1]
    u = [u for u in f['units'] if u['id'] == kl['uid']][0]
    tp0 = token_pos(u)

    def tagbox(cx, cy, w=None):
        w = w or REFUND_W
        kit_plate(L, (cx - w / 2, cy - REFUND_H / 2, cx + w / 2, cy + REFUND_H / 2), CYAN, 2, 6)
        if words:
            L.text((cx, cy + 1), 'REFUND', REFUND_PX, 'mono', fill=CYAN)
    if opt == 'A':          # on the cell's open stretch, clear of the pencil X and the dead token; tag under it
        x, y = ppx(C, rmid(0) - 1, 203)
        refund_token(L, x, y, 44, tok)
        tagbox(x, y + 42)
    else:                   # A2: on the dead token's shoulder, tag under the pair
        x, y = tp0[0] + 25, tp0[1] - 20
        refund_token(L, x, y, 40, tok)
        tagbox(tp0[0] + 6, tp0[1] + 45)


# ---------------------------------------------------------------------------- resolve fire lines
def fire_lines(L, f, opt='A'):
    """A: the decide-state gun tracers (dash 12/6 cyan, ends on the target) with their result marks at 55 percent.  A2: 70 percent."""
    sub = L2()
    gun_tracers10(sub, f)
    k = 0.55 if opt == 'A' else 0.70
    im = sub.im
    im.putalpha(im.split()[3].point(lambda v: int(v * k)))
    L.im.alpha_composite(im)


# ---------------------------------------------------------------------------- trigger_tower_hit: Trigger pierce that reaches the tower (LATENT; hypothetical entry)
def tower_hit(L, f, dep, sec, hit, opt):
    ang = 60 * sec
    ri1, ro1 = CB.ring_geom(dep)
    p0 = ppx(C, ro1 - 12, ang)
    rim = RS['s1'] + 6
    q = ppx(C, rim, ang)
    if opt == 'A':          # wax threat line to the rim + the vector chevron stack just inside it
        wax(L, [p0, q], PTHREAT, 7, 52, 0.6)
        chev_stack(L, RS['s1'] - 10, ang, hit, RED)
    elif opt == 'B':        # the stack itself is pencilled: open hand-drawn V per hit, nested, drawn along the line
        wax(L, [p0, ppx(C, RS['s1'] + 14, ang)], PTHREAT, 7, 52, 0.6)
        dirv = math.atan2(C[1] - p0[1], C[0] - p0[0])
        for i in range(hit):
            tip = ppx(C, RS['s1'] + 1 - i * 13, ang)
            wax_v(L, tip, dirv, 17, PTHREAT, 60 + i, 6)
    else:                   # C: line ends in a hand-drawn jab bar across the rim, chevron stack sits on the line on the ring side
        wax(L, [p0, ppx(C, RS['s1'] + 8, ang)], PTHREAT, 7, 52, 0.6)
        wax([L][0], [ppx(C, RS['s1'] + 6, ang - 3.6), ppx(C, RS['s1'] + 6, ang + 3.6)], PTHREAT, 6, 53, 0.3)
        chev_stack(L, RS['s1'] + 34, ang, hit, RED)
