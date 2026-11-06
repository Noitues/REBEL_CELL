"""C War Table: scene model + beat frames (all composited over the real Godot city plate)."""
import math, random
from wt_lib import *

GEO, NODES = load_geo()
CORE, HOME = "the_genome_core", "home"
EXPLOIT = {"t2_breach", "t2_intel", "t2_virus"}
TIER = {"t1": 1, "t2": 2, "t3": 3}
SITES = [k for k in NODES if k not in (CORE, HOME)]


def P(n):
    return T(NODES[n])


PITCH = 12.5
BEAMS = {
    "K1": dict(t="D", path=[CORE, "t3_c", "t2_virus", "t1_c", "t1_b", HOME], lane=0, sealed=False),
    "B": dict(t="D", path=[CORE, "t3_c", "t2_virus", "t1_c", "t1_b", HOME], lane=1, sealed=True),
    "K2": dict(t="D", path=[CORE, "t3_b", "t2_breach", "t1_b", "t1_c", HOME], lane=2, sealed=False),
    "C": dict(t="N", path=[CORE, "t3_b", "t2_breach", "t1_b", "t1_c", HOME], lane=3, sealed=True),
    "A": dict(t="E", path=[CORE, "t3_b", "t2_breach", "t1_b", "t1_a", HOME], lane=4, sealed=True),
}
LANE_MID = 2.0

_geo_cache = {}


def beam_geom(name):
    if name in _geo_cache:
        return _geo_cache[name]
    b = BEAMS[name]
    nodes = [P(n) for n in b["path"]]
    raw = route(nodes)
    # arclength at every node (raw)
    node_s = []
    for n in nodes:
        best = min(range(len(raw)), key=lambda i: (raw[i][0] - n[0]) ** 2 + (raw[i][1] - n[1]) ** 2)
        node_s.append(arclen(raw)[best])
    off = offset_poly(raw, (b["lane"] - LANE_MID) * PITCH)
    pts = fillet(off, 24)
    ls = arclen(pts)
    k = ls[-1] / (arclen(raw)[-1] or 1)
    out = dict(pts=pts, ls=ls, node_s=[s * k for s in node_s], raw=raw)
    _geo_cache[name] = out
    return out


def site_s(name, site):
    g = beam_geom(name)
    i = BEAMS[name]["path"].index(site)
    return g["node_s"][i]


# ---------------------------------------------------------------------------------------
def draw_beams(cv, active, alpha=None, sealed_style=None, hunter=False):
    """active: list of beam names. alpha: dict name->alpha(0..1). sealed -> thin dashed paper line."""
    alpha = alpha or {}
    # soft contact shadow under every line (reads over the busy city)
    sh = cv.layer()
    d = ImageDraw.Draw(sh)
    for n in active:
        g = beam_geom(n)
        P_ = pts2(g["pts"])
        d.line(P_, fill=(8, 4, 16, int(170 * alpha.get(n, 1.0))), width=int(15 * SS), joint="curve")
    sh = sh.filter(ImageFilter.GaussianBlur(5 * SS))
    cv.merge(sh)
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    for n in active:
        b = BEAMS[n]
        g = beam_geom(n)
        a = int(255 * alpha.get(n, 1.0))
        col = BEAM[b["t"]]
        sealed = b["sealed"] and (sealed_style or n in (sealed_style or []))
        if sealed_style == "all":
            sealed = b["sealed"]
        else:
            sealed = n in (sealed_style or [])
        if sealed:
            for seg in dashed(g["pts"], 14, 9):
                ink_line(d, seg, 4.6, (214, 208, 196), ink_w=1.8, alpha=int(a * 0.9))
            continue
        ink_line(d, g["pts"], 9.5, col, ink_w=2.6, alpha=a)
        if b["t"] == "N":
            line_w(d, g["pts"], 3.2, INK, int(a * 0.95))
        elif b["t"] == "D":
            s = 12
            while s < g["ls"][-1] - 10:
                p, _ = point_at(g["pts"], g["ls"], s)
                d.ellipse(sc([p[0] - 2.5, p[1] - 2.5, p[0] + 2.5, p[1] + 2.5]), fill=(255, 255, 255, int(a * 0.95)))
                s += 26
        else:
            s = 10
            while s < g["ls"][-1] - 8:
                p, ang = point_at(g["pts"], g["ls"], s)
                nx, ny = -math.sin(ang), math.cos(ang)
                d.line(sc([(p[0] - nx * 4.3, p[1] - ny * 4.3), (p[0] + nx * 4.3, p[1] + ny * 4.3)]), fill=rgba(INK, int(a * 0.8)), width=int(1.8 * SS))
                s += 14
        # riding passengers (Mini Metro): the beam's shape, so type reads without colour
        s = 90
        while s < g["ls"][-1] - 40:
            p, _ = point_at(g["pts"], g["ls"], s)
            rider(d, b["t"], p, col, a)
            s += 150
    cv.merge(lay)


