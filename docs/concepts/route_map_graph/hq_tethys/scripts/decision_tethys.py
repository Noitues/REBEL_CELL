"""hq_tethys: the DECISION and HOVER finals' UI compose (the other corps' kit grammar, on the Tethys plates).

python decision_tethys.py <decision|hover> <plate.png> <rooms.json> <out.png> [--plate-out <pre-grade plate.png>]

It reuses the HQ kit widgets from hq_solace/scripts (sidekit, kit44, ui31: stickers, cables, chips, the corp paper
dossier, the terminals, the legend strip) and draws the Tethys fixture on top of the plate:
  current  = the arrival pod (outer_0), the causeway landing; walked = the DOCK LOCK and a room halfway along the causeway
  options  = 1 an inner pod on that pier (elite), 2 the adjacent ring pod (fight)
  ahead    = the rest of the branch to THE BLACK SMOKER (the target): station deck, the deep stair, the vent cap
The overlay is drawn at 1920 x 1080 twice (on black and on 50 % grey) and solved per pixel as out = plate * m + b, then
upscaled to the plate's size (the compose_aaa matte method of hq_compose). The hover grade (PIPELINE_SPEC 9.4) is ONE 2D
pass on the plate (outside the branch x cut_level, cut_desat, branch x branch_boost); there is no 3D cut.
The top-right panel is a neutral PLACEHOLDER: the BALLAST TIDE is a proposal (game design), not drawn here.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOL = os.path.join(os.path.dirname(os.path.dirname(HERE)), "hq_solace", "scripts")
sys.path.insert(0, SOL)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import hq_preset as HP  # noqa: E402  (the solace kit's preset: only its corp-paper header is patched below)
import kit44 as KT  # noqa: E402
import r32ui as U32  # noqa: E402
import sidekit as S  # noqa: E402
import ui31 as K  # noqa: E402
import r35ui as R35  # noqa: E402
import r31lib as RL  # noqa: E402

W, H = 1920, 1080
TEAL = (70, 225, 215)                                    # the frames' teal (designer ruling: not the spec's blue)
FLAT = 0.5
HOVER = dict(cut_level=0.20, cut_desat=0.70, branch_boost=1.35, type_glow=1.0)    # PIPELINE_SPEC 9.4
POD_R = dict(inner=4.2, outer=3.1, mid=2.5)              # drum radii in BU (DESIGN.md section 2)
KIND = dict(inner_0="elite", mid_0="router", outer_0="router", outer_1="terminal", inner_1="modem", main_deck="elite",
            vent_cap="modem", deck_2="router", deck_4="terminal")
WORDS = dict(router="FIGHT", elite="ELITE", terminal="EVENT", modem="SHOP")
CURRENT, OPT = "outer_0", ["inner_0", "mid_0"]
BRANCH_HOVER2 = ["mid_0", "outer_1", "inner_1", "main_deck", "deck_1", "deck_2", "deck_3", "deck_4", "deck_5", "vent_cap", "server"]
BRANCH_HOVER1 = ["inner_0", "main_deck", "deck_1", "deck_2", "deck_3", "deck_4", "deck_5", "vent_cap", "server"]
DISPATCH = "tide's rising. the inner pod's open; the ring pod's across. go deep while they bail."


# ---------------------------------------------------------------- Tethys bits of the kit (corp colour, crest, paper)
K.CORP["tethys"] = TEAL
K.CORP2["tethys"] = (8, 40, 46)
HP.PRESET["hq"]["dossier"] = ("TETHYS", "DEEP // AIR AND WATERLINE", TEAL)


def _crest(px):
    """The TIDE WHIRL, simplified: three crests turning round a calm centre (alpha mask, white)."""
    S4 = 4
    im = Image.new("L", (px * S4, px * S4), 0)
    d = ImageDraw.Draw(im)
    c = px * S4 / 2
    for k in range(3):
        a0 = k * 120.0
        pts = []
        for i in range(41):
            t = i / 40.0
            ang = math.radians(a0 + 20 + 230 * t)
            r = c * (0.78 - 0.50 * t * t)
            pts.append((c + r * math.cos(ang), c + r * math.sin(ang)))
        for i in range(len(pts) - 1):
            w = int(px * S4 * (0.13 * (1.0 - i / 44.0) + 0.02))
            d.line([pts[i], pts[i + 1]], fill=255, width=max(2, w))
            d.ellipse([pts[i][0] - w / 2, pts[i][1] - w / 2, pts[i][0] + w / 2, pts[i][1] + w / 2], fill=255)
    return im.resize((px, px), Image.LANCZOS)


_corp_emblem = KT.corp_emblem


def corp_emblem(px, col, corp="meridian"):
    if corp != "tethys":
        return _corp_emblem(px, col, corp)
    im = Image.new("RGBA", (px, px), tuple(col) + (0,))
    im.putalpha(_crest(px))
    return im


KT.corp_emblem = corp_emblem


# ---------------------------------------------------------------- geometry
class Scene:
    def __init__(self, rooms_json):
        R = json.load(open(rooms_json))
        self.res = R["res"]
        s = W / R["res"][0]
        self.s = s
        self.lens_k = 1920.0 * 30.0 / 36.0                 # px (1080 frame) * depth, lens 30 mm on a 36 mm sensor
        self.P = {}
        self.Z = {}
        for k, v in R["rooms"].items():
            if v["px"]:
                self.P[k] = (v["px"][0] * s, v["px"][1] * s)
                self.Z[k] = v["px"][2]

    def u(self, k):
        """screen px (1080 frame) per BU at room k"""
        return self.lens_k / self.Z[k]

    def pod_r(self, k):
        t = k.split("_")[0]
        return POD_R.get(t, 3.0)

    def ell(self, k, grow=1.0, up=0.0, n=28):
        """the room's frame: an ellipse round its drum (screen 1080), `up` raises it (mast / dome)"""
        x, y = self.P[k]
        if k == "main_deck":
            cx, cy = (x + self.P["crown"][0]) / 2, (y + self.P["crown"][1]) / 2
            rx = 10.8 * self.u(k) * grow
            ry = rx * 0.98
            y = cy
            x = cx
        elif k.startswith("deck_"):
            rx = 5.0 * self.u(k) * grow
            ry = rx * 0.55
        elif k in ("server", "vent_cap"):
            rx = 4.4 * self.u(k) * grow
            ry = rx * 0.8
        elif k == "lock":
            rx = 7.0 * self.u(k) * grow
            ry = rx * 0.8
        else:
            rx = self.pod_r(k) * self.u(k) * 1.12 * grow
            ry = rx * 0.92
            y -= rx * 0.25
        y -= up
        return [(x + rx * math.cos(2 * math.pi * i / n), y + ry * math.sin(2 * math.pi * i / n)) for i in range(n)], (x, y, rx, ry)


