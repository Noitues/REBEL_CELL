"""Round 20: CAMPAIGN LOST. The home server hit 0: the Cell's own computer station is hacked and taken down.

Option A  RANSOMWARE LOCK: the losing corporation's ransomware takes over the whole screen in its own house style
          (Halcyon Civic shown; Meridian / Solace / Orbital / REBEL_CELL variants), padlocks stamp every node, the
          Cell's vinyl stickers peel off and fall, a countdown runs to the wipe -> campaign summary.
Option B  CARRIER LOST: the station's monitors die: tearing, RGB split, the CRT collapses to a line and a dot, then a
          bare terminal (NO CARRIER / TRACE COMPLETE) with the corp watermark burned in.
Every frame is a function of (option, u) so the PNG sheet and the GIF share one code path.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import layout as LY
import finish19 as FN
import ui19 as U
import icons20 as IC

SL = U.SL
HERE = os.path.dirname(os.path.abspath(__file__))
EMB = os.path.join(os.path.dirname(HERE), "scratch", "emblems")
BAHN = "C:/Windows/Fonts/bahnschrift.ttf"
GEORGIA_B = "C:/Windows/Fonts/georgiab.ttf"
W, H = 1920, 1080
CORP_STYLE = {
    "HALCYON": dict(name="HALCYON CIVIC", col=(150, 92, 255), acc=(255, 168, 30), bg=(18, 12, 40), motif="blueprint",
                    head="YOUR CELL HAS BEEN PROCESSED", sub="Civic Order 7/88: network assets seized, operatives reclassified.",
                    stamp="PROCESSED", ref="REF HC-7718/CELL", font=BAHN),
    "MERIDIAN": dict(name="MERIDIAN FREIGHT", col=(255, 128, 16), acc=(255, 214, 60), bg=(34, 18, 6), motif="hazard",
                     head="CARGO RECLAIMED", sub="Manifest closed: 6 nodes repossessed under freight lien.", stamp="RECLAIMED",
                     ref="MANIFEST MF-0041-C", font=SL.ANTON),
    "SOLACE": dict(name="SOLACE BIOSYSTEMS", col=(108, 255, 40), acc=(236, 246, 236), bg=(6, 24, 12), motif="cells",
                   head="YOUR CELL HAS BEEN TREATED", sub="Infection contained. Please remain calm while we sterilise your network.",
                   stamp="STERILE", ref="CASE SB-2210/QUARANTINE", font=SL.PLEX),
    "ORBITAL": dict(name="ORBITAL COMMONS", col=(120, 236, 255), acc=(232, 246, 255), bg=(4, 14, 28), motif="stars",
                    head="SIGNAL DE-ORBITED", sub="Your uplink has been reassigned to the commons. Burn-up in progress.",
                    stamp="DE-ORBITED", ref="TLE OC-55 / DECAY", font=BAHN),
    "REBEL_CELL": dict(name="DISPATCH", col=(255, 26, 34), acc=(255, 120, 80), bg=(30, 4, 6), motif="glitch",
                       head="DISPATCH HAS YOUR CELL", sub="you were always a copy. the original sends its regards.",
                       stamp="OVERWRITTEN", ref="DISPATCH // ECHO 00", font=SL.MARKER),
}


def F(path, size):
    return ImageFont.truetype(path, int(size))


def to_pil(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def to_f(im):
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


def emblem_img(name, size, col):
    g = Image.open(os.path.join(EMB, name.lower() + ".png")).split()[3].resize((size, size), Image.LANCZOS)
    im = Image.new("RGBA", (size, size), col + (0,))
    im.putalpha(g)
    return im


# ------------------------------------------------------------------ the raid screen the loss happens on
_base = {}


def raid_screen():
    """W_full finished with the home server burnt (0/50), the links dead, the HUD of a running raid (no stickers yet)."""
    if "map" not in _base:
        import netdecal19 as ND
        st = {k: ("burnt" if k == "core" else "holds") for k in LY.NODES}
        st.update(dict(vault="disabled", proxy="seized"))

        def deco(net):
            ND.setup_state(net, forecast=False, statuses=st, integ=dict(core=0.0, vault=0.0, safe=0.6),
                           routes=("r1", "r2", "r3"), entries_incoming=tuple(LY.ENTRIES), t=0.4,
                           link_states={("core", "relay"): "dead", ("core", "firewall"): "dead", ("core", "vault"): "dead", ("core", "safe"): "dead"})
            for (corp, ui, x, y, a, up, hp) in LY.THREATS_V2:
                net.threat_ring(x, y, hp=hp)
        img = FN.finish("W_full", "night", decorate=deco, seed=1, rain=True)
        img = U.put_panel(img, U.terminal("YOUR NODES", [("kv", "CORE (home)", "00/50", U.HARM), ("kv", "VAULT TERMINAL", "DISABLED", U.AMBER),
                                                          ("kv", "PROXY RELAY", "SEIZED", U.HARM), ("kv", "FIREWALL RELAY", "22/30", U.GREEN),
                                                          ("kv", "SAFEHOUSE", "12/20", U.GREEN)], w=330), 22, 150)
        img = U.put_panel(img, U.terminal("RAID FEED  //  STEP 19/30", [("t", "BAILIFF reached CORE: -14", U.HARM),
                                                                         ("t", "CORE integrity 0 / 50", U.HARM),
                                                                         ("t", "> connection to home server lost", (190, 225, 240))],
                                          w=330, accent=U.HARM), 1568, 150)
        _base["map"] = img
    return _base["map"].copy()


def stickers():
    """The Cell's vinyl on screen: title, defence cards, a CELL sticker. (sticker, cx, cy, angle)."""
    out = [(U.word_sticker(["CELL DEFENSE"], 46, [U.FILL_YELLOW], seed=11, border=14), 330, 70, -1.5)]
    x = 560
    for i, (nm, gl, hp, cp, ds, col) in enumerate(U.TRAY[:5]):
        out.append((U.asset_card(nm, gl, hp, cp, ds, col, 50 + i), x, 985, [-2, 1.5, -1, 2, -1.5][i]))
        x += 162
    out.append((U.word_sticker(["REBEL_CELL"], 34, [U.FILL_PINK], seed=21, border=12), 1690, 1012, -3))
    return out


