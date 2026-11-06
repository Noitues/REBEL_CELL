"""Stickers and identity: SEND IT, UNDO chip, nameplate, hint, nowords forms. Options keyed A/B/C; 'cur' = E10 as drawn (build10.stickers).
stickers_layer(words, sel) -> full-screen RGBA with undo chip, stickers (one shadow), hint.  sel keys: send, undo, name, mat, snw, hint, hover(bool), locked(bool)."""
import sys, math
sys.dont_write_bytecode = True
from a_kit import *

SEND_RIGHT = 1894
STACK_BOTTOM = 1054


# ----------------------------------------------------------------------------- SEND IT
def send_it(opt, words=True, mat='A', glyph='ring'):
    GL = {'ring': g_go_ring, 'bar': g_go_bar, 'enter': g_enter}[glyph]
    f = anton(62 * S3)
    if opt == 'A':
        tw = anton(62).getlength('SEND IT')
        w, h = int(tw + 44), 90

        def content(d, S, ox, oy, w, h):
            if words:
                text_ink(d, (ox + w * S / 2, oy + h * S / 2 + 3 * S), 'SEND IT', 62, S)
            else:
                GL(d, ox + w * S / 2, oy + h * S / 2, 34 * S, INK, VY_TOP)
        return vinyl2(w, h, 62, content, VY_TOP, VY_BOT, -3, mat)
    if opt == 'B':
        w, h = 176, 158

        def content(d, S, ox, oy, w, h):
            if words:
                text_ink(d, (ox + 22 * S, oy + 46 * S), 'SEND', 62, S, anchor='lm')
                text_ink(d, (ox + 22 * S, oy + 112 * S), 'IT', 62, S, anchor='lm')
                GL(d, ox + 118 * S, oy + 110 * S, 28 * S, INK, VY_TOP)
            else:
                GL(d, ox + w * S / 2, oy + h * S / 2, 46 * S, INK, VY_TOP)
        return vinyl2(w, h, 62, content, VY_TOP, VY_BOT, -3, mat)
    if opt == 'C':
        w = h = 176

        def content(d, S, ox, oy, w, h):
            cx, cy = ox + w * S / 2, oy + h * S / 2
            ring = [(cx + 80 * S * math.cos(math.radians(a)), cy + 80 * S * math.sin(math.radians(a))) for a in range(0, 360, 6)]
            for i in range(0, len(ring), 2):
                pstroke(d, ring[i:i + 2], INK, 2.2 * S, cap=False)
            if words:
                text_ink(d, (cx, cy - 30 * S + 3 * S), 'SEND', 62, S)
                text_ink(d, (cx - 22 * S, cy + 34 * S + 3 * S), 'IT', 62, S)
                GL(d, cx + 34 * S, cy + 36 * S, 22 * S, INK, VY_TOP)
            else:
                GL(d, cx, cy, 44 * S, INK, VY_TOP)
        return vinyl2(w, h, 62, content, VY_TOP, VY_BOT, -3, mat, shape='circle', r_in=10)
    raise KeyError(opt)


# ----------------------------------------------------------------------------- nameplate
def nameplate(opt, words=True, mat='A', glyph='tally'):
    def emblem(d, S, cx, cy, R):
        d.ellipse([cx - R * S, cy - R * S, cx + R * S, cy + R * S], fill=(16, 40, 60), outline=INK, width=int(2.4 * S))
        g_breaker(d, cx, cy, R * 0.62 * S, (150, 240, 255), INK)

    if opt == 'A':
        w, h = 214, 80

        def content(d, S, ox, oy, w, h):
            emblem(d, S, ox + 36 * S, oy + h * S / 2, 24)
            if words:
                text_ink(d, (ox + 66 * S, oy + 29 * S), 'CELL-9', 34, S, anchor='lm')
                text_ink(d, (ox + 66 * S, oy + 60 * S), '// BREAKER', 22, S, anchor='lm')
            else:
                tally(d, ox + 80 * S, oy + h * S / 2, 9, 34 * S, INK, (150, 240, 255), 3.2 * S, 11 * S)
        return vinyl2(w, h, 34, content, VC_TOP, VC_BOT, 2, mat)
    if opt == 'B':
        tw = anton(30).getlength('CELL-9 // BREAKER')
        w, h = int(tw + 40 + 56), 56

        def content(d, S, ox, oy, w, h):
            emblem(d, S, ox + 30 * S, oy + h * S / 2, 19)
            if words:
                text_ink(d, (ox + 58 * S, oy + h * S / 2 + 2 * S), 'CELL-9 // BREAKER', 30, S, anchor='lm')
            else:
                tally(d, ox + 74 * S, oy + h * S / 2, 9, 28 * S, INK, (150, 240, 255), 3 * S, 10 * S)
        return vinyl2(w, h, 30, content, VC_TOP, VC_BOT, 2, mat)
    if opt == 'C':
        w = h = 160

        def content(d, S, ox, oy, w, h):
            cx = ox + w * S / 2
            emblem(d, S, cx, oy + 40 * S, 28)
            if words:
                text_ink(d, (cx, oy + 94 * S), 'CELL-9', 32, S)
                text_ink(d, (cx, oy + 122 * S), '// BREAKER', 20, S)
            else:
                tally(d, cx - 32 * S, oy + 110 * S, 9, 30 * S, INK, (150, 240, 255), 3 * S, 10 * S)
        return vinyl2(w, h, 32, content, VC_TOP, VC_BOT, 2, mat, shape='circle')
    raise KeyError(opt)


