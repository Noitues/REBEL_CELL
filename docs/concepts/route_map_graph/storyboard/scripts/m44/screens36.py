"""Round 36 deliverables: city_grid.png, raid_management.png, run_transit.png, three_views.png, zoom_through.gif.

python screens36.py [city raid transit three gif contact]
Inputs: ../scratch/bl (run36.py stills / zoom), ../scratch/layout (layout36.py).
UI kit: round 35 (r35ui dossier / info window / heat / tier badges, r32ui node stickers + chips, r31lib), ui19 terminals.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout36 as L  # noqa: E402
import post36 as P  # noqa: E402
import r31lib as RL  # noqa: E402
import r32ui as U32  # noqa: E402
import r35ui as R  # noqa: E402
import ui19 as U19  # noqa: E402

OUT = os.path.dirname(HERE)
W, H = 1920, 1080
NET = P.NET
NODES = P.NODES
SCOL = {"owned": (212, 255, 0), "core": (255, 61, 168), "available": (255, 140, 26), "white": (236, 234, 244), "grey": (118, 114, 128)}
CORPC = {"meridian": (255, 140, 26), "solace": (61, 255, 139), "halcyon": (150, 120, 255), "orbital": (120, 220, 255), "rebel_cell": (255, 40, 50)}
CORPN = {"meridian": "MERIDIAN", "solace": "SOLACE", "halcyon": "HALCYON", "orbital": "ORBITAL", "rebel_cell": "REBEL_CELL"}
HQ_TOP = {"meridian": 26, "solace": 96, "halcyon": 48, "orbital": 40, "rebel_cell": 58}
PIN_H = 34.0


def to_rgba(img):
    return Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")


def prj(cam, p_lots, z=0.0, w=W, h=H):
    x, y = L.W(p_lots)
    return L.project(cam, x, y, z, w, h)


def prj_w(cam, x, y, z=0.0, w=W, h=H):
    return L.project(cam, x, y, z, w, h)


def save(img, name):
    img.convert("RGB").save(os.path.join(OUT, name), optimize=True)
    print("saved", name, flush=True)


def tag(canvas, x, y, text, col, size=30, a=1.0):
    """The city map's district / HQ tag (round 30 v6): a dark tag with a slanted corp-colour bar."""
    f = RL.font(RL.BAHN, size)
    tw = f.getlength(text)
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0 = x - tw / 2 - 18, y - size * 0.75
    d.rectangle([x0, y0, x0 + tw + 30, y0 + size * 1.5], fill=(10, 10, 14, int(225 * a)))
    d.polygon([(x0 + 2, y0 + size * 1.5), (x0 + 9, y0), (x0 + 15, y0), (x0 + 8, y0 + size * 1.5)], fill=col + (int(255 * a),))
    d.text((x0 + 22, y0 + size * 0.75), text, font=f, fill=col + (int(255 * a),) if col != (236, 234, 244) else (240, 240, 245, int(255 * a)), anchor="lm")
    canvas.alpha_composite(lay)
    return canvas


def network_deco(raid=False, run=None, t=0.0, exposed=()):
    def deco(net):
        P.network(net, raid=raid, exposed=exposed)
        if run:
            for (p, col, gl, dashed) in run:
                net.runnode(p, P.C(*[c / 255 for c in col]), gl, dashed=dashed)
    return deco


