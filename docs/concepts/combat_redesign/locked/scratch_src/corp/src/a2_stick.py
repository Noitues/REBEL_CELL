"""R2 stickers and identity: SEND IT (A + states), UNDO tab, nameplate (Breaker crest), bottom hint, nowords forms.
stack_layer(words, sel) -> (RGBA full-screen layer, info).
sel: send(A|A2) undo(A|A2) name(A|A2) mat(A|B) hint(A|A2) snw(A|B) state(None|hover|focus|pressed|disabled) sopt(A|B|C states option) locked fopt(A|B|C)"""
import sys, math
sys.dont_write_bytecode = True
import numpy as np
from a2_kit import *
import a2_glyphs as GLY
from bb_lib import glyph_rgba

RIGHT = 1896            # column right edge; the sticker's whole image (die-cut + tilt) stays inside
BOTTOM = 1056           # 24 px margin
GREY_LOCK = (118, 128, 146)
TERM_FILL = (5, 13, 28, 237)        # terminal kit: 93 percent
CY_PLATE = (150, 240, 255)


# ---------------------------------------------------------------------------- terminal kit plate (shared with the hover tag)
def kit_plate(L, box, col=CYAN, w=2, r=8, hero=False):
    import hud2      # ASSEMBLY (Y5): hud2.P is the kit plate
    hud2.P(L, box, 'bill' if hero else 'plate', col=col, w=(3 if hero else w), r=r)


# ---------------------------------------------------------------------------- SEND IT
def send_base(opt='A', words=True, mat='A', glyph='ring', top=VY_TOP, bot=VY_BOT, tilt=-3, ink=INK, size=None):
    GL = {'ring': g_go_ring, 'bar': g_go_bar}[glyph]
    sz = size or (62 if opt == 'A' else 56)
    tw = anton(sz).getlength('SEND IT')
    w, h = int(tw + 44 * sz / 62), int(90 * sz / 62)

    def content(d, S, ox, oy, w, h):
        if words:
            text_ink(d, (ox + w * S / 2, oy + h * S / 2 + 3 * S), 'SEND IT', sz, S, col=ink)
        else:
            GL(d, ox + w * S / 2, oy + h * S / 2, 34 * S, ink, top)
    return vinyl2(w, h, sz, content, top, bot, tilt, mat)


def _tint(im, k):
    a = np.asarray(im, np.float32).copy()
    m = (a[..., 3:4] > 0)
    a[..., :3] = np.where(m, np.clip(a[..., :3] * k, 0, 255), a[..., :3])
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def _gray(im, amt=0.9, k=1.0):
    a = np.asarray(im, np.float32).copy()
    lum = (a[..., :3] * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1, keepdims=True)
    a[..., :3] = np.clip((a[..., :3] * (1 - amt) + lum * amt) * k, 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def _scale(im, k):
    return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)