def rider(d, kind, p, col, a=255, s=10.5):
    shape_glyph(d, kind, p[0], p[1], s + 1.7, INK, INK, 0, a)
    shape_glyph(d, kind, p[0], p[1], s + 0.2, (255, 255, 255), INK, 0, a)
    shape_glyph(d, kind, p[0], p[1], s - 2.0, col if kind != "N" else (90, 70, 110), INK, 0, a)


def draw_hunter(cv, show=True, lit=None):
    """Hunter: picks one of 2 cross streets; revealed last. Two dotted strings with a crosshair pawn between."""
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    for chain in (["t2_intel", "t2_breach", "t2_virus"], ["t3_core", "t3_b", "t3_c"]):
        pts = route([P(n) for n in chain])
        for seg in dashed(pts, 4, 10):
            ink_line(d, seg, 3.4, (255, 240, 220), ink_w=1.4)
        mid = P(chain[1])
        d.ellipse(sc([mid[0] + 20, mid[1] - 46, mid[0] + 50, mid[1] - 16]), fill=rgba(INK))
        g_crosshair(d, mid[0] + 35, mid[1] - 31, 8, (255, 240, 220))
    cv.merge(lay)


def tier_of(site):
    return TIER.get(site[:2], 2)


def draw_tokens(cv, down=(), taken=(), guards=None, skip=()):
    order = sorted([s for s in SITES if s not in skip], key=lambda s: P(s)[1])
    for s in order:
        st = "taken" if s in taken else ("down" if s in down else "healthy")
        cv.img = put_token(cv.img, P(s), tier_of(s), st, exploit=(s in EXPLOIT), seed=hash(s) % 97)


def draw_hq(cv, glow=False):
    p = P(CORE)
    cv.img = put_token(cv.img, p, 3, "healthy", R=42)
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    g_helix(d, p[0], p[1] - 3 * TH - 2, 15, (95, 150, 86), INK)
    cv.merge(lay)
    return p


def draw_home(cv, broken=False, hp_state="ok"):
    p = P(HOME)
    cv.img = put_token(cv.img, p, 2, "taken" if broken else "healthy", R=36)
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    g_house(d, p[0], p[1] - 2 * TH - 2, 13, (255, 61, 168) if not broken else (120, 60, 120))
    cv.merge(lay)


def draw_guard_stickers(cv, guards):
    """guards: list of (site, type, verb, spent)."""
    by = {}
    for g in guards:
        by.setdefault(g[0], []).append(g)
    for site, lst in by.items():
        p = P(site)
        top = (p[0], p[1] - TH * tier_of(site) - 4)
        for i, (s_, ty, verb, spent) in enumerate(lst):
            stock = {"GUARD": STOCK_CREAM, "SHIFT": STOCK_YELLOW, "JAM": STOCK_PINK}[verb]
            if spent:
                stock = (190, 186, 180)
            sp = sticker(verb, ty, stock, label=False)
            n = len(lst)
            dx = (i - (n - 1) / 2) * 24
            ang = (i - (n - 1) / 2) * -10 + (3 if site == "t1_b" else -3)
            cv.img = put_sticker(cv.img, sp, (top[0] + dx, top[1] - 8), ang, scale=0.37, lift=0.4)
            if spent:
                lay = cv.layer()
                d = ImageDraw.Draw(lay)
                line_w(d, [(top[0] + dx - 7, top[1] - 12), (top[0] + dx + 7, top[1] + 4)], 2.2, INK, 200)
                cv.merge(lay)


