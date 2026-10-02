"""Round 14: the locked D4 "Lens & rail" frame, generalised for

- corp themes (bezel material, rim language, crest, accent) inherited by every enemy of the corp,
- tiers: regular -> elite (gold collar, rank chevrons, small crests) -> boss (threat ring, crest lugs,
  banner-mounted crowned blade, phase pips),
- boss phase upgrades: extra readers (secondary pins + rails), slice re-skin (skins.BOSS), armour plates
  bolted on (P3), screen overdrive (P3, motifs.overdrive), slices merging (DISPATCH P3), docked drones,
- the card-play preview indicator (player wheel): three styles.

render(spec, ss, lod, preview, hp_number) -> (RGBA at ss, centre px, meta)
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import frames as F
from frames import P, Q, layer, add_glow, over_pil, over_arr, shadow_of, new_canvas, grids, INK, CREAM
from slicelib import R_OUT, R_IN, PROGRAMS, CORPS, render_slice, f_num, f_ui, f_mono, glyph_rgba, c01
import roster_wheel as RW
import combat_wheel as CWL
import motifs as MO
import tiles as TL

CORP_STYLE = {
    "meridian": dict(base=(0.40, 0.22, 0.08), name="MERIDIAN FREIGHT"),
    "solace": dict(base=(0.74, 0.77, 0.75), name="SOLACE BIOSYSTEMS"),
    "halcyon": dict(base=(0.30, 0.15, 0.46), name="HALCYON CIVIC"),
    "orbital": dict(base=(0.62, 0.72, 0.76), name="ORBITAL COMMONS"),
    "rebel_cell": dict(base=(0.16, 0.035, 0.045), name="REBEL_CELL"),
}
GOLD = (255, 205, 90)


def acc_of(spec):
    if spec["theme"] == "player":
        return RW.CLASS_STYLE[spec["cls"]]["acc"]
    return MO.ACCENT[spec["theme"]]["a"]


def mix(a, b, k):
    return tuple(int(a[i] * (1 - k) + b[i] * k) for i in range(3))


# ================================================================== slices
_CACHE = {}


def slice_layers(spec, ss, lod, rot):
    merge = spec.get("merge")
    boss = spec.get("boss")
    out = {}
    for i in range(6):
        if merge and i == merge[1]:
            continue
        span = 120 if (merge and i == merge[0]) else 60
        key = (spec.get("key"), spec.get("variant"), spec.get("corp_tier"), i, ss, lod, round(rot, 3))
        if key in _CACHE:
            out[i] = _CACHE[key]
            continue
        sl = spec["slots"][i]
        a0 = -30.0 + 60 * i + rot
        angs = np.radians(np.linspace(a0, a0 + span, 60))
        xs = [r * np.sin(a) for r in (R_IN, R_OUT) for a in angs]
        ys = [-r * np.cos(a) for r in (R_IN, R_OUT) for a in angs]
        m = 24
        x0, x1 = int((min(xs) - m) * ss), int((max(xs) + m) * ss)
        y0, y1 = int((min(ys) - m) * ss), int((max(ys) + m) * ss)
        cv = np.zeros((y1 - y0, x1 - x0, 4), np.float32)
        opts = dict(RW.LOD) if lod else {}
        opts.update(upright=True, defer_icons=True, tier=spec.get("tier", "regular"))
        if spec.get("corp_tier") and spec["theme"] in TL.TIER_COLS:
            opts.update(corp_tier=spec["corp_tier"], tier_cols=TL.TIER_COLS[spec["theme"]])
        if boss:
            opts.update(boss=True, phase=boss.get("phase", 1))
        val = sl["value"]
        if sl["program"] == "NULL" or (sl.get("special") and sl["special"] != "tariff"):
            val = None
        badge = sl.get("badge")
        if span == 120:
            badge = "MERGED x2"
        blk, bx, by = render_slice(cv, -x0, -y0, sl["program"], a0, span, val, (0.3 + i * 0.137) % 1.0, spec["theme"], ss,
                                   opts, seed=i + spec.get("seed", 1) * 7, glyph=RW.SPECIAL_GLYPH.get(sl.get("special")),
                                   badge=badge, special=sl.get("special"))
        L = dict(arr=cv, x0=x0, y0=y0, blk=F.premult(blk), bx=bx + x0, by=by + y0, a0=a0, span=span, mid=a0 + span / 2,
                 prog=sl["program"], value=val, special=sl.get("special"), i=i)
        _CACHE[key] = L
        out[i] = L
    return out


def index_at(spec, ang, rot=0.0):
    i = int(((ang - rot + 30) % 360) // 60)
    merge = spec.get("merge")
    if merge and i == merge[1]:
        i = merge[0]
    return i


def glyph_name(L):
    return RW.SPECIAL_GLYPH.get(L["special"]) or L["prog"]


# ================================================================== telemetry with any number of rails
def telemetry_multi(img, d, gd, spec, R0, R1, ss, acc, emblem, lod, rails, badges=True, rail_alpha=1.0):
    ring_r = (R0 + R1) / 2 - 5
    for rr in (R0 + 4, R1 - 4):
        bb = [RW.CX * ss - rr * ss, RW.CY * ss - rr * ss, RW.CX * ss + rr * ss, RW.CY * ss + rr * ss]
        d.ellipse(bb, outline=tuple(int(v * 0.5) for v in acc) + (255,), width=max(1, ss))
    iv = sorted(((c - h) % 360, h * 2, prog, value, c) for (prog, value, c, h) in rails)
    # complement arcs
    gaps = []
    if not iv:
        gaps = [(0, 360)]
    for k in range(len(iv)):
        s0 = iv[k][0] + iv[k][1] + 2
        e0 = iv[(k + 1) % len(iv)][0] - 2
        if k == len(iv) - 1:
            e0 += 360
        if e0 > s0:
            gaps.append((s0, e0))
    key = spec.get("key", "")
    text = CWL.READOUT.get(key, (spec.get("hub", {}).get("name", key) + " // " + CORP_STYLE.get(spec["theme"], {}).get("name", "") + " // ").upper())
    for (a0, a1) in gaps:
        if not lod:
            CWL.text_ring(img, text, ring_r, a0, a1, ss, f_mono(int(13 * ss)), tuple(int(v * 0.95) for v in acc), head=a0 + 30)
        else:
            a = a0
            while a < a1 - 2:
                d.line([P(ring_r + 2, a, ss), P(ring_r + 2, a + 1.6, ss)], fill=acc + (200,), width=int(4 * ss))
                a += 3
    for (s, span, prog, value, c) in iv:
        pc = PROGRAMS[prog]["col"]
        h = span / 2
        poly = RW.arc_poly(R0 + 5, R1 - 5, c - h, c + h, ss, 40)
        gd.polygon(poly, fill=pc + (int(150 * rail_alpha),))
        d.polygon(poly, fill=tuple(int(v * 0.42) for v in pc) + (255,))
        for a in (c - h, c + h):
            d.line([P(R0 + 2, a, ss), P(R1 - 2, a, ss)], fill=pc + (255,), width=int(3 * ss))
        kind = F.KIND[PROGRAMS[prog]["kind"]]
        txt = ("%s %s // %s // " % (prog, value, kind)) if value is not None else "%s // %s // " % (prog, kind)
        if not lod:
            CWL.text_ring(img, txt * 4, ring_r, c - h + 1, c + h - 1, ss, f_mono(int(14 * ss)), (255, 255, 255))
        else:
            for a in range(int(c - h), int(c + h), 3):
                d.line([P(ring_r + 2, a, ss), P(ring_r + 2, a + 2, ss)], fill=(255, 255, 255, 255), width=int(6 * ss))
    if badges:
        ptr = [p * 12 for p in spec.get("pointers", [0])]
        for a in (0, 90, 180, 270):
            if any(abs(((a - p + 180) % 360) - 180) < 40 for p in ptr):
                continue
            x, y = P((R0 + R1) / 2, a, ss)
            CWL.emblem_badge(img, d, gd, x, y, 19 * ss, acc, emblem)


# ================================================================== corp rim language
def corp_rim(img, d, gd, ss, corp, R0, R1, acc, skip=()):
    rm = (R0 + R1) / 2
    A = MO.ACCENT[corp]
    if corp == "meridian":  # hazard stripes + notched teeth (container corrugation)
        for i in range(90):
            a = i * 4
            poly = [P(R0, a, ss), P(R1, a + 1.6, ss), P(R1, a + 3.2, ss), P(R0, a + 1.6, ss)]
            d.polygon(poly, fill=(22, 16, 10, 255) if i % 2 else acc + (255,))
        for i in range(30):
            a = i * 12 + 6
            d.polygon([P(R1, a - 2.2, ss), P(R1 + 7, a - 1.0, ss), P(R1 + 7, a + 1.0, ss), P(R1, a + 2.2, ss)],
                      fill=(70, 40, 16, 255), outline=INK + (255,))
    elif corp == "solace":  # porcelain with mint capsule studs + glass glow ring
        bb = [RW.CX * ss - (R1 + 3) * ss, RW.CY * ss - (R1 + 3) * ss, RW.CX * ss + (R1 + 3) * ss, RW.CY * ss + (R1 + 3) * ss]
        gd.ellipse(bb, outline=acc + (220,), width=int(6 * ss))
        d.ellipse(bb, outline=mix(acc, (255, 255, 255), 0.5) + (255,), width=int(2 * ss))
        for i in range(12):
            a = i * 30 + 15
            if any(abs(((a - s + 180) % 360) - 180) < 14 for s in skip):
                continue
            pts = RW.arc_poly(rm - 4, rm + 4, a - 5, a + 5, ss, 8)
            gd.polygon(pts, fill=acc + (200,))
            d.polygon(pts, fill=acc + (255,), outline=(20, 70, 50, 255), width=max(1, ss))
            x, y = P(rm + 1.5, a - 2.5, ss)
            d.ellipse([x - 1.5 * ss, y - 1.5 * ss, x + 1.5 * ss, y + 1.5 * ss], fill=(255, 255, 255, 230))
    elif corp == "halcyon":  # colonnade: pale pillars + gold halo arc on top
        for i in range(48):
            a = i * 7.5
            pts = RW.arc_poly(R0 + 1, R1 - 1, a - 1.3, a + 1.3, ss, 3)
            d.polygon(pts, fill=A["paper"] + (230,))
        d.ellipse([RW.CX * ss - R1 * ss, RW.CY * ss - R1 * ss, RW.CX * ss + R1 * ss, RW.CY * ss + R1 * ss], outline=A["paper"] + (255,), width=max(1, int(1.5 * ss)))
        bb = [RW.CX * ss - (R1 + 9) * ss, RW.CY * ss - (R1 + 9) * ss, RW.CX * ss + (R1 + 9) * ss, RW.CY * ss + (R1 + 9) * ss]
        gd.arc(bb, 200 - 90, 340 - 90, fill=A["gold"] + (220,), width=int(6 * ss))
        d.arc(bb, 200 - 90, 340 - 90, fill=A["gold"] + (255,), width=int(2.5 * ss))
    elif corp == "orbital":  # azimuth ring 000..330
        f = f_mono(int(9 * ss))
        for i in range(72):
            a = i * 5
            L = 7 if i % 6 == 0 else 3.5
            d.line([P(R1 - 1, a, ss), P(R1 - 1 - L, a, ss)], fill=A["paper"] + (255,), width=max(1, int(1.2 * ss)))
        for i in range(12):
            a = i * 30
            if any(abs(((a - s + 180) % 360) - 180) < 10 for s in skip):
                continue
            s = "%03d" % a
            im = Image.new("RGBA", (int(f.getlength(s) + 4), int(12 * ss)), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((2, 0), s, font=f, fill=A["paper"] + (255,))
            im = im.rotate(-a, expand=True, resample=Image.BICUBIC)
            x, y = P(R0 + 4, a, ss)
            img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
        bb = [RW.CX * ss - (R1 + 2) * ss, RW.CY * ss - (R1 + 2) * ss, RW.CX * ss + (R1 + 2) * ss, RW.CY * ss + (R1 + 2) * ss]
        gd.ellipse(bb, outline=acc + (200,), width=int(5 * ss))
        d.ellipse(bb, outline=acc + (255,), width=max(1, int(1.5 * ss)))
    else:  # rebel_cell: broken, offset black-red segments with hex rivets
        rng = np.random.default_rng(5)
        a = 0.0
        while a < 360:
            L = 18 + rng.random() * 26
            off = (rng.random() - 0.5) * 5
            pts = RW.arc_poly(R0 + 1 + off, R1 - 1 + off, a + 1.5, a + L - 1.5, ss, 10)
            d.polygon(pts, fill=(34, 6, 9, 255), outline=acc + (255,), width=max(1, ss))
            x, y = P(rm + off, a + L / 2, ss)
            r = 3.6 * ss
            hx = [(x + r * math.cos(math.radians(60 * j)), y + r * math.sin(math.radians(60 * j))) for j in range(6)]
            d.polygon(hx, fill=acc + (255,))
            a += L


def crest(img, d, gd, ss, x, y, r, corp, acc, emblem):
    """Corp-shaped crest plate with the emblem."""
    A = MO.ACCENT.get(corp, MO.ACCENT["meridian"])
    if corp == "meridian":
        pts = [(x + r * math.cos(math.radians(60 * j)), y + r * math.sin(math.radians(60 * j))) for j in range(6)]
        gd.polygon(pts, fill=acc + (160,))
        d.polygon(pts, fill=(34, 24, 16, 255), outline=acc + (255,), width=int(3 * ss))
    elif corp == "solace":
        gd.ellipse([x - r, y - r, x + r, y + r], fill=acc + (160,))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(222, 232, 228, 255), outline=acc + (255,), width=int(3 * ss))
        d.ellipse([x - r * 0.78, y - r * 0.78, x + r * 0.78, y + r * 0.78], fill=(14, 40, 34, 255))
    elif corp == "halcyon":
        pts = [(x - r * 0.85, y - r * 0.55), (x, y - r * 1.05), (x + r * 0.85, y - r * 0.55), (x + r * 0.85, y + r * 0.35),
               (x, y + r), (x - r * 0.85, y + r * 0.35)]
        gd.polygon(pts, fill=A["gold"] + (150,))
        d.polygon(pts, fill=(20, 20, 64, 255), outline=A["gold"] + (255,), width=int(3 * ss))
    elif corp == "orbital":
        gd.ellipse([x - r, y - r, x + r, y + r], fill=acc + (160,))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(12, 20, 50, 255), outline=A["paper"] + (255,), width=int(2.5 * ss))
        d.ellipse([x - r * 1.35, y - r * 0.38, x + r * 1.35, y + r * 0.38], outline=acc + (255,), width=int(2 * ss))
    else:
        pts = [(x + r * math.cos(math.radians(60 * j + 30)), y + r * math.sin(math.radians(60 * j + 30))) for j in range(6)]
        gd.polygon(pts, fill=acc + (160,))
        d.polygon(pts, fill=(24, 4, 8, 255))
        for j in range(6):
            if j == 2:
                continue  # the break in the hex
            d.line([pts[j], pts[(j + 1) % 6]], fill=acc + (255,), width=int(3 * ss))
    g = RW.tinted_glyph(emblem, int(r * 1.15), acc if corp != "halcyon" else A["gold"])
    img.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))


def elite_collar(img, d, gd, ss, R0, R1, acc, corp, emblem, skip=()):
    bb = [RW.CX * ss - R1 * ss, RW.CY * ss - R1 * ss, RW.CX * ss + R1 * ss, RW.CY * ss + R1 * ss]
    d.ellipse(bb, outline=(24, 20, 16, 255), width=int((R1 - R0) * ss))
    for r in (R0 + 1.5, R1 - 1.5):
        bb = [RW.CX * ss - r * ss, RW.CY * ss - r * ss, RW.CX * ss + r * ss, RW.CY * ss + r * ss]
        gd.ellipse(bb, outline=GOLD + (160,), width=int(4 * ss))
        d.ellipse(bb, outline=GOLD + (255,), width=max(1, int(1.4 * ss)))
    for i in range(48):
        a = i * 7.5 + 3.75
        if any(abs(((a - s + 180) % 360) - 180) < 12 for s in skip):
            continue
        d.polygon(RW.arc_poly(R0 + 3.5, R1 - 3.5, a - 1.6, a + 1.6, ss, 3), fill=acc + (255,))
    for a in (90, 270):
        x, y = P((R0 + R1) / 2, a, ss)
        crest(img, d, gd, ss, x, y, 26 * ss, corp, acc, emblem)


# ================================================================== preview indicator (card hover)
def arc_line(d, r, a0, a1, ss, col, w, n=None, alpha0=None):
    n = n or max(4, int(abs(a1 - a0) / 1.5))
    pts = [P(r, a0 + (a1 - a0) * k / n, ss) for k in range(n + 1)]
    if alpha0 is None:
        d.line(pts, fill=col, width=w, joint="curve")
    else:  # comet: alpha rises toward a1
        for k in range(n):
            al = int(alpha0 + (col[3] - alpha0) * (k + 1) / n)
            d.line([pts[k], pts[k + 1]], fill=col[:3] + (al,), width=w)


def dashed_poly(d, pts, col, w, dash=8, gap=6):
    """Dashed closed polyline: densify, then draw the pieces whose arc length falls in a dash."""
    seq = pts + [pts[0]]
    period = dash + gap
    cum = 0.0
    for (xa, ya), (xb, yb) in zip(seq[:-1], seq[1:]):
        L = math.hypot(xb - xa, yb - ya)
        n = max(1, int(L / 1.5))
        for k in range(n):
            t0, t1 = k / n, (k + 1) / n
            if (cum + L * (t0 + t1) / 2) % period < dash:
                d.line([(xa + (xb - xa) * t0, ya + (yb - ya) * t0), (xa + (xb - xa) * t1, ya + (yb - ya) * t1)], fill=col, width=w)
        cum += L

def aim_of(off_ticks):
    o = abs(off_ticks)
    return (3, "PERFECT") if o < 0.5 else ((2, "GOOD") if o < 1.5 else (1, "PARTIAL"))


def preview_layer(canvas, spec, Ls, ss, pv, R_rail, top_r):
    """pv = dict(style='ghost'|'rail'|'ticker', moves=[ticks...], card='HEAVY SPIN 9').
    A spin of N ticks moves the slices N ticks clockwise, so the slice now at -12N lands under the pointer."""
    im, d = layer(ss)
    gl, gd = layer(ss)
    Rch0, Rch1 = R_rail
    rr = (Rch0 + Rch1) / 2
    style = pv["style"]
    for mv in pv["moves"]:
        a_land = -12.0 * mv
        li = index_at(spec, a_land)
        L = Ls[li]
        pc = PROGRAMS[L["prog"]]["col"]
        off = (((a_land - L["mid"]) + 180) % 360 - 180) / 12.0
        pips, aim = aim_of(off)
        wp = F.wedge_pts(L["a0"] + 1.2, L["a0"] + L["span"] - 1.2, R_IN + 4, R_OUT - 4, ss, 40)
        sgn = 1 if a_land >= 0 else -1
        if style == "ghost":
            # comet sweep in the telemetry channel, one dot per tick, then a hollow ghost blade
            arc_line(gd, rr, 0, a_land, ss, (255, 255, 255, 200), int(10 * ss))
            arc_line(d, rr, 0, a_land, ss, (255, 255, 255, 230), int(3.5 * ss), alpha0=40)
            for k in range(1, abs(int(mv)) + 1):
                x, y = P(rr, -12 * k * (1 if mv > 0 else -1), ss)
                r = 4 * ss
                d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 255), outline=INK + (255,))
            dashed_poly(d, wp, pc + (255,), int(4 * ss), dash=10 * ss, gap=7 * ss)
            gd.polygon(wp, outline=pc + (255,), width=int(10 * ss))
            tip, top = R_OUT - 24, top_r
            sh = top - 78
            pts = [Q(tip, 0, a_land, ss), Q(sh, 34, a_land, ss), Q(top, 50, a_land, ss), Q(top, -50, a_land, ss), Q(sh, -34, a_land, ss)]
            gfill = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(gfill).polygon(pts, fill=(255, 255, 255, 70))
            im.alpha_composite(gfill)
            d = ImageDraw.Draw(im)
            gd.polygon(pts, outline=(255, 255, 255, 200), width=int(8 * ss))
            dashed_poly(d, pts, (255, 255, 255, 255), int(4 * ss), dash=12 * ss, gap=7 * ss)
            w0, w1 = top - 66, top - 18
            wpts = [Q(w0, -36, a_land, ss), Q(w0, 36, a_land, ss), Q(w1, 36, a_land, ss), Q(w1, -36, a_land, ss)]
            d.polygon(wpts, fill=(12, 12, 18, 200), outline=pc + (255,), width=int(2 * ss))
            cx, cy = Q((w0 + w1) / 2, 0, a_land, ss)
            txt = str(L["value"]) if L["value"] is not None else "-"
            f = f_num(int(46 * ss))
            tw = f.getlength(txt)
            d.text((cx - tw / 2, cy - 29 * ss), txt, font=f, fill=pc + (255,), stroke_width=int(1.5 * ss), stroke_fill=INK + (255,))
            # aim pips under the ghost window
            for k in range(3):
                x, y = Q(w0 - 14, (k - 1) * 14, a_land, ss)
                r = 5 * ss
                d.ellipse([x - r, y - r, x + r, y + r], fill=((255, 214, 64) if k < pips else (70, 70, 80)) + (255,), outline=INK + (255,))
        elif style == "rail":
            # the landing slice gets its own (hatched) rail; a chevron run links the two rails
            h = 22
            poly = RW.arc_poly(Rch0 + 5, Rch1 - 5, a_land - h, a_land + h, ss, 30)
            gd.polygon(poly, fill=pc + (170,))
            d.polygon(poly, fill=tuple(int(v * 0.30) for v in pc) + (240,))
            for k in range(-int(h), int(h), 3):
                d.line([P(Rch0 + 6, a_land + k, ss), P(Rch1 - 6, a_land + k + 2, ss)], fill=pc + (150,), width=max(1, ss))
            for a in (a_land - h, a_land + h):
                d.line([P(Rch0 + 2, a, ss), P(Rch1 - 2, a, ss)], fill=pc + (255,), width=int(3 * ss))
            span = a_land
            step = 7 * sgn
            a = 52 * sgn if abs(a_land) > 60 else 8 * sgn
            while (a_land - a) * sgn > h + 2:
                cx = a
                p0, p1, p2 = P(rr - 7, cx - 2.5 * sgn, ss), P(rr, cx + 1.5 * sgn, ss), P(rr + 7, cx - 2.5 * sgn, ss)
                d.line([p0, p1, p2], fill=(255, 255, 255, 235), width=int(3 * ss), joint="curve")
                a += step
            fill = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(fill).polygon(wp, fill=pc + (70,))
            im.alpha_composite(fill)
            d = ImageDraw.Draw(im)
            # landing chip outside the rim
            x, y = P(Rch1 + 70, a_land, ss)
            s1 = "%s %s" % (L["prog"], L["value"] if L["value"] is not None else "")
            fch = f_num(int(26 * ss))
            fs = f_ui(int(15 * ss), b"Bold SemiCondensed")
            w = max(fch.getlength(s1), fs.getlength(aim) + 52 * ss) + 22 * ss
            box = [x - w / 2, y - 26 * ss, x + w / 2, y + 30 * ss]
            d.rounded_rectangle(box, radius=8 * ss, fill=(12, 10, 18, 245), outline=pc + (255,), width=int(2.5 * ss))
            d.text((box[0] + 11 * ss, box[1] + 2 * ss), s1, font=fch, fill=(255, 255, 255, 255))
            for k in range(3):
                xx = box[0] + 11 * ss + k * 15 * ss
                d.ellipse([xx, box[1] + 36 * ss, xx + 11 * ss, box[1] + 47 * ss], fill=((255, 214, 64) if k < pips else (70, 70, 80)) + (255,))
            d.text((box[0] + 60 * ss, box[1] + 33 * ss), aim, font=fs, fill=(255, 214, 64, 255))
        else:  # ticker: tick dots round the hub edge + hatched landing slice + ghost notch
            r_t = R_IN - 2
            n = abs(int(mv))
            for k in range(0, n + 1):
                a = -12 * k * (1 if mv > 0 else -1)
                x, y = P(r_t, a, ss)
                r = (5.5 if k in (0, n) else 3.6) * ss
                col = (255, 255, 255) if k < n else pc
                gd.ellipse([x - r * 1.8, y - r * 1.8, x + r * 1.8, y + r * 1.8], fill=col + (150,))
                d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,), outline=INK + (255,), width=max(1, ss))
            arc_line(d, r_t, 0, a_land, ss, (255, 255, 255, 170), int(2 * ss))
            hatch = Image.new("RGBA", im.size, (0, 0, 0, 0))
            hd = ImageDraw.Draw(hatch)
            hd.polygon(wp, fill=pc + (55,))
            mask = Image.new("L", im.size, 0)
            ImageDraw.Draw(mask).polygon(wp, fill=255)
            st = Image.new("RGBA", im.size, (0, 0, 0, 0))
            sd = ImageDraw.Draw(st)
            for k in range(-im.height, im.width, int(16 * ss)):
                sd.line([(k, 0), (k + im.height, im.height)], fill=pc + (120,), width=int(4 * ss))
            hatch.alpha_composite(Image.composite(st, Image.new("RGBA", im.size, (0, 0, 0, 0)), mask))
            im.alpha_composite(hatch)
            d = ImageDraw.Draw(im)
            d.polygon(wp, outline=pc + (255,), width=int(3 * ss))
            tipp = [P(R_OUT - 6, a_land, ss), P(R_OUT + 14, a_land - 3.2, ss), P(R_OUT + 14, a_land + 3.2, ss)]
            d.polygon(tipp, fill=(255, 255, 255, 255), outline=INK + (255,), width=max(1, ss))
            # tick count label beside the last dot
            x, y = P(r_t - 26, a_land, ss)
            s = "%+d" % (-mv) if pv.get("nudge") else "%d" % abs(mv)
            ff = f_num(int(22 * ss))
            d.text((x - ff.getlength(s) / 2, y - 14 * ss), s, font=ff, fill=(255, 255, 255, 255), stroke_width=int(2 * ss), stroke_fill=INK + (255,))
    add_glow(canvas, gl, ss, 0.8)
    over_pil(canvas, im)


def split_window(canvas, ss, ang, top, Rbase, now, nxt, pc_now, pc_next, ps=1.0):
    """ticker style: the blade window shows 'now > next'."""
    im, d = layer(ss)
    w0, w1, ww = Rbase + 30 * ps, top - 18 * ps, 36 * ps
    wp = [Q(w0, -ww - 26, ang, ss), Q(w0, ww + 26, ang, ss), Q(w1, ww + 26, ang, ss), Q(w1, -ww - 26, ang, ss)]
    d.polygon(wp, fill=(12, 12, 18, 255), outline=pc_next + (255,), width=int(2.4 * ss))
    cx, cy = Q((w0 + w1) / 2, 0, ang, ss)
    f = f_num(int((w1 - w0) * 0.86 * ss))
    a, b = str(now), str(nxt)
    fa = f_num(int((w1 - w0) * 0.6 * ss))
    ta, tb = fa.getlength(a), f.getlength(b)
    arrow = 12 * ss
    tot = ta + tb + arrow + 10 * ss
    x = cx - tot / 2
    d.text((x, cy - (w1 - w0) * 0.36 * ss), a, font=fa, fill=(150, 150, 160, 255))
    xa = x + ta + 4 * ss
    d.polygon([(xa, cy - 6 * ss), (xa + arrow, cy), (xa, cy + 6 * ss)], fill=(255, 255, 255, 255))
    d.text((xa + arrow + 6 * ss, cy - (w1 - w0) * 0.52 * ss), b, font=f, fill=pc_next + (255,), stroke_width=int(1.5 * ss), stroke_fill=INK + (255,))
    over_pil(canvas, im)


# ================================================================== render
def render(spec, ss=1, lod=False, rot=0.0, hp_number=False, preview=None, banner_on=True):
    corp = spec["theme"]
    is_player = corp == "player"
    tier = "player" if is_player else spec.get("tier", "regular")
    boss = spec.get("boss")
    phase = boss.get("phase", 1) if boss else 1
    acc = acc_of(spec)
    st = RW.CLASS_STYLE[spec["cls"]] if is_player else None
    emblem = st["emblem"] if is_player else RW.CORP_EMBLEM[corp]
    canvas = new_canvas(ss)
    Ls = slice_layers(spec, ss, lod, rot)
    ptrs = [p * 12 for p in spec.get("pointers", [0])] or [0]
    act = []
    for a in ptrs:
        i = index_at(spec, a, rot)
        if i not in act:
            act.append(i)
    hub_r = 96 if spec.get("ring") else 126
    R_lip = R_OUT - 4
    Rch0, Rch1 = R_OUT + 8, R_OUT + 44
    R1 = R_OUT + (54 if is_player else 64)
    Rx = R1  # outer edge so far
    if tier == "elite":
        Rx = R1 + 14
    if boss:
        Rx = R1 + 30
    armour_on = bool(boss) and spec.get("armour", False)
    RA = Rx + (24 if armour_on else 0)
    base = (0.16, 0.15, 0.19) if is_player else CORP_STYLE[corp]["base"]
    # back plate + slices
    dx, dy = grids(ss)
    rho = np.hypot(dx, dy)
    bp = np.clip(R_OUT + 4 - rho, 0, 1)
    canvas[..., :3] = canvas[..., :3] * (1 - bp[..., None]) + np.array([0.02, 0.018, 0.03]) * bp[..., None]
    canvas[..., 3] = np.maximum(canvas[..., 3], bp)
    del dx, dy, rho, bp
    for i, L in Ls.items():
        if i not in act:
            F.place_slice(canvas, L, ss, dim=0.68)
    F.disc_shadow(canvas, ss, R_lip + 0.5, R_lip, (5, 9), k=0.5, soft=6)
    F.disc_shadow(canvas, ss, R_OUT, None, (6, 10), k=0.45, soft=7, raised_disc=(127 if spec.get("ring") else hub_r))
    F.machined(canvas, ss, [(R_lip, 0.0), (R_lip + 3, 6.0), (Rch0 - 3, 7.0), (Rch0, 2.0), (Rch1, 2.0), (Rch1 + 3, 7.0),
                            (R1 - 4, 8.0), (R1, 0.0)], base, acc, screen=(Rch0, Rch1), seed=17,
               accent_r=((Rch0 + 0.5, 0.9, 0.8), (Rch1 - 0.5, 0.9, 0.8), (R1 - 0.8, 1.0, 1.0)), brushed=0.04,
               gloss=0.8 if corp != "solace" else 1.1)
    im, d = layer(ss)
    gl, gd = layer(ss)
    half = 50 if len(ptrs) == 1 else 24
    rails = []
    for a in ptrs:
        L = Ls[index_at(spec, a, rot)]
        rails.append((L["prog"], L["value"], a, half))
    telemetry_multi(im, d, gd, spec, Rch0 - 2, Rch1 + 2, ss, acc, emblem, lod, rails)
    if not is_player:
        corp_rim(im, d, gd, ss, corp, Rch1 + 3, R1 - 1, acc, skip=ptrs)
    if tier == "elite":
        elite_collar(im, d, gd, ss, R1 + 1, R1 + 14, acc, corp, emblem, skip=ptrs)
    if boss:
        hot = phase >= 2
        F.threat_ring(d, gd, ss, R1 + 1, R1 + 30, THREAT_HOT if hot else acc, rot=-rot * 1.7 + 7, telegraph=(), lod=lod)
        if hot:  # P2+: threat ring runs hot: a second, inner chevron row
            bb = [RW.CX * ss - (R1 + 3) * ss, RW.CY * ss - (R1 + 3) * ss, RW.CX * ss + (R1 + 3) * ss, RW.CY * ss + (R1 + 3) * ss]
            gd.ellipse(bb, outline=(255, 60, 60, 200), width=int(5 * ss))
        if armour_on:  # P3: armour plates bolt on outside the threat ring
            F.armour(im, d, gd, ss, Rx + 1, RA, acc, emblem, base=ARMOUR_BASE.get(corp, (46, 36, 28)), skip=ptrs)
        for a in (90, 270):
            x, y = P(RA + 8, a, ss)
            crest(im, d, gd, ss, x, y, 40 * ss, corp, acc, emblem)
    F._hub_std(im, d, gd, spec, ss, hub_r, acc, st, lod, hp_in_hub=lod)
    if spec.get("resistance"):
        RW.draw_res_badge(im, d, gd, ss, spec["resistance"], hub_r, lock=spec.get("lock", False))
    F._hp(d, gd, ss, RA, spec, boss, hp_number)
    dang = spec.get("drone_angles", [62, 102])
    for k, dr in enumerate(spec.get("drones", [])[:2]):
        RW.draw_drone(im, d, gd, dang[k], RA + 74, ss, acc, dr["name"], dr["hp"], acc)
    add_glow(canvas, gl, ss)
    over_pil(canvas, im)
    # lifted active slices
    s_l, sh_l = 1.025, 1.0
    for i in act:
        L = Ls[i]
        tmp = new_canvas(ss)
        F.place_slice(tmp, L, ss, scale=s_l, shift=sh_l)
        sa = tmp[..., 3]
        small = Image.fromarray((sa * 255).astype(np.uint8)).resize((F.CW * ss // 4, F.CH * ss // 4), Image.BILINEAR)
        small = small.filter(ImageFilter.GaussianBlur(4 * ss)).resize((F.CW * ss, F.CH * ss), Image.BILINEAR)
        shd = np.zeros_like(tmp)
        shd[..., 3] = np.asarray(small, np.float32) / 255 * 0.8
        over_arr(canvas, shd, 6 * ss, 11 * ss)
        over_arr(canvas, tmp)
        del tmp, shd
        im2, d2 = layer(ss)
        gl2, gd2 = layer(ss)
        pts = F.wedge_pts(L["a0"] + 0.9, L["a0"] + L["span"] - 0.9, R_IN + 2, R_OUT - 1.5, ss, 50, s_l, sh_l)
        gd2.polygon(pts, outline=PROGRAMS[L["prog"]]["col"] + (255,), width=int(16 * ss))
        d2.polygon(pts, outline=INK + (255,), width=int(8 * ss))
        d2.polygon(pts, outline=CREAM + (255,), width=int(4 * ss))
        add_glow(canvas, gl2, ss, 0.8, blur=9)
        over_pil(canvas, im2)
    # blades: primary full blade, secondary readers as numbered pins
    ps = 1.6 if lod else 1.0
    tip = R_OUT - 24
    top = RA + 96 * ps
    if is_player:
        body = CREAM
    elif boss:
        body = acc
    else:
        body = mix(acc, (255, 255, 255), 0.35)
    for k, a in enumerate(ptrs):
        L = Ls[index_at(spec, a, rot)]
        if k == 0 or spec.get("full_blades"):
            bl, bg = F.blade(ss, a, acc, body, (230, 220, 200), L["value"], L["prog"], tip=tip, sh=RA + 18 * ps, top=top,
                             wsh=34 * ps, wtop=50 * ps, win=(RA + 30 * ps, top - 18 * ps, 36 * ps), crown=bool(boss),
                             notch_col=acc if not boss else INK, glyph=glyph_name(L), rank=2 if tier == "elite" else 0)
        else:
            bl, bg = pin(ss, a, acc, body, L, tip, Rch1, k + 1, ps)
        if spec.get("full_blades") and len(ptrs) > 1:  # index tab: needle 1 / 2 / 3
            dd = ImageDraw.Draw(bl)
            tx, ty = Q(RA + 22 * ps, 0, a, ss)
            r = 12 * ss * ps
            dd.ellipse([tx - r, ty - r, tx + r, ty + r], fill=(255, 255, 255, 255), outline=INK + (255,), width=int(2 * ss))
            fi = f_num(int(r * 1.5))
            dd.text((tx - fi.getlength(str(k + 1)) / 2, ty - r * 0.95), str(k + 1), font=fi, fill=INK + (255,))
        shadow_of(canvas, bl, ss, 7, 12, 5, 0.65)
        add_glow(canvas, bg, ss, 0.9)
        over_pil(canvas, bl)
    if spec.get("orbit") and not lod:
        tag(canvas, ss, ptrs[0], RA, "ORBIT +%d / TURN" % spec["orbit"], acc)
    if preview and preview.get("style") == "A2":
        import preview16
        preview16.draw(canvas, spec, Ls, ss, preview, ptrs, RA, top, ps, index_at, acc)
    elif preview and preview.get("style") == "A":
        import preview15
        preview15.draw(canvas, spec, Ls, ss, preview, ptrs, RA, top, ps, index_at, glyph_name)
    elif preview:
        preview_layer(canvas, spec, Ls, ss, preview, (Rch0 - 2, Rch1 + 2), top)
        if preview["style"] == "ticker":
            L0 = Ls[index_at(spec, 0)]
            Ln = Ls[index_at(spec, -12.0 * preview["moves"][0])]
            split_window(canvas, ss, 0, top, RA, L0["value"], Ln["value"], PROGRAMS[L0["prog"]]["col"], PROGRAMS[Ln["prog"]]["col"], ps)
    # glass crescent
    dx, dy = grids(ss)
    rho = np.hypot(dx, dy)
    th = np.degrees(np.arctan2(dx, -dy)) % 360
    cres = np.exp(-((rho / R_lip - 0.88) / 0.06) ** 2) * np.clip(np.cos(np.radians(th - 315)), 0, 1) ** 2 * 0.10
    canvas[..., :3] += (cres * (rho < R_lip))[..., None]
    del dx, dy, rho, th, cres
    meta = dict(ptr_r=(RA + 30 * ps + top - 20 * ps) / 2, hp_r=RA + 36, top_r=top)
    if boss and banner_on and not lod:
        im3, d3 = layer(ss)
        gl3, gd3 = layer(ss)
        F.banner(im3, d3, gd3, ss, RW.CY - top - 8, boss["title"], boss["sub"], acc, mount=True)
        shadow_of(canvas, im3, ss, 6, 10, 6, 0.6)
        add_glow(canvas, gl3, ss)
        over_pil(canvas, im3)
    F.set_centre()
    rgb = np.clip(canvas[..., :3], 0, 1)
    a = np.clip(canvas[..., 3:], 0, 1)
    straight = np.where(a > 1e-4, rgb / np.maximum(a, 1e-4), 0)
    out = Image.fromarray((np.clip(np.concatenate([straight, a], 2), 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")
    bb = out.split()[3].point(lambda v: 255 if v > 3 else 0).getbbox()
    out = out.crop(bb)
    return out, (F.CX * ss - bb[0], F.CY * ss - bb[1]), meta


THREAT_HOT = (255, 70, 60)
ARMOUR_BASE = {"meridian": (60, 40, 22), "solace": (150, 160, 156), "halcyon": (60, 30, 96), "orbital": (120, 140, 150),
               "rebel_cell": (40, 8, 12)}


def pin(ss, ang, acc, body, L, tip, Rch1, num, ps):
    """Secondary reader: a short pin that stays inside the rim, with a round value window and its number."""
    im, d = layer(ss)
    gl, gd = layer(ss)
    root = Rch1 + 2
    pts = [Q(tip, 0, ang, ss), Q(R_OUT + 2, 20 * ps, ang, ss), Q(root, 22 * ps, ang, ss), Q(root, -22 * ps, ang, ss), Q(R_OUT + 2, -20 * ps, ang, ss)]
    gd.polygon(pts, fill=acc + (220,))
    d.polygon(pts, fill=body + (255,), outline=INK + (255,), width=int(3 * ss))
    cx, cy = Q(R_OUT + 20, 0, ang, ss)
    r = 19 * ss * ps
    pc = PROGRAMS[L["prog"]]["col"]
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(12, 12, 18, 255), outline=pc + (255,), width=int(2.4 * ss))
    txt = str(L["value"]) if L["value"] is not None else ""
    if txt:
        f = f_num(int(r * 1.25))
        tw = f.getlength(txt)
        d.text((cx - tw / 2, cy - r * 0.78), txt, font=f, fill=(255, 255, 255, 255))
    else:
        g = glyph_rgba(glyph_name(L), int(r * 1.3), 2 * ss)
        im.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))
    # reader number tab
    nx, ny = Q(root + 12, 0, ang, ss)
    rn = 11 * ss * ps
    d.ellipse([nx - rn, ny - rn, nx + rn, ny + rn], fill=acc + (255,), outline=INK + (255,), width=int(2 * ss))
    fn = f_num(int(rn * 1.5))
    s = str(num)
    d.text((nx - fn.getlength(s) / 2, ny - rn * 0.95), s, font=fn, fill=INK + (255,))
    return im, gl


def tag(canvas, ss, ang, R, text, acc):
    im, d = layer(ss)
    f = f_num(int(18 * ss))
    tw = f.getlength(text)
    tx, ty = Q(R + 40, 58, ang, ss)
    d.polygon([(tx, ty - 13 * ss), (tx + tw + 20 * ss, ty - 13 * ss), (tx + tw + 28 * ss, ty), (tx + tw + 20 * ss, ty + 13 * ss),
               (tx, ty + 13 * ss), (tx - 9 * ss, ty)], fill=(14, 12, 20, 255), outline=acc + (255,), width=int(2 * ss))
    d.text((tx + 8 * ss, ty - 11 * ss), text, font=f, fill=acc + (255,))
    over_pil(canvas, im)