def pins(canvas, cam, lod, sel=None):
    """City zoom: every node raises a pin above the roofs (a billboard: thin light line + tier badge / Cell icon).
    It fades out between lod 1.8 and 1.3 (on the way into a district the pin retracts into the socket)."""
    a = min(1.0, max(0.0, (lod - 1.3) / 0.5))
    if a <= 0:
        return canvas
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    w, h = canvas.size
    tops = {}
    for n in NET["nodes"]:
        x0, y0 = prj(cam, n["lot"], 0, w, h)
        x1, y1 = prj(cam, n["lot"], PIN_H, w, h)
        col = SCOL[n["state"]]
        d.line([(x0, y0), (x1, y1)], fill=col + (int(170 * a),), width=2)
        d.ellipse([x0 - 4, y0 - 2, x0 + 4, y0 + 2], fill=col + (int(220 * a),))
        tops[n["id"]] = (x1, y1)
    canvas.alpha_composite(lay)
    for n in sorted(NET["nodes"], key=lambda n: tops[n["id"]][1]):
        x, y = tops[n["id"]]
        col = SCOL[n["state"]]
        if n["state"] == "core":
            import route_d_city as RC
            ic = RC.cell_icon("relay", int(26 * (w / W) / 0.9), (255, 61, 168))
            ic.putalpha(ic.split()[3].point(lambda v: int(v * a)))
            canvas.alpha_composite(ic, (int(x - ic.width / 2), int(y - ic.height / 2)))
            continue
        if a < 1:
            sub = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            sub = R.tier_badge(sub, x, y, n["tier"] or 1, col, key=n["kind"] == "key", size=int(15 * w / W) or 8)
            sub.putalpha(sub.split()[3].point(lambda v: int(v * a)))
            canvas.alpha_composite(sub)
        else:
            canvas = R.tier_badge(canvas, x, y, n["tier"] or 1, col, key=n["kind"] == "key", size=int(15 * w / W) or 8)
    if sel:
        x, y = tops[sel]
        lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            cx_, cy_ = x + sx * 24, y + sy * 20
            d.line([(cx_, cy_), (cx_ - sx * 10, cy_)], fill=(255, 230, 0, 255), width=3)
            d.line([(cx_, cy_), (cx_, cy_ - sy * 10)], fill=(255, 230, 0, 255), width=3)
        canvas.alpha_composite(lay)
    return canvas


def hq_tags(canvas, cam, lod, size=30):
    a = min(1.0, max(0.0, (lod - 1.25) / 0.5))
    if a <= 0:
        return canvas
    w, h = canvas.size
    for corp, c in NET["hq"].items():
        x, y = prj(cam, c, HQ_TOP[corp], w, h)
        canvas = tag(canvas, x, y - 20 * w / W, CORPN[corp], CORPC[corp], int(size * w / W), a)
    x, y = prj(cam, NET["cell_base"], 0, w, h)
    canvas = tag(canvas, x - 330 * w / W, y + 60 * w / W, "REBEL_CELL", CORPC["rebel_cell"], int(size * w / W), a)
    for p in ((-40, 22), (24, -24)):
        x, y = prj(cam, p, 30, w, h)
        canvas = tag(canvas, x, y, "THE SPRAWL", (236, 234, 244), int(size * 0.8 * w / W), a)
    return canvas


def heat_pools(cam_name):
    """Heat B (round 35, locked H1 language): searchlights on the Cell's border, in world terms (pools)."""
    pts = [NODES[k]["lot"] for k in ("a7", "a10") if k in NODES] + [NODES["core"]["lot"]]
    out = []
    for i, p in enumerate(pts):
        x, y = L.W((p[0] + 1.5 * math.sin(i * 2.1), p[1] + 1.5 * math.cos(i * 1.7)))
        out.append((x, y, 9.0 if cam_name != "city" else 16.0, 0.9))
    return out


def cones(canvas, cam, pools, k=0.8):
    w, h = canvas.size
    beams = []
    for i, (x, y, r, _) in enumerate(pools):
        tx, ty = prj_w(cam, x, y, 0, w, h)
        sx, sy = prj_w(cam, x + 18 * math.cos(i * 2.4 + 0.6), y + 18 * math.sin(i * 2.4 + 0.6), 70, w, h)
        rr = r * w / cam["ortho"] * 1.1
        beams.append((sx, sy, tx, ty, rr))
    return R.heat_diegetic(canvas.convert("RGBA"), beams, [], k=k).convert("RGBA")


# ------------------------------------------------------------------ 1. city grid
SEL = "a8"