# ----------------------------------------------------------------------------- UNDO chip (terminal) + hint (drawn on L2)
GREY_LOCK = (118, 128, 146)


def keycap(L, x, y, s='Z', col=CYAN, h=28):
    L.rect([x, y - h / 2, x + h, y + h / 2], fill=(10, 24, 40, 255), outline=col, w=2, r=5)
    L.text((x + h / 2, y + 1), s, 18, 'mono', fill=col)
    return h


def undo_glyph(L, cx, cy, R, col):
    pts = []
    for i in range(0, 231, 10):
        a = math.radians(-20 - i)
        pts.append((cx + R * math.cos(a), cy + R * math.sin(a)))
    L.line(pts, INK, 5.2)
    L.line(pts, col, 2.6)
    a = math.radians(-250)
    dirv = math.atan2(-math.cos(a), math.sin(a))
    hd = []
    for sg in (1, -1):
        b_ = dirv + math.pi + sg * 0.62
        hd.append((pts[-1][0] + R * 0.8 * math.cos(b_), pts[-1][1] + R * 0.8 * math.sin(b_)))
    hd = [hd[0], pts[-1], hd[1]]
    L.line(hd, INK, 5.2)
    L.line(hd, col, 2.6)


def undo_chip(L, opt, box, locked=False, words=True):
    """box = (x0, y0, x1, y1) of the chip. locked: grey edge + grey tick (undo spent / nothing to undo)"""
    col = GREY_LOCK if locked else CYAN
    tcol = GREY_LOCK if locked else CRT_TXT
    x0, y0, x1, y1 = box
    cy = (y0 + y1) / 2 if opt == 'C' else y0 + 19
    L.rect(box, fill=(5, 13, 28, 240), outline=col + (230,), w=2, r=8)
    for yy in range(int(y0) + 5, int(y1) - 3, 4):
        L.line([(x0 + 5, yy), (x1 - 5, yy)], (0, 0, 0, 38), 1)
    if opt == 'A':          # word 22 leads, keycap right
        if words:
            L.text((x0 + 14, cy + 1), 'UNDO', 22, 'mono', fill=tcol, anchor='lm')
        else:
            undo_glyph(L, x0 + 28, cy, 11, tcol)
        xk = x1 - 40
        if locked:
            L.line([(xk - 4, cy + 1), (xk + 6, cy + 9), (xk + 24, cy - 9)], INK, 6)
            L.line([(xk - 4, cy + 1), (xk + 6, cy + 9), (xk + 24, cy - 9)], GREY_LOCK, 3)
        else:
            keycap(L, xk, cy)
    elif opt == 'B':        # glyph-led: [undo arc] UNDO [Z]
        undo_glyph(L, x0 + 24, cy, 10, tcol)
        if words:
            L.text((x0 + 44, cy + 1), 'UNDO', 20, 'mono', fill=tcol, anchor='lm')
        xk = x1 - 38
        if locked:
            L.line([(xk, cy + 1), (xk + 8, cy + 9), (xk + 24, cy - 9)], INK, 6)
            L.line([(xk, cy + 1), (xk + 8, cy + 9), (xk + 24, cy - 9)], GREY_LOCK, 3)
        else:
            keycap(L, xk, cy, h=26)
    else:                   # C: 'press Z to UNDO' reads as a link row: keycap first
        if locked:
            L.line([(x0 + 12, cy + 1), (x0 + 20, cy + 9), (x0 + 36, cy - 9)], INK, 6)
            L.line([(x0 + 12, cy + 1), (x0 + 20, cy + 9), (x0 + 36, cy - 9)], GREY_LOCK, 3)
        else:
            keycap(L, x0 + 10, cy, h=26)
        if words:
            L.text((x0 + 48, cy + 1), 'UNDO', 20, 'mono', fill=tcol, anchor='lm')
        undo_glyph(L, x1 - 24, cy, 10, tcol)