# ---- ITB intent arrows ---------------------------------------------------------------------
def intent_arrow(lay, tail, head, color, w=15.0, hollow=False, blocked=False, alpha=255):
    d = ImageDraw.Draw(lay)
    dx, dy = head[0] - tail[0], head[1] - tail[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    hl = w * 1.5
    base = (head[0] - ux * hl, head[1] - uy * hl)
    shaft = [(tail[0] + nx * w / 2, tail[1] + ny * w / 2), (base[0] + nx * w / 2, base[1] + ny * w / 2),
             (base[0] + nx * w * 1.0, base[1] + ny * w * 1.0), head,
             (base[0] - nx * w * 1.0, base[1] - ny * w * 1.0), (base[0] - nx * w / 2, base[1] - ny * w / 2),
             (tail[0] - nx * w / 2, tail[1] - ny * w / 2)]
    if blocked:
        # flat bar head: "T" stop
        bar = [(head[0] + nx * w * 1.2, head[1] + ny * w * 1.2), (head[0] - nx * w * 1.2, head[1] - ny * w * 1.2)]
        shaft = [(tail[0] + nx * w / 2, tail[1] + ny * w / 2), (head[0] - ux * 4 + nx * w / 2, head[1] - uy * 4 + ny * w / 2),
                 (head[0] - ux * 4 - nx * w / 2, head[1] - uy * 4 - ny * w / 2), (tail[0] - nx * w / 2, tail[1] - ny * w / 2)]
    if hollow:
        fill = (*color, 70)
        d.polygon(pts2(shaft), fill=fill)
        pl = shaft + [shaft[0]]
        for seg in dashed(pl, 6, 4):
            line_w(d, seg, 2.6, color, alpha)
        d.line(pts2(pl), fill=rgba(INK, 120), width=SS)
    else:
        d.polygon(pts2(shaft), fill=rgba(INK, alpha))
        # inset
        k = 0.72
        cx = sum(p[0] for p in shaft) / len(shaft)
        cy = sum(p[1] for p in shaft) / len(shaft)
        ins = [(cx + (p[0] - cx) * k, cy + (p[1] - cy) * k) for p in shaft]
        d.polygon(pts2(ins), fill=rgba(color, alpha))
        d.line(pts2([(tail[0] + ux * 6, tail[1] + uy * 6), (base[0] - ux * 2, base[1] - uy * 2)]), fill=(255, 255, 255, int(alpha * 0.55)), width=int(1.6 * SS))
    if blocked:
        d.polygon(pts2([(bar[0][0] + ux * 2, bar[0][1] + uy * 2), (bar[1][0] + ux * 2, bar[1][1] + uy * 2),
                        (bar[1][0] - ux * 7, bar[1][1] - uy * 7), (bar[0][0] - ux * 7, bar[0][1] - uy * 7)]), fill=rgba(INK, alpha))
        d.polygon(pts2([(bar[0][0] - ux * 0, bar[0][1]), (bar[1][0], bar[1][1]),
                        (bar[1][0] - ux * 5, bar[1][1] - uy * 5), (bar[0][0] - ux * 5, bar[0][1] - uy * 5)]), fill=rgba(color, alpha))


def badge(lay, pos, color, text=None, glyph=None, r=18.5, hollow=False, alpha=255):
    d = ImageDraw.Draw(lay)
    d.ellipse(sc([pos[0] - r - 2, pos[1] - r - 2, pos[0] + r + 2, pos[1] + r + 2]), fill=rgba(INK, alpha))
    d.ellipse(sc([pos[0] - r, pos[1] - r, pos[0] + r, pos[1] + r]), fill=rgba((250, 248, 240) if hollow else color, alpha))
    if hollow:
        d.ellipse(sc([pos[0] - r + 2, pos[1] - r + 2, pos[0] + r - 2, pos[1] + r - 2]), outline=rgba(color, alpha), width=int(3 * SS))
    if text:
        f = font("anton", r * 1.25)
        tm = text_mask(text, f, 0)
        col = INK if (hollow or sum(color) > 480) else (255, 255, 255)
        lay.paste(Image.new("RGBA", tm.size, rgba(col, alpha)), (int(pos[0] * SS - tm.width / 2), int(pos[1] * SS - tm.height / 2)), tm)
    if glyph == "shield":
        g_shield(d, pos[0], pos[1] - 0.5, r * 0.55, (255, 255, 255) if not hollow else color)
    if glyph == "skull":
        g_skull(d, pos[0], pos[1], r * 0.62, (255, 255, 255))


def arrow_into(lay, beam, site, color, hollow=False, blocked=False, num=None, glyph=None, back=84, gap=30, off=(0, 0), badge_at=(26, -30)):
    g = beam_geom(beam)
    s = site_s(beam, site)
    ps = max(0, s - back)
    pe = max(1, s - gap)
    a, _ = point_at(g["pts"], g["ls"], ps)
    b, _ = point_at(g["pts"], g["ls"], pe)
    a = (a[0] + off[0], a[1] + off[1])
    b = (b[0] + off[0], b[1] + off[1])
    intent_arrow(lay, a, b, color, hollow=hollow, blocked=blocked)
    tp = P(site)
    if num is not None or glyph:
        badge(lay, (tp[0] + badge_at[0], tp[1] - TH * tier_of(site) + badge_at[1]), color, num, glyph, hollow=hollow)


# ---- HOME ring (Frostpunk-style integrity clock on the table) ---------------------------------
def home_ring(cv, hp=44, mx=50, preview=0, preview_color=DAMAGED, shards=0, crack=False, hollow_preview=False, rx=128, band=19):
    c = P(HOME)
    ry = rx * ISO_K
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    # table underlay disc
    d.ellipse(sc([c[0] - rx - 14, c[1] - ry - 14 * ISO_K - 2, c[0] + rx + 14, c[1] + ry + 14 * ISO_K + 2]), fill=(10, 6, 20, 165))
    d.ellipse(sc([c[0] - rx - 14, c[1] - ry - 14 * ISO_K - 2, c[0] + rx + 14, c[1] + ry + 14 * ISO_K + 2]), outline=rgba(INK, 255), width=int(2 * SS))
    seg = 360.0 / mx
    for i in range(mx):
        a0 = -90 + i * seg + 0.9
        a1 = -90 + (i + 1) * seg - 0.9
        outer = ellipse_pts(c[0], c[1], rx, ry, a0, a1, 4)
        inner = ellipse_pts(c[0], c[1], rx - band, ry - band * ISO_K, a1, a0, 4)
        poly = outer + inner
        if i < hp - preview:
            fill = HOLDS
        elif i < hp:
            fill = preview_color
        else:
            fill = (40, 30, 56)
        if i < hp - preview or i >= hp:
            d.polygon(pts2(poly), fill=rgba(fill), outline=rgba(INK), width=int(1.4 * SS))
        else:
            if hollow_preview:
                d.polygon(pts2(poly), fill=(*fill, 90), outline=rgba(INK), width=int(1.4 * SS))
                line_w(d, outer, 2.2, fill)
            else:
                d.polygon(pts2(poly), fill=rgba(fill), outline=rgba(INK), width=int(1.4 * SS))
                # hatch
                mid = ellipse_pts(c[0], c[1], rx - band / 2, ry - band / 2 * ISO_K, (a0 + a1) / 2, (a0 + a1) / 2, 1)[0]
                d.line(sc([(mid[0] - 3, mid[1] + 3), (mid[0] + 3, mid[1] - 3)]), fill=(255, 255, 255, 220), width=int(1.6 * SS))
    cv.merge(lay)


# ---- Frame chrome: HUD -------------------------------------------------------------------------
def chip(d, x0, y0, x1, y1):
    d.rounded_rectangle(sc([x0, y0, x1, y1]), radius=8 * SS, fill=(8, 18, 36, 235), outline=rgba(CRT_EDGE, 255), width=int(1.8 * SS))
    d.line(sc([(x0 + 8, y0 + 4), (x1 - 8, y0 + 4)]), fill=(255, 255, 255, 40), width=SS)


def num(lay, txt, x, y, size, col=(255, 255, 255), anchor="l"):
    f = font("anton", size)
    tm = text_mask(txt, f, 0)
    w = tm.width
    px = x * SS if anchor == "l" else (x * SS - w / 2 if anchor == "c" else x * SS - w)
    lay.paste(Image.new("RGBA", tm.size, rgba(col)), (int(px), int(y * SS - tm.height / 2)), tm)
    return w / SS


def hud(cv, hp=44, mx=50, heat=80, healthy=8, infected=0, raid=1, hp_col=HOLDS, hp_flash=False, tip_override=None):
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    # HEAT
    chip(d, 28, 12, 290, 70)
    g_flame(d, 54, 41, 15, BREACH if heat >= 75 else LOST)
    num(lay, str(heat), 80, 42, 34)
    gx0, gx1 = 140, 274
    d.rounded_rectangle(sc([gx0, 34, gx1, 48]), radius=5 * SS, fill=(30, 20, 44, 255), outline=rgba(INK), width=int(1.5 * SS))
    fw = (gx1 - gx0) * heat / 100
    d.rounded_rectangle(sc([gx0 + 2, 36, gx0 + fw, 46]), radius=4 * SS, fill=rgba(DAMAGED))
    for q in (25, 50, 75):
        xq = gx0 + (gx1 - gx0) * q / 100
        d.line(sc([(xq, 32), (xq, 50)]), fill=rgba(INK), width=SS * 2)
    # HOME
    chip(d, 310, 12, 520, 70)
    g_house(d, 340, 43, 14, (255, 61, 168))
    w = num(lay, str(hp), 366, 42, 34, hp_col if not hp_flash else DAMAGED)
    num(lay, "/" + str(mx), 366 + w + 3, 48, 20, (150, 160, 190))
    # integrity ticks (mini ring)
    # SCALE: healthy vs INFECTED (CITY LOST when infected outnumber healthy)
    chip(d, 540, 12, 900, 70)
    cx, cy = 720, 46
    tot = max(1, healthy + infected)
    tilt = tip_override if tip_override is not None else max(-1, min(1, (infected - healthy) / tot * 2.0)) * 17
    ang = math.radians(tilt)
    L = 72
    lx, ly = cx - L * math.cos(ang), cy - L * math.sin(ang)
    rx_, ry_ = cx + L * math.cos(ang), cy + L * math.sin(ang)
    d.polygon(sc([(cx, cy - 4), (cx - 11, cy + 14), (cx + 11, cy + 14)]), fill=rgba(PAPER), outline=rgba(INK))
    line_w(d, [(lx, ly), (rx_, ry_)], 4.5, INK)
    line_w(d, [(lx, ly), (rx_, ry_)], 2.4, PAPER)
    # card stacks
    def stack(px, py, n, col, tilt_=0):
        n = min(n, 9)
        for i in range(n):
            yy = py - 4 - i * 5.2
            d.rounded_rectangle(sc([px - 15, yy - 2.6, px + 15, yy + 2.6]), radius=2 * SS, fill=rgba(col), outline=rgba(INK), width=int(1.2 * SS))
    stack(lx + 6, ly, healthy, UNTOUCHED)
    stack(rx_ - 6, ry_, infected, PLUM2)
    # infected stack: pink veins edge
    for i in range(min(infected, 9)):
        yy = ry_ - 4 - 5.2 - i * 5.2
        d.line(sc([(rx_ - 6 - 14, yy + 1.5), (rx_ - 6 + 14, yy + 1.5)]), fill=rgba(VEIN), width=SS)
    num(lay, str(healthy), 580, 42, 34, UNTOUCHED, "c")
    num(lay, str(infected), 860, 42, 34, (255, 120, 205), "c")
    # RAID queue pips
    chip(d, 920, 12, 1050, 70)
    g_shield(d, 950, 40, 12, (230, 235, 250))
    num(lay, str(raid), 982, 42, 34)
    cv.merge(lay)


# ---- table props -------------------------------------------------------------------------------
def props(cv, pencil=True, stamp=True):
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    if pencil:
        # red grease pencil lying on the table (D28)
        def pen(cx, cy, ang):
            L, Wd = 250, 17
            im = Image.new("RGBA", (int((L + 40) * SS), int(Wd * 3 * SS)), (0, 0, 0, 0))
            dd = ImageDraw.Draw(im)
            y0 = Wd * SS
            dd.rounded_rectangle([20 * SS, y0, (20 + L) * SS, y0 + Wd * SS], radius=int(3 * SS), fill=rgba((196, 40, 52)), outline=rgba(INK), width=int(2 * SS))
            dd.rectangle([20 * SS + 8 * SS, y0 + 2 * SS, (20 + L) * SS - 6 * SS, y0 + 6 * SS], fill=(240, 120, 120, 255))
            dd.polygon([(20 * SS, y0), (3 * SS, y0 + Wd * SS / 2), (20 * SS, y0 + Wd * SS)], fill=rgba((236, 214, 170)), outline=rgba(INK))
            dd.polygon([(8 * SS, y0 + Wd * SS * 0.38), (3 * SS, y0 + Wd * SS / 2), (8 * SS, y0 + Wd * SS * 0.62)], fill=rgba((255, 59, 48)))
            dd.rectangle([(20 + L - 34) * SS, y0, (20 + L - 24) * SS, y0 + Wd * SS], fill=rgba((236, 230, 220)))
            return im
        pm = pen(0, 0, 0)
        sh = Image.new("RGBA", pm.size, (0, 0, 0, 0))
        sh.putalpha(pm.getchannel("A").point(lambda v: int(v * 0.6)))
        sh = sh.filter(ImageFilter.GaussianBlur(4 * SS))
        sh = Image.merge("RGBA", (Image.new("L", sh.size, 0),) * 3 + (sh.getchannel("A"),))
        cv.img = paste_rot(cv.img, sh, (1700 + 5, 1006 + 8), 14)
        cv.img = paste_rot(cv.img, pm, (1700, 1006), 14)
    if stamp:
        lay = cv.layer()
        d = ImageDraw.Draw(lay)
        cx, cy = 150, 985
        sh = Image.new("RGBA", cv.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse(sc([cx - 62, cy - 20, cx + 70, cy + 60]), fill=(0, 0, 0, 150))
        cv.img = Image.alpha_composite(cv.img, sh.filter(ImageFilter.GaussianBlur(7 * SS)))
        lay = cv.layer()
        d = ImageDraw.Draw(lay)
        d.rounded_rectangle(sc([cx - 56, cy - 4, cx + 56, cy + 38]), radius=8 * SS, fill=rgba((44, 34, 50)), outline=rgba(INK), width=int(2 * SS))
        d.rounded_rectangle(sc([cx - 50, cy - 1, cx + 50, cy + 12]), radius=6 * SS, fill=rgba((92, 76, 110)))
        d.ellipse(sc([cx - 30, cy - 52, cx + 30, cy + 10]), fill=rgba((120, 78, 52)), outline=rgba(INK), width=int(2 * SS))
        d.ellipse(sc([cx - 22, cy - 46, cx + 18, cy - 12]), fill=rgba((172, 116, 78)))
        d.ellipse(sc([cx - 14, cy - 40, cx - 2, cy - 30]), fill=(255, 220, 190, 120))
        cv.merge(lay)


def hand(cv, cards, base=(1000, 1010), spread=128, fan=3.2, scale=0.80, lift=None, focus=None):
    """cards: list of (verb, type). Returns positions."""
    n = len(cards)
    pos = []
    for i, (verb, ty) in enumerate(cards):
        t = i - (n - 1) / 2
        stock = {"GUARD": STOCK_CREAM, "SHIFT": STOCK_YELLOW, "JAM": STOCK_PINK}[verb]
        sp = sticker(verb, ty, stock, label=True)
        p = (base[0] + t * spread, base[1] + abs(t) ** 1.6 * 6 - (lift or {}).get(i, 0))
        cv.img = put_sticker(cv.img, sp, p, -t * fan, scale=scale, lift=1.0 + ((lift or {}).get(i, 0) > 0))
        pos.append(p)
    return pos


def odds_row(cv, tiers, x0=520, y=905, size=30):
    """Pictogram odds: one tile per outcome, stamped in tier colours (no words)."""
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    for i, c in enumerate(tiers):
        x = x0 + i * (size + 6)
        d.rounded_rectangle(sc([x + 2, y + 3, x + size + 2, y + size + 3]), radius=5 * SS, fill=(0, 0, 0, 120))
        d.rounded_rectangle(sc([x, y, x + size, y + size]), radius=5 * SS, fill=rgba(c), outline=rgba(INK), width=int(2 * SS))
        d.line(sc([(x + 4, y + 5), (x + size - 4, y + 5)]), fill=(255, 255, 255, 90), width=SS)
    cv.merge(lay)


# ---- FX -----------------------------------------------------------------------------------------
def pulse(cv, name, s, col, trail=60, r=7):
    g = beam_geom(name)
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    p0 = sub_path(g["pts"], g["ls"], max(0, s - trail), s)
    glow = cv.layer()
    gd = ImageDraw.Draw(glow)
    gd.line(pts2(p0), fill=(*col, 230), width=int(14 * SS), joint="curve")
    p, _ = point_at(g["pts"], g["ls"], s)
    gd.ellipse(sc([p[0] - 14, p[1] - 14, p[0] + 14, p[1] + 14]), fill=(*col, 255))
    glow = glow.filter(ImageFilter.GaussianBlur(8 * SS))
    cv.merge(glow)
    line_w(d, p0, 6, (255, 255, 255), 230)
    d.ellipse(sc([p[0] - r, p[1] - r, p[0] + r, p[1] + r]), fill=(255, 255, 255, 255), outline=rgba(INK), width=int(2 * SS))
    cv.merge(lay)
    return p


def burst(cv, c, col, r=34, spikes=12, seed=3, bits=True):
    rng = random.Random(seed)
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    pts = []
    for i in range(spikes * 2):
        a = math.pi * i / spikes + rng.uniform(-0.08, 0.08)
        rr = r * (1.0 if i % 2 == 0 else 0.5) * rng.uniform(0.85, 1.15)
        pts.append((c[0] + math.cos(a) * rr, c[1] + math.sin(a) * rr * 0.9))
    d.polygon(pts2(pts), fill=rgba(INK))
    ins = [(c[0] + (x - c[0]) * 0.82, c[1] + (y - c[1]) * 0.82) for x, y in pts]
    d.polygon(pts2(ins), fill=rgba(col))
    ins2 = [(c[0] + (x - c[0]) * 0.45, c[1] + (y - c[1]) * 0.45) for x, y in pts]
    d.polygon(pts2(ins2), fill=(255, 255, 255, 255))
    if bits:
        f = font("mono", 15)
        for i in range(16):
            a = rng.uniform(0, 6.283)
            rr = rng.uniform(r * 1.1, r * 2.3)
            ch = rng.choice("01")
            x, y = c[0] + math.cos(a) * rr, c[1] + math.sin(a) * rr * 0.75
            d.text((x * SS, y * SS), ch, font=f, fill=rgba(col, 235), anchor="mm")
            # streak back to impact
            line_w(d, [(c[0] + math.cos(a) * rr * 0.55, c[1] + math.sin(a) * rr * 0.4), (x, y)], 1.2, col, 120)
    cv.merge(lay)


def hex_flash(cv, c, col, r=30, n=3):
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    for i in range(n):
        rr = r * (0.7 + 0.45 * i)
        hp = hexpts(c[0], c[1], rr, 0.9, 30)
        a = int(255 * (1 - i / (n + 0.3)))
        d.line(pts2(hp + [hp[0]]), fill=rgba(INK, a), width=int(5.5 * SS))
        d.line(pts2(hp + [hp[0]]), fill=rgba(col, a), width=int(3 * SS))
    cv.merge(lay)


def lime_halo(cv, pos, r=26):
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    d.ellipse(sc([pos[0] - r, pos[1] - r * ISO_K - 4, pos[0] + r, pos[1] + r * ISO_K + 6]), outline=rgba(LIME), width=int(3.2 * SS))
    d.ellipse(sc([pos[0] - r - 5, pos[1] - (r + 5) * ISO_K - 4, pos[0] + r + 5, pos[1] + (r + 5) * ISO_K + 6]), outline=(212, 255, 0, 110), width=int(1.6 * SS))
    cv.merge(lay)


def clock(lay, pos, frac=0.75, r=10):
    """Frostpunk-style decay clock: plum wedge fills toward TAKEN."""
    d = ImageDraw.Draw(lay)
    d.ellipse(sc([pos[0] - r - 2, pos[1] - r - 2, pos[0] + r + 2, pos[1] + r + 2]), fill=rgba(INK))
    d.ellipse(sc([pos[0] - r, pos[1] - r, pos[0] + r, pos[1] + r]), fill=rgba(PAPER))
    d.pieslice(sc([pos[0] - r, pos[1] - r, pos[0] + r, pos[1] + r]), -90, -90 + 360 * frac, fill=rgba((88, 30, 92)))
    d.ellipse(sc([pos[0] - r, pos[1] - r, pos[0] + r, pos[1] + r]), outline=rgba(INK), width=int(1.6 * SS))
    ex = pos[0] + r * 1.0 * math.cos(math.radians(-90 + 360 * frac))
    ey = pos[1] + r * 1.0 * math.sin(math.radians(-90 + 360 * frac))
    d.line(sc([(pos[0], pos[1]), (ex, ey)]), fill=rgba(VEIN), width=int(1.8 * SS))


def marks(cv, down=(), taken=(), clocks=True, circle=False):
    """D28 grease-pencil marks: DOWN = red X; TAKEN = pink-ringed X; decay clock on DOWN."""
    lay = cv.layer()
    for s in down:
        p = P(s)
        c = (p[0], p[1] - TH * tier_of(s) - 2)
        grease_x(lay, p[0] + 8, p[1] - 12, 23, BREACH, seed=hash(s) % 50 + 1)
        if clocks:
            clock(lay, (p[0] + 34, p[1] - 44), 0.8, 13)
    for s in taken:
        p = P(s)
        grease_circle(lay, p[0], p[1] - 12, 33, 27, VEIN, seed=hash(s) % 50 + 3)
        grease_x(lay, p[0], p[1] - 12, 16, VEIN, seed=hash(s) % 50 + 2, w=4.4)
    cv.merge(lay)


def put_stamp(cv, word, color, pos, angle=-7, size=60, glyph=None, tag=True, tag_size=(330, 170), seed=3):
    if tag:
        tg, ctr = paper_tag(*tag_size, seed=seed)
        cv.img = paste_rot(cv.img, tg, pos, angle * 0.5)
    sp = stamp_sprite(word, color, size, glyph=glyph, seed=seed)
    cv.img = paste_rot(cv.img, sp, (pos[0] + 6, pos[1] + 14), angle)


def hq_queue(cv, items):  # chips 44px
    """The corp HQ queue: what is coming. items: ('shape','D')|('env','A')|('eye',)"""
    p = P(CORE)
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    n = len(items)
    x0 = p[0] - (n - 1) * 22
    for i, it in enumerate(items):
        x, y = x0 + i * 44, p[1] - 112
        d.rounded_rectangle(sc([x - 20, y - 20, x + 20, y + 22]), radius=7 * SS, fill=(14, 10, 26, 235), outline=rgba(INK), width=int(2.4 * SS))
        if it[0] == "shape":
            shape_glyph(d, it[1], x, y, 11.5, BEAM[it[1]], INK, 2.2)
        elif it[0] == "env":
            g_envelope(d, x, y + 1, 30, 21, (236, 228, 206))
            d.ellipse(sc([x - 6, y - 2, x + 6, y + 10]), fill=rgba(BREACH), outline=rgba(INK), width=SS)
            f = font("anton", 13)
            tm = text_mask(it[1], f, 0)
            lay.paste(Image.new("RGBA", tm.size, (255, 255, 255, 255)), (int(x * SS - tm.width / 2), int((y + 3) * SS - tm.height / 2)), tm)
        else:
            g_crosshair(d, x, y + 1, 9.5, (255, 240, 220))
    cv.merge(lay)


# ---- ITB tile highlight + drop arrow ---------------------------------------------------------------
def tile_mark(lay, pos, color, r=None, hollow=False, alpha=255):
    """ITB target-tile highlight: a hex outline on the table around the token."""
    r = r or (TR + 12)
    d = ImageDraw.Draw(lay)
    hp = hexpts(pos[0], pos[1], r, ISO_K)
    if not hollow:
        d.polygon(pts2(hp), fill=(*color, 70))
    P_ = hp + [hp[0]]
    d.line(pts2(P_), fill=rgba(INK, alpha), width=int(7.5 * SS), joint="curve")
    if hollow:
        for seg in dashed(P_, 8, 5):
            line_w(d, seg, 3.6, color, alpha)
    else:
        d.line(pts2(P_), fill=rgba(color, alpha), width=int(4 * SS), joint="curve")


def drop_arrow(lay, pos, color, dx=0, top=None, height=92, blocked=False, hollow=False, num=None, glyph=None, tier=1, badge_dx=0, w=17.0):
    """ITB telegraph: a fat arrow dropping from above onto the target; number badge on the shaft."""
    ty = pos[1] - (TH * tier if top is None else top)
    head = (pos[0] + dx, ty - 6)
    tail = (pos[0] + dx, ty - 6 - height)
    intent_arrow(lay, tail, head, color, w=w, hollow=hollow, blocked=blocked)
    if num is not None or glyph:
        badge(lay, (pos[0] + dx + badge_dx, ty - 6 - height * 0.62), color, num, glyph, hollow=hollow)


def aim_arrow(lay, pos, color, ang, tier=1, length=96, standoff=34, blocked=False, hollow=False, num=None, glyph=None, w=22.0, badge_t=0.55, badge_perp=0):  # noqa
    """ITB intent arrow travelling in direction ang (deg, screen) onto the target token."""
    u = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
    centre = (pos[0], pos[1] - TH * tier * 0.7 - 4)
    head = (centre[0] - u[0] * standoff, centre[1] - u[1] * standoff)
    tail = (head[0] - u[0] * length, head[1] - u[1] * length)
    intent_arrow(lay, tail, head, color, w=w, hollow=hollow, blocked=blocked)
    if num is not None or glyph:
        bp = (tail[0] + (head[0] - tail[0]) * badge_t - u[1] * badge_perp, tail[1] + (head[1] - tail[1]) * badge_t + u[0] * badge_perp)
        badge(lay, bp, color, num, glyph, hollow=hollow)


def lime_halo_circle(cv, pos, r):
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    d.ellipse(sc([pos[0] - r, pos[1] - r, pos[0] + r, pos[1] + r]), outline=rgba(LIME), width=int(4 * SS))
    d.ellipse(sc([pos[0] - r - 6, pos[1] - r - 6, pos[0] + r + 6, pos[1] + r + 6]), outline=(212, 255, 0, 110), width=int(2 * SS))
    cv.merge(lay)


def table_spill(cv):
    """The Bloom ink runs over the foam-board edge onto the felt (CITY LOST): plum body, hot hairline, drips."""
    rng = np.random.default_rng(12)
    m = Image.new("L", (W * SS, H * SS), 0)
    d = ImageDraw.Draw(m)
    x = 90
    while x < 1100:
        r = rng.uniform(22, 62)
        d.ellipse(sc([x - r, 872 + rng.uniform(-6, 26) - r * 0.2, x + r, 872 + rng.uniform(6, 40) + r]), fill=255)
        x += r * rng.uniform(0.7, 1.3)
    for _ in range(9):  # drips running down the felt
        xx = rng.uniform(120, 1050)
        wd = rng.uniform(9, 17)
        ln = rng.uniform(60, 170)
        d.rounded_rectangle(sc([xx, 880, xx + wd, 880 + ln]), radius=int(wd / 2 * SS), fill=255)
        d.ellipse(sc([xx - wd * 0.35, 880 + ln - wd * 0.6, xx + wd * 1.35, 880 + ln + wd * 1.1]), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(4 * SS)).point(lambda v: 255 if v > 128 else 0)
    # pull out of the table only (below the slab edge)
    body = Image.new("RGBA", m.size, rgba(PLUM, 255))
    body.putalpha(m)
    edge = m.filter(ImageFilter.MaxFilter(5 * SS + 1))
    ring = ImageChops.subtract(edge, m)
    hot = Image.new("RGBA", m.size, rgba(HOTFRONT, 255))
    hot.putalpha(ring)
    glow = Image.new("RGBA", m.size, rgba(VEIN, 255))
    glow.putalpha(ring.filter(ImageFilter.GaussianBlur(8 * SS)).point(lambda v: int(v * 0.7)))
    cv.img = Image.alpha_composite(cv.img, glow)
    cv.img = Image.alpha_composite(cv.img, body)
    cv.img = Image.alpha_composite(cv.img, hot)
    # veins on the puddle
    lay = cv.layer()
    dd = ImageDraw.Draw(lay)
    for _ in range(14):
        x0 = rng.uniform(140, 1450)
        pts = [(x0, 872)]
        for i in range(4):
            pts.append((pts[-1][0] + rng.uniform(-18, 18), pts[-1][1] + rng.uniform(10, 32)))
        line_w(dd, pts, 1.6, VEIN, 200)
    lay.putalpha(ImageChops.multiply(lay.getchannel("A"), m))
    cv.merge(lay)