def city_grid():
    pools = heat_pools("city")
    img, cam = P.finish("city", decorate=network_deco(), pools=pools)
    cv = to_rgba(img)
    cv = cones(cv, cam, pools, 0.7)
    lod = P.lod_of(cam["ortho"])
    cv = hq_tags(cv, cam, lod)
    cv = pins(cv, cam, lod, sel=SEL)
    cv = RL.place_sticker(cv, RL.sticker_word(["THE GRID"], 64, fills=["yellow"], seed=61), 170, 62, angle=-3)
    cv = R.heat_strip(cv, (720, 18), 52, "HUNTED", w=480)
    n = NODES[SEL]
    cv = R.node_info(cv, (1480, 780, 1898, 990), "DEPOT 15", "T%d" % n["tier"], ["+9 Schematics, Firmware", "1 armory asset"], "Logistics depot")
    x, y = prj(cam, n["lot"], PIN_H)
    lay = Image.new("RGBA", cv.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).line([(x + 26, y), (1480, 820)], fill=(255, 140, 26, 160), width=2)
    cv.alpha_composite(lay)
    cv = U32.term_button(cv, (1640, 1000, 1898, 1066), "JACK IN", "[ENTER]")
    leg = RL.CRT(1080, 46, (92, 225, 255), None, header=False, seed=36)
    xx = 16
    for lab, col in (("owned", SCOL["owned"]), ("available", SCOL["available"]), ("not yet", SCOL["white"]), ("already run", SCOL["grey"]),
                     ("Cell CORE", SCOL["core"])):
        leg.d.polygon([(xx, 23), (xx + 10, 15), (xx + 20, 23), (xx + 10, 31)], fill=col + (255,))
        leg.text((xx + 28, 23), lab, 15, (220, 236, 245), anchor="lm")
        xx += 30 + RL.f_mono(15).getlength(lab) + 26
    leg.text((xx + 4, 23), "|  WHEEL: zoom in > raid > netrun", 15, (150, 190, 205), anchor="lm")
    cv = RL.paste(cv, leg.finish(scan=0.15), 24, 1016)
    return cv, cam


# ------------------------------------------------------------------ 2. raid management
def raid_management():
    pools = [heat_pools("raid")[2]]
    img, cam = P.finish("raid", decorate=network_deco(raid=True, exposed=("core",)), pools=pools)
    cv = to_rgba(img)
    cv = cones(cv, cam, pools, 0.6)
    cv = RL.place_sticker(cv, RL.sticker_word(["CELL DEFENSE"], 54, fills=["yellow"], seed=62), 220, 58, angle=-2)
    rows = []
    for n in NET["nodes"]:
        if n["state"] not in ("owned", "core"):
            continue
        nm = {"core": "CORE (home)", "relay": "RELAY", "firewall": "FIREWALL RELAY", "vault": "VAULT TERMINAL", "proxy": "PROXY RELAY",
              "safehouse": "SAFEHOUSE"}[n["kind"]]
        rows.append(("kv", nm, "HOLDS" if n["state"] == "owned" else "50/50", U19.GREEN if n["state"] == "owned" else U19.PINK))
    cv = to_rgba(U19.put_panel(np.asarray(cv.convert("RGB"), np.float32) / 255, U19.terminal("YOUR NODES  //  IF IT RAN NOW", rows, w=340), 22, 120))
    rr = [("big", "COMPLIANCE SWEEP", (230, 240, 255)), ("t", "HALCYON CIVIC  //  HEAT 52 RAID", U19.HALCYON), ("sep",),
          ("kv", "ENTRY SITES", "1", (190, 225, 240)), ("kv", "WAVES", "1", (190, 225, 240)), ("kv", "SPOTLIT", "CORE (exposed)", (255, 255, 255))]
    cv = to_rgba(U19.put_panel(np.asarray(cv.convert("RGB"), np.float32) / 255, U19.terminal("RAID INCOMING", rr, w=330, accent=U19.HARM), 1568, 110))
    # the incoming Halcyon units wait at the route's entry (v4 icons, locked round 22)
    import icons22 as IC
    r = P.route()
    pts = r["pts"]
    p = pts[0]
    fine = [(a[0] + (b[0] - a[0]) * k / 20, a[1] + (b[1] - a[1]) * k / 20) for a, b in zip(pts, pts[1:]) for k in range(20)]
    for q in fine:                                  # the first route point inside the frame: the convoy's front
        qx, qy = prj(cam, q, 0)
        if 380 < qx < 1540 and 180 < qy < 860:
            p = q
            break
    for i in range(3):
        x, y = prj(cam, (p[0] + 0.0, p[1] + 0.9 * i - 0.9), 0)
        ic = IC.unit_icon("HALCYON", [1, 0, 2][i], up=i == 0, size=34)
        cv.alpha_composite(ic, (int(x - ic.width / 2), int(y - ic.height / 2)))
    cvf = np.asarray(cv.convert("RGB"), np.float32) / 255
    x0 = 600
    for i, (nm, gl, hp, cp, ds, col) in enumerate(U19.TRAY):
        sd = U19.asset_card(nm, gl, hp, cp, ds, col, 50 + i)
        cvf = U19.place(cvf, sd, x0 + i * 150, 990, angle=[-2, 1.5, -1, 2, -1.5, 1][i], scale=0.86)
    sd = U19.word_sticker(["START DEFENSE"], 40, [U19.FILL_PINK], seed=21, border=13)
    cvf = U19.place(cvf, sd, 1700, 1010, angle=-2)
    return to_rgba(cvf), cam