def hint_line(L, opt, cx, y, wd, words=True):
    """> turn_resolve.exe  mono 18 TEXT_MID, fully visible"""
    s = '> turn_resolve.exe'
    if opt == 'A':
        tw = L.tw(s, 18, 'mono')
        x0 = cx - (tw + 14) / 2
        L.text((x0, y), s, 18, 'mono', fill=TXT_MID, anchor='lm')
        L.rect([x0 + tw + 4, y - 7, x0 + tw + 12, y + 7], fill=TXT_MID + (255,), r=1)
    elif opt == 'B':
        L.rect([cx - wd / 2, y - 14, cx + wd / 2, y + 14], fill=(5, 13, 28, 235), outline=(70, 110, 130, 220), w=2, r=6)
        tw = L.tw(s, 18, 'mono')
        x0 = cx - (tw + 14) / 2
        L.text((x0, y + 1), s, 18, 'mono', fill=TXT_MID, anchor='lm')
        L.rect([x0 + tw + 4, y - 7, x0 + tw + 12, y + 7], fill=CYAN + (255,), r=1)


# ----------------------------------------------------------------------------- stack layout + layer
def stickers_layer(words=True, sel=None, mat_default='A'):
    sel = sel or {}
    base = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    L = L2()
    mat = sel.get('mat', mat_default)
    so, uo, no, ho = sel.get('send', 'A'), sel.get('undo', 'A'), sel.get('name', 'A'), sel.get('hint', 'A')
    snw = sel.get('snw', 'A')
    glyph = {'A': 'ring', 'B': 'bar', 'C': 'enter'}[snw]
    if not words:
        ho = 'none'
        if 'name' not in sel:
            no = {'A': 'A', 'B': 'C', 'C': 'A'}[snw]
    st = send_it(so, words, mat, glyph)
    iw, ih = st.size
    undo_top = uo in ('A', 'B')
    below = []
    y_bot = STACK_BOTTOM
    if ho in ('A', 'B'):
        hh = 30
        below.append(('hint', hh))
    if uo == 'C':
        below.insert(0, ('undo', 40))
    total_below = sum(h for _, h in below) + 4 * len(below)
    sy = y_bot - total_below - ih
    sx = SEND_RIGHT - iw
    cx = sx + iw / 2
    plate_w = iw - 24
    y = sy + ih
    if undo_top:
        if uo == 'A':
            box = (sx + 14, sy - 34, SEND_RIGHT - 14, sy + 16)
        else:
            box = (SEND_RIGHT - 190, sy - 30, SEND_RIGHT - 18, sy + 12)
            # hinge clasps: two ink tabs tie the chip to the sticker
            for hx in (box[0] + 26, box[2] - 26):
                L.rect([hx - 7, box[3] - 6, hx + 7, box[3] + 14], fill=INK + (255,), outline=CYAN + (230,), w=2, r=2)
        undo_chip(L, uo, box, sel.get('locked', False), words)
    ycur = y - 8
    for kind, hh in below:
        if kind == 'undo':
            box = (sx + 30, ycur - 6, SEND_RIGHT - 30, ycur + 34)
            undo_chip(L, 'C', box, sel.get('locked', False), words)
            ycur += hh + 4
        else:
            hint_line(L, ho, cx, ycur + 14, plate_w - 10, words)
            ycur += hh + 4
    base.alpha_composite(L.done())
    # nameplate first (under nothing), sticker on top of the chip
    put_sticker(base, st, (sx, sy))
    if ho == 'C' and sel.get('hover'):
        L2_ = L2()
        s = '> turn_resolve.exe'
        tw = L2_.tw(s, 18, 'mono') + 28
        tb = (cx - tw / 2, sy - 62, cx + tw / 2, sy - 28)
        terminal(L2_, tb)
        L2_.text((cx, sy - 45), s, 18, 'mono', fill=TXT_MID)
        base.alpha_composite(L2_.done())
    # nameplate
    nm = nameplate(no, words, mat, 'tally')
    nw, nh = nm.size
    if no == 'A':
        pos = (26, 1056 - nh)
    elif no == 'B':
        pos = (1066, 392)
    else:
        pos = (24, 1056 - nh)
    put_sticker(base, nm, pos)
    return base, dict(send=(sx, sy, iw, ih), name=pos + (nw, nh))


def stickers_cur(words=True):
    """E10 as drawn (build10.stickers)"""
    import build10 as B10
    base = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    L = L2()
    NOW['words'] = words
    B10.stickers(base, L)
    base.alpha_composite(L.done())
    return base
