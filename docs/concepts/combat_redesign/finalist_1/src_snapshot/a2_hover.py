"""R2 hover (p2b) pieces: hover_tag (A, bottom-left callout on the terminal kit plate, PENCIL_PLAN wax leader, Plex 20, <= 41 chars a line),
hovered_cell_outline (= focus_brackets drawing), plus nowords tag.  hover_path / hover_slice_highlight reuse the R1 A drawings (a_hover) unchanged."""
import sys, math
sys.dont_write_bytecode = True
from a2_kit import *
import a_hover as HV
from a_hover import rtext, rw, tag_texts, hv_unit, path_pts
from a2_stick import kit_plate, paste_glyph
import a2_glyphs as GLY
import build10 as B10

J = B10.J
LH = 26


def tag_lines(opt='A'):
    """text lines, content identical to E10's two long lines (words reflowed only).  A: 5 lines <= 33 chars.  A2: 4 lines <= 41 chars."""
    head, hp, hit, land, cost, sl = tag_texts()
    sls = ' + '.join(sl)
    if opt == 'A':
        return [[(head + '  ' + hp, True)], [(hit, False)], [(land, False)], [(cost, False)], [(sls, True)]]
    return [[(head + '  ' + hp, True), ('  ' + hit, False)], [(land, False)], [(cost, False)], [(sls, True)]]


def anchor_pt(f):
    u = hv_unit(f)
    ri, ro = CB.ring_geom(u['dep'])
    a0, a1 = span(u)
    cands = [ppx(C, (ri + ro) / 2, a0 + 9), ppx(C, (ri + ro) / 2, a1 - 9)]
    return min(cands, key=lambda p: math.hypot(p[0] - 180, p[1] - 800))     # the cell end nearest the bottom-left tag


def tag_box(L, opt, bottom):
    lines = tag_lines(opt)
    w = max(sum(rw(L, s, 20, b) for s, b in ln) for ln in lines) + 32
    h = LH * len(lines) + 18
    return lines, w, h, (24, bottom - h)


TAG_X0, TAG_Y0 = 1092, 404       # fix 4: off the board, in the free room zone right of the wheel (r >= 544 from (536,540)), under the p2b HUD bottom (384)


def leader(L, x0, y0, h):
    """fix 4: wax leader from the hovered token (its rim) to the tag's left edge; the tag itself stays off the wheel"""
    import asm_units as AU
    import copy as _cp
    u = hv_unit(_cp.deepcopy(J['f1']))
    tp = AU.token_pos(u)
    st = (x0, y0 + h * 0.5)
    d = math.hypot(st[0] - tp[0], st[1] - tp[1])
    anc = (tp[0] + (st[0] - tp[0]) / d * 20, tp[1] + (st[1] - tp[1]) / d * 20)
    mid = (st[0] - 34, st[1])
    pl = [anc, (mid[0] - 40, st[1] + (anc[1] - st[1]) * 0.1), mid, st]
    L.line(pl, INK, 6.5)
    L.line(pl, YEL, 2.6)
    L.ellipse([anc[0] - 6, anc[1] - 6, anc[0] + 6, anc[1] + 6], fill=YEL, outline=INK, w=2.4)


def hover_tag(L, f, opt='A', bottom=944):
    lines, w, h, _ = tag_box(L, opt, bottom)
    x0, y0 = TAG_X0, TAG_Y0
    leader(L, x0, y0, h)
    kit_plate(L, (x0, y0, x0 + w, y0 + h))
    for i, ln in enumerate(lines):
        xx = x0 + 16
        for s, b in ln:
            xx += rtext(L, (xx, y0 + 22 + i * LH), s, 20, WHITE, b)
    return (x0, y0, x0 + w, y0 + h)


