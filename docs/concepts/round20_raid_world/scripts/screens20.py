"""Round 20 raid world: every deliverable sheet / gif.

python screens20.py [name ...]   names: buildings operators opgif vehicles toggle heatgif lost lostgif summary contact
Inputs: ../scratch/bl (run_blender20.py + vehicles20.py), ../scratch/emblems (emblems20.py).
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
import layout as LY  # noqa: E402
import finish19 as FN  # noqa: E402
import netdecal19 as ND  # noqa: E402
import ui19 as U  # noqa: E402
import screens19 as S19  # noqa: E402  (canvas, paste, crop, label, title, setup_decor)
import roof20 as RF  # noqa: E402

OUT = os.path.dirname(HERE)
SL = U.SL
W, H = LY.W, LY.H
BG = S19.BG
canvas, paste, crop, label, title = S19.canvas, S19.paste, S19.crop, S19.label, S19.title
NODE_KEYS = ("relay", "firewall", "vault", "proxy", "safe")
TXT = (200, 210, 225)
DIM = (150, 165, 185)


def save(img, name):
    Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(os.path.join(OUT, name), optimize=True)
    print("saved", name, flush=True)


def to_pil(img):
    return Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))


def to_f(im):
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


def wrap(cv, x, y, text, width_chars, size=14, col=TXT, lh=None):
    lh = lh or int(size * 1.45)
    line = ""
    for wd in text.split(" "):
        if len(line) + len(wd) > width_chars:
            cv = label(cv, x, y, line.rstrip(), size, col)
            line, y = "", y + lh
        line += wd + " "
    if line.strip():
        cv = label(cv, x, y, line.rstrip(), size, col)
        y += lh
    return cv, y


def P(x, y, z=0.0, cam=None, w=W, h=H):
    keep = dict(LY.CAM)
    if cam:
        LY.CAM.update({k: (tuple(v) if isinstance(v, list) else v) for k, v in cam.items()})
    p = LY.project(x, y, z, w, h)
    LY.CAM.update(keep)
    return p[0], p[1]


def scene_cam(tag):
    return json.load(open(os.path.join(FN.SRC, tag + "_scene.json")))["cam"]


def world_decor(variant, slot="empty", cls=None, t=0.0, boosts=(), shares=(), extra=None, **kw):
    """setup network + round 20 roof decals on every node building."""
    base = S19.setup_decor(**kw)

    def deco(net):
        base(net)
        for key in NODE_KEYS:
            RF.roof(net, key, variant, slot=(slot if (key == "safe" and variant == "B") else None), cls=cls, t=t)
        for key, c in boosts:
            RF.boost(net, key, c, "own", t)
        for a, b, c in shares:
            RF.share_link(net, a, b, c, t)
            RF.boost(net, b, c, "shared", t)
        if extra:
            extra(net)
    return deco


# ------------------------------------------------------------------ 1. building nodes v2
ROOF_TXT = {
    "A": ("A  CROWN INLAY", "The riser climbs the -x facade and spills onto the roof as a circuit: lime neon parapet, corner pins, a "
                            "double inlay ring and the node glyph in the middle. Loudest at map zoom; on 6 nodes it gets busy."),
    "B": ("B  UPLINK PAD", "A raised pad on the roof is the street socket's twin (frame, pins, notch, glyph) with a beacon at its "
                           "corner. Calm, reads as 'ours' at any zoom, and on a Safehouse the pad IS the operative's station slot."),
    "C": ("C  MAST + LIT HATCH", "A lattice uplink mast with a lime beacon and an open roof hatch throwing a light shaft. Best "
                                "silhouette, but it reads as 'antenna', not as 'node', and the shaft fights the heat spotlights."),
}


def building_nodes_v2():
    cv = canvas()
    cv = title(cv, "NODE BUILDINGS V2", "THE ROOF MARKS THE NODE: 3 ROOFTOP INDICATIONS x FIREWALL RELAY / VAULT TERMINAL / SAFEHOUSE  //  "
                                        "RISERS KEPT AND NOW CLIMB TO THE ROOF")
    for i, v in enumerate("ABC"):
        x = 40 + i * 620
        pre = "e_" if v == "B" else ""
        tiles = [("%s_fw" % v, (x, 140), (600, 520)), ("%s_vault" % v, (x, 668), (296, 256)), ("%s_safe" % v, (x + 304, 668), (296, 256))]
        for tag, (tx, ty), size in tiles:
            img = FN.finish(tag, "night", decorate=world_decor(v), prefix=pre, seed=1, tilt=0.0, rain=False)
            cv = paste(cv, img, tx, ty, size)
        cv = label(cv, x + 8, 146, "FIREWALL RELAY", 13, (235, 240, 250))
        cv = label(cv, x + 8, 674, "VAULT TERMINAL", 11, (235, 240, 250))
        cv = label(cv, x + 312, 674, "SAFEHOUSE", 11, (235, 240, 250))
        nm, desc = ROOF_TXT[v]
        cv = label(cv, x, 936, nm, 24, U.LIME if v == "B" else (235, 240, 250), font=SL.ANTON)
        cv, _ = wrap(cv, x, 984, desc, 78, 13, TXT)
    L = U.pencil_layer(2001)
    U.pen_circle(L, 660 + 100, 953, 118, 26, U.Y_PEN, 5.5, 1.15)
    U.pen_text(L, "RECOMMENDED", 660 + 360, 950, 24, U.Y_PEN, 4.6)
    cv = U.pencil_composite(cv, L)
    return cv


# ------------------------------------------------------------------ 2. stationed operatives
CLASSES = ["breaker", "wrecker", "ghost", "phantom", "rigger", "overclocker", "botnet", "hivemind"]
BONUS = {"breaker": "node assets +50% dmg", "ghost": "entering threats -1 step", "rigger": "+integrity after each wave",
         "botnet": "1 free asset per raid", "wrecker": "alt of Breaker (tbd)", "phantom": "alt of Ghost (tbd)",
         "overclocker": "alt of Rigger (tbd)", "hivemind": "alt of Botnet (tbd)"}


def op_card(cls, rank=2, seed=7, gloss_k=0.22):
    """Roster card of an operative (a vinyl sticker: a static UI object), class colour strip + emblem."""
    col = RF.CLASS_RGB[cls]

    def fn(p):
        p.rect(8, 10, 112, 92, (30, 28, 42), r=8)
        p.glyph(os.path.join(RF.EMBLEMS, cls + ".png"), 60, 51, 64, col)
        p.text(10, 98, cls.upper(), SL.ANTON, 20, U.PAPER)
        p.text(10, 128, "RANK %d" % rank, SL.MONO, 12, col)
        p.text(110, 128, "STATION", SL.MONO, 10, (150, 146, 170), "ra")
        p.text(10, 146, BONUS[cls], SL.PLEX, 11, (190, 186, 205))
        p.rect(0, 0, 119, 5, col, r=2)
    return U.card_sticker(120, 166, fn, seed=seed, gloss_k=gloss_k)


def add_glow(img, lay, k=1.0, blur=6):
    """Additive light layer (float HxWx3) + its bloom."""
    b = np.asarray(to_pil(lay).filter(ImageFilter.GaussianBlur(blur)), np.float32) / 255.0
    return np.clip(img + lay * k + b * k * 0.9, 0, 1)


def beacon_layer(shape, x, y, top, col, w=16, k=1.0, emblem_cls=None, esize=46, ey=None):
    """R3 / recall: a class-colour light column rising from the pad (x, y) to `top`; optional emblem holo on top."""
    h, wd = shape[:2]
    lay = np.zeros((h, wd, 3), np.float32)
    yy, xx = np.mgrid[0:h, 0:wd].astype(np.float32)
    span = np.clip((y - yy) / max(1.0, (y - top)), 0, 1)
    core = np.exp(-((xx - x) / (w * (0.6 + 0.4 * span))) ** 2) * (yy < y) * (yy > top) * (1 - span) ** 0.6
    c = np.array(col, np.float32) / 255.0
    lay += core[..., None] * c * k
    if emblem_cls:
        ga = np.asarray(Image.open(os.path.join(RF.EMBLEMS, emblem_cls + ".png")).split()[3].resize((esize, esize), Image.LANCZOS), np.float32) / 255.0
        ga = ga * (np.arange(esize) % 3 != 0)[:, None]
        m = np.zeros((h, wd), np.float32)
        x0, y0 = int(x - esize / 2), int((top - esize / 2 - 6 if ey is None else ey) - esize / 2)
        if 0 <= x0 and x0 + esize <= wd and 0 <= y0 and y0 + esize <= h:
            m[y0:y0 + esize, x0:x0 + esize] = ga
        hexr = Image.new("L", (wd, h), 0)
        ImageDraw.Draw(hexr).regular_polygon((x, y0 + esize / 2, esize * 0.72), 6, rotation=30, outline=255, width=3)
        m = np.maximum(m, np.asarray(hexr, np.float32) / 255.0 * 0.9)
        lay += m[..., None] * c * 1.3
    return lay


def pad_screen(tag, w, h):
    s = LY.roof_spec("safe", "B")
    px, py, hs = s["pad"]
    return P(px, py, s["top"] + s["pad_h"], cam=scene_cam(tag), w=w, h=h)


def op_frame(tag, state, cls="breaker", t=0.0, share=False, rep="R1"):
    """One finished frame of the station flow. state: empty / hover / stationed / recall; rep R1 figure / R2 emblem / R3 beacon."""
    fig = state == "stationed" and rep == "R1"
    slot = {"empty": "empty", "hover": "hover", "stationed": "emblem" if rep == "R2" else "stationed", "recall": "recall"}[state]
    boosts = [("safe", cls)] if state == "stationed" else []
    shares = [("safe", "core", cls)] if (state == "stationed" and share) else []
    img = FN.finish(tag, "night", decorate=world_decor("B", slot=slot, cls=cls, t=t, boosts=boosts, shares=shares),
                    prefix="" if fig else "e_", seed=1, tilt=0.0, rain=False, fog=0.0)
    if state == "stationed" and rep == "R3":
        px, py = pad_screen(tag, img.shape[1], img.shape[0])
        img = add_glow(img, beacon_layer(img.shape, px, py - 4, 0, RF.CLASS_RGB[cls], w=22, k=0.8, emblem_cls=cls, esize=110, ey=max(70, py - 160)), 1.0, 12)
    return img


def operators():
    cv = canvas()
    cv = title(cv, "STATIONED OPERATIVES", "GDD 3.2 / 5.4: A SAFEHOUSE HAS ONE STATION SLOT = ITS ROOFTOP PAD (B). THE BONUS IS SHARED WITH "
                                           "ADJACENT NODES. RECALL ANY TIME BETWEEN RUNS")
    for i, c in enumerate(CLASSES):                    # class chips: emblem, colour, station bonus (GDD 5.2)
        x, y = 1050 + (i % 4) * 212, 14 + (i // 4) * 42
        g = Image.open(os.path.join(RF.EMBLEMS, c + ".png")).split()[3].resize((30, 30), Image.LANCZOS)
        im = to_pil(cv)
        im.paste(Image.new("RGB", (30, 30), RF.CLASS_RGB[c]), (x, y), g)
        cv = to_f(im)
        cv = label(cv, x + 38, y, c.upper(), 13, RF.CLASS_RGB[c])
        cv = label(cv, x + 38, y + 17, BONUS[c], 10, DIM)
    st = [("1  EMPTY SLOT", "B_opsafe", "empty", False, "dashed ring + '+' on the pad: an open slot (dashed = available)"),
          ("2  DRAG-HOVER, VALID", "B_opsafe", "hover", False, "drop target = the whole pad: it lights white and floods with the class colour"),
          ("3  STATIONED", "B_opsafe", "stationed", False, "figure on the pad + class ring; class brackets + emblem chip on its street socket"),
          ("4  ADJACENCY SHARE", "B_opadj", "stationed", True, "class chevrons run down the link to the neighbour (CORE): dashed brackets, hollow chip"),
          ("5  RECALL", "B_opsafe", "recall", False, "beam up in the class colour, the ring unwinds, the card flies back to the roster")]
    tw, th = 352, 305
    for i, (nm, tag, state, share, desc) in enumerate(st):
        x = 40 + i * 368
        img = op_frame(tag, state, t=0.35 if state != "recall" else 0.55, share=share)
        if state == "recall":
            px, py = pad_screen(tag, img.shape[1], img.shape[0])
            img = add_glow(img, beacon_layer(img.shape, px, py - 6, 0, RF.CLASS_RGB["breaker"], w=26, k=0.9), 1.0, 10)
        if tag == "B_opadj":
            img = crop(img, (470, 228, 1430, 1060))
        cv = paste(cv, img, x, 140, (tw, th))
        if state == "hover":
            cv = U.place(cv, op_card("breaker", seed=11), x + 262, 140 + 214, angle=-8, scale=0.62, hover=0.8)
        if state == "recall":
            cv = U.place(cv, op_card("breaker", seed=11), x + 300, 140 + 248, angle=6, scale=0.5, hover=0.3, opacity=0.85)
        cv = label(cv, x, 456, nm, 19, (235, 240, 250), font=SL.ANTON)
        cv, _ = wrap(cv, x, 486, desc, 50, 12, TXT, lh=16)
    L = U.pencil_layer(2002)
    U.pen_arrow(L, [(408 + 222, 140 + 186), (408 + 188, 140 + 128), (408 + 150, 140 + 70)], U.Y_PEN, 5.0, 16)
    U.pen_arrow(L, [(1512 + 150, 140 + 60), (1512 + 228, 140 + 148), (1512 + 258, 140 + 192)], U.Y_PEN, 4.0, 14, dashed=True)
    cv = U.pencil_composite(cv, L)
    reps = [("R1  ROOFTOP FIGURE", "R1", "A low-poly operative stands on the pad: class-colour visor, coat seam and foot ring. Reads as a "
                                       "person even small and gives the city a human scale. A two-pose idle (look around / kneel) is enough."),
            ("R2  EMBLEM DECAL", "R2", "No figure: the class emblem is painted into the pad decal in the class colour. Cheapest and clean "
                                     "at map zoom, but static; it reads like a node type, not a person."),
            ("R3  CLASS BEACON", "R3", "A class-colour light column from the pad, the emblem as a holo hexagon on top. Loudest at map "
                                     "zoom, but it competes with the heat spotlights and chopper beams.")]
    for i, (nm, rep, desc) in enumerate(reps):
        x = 40 + i * 620
        img = op_frame("B_opsafe", "stationed", t=0.2, rep=rep)
        cv = paste(cv, crop(img, (0, 0, 1200, 780)), x, 548, (600, 390))
        cv = label(cv, x, 954, nm, 22, U.LIME if rep == "R1" else (235, 240, 250), font=SL.ANTON)
        cv, _ = wrap(cv, x, 996, desc, 96, 12, TXT, lh=17)
    L = U.pencil_layer(2003)
    U.pen_circle(L, 40 + 112, 967, 126, 22, U.Y_PEN, 5.0, 1.15)
    U.pen_text(L, "RECOMMENDED", 40 + 390, 966, 22, U.Y_PEN, 4.4)
    cv = U.pencil_composite(cv, L)
    return cv


def save_gif(frames, name, durations, colors=200, max_mb=3.0):
    """Shared palette from a few frames, no dither (flat cel colours), optimised."""
    probe = Image.new("RGB", (frames[0].size[0], frames[0].size[1] * 3))
    for k, i in enumerate((0, len(frames) // 2, len(frames) - 1)):
        probe.paste(frames[i], (0, frames[0].size[1] * k))
    pal = probe.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    path = os.path.join(OUT, name)
    q[0].save(path, save_all=True, append_images=q[1:], duration=durations, loop=0, optimize=True, disposal=1)
    mb = os.path.getsize(path) / 1e6
    print("saved %s %.2f MB (%d frames)" % (name, mb, len(frames)), flush=True)
    return mb


def operator_gif():
    tag = "B_opadj"
    box = (420, 290, 1540, 920)
    GW, GH = 960, 540
    k = GW / (box[2] - box[0])
    px, py = pad_screen(tag, 1920, 1080)
    pad = ((px - box[0]) * k, (py - box[1]) * k)
    tray = [(78, 470), (168, 474)]
    col = RF.CLASS_RGB["breaker"]
    cards = [op_card("breaker", seed=11), op_card("ghost", rank=1, seed=12)]

    def base(state, t, share=False, fig=None):
        fig = (state == "stationed") if fig is None else fig
        slot = {"empty": "empty", "hover": "hover", "stationed": "stationed", "recall": "recall"}[state]
        boosts = [("safe", "breaker")] if state == "stationed" else []
        shares = [("safe", "core", "breaker")] if share else []
        img = FN.finish(tag, "night", decorate=world_decor("B", slot=slot, cls="breaker", t=t, boosts=boosts, shares=shares),
                        prefix="" if fig else "e_", seed=1, tilt=0.0, rain=False, fog=0.0)
        return np.asarray(to_pil(img).crop(box).resize((GW, GH), Image.LANCZOS), np.float32) / 255.0

    def caption(img, head, line, accent=U.CYAN):
        return U.put_panel(img, U.terminal(head, [("t", line, (190, 225, 240))], w=440), 14, 12)

    def tray_cards(img, skip_first=False):
        img = U.put_panel(img, U.terminal("ROSTER  //  RESERVES", [("t", "", (0, 0, 0))], w=250), 18, 382)
        for i, (sd, (x, y)) in enumerate(zip(cards, tray)):
            if i == 0 and skip_first:
                continue
            img = U.place(img, sd, x, y, angle=[-3, 2][i], scale=0.55)
        return img

    frames, durs = [], []

    def push(img, d=90):
        frames.append(to_pil(img))
        durs.append(d)
    # 1 empty slot
    for f in range(6):
        img = tray_cards(base("empty", f / 6))
        push(caption(img, "STATION SLOT  //  SAFEHOUSE", "open slot: drag an operative onto the rooftop pad"), 110)
    # 2 drag: card lifts from the tray and travels to the pad; the pad answers once the card is over it
    path = [tray[0], (300, 300), (pad[0] - 40, pad[1] + 60), pad]
    for f in range(10):
        u = (f + 1) / 10
        a, b, c, d = [np.array(p, float) for p in path]
        p = (1 - u) ** 3 * a + 3 * (1 - u) ** 2 * u * b + 3 * (1 - u) * u * u * c + u ** 3 * d
        over = u > 0.72
        img = tray_cards(base("hover" if over else "empty", f / 10), skip_first=True)
        img = U.place(img, cards[0], p[0] + 26, p[1] + 34, angle=-8 + 6 * u, scale=0.55 - 0.18 * u, hover=0.9)
        cur = to_pil(img)
        ImageDraw.Draw(cur).polygon([(p[0], p[1]), (p[0] + 4, p[1] + 20), (p[0] + 9, p[1] + 14), (p[0] + 18, p[1] + 13)], fill=(246, 243, 236), outline=(14, 12, 20))
        img = to_f(cur)
        push(caption(img, "DRAG  BREAKER", "valid target: the pad lights white, floods pink" if over else "drop target: any Safehouse pad"), 90)
    # 3 drop: a flash column, the figure resolves in
    empty_h, full = base("hover", 0.9), base("stationed", 0.0)
    for f in range(4):
        u = (f + 1) / 4
        img = empty_h * (1 - u) + full * u
        img = tray_cards(img, skip_first=True)
        img = add_glow(img, beacon_layer(img.shape, pad[0], pad[1] - 2, 0, (255, 255, 255) if f < 2 else col, w=18 * (1.2 - u), k=1.0 - 0.5 * u), 1.0, 8)
        push(caption(img, "STATIONED", "BREAKER on the Safehouse"), 80)
    # 4 stationed + adjacency share running down the link to CORE
    for f in range(14):
        img = tray_cards(base("stationed", f / 14, share=f >= 3), skip_first=True)
        line = "Safehouse assets +50% dmg" if f < 3 else "shared with adjacent CORE: assets +50% dmg"
        push(caption(img, "BREAKER  //  NODE ASSETS +50% DMG", line, accent=col), 100)
    # 5 recall: beam up, the figure fades out, the card flies home
    for f in range(9):
        u = (f + 1) / 9
        fig_img = base("stationed", 0.0)
        rec = base("recall", u)
        img = fig_img * max(0.0, 1 - u * 2.2) + rec * min(1.0, u * 2.2)
        img = add_glow(img, beacon_layer(img.shape, pad[0], pad[1] - 2, 0, col, w=20, k=1.0 * (1 - u * 0.6)), 1.0, 8)
        img = tray_cards(img, skip_first=True)
        q = np.array(pad) * (1 - u) + np.array(tray[0]) * u
        img = U.place(img, cards[0], q[0], q[1] - 40 * math.sin(u * math.pi), angle=-3, scale=0.3 + 0.25 * u, hover=0.6 * (1 - u))
        push(caption(img, "RECALL", "back to the reserves, unharmed; the slot is open again"), 90)
    for f in range(3):
        img = tray_cards(base("empty", f / 3))
        push(caption(img, "STATION SLOT  //  SAFEHOUSE", "open slot: drag an operative onto the rooftop pad"), 140)
    return save_gif(frames, "operator_drop.gif", durs, colors=200)


# ------------------------------------------------------------------ 3. threat vehicles v2 + icons + toggle
import icons20 as IC  # noqa: E402


def paste_rgba(img, ic, cx, cy):
    im = to_pil(img).convert("RGBA")
    im.alpha_composite(ic, (int(cx - ic.size[0] / 2), int(cy - ic.size[1] / 2)))
    return to_f(im)


def vehicle_matrix_img():
    src = FN.SRC
    beauty = FN.load(os.path.join(src, "veh_beauty.png"))
    glow = FN.load(os.path.join(src, "veh_glow.png"))
    ids = FN.load(os.path.join(src, "veh_id.png"))
    nrm = FN.load(os.path.join(src, "veh_normal.png"))
    ink = np.maximum(FN.F0.diff_edges(ids, 0.03), FN.F0.diff_edges(nrm, 0.42))
    ink = FN.F0.blur(FN.F0.maxf(FN.F0.warp(ink, 5, 1.0), 3), 0.6) * 0.85
    emis = np.clip(glow.max(axis=2) * 2, 0, 1)
    img = beauty * (1 - ink[..., None] * (1 - emis[..., None])) + np.array([0.04, 0.03, 0.08], np.float32) * ink[..., None] * (1 - emis[..., None])
    b1, b2, b3 = FN.F0.blur_down(glow, 6, 2), FN.F0.blur_down(glow, 24, 4), FN.F0.blur_down(glow, 60, 8)
    img = img * (1 + 0.8 * b2 + 0.6 * b3) + 0.6 * b1 + 0.4 * b2 + 0.15 * b3          # stronger spill: the livery lights the street
    return img * np.array([0.82, 0.8, 0.9], np.float32)


def threat_vehicles_v2():
    img = vehicle_matrix_img()
    lay = json.load(open(os.path.join(FN.SRC, "veh_layout.json")))
    cv = np.clip(img, 0, 1)
    cv[770:, :] = cv[770:, :] * 0.2 + BG * 0.8
    cv = title(cv, "THREAT VEHICLES V2", "CORP LIVERY x3: UNDER-GLOW POOL + ROOF LIVERY PLATE + CORP BEACONS  //  EACH WITH ITS MAP ICON  //  SHOWN AT 2.2x MAP ZOOM")
    corp_names = list(IC.CORP_RGB)
    for it in lay["items"]:
        x, y = it["px"], it["py"]
        corp = it["corp"]
        ui = it["col"] // 2
        cv = paste_rgba(cv, IC.vehicle_icon(corp, ui, up=it["up"], size=40), x - 120, y - 4)
        nm = it["unit"] + (" +" if it["up"] else "")
        cv = label(cv, x - 120, y + 30, nm, 12, (230, 236, 245), anchor="ma")
        if not it["up"]:
            cv = label(cv, x - 120, y + 45, it["role"], 10, DIM, anchor="ma")
    for it in lay["items"]:
        if it["col"] == 0:
            cv = label(cv, 24, it["py"] - 6, it["corp"], 24, IC.CORP_RGB[it["corp"]], font=SL.ANTON)
    sub = {"MERIDIAN": "orange + amber", "SOLACE": "lime-green + white", "HALCYON": "violet + amber", "ORBITAL": "ice-white + cyan",
           "REBEL_CELL": "red + scrap"}
    for it in lay["items"]:
        if it["col"] == 0:
            cv = label(cv, 24, it["py"] + 24, sub[it["corp"]], 11, DIM)
    # bottom left: the icon grammar
    cv = label(cv, 40, 786, "ICON GRAMMAR  (zoomed-out raid map, one rule per channel)", 14, U.CYAN)
    rules = [("SHAPE = CORP", "crate / capsule / shield / finned diamond / scrap octagon"),
             ("FILL = CORP COLOUR", "v2 livery colours, ink edge, white die-cut rim"),
             ("GLYPH = ROLE", ">> fast  weight heavy  special: seal/dose/freeze/drop/burn"),
             ("CROWN = UPGRADED +", "two white chevrons on top + double rim"),
             ("NOTCH = HEADING", "a pointer on the rim turns with the unit; the badge stays upright"),
             ("RING = LIVE HP", "lit segments, the same ring as the street threat ring")]
    for i, (a, b) in enumerate(rules):
        cv = label(cv, 40, 814 + i * 26, a, 14, (235, 240, 250))
        cv = label(cv, 250, 816 + i * 26, b, 12, TXT)
    demo = [("HALCYON", 1, False, None, None), ("HALCYON", 1, True, None, None), ("HALCYON", 1, True, -2.4, None), ("HALCYON", 1, True, -2.4, 0.64)]
    for i, (c, u, up, hd, hp) in enumerate(demo):
        cv = paste_rgba(cv, IC.vehicle_icon(c, u, up=up, size=52, heading=hd, hp=hp), 150 + i * 110, 1010)
    for i, t in enumerate(("base", "upgraded", "+ heading", "+ live HP")):
        cv = label(cv, 150 + i * 110, 1046, t, 11, DIM, anchor="ma")
    # bottom right: true map scale, vehicles vs icons
    k = lay["ortho"] / 440.0
    full = to_pil(img).resize((int(W * k), int(H * k)), Image.LANCZOS)
    xs = [it["px"] for it in lay["items"]]
    ys = [it["py"] for it in lay["items"]]
    bx = (int((min(xs) - 70) * k), int((min(ys) - 60) * k), int((max(xs) + 70) * k), int((max(ys) + 40) * k))
    strip = full.crop(bx)
    fit = min(600 / strip.size[0], 252 / strip.size[1])
    strip = strip.resize((int(strip.size[0] * fit), int(strip.size[1] * fit)), Image.LANCZOS)
    sx, sy = 660, 808
    cv = paste(cv, np.asarray(strip, np.float32) / 255, sx, sy)
    cv = label(cv, sx, sy - 22, "MAP SCALE (x%.2f): models" % fit, 13, U.CYAN)
    ix = sx + strip.size[0] + 24
    cv = label(cv, ix, sy - 22, "SAME, AS ICONS (zoomed-out view)", 13, U.CYAN)
    tile = np.zeros((strip.size[1], strip.size[0], 3), np.float32) + np.array([0.09, 0.08, 0.14], np.float32)
    for it in lay["items"]:
        tx = (it["px"] * k - bx[0]) * fit
        ty = (it["py"] * k - bx[1]) * fit
        tile = paste_rgba(tile, IC.vehicle_icon(it["corp"], it["col"] // 2, up=it["up"], size=22, heading=math.pi), tx, ty)
    cv = paste(cv, tile, ix, sy)
    return cv


def threat_rings(net, t=0.0):
    for (corp, ui, x, y, a, up, hp) in LY.THREATS_V2:
        net.threat_ring(x, y, hp=hp, state="live", t=t)


def screen_heading(x, y, a, cam=None):
    p0 = P(x, y, 0, cam=cam)
    p1 = P(x + math.cos(a) * 10, y + math.sin(a) * 10, 0, cam=cam)
    return math.atan2(p1[1] - p0[1], p1[0] - p0[0])


def vehicle_toggle():
    cv = canvas()
    cv = title(cv, "VEHICLE / ICON TOGGLE", "SAME RAID, SAME STREETS: CLOSE-UP SHOWS THE MODELS; ZOOMED OUT EACH UNIT BECOMES ITS ICON (AUTO BELOW 0.6x ZOOM, OR HOLD [V])")
    dec = world_decor("B", slot="stationed", cls="breaker", boosts=[("safe", "breaker")], routes=("r1", "r3"),
                      extra=lambda n: threat_rings(n))
    close = FN.finish("W_close", "night", decorate=dec, seed=1, tilt=0.0)
    cv = paste(cv, close, 40, 150, (1000, 563))
    cv = label(cv, 40, 724, "CLOSE-UP  (1.0x+): models with the v2 livery, HP ring on the street", 15, (235, 240, 250))
    # zoomed-out: a wider crop of the full map, models swapped for icons
    full_cam = scene_cam("B_full")
    cx, cy = P(104, -82, 0, cam=full_cam)
    cw, ch = 1150, 647
    box = (int(cx - cw / 2), int(cy - ch / 2) + 30, int(cx + cw / 2), int(cy + ch / 2) + 30)
    dw, dh = 820, 461
    sk = dw / cw
    icon_view = FN.finish("B_full", "night", decorate=world_decor("B", slot="stationed", cls="breaker", boosts=[("safe", "breaker")],
                                                                  routes=("r1", "r3")), seed=1)
    iv = crop(icon_view, box, (dw, dh))
    for (corp, ui, x, y, a, up, hp) in LY.THREATS_V2:
        px, py = P(x, y, 0, cam=full_cam)
        iv = paste_rgba(iv, IC.vehicle_icon(corp, ui, up=up, size=26, heading=screen_heading(x, y, a, full_cam), hp=hp),
                        (px - box[0]) * sk, (py - box[1]) * sk)
    # the close-up's footprint
    im = to_pil(iv)
    d = ImageDraw.Draw(im)
    fw, fh = 1920 * 150 / 440 * sk, 1080 * 150 / 440 * sk
    fx, fy = (cx - box[0]) * sk, (cy - box[1]) * sk
    d.rectangle([fx - fw / 2, fy - fh / 2, fx + fw / 2, fy + fh / 2], outline=(92, 225, 255), width=2)
    iv = to_f(im)
    cv = paste(cv, iv, 1060, 150)
    cv = label(cv, 1060, 622, "ZOOMED OUT (< 0.6x): icons, corp + role + upgrade + heading + HP", 15, (235, 240, 250))
    cv = label(cv, 1066, 158, "close-up area", 11, U.CYAN)
    wf = FN.finish("W_full", "night", decorate=world_decor("B", slot="stationed", cls="breaker", routes=("r1", "r3"),
                                                          extra=lambda n: threat_rings(n)), seed=1)
    cv = paste(cv, crop(wf, box, (400, 225)), 1060, 690)
    cv = label(cv, 1060, 922, "zoomed out WITHOUT the swap: corp colour survives,", 12, DIM)
    cv = label(cv, 1060, 940, "role / upgrade / heading do not", 12, DIM)
    # the toggle widget (CRT terminal, same family as the raid panels)
    rows = [("kv", "MAP ZOOM", "0.45x", (190, 225, 240)), ("kv", "UNITS", "ICONS (auto)", U.LIME), ("t", "hold [V]: show models", (150, 190, 205)),
            ("t", "hover an icon: name, HP, route", (150, 190, 205))]
    cv = U.put_panel(cv, U.terminal("VIEW", rows, w=330), 1500, 690)
    notes = ["Swap = a crossfade over 0.15 s at the zoom threshold (hysteresis 0.55 / 0.65); the HP ring stays on the street in both.",
             "Icons are billboards at a fixed screen size (26 px at 1080p), drawn above the ink, under the panels; the heading notch turns.",
             "Mixed corps are shown here only to compare the liveries; a real raid is usually one corporation."]
    for i, t in enumerate(notes):
        cv = label(cv, 40, 760 + i * 24, t, 13, TXT)
    demo = [("HALCYON", 1, False, 0.8), ("HALCYON", 0, True, 1.0), ("MERIDIAN", 1, True, 0.55), ("ORBITAL", 2, False, 1.0),
            ("SOLACE", 2, False, 0.4), ("REBEL_CELL", 0, True, 1.0)]
    for i, (c, u, up, hp) in enumerate(demo):
        cv = paste_rgba(cv, IC.vehicle_icon(c, u, up=up, size=46, hp=hp), 90 + i * 150, 900)
        cv = label(cv, 90 + i * 150, 950, IC.UNIT_NAMES[c][u] + (" +" if up else ""), 12, (230, 236, 245), anchor="ma")
        cv = label(cv, 90 + i * 150, 968, c, 10, IC.CORP_RGB[c], anchor="ma")
    cv = label(cv, 40, 1000, "the six units in this wave, as icons (46 px hover size)", 12, DIM)
    return cv


# ------------------------------------------------------------------ 4. heat at raid start, three bands live
HEAT_ROUTES = {1: ("r1",), 2: ("r1", "r2"), 3: ("r1", "r2", "r3")}
HEAT_EXPOSED = {1: (), 2: ("vault",), 3: ("vault", "proxy", "safe", "core")}
HEAT_HEAD = {1: ("HEAT 25", "WATCHED", U.AMBER), 2: ("HEAT 50", "HUNTED", (255, 120, 60)), 3: ("HEAT 75", "MANHUNT", U.HARM)}
HEAT_LINES = {1: ["1 wave  /  1 route  /  3 threats", "1 chopper sweeping the edge", "3 drones, no spotlights"],
              2: ["1 wave  /  2 routes  /  6 threats, +integrity", "chopper circling the VAULT", "7 drones with mini spots, strobes"],
              3: ["2 waves  /  3 routes  /  9 + 9 threats, +25%", "3 choppers + gunship on CORE", "14 drones, overlapping spots"]}
HEAT_UNITS = {1: [0, 1, 0], 2: [1, 0, 2], 3: [1, 2, 0]}       # halcyon unit index per convoy slot


def route_pos(pts, s):
    """Point at fraction s along a polyline (+ heading)."""
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    L = sum(seg)
    d = s * L
    for (a, b), l in zip(zip(pts, pts[1:]), seg):
        if d <= l:
            u = d / l
            return a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, math.atan2(b[1] - a[1], b[0] - a[0])
        d -= l
    a, b = pts[-2], pts[-1]
    return b[0], b[1], math.atan2(b[1] - a[1], b[0] - a[0])


def convoy(hl, t):
    """Threats moving along the band's routes at loop time t: (x, y, heading, unit, upgraded, alpha)."""
    out = []
    for ri, rid in enumerate(HEAT_ROUTES[hl]):
        pts = LY.route_points(rid)
        for k in range(3):
            s = (t + k * 0.11 + ri * 0.17) % 1.0
            x, y, a = route_pos(pts, 0.04 + 0.88 * s)
            alpha = min(1.0, s / 0.08, (1 - s) / 0.08)
            out.append((x, y, a, HEAT_UNITS[hl][k], hl >= 2, alpha))
    return out