def room_state(k, hover):
    if k == CURRENT:
        return "current"
    if k in ("lock", "cw_mid"):
        return "walked"
    if k in OPT:
        return "option"
    if k == "server":
        return "target"
    return "reach"


# ---------------------------------------------------------------- the overlay (1920 x 1080 RGBA)
def draw_links(img, sc, hover):
    cab = S.Cables()
    P = sc.P

    def pts(names):
        return [P[n] for n in names if n in P]
    # walked (lime): the dock lock -> the causeway -> the arrival pod
    walk = pts(["lock", "cw_mid", "cw_pier", CURRENT])
    cab.solid(walk, S.LIME, 6, casing=3, glow=120)
    # next (orange): the two options
    for o in OPT:
        cab.solid(pts([CURRENT, o]), S.ORANGE, 6, casing=3, glow=140)
    # ahead (white dashed): the branch from each option to the target; under the water the lines run through the decks
    ahead1 = pts(["inner_0", "main_deck"])
    ahead2 = pts(["mid_0", "outer_1", "inner_1", "main_deck"])
    shaft = pts(["main_deck", "deck_1", "deck_2", "deck_3", "deck_4", "deck_5", "vent_cap", "server"])
    br = set(BRANCH_HOVER2) if hover == "mid_0" else (set(BRANCH_HOVER1) if hover == "inner_0" else set())
    for names, line in ((["inner_0", "main_deck"], ahead1), (["mid_0", "outer_1", "inner_1", "main_deck"], ahead2),
                        (["main_deck", "deck_1", "vent_cap", "server"], shaft)):
        lit = hover and all(n in br or n in ("main_deck",) for n in names[:2])
        cab.dashed(line, S.WHITE, 5 if lit else 4, on=18, off=11, casing=3, a=255 if (lit or not hover) else 150)
    return cab.comp(img, glow_col=S.ORANGE)