def hover_tag_nowords(L, f, bottom=944):
    """wordless tag: kind glyph + tallies.  width x3 = 3 strokes, HP 9/9 = 9 cream strokes, hit 2 now = 2 HARM, grown 0 = none, lands in 2 = 2 dots, 3 per slice = 3 HARM,
    cost 6 = 6 HARM strokes, then slice glyphs with their tallies."""
    hv = J['hover']
    fz = hv['fate']
    x0, y0 = TAG_X0, TAG_Y0
    w, h = 330, 112
    leader(L, x0, y0, h)
    kit_plate(L, (x0, y0, x0 + w, y0 + h))
    S = 2
    t = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    row = lambda i: (18 + i * 26) * S
    paste_glyph(d, 'C_PACKET' if False else KIND[hv['kind']][1], 30 * S, row(0), 26 * S, WHITE, 2 * S)
    tally(d, 58 * S, row(0), hv['w'], 20 * S, WHITE, INK, 3 * S, 9 * S)
    tally(d, 130 * S, row(0), hv['hp'], 20 * S, CREAM, INK, 3 * S, 8 * S)
    tally(d, 24 * S, row(1), hv['hit'], 20 * S, RED, INK, 3 * S, 9 * S)
    tally(d, 130 * S, row(1), fz['k'], 20 * S, WHITE, INK, 3 * S, 9 * S)
    tally(d, 200 * S, row(1), fz['hits'][0][2], 20 * S, RED, INK, 3 * S, 9 * S)
    tally(d, 24 * S, row(2), sum(h_[3] for h_ in fz['hits']), 20 * S, RED, INK, 3 * S, 9 * S)
    x = 24 * S
    for (sec, sl, hit, tohp) in fz['hits']:
        x += 4 * S
        tally(d, x, row(3) + 4 * S, tohp, 18 * S, WHITE, INK, 3 * S, 8 * S)
        x += 44 * S
    t = t.resize((w, h), Image.LANCZOS)
    L.im.alpha_composite(t.resize((w * L.k, h * L.k), Image.LANCZOS), (int(x0 * L.k), int(y0 * L.k)))
    return (x0, y0, x0 + w, y0 + h)


def hover_cell(L, f, fopt='A', w=FB_W):
    """hovered_cell_outline = focus_brackets on the cell band"""
    u = hv_unit(f)
    ri, ro = CB.ring_geom(u['dep'])
    a0, a1 = span(u)
    focus_brackets(L, 'band', dict(ri=ri + 4, ro=ro - 4, a0=a0 + 3, a1=a1 - 3), fopt, w=w, arm=26, grow=0)


# ---------------------------------------------------------------------------- hover_path (R1 A refined: weight steps) and hover_slice_highlight (A + variant)
def hover_path(L, f, opt='A'):
    """A: continuous wax 7 px + ink, open hand-drawn arrowhead 19 px, start dot on the cell.  A2: 6 px wax, longer open head 23 px."""
    pts = path_pts(f)
    tip = pts[-1]
    d_ = math.atan2(tip[1] - pts[-4][1], tip[0] - pts[-4][0])
    w, hd = (7, 19) if opt == 'A' else (6, 23)
    wax(L, pts, YEL, w, 11, 0.8)
    HV.wax_v(L, tip, d_, hd, YEL, 12, w)
    x, y = pts[0]
    L.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(6, 3, 8, 235))
    L.ellipse([x - 4.2, y - 4.2, x + 4.2, y + 4.2], fill=YEL)


def hover_slice(L, f, opt='A'):
    """A: yellow rim arc in the trim slot (the hovered unit's own trim is removed by the caller).  A2: + a wax end tick across the rim at both ends."""
    HV.hover_slice(L, f, 'A')
    if opt == 'A2':
        for sec in HV.hover_sectors(f):
            for a in (60 * sec - 26.5, 60 * sec + 26.5):
                wax(L, [ppx(C, RS['s1'] - 10, a), ppx(C, RS['s1'] + 8, a)], YEL, 4.4, 21 + sec, 0.3)