def heat_frame(hl, f, n, panel_box=(250, 15, 710, 525), size=(420, 466)):
    t = f / n
    cam = scene_cam("anim_h%d" % hl)
    units = convoy(hl, t)

    def rings(net):
        for (x, y, a, u, up, al) in units:
            if al > 0.3:
                net.threat_ring(x, y, hp=1.0, state="live", t=t)
    sc = json.load(open(os.path.join(FN.SRC, "anim_h%d_scene.json" % hl)))
    exposed = tuple(p[5] for p in sc["frames"][f] if p[4] == "heli" and p[5])
    dec = world_decor("B", slot="stationed", cls="breaker", t=t, boosts=[("safe", "breaker")], routes=HEAT_ROUTES[hl],
                      exposed=exposed, packets=True, entries_incoming=(("e_west", "e_south") if hl == 3 else ()), extra=rings)
    img = FN.finish("anim_h%d" % hl, "night", decorate=dec, prefix="f%02d_" % f, frame=f, seed=1, fog=0.35, rain=False,
                    creep=(60 + 40 * hl, 0.15 * hl) if hl > 1 else None)
    h, w = img.shape[:2]
    for (x, y, a, u, up, al) in units:
        if al <= 0.05:
            continue
        px, py = P(x, y, 0, cam=cam, w=w, h=h)
        ic = IC.vehicle_icon("HALCYON", u, up=up, size=17, heading=screen_heading(x, y, a, cam), glow=True)
        if al < 1:
            ic.putalpha(ic.split()[3].point(lambda v, al=al: int(v * al)))
        img = paste_rgba(img, ic, px, py - 2)
    pil = to_pil(img).crop(panel_box).resize(size, Image.LANCZOS)
    return pil