def draw_nodes(img, sc, hover):
    P = sc.P
    order = {"reach": 0, "walked": 1, "target": 2, "option": 3, "current": 4}
    names = ["lock", "cw_mid", CURRENT, "inner_0", "mid_0", "outer_1", "inner_1", "main_deck", "vent_cap", "deck_2", "deck_4"]
    br = set(BRANCH_HOVER2) if hover == "mid_0" else (set(BRANCH_HOVER1) if hover == "inner_0" else set())
    for k in sorted(names, key=lambda n: order[room_state(n, hover)]):
        if k not in P:
            continue
        st = room_state(k, hover)
        x, y = P[k]
        if not (-60 < x < W + 60 and -60 < y < H + 60):
            continue
        col = S.STATE_COL[st]
        poly, (ex, ey, rx, ry) = sc.ell(k)
        al = 0.8 if st == "reach" else 1.0
        if hover and st in ("reach", "option") and k not in br:
            al *= S.MIX_A
        kind = "start" if k == "lock" else KIND.get(k, "router")
        px = {"option": 50, "current": 46, "walked": 38, "reach": 40}.get(st, 40)
        small = k.startswith("deck_") or k in ("vent_cap", "cw_mid")
        if small:
            px = 30
        if k == "main_deck":
            px = 44
        if st in ("option", "current", "walked") and k not in ("lock", "cw_mid"):
            img = S.frame_poly(img, poly, col, 4 if st != "walked" else 3, al, glow=True)
        elif k in ("main_deck", "outer_1", "inner_1"):
            img = S.frame_poly(img, poly, col, 2, al * 0.9, glow=False)
        sx, sy = ex, ey + (rx * 0.05)
        if k == "lock":
            sx, sy = x, y
        if k == "cw_mid":
            sx, sy = x, y
        lift = 0.55 if (k == hover) else (0.25 if st == "option" else 0.0)
        alpha = 1.0 if not (hover and st in ("reach", "option") and k not in br) else S.MIX_A + 0.15
        img = S.sticker(img, kind, sx, sy - (4 if k == hover else 0), px, alpha=alpha, hover=lift)
        rc = col
        img = S.ring(img, sx, sy - (4 if k == hover else 0), px / 2 + 6, rc, 5 if st in ("option", "current") else 3, alpha)
        if st == "option":
            n = OPT.index(k) + 1
            img = S.number_chip(img, sx - px / 2 - 22, sy - px * 0.32, n, col=S.ORANGE)
    return img


def target_mark(img, sc):
    x, y = sc.P["server"]
    rx, ry = 40.0, 30.0
    word = (x - 190, y - 70)
    pr = S.target_pencil(x, y, rx, ry, word)
    img = S.finish_pencil(img, pr)
    img, _ = KT.chip(img, (x - rx - 12, y + 40), "CENTRAL SERVER // THE BLACK SMOKER", (255, 214, 64), 12, anchor="rm", pad=6) \
        if False else KT.chip(img, (x + rx + 12, y + 6), "CENTRAL SERVER // THE BLACK SMOKER", (255, 214, 64), 12, anchor="lm", pad=6)
    return img


def legend(img, cx=980):
    def ringf(col):
        def f(px):
            im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
            ImageDraw.Draw(im).ellipse([3, 3, px - 4, px - 4], outline=col + (255,), width=3)
            return im
        return f
    items = [(lambda px, k=k: U32.icon(k, px), lab) for k, lab in (("router", "FIGHT"), ("elite", "ELITE"),
                                                                   ("terminal", "EVENT"), ("modem", "SHOP"))]
    items += [(ringf(S.LIME), "walked"), (ringf(S.ORANGE), "next"), (ringf(S.WHITE), "ahead"), (ringf(S.GREY), "past")]
    img, box = KT.key_strip(img, int(cx - 640), 1030, items, hint="HOVER: SHOW ALL")
    return img


def view_toggle(img):
    box = (1612, 1030, 1904, 1070)
    img = KT.term(img, box, None, accent=K.CYAN, header=False, seed=35, chamfer=10)
    d = K.BD(img)
    f = K.F(K.MONO, 15)
    for k, (lab, a, b) in enumerate([("DECISION", 1622, 1736), ("OVERVIEW", 1740, 1854)]):
        if k == 0:
            d.rectangle((a, 1036, b, 1064), fill=(212, 255, 0, 235))
            K.text(img, ((a + b) / 2, 1050), lab, f, (12, 14, 6), "mm", 0)
        else:
            K.text(img, ((a + b) / 2, 1050), lab, f, (150, 190, 205), "mm", 0.4)
    K.text(img, (1880, 1050), "Z", K.F(K.MONO, 13), K.CYAN, "mm", 0.6)
    return img


