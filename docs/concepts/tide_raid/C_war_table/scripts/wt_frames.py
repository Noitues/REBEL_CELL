"""C War Table: the ten beat frames. State is declared per frame (art-only storyboard)."""
from wt_scene import *

GUARDS = [("t1_c", "D", "GUARD", False), ("t1_c", "D", "GUARD", False), ("t1_b", "N", "GUARD", False)]
HAND = [("GUARD", "D"), ("GUARD", "D"), ("GUARD", "N"), ("GUARD", "E"), ("SHIFT", "E"), ("JAM", "N"), ("GUARD", "D")]


def new(taken=(), r=78, dim=0.9, extra=None):
    seeds = [(*P(s), r) for s in taken] + (extra or [])
    bl = make_bloom(seeds) if seeds else None
    return Canvas(make_base(bl, dim))


def ground_rings(cv, sites, col, r=24):
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    for s in sites:
        p = P(s)
        d.ellipse(sc([p[0] - r, p[1] - r * ISO_K, p[0] + r, p[1] + r * ISO_K]), outline=rgba(col, 230), width=int(3 * SS))
    cv.merge(lay)


def common(cv, taken=(), down=(), guards=(), beams=(), sealed=(), alpha=None, hunter=False, ring=None, clocks=True, home_broken=False,
           spent=(), queue=None):
    ring = ring or dict(hp=44)
    home_ring(cv, **ring)
    draw_beams(cv, list(beams) + list(sealed), alpha, sealed_style=list(sealed))
    if hunter:
        draw_hunter(cv)
    draw_tokens(cv, down, taken)
    draw_guard_stickers(cv, [g for g in guards])
    marks(cv, down, taken, clocks)
    draw_hq(cv)
    draw_home(cv, home_broken)
    if queue:
        hq_queue(cv, queue)


TAKEN0 = ("t1_d", "t2_intel")


# ------------------------------------------------------------------------------------------------
def f_decay():
    cv = new(r=0, extra=[(*P("t1_d"), 84), (*P("t2_intel"), 70)])
    common(cv, taken=(), down=("t1_d", "t2_intel"), ring=dict(hp=44), clocks=True)
    # clocks full -> sweep done: pink front rings around the DOWN tokens, TAKEN ring marks inked on
    lay = cv.layer()
    for s in ("t1_d", "t2_intel"):
        p = P(s)
        grease_circle(lay, p[0], p[1] - 8, 28, 23, VEIN, seed=9)
    cv.merge(lay)
    # two INFECTED cards flying from the tokens to the HUD scale
    for k, s in enumerate(("t1_d", "t2_intel")):
        p = P(s)
        a = (p[0], p[1] - 40)
        b = (860 - k * 16, 60)
        mid = ((a[0] + b[0]) / 2 + 60, (a[1] + b[1]) / 2 - 140)
        lay = cv.layer()
        d = ImageDraw.Draw(lay)
        prev = a
        for i in range(1, 25):
            t = i / 24
            x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * mid[0] + t * t * b[0]
            y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * mid[1] + t * t * b[1]
            if i % 2:
                line_w(d, [prev, (x, y)], 2.2, VEIN, 190)
            prev = (x, y)
        cv.merge(lay)
        sp = Image.new("RGBA", (int(70 * SS), int(92 * SS)), (0, 0, 0, 0))
        dd = ImageDraw.Draw(sp)
        dd.rounded_rectangle([6 * SS, 6 * SS, 64 * SS, 86 * SS], radius=8 * SS, fill=rgba(PLUM2), outline=rgba(INK), width=int(2.5 * SS))
        for j in range(4):
            dd.line([(10 * SS, (20 + j * 16) * SS), (60 * SS, (14 + j * 16 + 8) * SS)], fill=rgba(VEIN), width=int(1.6 * SS))
        g_skull(dd, 35, 46, 12, (255, 128, 215), PLUM)
        t = 0.55 + 0.25 * k
        x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * mid[0] + t * t * b[0]
        y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * mid[1] + t * t * b[1]
        cv.img = put_sticker(cv.img, sp, (x, y), -14 + k * 18, scale=0.62, lift=1.6)
    hud(cv, 44, 50, 80, healthy=8, infected=1)
    props(cv)
    return cv