_curls = {}


def put_stickers(img, peel=0.0, fall=0.0, seed=3):
    """peel 0..1: corners curl in turn; fall 0..1: stickers drop off the screen (rotating), staggered."""
    rng = np.random.default_rng(seed)
    corners = ["tr", "tl", "br", "bl"]
    for i, (sd, cx, cy, ang) in enumerate(stickers()):
        delay = rng.uniform(0, 0.35)
        p = float(np.clip((peel - delay) / 0.65, 0, 1))
        fl = float(np.clip((fall - delay * 0.8) / 0.7, 0, 1))
        if fl >= 1.0:
            continue
        if p > 0.02:
            amt = round(0.08 + 0.62 * p, 2)
            key = (i, amt)
            if key not in _curls:
                _curls[key] = SL.apply_curl(sd, corner=corners[i % 4], amount=amt)
            sd = _curls[key]
        dy = fl * fl * 900
        img = U.place(img, sd, cx + fl * rng.uniform(-80, 80), cy + dy, angle=ang + fl * rng.uniform(-50, 50), hover=min(1.0, p * 0.8 + fl),
                      opacity=1.0 - fl * 0.3)
    return img


# ------------------------------------------------------------------ glitch / CRT
def glitch(img, k, seed):
    """Horizontal band tearing, RGB split, blocky corruption. k 0..1."""
    if k <= 0:
        return img
    rng = np.random.default_rng(seed)
    out = img.copy()
    h, w = img.shape[:2]
    for _ in range(int(6 + 30 * k)):
        y0 = int(rng.uniform(0, h))
        hh = int(rng.uniform(4, 60 * k + 6))
        sh = int(rng.normal(0, 120 * k))
        out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], sh, axis=1)
    s = int(4 + 18 * k)
    out[..., 0] = np.roll(out[..., 0], s, axis=1)
    out[..., 2] = np.roll(out[..., 2], -s, axis=1)
    for _ in range(int(20 * k)):
        x0, y0 = int(rng.uniform(0, w - 80)), int(rng.uniform(0, h - 40))
        bw, bh = int(rng.uniform(20, 220)), int(rng.uniform(6, 40))
        out[y0:y0 + bh, x0:x0 + bw] = out[y0:y0 + bh, x0:x0 + bw][:, ::-1] * rng.uniform(0.3, 1.6)
    sl = (np.arange(h) % 3 == 0)[:, None, None]
    out = out * (1 - 0.25 * k * sl)
    return np.clip(out, 0, 1)