def placeholder_panel(img):
    """The top-right mechanic panel: a neutral placeholder (the BALLAST TIDE is a proposal, not drawn as a rule)."""
    x, y = 1600, 10
    box = (x, y, x + 306, y + 150)
    img = KT.term(img, box, "CORP MECHANIC", accent=(170, 200, 205), seed=29)
    d = ImageDraw.Draw(img)
    for r in range(4):
        yy = y + 52 + r * 24
        d.line([(x + 22, yy), (x + 150, yy)], fill=(120, 140, 150, 255), width=2)
        d.ellipse([x + 160, yy - 7, x + 174, yy + 7], outline=(150, 175, 185, 255), width=2)
    K.text(img, (x + 196, y + 78), "placeholder", K.F(K.MONO, 13), (170, 200, 205), "lm", 0.3)
    K.text(img, (x + 196, y + 100), "not a rule", K.F(K.MONO, 13), (170, 200, 205), "lm", 0.3)
    return img


def sidebar(img, n_opts, hover):
    """The left column (sidekit.sidebar with Tethys wording; the dossier is the corp paper, patched to Tethys)."""
    R35.TYPEF, R35.TYPEB = K.COUR, K.COUR_B
    op = dict(R35.OPERATIVE)
    op["hp"] = "52 / 60"
    dz = R35.dossier(op=op, heat_stamp=None)
    dz = dz.resize((int(dz.width * 0.62), int(dz.height * 0.62)), Image.LANCZOS)
    img = RL.drop_shadow(img, dz, 16, 136, blur=14, off=(6, 12), op=0.55)
    box = (14, 476, S.SIDE_X1, 712)
    img = KT.term(img, box, "ROUTE", seed=23)
    f = K.F(K.MONO, 14)
    K.text(img, (30, 520), "PICK A ROOM: click a", f, (205, 218, 230), "lm", 0.3)
    K.text(img, (30, 538), "numbered room, then CONFIRM.", f, (205, 218, 230), "lm", 0.3)
    K.text(img, (30, 556), "Keys 1-%d go now." % n_opts, f, (205, 218, 230), "lm", 0.3)
    img = K.term_button(img, (30, 572, 274, 612), "CONFIRM", None, state="disabled")
    K.text(img, (268, 606), "pick first", K.F(K.MONO, 11), (130, 138, 156), "rm", 0.6)
    img = K.term_button(img, (30, 618, 274, 656), "GRID VIEW", None)
    K.text(img, (268, 650), "[G]", K.F(K.MONO, 11), K.CYAN, "rm", 0.6)
    img = K.term_button(img, (30, 662, 274, 700), "Save & quit", None)
    if hover:
        word = WORDS[KIND[hover]]
        rows = [("TIER", "T4"), ("TYPE", "Fight: a pump warden" if word == "FIGHT" else "Elite: a pressure sentinel"),
                ("REWARDS", "20-30 Cycles, a card"), ("", "maybe a Firmware chip"), ("sep", ""), ("HP", "41 / 60 on arrival", (140, 255, 170))]
        img = KT.holo_file(img, (14, 724, S.SIDE_X1 + 6, 986), "%s  //  L2" % word, rows, corp="tethys", seed=12, key_w=78, scale=0.8)
    return img


def overlay(base, sc, hover):
    """Everything above the world grade, drawn at 1920 x 1080 onto base (RGB)."""
    img = base.convert("RGBA")
    img = draw_links(img, sc, hover)
    img = draw_nodes(img, sc, hover)
    img = target_mark(img, sc)
    if hover:
        x, y = sc.P[hover]
        poly, (ex, ey, rx, ry) = sc.ell(hover)
        img, _ = KT.chip(img, (ex - rx * 0.6, ey - ry - 36), "%s  L2" % WORDS[KIND[hover]], S.ORANGE, 14, anchor="lm", pad=7)
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ui = S.chrome_top(ui, DISPATCH)
    ui = sidebar(ui, 2, hover)
    ui = placeholder_panel(ui)
    if hover:
        ui, _ = KT.chip(ui, (14, 996), "RING: the walkway to the next pier-end pod, then in along that pier",
                        (230, 236, 240), 13, anchor="lm", pad=8)
    ui = legend(ui)
    ui = view_toggle(ui)
    if hover:
        ex, ey = sc.ell(hover)[1][:2]
        ui = S.cursor(ui, ex + 6, ey + 2)
    img.alpha_composite(ui)
    return img