def f_draw():
    cv = new(TAKEN0)
    common(cv, taken=TAKEN0, beams=["K1", "K2"], sealed=["A", "B", "C"], ring=dict(hp=44),
           queue=[("shape", "D"), ("shape", "D"), ("env", "A"), ("env", "B"), ("env", "C"), ("eye",)])
    draw_hunter(cv)
    hud(cv, 44, 50, 80, healthy=8, infected=2)
    hand(cv, HAND[:6], base=(1010, 962), spread=140, scale=0.92, lift={2: 34})
    # card mid-flight: dealt from the deck (lower-right)
    sp = sticker("GUARD", "D", STOCK_CREAM)
    for i, (p, a) in enumerate([((1560, 960), 14), ((1625, 905), 26)]):
        pass
    cv.img = put_sticker(cv.img, sp, (1560, 958), 17, scale=0.9, lift=2.2)
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    for k in range(4):
        line_w(d, [(1640 + k * 22, 905 - k * 26), (1600 + k * 22, 935 - k * 26)], 3, (255, 255, 255), 120 - k * 25)
    cv.merge(lay)
    props(cv)
    return cv


def _plan_common(cv, taken=TAKEN0, revealed=("A",), ring=None):
    sealed = [n for n in ("A", "B", "C") if n not in revealed]
    common(cv, taken=taken, guards=GUARDS, beams=["K1", "K2"] + list(revealed), sealed=sealed, ring=ring or dict(hp=44),
           queue=[("shape", "D"), ("shape", "D")] + [("env", n) for n in sealed] + [("eye",)])
    draw_hunter(cv)


def f_plan(with_hand=True):
    cv = new(TAKEN0)
    # legal-drop hints: sites on the picked card's (D guard) beams' paths glow in the D hue
    ground_rings(cv, ["t1_c", "t1_b", "t2_virus", "t3_c", "t2_breach", "t3_b"], BEAM["D"], 21)
    ground_rings(cv, ["t1_c"], (255, 255, 255), 27)
    _plan_common(cv)
    lime_halo(cv, P("t1_c"), 44)
    if with_hand:
        hand(cv, HAND[3:], base=(1010, 962), spread=140, scale=0.92)
    # held card hovering above the district it will land on (the lift shadow says "not yet placed")
    sp = sticker("GUARD", "E", STOCK_CREAM, label=False)
    cv.img = put_sticker(cv.img, sp, (P("t1_c")[0] + 52, P("t1_c")[1] - 90), -9, scale=0.40, lift=2.4)
    hud(cv, 44, 50, 80, healthy=8, infected=2)
    props(cv, stamp=with_hand)
    return cv


def f_plan_nopanels():
    cv = new(TAKEN0)
    ground_rings(cv, ["t1_c", "t1_b", "t2_virus", "t3_c", "t2_breach", "t3_b"], BEAM["D"], 21)
    ground_rings(cv, ["t1_c"], (255, 255, 255), 27)
    _plan_common(cv)
    lime_halo(cv, P("t1_c"), 44)
    sp = sticker("GUARD", "E", STOCK_CREAM, label=False)
    cv.img = put_sticker(cv.img, sp, (P("t1_c")[0] + 52, P("t1_c")[1] - 90), -9, scale=0.40, lift=2.4)
    hud(cv, 44, 50, 80, healthy=8, infected=2)
    return cv


def _forecast_tiles(cv):
    """Ground layer: ITB target tiles (under lines and tokens)."""
    lay = cv.layer()
    tile_mark(lay, P("t1_c"), LOST, r=TR + 14)
    tile_mark(lay, P("t1_b"), HOLDS, r=TR + 14, hollow=True)
    tile_mark(lay, P(HOME), DAMAGED, r=TR + 22)
    cv.merge(lay)


def _forecast_marks(cv, taken):
    lay = cv.layer()
    c, b, h = P("t1_c"), P("t1_b"), P(HOME)
    aim_arrow(lay, c, HOLDS, 147, blocked=True, glyph="shield", length=96, standoff=66)             # K1 (D) stopped by the D guard
    aim_arrow(lay, c, LOST, 0, num="1", length=104, standoff=68)                                    # K2 (D) lands: one site down
    aim_arrow(lay, b, HOLDS, 0, blocked=True, num="C", length=104, standoff=68)                      # C (N) stopped by the N guard
    aim_arrow(lay, h, DAMAGED, 90, tier=2, num="-6", length=124, standoff=40, w=28.0)               # A (E) reaches HOME
    badge(lay, (c[0] + 4, c[1] + 54), HOLDS, "B", r=15, hollow=True)                                 # B is still sealed: a hollow ghost chip
    cv.merge(lay)