# ------------------------------------------------------------------ 3. run transit
def run_plan():
    """The run's map nodes on the chosen link's streets (start = owned node, final = the Site)."""
    lk = NET["transit"]["link"]
    l = next(l for l in NET["links"] if [l["a"], l["b"]] == lk)
    pts = l["pts"]
    seg = [(a, b, math.hypot(b[0] - a[0], b[1] - a[1])) for a, b in zip(pts, pts[1:])]
    total = sum(s[2] for s in seg)

    def at(t):
        d = t * total
        for a, b, Ls in seg:
            if d <= Ls:
                u = d / Ls
                return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u), ((b[0] - a[0]) / Ls, (b[1] - a[1]) / Ls)
            d -= Ls
        return pts[-1], (0, 0)
    kinds = ["router", "terminal", "elite", "router", "modem", "rack"]
    out = []
    n = len(kinds)
    for i, k in enumerate(kinds):
        p, dv = at((i + 1) / (n + 1))
        out.append(dict(p=p, kind=k, side=False))
        if i in (1, 3):                    # branches: a node one lot off the line (the run's choices)
            q = (p[0] - dv[1] * 1.6, p[1] + dv[0] * 1.6)
            out.append(dict(p=q, kind="router" if i == 1 else "elite", side=True))
    return l, out


RUN_STATE = {0: "walked", 1: "walked", 2: "current", 3: "option", 4: "option"}