def send_state(sopt, state, words=True, mat='A', glyph='ring'):
    """returns (image, shadow dict).  focus = rest + brackets (drawn by the caller).
    A lift/sink: hover lifts (bigger, brighter, longer softer shadow), pressed sinks (smaller, darker, shadow collapses), disabled = grey vinyl with flat shadow.
    B rim light/inset: hover = white inner rim + warm bloom, no move; pressed = inset (inner top shadow); disabled = 50 percent see-through grey, no shadow.
    C straighten: hover / pressed square the sticker to 0 deg; pressed dims; disabled = grey lacquer with the peeled corner."""
    sh = dict(k=0.5, blur=8, off=(4, 8))
    if state in (None, 'rest', 'focus'):
        return send_base('A', words, mat, glyph), sh
    if sopt == 'A':
        if state == 'hover':
            im = send_base('A', words, mat, glyph, (255, 246, 140), (255, 196, 40))
            return _scale(im, 1.03), dict(k=0.55, blur=12, off=(7, 13))
        if state == 'pressed':
            im = _tint(send_base('A', words, mat, glyph, (232, 206, 70), (214, 148, 10)), 0.96)
            return _scale(im, 0.97), dict(k=0.4, blur=4, off=(1, 3))
        im = _gray(send_base('A', words, mat, glyph, (214, 216, 222), (150, 154, 166), ink=(70, 72, 84)), 0.2)
        return im, dict(k=0.3, blur=4, off=(2, 4))
    if sopt == 'B':
        if state == 'hover':
            im = send_base('A', words, mat, glyph, (255, 244, 130), (255, 190, 30))
            a = im.split()[3]
            core = a.filter(ImageFilter.MinFilter(7))
            ring = Image.fromarray(np.clip(np.asarray(a, np.float32) - np.asarray(core, np.float32), 0, 255).astype(np.uint8))
            white = Image.new('RGBA', im.size, (255, 255, 255, 0))
            white.putalpha(ring.point(lambda v: int(v * 0.0)))
            pad = 20
            bloom = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (255, 214, 60, 0))
            ba = Image.new('L', bloom.size, 0)
            ba.paste(a, (pad, pad))
            bloom.putalpha(ba.filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.6)))
            bloom.alpha_composite(im, (pad, pad))
            # white inner rim: 2 px just inside the die-cut paper edge, over the plate only
            return bloom, dict(k=0.5, blur=8, off=(4, 8), pad=pad)
        if state == 'pressed':
            im = send_base('A', words, mat, glyph, (232, 168, 20), (255, 196, 40))
            a = np.asarray(im.split()[3], np.float32)
            inner = np.asarray(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(4)), np.float32)
            edge = np.clip(inner / 255.0 - np.roll(inner, 6, 0) / 255.0, 0, 1)
            arr = np.asarray(im, np.float32).copy()
            arr[..., :3] *= (1 - edge[..., None] * 0.55)
            return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA'), dict(k=0.3, blur=3, off=(1, 2))
        im = _gray(send_base('A', words, mat, glyph, (214, 216, 222), (150, 154, 166), ink=(60, 62, 76)), 0.85)
        im.putalpha(im.split()[3].point(lambda v: int(v * 0.5)))
        return im, dict(k=0.0, blur=1, off=(0, 0))
    if state == 'hover':
        im = send_base('A', words, mat, glyph, (255, 244, 130), (255, 190, 30), tilt=0)
        return _scale(im, 1.02), dict(k=0.55, blur=10, off=(5, 10))
    if state == 'pressed':
        im = _tint(send_base('A', words, mat, glyph, (236, 214, 80), (222, 156, 14), tilt=0), 0.94)
        return _scale(im, 0.97), dict(k=0.4, blur=4, off=(1, 3))
    im = _gray(send_base('A', words, 'C', glyph, (214, 216, 222), (150, 154, 166), ink=(70, 72, 84)), 0.85)
    return im, dict(k=0.3, blur=4, off=(2, 4))


# ---------------------------------------------------------------------------- nameplate (Breaker crest, two lines)
def paste_glyph(d, name, cx, cy, px, col, ink_px):
    g = glyph_rgba(name, int(px), int(ink_px), fill=col)
    d._image.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))


def _vk(c, k=0.80):
    """fix 3: value and saturation both x0.80 (HSV)"""
    import colorsys
    h_, s_, v_ = colorsys.rgb_to_hsv(*[x / 255.0 for x in c])
    return tuple(int(round(x * 255)) for x in colorsys.hsv_to_rgb(h_, s_ * k, v_ * k))


NP_TOP, NP_BOT = _vk(VC_TOP), _vk(VC_BOT)


def nameplate(opt='A', words=True, mat='A'):
    w, h = (214, 80) if opt == 'A' else (232, 80)

    def emblem(d, S, cx, cy, R):
        d.ellipse([cx - R * S, cy - R * S, cx + R * S, cy + R * S], fill=(12, 30, 46), outline=INK, width=int(2.4 * S))
        paste_glyph(d, GLY.CREST, cx, cy, R * 1.34 * S, (92, 225, 255), R * 1.34 * S * 0.075)

    def content(d, S, ox, oy, w, h):
        if opt == 'A':
            emblem(d, S, ox + 36 * S, oy + h * S / 2, 24)
            tx = ox + 70 * S
        else:               # A2: crest on the right end, text first
            emblem(d, S, ox + (w - 34) * S, oy + h * S / 2, 22)
            tx = ox + 18 * S
        if words:
            text_ink(d, (tx, oy + 29 * S), 'CELL-9', 34, S, anchor='lm')
            text_ink(d, (tx, oy + 60 * S), '// BREAKER', 22, S, anchor='lm')
        else:
            tally(d, tx + 4 * S, oy + h * S / 2, 9, 34 * S, INK, (150, 240, 255), 3.2 * S, 11 * S)
    return vinyl2(w, h, 34, content, NP_TOP, NP_BOT, 2, mat)


