"""Cohesion redo 1: hq_idle.png and hq_node_selected.png on the r42 city.

python build_hq.py [idle|selected|strengths] [--grade light|mid|strong]

Reuses hq44.py (copied unchanged beside this file) for every piece of chrome: HUD strip, work order, polaroids, tabs,
holo Site file, JACK IN, toast, pencils, markers. Replaced: the plate (r42 backdrop + Aff map), the grade, the links
(PIL lines), the TARGET (the Solace helix is the Central Server, in frame), and the Site file (Solace lime #96FF46).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ["NET36"] = "net_scope.json"
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import r42lib as R  # noqa: E402
import kit44 as KT  # noqa: E402
import ui31 as K  # noqa: E402
import hq44 as H  # noqa: E402
import markers42 as M  # noqa: E402
import r31lib as RL  # noqa: E402
import post40 as P  # noqa: E402

SOLACE = (150, 255, 70)                                  # ART_BIBLE 2.4 lime #96FF46
K.CORP["solace"] = SOLACE
CAM = R.Aff(822, 268, (17.1, 8.36), (-17.1, 8.36))
GRADE = "mid"
_holo_orig = KT.holo_file


def _col(a):
    return tuple(int(round(float(v) * 255)) for v in a)


# ---- Solace crest on the corporate Site disc (the old disc drew Meridian's crane)
_disc_orig = M.disc


def disc_solace(kind, px, exploit=None, status="corporate"):
    if kind != "site":
        return _disc_orig(kind, px, exploit, status)
    S = 4
    Pp = px * S
    im = Image.new("RGBA", (Pp, Pp), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([S, S, Pp - S, Pp - S], fill=(14, 28, 14, 255), outline=(10, 9, 12, 255), width=2 * S)
    em = Image.open(os.path.join(R.OUT, "scratch", "emblems", "solace.png")).convert("RGBA").split()[3]
    g = int(Pp * 0.62)
    em = em.resize((g, g), Image.LANCZOS)
    cr = Image.new("RGBA", (g, g), SOLACE + (255,))
    cr.putalpha(em)
    im.alpha_composite(cr, ((Pp - g) // 2, (Pp - g) // 2))
    im = im.resize((px, px), Image.LANCZOS)
    if status == "cleared":
        a = im.split()[3]
        from PIL import ImageEnhance
        im = ImageEnhance.Brightness(im.convert("L").convert("RGB")).enhance(0.8).convert("RGBA")
        im.putalpha(a)
    return im


M.disc = disc_solace


def prj(cam, lot):
    return cam.prj(lot)


H.prj = prj
CAM.special[(round(float(H.NET["hq"]["solace"][0]), 3), round(float(H.NET["hq"]["solace"][1]), 3))] = (1700.0, 300.0)


def draw_links(img):
    shown = H.shown_ids()
    for l in H.NET["links"]:
        if l["a"] not in shown or l["b"] not in shown:
            continue
        st = l["state"]
        if st == "owned":
            R.link(img, CAM, l["pts"], _col(P.LINK_COL["owned"]), width=4.5, k=1.0)
        elif st == "border":
            sel = H.SELECTED in (l["a"], l["b"])
            R.link(img, CAM, l["pts"], _col(P.LINK_COL["border"]), width=4.0 if sel else 3.0, k=1.0 if sel else 0.6, dash=(15, 9))
        elif st == "grey":
            R.link(img, CAM, l["pts"], _col(P.LINK_COL["grey"]), width=3.0, k=0.5)
    return img


def grade_and_links(img, net_mask, lit_mask=None):
    g = R.grade(img, net_mask, lit_mask, GRADE)
    return draw_links(g)


KT.grade_map = grade_and_links


def plate():
    return R.backdrop().convert("RGBA"), CAM


H.plate = plate


def target_helix(img, cam):
    """The Solace Central Server is the helix, in frame: the red pencil circle round it + TARGET + the exploit chip."""
    pen = KT.pencil(KT.PEN_R, 441)
    pen.circle(1700, 268, 112, 168, width=9)
    pen.text("TARGET", 1404, 150, 40, angle=-6)
    img, _ = KT.chip(img, (1500, 520), "CENTRAL SERVER  //  EXPLOITS 1/3", K.GOLD, 14, anchor="lm")
    return img, pen


H.target_edge = target_helix


def site_holo_for(title, rows, sub, file_no):
    def extra(im, y):
        K.text(im, (1486, y + 6), "IF CLEARED", KT.F(K.MONO, 14), K.CYAN, "lm", 1.4)
        row = RL.outcome_row([("schem", "+12", True), ("heat", "+3", False), ("none", "OPENS 2", True)], size=17, gap=8)
        im.alpha_composite(row, (1486, int(y + 22)))
        return im

    def f(img):
        return _holo_orig(img, (1466, 586, 1902, 872), title, rows + [("sep",)], corp="solace", sub=sub, extra=extra, seed=file_no)
    return f


def build(mode, grade="mid"):
    global GRADE
    GRADE = grade
    H.SELECTED = "m2_d" if mode == "idle" else "sink_the_cargo_logs"
    base, cam = plate()
    nb = H.net_box(cam)
    netm = R.soft_rect(nb, blur=80)
    fx, fy = prj(cam, H.NODES[H.SELECTED]["lot"])
    lit = R.soft_ellipse(fx, fy - 10, 250, 170, blur=70)
    img = grade_and_links(base, netm, lit)
    img = H.markers(img, cam)
    img = K.over(img, (3, 2, 8), KT.soft_l((0, 0, 1920, 96), blur=24), 0.35)
    img = K.over(img, (3, 2, 8), KT.soft_l((0, 830, 900, 1080), blur=40), 0.3)
    img, tpen = target_helix(img, cam)
    name = "SEED VAULT EXCHANGE" if mode == "idle" else "BURN TRIAL LOGS"
    img = H.name_tag(img, cam, H.SELECTED, name, SOLACE)
    img = H.work_order_panel(img)
    img = H.topbar_full(img)
    img = H.tabs(img, "CREW")
    img, anchors = H.crew(img, runner=(mode == "idle"))
    if mode == "idle":
        img = site_holo_for("T2  //  SEED VAULT EXCHANGE",
                            [("TYPE", "Seed exchange  //  router run"), ("REWARDS", "+12 Schematics, firmware"),
                             ("LINK", "from CULTURE INTAKE")], "SOLACE BIOSYSTEMS  //  SITE FILE 207", 9)(img)
        sd = KT.rainbow_sweep(KT.sticker("JACK IN", 84, "pink", seed=31), pos=0.56, k=0.55)
        img = KT.place_sticker(img, sd, 1712, 968, angle=-3, spill_col=K.PINK, spill_k=0.3)
        K.text(img, (1902, 1062), "> jack --to SEED_VAULT  [SPACE]", KT.F(K.MONO, 13), (120, 170, 190), "ra", 0.6, alpha=150)
        img = H.toast(img, "INTERCEPTED // SOLACE: culture-lane audit moved up a shift")
        sx, sy = prj(cam, H.NODES[H.SELECTED]["lot"])
        ppen = KT.pencil(KT.PEN_Y, 442)
        ppen.circle(sx, sy - 18, 46, 34, width=9)
        dx_, dy_ = prj(cam, H.NODES["m1_d"]["lot"])
        ppen.arrow([(dx_ + 14, dy_ - 46), (dx_ + 96, dy_ - 120), (sx - 30, sy + 26)], width=9, head=24)
        img = KT.spill(img, ppen.mask.resize((1920, 1080)), KT.PEN_Y, 0.12, 30)
        img = KT.ink(img, ppen)
    else:
        img = site_holo_for("T3  //  BURN THE TRIAL LOGS",
                            [("TYPE", "Heat objective  //  elite run"), ("REWARDS", "-10 Heat, +30 Schematics"),
                             ("LINK", "from GROWTH PLANNER")], "SOLACE BIOSYSTEMS  //  SITE FILE 311", 14)(img)
        sd = KT.rainbow_sweep(KT.sticker("JACK IN", 84, "pink", seed=31), pos=0.56, k=0.55)
        img = KT.place_sticker(img, sd, 1712, 968, angle=-3, spill_col=K.PINK, spill_k=0.3)
        K.text(img, (1902, 1062), "> jack --to BURN_TRIAL_LOGS  [SPACE]", KT.F(K.MONO, 13), (120, 170, 190), "ra", 0.6, alpha=150)
        cx, cy = prj(cam, H.NODES[H.SELECTED]["lot"])
        img = K.focus_brackets(img, (cx - 34, cy - 58, cx + 34, cy + 16), gap=6, ln=12, w=3)
        img = KT.cursor(img, cx + 16, cy - 10)
    img = KT.spill(img, tpen.mask.resize((1920, 1080)), KT.PEN_R, 0.14, 30)
    img = KT.ink(img, tpen)
    return RL.bloom(img, 0.10, 0.84, 8)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    g = "mid"
    if "--grade" in args:
        g = args[args.index("--grade") + 1]
    which = [a for a in args if a in ("idle", "selected", "strengths")] or ["idle", "selected"]
    if "strengths" in which:
        for s in R.GRADES:
            im = build("idle", s)
            im.convert("RGB").save(os.path.join(R.OUT, "scratch", "hq_idle_%s.png" % s))
            print("saved", s)
    if "idle" in which:
        build("idle", g).convert("RGB").save(os.path.join(R.OUT, "hq_idle.png"), optimize=True)
        print("saved hq_idle", g)
    if "selected" in which:
        build("selected", g).convert("RGB").save(os.path.join(R.OUT, "hq_node_selected.png"), optimize=True)
        print("saved hq_node_selected", g)