def run_transit():
    l, plan = run_plan()
    st = []
    for i, nd in enumerate(plan):
        s = RUN_STATE.get(i, "white")
        st.append(s)
    cols = {"walked": (212, 255, 0), "current": (212, 255, 0), "option": (255, 140, 26), "white": (236, 234, 244)}
    gl = {"router": "slice_exploit", "elite": "slice_zero_day", "terminal": "picto_draw", "modem": "picto_ram", "rack": "placeholder_vault"}
    run = [(nd["p"], cols[s], gl[nd["kind"]], s == "white") for nd, s in zip(plan, st)]
    pools = [heat_pools("transit")[0]]
    img, cam = P.finish("transit", decorate=network_deco(run=run), pools=pools)
    cv = to_rgba(img)
    cv = cones(cv, cam, pools, 0.5)
    for (nd, s) in sorted(zip(plan, st), key=lambda t: prj(cam, t[0]["p"])[1]):
        x, y = prj(cam, nd["p"], 0)
        px = {"walked": 50, "current": 56, "option": 64, "white": 52}[s]
        sd = U32.node_sd(nd["kind"], px, grey=False) if s != "white" else RL.greyscale(U32.node_sd(nd["kind"], px), 0.85)
        cv = RL.place_sticker(cv, sd, x, y - 34, angle=((len(nd["kind"]) % 5) - 2) * 1.5, hover=0.35 if s == "option" else 0.0,
                              opacity=0.8 if s == "white" else 1.0)
    cur = plan[2]["p"]
    x, y = prj(cam, cur, 0)
    cv = RL.place_sticker(cv, U32.token_sd(54), x + 30, y - 82, angle=-14, hover=0.6)
    fx, fy = prj(cam, NODES[l["b"]]["lot"], 0)
    pr = RL.pen(RL.GP_RED, seed=361)
    pr.circle(fx, fy - 20, 86, 64, width=9)
    pr.text("DEPOT 15", fx + 120, fy + 64, 30, angle=-4)
    cv = RL.ink(cv, pr)
    sx, sy = prj(cam, NODES[l["a"]]["lot"], 0)
    cv = U32.chip(cv, (sx - 90, sy + 40), "RELAY 4", (212, 255, 0), 14, bright=True)
    cv = RL.place_sticker(cv, RL.sticker_word(["NETRUN"], 64, fills=["yellow"], seed=63), 170, 62, angle=-3)
    dz = R.dossier(heat_stamp="HEAT 52: WATCH LIST")
    dz = dz.resize((int(dz.width * 0.8), int(dz.height * 0.8)), Image.LANCZOS)
    cv = RL.drop_shadow(cv, dz, 22, 116, blur=14, off=(8, 12), op=0.6)
    cv = R.node_info(cv, (1480, 820, 1898, 1030), "DEPOT 15", "T1", ["+9 Schematics, Firmware", "1 armory asset"], "Logistics depot")
    cv = U32.term_button(cv, (24, 980, 230, 1050), "DECK", "[D]")
    cv = U32.term_button(cv, (242, 980, 448, 1050), "MENU", "[ESC]")
    return cv, cam


# ------------------------------------------------------------------ 4. three views + zoom
CALL = [("A", "NODE  RELAY 4", (255, 222, 30)), ("B", "LINK  RELAY 4 > DEPOT 15", (92, 225, 255)), ("C", "BUILDING  its uplink pad", (255, 120, 200))]