# ---------------------------------------------------------------------------- UNDO tab + hint
def keycap(L, x, y, s='Z', col=CYAN, h=28):
    L.rect([x, y - h / 2, x + h, y + h / 2], fill=(10, 24, 40, 255), outline=col, w=2, r=5)
    if NOW['words']:
        L.text((x + h / 2, y + 1), s, 18, 'mono', fill=col)
    else:                   # a key label is not a word: drawn as strokes so it survives words-off
        L.line([(x + 8, y - 6), (x + h - 8, y - 6), (x + 8, y + 6), (x + h - 8, y + 6)], col, 2.6)


def undo_arc(L, cx, cy, R, col):
    pts = [(cx + R * math.cos(math.radians(-20 - i)), cy + R * math.sin(math.radians(-20 - i))) for i in range(0, 231, 10)]
    L.line(pts, INK, 5.2)
    L.line(pts, col, 2.6)
    a = math.radians(-250)
    dirv = math.atan2(-math.cos(a), math.sin(a))
    hd = [(pts[-1][0] + R * 0.8 * math.cos(dirv + math.pi + s * 0.62), pts[-1][1] + R * 0.8 * math.sin(dirv + math.pi + s * 0.62)) for s in (1, -1)]
    hd = [hd[0], pts[-1], hd[1]]
    L.line(hd, INK, 5.2)
    L.line(hd, col, 2.6)


def undo_tab(L, box, opt='A', locked=False, words=True):
    """terminal-kit tab: word 22 + Z keycap, locked = grey edge + grey tick.  The sticker overlaps its lower edge."""
    col = GREY_LOCK if locked else CYAN
    tcol = GREY_LOCK if locked else CRT_TXT
    x0, y0, x1, y1 = box
    kit_plate(L, box, col)
    cy = y0 + 19
    if words:
        if opt == 'A2':
            undo_arc(L, x0 + 26, cy, 9, tcol)
            L.text((x0 + 46, cy + 1), 'UNDO', 22, 'mono', fill=tcol, anchor='lm')
        else:
            L.text((x0 + 14, cy + 1), 'UNDO', 22, 'mono', fill=tcol, anchor='lm')
    else:
        undo_arc(L, x0 + 28, cy, 11, tcol)
    xk = x1 - 40
    if locked:
        pts = [(xk - 2, cy + 1), (xk + 8, cy + 9), (xk + 26, cy - 9)]
        L.line(pts, INK, 6)
        L.line(pts, GREY_LOCK, 3)
    else:
        keycap(L, xk, cy)


def hint_line(L, opt, cx, y, words=True):
    """> turn_resolve.exe, mono 18 TEXT_MID, block cursor.  nowords: prompt chevron + cursor only."""
    s = '> turn_resolve.exe' if words else '>'
    tw = L.tw(s, 18, 'mono') if words else 10
    if not words:
        x0 = cx - (tw + 14) / 2
        L.line([(x0, y - 6), (x0 + 7, y), (x0, y + 6)], TXT_MID, 2.6)
        L.rect([x0 + tw + 4, y - 7, x0 + tw + 12, y + 7], fill=TXT_MID + (255,), r=1)
        return
    x0 = cx - (tw + 14) / 2
    if opt == 'A2' and words:
        L.text((x0, y), '>', 18, 'mono', fill=CYAN, anchor='lm')
        L.text((x0 + L.tw('>', 18, 'mono'), y), s[1:], 18, 'mono', fill=TXT_MID, anchor='lm')
    else:
        L.text((x0, y), s, 18, 'mono', fill=TXT_MID, anchor='lm')
    L.rect([x0 + tw + 4, y - 7, x0 + tw + 12, y + 7], fill=TXT_MID + (255,), r=1)


