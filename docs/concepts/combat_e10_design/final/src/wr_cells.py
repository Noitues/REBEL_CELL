"""Cell-level painters: ring_separators, empty_cell, unit_cell_screen, unit_screen_bezel, unit_screen_code_text, screen_motif_skull.
When every one of these options is E the approved master render (programme screens + dark glass) is used untouched.
Otherwise the board is rendered WITHOUT the cells and these functions paint them on the 2x overlay with constant-width gutters."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import wr_state as ST
from wr_state import opt
from wr_geo import *


def painter_mode():
    sep = opt('ring_separators') != 'E'
    return dict(units=sep or any(opt(k) != 'E' for k in ('unit_cell_screen', 'unit_screen_bezel', 'unit_screen_code_text', 'screen_motif_skull')),
                empties=sep or opt('empty_cell') != 'E')


def live_units(f):
    return [u for u in f['units'] if not (u['consumed'] or u['trigdead'])]


def covered(f):
    cov = set()
    for u in live_units(f):
        for q in range(u['w']):
            cov.add((u['dep'], (u['s'] + q) % 6))
    a = f['adj']
    if a and a['hp'] > 0:
        cov.add((a['ring'], a['s']))
    return cov


# ----------------------------------------------------------------------------- ring_separators (gutter bed + spokes)
def gutters(L, f):
    o = opt('ring_separators')
    if o == 'E':
        return
    if o in ('R', 'V'):
        import wr2_cells as W2C
        return W2C.gutters(L, f)
    for dep in range(3):
        ri, ro = CB.ring_geom(dep)
        L.poly(L.band(C, ri, ro, 0, 359.9), fill=GUT_FILL + (255,))
    if o == 'C':      # rail: a lighter 2 px centre line down every gutter, ring circles and spokes alike, continuous to the slice gutters
        RAIL = (46, 54, 80)
        for dep in range(3):
            ri, ro = CB.ring_geom(dep)
            for r in (ri,) + ((ro,) if dep == 2 else ()):
                L.line(L.arc_pts(C, r, 0, 360, 180), RAIL, 2)
            for s in range(6):
                a = 60 * s - 30
                L.line([ppx(C, ri + 2, a), ppx(C, ro - 2, a)], RAIL, 2)


def separators_post(L, f):
    """B: a hairline spoke inside wide cells at every interior sector boundary, with notches at both edges, so the sector count still reads (the cell stays one body)"""
    if opt('ring_separators') in ('R', 'V'):
        import wr2_cells as W2C
        return W2C.interior_hairlines(L, f)
    if opt('ring_separators') != 'B':
        return
    for u in live_units(f):
        for q in range(1, u['w']):
            a = 60 * (u['s'] + q) - 30
            ra, rb = radial_ext(u['dep'])
            wash = kind_wash(u['kind'], u['dep'])
            x0, y0 = ppx(C, ra, a)
            x1, y1 = ppx(C, rb, a)
            L.line([(x0, y0), (x1, y1)], mix(wash, (6, 4, 18), 0.55), 1.6)
            for (r0, r1) in ((ra, ra + 12), (rb - 12, rb)):
                x0, y0 = ppx(C, r0, a)
                x1, y1 = ppx(C, r1, a)
                L.line([(x0, y0), (x1, y1)], GUT_FILL, 6.5)


# ----------------------------------------------------------------------------- empty_cell
def _walk(path, idx, dist, direction):
    out = [path[idx]]
    d = 0.0
    i = idx
    n = len(path)
    while d < dist:
        j = (i + direction) % n
        d += math.hypot(path[j][0] - path[i][0], path[j][1] - path[i][1])
        out.append(path[j])
        i = j
    return out


def corner_ticks(L, poly, col, w, length, ink=True):
    path = resample(poly + [poly[0]], 1.0)[:-1]
    n = len(poly) // 2
    for c in (poly[0], poly[n - 1], poly[n], poly[-1]):
        k = min(range(len(path)), key=lambda i: (path[i][0] - c[0]) ** 2 + (path[i][1] - c[1]) ** 2)
        for dr in (1, -1):
            seg = _walk(path, k, length, dr)
            if ink:
                L.line(seg, INK_, w + 3)
            L.line(seg, col, w)


def empty_cell(L, dep, s):
    o = opt('empty_cell')
    if o in ('R', 'V'):
        import wr2_cells as W2C
        return W2C.empty_cell(L, dep, s)
    lane = LANE[dep]['col']
    b0, b1 = 60 * s - 30, 60 * s + 30
    if o == 'E':      # the E10 look re-drawn on the overlay (dark glass + dim orange master outline + 30 percent lane border) when only the gutters change
        fill = (9, 14, 26)
        poly = cell_poly(dep, b0, b1, kind='empty')
        L.poly(poly, fill=fill + (255,))
        L.line(poly + [poly[0]], mix(fill, ORANGE, 0.40), 1.4)
        L.line(poly + [poly[0]], mix(fill, lane, 0.28), LANE[dep]['w'] * 0.7, dash=LANE[dep]['dash'])
    elif o == 'A':
        # A "void tint": one lifted dark glass, ONE hairline edge in the lane colour at 30 percent, no orange outline, a faint top-lit sheen
        fill = (17, 24, 40)
        poly = cell_poly(dep, b0, b1, kind='empty')
        L.poly(poly, fill=fill + (255,))
        L.line(poly + [poly[0]], mix(fill, lane, 0.30), 1.6)
        ra, rb = radial_ext(dep, 4, 4)
        L.line(L.arc_pts(C, rb, b0 + 5, b1 - 5), mix(fill, (150, 180, 230), 0.16), 2)
    elif o == 'B':
        # B "registration ticks": flat dark glass with four lane-colour corner ticks instead of an edge; reads as an empty slot, no dashed noise
        fill = (12, 17, 30)
        poly = cell_poly(dep, b0, b1, kind='empty')
        L.poly(poly, fill=fill + (255,))
        corner_ticks(L, poly, mix(fill, lane, 0.95), 2.6, 17)
    else:
        # C "recessed pocket": a lighter tray and a smaller darker pocket sunk into it, so the black area is smaller than a unit's and the bed shows
        tray = (24, 29, 45)
        poly = cell_poly(dep, b0, b1, kind='empty')
        L.poly(poly, fill=tray + (255,))
        pk = cell_poly(dep, b0, b1, 5, 5, kind='empty', tin=5)
        L.poly(pk, fill=(8, 11, 22, 255))
        L.line(pk + [pk[0]], mix((8, 11, 22), (70, 86, 120), 0.55), 1.4)


# ----------------------------------------------------------------------------- unit screens
def _gradient_fill(L, u, colfn, steps=2.0):
    b0, b1 = unit_bounds(u)
    ra, rb = radial_ext(u['dep'])
    n = int((rb - ra) / steps) + 1
    for i in range(n):
        r0 = ra + (rb - ra) * i / n
        r1 = min(rb, ra + (rb - ra) * (i + 1) / n + 0.8)
        L.poly(band_poly(u['dep'], b0, b1, r0, r1), fill=colfn((i + 0.5) / n) + (255,))


def screen_A(L, u):
    """A flat wash: one muted mauve per kind (rose / violet / indigo / plum), a clear value ramp by ring (1.00 / 0.84 / 0.68), faint arc scanlines"""
    wash = kind_wash(u['kind'], u['dep'])
    poly = unit_poly(u)
    L.poly(poly, fill=wash + (255,))
    b0, b1 = unit_bounds(u)
    ra, rb = radial_ext(u['dep'])
    ln = mix(wash, (0, 0, 8), 0.10)
    r = ra + 5
    while r < rb - 3:
        L.line(L.arc_pts(C, r, b0 + dA(r, 8) + 1, b1 - dA(r, 8) - 1), ln, 1.0)
        r += 6


def screen_C(L, u):
    """C CRT bowl: dark at the inner edge (where the red chevrons sit) rising to a lit outer edge (where the HP row sits)"""
    wash = kind_wash(u['kind'], u['dep'], ramp=(-0.08, 0.12, 0.32))
    dark = mix(wash, (6, 4, 18), 0.55)
    _gradient_fill(L, u, lambda t: mix(dark, wash, min(1.0, t * 1.15) ** 0.9))


def finish_B(L, f):
    """B calm programme art: the real programme screens, graded, low-passed (kills moire, hex text and the skull) and added at 38 percent as luminance only over the flat wash"""
    box = (130, 130, 950, 950)
    bw, bh = box[2] - box[0], box[3] - box[1]
    k = 2
    m = Image.new('L', (bw * k, bh * k), 0)
    md = ImageDraw.Draw(m)
    for u in live_units(f):
        md.polygon([((x - box[0]) * k, (y - box[1]) * k) for x, y in unit_poly(u)], fill=255)
    prog = ST.PROG.crop(box).resize((bw * k, bh * k), Image.BICUBIC).convert('RGB')
    a = np.asarray(prog, np.float32)
    me = np.asarray(m.filter(ImageFilter.MinFilter(9)), np.float32) / 255.0
    sig = 5.0

    def blur(arr2d, s):
        return np.asarray(Image.fromarray(np.clip(arr2d, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(s)), np.float32)
    lum = a.mean(-1)
    num = blur(lum * me, sig)
    den = blur(me * 255, sig) / 255.0 + 1e-3
    fill = num / den
    det = (blur(fill, 4) - blur(fill, 30)) * 0.75
    base = np.asarray(L.im.crop((box[0] * 2, box[1] * 2, box[2] * 2, box[3] * 2)), np.float32).copy()
    mk = (np.asarray(m, np.float32) / 255.0)
    for i in range(3):
        base[..., i] = np.clip(base[..., i] + det * mk, 0, 255)
    L.im.paste(Image.fromarray(base.astype(np.uint8), 'RGBA'), (box[0] * 2, box[1] * 2))


def unit_screen(L, u, f):
    o = opt('unit_cell_screen')
    if u['w'] == 6:
        return
    if o in ('R', 'V'):
        import wr2_cells as W2C
        return W2C.screen(L, u)
    if o == 'C':
        screen_C(L, u)
    else:
        screen_A(L, u)       # A, B (detail added after) and E-with-another-option all start from the flat wash


def code_text(L, u):
    o = opt('unit_screen_code_text')
    if o in ('E', 'A'):
        return
    rnd = random.Random(u['id'] * 91 + 7)
    wash = kind_wash(u['kind'], u['dep'])
    b0, b1 = unit_bounds(u)
    ra, rb = radial_ext(u['dep'], 17, 17)
    ink = mix(wash, (235, 200, 235), 0.075)      # under 10 percent contrast
    r = ra + 2
    while r < rb:
        a = b0 + dA(r, 8) + 6
        end = b1 - dA(r, 8) - 6
        while a < end - 4:
            wordlen = rnd.choice((18, 30, 44, 60))        # px
            da = math.degrees(wordlen / r)
            if o == 'B':      # sub-legible glyph blocks in hex-like pairs
                x = 0
                while x < wordlen and a + math.degrees(x / r) < end:
                    aa = a + math.degrees(x / r)
                    L.poly(arc_band(r - 2.2, r + 2.2, aa, aa + math.degrees(2.6 / r)), fill=ink + (255,))
                    L.poly(arc_band(r - 2.2, r + 2.2, aa + math.degrees(4.4 / r), aa + math.degrees(7.0 / r)), fill=ink + (255,))
                    x += 12
            else:             # C greeked text lines: one thin bar per word
                L.poly(arc_band(r - 1.2, r + 1.2, a, min(a + da, end)), fill=ink + (255,))
            a += da + math.degrees(rnd.choice((10, 16, 24)) / r)
        r += 8.5


def motif(L, u):
    o = opt('screen_motif_skull')
    if o in ('E', 'A'):
        return
    rnd = random.Random(u['id'] * 53 + 3)
    wash = kind_wash(u['kind'], u['dep'])
    b0, b1 = unit_bounds(u)
    ra, rb = radial_ext(u['dep'], 9, 9)
    ink = mix(wash, (230, 190, 230), 0.085)
    if o == 'B':        # circuit traces: arc runs joined by radial steps, node dots
        for run in range(5):
            r = ra + 5 + rnd.random() * (rb - ra - 10)
            a = b0 + 14 + rnd.random() * 20
            for step in range(7):
                a1 = a + rnd.choice((6, 10, 16))
                if a1 > b1 - 14:
                    break
                L.line(L.arc_pts(C, r, a, a1), ink, 1.6)
                nr = min(max(r + rnd.choice((-10, 10)), ra + 4), rb - 4)
                x0, y0 = ppx(C, r, a1)
                x1, y1 = ppx(C, nr, a1)
                L.line([(x0, y0), (x1, y1)], ink, 1.6)
                r, a = nr, a1
            x1, y1 = ppx(C, r, a)
            L.ellipse([x1 - 2.8, y1 - 2.8, x1 + 2.8, y1 + 2.8], outline=ink, w=1.4)
    else:               # C scan rings: partial concentric arcs of unequal length
        for r in range(int(ra + 4), int(rb - 3), 11):
            a = b0 + 10 + rnd.random() * 30
            L.line(L.arc_pts(C, r, a, min(b1 - 10, a + 20 + rnd.random() * 60)), ink, 1.4)


def bezel_mark(L, u):
    o = opt('unit_screen_bezel')
    if o in ('E', 'A') or u['w'] == 6:
        return
    b0, b1 = unit_bounds(u)
    ra, rb = radial_ext(u['dep'])
    wash = kind_wash(u['kind'], u['dep'])
    G = sep_G()
    if o == 'B':        # B deliberate end caps: a dark screen-edge bar across each cell end, one treatment for every unit
        d_in, d_out = ((dA(ra, G), dA(rb, G)) if G else (3.0, 3.0))
        cap = 6.0
        pts = [ppx(C, ra, b0 + d_in), ppx(C, rb, b0 + d_out), ppx(C, rb, b0 + d_out + math.degrees(cap / rb)), ppx(C, ra, b0 + d_in + math.degrees(cap / ra))]
        L.poly(pts, fill=mix(wash, (8, 6, 18), 0.6) + (255,))
        pts = [ppx(C, ra, b1 - d_in), ppx(C, rb, b1 - d_out), ppx(C, rb, b1 - d_out - math.degrees(cap / rb)), ppx(C, ra, b1 - d_in - math.degrees(cap / ra))]
        L.poly(pts, fill=mix(wash, (8, 6, 18), 0.6) + (255,))
    else:               # C corner studs: four small screw heads in the screen corners (neutral, never pink)
        da = dA(ra, G) if G else 3.0
        for rr in (ra + 7, rb - 7):
            for (aa, sg) in ((b0 + (dA(rr, G) if G else 3.0) + math.degrees(8 / rr), 1), (b1 - (dA(rr, G) if G else 3.0) - math.degrees(8 / rr), -1)):
                x, y = ppx(C, rr, aa)
                L.ellipse([x - 3.6, y - 3.6, x + 3.6, y + 3.6], fill=mix(wash, (6, 4, 14), 0.5), outline=INK_, w=1.2)
                L.ellipse([x - 1.8, y - 2.2, x + 0.2, y - 0.4], fill=mix(wash, (255, 255, 255), 0.35))


def paint_cells(L, f, beat, painter):
    if not (painter['units'] or painter['empties']):
        return
    gutters(L, f)
    cov = covered(f)
    if painter['empties']:
        for dep in range(3):
            for s in range(6):
                if (dep, s) not in cov:
                    empty_cell(L, dep, s)
    if painter['units']:
        for u in live_units(f):
            unit_screen(L, u, f)
        if opt('unit_cell_screen') == 'B':
            finish_B(L, f)
        for u in live_units(f):
            code_text(L, u)
            motif(L, u)
            bezel_mark(L, u)
    separators_post(L, f)