# ---------------------------------------------------------------- the hover grade (one 2D pass, spec 9.4)
def lum(a):
    return a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11


def branch_mask(sc, names, size):
    """room shapes grown 8 px, blurred 8 px (at the plate's size); decks are inside the lit well, never drawn as hull."""
    Wp, Hp = size
    k = Wp / W
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    for n in names:
        if n not in sc.P or n.startswith("deck_"):
            continue
        poly, _ = sc.ell(n, grow=1.12)
        d.polygon([(x * k, y * k) for x, y in poly], fill=255)
    # the moon pool well: a capsule from the collar down to the server (the glass drops of the deep stair)
    if "collar" in sc.P and "server" in sc.P:
        (x0, y0), (x1, y1) = sc.P["collar"], sc.P["server"]
        r = 4.8 * sc.u("server") * k
        d.line([(x0 * k, y0 * k), (x1 * k, y1 * k)], fill=255, width=int(2 * r))
        for (x, y) in ((x0, y0), (x1, y1)):
            d.ellipse([x * k - r, y * k - r, x * k + r, y * k + r], fill=255)
    m = m.filter(ImageFilter.MaxFilter(2 * int(8 * k) + 1)).filter(ImageFilter.GaussianBlur(8 * k))
    return np.asarray(m, np.float32) / 255.0


def grade(plate, sc, hover):
    """spec 9.4: outside the branch + the current room: x cut_level, desaturated cut_desat; the branch x branch_boost with
    a type-colour glow. One value for street and HQ; nothing else is darkened (no 3D cut, no extra link shading)."""
    out = np.asarray(plate.convert("RGB"), np.float32) / 255.0
    Wp, Hp = plate.size
    br = BRANCH_HOVER2 if hover == "mid_0" else BRANCH_HOVER1
    keep = branch_mask(sc, list(br) + [CURRENT], (Wp, Hp))[..., None]
    l3 = lum(out)[..., None]
    dim = (out * (1 - HOVER["cut_desat"]) + l3 * HOVER["cut_desat"]) * HOVER["cut_level"]
    lit = np.clip(out * HOVER["branch_boost"], 0, 1.0)
    g = lit * keep + dim * (1 - keep)
    img = Image.fromarray((np.clip(g, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    k = Wp / W
    for n in br:
        if n not in sc.P or n.startswith("deck_") or n in ("server", "vent_cap", "main_deck"):
            continue
        poly, _ = sc.ell(n)
        m = Image.new("L", (Wp, Hp), 0)
        ImageDraw.Draw(m).polygon([(x * k, y * k) for x, y in poly], fill=255)
        col = S.TYPE_COL[KIND.get(n, "router")]
        img = K.add_glow(img, m, col, int(30 * k), 0.5 * HOVER["type_glow"])
    return img


# ---------------------------------------------------------------- compose (the matte method)
def compose(plate, sc, hover):
    Wp, Hp = plate.size
    base = grade(plate, sc, hover) if hover else plate.convert("RGBA")

    def up(a):
        if a.shape[1] == Wp:
            return a
        return np.stack([np.asarray(Image.fromarray(a[..., c].astype(np.float32), "F").resize((Wp, Hp), Image.LANCZOS),
                                    np.float32) for c in range(3)], axis=-1)
    o0 = np.asarray(overlay(Image.new("RGB", (W, H), (0, 0, 0)), sc, hover).convert("RGB"), np.float32) / 255.0
    o1 = np.asarray(overlay(Image.new("RGB", (W, H), (int(255 * FLAT),) * 3), sc, hover).convert("RGB"), np.float32) / 255.0
    M = np.clip(up(np.clip((o1 - o0) / FLAT, 0, 1)), 0, 1)
    B = np.clip(up(o0), 0, 1)
    P = np.asarray(base.convert("RGB"), np.float32) / 255.0
    return Image.fromarray((np.clip(P * M + B, 0, 1) * 255 + 0.5).astype(np.uint8))


if __name__ == "__main__":
    mode, plate_p, rooms_p, out_p = sys.argv[1:5]
    plate = Image.open(plate_p).convert("RGB")
    sc = Scene(rooms_p)
    hv = "mid_0" if mode == "hover" else None
    compose(plate, sc, hv).save(out_p)
    print("saved", out_p)