# ---------------------------------------------------------------------------- the stack
def stack_layer(words=True, sel=None):
    sel = sel or {}
    base = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    L = L2()
    mat = sel.get('mat', 'A')
    glyph = {'A': 'ring', 'B': 'bar'}[sel.get('snw', 'A')]
    state = sel.get('state')
    if sel.get('send', 'A') == 'A2':
        st, shd = send_base('A2', words, mat, glyph), dict(k=0.5, blur=8, off=(4, 8))
    else:
        st, shd = send_state(sel.get('sopt', 'A'), state, words, mat, glyph)
    pad = shd.get('pad', 0)
    iw, ih = st.size
    pw_, ph_ = iw - 2 * pad, ih - 2 * pad
    sy = BOTTOM - 34 - ph_
    sx = RIGHT - pw_
    cx, cy = sx + pw_ / 2, sy + ph_ / 2
    # UNDO tab, tilted with the sticker so it stays tucked under the top edge
    Lt = L2()
    box = (sx + 18, sy - 30, sx + pw_ - 18, sy + 22)
    undo_tab(Lt, box, sel.get('undo', 'A'), sel.get('locked', False), words)
    flat = state in ('hover', 'pressed') and sel.get('sopt', 'A') == 'C'
    tl = Lt.done().rotate(0 if flat else -3, center=(cx, cy), resample=Image.BICUBIC)
    base.alpha_composite(tl)
    hint_line(L, sel.get('hint', 'A'), cx, BOTTOM - 14, words)
    base.alpha_composite(L.done())
    xy = (cx - st.width / 2, cy - st.height / 2)
    PADS = 26                       # room for the blurred shadow so it never clips at the image bounds
    padded = Image.new('RGBA', (st.width + 2 * PADS, st.height + 2 * PADS), (0, 0, 0, 0))
    padded.alpha_composite(st, (PADS, PADS))
    st = padded
    xy = (xy[0] - PADS, xy[1] - PADS)
    if shd['k'] > 0:
        shadow_paste(base, st, xy, shd['k'], shd['blur'], shd['off'])
    else:
        base.alpha_composite(st, (int(xy[0]), int(xy[1])))
    info = dict(send=(xy[0], xy[1], st.width, st.height), plate=(cx, cy, pw_, ph_), undo=box)
    if state == 'focus':
        Lf = L2()
        b = border_for(62)
        focus_brackets(Lf, 'rect', dict(box=(cx - pw_ / 2 + b, cy - ph_ / 2 + b, cx + pw_ / 2 - b, cy + ph_ / 2 - b), tilt=0 if flat else -3), sel.get('fopt', 'A'), arm=22, grow=7)
        base.alpha_composite(Lf.done())
    nm0 = nameplate(sel.get('name', 'A'), words, mat)
    # ASSEMBLY (Y14): the zine never covers the wheels: every pixel of the nameplate (die-cut, tilt and shadow, alpha > 8) at r >= 520 from the board centre (536, 540).
    # 24 px bottom and side margins; scale 0.92 if it still intrudes, then further in 0.02 steps (reported).
    sc = 1.0
    while True:
        nm = nm0 if sc == 1.0 else nm0.resize((int(round(nm0.width * sc)), int(round(nm0.height * sc))), Image.LANCZOS)
        nw, nh = nm.size
        pos = (24, BOTTOM - nh)
        tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        shadow_paste(tmp, nm, pos, 0.5, 8, (4, 8))
        a_ = np.asarray(tmp.split()[3])[:, :700]
        ys_, xs_ = np.nonzero(a_ > 8)
        rmin = float(np.hypot(xs_ - 536, ys_ - 540).min())
        if rmin >= 520.0 or sc < 0.7:
            break
        sc = round(sc - 0.02, 2) if sc <= 0.92 else 0.92
    base.alpha_composite(tmp)
    info['name'] = pos + (nw, nh)
    info['name_scale'] = sc
    info['name_rmin'] = rmin
    return base, info