def crt_off(img, u):
    """u 0..1: the picture squashes to a bright line (0..0.6), then to a dot (0.6..0.9), then black."""
    h, w = img.shape[:2]
    out = np.zeros_like(img)
    if u >= 0.95:
        return out
    if u < 0.6:
        v = u / 0.6
        nh = max(2, int(h * (1 - v) ** 2))
        im = to_pil(img * (1 + 2.5 * v)).resize((w, nh), Image.BILINEAR)
        out[(h - nh) // 2:(h - nh) // 2 + nh] = to_f(im)
    else:
        v = (u - 0.6) / 0.35
        nw = max(2, int(w * (1 - v) ** 3))
        line = np.ones((3, nw, 3), np.float32) * np.array([0.85, 0.95, 1.0], np.float32)
        out[h // 2 - 1:h // 2 + 2, (w - nw) // 2:(w - nw) // 2 + nw] = line
    glow = np.asarray(to_pil(out).filter(ImageFilter.GaussianBlur(14)), np.float32) / 255.0
    return np.clip(out + glow * 1.6, 0, 1)


# ------------------------------------------------------------------ option A: the corp's ransomware
def motif(style, seed=1):
    """Full-screen motif layer (L mask) in the corp's house style."""
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    rng = np.random.default_rng(seed)
    if style == "blueprint":
        for x in range(0, W, 48):
            d.line([(x, 0), (x, H)], fill=70 if x % 240 else 140, width=1)
        for y in range(0, H, 48):
            d.line([(0, y), (W, y)], fill=70 if y % 240 else 140, width=1)
        for _ in range(14):
            cx, cy, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(40, 200)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=110, width=1)
    elif style == "hazard":
        for x in range(-H, W, 90):
            d.polygon([(x, H), (x + 45, H), (x + 45 + H, 0), (x + H, 0)], fill=60)
        for _ in range(30):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            for k in range(int(rng.uniform(10, 30))):
                d.rectangle([x + k * 5, y, x + k * 5 + rng.integers(1, 4), y + 40], fill=120)
    elif style == "cells":
        for _ in range(160):
            cx, cy, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(10, 60)
            d.regular_polygon((cx, cy, r), 6, outline=110)
    elif style == "stars":
        for _ in range(900):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            s = rng.uniform(0.5, 2.2)
            d.ellipse([x - s, y - s, x + s, y + s], fill=int(rng.uniform(80, 255)))
        for k in range(6):
            r = 300 + k * 160
            d.arc([W / 2 - r, H / 2 - r * 0.35, W / 2 + r, H / 2 + r * 0.35], 0, 360, fill=90, width=1)
    else:   # glitch
        for _ in range(140):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            d.rectangle([x, y, x + rng.uniform(20, 300), y + rng.uniform(2, 14)], fill=int(rng.uniform(60, 200)))
    return m


def seal(st, size):
    """Corp seal: emblem in a double ring with the corp name around it."""
    S = size * 2
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = st["col"]
    d.ellipse([4, 4, S - 4, S - 4], outline=col + (255,), width=int(S * 0.03))
    d.ellipse([S * 0.16, S * 0.16, S * 0.84, S * 0.84], outline=col + (255,), width=int(S * 0.015))
    f = F(SL.MONO, S * 0.075)
    txt = ("  %s  *  " % st["name"]) * 2
    n = len(txt)
    for i, ch in enumerate(txt):
        a = -math.pi / 2 + 2 * math.pi * i / n
        r = S * 0.41
        x, y = S / 2 + r * math.cos(a), S / 2 + r * math.sin(a)
        ci = Image.new("RGBA", (int(S * 0.1), int(S * 0.1)), (0, 0, 0, 0))
        ImageDraw.Draw(ci).text((S * 0.05, S * 0.05), ch, font=f, fill=col + (255,), anchor="mm")
        ci = ci.rotate(-math.degrees(a) - 90, Image.BICUBIC)
        im.alpha_composite(ci, (int(x - ci.size[0] / 2), int(y - ci.size[1] / 2)))
    corp_key = [k for k, v in CORP_STYLE.items() if v is st][0]
    e = emblem_img(corp_key, int(S * 0.44), col)
    im.alpha_composite(e, (int(S * 0.28), int(S * 0.28)))
    return im.resize((size, size), Image.LANCZOS)


def padlock(size, col):
    S = size * 3
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.arc([S * 0.25, S * 0.06, S * 0.75, S * 0.62], 180, 360, fill=col + (255,), width=int(S * 0.1))
    d.line([(S * 0.3, S * 0.34), (S * 0.3, S * 0.48)], fill=col + (255,), width=int(S * 0.1))
    d.line([(S * 0.7, S * 0.34), (S * 0.7, S * 0.48)], fill=col + (255,), width=int(S * 0.1))
    d.rounded_rectangle([S * 0.14, S * 0.44, S * 0.86, S * 0.94], S * 0.08, fill=col + (255,))
    d.ellipse([S * 0.44, S * 0.58, S * 0.56, S * 0.7], fill=(10, 8, 14, 255))
    d.rectangle([S * 0.48, S * 0.66, S * 0.52, S * 0.82], fill=(10, 8, 14, 255))
    return im.resize((size, size), Image.LANCZOS)


def ransom(img, corp="HALCYON", u=1.0, countdown=9.43, progress=0.66, seed=1, panel_scale=1.0):
    """Overlay the ransomware takeover. u 0..1 = how far it has taken the screen (wipe-in from the top + lock stamps)."""
    st = CORP_STYLE[corp]
    col = np.array(st["col"], np.float32) / 255.0
    bgc = np.array(st["bg"], np.float32) / 255.0
    h, w = img.shape[:2]
    lum = img.mean(axis=2, keepdims=True)
    tinted = lum * 0.55 * (0.5 + col * 0.8) + bgc * 0.6
    m = np.asarray(motif(st["motif"], seed), np.float32)[..., None] / 255.0
    tinted = tinted + m * col * 0.32
    # wipe: the takeover rolls down the screen with a bright scan edge
    edge = u * (h + 200) - 100
    yy = np.arange(h, dtype=np.float32)[:, None, None]
    cover = np.clip((edge - yy) / 60.0, 0, 1)
    scan = np.exp(-((yy - edge) / 8.0) ** 2) * (u < 1.0)
    out = img * (1 - cover) + tinted * cover + scan * col * 1.4
    pil = to_pil(out).convert("RGBA")
    # padlocks on every node socket
    cam = FN.json.load(open(os.path.join(FN.SRC, "W_full_scene.json")))["cam"]
    keep = dict(LY.CAM)
    LY.CAM.update({k: (tuple(v) if isinstance(v, list) else v) for k, v in cam.items()})
    for i, (k, n) in enumerate(sorted(LY.NODES.items())):
        px, py, _ = LY.project(n[0], n[1], 0)
        if py < edge - 40 and u > 0.2:
            lk = padlock(54 if k != "core" else 72, st["acc"])
            pil.alpha_composite(lk, (int(px - lk.size[0] / 2), int(py - lk.size[1] / 2 - 10)))
    LY.CAM.update(keep)
    if u >= 0.55:
        k = min(1.0, (u - 0.55) / 0.3)
        pw, ph = int(1040 * panel_scale), int(560 * panel_scale)
        x0, y0 = (w - pw) // 2, (h - ph) // 2 - 10
        pan = Image.new("RGBA", (pw, ph), st["bg"] + (int(235 * k),))
        d = ImageDraw.Draw(pan)
        c = st["col"]
        d.rectangle([0, 0, pw - 1, ph - 1], outline=c + (255,), width=3)
        d.rectangle([0, 0, pw, int(56 * panel_scale)], fill=c + (255,))
        d.text((int(24 * panel_scale), int(28 * panel_scale)), "%s  //  NOTICE" % st["name"], font=F(SL.MONO, 26 * panel_scale),
               fill=st["bg"] + (255,), anchor="lm")
        d.text((pw - int(24 * panel_scale), int(28 * panel_scale)), st["ref"], font=F(SL.MONO, 18 * panel_scale), fill=st["bg"] + (255,), anchor="rm")
        sz = int(200 * panel_scale)
        pan.alpha_composite(seal(st, sz), (int(30 * panel_scale), int(90 * panel_scale)))
        tx = int(260 * panel_scale)
        head = st["head"]
        fs = 64 * panel_scale
        while F(st["font"], fs).getlength(head) > pw - tx - 30 and fs > 20:
            fs -= 2
        d.text((tx, int(96 * panel_scale)), head, font=F(st["font"], fs), fill=(244, 241, 233, 255))
        d.text((tx, int(96 * panel_scale + fs * 1.35)), st["sub"], font=F(SL.PLEX, 22 * panel_scale), fill=c + (255,))
        d.text((tx, int(250 * panel_scale)), "HOME SERVER  00/50   //   NODES ENCRYPTED  %d/6" % round(progress * 6),
               font=F(SL.MONO, 20 * panel_scale), fill=(244, 241, 233, 255))
        bx0, by0, bx1 = tx, int(284 * panel_scale), pw - int(40 * panel_scale)
        d.rectangle([bx0, by0, bx1, by0 + int(22 * panel_scale)], outline=c + (255,), width=2)
        d.rectangle([bx0 + 4, by0 + 4, bx0 + 4 + (bx1 - bx0 - 8) * progress, by0 + int(22 * panel_scale) - 4], fill=st["acc"] + (255,))
        d.text((int(30 * panel_scale), int(340 * panel_scale)), "WIPE IN", font=F(SL.MONO, 26 * panel_scale), fill=c + (255,))
        cd = "00:%05.2f" % max(0.0, countdown)
        d.text((int(26 * panel_scale), int(372 * panel_scale)), cd, font=F(SL.MONO, 132 * panel_scale), fill=st["acc"] + (255,))
        d.text((int(30 * panel_scale), ph - int(46 * panel_scale)), "decryption is not offered.  your station is no longer yours.",
               font=F(SL.MONO, 18 * panel_scale), fill=(200, 200, 210, 255))
        # big stamp across the panel, the corp's verb
        stp = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        ImageDraw.Draw(stp).text((int(pw * 0.73), int(ph * 0.72)), st["stamp"], font=F(SL.ANTON, 84 * panel_scale), fill=st["acc"] + (200,), anchor="mm")
        stp = stp.rotate(9, Image.BICUBIC)
        pan.alpha_composite(stp)
        if k < 1:
            pan.putalpha(pan.split()[3].point(lambda v: int(v * k)))
        pil.alpha_composite(pan, (x0, y0))
    return to_f(pil)


# ------------------------------------------------------------------ option B: carrier lost
def carrier(corp="HALCYON", blink=True, lines=6, watermark=0.25):
    st = CORP_STYLE[corp]
    im = Image.new("RGB", (W, H), (4, 5, 8))
    wm = emblem_img(corp, 620, st["col"])
    wm.putalpha(wm.split()[3].point(lambda v: int(v * watermark)))
    rgba = im.convert("RGBA")
    rgba.alpha_composite(wm, ((W - 620) // 2, (H - 620) // 2))
    d = ImageDraw.Draw(rgba)
    txt = ["NO CARRIER", "", "TRACE COMPLETE  ..  route 7 hops  ..  origin: %s" % st["name"],
           "HOME SERVER  00/50  ..  integrity lost", "station handshake refused  (x3)", "local session terminated by remote",
           "", "> _"]
    green = (126, 255, 140)
    for i, t in enumerate(txt[:lines + 2]):
        if t == "> _" and not blink:
            t = ">"
        fs = 84 if i == 0 else 26
        d.text((180, 260 + (0 if i == 0 else 70 + i * 40)), t, font=F(SL.MONO, fs), fill=green if i else (255, 68, 51))
    a = to_f(rgba)
    sl = (np.arange(H) % 3 == 0)[:, None, None]
    a = a * (1 - 0.3 * sl)
    glow = np.asarray(to_pil(a).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255.0
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = 1 - 0.55 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return np.clip((a + glow * 0.6) * vig[..., None], 0, 1)


# ------------------------------------------------------------------ the timelines
def frame_A(u, corp="HALCYON"):
    """Option A over u 0..1: 0-.15 hit + glitch, .15-.5 the ransomware wipes in and padlocks every node, .5-1 the notice +
    countdown. The stickers are vinyl ON THE GLASS: never glitched or tinted, they curl and then drop off."""
    img = raid_screen()
    if u < 0.18:
        img = glitch(img, 0.25 + 2.5 * u, int(u * 1000))
    rw = float(np.clip((u - 0.14) / 0.35, 0, 1))
    if rw > 0:
        img = ransom(img, corp, u=0.2 + rw * 0.8 if rw < 1 else 1.0, countdown=10.0 - 10.0 * float(np.clip((u - 0.5) / 0.5, 0, 1)),
                     progress=float(np.clip((u - 0.3) / 0.6, 0, 1)))
        if 0.6 < u < 0.64 or 0.8 < u < 0.82:
            img = glitch(img, 0.35, int(u * 1000))
    return put_stickers(img, peel=float(np.clip((u - 0.12) / 0.4, 0, 1)), fall=float(np.clip((u - 0.5) / 0.4, 0, 1)))


def frame_B(u, corp="HALCYON"):
    """Option B over u 0..1: 0-.3 tearing, .3-.55 CRT collapse, .55-1 the bare terminal types in. The stickers stay on
    the dead glass, half peeled."""
    peel = float(np.clip(u / 0.5, 0, 1)) * 0.55
    base = raid_screen()
    if u < 0.3:
        img = glitch(base, 0.2 + u * 3.0, int(u * 997))
    elif u < 0.55:
        img = crt_off(glitch(base, 0.9, 7), (u - 0.3) / 0.25)
    else:
        v = (u - 0.55) / 0.45
        img = carrier(corp, blink=int(v * 12) % 2 == 0, lines=int(v * 9), watermark=0.25 * min(1.0, v * 2))
    return put_stickers(img, peel=peel)