def callout_points(cam, w, h):
    """The same node / link / building in any camera (world -> screen)."""
    lk = NET["transit"]["link"]
    l = next(l for l in NET["links"] if [l["a"], l["b"]] == lk)
    a = NODES[lk[0]]
    pts = l["pts"]
    mid = pts[len(pts) // 2]
    sc = json.load(open(os.path.join(P.SRC, "city_scene.json")))
    nb = sc["node_bld"].get(lk[0])
    bx, by, bz = (nb["centre"][0], nb["centre"][1], nb["top"]) if nb else (*L.W(a["lot"]), 10.0)
    return {"A": prj(cam, a["lot"], 0, w, h), "B": prj(cam, mid, 0, w, h), "C": prj_w(cam, bx, by, bz, w, h)}


def mark(canvas, pts, big=True):
    d = ImageDraw.Draw(canvas)
    w = canvas.size[0]
    r = 22 if big else 14
    for key, nm, col in CALL:
        x, y = pts[key]
        if not (-40 < x < w + 40 and -40 < y < canvas.size[1] + 40):
            continue
        d.ellipse([x - r, y - r, x + r, y + r], outline=col + (255,), width=3)
        bx, by = x + r + 6, y - r - 18
        d.rectangle([bx, by, bx + (26 if big else 18), by + (24 if big else 18)], fill=col + (255,))
        d.text((bx + (13 if big else 9), by + (12 if big else 9)), key, font=RL.font(RL.ANTON, 20 if big else 14), fill=(14, 12, 20, 255), anchor="mm")
    return canvas


def three_views():
    cv = Image.new("RGBA", (W, H), (8, 7, 14, 255))
    cv = RL.place_sticker(cv, RL.sticker_word(["ONE CITY"], 52, fills=["yellow"], seed=64), 150, 54, angle=-3)
    d = ImageDraw.Draw(cv)
    d.text((300, 40), "the REAL city (the game's layout: every building, street, lane colour, HQ) is the one model; city grid, raid and",
           font=RL.f_mono(17), fill=(92, 225, 255, 255))
    d.text((300, 64), "netrun transit are ONE orthographic camera on it - only the target and the zoom change. Same building, node, link:",
           font=RL.f_mono(17), fill=(92, 225, 255, 255))
    shots = [("city_grid.png", "city", "CITY GRID   ortho 820"), ("raid_management.png", "raid", "RAID   ortho 176"),
             ("run_transit.png", "transit", "NETRUN TRANSIT   ortho 88")]
    tw, th = 616, 347
    for i, (fn, tagn, lab) in enumerate(shots):
        x = 16 + i * (tw + 8)
        im = Image.open(os.path.join(OUT, fn)).convert("RGBA")
        cam = json.load(open(os.path.join(P.SRC, tagn + "_scene.json")))["cam"]
        im = mark(im, callout_points(cam, W, H))
        cv.alpha_composite(im.resize((tw, th), Image.LANCZOS), (x, 104))
        d.text((x, 462), lab, font=RL.font(RL.ANTON, 26), fill=(235, 240, 250, 255))
    # the same block, enlarged from each render (no UI): the building C and node A at each zoom
    for i, (fn, tagn, lab) in enumerate(shots):
        x = 16 + i * (tw + 8)
        img, cam = P.finish(tagn, decorate=network_deco(), rain=False)
        pts = callout_points(cam, W, H)
        cx, cy = (pts["A"][0] + pts["C"][0]) / 2, (pts["A"][1] + pts["C"][1]) / 2
        half = {"city": 70, "raid": 190, "transit": 300}[tagn]
        hw = half * 16 / 9
        cx = min(max(cx, hw), W - hw)
        cy = min(max(cy, half), H - half)
        box = (int(cx - hw), int(cy - half), int(cx + hw), int(cy + half))
        im = mark(to_rgba(img), pts, big=tagn != "city")
        im = im.crop(box).resize((tw, th), Image.LANCZOS)
        cv.alpha_composite(im, (x, 510))
        d.text((x, 864), "the same block, enlarged x%.1f" % (W / (box[2] - box[0])), font=RL.f_mono(14), fill=(150, 165, 185, 255))
    y = 900
    rows = [("A", "NODE", "city: a pin + tier badge over a filled socket   >   raid: the circuit-inlay socket (frame, pins, integrity track, glyph)   >   transit: the run's start"),
            ("B", "LINK", "city: one bright trace (x-ray through buildings)   >   raid: the 3-trace bus with vias + packets   >   transit: the run's nodes ride it"),
            ("C", "BUILDING", "the game's own extrusion everywhere: city = mass + roof trim + window dots; raid = facets, ledges, signs, uplink pad; transit = shopfronts, awnings, pipes")]
    for key, nm, txt in rows:
        col = dict((k, c) for k, _, c in CALL)[key]
        d.rectangle([16, y, 40, y + 22], fill=col + (255,))
        d.text((28, y + 11), key, font=RL.font(RL.ANTON, 18), fill=(14, 12, 20, 255), anchor="mm")
        d.text((52, y + 11), nm, font=RL.font(RL.ANTON, 20), fill=col + (255,), anchor="lm")
        d.text((170, y + 11), txt, font=RL.f_mono(15), fill=(210, 220, 232, 255), anchor="lm")
        y += 34
    d.text((16, 1046), "Zoom continuously between them: zoom_through.gif (one camera, no cut).", font=RL.f_mono(15), fill=(255, 222, 30, 255))
    return cv


GSZ = (640, 360)


def zoom_gif():
    frames, durs = [], []
    n = len([f for f in os.listdir(P.SRC) if f.startswith("z") and f.endswith("_scene.json")])
    keep = [i for i in range(n) if i >= 14 or i % 2 == 0]       # the dense city-zoom frames at half rate (gif budget)
    for i in keep:
        tg = "z%02d" % i
        cam = json.load(open(os.path.join(P.SRC, tg + "_scene.json")))["cam"]
        lod = P.lod_of(cam["ortho"])
        run = None
        if lod < 0.6:
            _, plan = run_plan()
            k = (0.6 - lod) / 0.6
            run = [(nd["p"], (int(212 * k + 236 * (1 - k)), int(255 * k + 234 * (1 - k)), int(244 * (1 - k))), "slice_exploit", False) for nd in plan]
        img, cam = P.finish(tg, decorate=network_deco(raid=0.6 < lod < 1.5, run=run), out_size=(960, 540), rain=False, seed=i)
        cv = to_rgba(img)
        cv = hq_tags(cv, cam, lod, size=34)
        cv = pins(cv, cam, lod)
        d = ImageDraw.Draw(cv)
        stage = "CITY GRID" if lod > 1.6 else "RAID" if lod > 0.55 else "NETRUN TRANSIT"
        d.rectangle([10, 10, 330, 40], fill=(5, 13, 28, 230))
        d.text((20, 25), "%s   ortho %d" % (stage, cam["ortho"]), font=RL.f_mono(16), fill=(92, 225, 255, 255), anchor="lm")
        frames.append(cv.convert("RGB").resize(GSZ, Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.35)))
        durs.append(240 if i < 14 else 120)
        print("zoom", i, flush=True)
    durs[0] = durs[len(durs) // 2] = durs[-1] = 1300
    return save_gif(frames, durs, "zoom_through.gif")


def save_gif(frames, durs, name, colors=255):
    n = len(frames)
    step = max(1, n // 12)
    sub = [frames[i].resize((frames[0].size[0] // 2, frames[0].size[1] // 2)) for i in range(0, n, step)]
    probe = Image.new("RGB", (sub[0].size[0], sub[0].size[1] * len(sub)))
    for k, sb in enumerate(sub):
        probe.paste(sb, (0, k * sub[0].size[1]))
    base = probe.quantize(colors=120, method=Image.Quantize.MEDIANCUT).getpalette()[:120 * 3]
    extra = []
    for c in list(SCOL.values()) + list(CORPC.values()) + [(92, 225, 255), (255, 222, 30)]:
        for k in (1.0, 0.7, 0.45):
            extra += [int(v * k) for v in c]
    palv = (base + extra)[:768]
    palv += [0] * (768 - len(palv))
    pal = Image.new("P", (1, 1))
    pal.putpalette(palv)
    q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    path = os.path.join(OUT, name)
    q[0].save(path, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=True, disposal=1)
    print("saved %s %.2f MB (%d frames)" % (name, os.path.getsize(path) / 1e6, n), flush=True)


def contact():
    from PIL import ImageSequence
    names = ["city_grid.png", "raid_management.png", "run_transit.png", "three_views.png", "zoom_through.gif"]
    tw, th = 600, 338
    sheet = Image.new("RGB", (3 * tw + 40, 2 * (th + 24) + 80), (10, 9, 16))
    d = ImageDraw.Draw(sheet)
    d.text((14, 16), "ROUND 36  ONE CITY: GRID, RAID AND NETRUN FROM THE REAL CITY MODEL", font=RL.font(RL.ANTON, 30), fill=(255, 222, 30))
    for i, nme in enumerate(names):
        im = Image.open(os.path.join(OUT, nme))
        if nme.endswith(".gif"):
            fr = [f.convert("RGB") for f in ImageSequence.Iterator(im)]
            im = fr[len(fr) // 4]
        im = im.convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = 10 + (i % 3) * (tw + 10), 70 + (i // 3) * (th + 24)
        sheet.paste(im, (x, y))
        d.text((x + 4, y + th + 2), nme, font=RL.f_mono(15), fill=(92, 225, 255))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=86)
    print("saved contact_sheet.jpg")


if __name__ == "__main__":
    which0 = sys.argv[1:]
    if "three" in which0:
        save(three_views(), "three_views.png")
    if "gif" in which0:
        zoom_gif()
    if "contact" in which0:
        contact()
    which = sys.argv[1:] or ["city", "raid", "transit"]
    if "city" in which:
        save(city_grid()[0], "city_grid.png")
    if "raid" in which:
        save(raid_management()[0], "raid_management.png")
    if "transit" in which:
        save(run_transit()[0], "run_transit.png")