def heat_gif():
    n = 20
    pw, ph = 420, 466
    gap = 14
    GW = 3 * pw + 4 * gap
    top, foot = 64, 96
    GH = top + ph + foot
    frames = []
    statics = []
    base = Image.new("RGB", (GW, GH), (8, 7, 14))
    d = ImageDraw.Draw(base)
    d.text((gap, 16), "HEAT AT RAID START SETS THE RAID", font=U.F(SL.ANTON, 30), fill=(255, 222, 30))
    d.text((gap + 470, 30), "locked for the whole raid: no escalation mid-raid  //  spot-lit node = EXPOSED (proposal)", font=U.F(SL.MONO, 14), fill=(92, 225, 255))
    for i, hl in enumerate((1, 2, 3)):
        x = gap + i * (pw + gap)
        head, mood, col = HEAT_HEAD[hl]
        y = top + ph + 8
        d.rectangle([x, y, x + pw, y + foot - 14], fill=(5, 13, 28), outline=tuple(int(c * 0.75) for c in col))
        d.text((x + 10, y + 8), "> %s  %s" % (head, mood), font=U.F(SL.MONO, 16), fill=col)
        # the locked heat meter: fill to the band, a padlock tick at its right end
        mx0, mx1, my = x + 230, x + pw - 30, y + 17
        d.rectangle([mx0, my - 5, mx1, my + 5], outline=(60, 70, 90))
        fx = mx0 + (mx1 - mx0) * (25 * hl) / 100
        d.rectangle([mx0 + 1, my - 4, fx, my + 4], fill=col)
        d.rectangle([fx + 4, my - 6, fx + 14, my + 6], outline=col, width=2)
        d.arc([fx + 5, my - 12, fx + 13, my - 2], 180, 360, fill=col, width=2)
        for k, ln in enumerate(HEAT_LINES[hl]):
            d.text((x + 12, y + 32 + k * 16), ln, font=U.F(SL.MONO, 13), fill=(190, 225, 240))
    for f in range(n):
        im = base.copy()
        for i, hl in enumerate((1, 2, 3)):
            x = gap + i * (pw + gap)
            im.paste(heat_frame(hl, f, n), (x, top))
            if hl == 3 and (f // 3) % 2 == 0:                  # wave 2 incoming blink
                ImageDraw.Draw(im).text((x + pw - 12, top + 12), "WAVE 2 INCOMING", font=U.F(SL.MONO, 13), fill=(255, 68, 51), anchor="ra")
        frames.append(im)
        print("heat frame", f, flush=True)
    return save_gif(frames, "heat_levels_live.gif", [110] * n, colors=200)


# ------------------------------------------------------------------ 5. campaign lost
import lost20 as LO  # noqa: E402


def campaign_lost():
    cv = canvas()
    sd = U.word_sticker(["CAMPAIGN LOST"], 50, [U.FILL_RED], seed=13, border=14)
    cv = U.place(cv, sd, 40 + sd["img"].size[0] / U.S / 2 - 20, 62, angle=-1.5)
    cv = label(cv, 46, 106, "HOME SERVER 0/50: THE CELL'S OWN STATION IS HACKED AND TAKEN DOWN  //  TWO WAYS TO SHOW IT", 15, U.CYAN)
    cv = paste(cv, LO.frame_A(0.86), 40, 150, (1000, 563))
    cv = label(cv, 40, 724, "A  RANSOMWARE LOCK", 24, U.LIME, font=SL.ANTON)
    cv = label(cv, 300, 732, "the losing corp's ransomware in its house style; padlocks stamp every node; countdown to the wipe", 12, TXT)
    for i, (u, t) in enumerate(((0.08, "1  the home server falls: tearing"), (0.32, "2  takeover wipes down, nodes padlocked, vinyl curls"),
                                (0.6, "3  notice + countdown, stickers drop off the glass"))):
        x = 40 + i * 340
        cv = paste(cv, LO.frame_A(u), x, 770, (320, 180))
        cv = label(cv, x, 956, t, 11, DIM)
    cv = paste(cv, LO.frame_B(0.9), 1080, 150, (800, 450))
    cv = label(cv, 1080, 610, "B  CARRIER LOST", 24, (235, 240, 250), font=SL.ANTON)
    cv = label(cv, 1300, 618, "the station's monitors die; a bare terminal is left", 12, TXT)
    for i, (u, t) in enumerate(((0.15, "1  tearing + RGB split"), (0.45, "2  CRT collapses to a line, a dot"))):
        x = 1080 + i * 410
        cv = paste(cv, LO.frame_B(u), x, 650, (390, 219))
        cv = label(cv, x, 874, t, 11, DIM)
    cv = label(cv, 1080, 906, "A, in each corporation's house style:", 13, U.CYAN)
    for i, corp in enumerate(("MERIDIAN", "SOLACE", "ORBITAL", "REBEL_CELL")):
        x = 1080 + i * 203
        img = LO.ransom(LO.raid_screen(), corp, u=1.0, countdown=6.21, progress=0.83, seed=3 + i)
        cv = paste(cv, img, x, 930, (190, 107))
        cv = label(cv, x, 1042, LO.CORP_STYLE[corp]["name"], 11, LO.CORP_STYLE[corp]["col"])
    L = U.pencil_layer(2005)
    U.pen_circle(L, 40 + 128, 737, 138, 24, U.Y_PEN, 5.0, 1.15)
    cv = U.pencil_composite(cv, L)
    cv = label(cv, 40, 990, "RECOMMENDED A: it says WHO beat you (corp style, their verb: PROCESSED / RECLAIMED / TREATED / DE-ORBITED / OVERWRITTEN)", 13, TXT)
    cv = label(cv, 40, 1012, "and keeps the Cell's mixed media alive to the last frame; B is purer but anonymous.", 13, TXT)
    return cv


def campaign_lost_gif():
    n_a, n_b = 28, 16
    GS = (640, 360)
    frames, durs = [], []
    for f in range(n_a):
        u = f / (n_a - 1)
        frames.append(LO.to_pil(LO.frame_A(u)).resize(GS, Image.LANCZOS))
        durs.append(70 if u < 0.2 else 110)
        print("A", f, flush=True)
    durs[-1] = 900
    card = Image.new("RGB", GS, (6, 5, 10))
    ImageDraw.Draw(card).text((GS[0] // 2, GS[1] // 2), "OPTION B  //  CARRIER LOST", font=U.F(SL.MONO, 28), fill=(92, 225, 255), anchor="mm")
    frames.append(card)
    durs.append(700)
    for f in range(n_b):
        u = f / (n_b - 1)
        frames.append(LO.to_pil(LO.frame_B(u)).resize(GS, Image.LANCZOS))
        durs.append(80 if u < 0.55 else 140)
        print("B", f, flush=True)
    durs[-1] = 1200
    return save_gif(frames, "campaign_lost.gif", durs, colors=220)


def term_blank(title_, w, h, accent=U.CYAN, seed=1):
    """A CRT terminal of a given height (blank rows) to draw custom content into."""
    rows = [("t", "", (0, 0, 0))] * max(1, int((h - 58) / 20))
    return U.terminal(title_, rows, w=w, accent=accent, seed=seed)


HEAT_RUNS = [6, 14, 26, 31, 44, 52, 58, 66, 70, 77, 82]       # heat after each run / raid (11 events)


def campaign_summary():
    base = LO.raid_screen()
    lum = base.mean(axis=2, keepdims=True)
    cv = lum * 0.22 * np.array([0.7, 0.62, 1.0], np.float32) + BG * 0.6
    sd = U.word_sticker(["CELL DOWN"], 58, [U.FILL_RED], seed=31, border=15)
    cv = U.place(cv, sd, 40 + sd["img"].size[0] / U.S / 2 - 16, 66, angle=-2)
    cv = label(cv, 46, 116, "CAMPAIGN 03  //  41 DAYS  //  11 RUNS + RAIDS  //  TAKEN DOWN BY HALCYON CIVIC (COMPLIANCE SWEEP, HEAT 82)", 15, U.CYAN)
    # --- operatives: roster cards (stickers) with their fate in grease pencil
    cv = U.put_panel(cv, term_blank("OPERATIVES  //  FATE", 600, 400), 40, 150)
    ops = [("breaker", 3, "STATIONED", "7 runs, MVP"), ("ghost", 2, "KIA run 9", "Server Rack, layer 7"),
           ("rigger", 1, "KIA run 4", "elite router"), ("botnet", 2, "RESERVES", "5 runs"), ("wrecker", 0, "KIA run 11", "the last run")]
    for i, (c, rk, fate, note) in enumerate(ops):
        x, y = 100 + i * 112, 300
        cv = U.place(cv, op_card(c, rank=rk, seed=40 + i), x, y, angle=[-3, 2, -1.5, 2.5, -2][i], scale=0.78)
        col = (255, 68, 51) if fate.startswith("KIA") else (123, 224, 123) if fate == "STATIONED" else (190, 225, 240)
        cv = label(cv, x, 392, fate, 12, col, anchor="ma")
        cv = label(cv, x, 410, note, 10, DIM, anchor="ma")
    cv = label(cv, 60, 440, "3 KIA  //  2 alive when the station fell (stationed + reserves)", 11, DIM)
    cv = label(cv, 60, 460, "a death loses everything unbanked (GDD 4.2)", 11, DIM)
    L = U.pencil_layer(2010)
    for i, (c, rk, fate, note) in enumerate(ops):
        if fate.startswith("KIA"):
            U.pen_x(L, 100 + i * 112, 300, 40, U.R_PEN, 6.0)
    U.pen_circle(L, 100, 300, 58, 76, U.Y_PEN, 4.5, 1.1)
    U.pen_text(L, "MVP", 100, 190, 22, U.Y_PEN, 4.0)
    cv = U.pencil_composite(cv, L)
    # --- the network at the end: the burnt map + node tally
    cv = U.put_panel(cv, term_blank("NETWORK AT THE END", 600, 420, accent=U.HARM), 40, 580)
    mp = crop(base, (560, 300, 1400, 800), (420, 250))
    cv = paste(cv, mp, 54, 618)
    rows = [("HELD", "3", U.GREEN), ("DISABLED", "1", U.AMBER), ("SEIZED", "1", U.HARM), ("HOME", "LOST", U.HARM), ("PEAK", "7 nodes", (190, 225, 240))]
    for i, (k, v, c) in enumerate(rows):
        cv = label(cv, 490, 626 + i * 26, k, 13, (150, 190, 205))
        cv = label(cv, 626, 626 + i * 26, v, 13, c, anchor="ra")
    cv = label(cv, 54, 884, "Sites claimed 9  //  raids 4: 3 held, 1 lost", 13, (190, 225, 240))
    cv = label(cv, 54, 906, "Exploits extracted 2 / 3  //  Schematics earned 214, spent 190", 13, (190, 225, 240))
    cv = label(cv, 54, 928, "Cycles banked 1 380  //  assets in the Armory at the end 5 / 6", 13, (190, 225, 240))
    L = U.pencil_layer(2011)
    cx, cy = 54 + (960 - 560) * 0.5, 618 + (585 - 300) * 0.5
    U.pen_circle(L, cx, cy, 34, 22, U.R_PEN, 5.0, 1.2)
    U.pen_text(L, "HOME", cx + 70, cy - 26, 18, U.R_PEN, 3.6)
    cv = U.pencil_composite(cv, L)
    # --- heat over the campaign (CRT graph) + who took you down
    pan = term_blank("HEAT  //  PEAK 82", 560, 300, accent=U.AMBER)
    im = pan["img"]
    d = ImageDraw.Draw(im)
    gx0, gy0, gx1, gy1 = 46, 44, 540, 262
    for th, nm in ((25, "25"), (50, "50"), (75, "75")):
        y = gy1 - (gy1 - gy0) * th / 100
        for x in range(gx0, gx1, 12):
            d.line([(x, y), (x + 6, y)], fill=(90, 70, 40, 255), width=1)
        d.text((gx0 - 8, y), nm, font=U.F(SL.MONO, 11), fill=(255, 176, 0, 255), anchor="rm")
    pts = [(gx0 + (gx1 - gx0) * i / (len(HEAT_RUNS) - 1), gy1 - (gy1 - gy0) * v / 100) for i, v in enumerate(HEAT_RUNS)]
    d.line(pts, fill=(255, 176, 0, 255), width=3)
    for i, p in enumerate(pts):
        r = 4 if i not in (2, 5, 9, 10) else 7
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=(255, 176, 0, 255) if i not in (2, 5, 9, 10) else (255, 68, 51, 255))
    d.text((gx0, gy1 + 12), "run 1", font=U.F(SL.MONO, 11), fill=(150, 190, 205, 255))
    d.text((gx1, gy1 + 12), "final raid", font=U.F(SL.MONO, 11), fill=(150, 190, 205, 255), anchor="ra")
    cv = U.put_panel(cv, pan, 680, 150)
    cv = label(cv, 700, 458, "red dots = raids (25+ / 50+ / 75+, heat at raid start sets the raid)", 11, DIM)
    st = LO.CORP_STYLE["HALCYON"]
    pan2 = term_blank("TAKEN DOWN BY", 560, 240, accent=st["col"])
    im2 = pan2["img"]
    im2.alpha_composite(LO.seal(st, 170), (20, 44))
    d2 = ImageDraw.Draw(im2)
    d2.text((210, 56), "HALCYON CIVIC", font=U.F(LO.BAHN, 40), fill=(244, 241, 233, 255))
    d2.text((210, 108), "raid: COMPLIANCE SWEEP", font=U.F(SL.MONO, 16), fill=st["col"] + (255,))
    d2.text((210, 132), "3 routes, 2 waves, 18 threats", font=U.F(SL.MONO, 14), fill=(190, 225, 240, 255))
    d2.text((210, 154), "BAILIFF reached the home server", font=U.F(SL.MONO, 14), fill=(190, 225, 240, 255))
    d2.text((210, 176), "on step 19 / 30", font=U.F(SL.MONO, 14), fill=(190, 225, 240, 255))
    cv = U.put_panel(cv, pan2, 680, 490)
    stp = U.word_sticker(["PROCESSED"], 30, [("grad", (190, 150, 255), (120, 80, 230))], seed=33, border=10)
    cv = U.place(cv, stp, 1120, 700, angle=8, scale=0.9)
    log = [("01  T1  CUSTOMS YARD", "BREAKER", "CLEARED", U.GREEN), ("02  T1  CLINIC 4", "GHOST", "CLEARED", U.GREEN),
           ("03  RAID  heat 25", "-", "HELD", U.GREEN), ("04  T2  RELAY FARM", "RIGGER", "KIA", U.HARM),
           ("05  T2  ARCHIVE", "BREAKER", "EXPLOIT", U.AMBER), ("06  RAID  heat 50", "-", "HELD", U.GREEN),
           ("07  T2  DEPOT 12", "BOTNET", "CLEARED", U.GREEN), ("08  T3  CIVIC HALL", "BREAKER", "EXPLOIT", U.AMBER),
           ("09  T3  SERVER VAULT", "GHOST", "KIA", U.HARM), ("10  RAID  heat 75", "-", "HELD", U.GREEN),
           ("11  T4  CIVIC CORE", "WRECKER", "KIA + RAID LOST", U.HARM)]
    pan3 = term_blank("RUN LOG", 560, 290, accent=U.CYAN, seed=4)
    d3 = ImageDraw.Draw(pan3["img"])
    for i, (a, b, c, col) in enumerate(log):
        y = 40 + i * 21
        d3.text((14, y), a, font=U.F(SL.MONO, 14), fill=(190, 225, 240, 255))
        d3.text((290, y), b, font=U.F(SL.MONO, 14), fill=(150, 190, 205, 255))
        d3.text((546, y), c, font=U.F(SL.MONO, 14), fill=col + (255,), anchor="ra")
    cv = U.put_panel(cv, pan3, 680, 760)
    # --- unlocks (stickers: static rewards) + records
    cv = U.put_panel(cv, term_blank("UNLOCKED  //  PROFILE", 560, 300, accent=U.LIME), 1320, 150)
    cv = U.place(cv, op_card("phantom", rank=0, seed=60, gloss_k=1.0), 1420, 320, angle=-4, scale=0.8)
    cv = label(cv, 1420, 410, "NEW CLASS", 12, U.LIME, anchor="ma")
    u1 = U.word_sticker(["ICE 6"], 34, [U.FILL_YELLOW], seed=41, border=11)
    cv = U.place(cv, u1, 1610, 260, angle=3)
    cv = label(cv, 1610, 296, "ICE record, Halcyon", 11, DIM, anchor="ma")
    u2 = U.word_sticker(["BUNKER"], 30, [("grad", (120, 236, 255), (40, 160, 220))], seed=42, border=11)
    cv = U.place(cv, u2, 1610, 355, angle=-2)
    cv = label(cv, 1610, 390, "home-server variant", 11, DIM, anchor="ma")
    cv = label(cv, 1340, 430, "kept: profile unlocks, ICE records, class unlocks", 11, DIM)
    rows = [("kv", "CAMPAIGNS", "3  (1 won)", (190, 225, 240)), ("kv", "BEST ICE", "6 / HALCYON 6", U.AMBER), ("kv", "RUNS SURVIVED", "18 total", (190, 225, 240)),
            ("kv", "OPERATIVES LOST", "7 total", U.HARM)]
    cv = U.put_panel(cv, U.terminal("RECORDS", rows, w=560, accent=U.CYAN), 1320, 490)
    # --- buttons (stickers)
    b1 = U.word_sticker(["NEW CAMPAIGN"], 40, [U.FILL_PINK], seed=21, border=13)
    cv = U.place(cv, b1, 1640, 860, angle=-2)
    b2 = U.word_sticker(["MAIN MENU"], 26, [("grad", (230, 230, 236), (170, 170, 182))], seed=22, border=10)
    cv = U.place(cv, b2, 1680, 960, angle=1.5)
    L = U.pencil_layer(2012)
    U.pen_text(L, "AGAIN?", 1430, 940, 26, U.Y_PEN, 4.4)
    U.pen_arrow(L, [(1470, 920), (1500, 890), (1520, 872)], U.Y_PEN, 4.0, 14)
    cv = U.pencil_composite(cv, L)
    return cv


def contact():
    from PIL import ImageSequence
    names = ["building_nodes_v2.png", "operators.png", "operator_drop.gif", "threat_vehicles_v2.png", "vehicle_toggle.png",
             "heat_levels_live.gif", "campaign_lost.png", "campaign_lost.gif", "campaign_summary.png"]
    tw, th, cols = 600, 338, 3
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols + 40, th * rows + 24 * rows + 80), (10, 9, 16))
    d = ImageDraw.Draw(sheet)
    d.text((14, 16), "ROUND 20  RAID WORLD: ROOFTOPS, STATIONED OPERATIVES, CORP LIVERY + ICONS, HEAT LIVE, CAMPAIGN LOST", font=U.F(SL.ANTON, 30), fill=(255, 222, 30))
    for i, n in enumerate(names):
        im = Image.open(os.path.join(OUT, n))
        if n.endswith(".gif"):
            fr = [f.convert("RGB") for f in ImageSequence.Iterator(im)]
            im = fr[len(fr) * 2 // 3]
        im = im.convert("RGB")
        k = min(tw / im.size[0], th / im.size[1])
        im = im.resize((int(im.size[0] * k), int(im.size[1] * k)), Image.LANCZOS)
        x, y = 10 + (i % cols) * (tw + 10), 70 + (i // cols) * (th + 24)
        sheet.paste(im, (x, y))
        d.text((x + 4, y + th + 2), n, font=U.F(SL.MONO, 15), fill=(92, 225, 255))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=86)
    print("saved contact_sheet.jpg")


if __name__ == "__main__":
    which = sys.argv[1:] or ["buildings", "operators", "opgif", "vehicles", "toggle", "heatgif", "lost", "lostgif", "summary", "contact"]
    if "buildings" in which:
        save(building_nodes_v2(), "building_nodes_v2.png")
    if "operators" in which:
        save(operators(), "operators.png")
    if "opgif" in which:
        operator_gif()
    if "vehicles" in which:
        save(threat_vehicles_v2(), "threat_vehicles_v2.png")
    if "toggle" in which:
        save(vehicle_toggle(), "vehicle_toggle.png")
    if "heatgif" in which:
        heat_gif()
    if "lost" in which:
        save(campaign_lost(), "campaign_lost.png")
    if "lostgif" in which:
        campaign_lost_gif()
    if "summary" in which:
        save(campaign_summary(), "campaign_summary.png")
    if "contact" in which:
        contact()