def f_forecast():
    cv = new(TAKEN0)
    _forecast_tiles(cv)
    # forecast ring: HOME 44/50 with the worst case preview (-6)
    _plan_common(cv, revealed=("A", "C"), ring=dict(hp=44, preview=6))
    _forecast_marks(cv, TAKEN0)
    hud(cv, 44, 50, 80, healthy=8, infected=2)
    # odds: one stamped tile per outcome (12 of 12 rolls) in the ruled tier colours
    odds_row(cv, [UNTOUCHED] * 1 + [HOLDS] * 6 + [LOST] * 3 + [DAMAGED] * 2, x0=86, y=895)
    # table: the held hand is already down; only the odds row + props
    props(cv)
    return cv


def f_response():
    cv = new(TAKEN0)
    common(cv, taken=TAKEN0, guards=GUARDS, beams=["K1", "K2"], sealed=["A", "B", "C"], alpha={"K1": 0.55, "K2": 0.55}, ring=dict(hp=44))
    draw_hunter(cv)
    hud(cv, 44, 50, 80, healthy=8, infected=2)
    # four response tokens: round vinyl discs (word + glyph + outcome pips)
    acts = [("DEPLOY", "deploy"), ("HOLD", "hold"), ("MOVE", "move"), ("SACRIFICE", "sac")]
    outs = {"DEPLOY": [HOLDS, LOST, DAMAGED], "HOLD": [HOLDS, HOLDS, LOST], "MOVE": [HOLDS, LOST, LOST], "SACRIFICE": [UNTOUCHED, UNTOUCHED, BREACH]}
    lay = cv.layer()
    for i, (w, k) in enumerate(acts):
        cx = 600 + i * 215
        cy = 968 - (24 if w == "HOLD" else 0)
        sel = w == "HOLD"
        r = 66
        sh = Image.new("RGBA", cv.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse(sc([cx - r + 6, cy - r + 10 + (8 if sel else 0), cx + r + 6, cy + r + 10 + (8 if sel else 0)]), fill=(0, 0, 0, 160))
        cv.img = Image.alpha_composite(cv.img, sh.filter(ImageFilter.GaussianBlur((6 if sel else 3) * SS)))
        d = ImageDraw.Draw(lay)
        d.ellipse(sc([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4]), fill=(250, 250, 246, 255), outline=rgba(INK), width=int(2 * SS))
        d.ellipse(sc([cx - r, cy - r, cx + r, cy + r]), fill=rgba((52, 38, 70) if not sel else STOCK_CREAM), outline=rgba(INK), width=int(2.5 * SS))
        gc = (255, 255, 255) if not sel else INK
        if k == "deploy":
            hexd = hexpts(cx, cy + 6, 22, ISO_K)
            d.polygon(pts2(hexd), fill=rgba((120, 100, 128)), outline=rgba(INK), width=int(2 * SS))
            line_w(d, [(cx, cy - 36), (cx, cy - 6)], 7, gc)
            d.polygon(pts2([(cx - 13, cy - 10), (cx + 13, cy - 10), (cx, cy + 6)]), fill=rgba(gc))
        elif k == "hold":
            g_shield(d, cx, cy - 4, 24, INK)
            d.rectangle(sc([cx - 9, cy - 14, cx - 3, cy + 6]), fill=rgba(STOCK_CREAM))
            d.rectangle(sc([cx + 3, cy - 14, cx + 9, cy + 6]), fill=rgba(STOCK_CREAM))
        elif k == "move":
            hexd = hexpts(cx, cy + 10, 15, ISO_K)
            d.polygon(pts2(hexd), fill=rgba(gc))
            for a in (0, 90, 180, 270):
                ux, uy = math.cos(math.radians(a)), math.sin(math.radians(a))
                tip = (cx + ux * 36, cy - 6 + uy * 30)
                line_w(d, [(cx + ux * 14, cy - 6 + uy * 12), tip], 5, gc)
                nx, ny = -uy, ux
                d.polygon(pts2([(tip[0] + ux * 9, tip[1] + uy * 9), (tip[0] + nx * 8, tip[1] + ny * 8), (tip[0] - nx * 8, tip[1] - ny * 8)]), fill=rgba(gc))
        else:
            hexd = hexpts(cx, cy + 12, 17, ISO_K)
            d.polygon(pts2(hexd), fill=rgba(gc))
            g_flame(d, cx, cy - 12, 15, BREACH)
        # outcome pips (what this response tends to give)
        for j, c in enumerate(outs[w]):
            px = cx + (j - 1) * 17
            d.ellipse(sc([px - 6, cy + r - 22, px + 6, cy + r - 10]), fill=rgba(c), outline=rgba(INK), width=int(1.6 * SS))
    cv.merge(lay)
    lay = cv.layer()
    for i, (w, k) in enumerate(acts):
        cx = 600 + i * 215
        cy = 968 - (24 if w == "HOLD" else 0)
        f = font("anton", 21)
        tm = text_mask(w, f, 1)
        tag = Image.new("RGBA", (tm.width + 28 * SS, tm.height + 12 * SS), (0, 0, 0, 0))
        ImageDraw.Draw(tag).rounded_rectangle([0, 0, tag.width - 1, tag.height - 1], radius=6 * SS, fill=rgba(INK), outline=(255, 255, 255, 255), width=int(1.5 * SS))
        tag.paste(Image.new("RGBA", tm.size, (255, 255, 255, 255)), (14 * SS, 6 * SS), tm)
        lay.paste(tag, (int(cx * SS - tag.width / 2), int((cy - 66 - 14) * SS - tag.height / 2)), tag)
    cv.merge(lay)
    lime_halo_circle(cv, (600 + 215, 968 - 24), 84)
    props(cv, stamp=False)
    return cv


SPENT = [("t1_c", "D", "GUARD", True), ("t1_c", "D", "GUARD", True), ("t1_b", "N", "GUARD", True)]


def fallen_stickers(cv, site, n=2, spent=True):
    """Spent guard stickers peeled off and lying on the table beside a toppled token."""
    p = P(site)
    for i in range(n):
        sp = sticker("GUARD", "D", (190, 186, 180), label=False)
        cv.img = put_sticker(cv.img, sp, (p[0] - 62 + i * 26, p[1] + 38 + i * 6), -24 + i * 30, scale=0.36, lift=0.2)
        lay = cv.layer()
        d = ImageDraw.Draw(lay)
        cx, cy = p[0] - 62 + i * 26, p[1] + 38 + i * 6
        line_w(d, [(cx - 7, cy - 8), (cx + 3, cy), (cx - 2, cy + 3), (cx + 8, cy + 11)], 2.4, INK, 210)
        cv.merge(lay)


def f_playout_impact():
    """K1 (D) arrives at t1_c: the D guard takes it. Shield flash, bits, the pawn knocked off the line."""
    cv = new(TAKEN0)
    common(cv, taken=TAKEN0, guards=GUARDS, beams=["K1", "K2", "A", "C"], sealed=["B"],
           alpha={"K2": 0.25, "K1": 1.0, "A": 0.25, "B": 0.25, "C": 0.25}, ring=dict(hp=44))
    s = site_s("K1", "t1_c") - 40
    pulse(cv, "K1", s, BEAM["D"], trail=190, r=9)
    tp = P("t1_c")
    hex_flash(cv, (tp[0], tp[1] - 20), UNTOUCHED, 46, 3)
    burst(cv, (tp[0] + 4, tp[1] - 34), UNTOUCHED, r=44, seed=5)
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    kp = (tp[0] + 112, tp[1] + 52)
    d.ellipse(sc([kp[0] - 18, kp[1] - 8, kp[0] + 18, kp[1] + 14]), fill=(0, 0, 0, 130))
    # tipped pawn: lying circle (D) with a grease X
    d.ellipse(sc([kp[0] - 14, kp[1] - 15, kp[0] + 14, kp[1] + 6]), fill=rgba(BEAM["D"]), outline=rgba(INK), width=int(2.6 * SS))
    grease_x(lay, kp[0], kp[1] - 5, 13, UNTOUCHED, seed=4, w=4.2)
    cv.merge(lay)
    lay = cv.layer()
    badge(lay, (tp[0] - 4, tp[1] - 108), HOLDS, glyph="shield", r=19)
    cv.merge(lay)
    hud(cv, 44, 50, 80, healthy=8, infected=2)
    props(cv)
    return cv


def f_playout_home():
    """Beam A (E, square) finds no E guard: it runs through to HOME. The ring takes the hit."""
    cv = new(TAKEN0)
    home_ring(cv, hp=44, preview=6, preview_color=BREACH)
    draw_beams(cv, ["A", "K1", "K2", "C"], {"A": 1.0, "K1": 0.16, "K2": 0.16, "C": 0.16}, sealed_style=[])
    down = ("t1_c",)
    draw_tokens(cv, down, TAKEN0)
    marks(cv, down, TAKEN0, clocks=False)
    fallen_stickers(cv, "t1_c")
    draw_guard_stickers(cv, [("t1_b", "N", "GUARD", True)])
    draw_hq(cv)
    draw_home(cv)
    hp = P(HOME)
    s = beam_geom("A")["ls"][-1] - 40
    pulse(cv, "A", s, BEAM["E"], trail=230, r=10)
    burst(cv, (hp[0] + 6, hp[1] - 50), BREACH, r=66, seed=8)
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    rng = random.Random(4)
    for i in range(7):
        a = math.radians(-90 - 7 * 7.2 + 7.2 * i)
        x = hp[0] + 128 * math.cos(a) * 1.35 + rng.uniform(-8, 8)
        y = hp[1] + 128 * ISO_K * math.sin(a) * 1.35 - rng.uniform(10, 44)
        pts = [(x + rng.uniform(-9, 9), y + rng.uniform(-6, 6)) for _ in range(4)]
        d.polygon(pts2(pts), fill=rgba(HOLDS), outline=rgba(INK), width=int(2 * SS))
    cv.merge(lay)
    tg, _ = paper_tag(150, 92, seed=5)
    cv.img = paste_rot(cv.img, tg, (hp[0] + 180, hp[1] - 130), 7)
    lay = cv.layer()
    num(lay, "-6", hp[0] + 180, hp[1] - 124, 66, BREACH, "c")
    cv.merge(lay)
    hud(cv, 38, 50, 80, healthy=8, infected=2, hp_col=BREACH, hp_flash=True)
    props(cv)
    return cv


def f_aftermath():
    cv = new(TAKEN0)
    home_ring(cv, hp=38, mx=50)
    down = ("t1_c",)
    draw_tokens(cv, down, TAKEN0)
    marks(cv, down, TAKEN0, clocks=True)
    fallen_stickers(cv, "t1_c")
    draw_guard_stickers(cv, [("t1_b", "N", "GUARD", True)])
    draw_hq(cv)
    draw_home(cv)
    # faint trails: where each beam went (grey residue), no more lines
    put_stamp(cv, "DAMAGED", DAMAGED, (1330, 735), angle=-8, size=70, glyph=lambda d, x, y, s, c, i: g_house(d, x, y, s, c, i), tag_size=(470, 210), seed=3)
    hud(cv, 38, 50, 80, healthy=8, infected=2, hp_col=DAMAGED)
    props(cv)
    return cv


def f_hq_step():
    cv = new(TAKEN0)
    home_ring(cv, hp=38, mx=50)
    down = ("t1_c",)
    draw_tokens(cv, down, TAKEN0)
    marks(cv, down, TAKEN0, clocks=True)
    fallen_stickers(cv, "t1_c")
    draw_guard_stickers(cv, [("t1_b", "N", "GUARD", True)])
    draw_hq(cv)
    draw_home(cv)
    hq_queue(cv, [("env", "A"), ("env", "B"), ("env", "C")])
    hp = P(HOME)
    tc = P("t1_c")
    offered = [("wrench", (740, 790), tc), ("shield", (520, 815), hp), ("flag", (1240, 790), None)]
    lay = cv.layer()
    d = ImageDraw.Draw(lay)
    for k, pos, tgt in offered:
        if tgt is None:
            continue
        a = (pos[0] - 30, pos[1] - 36)
        b = (tgt[0] + 40, tgt[1] + 44) if k == "wrench" else (tgt[0] + 142, tgt[1] + 24)
        mid = ((a[0] + b[0]) / 2, min(a[1], b[1]) - 80 if k == "wrench" else (a[1] + b[1]) / 2 + 10)
        pts = []
        for i in range(25):
            t = i / 24
            pts.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * mid[0] + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * mid[1] + t * t * b[1]))
        for seg in dashed(pts, 11, 7):
            line_w(d, seg, 4.2, (255, 255, 255), 240)
        ang = math.atan2(pts[-1][1] - pts[-3][1], pts[-1][0] - pts[-3][0])
        nx, ny = -math.sin(ang), math.cos(ang)
        tip = pts[-1]
        d.polygon(pts2([(tip[0] + math.cos(ang) * 16, tip[1] + math.sin(ang) * 16), (tip[0] + nx * 10, tip[1] + ny * 10), (tip[0] - nx * 10, tip[1] - ny * 10)]), fill=(255, 255, 255, 245))
    cv.merge(lay)
    for k, pos, tgt in offered:
        r = 50
        sh = Image.new("RGBA", cv.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse(sc([pos[0] - r + 6, pos[1] - r + 11, pos[0] + r + 6, pos[1] + r + 11]), fill=(0, 0, 0, 175))
        cv.img = Image.alpha_composite(cv.img, sh.filter(ImageFilter.GaussianBlur(5 * SS)))
        lay = cv.layer()
        d = ImageDraw.Draw(lay)
        dark = k == "flag"
        d.ellipse(sc([pos[0] - r - 5, pos[1] - r - 5, pos[0] + r + 5, pos[1] + r + 5]), fill=(250, 250, 246, 255), outline=rgba(INK), width=int(2.4 * SS))
        d.ellipse(sc([pos[0] - r, pos[1] - r, pos[0] + r, pos[1] + r]), fill=rgba((52, 38, 70) if dark else STOCK_CREAM), outline=rgba(INK), width=int(2.8 * SS))
        if k == "wrench":
            g_wrench(d, pos[0], pos[1], 26, INK)
            clock(lay, (pos[0] + 38, pos[1] - 38), 0.8, 14)
        elif k == "shield":
            g_shield(d, pos[0], pos[1] - 2, 27, INK)
            g_shield(d, pos[0], pos[1] - 2, 15, HOLDS)
        else:
            g_flag(d, pos[0] + 5, pos[1] + 2, 26, (255, 255, 255), (255, 255, 255))
        cv.merge(lay)
    hud(cv, 38, 50, 80, healthy=8, infected=2, hp_col=DAMAGED)
    props(cv)
    return cv


def f_city_lost():
    taken = ("t1_a", "t1_b", "t1_c", "t1_d", "t2_intel", "t2_breach")
    seeds = [(*P(s), 360) for s in ("t1_a", "t1_c", "t1_d")] + [(*P("t2_breach"), 560), (*P("t1_b"), 640), (*P(HOME), 260), (*P("t2_intel"), 460),
                                                                    (*P("t2_virus"), 420), (*P("t3_c"), 250)]
    cv = Canvas(make_base(make_bloom(seeds), 0.9))
    home_ring(cv, hp=0, mx=50)
    draw_tokens(cv, (), taken)
    marks(cv, (), taken, clocks=False)
    draw_hq(cv)
    draw_home(cv, broken=True)
    table_spill(cv)
    hud(cv, 0, 50, 80, healthy=4, infected=6, hp_col=BREACH, tip_override=15)
    put_stamp(cv, "CITY LOST", (255, 70, 150), (980, 560), angle=-6, size=104, glyph=lambda d, x, y, s, c, i: g_skull(d, x, y, s, c, i), tag_size=(720, 320), seed=9)
    props(cv)
    return cv


FRAMES = [
    ("01_decay", f_decay), ("02_draw", f_draw), ("03_plan", f_plan), ("04_forecast", f_forecast), ("05_response", f_response),
    ("06_playout_impact", f_playout_impact), ("07_playout_home", f_playout_home), ("08_aftermath", f_aftermath),
    ("09_hq_step", f_hq_step), ("10_city_lost", f_city_lost), ("11_panels_removed", f_plan_nopanels),
]
