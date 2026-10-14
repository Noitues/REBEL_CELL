"""Round 19 raid: every deliverable frame / sheet.

python screens19.py [name ...]   names: setup_night setup_day wave panels key live link world buildings heat gif
                                        vehicles interactions contact (default: all)
Inputs: ../scratch/bl (run_blender.py + vehicles.py). Outputs: ../*.png, ../heat_spotlights.gif, ../contact_sheet.jpg
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as LY  # noqa: E402
import finish19 as FN  # noqa: E402
import netdecal19 as ND  # noqa: E402
import ui19 as U  # noqa: E402

OUT = os.path.dirname(HERE)
SL = U.SL
W, H = LY.W, LY.H
BG = np.array([0.03, 0.028, 0.05], np.float32)


def P(x, y, z=0.0):
    p = LY.project(x, y, z)
    return p[0], p[1]


def save(img, name):
    Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(os.path.join(OUT, name), optimize=True)
    print("saved", name, flush=True)


def canvas():
    return np.zeros((H, W, 3), np.float32) + BG


def paste(cv, img, x, y, size=None):
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    if size:
        im = im.resize(size, Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255
    hh, ww = min(a.shape[0], cv.shape[0] - y), min(a.shape[1], cv.shape[1] - x)
    cv[y:y + hh, x:x + ww] = a[:hh, :ww]
    return cv


def crop(img, box, size=None):
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).crop(box)
    if size:
        im = im.resize(size, Image.LANCZOS)
    return np.asarray(im, np.float32) / 255


def label(cv, x, y, text, size=15, col=(190, 225, 240), font=None, anchor="la"):
    im = Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.text((x, y), text, font=U.F(font or SL.MONO, size), fill=col, anchor=anchor)
    return np.asarray(im, np.float32) / 255


def title(img, big, sub, col=None, x=40, y=24, gloss_k=0.22):
    sd = U.word_sticker([big], 50, [col or U.FILL_YELLOW], seed=11, border=14, gloss_k=gloss_k)
    w = sd["img"].size[0] / U.S
    img = U.place(img, sd, x + w / 2 - 20, y + 38, angle=-1.5)
    return label(img, x + 6, y + 82, sub, 15, U.CYAN)


# ------------------------------------------------------------------ the state of the setup example (true to GDD 7)
NODE_ROWS = [("relay", "RELAY", "holds", "15/15", "-"), ("firewall", "FIREWALL RELAY", "holds", "30/30", "TURRET (built in) + ICE LOCK"),
             ("vault", "VAULT TERMINAL", "disabled", "20/20", "RAILGUN"), ("proxy", "PROXY RELAY", "seized", "15/15", "-"),
             ("safe", "SAFEHOUSE", "holds", "20/20", "SENTRY"), ("core", "CORE (home)", "home", "50/50", "TURRET")]
GLYPH = {"relay": "picto_all_targets", "firewall": "slice_firewall", "vault": "placeholder_vault", "proxy": "placeholder_spoof",
         "safe": "placeholder_key", "core": "picto_hp"}
OUT_COL = {"holds": U.GREEN, "disabled": U.AMBER, "seized": U.HARM, "home": U.PINK}


def rows_nodes():
    rows = [("h", "YOUR NODES  // IF IT RAN NOW")]
    for k, nm, st, integ, assets in NODE_ROWS:
        chip = {"holds": "HOLDS", "disabled": "DISABLED", "seized": "SEIZED", "home": "HOME -8"}[st]
        rows.append(("node", GLYPH[k], nm, chip, OUT_COL[st], "INT %s  %s" % (integ, assets)))
    return rows


def rows_raid():
    return [("h", "RAID INCOMING"), ("big", "COMPLIANCE SWEEP", (230, 240, 255)), ("t", "HALCYON CIVIC  //  HEAT 50 RAID", U.HALCYON),
            ("sep",), ("kv", "HOME", "50 > 42", U.PINK), ("kv", "DISABLED", "1", U.AMBER), ("kv", "SEIZED", "1", U.HARM),
            ("kv", "HOLD", "3", U.GREEN), ("sep",), ("kv", "ENTRY SITES", "3", (190, 225, 240)), ("kv", "WAVES", "1  (step 1)", (190, 225, 240)),
            ("kv", "FROZEN LINKS", "0", (190, 225, 240))]


def rows_intel():
    return [("h", "THREAT INTEL"), ("t", "6 THREATS  //  STRENGTH +52% (HEAT)", U.HALCYON),
            ("route", "A", "BAILIFF  +  COURIER", "> weakest node  /  > top value x2"),
            ("route", "B", "HAULER  +  INSPECTOR", "> weakest node  /  > top value x2"),
            ("route", "C", "CUSTOMS  +  LANDER", "seals link behind / drops in x2")]


# ------------------------------------------------------------------ shared drawing of the setup example
def setup_decor(extra=None, forecast=True, link_states=None, statuses=None, exposed=(), routes=("r1", "r2", "r3"), hud=False,
                integ=None, packets=False, t=0.0, entries_incoming=(), skip=()):
    def deco(net):
        ND.setup_state(net, forecast=forecast, link_states=link_states, statuses=statuses, exposed=exposed, routes=routes,
                       hud=hud, integ=integ, packets=packets, t=t, entries_incoming=entries_incoming, skip=skip)
        if extra:
            extra(net)
    return deco


def tray(img, skip=None, y=985, x0=560, gloss_sweep=None):
    x = x0
    for i, (nm, gl, hp, cp, ds, col) in enumerate(U.TRAY):
        if nm == skip:
            x += 162
            continue
        sd = U.asset_card(nm, gl, hp, cp, ds, col, 50 + i, gloss_k=1.0 if nm == gloss_sweep else 0.22)
        img = U.place(img, sd, x, y, angle=[-2, 1.5, -1, 2, -1.5, 1][i])
        x += 162
    img = U.put_panel(img, U.terminal("DEFENCE LOADOUT  ARMORY 5/6", [("t", "drag a card onto a node socket", (150, 190, 205))], w=300), x0 - 420, y - 40)
    return img


def start_button(img, x=1700, y=1010):
    sd = U.word_sticker(["START DEFENSE"], 40, [U.FILL_PINK], seed=21, border=13)
    return U.place(img, sd, x, y, angle=-2)


def routes_pencil(L, letters=True):
    for i, rid in enumerate(("r1", "r2", "r3")):
        e = LY.pt(LY.ROUTES[rid][0])
        ex, ey = P(*e)
        U.pen_circle(L, ex, ey, 44, 29, U.R_PEN, 6.0)
        if letters:
            lx, ly = ex + (-60 if ex > 960 else 60), ey - 36
            U.pen_text(L, "ABC"[i], lx, ly, 30, U.R_PEN, 5.5)


def setup_frame(mode="night"):
    vx, vy = LY.NODES["vault"][:2]

    def hover(net):   # the ICE LOCK card hovers over the vault socket: white frame + live forecast preview
        net.pad("vault", "holds", integ=1.0, forecast="holds", flash="hover")
    img = FN.finish("setup_h1", mode, decorate=setup_decor(extra=hover, skip=("vault",)), seed=1)
    L = U.pencil_layer(1901)
    routes_pencil(L)
    px, py = P(vx, vy)
    U.pen_circle(L, px, py, 76, 50, U.Y_PEN, 7.0, 1.2)
    U.pen_arrow(L, [(1345, 600), (1330, 520), (1262, 462)], U.Y_PEN, 7.0, 20)
    img = U.pencil_composite(img, L)
    img = title(img, "RAID SETUP", "03 CELL DEFENSE  //  COMPLIANCE SWEEP  //  DRAG DEFENCES ONTO NODE SOCKETS")
    img = U.put_panel(img, U.terminal("YOUR NODES", rows_nodes()[1:], w=330), 22, 150)
    img = U.put_panel(img, U.terminal("RAID INCOMING", rows_raid()[1:], w=300, accent=U.HARM), 1600, 120)
    img = U.put_panel(img, U.terminal("THREAT INTEL", rows_intel()[1:], w=330, accent=U.HALCYON), 22, 448)
    img = U.put_panel(img, U.terminal("IF PLACED", [("t", "ICE LOCK > VAULT TERMINAL", (190, 225, 240)), ("kv", "VAULT", "DISABLED > HOLDS", U.GREEN),
                                                    ("kv", "HOME", "42 > 45", U.PINK)], w=300, accent=U.GREEN), 1600, 520)
    img = tray(img, skip="ICE LOCK")
    sd = U.asset_card(*U.TRAY[2][:5], U.TRAY[2][5], 52, gloss_k=1.0)   # the one sticker showing the sweep
    img = U.place(img, sd, 1395, 660, angle=-9, hover=0.7)
    return start_button(img)


# ------------------------------------------------------------------ wave (in progress)
WAVE_INTEG = {"core": 1.0, "firewall": 0.9, "relay": 1.0, "safe": 0.7, "vault": 0.3, "proxy": 0.0}
WAVE_ST = {"core": "home", "firewall": "holds", "relay": "holds", "safe": "damaged", "vault": "damaged", "proxy": "disabled"}


def wave_spots():
    sc = json.load(open(os.path.join(FN.SRC, "wave_h2_scene.json")))
    return {k: tuple(v) for k, v in sc["spots"].items()}


THREAT_HP = {"bailiff": (4, 12), "hauler": (9, 15), "inspector": (3, 6), "customs": (5, 8), "lander": (10, 10)}


def wave_decor(hud=False, rings=True, extra=None, t=0.3):
    sp = wave_spots()

    def deco(net):
        ND.setup_state(net, forecast=False, statuses=WAVE_ST, integ=WAVE_INTEG, packets=True, t=t, hud=hud,
                       entries_incoming=("e_west",))
        if rings:
            for k, hp in (("bailiff", 0.35), ("hauler", 0.6), ("inspector", 0.5), ("customs", 0.6), ("lander", 1.0)):
                net.threat_ring(sp[k][0], sp[k][1], hp, txt=("%d/%d" % THREAT_HP[k]) if hud else None)
            net.threat_ring(sp["courier"][0], sp["courier"][1], 0.0, "down")
        if extra:
            extra(net)
    return deco


def feed_terminal(w=330):
    rows = [("t", "07  RAILGUN > BAILIFF        -8", U.CYAN), ("t", "07  FLAK x3 > HAULER          -6", U.AMBER),
            ("t", "07  FW TURRET > INSPECTOR    -3", U.CYAN), ("t", "06  COURIER DESTROYED", U.GREEN),
            ("t", "06  PROXY DISABLED (HAULER)", U.AMBER), ("t", "06  LANDER DROPS (SOUTH)", U.HARM),
            ("t", "05  CUSTOMS SEALS LINK S2", U.HARM), ("t", "05  VAULT HIT  -6", U.AMBER)]
    return U.terminal("LIVE RAID FEED", rows, w=w)


def wave_frame():
    sp = wave_spots()
    img = FN.finish("wave_h2", "night", decorate=wave_decor(), seed=3)
    rng = np.random.default_rng(7)
    for k, txt in (("bailiff", "-8"), ("hauler", "-6"), ("inspector", "-3")):
        x, y = P(*sp[k][:2], sp[k][2])
        img = U.shards(img, x, y - 10, rng, n=22)
        img = U.float_number(img, x + 26, y - 44, txt, size=30)
    L = U.pencil_layer(1902)
    cx, cy = P(*sp["courier"][:2], sp["courier"][2])
    U.pen_x(L, cx, cy, 20)
    U.pen_text(L, "DOWN", cx + 4, cy - 44, 17, U.R_PEN, 4.0)
    ex, ey = P(*LY.ENTRIES["e_west"])
    U.pen_circle(L, ex, ey, 50, 33, U.R_PEN)
    U.pen_text(L, "INCOMING", ex + 20, ey - 58, 18, U.R_PEN, 4.2)
    img = U.pencil_composite(img, L)
    img = title(img, "RAID IN PROGRESS", "03 CELL DEFENSE  //  COMPLIANCE SWEEP  //  WAVE 1 OF 2  //  HEAT 52", col=U.FILL_RED)
    img = U.put_panel(img, feed_terminal(), 22, 150)
    img = U.put_panel(img, U.terminal("RAID", [("kv", "HOME", "50 / 50", U.PINK), ("kv", "THREATS LEFT", "5 / 6", U.HARM),
                                               ("kv", "NEXT WAVE", "STEP 9  (WEST)", U.HARM), ("bar", "HEAT 52", 0.52, U.HARM)], w=300, accent=U.HARM), 1600, 120)
    img = U.put_panel(img, U.speed_terminal(), 745, 1010)
    return img


# ------------------------------------------------------------------ panel mediums
def panel_mediums():
    base = FN.finish("setup_h1", "night", decorate=setup_decor(), seed=1)
    cv = base * 0.45
    cv = title(cv, "PANEL MEDIUMS", "NODE SUMMARY / RAID INCOMING / THREAT INTEL  //  SAME CONTENT, THREE MEDIUMS  //  STICKERS ARE NOT USED FOR CHANGING INFO")
    xs = [40, 680, 1320]
    names = ["A  CRT TERMINAL  (C screens & data)  - recommended", "B  CASE FILE UNDER GLASS", "C  PROJECTED HOLO READOUT"]
    for i in range(3):
        x = xs[i]
        cv = label(cv, x, 128, names[i], 16, [U.CYAN, (233, 223, 198), (120, 230, 255)][i])
        if i == 0:
            p1, p2, p3 = (U.terminal("YOUR NODES", rows_nodes()[1:], w=290), U.terminal("RAID INCOMING", rows_raid()[1:5] + rows_raid()[5:9], w=270, accent=U.HARM),
                          U.terminal("THREAT INTEL", rows_intel()[1:], w=300, accent=U.HALCYON))
        elif i == 1:
            p1, p2, p3 = (U.dossier("YOUR NODES", rows_nodes()[1:], w=270), U.dossier("RAID INCOMING", rows_raid()[1:5] + rows_raid()[5:9], w=250, stamp="INCOMING"),
                          U.dossier("THREAT INTEL", rows_intel()[1:], w=290))
        else:
            p1, p2, p3 = (U.holo("YOUR NODES", rows_nodes()[1:], w=290), U.holo("RAID INCOMING", rows_raid()[1:5] + rows_raid()[5:9], w=270, col=(255, 120, 110)),
                          U.holo("THREAT INTEL", rows_intel()[1:], w=300, col=(170, 150, 255)))
        cv = U.put_panel(cv, p1, x, 160)
        cv = U.put_panel(cv, p2, x + 300 if i != 1 else x + 300, 160)
        cv = U.put_panel(cv, p3, x, 160 + p1["img"].size[1] + 16)
    notes = [("A", "same glass + mono + scanline language as the combat C screens; glows into the map; cheapest to animate (type-on, cursor)."),
             ("B", "tactile and noir; reads as 'intel on the Cell's desk'; must stay off the map's centre (opaque paper)."),
             ("C", "diegetic: floats over the city with its emitter; weakest contrast over bright neon, chromatic fringe costs legibility.")]
    for i, (k, t) in enumerate(notes):
        cv = label(cv, 40, 1000 + i * 24, "%s  %s" % (k, t), 14, (200, 210, 225))
    return cv


# ------------------------------------------------------------------ node status key (synthetic street plane)
def synth_pos(cx, cy, w, h, ppm):
    r, u, f = LY.cam_basis()
    jj, ii = np.mgrid[0:h, 0:w].astype(np.float32)
    xc = (ii - w / 2) / ppm
    yc = -(jj - h / 2) / ppm
    t = -(u[2] * yc) / f[2]
    X = cx + r[0] * xc + u[0] * yc + f[0] * t
    Y = cy + r[1] * xc + u[1] * yc + f[1] * t
    sw = 8.5
    street = (np.abs(X - cx) < sw) | (np.abs(Y - cy) < sw)
    Z = np.where(street, 0.0, 0.35).astype(np.float32)
    return np.stack([X, Y, Z], -1)


def key_tile(fn, w=300, h=230, key="relay", ppm=6.2, link=True, mode="night"):
    n = LY.NODES[key]
    pos = synth_pos(n[0], n[1], w, h, ppm)
    net = ND.Net(pos, mode=mode)
    if link:
        net.link("relay", "core", "ok" if fn.__name__ != "dead" else "dead")
    fn(net)
    em, dk = net.result()
    Z = pos[..., 2]
    rng = np.random.default_rng(3)
    base = np.where(Z[..., None] < 0.1, np.array([0.055, 0.05, 0.075], np.float32), np.array([0.11, 0.10, 0.14], np.float32))
    base = base * (0.9 + 0.2 * rng.random((h, w, 1)).astype(np.float32))
    img = base * dk[..., None] + em * 0.75
    gl = np.asarray(Image.fromarray((np.clip(em, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
    return np.clip(img + gl * 0.6, 0, 1)


def node_status_key():
    cv = canvas()
    cv = title(cv, "NODE STATUS KEY", "NO TAGS: TYPE = SOCKET GLYPH  //  STATUS = FRAME COLOUR + PATTERN  //  INTEGRITY = INNER TRACK  //  FORECAST = DASHED RING")
    types = [("relay", "RELAY"), ("firewall", "FIREWALL RELAY"), ("vault", "VAULT TERMINAL"), ("proxy", "PROXY RELAY"),
             ("safe", "SAFEHOUSE"), ("core", "CORE (home)")]
    tw, th = 300, 200
    y0 = 140
    cv = label(cv, 40, y0 - 4, "TYPE (round 17 glyphs on the socket)", 15, U.CYAN)
    for i, (k, nm) in enumerate(types):
        st = "home" if k == "core" else "holds"
        t = key_tile(lambda n_, k=k, st=st: n_.pad(k, st), tw, th, key=k)
        cv = paste(cv, t, 40 + i * 310, y0 + 20)
        cv = label(cv, 48 + i * 310, y0 + 24 + th, nm, 14)
    states = [
        ("HOLDS", "solid green frame, pins lit, track full", lambda n: n.pad("relay", "holds", 1.0)),
        ("DAMAGED 60%", "track drains clockwise from the notch; cracks", lambda n: n.pad("relay", "damaged", 0.6)),
        ("CRITICAL 25%", "track turns red under 1/3", lambda n: n.pad("relay", "damaged", 0.25)),
        ("DISABLED", "dashed amber frame, pins dark, glyph flickers", lambda n: n.pad("relay", "disabled", 0.0)),
        ("SEIZED", "violet corp hatch + corp mark, link dead", lambda n: n.pad("relay", "seized", 0.0)),
        ("TAKEN (node removed)", "burnt socket, embers; reclaim + reinstall", lambda n: n.pad("relay", "burnt", 0.0)),
        ("FORECAST: DISABLED", "setup: dashed ring = projected outcome", lambda n: n.pad("relay", "holds", 1.0, forecast="disabled")),
        ("FORECAST: SEIZED", "red dashed ring", lambda n: n.pad("relay", "holds", 1.0, forecast="seized")),
        ("DRAG: VALID", "white frame while a card hovers", lambda n: n.pad("relay", "holds", 1.0, flash="hover")),
        ("DRAG: INVALID", "red frame + X: no slot / seized", lambda n: n.pad("relay", "seized", 0.0, flash="invalid")),
        ("PLACED", "a ripple in the link colour", lambda n: n.pad("relay", "holds", 1.0, flash="place")),
        ("EXPOSED (PROPOSAL)", "spotlit: white hazard ticks", lambda n: (n.pad("relay", "holds", 1.0, exposed=True), n.pool_ring(-60, -50, 12.5, ND.WHITE, 0.7))),
    ]
    y1 = y0 + th + 60
    cv = label(cv, 40, y1 - 4, "STATUS / INTEGRITY / FORECAST / DRAG", 15, U.CYAN)
    tw2, th2 = 300, 170
    for i, (nm, desc, fn) in enumerate(states):
        r, c = divmod(i, 6)
        x, y = 40 + c * 310, y1 + 20 + r * (th2 + 64)
        fn.__name__ = "dead" if nm == "SEIZED" else "f"
        t = key_tile(fn, tw2, th2, key="relay", ppm=5.6)
        cv = paste(cv, t, x, y)
        cv = label(cv, x + 8, y + th2 + 4, nm, 14, (230, 236, 245))
        cv = label(cv, x + 8, y + th2 + 22, desc, 11, (150, 165, 185))
    cv = label(cv, 40, 1050, "Socket = the tactical node on the street. Its machine lives in the building behind it (riser traces). Threats: red ring under each unit, lit segments = HP.", 13, (170, 180, 200))
    return cv


# ------------------------------------------------------------------ live info options
def live_info_options():
    sp = wave_spots()
    box = (640, 250, 1240, 890)
    cw, ch = 600, 640
    cv = canvas()
    cv = title(cv, "LIVE INFO", "FEED, SPEED, DAMAGE, UNIT HP, NODE INTEGRITY  //  NEVER STICKERS  //  THREE LIVE MEDIUMS")
    rng = np.random.default_rng(5)
    xs = [40, 660, 1280]
    caps = [("L1  STREET HUD", "numbers projected flat on the street beside each socket and under each threat; feed + speed in the CRT terminal"),
            ("L2  THE INLAY IS THE GAUGE", "no numbers on the map: socket track drains, threat ring segments go dark, hits surge along the traces"),
            ("L3  DIEGETIC FLOATS", "binary shards burst from every hit (combat language), numerals rise and fade, thin holo bars over units")]
    for i in range(3):
        if i == 0:
            def extra(net):
                for k, hp, mx in (("bailiff", 4, 12), ("hauler", 9, 15), ("inspector", 3, 6), ("customs", 5, 8)):
                    pass
            img = FN.finish("wave_h2", "night", decorate=wave_decor(hud=True), seed=3)
            for k, txt in (("bailiff", "-8"), ("hauler", "-6"), ("inspector", "-3")):
                x, y = P(*sp[k][:2], 0)
                img = U.float_number(img, x, y + 30, txt, size=22, col=(255, 110, 90))
        elif i == 1:
            img = FN.finish("wave_h2", "night", decorate=wave_decor(), seed=3)
        else:
            img = FN.finish("wave_h2", "night", decorate=wave_decor(rings=False), seed=3)
            for k, txt, hp in (("bailiff", "-8", 0.35), ("hauler", "-6", 0.6), ("inspector", "-3", 0.5), ("customs", "", 0.6)):
                x, y = P(*sp[k][:2], sp[k][2])
                if txt:
                    img = U.shards(img, x, y - 8, rng, n=30, spread=70)
                    img = U.float_number(img, x + 28, y - 50, txt, size=30)
                img = U.holo_bar(img, x, y - 26, hp)
            for k, frac in WAVE_INTEG.items():
                if k == "proxy":
                    continue
                x, y = P(*LY.NODES[k][:2])
                img = U.holo_bar(img, x, y - 70, frac, col=(212, 255, 0) if frac > 0.66 else (255, 176, 0) if frac > 0.33 else (255, 68, 51), w=60)
        c = crop(img, box, (cw, ch))
        cv = paste(cv, c, xs[i], 150)
        cv = label(cv, xs[i], 150 + ch + 10, caps[i][0], 20, U.LIME, font=SL.ANTON)
        cv = label(cv, xs[i], 150 + ch + 44, caps[i][1][:78], 12, (190, 200, 215))
        cv = label(cv, xs[i], 150 + ch + 62, caps[i][1][78:], 12, (190, 200, 215))
        # the feed + speed in that column's medium
        if i == 0:
            cv = U.put_panel(cv, U.terminal("FEED", [("t", "07 RAILGUN > BAILIFF -8", U.CYAN), ("t", "07 FLAK x3 > HAULER -6", U.AMBER)], w=300), xs[i], 870)
            cv = U.put_panel(cv, U.speed_terminal(), xs[i], 1000)
        elif i == 1:
            cv = U.put_panel(cv, U.terminal("TICKER", [("t", "07 RAILGUN > BAILIFF  //  FLAK > HAULER", U.CYAN)], w=420), xs[i], 900)
            cv = U.put_panel(cv, U.speed_terminal("1x"), xs[i], 1000)
        else:
            cv = U.put_panel(cv, U.holo("FEED", [("t", "07 RAILGUN > BAILIFF -8", (220, 250, 255)), ("t", "07 FLAK x3 > HAULER -6", (220, 250, 255))], w=300), xs[i] + 300, 862)
            cv = U.put_panel(cv, U.speed_terminal("4x"), xs[i], 1000)
    return cv


# ------------------------------------------------------------------ link colour
def link_colour():
    cv = canvas()
    cv = title(cv, "LINK COLOUR", "STYLE_GUIDE cell_turf #D4FF00 (lime)  vs  round 18 net_cyan #5CE1FF  //  same frame, only the Cell's links + risers change")
    box = (420, 240, 1500, 900)
    cw, ch = 900, int(900 * (box[3] - box[1]) / (box[2] - box[0]))
    for i, (tag, link, nm) in enumerate((("setup_h1", "lime", "LIME  cell_turf  (recommended)"), ("setup_h1_cyan", "cyan", "CYAN  net_cyan  (round 18)"))):
        img = FN.finish(tag, "night", decorate=setup_decor(), link=link, seed=1)
        cv = paste(cv, crop(img, box, (cw, ch)), 40 + i * 940, 150)
        cv = label(cv, 40 + i * 940, 160 + ch, nm, 22, U.LIME if link == "lime" else U.CYAN, font=SL.ANTON)
    notes = ["Lime separates the Cell's network from the city's neutral cyan (holo ads, windows, cool neon) and from net_cyan UI chrome.",
             "Cyan reads as 'the net' but merges with the defence tracers, ICE and the CRT panels; status greens stay distinct in both.",
             "Day: lime stays legible on grey asphalt; cyan washes out (see raid_setup_day.png, lime)."]
    for k, t in enumerate(notes):
        cv = label(cv, 40, 970 + k * 26, t, 15, (200, 210, 225))
    return cv


# ------------------------------------------------------------------ world detail
def world_detail():
    cv = canvas()
    cv = title(cv, "WORLD DETAIL", "ROUND 18 facets (left)  vs  ROUND 19: ~2.6 m triangulated facets + ledges, dark glass, shopfronts, awnings, blade signs, AC, pipes, roof clutter")
    for i, tag in enumerate(("wd_old", "wd_new")):
        img = FN.finish(tag, "night", decorate=setup_decor(), seed=1, tilt=0.4)
        c = crop(img, (360, 120, 1560, 1000), (900, 660))
        cv = paste(cv, c, 40 + i * 940, 150)
        cv = label(cv, 40 + i * 940, 818, "ROUND 18" if i == 0 else "ROUND 19", 22, (230, 236, 245), font=SL.ANTON)
        dimg = FN.finish(tag, "day", decorate=setup_decor(), seed=1, tilt=0.0)
        z = crop(dimg, (700, 260, 1140, 508), (440, 248))
        cv = paste(cv, z, 40 + i * 940 + 460, 820)
        cv = label(cv, 40 + i * 940 + 460, 1068, "day, x2 crop", 11, (150, 165, 185))
    return cv


# ------------------------------------------------------------------ building nodes
def building_nodes():
    cv = canvas()
    cv = title(cv, "NODES IN BUILDINGS", "THE SOCKET STAYS ON THE STREET (tactical node); ITS MACHINE LIVES IN THE CORNER BUILDING, WIRED BY AN INLAY RISER")
    designs = [("bn_vault", "1  SERVER ROOM", "vault / firewall: racks lit behind a ground-floor glass front; the riser runs into the sill"),
               ("bn_relay", "2  ROOFTOP DISH", "relay / proxy: the riser climbs the facade corner to a dish on the roof"),
               ("bn_safe", "3  SHOPFRONT", "safehouse: the socket's riser ends at a half-open shutter under the glyph sign")]
    for i, (tag, nm, desc) in enumerate(designs):
        img = FN.finish(tag, "night", decorate=setup_decor(), seed=1, tilt=0.0, rain=False)
        c = crop(img, (330, 30, 1590, 1050), (600, 486))
        cv = paste(cv, c, 40 + i * 620, 150)
        day = FN.finish(tag, "day", decorate=setup_decor(), seed=1, tilt=0.0)
        cv = paste(cv, crop(day, (330, 30, 1590, 1050), (300, 243)), 40 + i * 620, 650)
        cv = label(cv, 350 + i * 620, 650, nm, 22, U.LIME, font=SL.ANTON)
        words = desc.split(" ")
        line, yy = "", 690
        for wd in words:
            if len(line) + len(wd) > 34:
                cv = label(cv, 350 + i * 620, yy, line, 13, (200, 210, 225))
                line, yy = "", yy + 20
            line += wd + " "
        cv = label(cv, 350 + i * 620, yy, line, 13, (200, 210, 225))
    cv = label(cv, 40, 920, "At map zoom the three read as: a lit window, a dish on a roof, a glowing sign - each tied to its socket by the lime riser.", 15, (200, 210, 225))
    cv = label(cv, 40, 946, "States carry up the riser: disabled = riser dims + building lights flicker; seized = riser dead, the sign switches to the corp mark.", 15, (200, 210, 225))
    full = FN.finish("setup_h1", "night", decorate=setup_decor(), seed=1)
    cv = paste(cv, crop(full, (420, 330, 1500, 840), (360, 170)), 1530, 900)
    cv = label(cv, 1530, 880, "at map zoom", 12, (150, 165, 185))
    return cv


# ------------------------------------------------------------------ heat
HEAT_TXT = {1: ("HEAT 25+  WATCHED", ["1 wave, 1 route", "1 chopper circling the edge, light on the street", "3 drones, no spotlights"]),
            2: ("HEAT 50+  HUNTED", ["stronger threats (+integrity), 2 routes", "a chopper circles the VAULT: exposed*", "drones' mini spots, corner strobes"]),
            3: ("HEAT 75+  MANHUNT", ["2 waves, 3 routes", "choppers on VAULT, PROXY, SAFE; gunship on CORE*", "14 drones, overlapping mini spots"])}
HEAT_ROUTES = {1: ("r1",), 2: ("r1", "r2"), 3: ("r1", "r2", "r3")}
HEAT_EXPOSED = {1: (), 2: ("vault",), 3: ("vault", "proxy", "safe", "core")}


def heat_levels_v2():
    cv = canvas()
    cv = title(cv, "HEAT LEVELS", "MORE HEAT = STRONGER WAVES + MORE ROUTES (GDD 4.4 / 7)  //  *SPOTLIT NODE IS EXPOSED: PROPOSAL, NEEDS A GDD DECISION")
    box = (500, 40, 1420, 1060)
    pw, ph = 600, int(600 * (box[3] - box[1]) / (box[2] - box[0]))
    ph = min(ph, 700)
    box = (box[0], box[1], box[2], box[1] + int(ph * (box[2] - box[0]) / pw))
    for i, hl in enumerate((1, 2, 3)):
        img = FN.finish("setup_h%d" % hl, "night", decorate=setup_decor(routes=HEAT_ROUTES[hl], exposed=HEAT_EXPOSED[hl],
                                                                       entries_incoming=tuple(LY.ROUTES[r][0] for r in HEAT_ROUTES[hl]) if hl == 3 else ()),
                        seed=1, creep=(60 + 40 * hl, 0.15 * hl) if hl > 1 else None)
        L = U.pencil_layer(1910 + hl)
        if hl == 3:
            ex, ey = P(*LY.ENTRIES["e_west"])
            U.pen_text(L, "WAVE 2", ex + 30, ey - 60, 18, U.R_PEN, 4.2)
        img = U.pencil_composite(img, L)
        cv = paste(cv, crop(img, box, (pw, ph)), 40 + i * 620, 140)
        head, lines = HEAT_TXT[hl]
        rows = [("t", ln, (190, 225, 240) if "*" not in ln else U.AMBER) for ln in lines]
        cv = U.put_panel(cv, U.terminal(head, rows, w=420, accent=[U.AMBER, (255, 120, 60), U.HARM][hl - 1]), 40 + i * 620, 140 + ph + 14)
    return cv


def heat_gif():
    sc = json.load(open(os.path.join(FN.SRC, "anim_h3_scene.json")))
    n = sc["anim"]
    frames = []
    for f in range(n):
        pl = sc["frames"][f]
        exposed = tuple(p[5] for p in pl if p[4] == "heli" and p[5])
        img = FN.finish("anim_h3", "night", decorate=setup_decor(exposed=exposed, t=f / n, packets=True), prefix="f%02d_" % f, frame=f,
                        seed=1, fog=0.6)
        im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((800, 450), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        d.rectangle([10, 10, 330, 36], fill=(5, 13, 28))
        d.text((18, 23), "HEAT 75  //  SPOTLIT = EXPOSED (PROPOSAL)", font=U.F(SL.MONO, 13), fill=(255, 176, 0), anchor="lm")
        frames.append(im)
        print("gif frame", f, flush=True)
    pal = frames[0].quantize(colors=160, method=Image.Quantize.MEDIANCUT)
    q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    path = os.path.join(OUT, "heat_spotlights.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=110, loop=0, optimize=True)
    print("saved heat_spotlights.gif", os.path.getsize(path) // 1024, "KB")
    return frames


# ------------------------------------------------------------------ vehicles
def threat_vehicles():
    src = FN.SRC
    beauty = FN.load(os.path.join(src, "veh_beauty.png"))
    glow = FN.load(os.path.join(src, "veh_glow.png"))
    ids = FN.load(os.path.join(src, "veh_id.png"))
    nrm = FN.load(os.path.join(src, "veh_normal.png"))
    ink = np.maximum(FN.F0.diff_edges(ids, 0.03), FN.F0.diff_edges(nrm, 0.42))
    ink = FN.F0.blur(FN.F0.maxf(FN.F0.warp(ink, 5, 1.0), 3), 0.6) * 0.85
    emis = np.clip(glow.max(axis=2) * 2, 0, 1)
    img = beauty * (1 - ink[..., None] * (1 - emis[..., None])) + np.array([0.04, 0.03, 0.08], np.float32) * ink[..., None] * (1 - emis[..., None])
    b1, b2 = FN.F0.blur_down(glow, 6, 2), FN.F0.blur_down(glow, 24, 4)
    img = img * (1 + 0.5 * b2) + 0.6 * b1 + 0.4 * b2
    lay = json.load(open(os.path.join(src, "veh_layout.json")))
    cv = np.clip(img, 0, 1) * 0.92
    cv[760:, :] = cv[760:, :] * 0.25 + BG * 0.75
    cv = title(cv, "THREAT VEHICLES", "5 CORPORATIONS x FAST / HEAVY / SPECIAL  //  BASE + UPGRADED (+)  //  SHOWN AT 2.2x MAP ZOOM")
    for it in lay["items"]:
        x, y = it["px"], it["py"]
        nm = it["unit"] + (" +" if it["up"] else "")
        cv = label(cv, x - 50, y + 28, nm, 12, (230, 236, 245))
        if not it["up"]:
            cv = label(cv, x - 50, y + 43, it["role"], 10, (150, 165, 185))
    corp_cols = {"MERIDIAN": (255, 140, 26), "SOLACE": (61, 255, 139), "HALCYON": (140, 123, 255), "ORBITAL": (127, 168, 255), "REBEL_CELL": (232, 20, 30)}
    for it in lay["items"]:
        if it["col"] == 0:
            cv = label(cv, 24, it["py"] - 6, it["corp"], 22, corp_cols[it["corp"]], font=SL.ANTON)
    k = lay["ortho"] / 440.0   # the raid map is 440 m across 1920 px
    full = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((int(W * k), int(H * k)), Image.LANCZOS)
    xs = [it["px"] for it in lay["items"]]
    ys = [it["py"] for it in lay["items"]]
    bx = (int((min(xs) - 70) * k), int((min(ys) - 60) * k), int((max(xs) + 70) * k), int((max(ys) + 40) * k))
    strip = full.crop(bx)
    sx, sy = W - strip.size[0] - 30, 790
    cv = paste(cv, np.asarray(strip, np.float32) / 255, sx, sy)
    cv = label(cv, sx, sy - 22, "TRUE MAP SCALE (all 30, as they appear on the raid map)", 13, U.CYAN)
    notes = ["MERIDIAN  boxy freight: containers, hazard stripes, amber beacons",
             "SOLACE    white capsules, green helix stripe, misting arms",
             "HALCYON   police wedges, violet rim, red/blue light bars",
             "ORBITAL   hover pods, fins, thruster glow, star-dot lights",
             "REBEL_CELL scrap mirrors: odd plates, ram bars, red tags",
             "UPGRADED  +10% size, armour plates, 2nd light, roof chevrons"]
    for i, t in enumerate(notes):
        cv = label(cv, 40, 800 + i * 24, t, 14, (200, 210, 225))
    return cv


# ------------------------------------------------------------------ contact sheet
def contact():
    names = ["raid_setup_night.png", "raid_setup_day.png", "raid_wave_night.png", "panel_mediums.png", "node_status_key.png",
             "live_info_options.png", "link_colour.png", "interactions_sheet.png", "interactions_sheet_2.png", "interactions_sheet_3.png", "world_detail.png",
             "building_nodes.png", "heat_levels_v2.png", "threat_vehicles.png"]
    names = [n for n in names if os.path.exists(os.path.join(OUT, n))]
    tw, th = 480, 270
    cols = 4
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols + 50, th * rows + 20 * rows + 80), (10, 9, 16))
    d = ImageDraw.Draw(sheet)
    d.text((14, 16), "ROUND 19  RAID: STREET GRID LOCKED (C), MEDIUMS, LIVE INFO, WORLD, HEAT, THREATS", font=U.F(SL.ANTON, 30), fill=(255, 222, 30))
    for i, n in enumerate(names):
        im = Image.open(os.path.join(OUT, n)).convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = 10 + (i % cols) * (tw + 10), 70 + (i // cols) * (th + 20)
        sheet.paste(im, (x, y))
        d.text((x + 6, y + th + 2), n, font=U.F(SL.MONO, 14), fill=(92, 225, 255))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=88)
    print("saved contact_sheet.jpg")


if __name__ == "__main__":
    which = sys.argv[1:] or ["setup_night", "setup_day", "wave", "panels", "key", "live", "link", "world", "buildings", "heat",
                             "gif", "vehicles", "interactions", "contact"]
    if "setup_night" in which:
        save(setup_frame("night"), "raid_setup_night.png")
    if "setup_day" in which:
        save(setup_frame("day"), "raid_setup_day.png")
    if "wave" in which:
        save(wave_frame(), "raid_wave_night.png")
    if "panels" in which:
        save(panel_mediums(), "panel_mediums.png")
    if "key" in which:
        save(node_status_key(), "node_status_key.png")
    if "live" in which:
        save(live_info_options(), "live_info_options.png")
    if "link" in which:
        save(link_colour(), "link_colour.png")
    if "world" in which:
        save(world_detail(), "world_detail.png")
    if "buildings" in which:
        save(building_nodes(), "building_nodes.png")
    if "heat" in which:
        save(heat_levels_v2(), "heat_levels_v2.png")
    if "gif" in which:
        heat_gif()
    if "vehicles" in which:
        save(threat_vehicles(), "threat_vehicles.png")
    if "interactions" in which:
        import interactions19 as IX
        IX.build()
    if "contact" in which:
        contact()
