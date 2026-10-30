"""Round 44 A: raid setup at text scale 1.6 (REVIEW D5, D17, f "Raid setup", Q9, Q10).

SOLID40=1 NET36=net_scope.json python raid44.py  -> raid_setup.png
Plate: r_raid (run39.py r39), the same camera and SOLID40 finish as the locked round40 raid_view_v3.
- the yellow RAID SETUP title sticker is back (Q10);
- no node text tags: status on the node (frame colour / fill), forecast = the dashed outer ring in the outcome colour;
- only the shown raid's entries are drawn (Q4); non-entry Sites are hidden;
- the map legend collapses to the key strip;
- right column: THREAT INTEL (holo: corp tint, scanlines, bands, RGB edge, cracked seal + DECRYPTED) with YOUR NETWORK
  (terminal) stacked under it (Q9), START DEFENSE under them, Speed/Skip under START (locked); nothing covers the map
  network or the pencil;
- left column: the title and the one paper document (the intercepted work order).
"""
import os
import sys

os.environ.setdefault("NET36", "net_scope.json")
os.environ.setdefault("SOLID40", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import kit44 as KT  # noqa: E402
import ui31 as K  # noqa: E402
import post40 as P  # noqa: E402
import layout36 as L  # noqa: E402
import screens39 as S39  # noqa: E402
import ui19 as U  # noqa: E402
import ui20 as V  # noqa: E402
import icons22 as IC  # noqa: E402
import r31lib as RL  # noqa: E402
import sticker_lib19 as SL19  # noqa: E402

TS = 1.6                                    # Settings text scale
NET, NODES = P.NET, P.NODES
STATE = S39.RAID_STATE                      # m1_d disabled; m1_f and m2_virus damaged (holds)
FORECAST = {"m2_virus": P.GREEN, "core": P.PINK, "m1_d": np.array([1.0, 0.69, 0.0], np.float32)}


def prj(cam, lot):
    return L.project(cam, *L.W(lot), 0.0, 1920, 1080)


def plate(routes):
    entries = {r["start"] for r in routes}

    def deco(net):
        for l in NET["links"]:
            if l["state"] == "owned":
                dead = STATE.get(l["a"], ("", 1))[0] == "disabled" or STATE.get(l["b"], ("", 1))[0] == "disabled"
                net.link(l["pts"], P.LINK_COL["owned"], k=0.45 if dead else 1.2, packets=not dead)
        for n in NET["nodes"]:
            if n["state"] in ("owned", "core"):
                st, hp = STATE.get(n["id"], ("holds", 1.0))
                if st == "disabled":
                    net.node(dict(n, state="grey"))
                else:
                    net.node(n, exposed=n["state"] == "core")
                    if hp < 1:
                        net.health(n, hp)
            elif n["id"] in entries:
                net.node(n, scale=0.8)
        for nid, col in FORECAST.items():
            net.forecast(NODES[nid], col)
    hx, hy = L.W(NODES["core"]["lot"])
    img, cam = P.finish("r_raid", decorate=deco, pools=[(hx + 1, hy - 1, 12.0, 0.8)], t=0.2)
    return KT.f2p(img), cam


def densify(pts, step=22.0):
    out = [pts[0]]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(1, int(((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5 / step))
        out += [(ax + (bx - ax) * k / n, ay + (by - ay) * k / n) for k in range(1, n + 1)]
    return out


def pencil_routes(img, cam, routes):
    pen = KT.pencil(KT.PEN_R, 3901)
    for i, r in enumerate(routes):
        pts = densify([prj(cam, p) for p in r["pts"]])
        pen.arrow(pts, width=7, head=22)
        ex, ey = pts[0]
        if 0 < ey < 1080:
            pen.circle(ex, ey, 44, 29, width=7)
            pen.text("ABC"[i], ex + (-62 if ex > 960 else 62), ey - 42, 38)
    return pen


def convoy(img, cam, routes):
    for i, r in enumerate(routes):
        x, y = prj(cam, r["pts"][0])
        if y < 20:                                        # the entry is above the frame: the convoy waits at the edge
            x, y = prj(cam, r["pts"][min(3, len(r["pts"]) - 1)])
        for j, (ui, hp) in enumerate(((1, 1.0), (0, 0.7))):
            ic = IC.unit_icon("MERIDIAN", ui, up=(i == 0 and j == 0), size=40, hp=hp, statuses=(("SLOWED",) if i == 1 and j == 1 else ()))
            img.alpha_composite(ic, (int(x - ic.width / 2 + (j - 0.5) * 36), int(y - ic.height / 2 - 36)))
    return img


def work_order(img):
    rows = [("TARGET", "CORE (CELL)"), ("UNITS", "6 IN 1 WAVE", (170, 30, 25)), ("ENTRY SITES", "3"), ("IF RUN NOW", "HOME 50 > 41")]
    p = KT.work_order(rows, w=228, seed=52, scale=TS, title="MANIFEST AUDIT", sub="WO 52-MF-207")
    return K.paste_paper(img, p, (14, 150), angle=-1.2, sh=0.6)


def threat_intel(img):
    x0, y0, x1 = 1488, 18, 1904
    s = TS

    def extra(im, y):
        f, fs = KT.F(K.MONO, int(14 * s)), KT.F(K.MONO, int(11 * s))
        for letter, who, rule in (("A", "HAULER + COURIER", "> VAULT"), ("B", "HAULER + COURIER", "> CORE (home)"),
                                  ("C", "HAULER + COURIER", "> weakest node")):
            d = K.BD(im)
            d.ellipse([x0 + 18, y - 13, x0 + 18 + 26 * s * 0.85, y - 13 + 26 * s * 0.85], outline=K.HARM + (255,), width=3)
            K.text(im, (x0 + 18 + 13 * s * 0.85, y - 13 + 13 * s * 0.85), letter, KT.F(K.ANTON, int(15 * s)), K.HARM, "mm", 0)
            K.text(im, (x0 + 66, y - 2), who, f, (255, 236, 214), "lm", 0.6)
            K.text(im, (x0 + 66, y + 20), rule, fs, (255, 200, 150), "lm", 0.6)
            y += 50 * s * 0.8
        # scanned silhouettes (the corp's own units, scanlined in the corp tint)
        xs = x0 + 24
        for unit in ("HAULER", "COURIER"):
            sp, _, _ = S39.mer_sprite(unit, 2)
            sp = sp.resize((int(sp.width * 0.9), int(sp.height * 0.9)), Image.LANCZOS)
            a = np.asarray(sp, np.float32)
            lum = a[..., :3].mean(axis=2, keepdims=True)
            a[..., :3] = np.clip(lum / 255 * 1.5, 0, 1) * np.array(K.CORP["meridian"], np.float32)
            a[::3, :, 3] *= 0.4
            sp = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
            im.alpha_composite(sp, (int(xs), int(y - 14)))
            K.text(im, (xs + 8, y + sp.height - 14), unit, fs, K.CORP["meridian"], "la", 0.6)
            xs += 120
        return im
    rows = [("THREATS", "6  //  +52% (HEAT)")]
    return KT.holo_file(img, (x0, y0, x1, 486), "THREAT INTEL  //  SCAN", rows, sub="MERIDIAN FREIGHT  //  YARD SECURITY NET",
                        seed=7, scale=s * 0.82, key_w=118, extra=extra)


def your_network(img):
    x0, y0, x1, y1 = 1488, 504, 1904, 846
    img = KT.term(img, (x0, y0, x1, y1), "YOUR NETWORK", tag="9 NODES", seed=19)
    s = TS * 0.82
    rows = [("core", "CORE (home)", "HOME 50", K.PINK, 1.0), ("firewall", "RETURNS PROC.", "DISABLED", K.AMBER, 0.0),
            ("vault", "ROUTING MIRROR", "HOLDS", K.GREEN, 0.7), ("safehouse", "SHIFT PLANNER", "HOLDS", K.GREEN, 0.35)]
    y = y0 + 58
    f, fs = KT.F(K.MONO, int(16 * s)), KT.F(K.MONO, int(12 * s))
    for kind, name, chip, col, hp in rows:
        img = K.paste_glyph(img, S39.KIND_GLYPH[kind], (x0 + 30, y + 8), int(24 * s), col)
        K.text(img, (x0 + 56, y), name, f, (210, 232, 244), "lm", 0.6)
        K.text(img, (x0 + 56, y + 22), "INT %d%%" % int(hp * 100), fs, K.DIM, "lm", 0.6)
        cw = KT.F(K.MONO, int(14 * s)).getlength(chip) + 18
        d = K.BD(img)
        d.rectangle([x1 - 18 - cw, y - 12, x1 - 18, y + 14], outline=col + (230,), width=2)
        K.text(img, (x1 - 18 - cw / 2, y + 1), chip, KT.F(K.MONO, int(14 * s)), col, "mm", 0.4)
        y += 58
    K.text(img, (x0 + 18, y1 - 22), "v  5 MORE  (scroll)", KT.F(K.MONO, int(14 * s)), K.CYAN, "lm", 1.0)
    return img


def speed_strip(img):
    x0, y0, x1, y1 = 1488, 986, 1904, 1060
    img = KT.term(img, (x0, y0, x1, y1), None, header=False, seed=29, chamfer=10)
    x = x0 + 12
    for lab, w in (("1x", 58), ("2x", 58), ("4x", 58), ("SKIP", 88)):
        st = "pressed" if lab == "2x" else "idle"
        img = K.term_button(img, (x, y0 + 12, x + w, y1 - 12), lab, None, state=st)
        x += w + 8
    K.text(img, (x + 4, (y0 + y1) / 2), "-- / 30", KT.F(K.MONO, int(15 * TS * 0.82)), K.DIM, "lm", 0.8)
    return img


def tray(img):
    x = 560
    for i, (nm, gl, hp, cp, ds, col) in enumerate(U.TRAY):
        sd = U.asset_card(nm, gl, hp, cp, ds, col, 50 + i)
        img = SL19.place(img, sd, x, 990, angle=[-2, 1.5, -1, 2, -1.5, 1][i], scale=1.04)
        x += 166
    return img


def key_strip(img):
    s = TS * 0.75
    x0, y0, x1, y1 = 14, 948, 470, 1062
    img = KT.term(img, (x0, y0, x1, y1), "MAP KEY  [K]", seed=31, chamfer=10)
    f = KT.F(K.MONO, int(14 * s))
    items = [(K.GREEN, "holds"), (K.AMBER, "disabled"), (K.PINK, "home")]
    x = x0 + 16
    y = y0 + 58
    d = K.BD(img)
    for col, lab in items:
        d.rectangle([x, y - 9, x + 18, y + 9], outline=col + (255,), width=3)
        K.text(img, (x + 26, y), lab, f, (215, 225, 232), "lm", 0.4)
        x += 36 + f.getlength(lab)
    d = K.BD(img)
    for k in range(6):                                        # forecast = dashed outer ring
        a0 = k * 60
        d.arc([x, y - 12, x + 24, y + 12], a0, a0 + 34, fill=K.GREEN + (255,), width=3)
    K.text(img, (x + 32, y), "forecast", f, (215, 225, 232), "lm", 0.4)
    K.text(img, (x0 + 16, y + 30), "red pencil = threat route  |  HOVER: ALL", KT.F(K.MONO, int(13 * s)), K.CYAN, "lm", 0.4)
    return img


def build():
    routes = S39.raid_routes()
    base, cam = plate(routes)
    img = base
    # the world steps back under the side columns (dark bands, bible 3.1 / 4.1)
    img = K.over(img, (3, 2, 8), KT.soft_l((1470, 0, 1920, 1080), blur=40), 0.35)
    img = K.over(img, (3, 2, 8), KT.soft_l((0, 0, 400, 1080), blur=40), 0.3)
    img = convoy(img, cam, routes)
    pen = pencil_routes(img, cam, routes)
    img = work_order(img)
    sd = KT.sticker("RAID SETUP", 50, "yellow", seed=11)
    img = KT.place_sticker(img, sd, 196, 74, angle=-1.5)
    img = threat_intel(img)
    img = your_network(img)
    img = tray(img)
    img = key_strip(img)
    sd = KT.rainbow_sweep(KT.sticker("START DEFENSE", 52, "pink", seed=21), pos=0.5, k=0.5)
    img = KT.place_sticker(img, sd, 1696, 914, angle=-2, spill_col=K.PINK, spill_k=0.28)
    img = speed_strip(img)
    img = KT.spill(img, pen.mask.resize((1920, 1080)), KT.PEN_R, 0.14, 30)
    img = KT.ink(img, pen)
    return RL.bloom(img, 0.10, 0.84, 8)


if __name__ == "__main__":
    KT.save(build(), "raid_setup.png")
