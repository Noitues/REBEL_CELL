"""Round 20 raid UI: frames, sheets and the interaction gifs.

python screens20.py [name ...]  names: setup wave result health panels decoy gifs contact (default all)
Inputs: ../scratch/bl (run_blender.py + vehicles.py sprites). Outputs in the round folder.
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
import netdecal19 as N19  # noqa: E402
import netdecal20 as ND  # noqa: E402
import ui19 as U  # noqa: E402
import ui20 as V  # noqa: E402
from ui20 import Frame, P  # noqa: E402

OUT = os.path.dirname(HERE)
GIFS = os.path.join(OUT, "interactions_gifs")
SL = U.SL
W, H = LY.W, LY.H
N = LY.NODES
BG = np.array([0.03, 0.028, 0.05], np.float32)
FORECAST = {"vault": "disabled", "proxy": "seized"}
MAXI = {k: v[5][1] for k, v in N.items()}


def save(img, name, folder=OUT):
    Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(os.path.join(folder, name), optimize=True)
    print("saved", name, flush=True)


def label(img, x, y, text, size=15, col=(190, 225, 240), font=None, anchor="la"):
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    ImageDraw.Draw(im).text((x, y), text, font=U.F(font or SL.MONO, size), fill=col, anchor=anchor)
    return np.asarray(im, np.float32) / 255


def title(img, big, sub, col=None, x=40, y=24):
    sd = U.word_sticker([big], 50, [col or U.FILL_YELLOW], seed=11, border=14)
    w = sd["img"].size[0] / U.S
    img = U.place(img, sd, x + w / 2 - 20, y + 38, angle=-1.5)
    return label(img, x + 6, y + 82, sub, 15, U.CYAN)


# ------------------------------------------------------------------ the street-plane state (decal)
def deco(st=None, health=None, forecast=True, flash=None, link_states=None, packets=False, t=0.0, lure=None, frost=None,
         rings=(), entries_incoming=(), exposed=(), ripple=None, extra=None):
    st_ = {k: ("home" if k == "core" else "holds") for k in N}
    st_.update(st or {})
    health = health or {}
    flash = flash or {}
    link_states = link_states or {}
    fc = dict(FORECAST) if forecast is True else (forecast or {})

    def f(net):
        for a, b in LY.LINKS:
            s = link_states.get((a, b), link_states.get((b, a)))
            if s is None:
                s = "ok"
                if "seized" in (st_[a], st_[b]) or "burnt" in (st_[a], st_[b]):
                    s = "dead"
                elif "disabled" in (st_[a], st_[b]):
                    s = "dim"
            net.link(a, b, s, t=t, packets=packets)
        for key in LY.NODE_BUILDINGS:
            sk = st_[key]
            net.riser(key, "dead" if sk in ("seized", "burnt") else "dim" if sk == "disabled" else "ok")
        for k in LY.ENTRIES:
            net.entry(k, active=True, incoming=k in entries_incoming, t=t)
        if lure:
            net.lure(lure, t)
        if frost:
            net.frost_link(*frost)
        for k in N:
            f_ = fc.get(k)
            net.health_pad(k, st_[k], health.get(k, 1.0), forecast=f_, flash=flash.get(k), exposed=k in exposed, t=t)
        for r in rings:
            net.threat_ring(*r)
        if ripple:
            k, rr, a = ripple
            net.pool_ring(N[k][0], N[k][1], rr, ND.C(0.83, 1.0, 0.0), a)
            net.pool_ring(N[k][0], N[k][1], rr * 0.8, ND.C(0.83, 1.0, 0.0), a * 0.5)
        if extra:
            extra(net)
    return f


_cache = {}


def base(tag, d, box=None, key=None, mode="night"):
    """Finished frame (cached by key) as a Frame."""
    k = (tag, key, box, mode) if key is not None else None
    if k is not None and k in _cache:
        return Frame(_cache[k].copy(), box)
    img = FN.finish(tag, mode, decorate=d, net_cls=ND.Net, box=box, seed=1)
    if k is not None:
        if len(_cache) > 40:
            _cache.clear()
        _cache[k] = img.copy()
    return Frame(img, box)


def boxc(cx, cy, w=640, h=360):
    x0 = int(min(max(0, cx - w / 2), W - w))
    y0 = int(min(max(0, cy - h / 2), H - h))
    return (x0, y0, x0 + w, y0 + h)


# ------------------------------------------------------------------ the setup screen (per panel medium)
def setup_screen(medium="mixed", show_speed=True):
    vx, vy = P(*N["vault"][:2])
    fr = base("setup_h1", deco(flash={"vault": "hover"}, forecast={"vault": "holds", "proxy": "seized"}), key="setup_hover")
    pen = V.Pencil(fr, 2001)
    V.pencil_routes(pen)
    pen.circle(vx, vy, 76, 50, V.Y_PEN, 7.0, turns=1.2)
    pen.arrow([(1345, 600), (1330, 520), (1262, 462)], V.Y_PEN, 7.0, 20)
    fr = pen.composite()
    img = title(fr.img, "RAID SETUP", "03 CELL DEFENSE  //  COMPLIANCE SWEEP  //  " + V.MEDIUMS[medium]["name"])
    for pn, x, y in V.panels_for(medium):
        img = U.put_panel(img, pn, x, y)
    if medium == "glass":     # grease pencil allowed on the glass slate: the Cell circles the vault priority
        f2 = Frame(img)
        p2 = V.Pencil(f2, 2002)
        p2.circle(200, 548, 160, 20, V.R_PEN, 4.5)
        p2.text("!", 348, 544, 22, V.R_PEN, 4.5)
        img = p2.composite().img
    img = U.put_panel(img, U.terminal("IF PLACED", [("t", "ICE LOCK > VAULT TERMINAL", (190, 225, 240)), ("kv", "VAULT", "DISABLED > HOLDS", U.GREEN),
                                                    ("kv", "HOME", "42 > 45", U.PINK)], w=300, accent=U.GREEN), 1600, 560)
    img = tray(img)
    sd = U.asset_card(*U.TRAY[2][:5], U.TRAY[2][5], 52, gloss_k=1.0)
    img = U.place(img, sd, 1395, 660, angle=-9, hover=0.7)
    img = start_button(img)
    if show_speed:
        sp = V.speed_ctrl(medium, "2x", "-- / 30")
        img = label(img, 1480, 692, "PLAYOUT CONTROLS (same medium)", 12, (150, 165, 185))
        img = U.put_panel(img, sp, 1480, 710)
    return img


def tray(img, skip="ICE LOCK", y=985, x0=560):
    x = x0
    for i, (nm, gl, hp, cp, ds, col) in enumerate(U.TRAY):
        if nm == skip:
            x += 162
            continue
        sd = U.asset_card(nm, gl, hp, cp, ds, col, 50 + i)
        img = U.place(img, sd, x, y, angle=[-2, 1.5, -1, 2, -1.5, 1][i])
        x += 162
    return img


def start_button(img, x=1700, y=1010, squash=1.0):
    sd = U.word_sticker(["START DEFENSE"], 40, [U.FILL_PINK], seed=21, border=13)
    return U.place(img, sd, x, y, angle=-2, scale=squash, squash=(1.0 / max(squash, 0.5) ** 0.3, squash))


# ------------------------------------------------------------------ wave (in progress)
WAVE_ST = {"proxy": "disabled"}
WAVE_HEALTH = {"firewall": 0.9, "safe": 0.7, "vault": 0.3, "core": 1.0}


def wave_spots():
    sc = json.load(open(os.path.join(V.BL, "wave_h2_scene.json")))
    return {k: tuple(v) for k, v in sc["spots"].items()}


def wave_screen():
    sp = wave_spots()
    rings = [(sp[k][0], sp[k][1], hp) for k, hp in (("bailiff", 0.35), ("hauler", 0.6), ("inspector", 0.5), ("customs", 0.6), ("lander", 1.0))]
    rings.append((sp["courier"][0], sp["courier"][1], 0.0, "down"))
    fr = base("wave_h2", deco(st=WAVE_ST, health=WAVE_HEALTH, forecast={}, packets=True, t=0.3, rings=rings, entries_incoming=("e_west",)), key="wave")
    rng = np.random.default_rng(7)
    for k, txt in (("bailiff", "-8"), ("hauler", "-6"), ("inspector", "-3")):
        x, y = P(*sp[k][:2], sp[k][2])
        fr = V.shards(fr, x, y - 10, rng, 22, t=0.4)
        fr = V.float_num(fr, x + 26, y - 44, txt, size=30)
    fr = V.health_float(fr, "safe", 14, 20, col=(212, 255, 0))      # hovered node
    pen = V.Pencil(fr, 2003)
    V.pencil_routes(pen, letters=False)
    cx, cy = P(*sp["courier"][:2], sp["courier"][2])
    pen.x(cx, cy, 20)
    pen.text("DOWN", cx + 4, cy - 44, 17, V.R_PEN, 4.0)
    ex, ey = P(*LY.ENTRIES["e_west"])
    pen.circle(ex, ey, 50, 33)
    pen.text("INCOMING", ex + 20, ey - 58, 18, V.R_PEN, 4.2)
    img = pen.composite().img
    img = title(img, "RAID IN PROGRESS", "03 CELL DEFENSE  //  COMPLIANCE SWEEP  //  WAVE 1 OF 2  //  STEP 07", col=U.FILL_RED)
    img = U.put_panel(img, U.terminal("LIVE RAID FEED", [("t", "07  RAILGUN > BAILIFF        -8", U.CYAN), ("t", "07  FLAK x3 > HAULER          -6", U.AMBER),
                                                         ("t", "07  FW TURRET > INSPECTOR    -3", U.CYAN), ("t", "06  COURIER DESTROYED", U.GREEN),
                                                         ("t", "06  PROXY DISABLED (HAULER)", U.AMBER), ("t", "05  CUSTOMS SEALS LINK S2", U.HARM)], w=330), 22, 150)
    img = U.put_panel(img, U.terminal("RAID", [("kv", "HOME", "50 / 50", U.PINK), ("kv", "THREATS LEFT", "5 / 6", U.HARM),
                                               ("kv", "NEXT WAVE", "STEP 9  (WEST)", U.HARM)], w=300, accent=U.HARM), 1600, 120)
    img = label(img, 1600, 252, "hover a node: health numbers (or Options: always show)", 11, (150, 165, 185))
    img = U.put_panel(img, U.speed_terminal(), 745, 1010)
    return img


# ------------------------------------------------------------------ post-raid result
RESULT_ST = {"proxy": "disabled"}
RESULT_HEALTH = {"firewall": 0.9, "safe": 0.7, "vault": 0.3}


def result_rows():
    return [("t", "THREATS DESTROYED 6 / 6  //  STEPS 22", U.GREEN), ("sep",),
            ("node", "picto_hp", "CORE (home)", "50/50", U.PINK, "kept"),
            ("node", "slice_firewall", "FIREWALL RELAY", "27/30", U.GREEN, "kept"),
            ("node", "picto_all_targets", "RELAY", "15/15", U.GREEN, "kept"),
            ("node", "placeholder_key", "SAFEHOUSE", "14/20", U.GREEN, "kept"),
            ("node", "placeholder_vault", "VAULT TERMINAL", "6/20", U.AMBER, "kept, damaged"),
            ("node", "placeholder_spoof", "PROXY RELAY", "DISABLED", U.AMBER, "repair 10 SCH (50% of install)"),
            ("sep",), ("kv", "REWARD", "+12 SCHEMATICS", U.GREEN), ("kv", "HEAT", "52 > 52  (±0)", (190, 225, 240)),
            ("t", "a lost raid would add +5 Heat (GDD 11.5)", (110, 140, 160))]


def result_screen(stamp=1.0, rows_k=1.0):
    fr = base("setup_h1", deco(st=RESULT_ST, health=RESULT_HEALTH, forecast={}, packets=True, t=0.5), key="result")
    img = fr.img * 0.8
    img = title(img, "RAID REPORT", "03 CELL DEFENSE  //  COMPLIANCE SWEEP  //  RESULT  ->  HEAT IS SETTLED AFTER THE RAID")
    rows = result_rows()
    n = max(1, int(round(len(rows) * rows_k)))
    img = U.put_panel(img, U.terminal("RAID REPORT", rows[:n], w=420, accent=U.GREEN), 1460, 140)
    if stamp > 0:
        sd = U.word_sticker(["CELL HOLDS"], 92, [U.FILL_YELLOW], seed=31, border=20)
        sc = 1.0 + 0.6 * (1 - min(1.0, stamp)) ** 2
        img = U.place(img, sd, 760, 300, angle=-5, scale=sc, hover=max(0.0, 1 - stamp) * 0.8)
    sd = U.word_sticker(["BACK TO THE GRID"], 34, [U.FILL_PINK], seed=22, border=12)
    img = U.place(img, sd, 1700, 1010, angle=-2)
    return img


# ------------------------------------------------------------------ node health strip
def health_strip():
    cv = np.zeros((H, W, 3), np.float32) + BG
    cv = title(cv, "NODE HEALTH", "HEALTH = HOW MUCH OF THE SOCKET IS LIT  //  DRAINS NORTH > SOUTH  //  NUMBERS ON HOVER OR 'ALWAYS SHOW'")
    vx, vy = P(*N["safe"][:2])
    box = boxc(vx, vy - 20, 200, 173)
    steps = [(1.0, "holds", "20/20  FULL"), (0.75, "holds", "15/20"), (0.5, "holds", "10/20"), (0.25, "holds", "5/20  (low)"),
             (0.0, "disabled", "0  DISABLED")]
    for i, (hp, st, lab) in enumerate(steps):
        fr = Frame(FN.finish("setup_h1", "night", decorate=deco(st={"safe": st}, health={"safe": hp}, forecast={}), net_cls=ND.Net, box=box,
                             out_size=(300, 260), seed=1), box)
        x = 40 + i * 372
        cv[150:150 + 260, x:x + 300] = fr.img[:260, :300]
        cv = label(cv, x, 420, lab, 20, (230, 236, 245), font=SL.ANTON)
    cv = label(cv, 40, 456, "lit part = the active colour; the faded north part takes the disabled look (dashed frame, dark pins) but stays green;"
               " at 0 the socket switches to amber + dashed outline.", 13, (170, 185, 205))
    # hover / always-show
    for i, (hp, st, nowmx, note) in enumerate(((0.5, "holds", (10, 20), "HOVER: the numbers float above the north point"),
                                               (0.25, "holds", (5, 20), "OPTIONS 'ALWAYS SHOW HEALTH': on every node"))):
        bb = boxc(*P(*N["safe"][:2]), 300, 260)
        bb = (bb[0], bb[1] - 40, bb[2], bb[3] - 40)
        fr = base("setup_h1", deco(st={"safe": st}, health={"safe": hp}, forecast={}), box=bb, key="hs_h%d" % i)
        fr = V.health_float(fr, "safe", *nowmx, col=(212, 255, 0) if hp > 0.34 else (255, 176, 0))
        x = 40 + i * 372
        cv[520:780, x:x + 300] = fr.img[:260, :300]
        cv = label(cv, x, 790, note, 12, (200, 210, 225))
    full = base("wave_h2", deco(st=WAVE_ST, health=WAVE_HEALTH, forecast={}), key="wave_plain")
    for k in N:
        if k in WAVE_ST:
            continue
        hp = WAVE_HEALTH.get(k, 1.0)
        full = V.health_float(full, k, round(hp * MAXI[k]), MAXI[k], col=(212, 255, 0) if hp > 0.66 else (255, 176, 0) if hp > 0.33 else (255, 68, 51))
    c = Image.fromarray((np.clip(full.img, 0, 1) * 255).astype(np.uint8)).crop((420, 230, 1500, 900)).resize((860, 534), Image.LANCZOS)
    cv[520:1054, 1020:1880] = np.asarray(c, np.float32) / 255
    cv = label(cv, 1020, 500, "IN THE WAVE, 'ALWAYS SHOW' ON", 14, U.CYAN)
    return cv


# ------------------------------------------------------------------ panel mediums v2
def panel_mediums():
    cv = np.zeros((H, W, 3), np.float32) + BG
    cv = title(cv, "PANEL MEDIUMS v2", "WHAT EACH PANEL IS IN THE FICTION  ->  ITS MEDIUM  //  each shown on the setup screen (full size in panel_options/)")
    order = ["holo", "bezel", "glass", "decrypt", "mixed"]
    tw, th = 600, 338
    for i, m in enumerate(order):
        img = setup_screen(m)
        save(img, "opt_%s.png" % m, os.path.join(OUT, "panel_options"))
        r, c = divmod(i, 3)
        x, y = 40 + c * 620, 140 + r * 440
        t = np.asarray(Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((tw, th), Image.LANCZOS), np.float32) / 255
        cv[y:y + th, x:x + tw] = t
        cv = label(cv, x, y + th + 6, V.MEDIUMS[m]["name"], 20, U.LIME if m == "mixed" else (230, 236, 245), font=SL.ANTON)
        cv = label(cv, x, y + th + 36, V.MEDIUMS[m]["desc"], 11, (170, 185, 205))
    x, y = 40 + 2 * 620, 140 + 440
    lines = [("FICTION", U.CYAN), ("NETWORK STATUS = the Cell's own system", (220, 228, 240)), ("   -> C screens & data (CRT terminal)", (150, 165, 185)),
             ("RAID INCOMING = an intercepted corp work order", (220, 228, 240)), ("   -> printout under glass, redacted, corp seal", (150, 165, 185)),
             ("THREAT INTEL = scanned / decrypted surveillance", (220, 228, 240)), ("   -> projected holo with scanned silhouettes", (150, 165, 185)),
             ("LOADOUT = the armory's physical assets", (220, 228, 240)), ("   -> stickers (static objects)", (150, 165, 185)),
             ("SPEED / SKIP = a control of the Cell's deck", (220, 228, 240)), ("   -> same medium as the network panel", (150, 165, 185)),
             ("", (0, 0, 0)), ("E recommended: every medium earns its place;", U.LIME), ("the holo (designer's lean) carries the intel.", U.LIME),
             ("If one medium for all: A holo, with B/D as fallbacks.", (200, 210, 225))]
    for k, (t, col) in enumerate(lines):
        cv = label(cv, x, y + k * 24, t, 14, col)
    return cv


# ------------------------------------------------------------------ GIFS
def save_gif(frames, name, dur=90, colors=128, size=None):
    if size:
        frames = [f.resize(size, Image.LANCZOS) for f in frames]
    pal = frames[len(frames) // 2].quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    path = os.path.join(GIFS, name)
    q[0].save(path, save_all=True, append_images=q[1:], duration=dur, loop=0, optimize=True)
    kb = os.path.getsize(path) // 1024
    if kb > 1950 and colors > 48:
        return save_gif(frames, name, dur, colors // 2)
    print("gif", name, kb, "KB", flush=True)
    return frames


def topil(fr):
    return Image.fromarray((np.clip(fr.img, 0, 1) * 255).astype(np.uint8))


ONLY = [a for a in os.environ.get("GIF_ONLY", "").split(",") if a]


def gif(name, n, fn, dur=90, size=None):
    if ONLY and not any(name.startswith(o) for o in ONLY) and os.path.exists(os.path.join(GIFS, name)):
        g = Image.open(os.path.join(GIFS, name))
        frames = []
        for k in range(g.n_frames):
            g.seek(k)
            frames.append(g.convert("RGB").copy())
        GIF_FRAMES[name] = frames
        return frames
    frames = []
    for i in range(n):
        frames.append(topil(fn(i / n, i)))
    save_gif(frames, name, dur, size=size)
    GIF_FRAMES[name] = frames
    return frames


GIF_FRAMES = {}


def ease(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def seg(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def card_at(fr, name, x, y, ang=0.0, hover=0.7, gloss=0.22, scale=1.0):
    t_ = next(t for t in U.TRAY if t[0] == name)
    sd = U.asset_card(*t_[:5], t_[5], 60, gloss_k=gloss)
    return V.place_sticker(fr, sd, x, y, ang, hover=hover, scale=scale)


SPOTS = json.load(open(os.path.join(V.BL, "setup_h1_scene.json")))["spots"] if os.path.exists(os.path.join(V.BL, "setup_h1_scene.json")) else {}


def build_gifs():
    os.makedirs(GIFS, exist_ok=True)
    vx, vy = P(*N["vault"][:2])
    rx, ry = P(*N["relay"][:2])
    px, py = P(*N["proxy"][:2])
    fx, fy = P(*N["firewall"][:2])
    sx, sy = P(*N["safe"][:2])
    cx, cy = P(*N["core"][:2])
    INDEX.clear()

    # 01 pick up: card lifts, valid sockets pulse white
    b = boxc(vx - 60, vy + 120)

    def g01(t, i):
        on = t > 0.3 and int(i / 3) % 2 == 0
        fr = base("setup_h1", deco(flash={k: "hover" for k in ("relay", "firewall", "safe", "vault")} if on else {}), b, "g01%d" % on)
        e = ease(seg(t, 0.0, 0.5))
        return card_at(fr, "ICE LOCK", vx + 40, vy + 330 - 140 * e, -10 * e, hover=0.2 + 0.6 * e, gloss=0.22 + 0.78 * e)
    gif("01_pick_up.gif", 16, g01)
    INDEX.append(("01_pick_up.gif", "Pick up a defence", "sticker peels off the tray; every socket that can take it pulses white", "STICKER + INLAY"))

    # 02 drag valid: forecast ring re-projects, pencil arrow + circle draw on
    b = boxc(vx + 40, vy + 60)

    def g02(t, i):
        over = t > 0.45
        fr = base("setup_h1", deco(flash={"vault": "hover"} if over else {}, forecast={"vault": "holds" if over else "disabled", "proxy": "seized"}), b, "g02%d" % over)
        e = ease(seg(t, 0.0, 0.45))
        fr = card_at(fr, "ICE LOCK", vx + 280 - 80 * e, vy + 260 - 60 * e, -9)
        pen = V.Pencil(fr, 21)
        pen.arrow([(vx + 150, vy + 170), (vx + 110, vy + 90), (vx + 66, vy + 50)], V.Y_PEN, 7.0, 20, progress=seg(t, 0.45, 0.7))
        pen.circle(vx, vy, 76, 50, V.Y_PEN, 7.0, progress=seg(t, 0.6, 0.9), turns=1.2)
        fr = pen.composite()
        if over:
            fr = V.put_panel(fr, U.terminal("IF PLACED", [("kv", "VAULT", "DISABLED > HOLDS", U.GREEN)], w=250, accent=U.GREEN), b[0] + 10, b[1] + 10)
        return fr
    gif("02_drag_valid.gif", 18, g02)
    INDEX.append(("02_drag_valid.gif", "Drag over a valid node", "white frame; dashed forecast ring turns green; yellow pencil arrow + circle; IF PLACED terminal", "INLAY + PENCIL + TERMINAL"))

    # 03 drag invalid: FIREWALL RELAY's two asset slots are full -> red X, card springs back
    b = boxc(fx + 40, fy + 60)

    def g03(t, i):
        bad = 0.35 < t < 0.75
        fr = base("setup_h1", deco(flash={"firewall": "invalid"} if bad else {}), b, "g03%d" % bad)
        if t < 0.35:
            e = ease(seg(t, 0, 0.35))
            x, y = fx + 280 - 105 * e, fy + 260 - 125 * e
        elif t < 0.75:
            x, y = fx + 80 + 3 * math.sin(i * 2.5), fy + 100
        else:
            e = ease(seg(t, 0.75, 1.0))
            x, y = fx + 175 + 140 * e, fy + 135 + 220 * e
        fr = card_at(fr, "TURRET", x, y, 10)
        if bad:
            fr = V.put_panel(fr, U.terminal("NO SLOT", [("t", "FIREWALL RELAY: 2/2 ASSET SLOTS", U.HARM)], w=280, accent=U.HARM), b[0] + 10, b[1] + 10)
        return fr
    gif("03_drag_invalid.gif", 18, g03)
    INDEX.append(("03_drag_invalid.gif", "Invalid drop", "red frame + X (no free slot / seized / not a node); the card springs back to the tray", "INLAY + STICKER + TERMINAL"))

    # 04 placed: card shrinks onto the socket, lime ripple
    b = boxc(vx, vy + 40)

    def g04(t, i):
        rip = seg(t, 0.35, 1.0)
        fr = base("setup_h1", deco(forecast={"vault": "holds", "proxy": "seized"}, ripple=("vault", 11 + 26 * rip, 1.3 * (1 - rip)) if 0 < rip < 1 else None),
                  b, "g04%d" % int(rip * 20))
        if t < 0.35:
            e = ease(seg(t, 0, 0.35))
            fr = card_at(fr, "ICE LOCK", vx + 60 * (1 - e), vy + 40 * (1 - e), -9 * (1 - e), hover=0.7 * (1 - e), scale=1 - 0.8 * e)
        return fr
    gif("04_placed_ripple.gif", 16, g04)
    INDEX.append(("04_placed_ripple.gif", "Defence placed", "the card drops into the socket; a lime ripple; forecast ring settles green", "STICKER + INLAY"))

    # 05 remove a placed defence (sentry off the safehouse)
    b = boxc(sx - 60, sy + 20)

    def g05(t, i):
        off = t > 0.5
        fr = base("setup_h1", deco(forecast={"vault": "disabled", "proxy": "seized", "safe": "disabled"} if off else True), b, "g05%d" % off)
        e = ease(seg(t, 0.1, 0.8))
        pen = V.Pencil(fr, 25)
        pen.arrow([(sx, sy - 10), (sx - 70, sy + 50), (sx - 150, sy + 90)], V.Y_PEN, 6.0, 18, dashed=True, progress=seg(t, 0.1, 0.6))
        fr = pen.composite()
        sd = U.asset_card("SENTRY", "picto_target", 12, 1, ["3 dmg x2", "own node only"], U.GREEN, 61)
        return V.place_sticker(fr, sd, sx - 200 * e, sy + 120 * e, -8 * e, hover=0.6, scale=0.3 + 0.7 * e)
    gif("05_remove_defence.gif", 16, g05)
    INDEX.append(("05_remove_defence.gif", "Remove a defence", "drag the unit off its socket to the tray; the forecast ring re-projects (amber)", "INLAY + PENCIL + STICKER"))

    # 06 move / swap
    b = boxc((fx + rx) / 2 + 40, (fy + ry) / 2 + 20)

    def g06(t, i):
        over = t > 0.6
        fr = base("setup_h1", deco(flash={"relay": "hover"} if over else {}), b, "g06%d" % over)
        pen = V.Pencil(fr, 26)
        pen.arrow([(fx - 10, fy + 10), (fx - 90, fy + 160), (rx + 20, ry - 30)], V.Y_PEN, 6.5, 20, dashed=True, progress=seg(t, 0.0, 0.6))
        pen.circle(rx, ry, 70, 46, V.Y_PEN, 6.0, progress=seg(t, 0.6, 0.95))
        return pen.composite()
    gif("06_move_swap.gif", 16, g06)
    INDEX.append(("06_move_swap.gif", "Move / swap", "drag a placed unit node to node (dashed pencil); dropping on a full slot swaps the two", "INLAY + PENCIL"))

    # 07 forecast change: ring amber -> green, numbers tick
    b = boxc(vx, vy + 40)

    def g07(t, i):
        good = t > 0.45
        fr = base("setup_h1", deco(forecast={"vault": "holds" if good else "disabled", "proxy": "seized"}, t=t), b, "g07%d%d" % (good, i % 4))
        hv = 42 + int(round(3 * seg(t, 0.45, 0.8)))
        return V.put_panel(fr, U.terminal("IF IT RAN NOW", [("kv", "HOME", "50 > %d" % hv, U.PINK), ("kv", "VAULT", "HOLDS" if good else "DISABLED", U.GREEN if good else U.AMBER)],
                                          w=240, accent=U.GREEN if good else U.AMBER), b[0] + 10, b[3] - 100)
    gif("07_forecast_change.gif", 16, g07)
    INDEX.append(("07_forecast_change.gif", "Forecast changes", "dashed ring = projected outcome, re-projects live; terminal numbers count to the new value", "INLAY + TERMINAL"))

    # 08 routes revealed: red pencil draws from each corp entry
    b = (240, 135, 1680, 945)

    def g08(t, i):
        fr = base("setup_h1", deco(entries_incoming=tuple(LY.ENTRIES) if t < 0.5 else (), t=t), b, "g08%d" % (i % 4 if t < 0.5 else 9))
        pen = V.Pencil(fr, 28)
        V.pencil_routes(pen, progress=seg(t, 0.1, 0.85), letters=t > 0.85)
        return pen.composite()
    gif("08_routes_revealed.gif", 18, g08, size=(800, 450))
    INDEX.append(("08_routes_revealed.gif", "Threat routes revealed", "entry sockets pulse; red grease pencil draws each route A/B/C to its target", "INLAY + PENCIL"))

    # 09 decoy preview (setup): the DECOY card over the relay bends route B
    b = boxc((px + rx) / 2 + 120, (py + ry) / 2 - 40, 800, 450)
    old = LY.route_points("r2")
    bent = [LY.ENTRIES["e_west"], tuple(N["proxy"][:2]), tuple(N["relay"][:2])]

    def g09(t, i):
        over = t > 0.3
        fr = base("setup_h1", deco(flash={"relay": "hover"} if over else {}, lure="relay" if over else None, t=t), b, "g09%d%d" % (over, i % 6))
        p_old = V.Pencil(fr, 29)
        p_old.arrow(V.route_screen("r2", old)[2:], V.R_PEN, 6.0, 20)
        fr = p_old.composite(wipe=seg(t, 0.55, 0.85))
        pen = V.Pencil(fr, 30)
        pen.arrow(V.route_screen("r2", old)[:2], V.R_PEN, 6.0, 0)
        pen.arrow(V.route_screen("r2", bent)[1:], V.R_PEN, 6.0, 20, dashed=True, progress=seg(t, 0.35, 0.7))
        ex, ey = P(*LY.ENTRIES["e_west"])
        pen.circle(ex, ey, 44, 29)
        fr = pen.composite()
        e = ease(seg(t, 0, 0.3))
        return card_at(fr, "DECOY", rx + 260 - 80 * e, ry + 120 - 40 * e, 8)
    gif("09_decoy_preview.gif", 20, g09, size=(640, 360))
    INDEX.append(("09_decoy_preview.gif", "Route redirect preview (DECOY)", "only pull assets re-route: the old pencil route wipes, a dashed pencil bend draws to the decoy's node", "INLAY + PENCIL + STICKER"))

    # 10 link frozen (Lockdown Unit, setup)
    b = boxc((fx + cx) / 2, (fy + cy) / 2)

    def g10(t, i):
        amt = seg(t, 0.1, 0.8)
        fr = base("setup_h1", deco(link_states={("core", "firewall"): "dead"} if amt > 0 else {}, frost=("firewall", "core", amt) if amt > 0 else None), b, "g10%d" % int(amt * 10))
        return V.put_panel(fr, U.terminal("LOCKDOWN UNIT", [("t", "FREEZES CORE - FIREWALL FOR THIS RAID", U.ICE)], w=330, accent=U.ICE), b[0] + 10, b[1] + 10)
    gif("10_link_frozen.gif", 14, g10)
    INDEX.append(("10_link_frozen.gif", "Link frozen (setup)", "the busiest link to home frosts over from the node end; nothing routes or shoots across it", "INLAY + TERMINAL"))

    # 11 start defense
    b = boxc(1600, 900)

    def g11(t, i):
        fr = base("setup_h1", deco(), b, "g11")
        sq = 1.0 - 0.12 * math.sin(math.pi * seg(t, 0.2, 0.5)) if t < 0.5 else 1.0
        img = start_button(np.zeros((1, 1, 3)) if False else fr.img, 1700 - b[0], 1010 - b[1], squash=sq)
        fr.img = img
        if t > 0.6:
            fr.img = fr.img * (1 - 0.5 * seg(t, 0.6, 1.0))
        return fr
    gif("11_start_defense.gif", 14, g11)
    INDEX.append(("11_start_defense.gif", "START DEFENSE", "the one sticker button: slap-down squash, then the setup UI peels away", "STICKER"))

    # 12 wave incoming: entry rings + pencil INCOMING writes, holds, wipes
    ex, ey = P(*LY.ENTRIES["e_west"])
    b = boxc(ex + 160, ey - 60)

    def g12(t, i):
        fr = base("setup_h1", deco(entries_incoming=("e_west",), t=(t * 3) % 1, forecast={}), b, "g12%d" % (i % 6))
        pen = V.Pencil(fr, 32)
        pen.circle(ex, ey, 50, 33, progress=seg(t, 0.05, 0.3))
        pen.text("INCOMING", ex + 20, ey - 58, 18, V.R_PEN, 4.2, progress=seg(t, 0.25, 0.5))
        return pen.composite(wipe=seg(t, 0.78, 1.0))
    gif("12_wave_incoming.gif", 20, g12)
    INDEX.append(("12_wave_incoming.gif", "Wave incoming", "the entry socket rings red; pencil INCOMING writes, stays a moment, wipes away", "INLAY + PENCIL"))

    # 13 threat moving
    path = [LY.ENTRIES["e_west"], tuple(N["proxy"][:2])]
    b = boxc((ex + px) / 2 + 20, (ey + py) / 2)

    def g13(t, i):
        (x, y), hd = V.path_point(path, 0.1 + 0.85 * t)
        fr = base("setup_h1", deco(rings=[(x, y, 0.8)], forecast={}), b, None)
        return V.paste_sprite(fr, "INSPECTOR", hd, x, y)
    gif("13_threat_moving.gif", 16, g13)
    INDEX.append(("13_threat_moving.gif", "Threat moving", "corp vehicle on the street with its red ring (lit segments = HP)", "3D + INLAY"))

    # 14 defence fires / hit (railgun on the vault vs a bailiff)
    rail = SPOTS.get("railgun", [94.2, -51, 8.6])
    b = boxc(vx + 60, vy - 10)
    pathb = [(150, -50), (92, -50)]
    rng = np.random.default_rng(3)

    def g14(t, i):
        (x, y), hd = V.path_point(pathb, min(1.0, t * 1.2))
        hp = 1.0 - 0.33 * (t > 0.3) - 0.33 * (t > 0.7)
        fr = base("setup_h1", deco(rings=[(x, y, hp)], forecast={}), b, None)
        fr = V.paste_sprite(fr, "BAILIFF", hd, x, y)
        tx, ty = P(x, y, 4)
        for t0 in (0.3, 0.7):
            if t0 <= t < t0 + 0.12:
                fr = V.tracer(fr, P(*rail), (tx, ty), (200, 245, 255), 4)
            if t0 <= t < t0 + 0.3:
                k = seg(t, t0, t0 + 0.3)
                fr = V.shards(fr, tx, ty - 10, np.random.default_rng(int(t0 * 10)), 24, t=k)
                fr = V.float_num(fr, tx + 26, ty - 40 - 30 * k, "-8", alpha=1 - k)
        return fr
    gif("14_defence_fires.gif", 20, g14)
    INDEX.append(("14_defence_fires.gif", "Defence fires / hit", "tracer, binary 0/1 shards, a rising numeral; the ring loses lit segments", "FLOAT + INLAY"))

    # 15 threat held (ICE LOCK on the firewall) - fix of r19 tile 16
    pth = [tuple(N["proxy"][:2]), tuple(N["firewall"][:2]), tuple(N["core"][:2])]
    b = boxc(fx - 40, fy + 60)

    def g15(t, i):
        if t < 0.3:
            u = 0.42 * seg(t, 0, 0.3)
            held = 0
        elif t < 0.8:
            u = 0.42
            held = 2 if t < 0.55 else 1
        else:
            u = 0.42 + 0.3 * seg(t, 0.8, 1.0)
            held = 0
        (x, y), hd = V.path_point(pth, u)
        fr = base("setup_h1", deco(rings=[(x, y, 0.6, "held" if held else "live")], forecast={}), b, None)
        fr = V.paste_sprite(fr, "INSPECTOR", hd, x, y, tint=(178, 235, 255) if held else None)
        if held:
            X, Y = P(x, y, 8)
            fr = V.float_num(fr, X, Y - 40, "HELD %d" % held, col=(178, 235, 255), size=22)
        return fr
    gif("15_threat_held_ice.gif", 20, g15)
    INDEX.append(("15_threat_held_ice.gif", "Threat held (ICE LOCK)", "on the firewall node the ring freezes into an ice crystal, the unit frosts, HELD 2 > 1, then it moves on", "INLAY + FLOAT"))

    # 16 threat lured (DECOY, playout) - fix of r19 tile 17
    def g16(t, i):
        return lure_frame(t, i)
    gif("16_threat_lured_decoy.gif", 24, g16, size=(800, 450))
    INDEX.append(("16_threat_lured_decoy.gif", "Threat lured (DECOY)", "decoy pylon on RELAY broadcasts; the threat's pencil route; at the proxy the old route wipes and a dashed pencil bend draws to the decoy; the unit turns", "3D + INLAY + PENCIL"))

    # 17 unit destroyed + DOWN wipe
    b = boxc(vx + 60, vy - 10)

    def g17(t, i):
        x, y = 104, -50
        alive = t < 0.3
        fr = base("setup_h1", deco(rings=[(x, y, 0.2 if alive else 0.0, "live" if alive else "down")], forecast={}), b, "g17%d" % alive)
        if t < 0.45:
            fr = V.paste_sprite(fr, "BAILIFF", 2, x, y, alpha=1.0 if alive else 1 - seg(t, 0.3, 0.45))
        tx, ty = P(x, y, 4)
        if 0.2 <= t < 0.32:
            fr = V.tracer(fr, P(*rail), (tx, ty), (200, 245, 255), 4)
        if 0.25 <= t < 0.6:
            fr = V.shards(fr, tx, ty - 6, np.random.default_rng(5), 40, spread=80, t=seg(t, 0.25, 0.6))
        pen = V.Pencil(fr, 37)
        pen.x(tx, ty, 20, progress=seg(t, 0.35, 0.5))
        pen.text("DOWN", tx + 4, ty - 44, 17, V.R_PEN, 4.0, progress=seg(t, 0.45, 0.6))
        return pen.composite(wipe=seg(t, 0.8, 1.0))
    gif("17_unit_destroyed_wipe.gif", 24, g17)
    INDEX.append(("17_unit_destroyed_wipe.gif", "Unit destroyed (DOWN wipes)", "shards, the ring breaks to a grey X; pencil X + DOWN writes, holds, then a cloth wipe clears it", "FLOAT + INLAY + PENCIL"))

    # 18 node damage (health combo)
    b = boxc(sx, sy - 30)

    def g18(t, i):
        hp = 1.0 - 0.15 * int(t * 5)
        fr = base("setup_h1", deco(health={"safe": hp}, forecast={}), b, "g18%d" % int(t * 5))
        if (t * 5) % 1 < 0.4 and t > 0.2:
            X, Y = P(*N["safe"][:2])
            fr = V.float_num(fr, X + 40, Y - 20 - 30 * ((t * 5) % 1), "-3", alpha=1 - ((t * 5) % 1) * 2)
        if t > 0.5:
            fr = V.health_float(fr, "safe", round(hp * 20), 20, col=(212, 255, 0) if hp > 0.66 else (255, 176, 0))
            fr = V.put_panel(fr, U.terminal("HOVER", [("t", "health numbers on hover", (150, 190, 205))], w=210), b[0] + 10, b[1] + 10)
        return fr
    gif("18_node_damage.gif", 20, g18)
    INDEX.append(("18_node_damage.gif", "Node takes damage (health combo)", "the lit part fades north > south with each hit; numbers float above only on hover / always-show", "INLAY + FLOAT"))

    # 19 node disabled + cascade
    b = boxc(px + 100, py + 10)

    def g19(t, i):
        hp = max(0.0, 0.3 - t * 0.8)
        dis = hp <= 0
        surge = dis and t < 0.75
        st = {"proxy": "disabled"} if dis else {}
        hl = {"proxy": hp, "firewall": 1.0 - (0.15 if dis else 0), "relay": 1.0 - (0.15 if dis else 0)}
        ls = {("proxy", "firewall"): "hot", ("relay", "proxy"): "hot"} if surge and i % 2 == 0 else {}
        return base("setup_h1", deco(st=st, health=hl, forecast={}, link_states=ls), b, "g19%d%d%d" % (int(hp * 20), dis, len(ls)))
    gif("19_node_disabled_cascade.gif", 18, g19)
    INDEX.append(("19_node_disabled_cascade.gif", "Node disabled + cascade", "the last lit sliver goes; amber dashed frame; 50% of the excess surges along both links into the neighbours", "INLAY"))

    # 20 node seized + LOST pencil (wipes)
    def g20(t, i):
        seized = t > 0.25
        fr = base("setup_h1", deco(st={"proxy": "seized" if seized else "disabled"}, forecast={}), b, "g20%d" % seized)
        pen = V.Pencil(fr, 40)
        pen.text("LOST", px, py - 60, 22, V.R_PEN, 4.8, progress=seg(t, 0.3, 0.5))
        return pen.composite(wipe=seg(t, 0.8, 1.0))
    gif("20_node_seized.gif", 20, g20)
    INDEX.append(("20_node_seized.gif", "Node seized", "a disabled node hit again: violet corp hatch + corp glyph, links die; pencil LOST writes then wipes", "INLAY + PENCIL"))

    # 21 node lost (report): seized -> burnt
    def g21(t, i):
        return base("setup_h1", deco(st={"proxy": "burnt" if t > 0.4 else "seized"}, forecast={}), b, "g21%d" % (t > 0.4))
    gif("21_node_lost.gif", 10, g21, dur=160)
    INDEX.append(("21_node_lost.gif", "Node lost (after the raid)", "the seized node is removed: burnt socket with embers until reclaimed + reinstalled", "INLAY"))

    # 22 threat reaches home
    b = boxc(cx, cy)
    ph = [tuple(N["firewall"][:2]), tuple(N["core"][:2])]

    def g22(t, i):
        (x, y), hd = V.path_point(ph, 0.35 + 0.65 * min(1.0, t * 1.6))
        hit = t > 0.62
        fr = base("setup_h1", deco(health={"core": 0.82 if hit else 1.0}, forecast={}, rings=[(x, y, 0.5)],
                                    ripple=("core", 13 + 20 * seg(t, 0.62, 1.0), 1.2 * (1 - seg(t, 0.62, 1.0))) if hit else None), b, None)
        fr = V.paste_sprite(fr, "INSPECTOR", hd, x, y)
        return V.put_panel(fr, U.terminal("RAID", [("kv", "HOME", "50 > 41" if hit else "50 / 50", U.PINK)], w=200, accent=U.HARM), b[2] - 220, b[3] - 70)
    gif("22_reaches_home.gif", 18, g22)
    INDEX.append(("22_reaches_home.gif", "Threat reaches home", "CORE's lit part drops from the north, pink pulse; HOME 50 > 41 in the terminal", "INLAY + TERMINAL"))

    # 23 wave cleared
    b = boxc(cx - 100, cy + 40, 800, 450)

    def g23(t, i):
        clr = t > 0.4
        fr = base("setup_h1", deco(entries_incoming=() if clr else ("e_west",), forecast={}, packets=clr, t=(t * 2) % 1,
                                    st={"proxy": "disabled"}, health={"vault": 0.3, "safe": 0.7}), b, "g23%d%d" % (clr, i % 5))
        pen = V.Pencil(fr, 43)
        V.pencil_routes(pen, letters=False)
        fr = pen.composite(wipe=seg(t, 0.4, 0.75))
        if clr:
            fr = V.put_panel(fr, U.terminal("WAVE 1 / 2", [("t", "CLEARED  //  NEXT AT STEP 9", U.GREEN)], w=260, accent=U.GREEN), b[0] + 20, b[1] + 20)
        return fr
    gif("23_wave_cleared.gif", 18, g23, size=(640, 360))
    INDEX.append(("23_wave_cleared.gif", "Wave cleared", "the wave's pencil routes wipe away, entries stop pulsing, packets flow home", "INLAY + PENCIL + TERMINAL"))

    # 24 raid result (post-raid; replaces the in-raid heat escalation)
    def g24(t, i):
        img = result_screen(stamp=seg(t, 0.15, 0.45), rows_k=seg(t, 0.4, 0.95))
        return Frame(img)
    gif("24_raid_result.gif", 18, g24, size=(800, 450))
    INDEX.append(("24_raid_result.gif", "Raid result (CELL HOLDS)", "after the raid: the CELL HOLDS stamp slaps on, the report types out; Heat is settled here (win ±0, loss +5)", "STICKER + TERMINAL"))

    # 25 speed / skip
    b = boxc(960, 900)

    def g25(t, i):
        fr = base("wave_h2", deco(st=WAVE_ST, health=WAVE_HEALTH, forecast={}), b, "g25")
        act = ["1x", "2x", "4x", "SKIP"][min(3, int(t * 4))]
        step = 7 + int(t * 4) * (1 if act != "SKIP" else 0) + (23 if act == "SKIP" else 0)
        return V.put_panel(fr, U.speed_terminal(act, "%02d / 30" % min(30, step)), 745, 1010)
    gif("25_speed_skip.gif", 16, g25, dur=160)
    INDEX.append(("25_speed_skip.gif", "Speed / skip", "a live terminal strip (changes state, so not a sticker); SKIP jumps to the result", "TERMINAL"))

    # 26 home breached
    b = boxc(cx, cy - 20)

    def g26(t, i):
        hp = max(0.0, 0.4 - t)
        st = {"core": "burnt"} if hp <= 0 else {}
        fr = base("setup_h1", deco(st=st, health={"core": hp}, forecast={}), b, "g26%d" % int(hp * 20))
        pen = V.Pencil(fr, 46)
        pen.text("BREACHED", cx + 20, cy - 90, 26, V.R_PEN, 5.5, progress=seg(t, 0.45, 0.8))
        fr = pen.composite()
        if hp <= 0:
            fr = V.put_panel(fr, U.terminal("RAID RESULT", [("t", "HOME 0  //  CAMPAIGN LOST", U.HARM)], w=280, accent=U.HARM), b[2] - 300, b[3] - 70)
        return fr
    gif("26_home_breached.gif", 16, g26)
    INDEX.append(("26_home_breached.gif", "Home breached / lost", "CORE drains to nothing and burns out; pencil BREACHED stays (end state)", "INLAY + PENCIL + TERMINAL"))

    # 27 node health combo (deliverable 4)
    b = boxc(sx, sy - 30, 480, 300)

    def g27(t, i):
        hp = max(0.0, 1.0 - t * 1.15)
        st = {"safe": "disabled"} if hp <= 0 else {}
        fr = base("setup_h1", deco(st=st, health={"safe": hp}, forecast={}), b, "g27%d" % int(hp * 30))
        if 0.3 < t < 0.85 and hp > 0:
            fr = V.health_float(fr, "safe", round(hp * 20), 20, col=(212, 255, 0) if hp > 0.66 else (255, 176, 0) if hp > 0.33 else (255, 68, 51))
        return fr
    frames = gif("27_node_health.gif", 26, g27, dur=110)
    INDEX.append(("27_node_health.gif", "Node health combo", "lit part drains north > south; hover shows numbers; 0 = disabled colour + dashed", "INLAY + FLOAT"))
    frames[0].save(os.path.join(OUT, "node_health.gif"), save_all=True, append_images=frames[1:], duration=110, loop=0, optimize=True)
    write_index()


def lure_frame(t, i, size_box=None):
    """DECOY lure (playout): decoy pylon on the relay; route B (pencil) to the firewall; at the proxy it bends."""
    px, py = P(*N["proxy"][:2])
    rx, ry = P(*N["relay"][:2])
    b = size_box or boxc((px + rx) / 2 + 110, (py + ry) / 2 - 40, 640, 360)
    old = LY.route_points("r2")
    bent = [LY.ENTRIES["e_west"], tuple(N["proxy"][:2]), tuple(N["relay"][:2])]
    if t < 0.4:
        (x, y), hd = V.path_point([LY.ENTRIES["e_west"], tuple(N["proxy"][:2])], 0.15 + 0.85 * seg(t, 0, 0.4) * 0.82)
    elif t < 0.55:
        (x, y), hd = (N["proxy"][0] - 12, N["proxy"][1]), 0
    else:
        (x, y), hd = V.path_point([(N["proxy"][0] - 8, N["proxy"][1]), (N["proxy"][0] - 8, N["proxy"][1] - 22),
                                   (N["relay"][0], N["relay"][1] + 13)], seg(t, 0.55, 1.0))
    fr = base("setup_h1_decoy", deco(lure="relay", t=(t * 3) % 1, forecast={}, rings=[(x, y, 0.8)]), b, None)
    p_old = V.Pencil(fr, 29)
    p_old.arrow(V.route_screen("r2", old)[2:], V.R_PEN, 6.0, 20)
    fr = p_old.composite(wipe=seg(t, 0.42, 0.62))
    pen = V.Pencil(fr, 30)
    pen.arrow(V.route_screen("r2", old)[:2], V.R_PEN, 6.0, 0)
    pen.arrow(V.route_screen("r2", bent)[1:], V.R_PEN, 6.0, 20, dashed=True, progress=seg(t, 0.4, 0.62))
    ex, ey = P(*LY.ENTRIES["e_west"])
    pen.circle(ex, ey, 44, 29)
    fr = pen.composite()
    fr = V.paste_sprite(fr, "INSPECTOR", hd, x, y)
    dx_, dy_ = P(*N["relay"][:2])
    fr = V.put_panel(fr, U.terminal("DECOY", [("t", "PULL 3 on RELAY", U.VIOLET)], w=180, accent=U.VIOLET), b[2] - 190, b[3] - 70)
    return fr


def decoy_strip():
    cv = np.zeros((H, W, 3), np.float32) + BG
    cv = title(cv, "THREAT LURED", "DECOY (pull 3) ON THE RELAY  //  1 the decoy on its node  2 the threat on its pencil route  3 the route bends to the decoy  (gif: interactions_gifs/16)")
    for k, (t, cap) in enumerate(((0.32, "1  DECOY ON THE RELAY + THE ORIGINAL ROUTE"), (0.5, "2  AT THE PROXY: OLD ROUTE WIPES, DASHED BEND"), (0.85, "3  THE UNIT FOLLOWS THE BEND TO THE DECOY"))):
        fr = lure_frame(t, 0)
        im = topil(fr).resize((600, 338), Image.LANCZOS)
        cv[200:538, 40 + k * 620:640 + k * 620] = np.asarray(im, np.float32) / 255
        cv = label(cv, 40 + k * 620, 550, cap, 17, (230, 236, 245), font=SL.ANTON)
    notes = ["True to the rules: only DECOY / HONEYPOT (decoy_pull) change a threat's target (raid_resolver._target_of);",
             "the strongest pull wins and the threat routes to that node by next_hop. Guns never re-route.",
             "The bend is drawn the moment the threat re-targets; the abandoned route segment is wiped, not left to clutter."]
    for k, t in enumerate(notes):
        cv = label(cv, 40, 640 + k * 26, t, 15, (200, 210, 225))
    return cv


INDEX = []


def write_index():
    lines = ["# Round 20 interaction gifs", "", "Every interaction / state that changes, as a loop (<= 2 MB each). Medium: INLAY = street-plane decal, "
             "PENCIL = grease pencil (plans + static states, wipes after a beat), STICKER = static objects only, TERMINAL = C screens, FLOAT = diegetic hit/health floats.",
             "", "| gif | interaction | feedback | medium |", "|---|---|---|---|"]
    for f, t, d, m in INDEX:
        lines.append("| [%s](%s) | %s | %s | %s |" % (f, f, t, d, m))
    lines += ["| [heat_spotlights.gif](../../round19_raid/heat_spotlights.gif) | Spotlight: EXPOSED (locked, round 19) | the spotlit node is exposed (proposal for the GDD) | 3D + INLAY |", "",
              "Removed from round 19: the in-raid Heat escalation state. Heat never changes during a raid; it is settled on the result screen (24).", ""]
    open(os.path.join(GIFS, "index.md"), "w", encoding="utf-8").write("\n".join(lines))
    # contact index image: first meaningful frame of each gif
    names = [f for f, *_ in INDEX]
    tw, th = 300, 169
    cols = 6
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 10) + 10, rows * (th + 26) + 60), (10, 9, 16))
    d = ImageDraw.Draw(sheet)
    d.text((12, 14), "ROUND 20  INTERACTION GIFS (index.md)", font=U.F(SL.ANTON, 26), fill=(255, 222, 30))
    for k, n in enumerate(names):
        fr = GIF_FRAMES[n][len(GIF_FRAMES[n]) * 2 // 3].convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = 10 + (k % cols) * (tw + 10), 54 + (k // cols) * (th + 26)
        sheet.paste(fr, (x, y))
        d.text((x + 2, y + th + 4), n, font=U.F(SL.MONO, 12), fill=(92, 225, 255))
    sheet.save(os.path.join(GIFS, "index.jpg"), quality=88)
    print("saved index")


def contact():
    names = ["raid_setup_night.png", "raid_wave_night.png", "raid_result.png", "node_health.png", "threat_lured.png", "panel_mediums_v2.png",
             "interactions_gifs/index.jpg"]
    tw, th = 620, 349
    sheet = Image.new("RGB", (3 * (tw + 10) + 10, 3 * (th + 26) + 70), (10, 9, 16))
    d = ImageDraw.Draw(sheet)
    d.text((14, 16), "ROUND 20  RAID UI: PENCIL ROUTES, WIPES, HEALTH COMBO, GIFS, RESULT, PANEL MEDIUMS v2", font=U.F(SL.ANTON, 28), fill=(255, 222, 30))
    for k, n in enumerate(names):
        im = Image.open(os.path.join(OUT, n)).convert("RGB")
        im.thumbnail((tw, th), Image.LANCZOS)
        x, y = 10 + (k % 3) * (tw + 10), 64 + (k // 3) * (th + 26)
        sheet.paste(im, (x, y))
        d.text((x + 4, y + th + 4), n, font=U.F(SL.MONO, 14), fill=(92, 225, 255))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=88)
    print("saved contact_sheet.jpg")


if __name__ == "__main__":
    which = sys.argv[1:] or ["setup", "wave", "result", "health", "decoy", "panels", "gifs", "contact"]
    if "setup" in which:
        save(setup_screen("mixed"), "raid_setup_night.png")
    if "wave" in which:
        save(wave_screen(), "raid_wave_night.png")
    if "result" in which:
        save(result_screen(), "raid_result.png")
    if "health" in which:
        save(health_strip(), "node_health.png")
    if "decoy" in which:
        save(decoy_strip(), "threat_lured.png")
    if "panels" in which:
        save(panel_mediums(), "panel_mediums_v2.png")
    if "gifs" in which:
        build_gifs()
    if "contact" in which:
        contact()
