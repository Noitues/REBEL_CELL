"""Round 42 2D pass -> hq_room.png, hq_room_dispatch.png, hq_actions.png.
Takes the Blender room (scratch/room/room_<v>.png + quads_<v>.json), warps CRT content / paper onto every
screen quad (occlusion-safe: only where the placeholder screen colour shows), adds screen light spill,
rain on the window, grease-pencil plans ON THE WINDOW ONLY, and sticker labels on each station.

python hq2d.py [home|dispatch|actions|all]
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops, ImageOps

import r31lib as L
import sticker_lib19 as SL
import portraits as PT

ROOM = os.path.join(L.SCRATCH, "room")
CITY = os.path.join(L.CONCEPTS, "round6_city_restyle", "views", "restyle_night_crop.png")
RED = (232, 20, 30)
SCH = 64  # Schematics in the wallet for the mock-ups


# ------------------------------------------------------------------ warping
def coeffs(dst, src):
    """PIL PERSPECTIVE coefficients mapping output (dst quad) -> input (src quad)."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def warp_onto(room, content, quad, keep_mask=True, inset=0):
    w, h = content.size
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    q = [tuple(p) for p in quad]
    if inset:
        cx = sum(p[0] for p in q) / 4
        cy = sum(p[1] for p in q) / 4
        q = [(cx + (x - cx) * (1 - inset), cy + (y - cy) * (1 - inset)) for x, y in q]
    layer = content.convert("RGBA").transform(room.size, Image.PERSPECTIVE, coeffs(q, src), Image.BICUBIC)
    poly = Image.new("L", room.size, 0)
    ImageDraw.Draw(poly).polygon([tuple(p) for p in quad], fill=255)
    if keep_mask:
        # only where the flat placeholder colour is visible (other objects may occlude the screen)
        a = np.asarray(room.convert("RGB"), np.float32)
        pm = np.asarray(poly) > 0
        inq = a[pm]
        bright = inq[inq.max(axis=1) > 150]
        med = np.median(bright if len(bright) > 20 else inq, axis=0)
        dist = np.abs(a - med).sum(axis=2)
        m = ((dist < 70) & pm).astype(np.uint8) * 255
        mask = Image.fromarray(m).filter(ImageFilter.MaxFilter(3))
        mask = ImageChops.multiply(mask, poly)
    else:
        mask = poly
    mask = ImageChops.multiply(mask, layer.split()[3])
    room = room.copy()
    room.paste(layer, (0, 0), mask)
    return room


def spill(room, quads, names, k=0.35, blur=50):
    """Screen light spill: the warped screens, blurred, added onto the room."""
    m = Image.new("L", room.size, 0)
    d = ImageDraw.Draw(m)
    for n in names:
        d.polygon([tuple(p) for p in quads[n]], fill=255)
    lit = Image.new("RGBA", room.size, (0, 0, 0, 0))
    lit.paste(room, (0, 0), m)
    g = lit.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(room.convert("RGB"), np.float32) + np.asarray(g.convert("RGB"), np.float32) * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


# ------------------------------------------------------------------ screen contents
def crt_content(w, h, acc, title, lines, tag=None, big=None, seed=1, size=22, step=32):
    c = L.CRT(w, h, acc, title, tag=tag, seed=seed, alpha=255)
    y = 56
    if big:
        c.text((24, y - 4), big[0], 70, big[1], fnt=L.f_num(78))
        y += 92
    for ln in lines:
        col = acc
        if isinstance(ln, tuple):
            ln, col = ln
        c.text((24, y), ln, size, col)
        y += step
    return c.finish(scan=0.25)


def grid_map(w, h, dispatch=False):
    acc = RED if dispatch else L.CYAN
    c = L.CRT(w, h, acc, "CITY GRID // SOLACE" if not dispatch else "CITY GRID // REBEL_CELL", tag="RAID: NONE" if not dispatch else "OWNED", seed=3, alpha=255)
    city = Image.open(CITY).convert("L").resize((w - 40, h - 110), Image.LANCZOS)
    e = city.filter(ImageFilter.FIND_EDGES).point(lambda v: min(255, v * 3))
    lay = Image.new("RGBA", e.size, acc + (0,))
    lay.putalpha(e.point(lambda v: int(v * 0.7)))
    c.paste(lay, 20, 50)
    d = c.d
    rng = random.Random(4)
    nodes = [(rng.uniform(60, w - 60), rng.uniform(80, h - 80)) for _ in range(9)]
    for i, (x, y) in enumerate(nodes):
        col = (255, 61, 168) if (i % 3 == 0 and not dispatch) else acc
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=col + (255,), outline=(255, 255, 255, 255), width=2)
    for a, b in ((0, 3), (3, 6), (1, 4), (4, 7), (2, 5)):
        d.line([nodes[a], nodes[b]], fill=acc + (200,), width=3)
    if dispatch:
        d.text((w / 2, h / 2), "NO MORE MAN", font=L.f_num(80), fill=(255, 60, 60, 255), anchor="mm")
    c.text((20, h - 40), "> JACK IN" if not dispatch else "> JACK IN  [REVOKED]", 24, (255, 255, 255))
    return c.finish(scan=0.25)


def roster_feed(name, cid, mode, w, h, label, seed):
    f = PT.feed(name, w, h, PT.COL[cid], label, mode, seed=seed)
    return f.crop((12, 12, 12 + w, 12 + h))


def dispatch_screen(w, h, text="DISPATCH", seed=1):
    f = PT.dispatch_feed(w, h, seed=seed)
    f = f.crop((12, 12, 12 + w, 12 + h))
    d = ImageDraw.Draw(f)
    if text:
        d.rectangle([0, h * 0.4, w, h * 0.6], fill=(10, 0, 2, 220))
        fs = max(16, int(h * 0.12))
        d.text((w / 2, h / 2), text, font=L.f_num(fs), fill=(255, 70, 70, 255), anchor="mm")
    return f


def wanted_poster(w=520, h=690, heat=52, dispatch=False):
    pp = L.paper(w, h, seed=8, tint=(232, 224, 200))
    d = ImageDraw.Draw(pp)
    d.text((w / 2, 60), "WANTED", font=L.font(L.ANTON, 96), fill=(40, 30, 30, 255), anchor="mm")
    d.text((w / 2, 128), "SOLACE BIOSYSTEMS // CUSTOMER SAFETY", font=L.font(L.TYPE_B, 18), fill=(30, 120, 80, 255), anchor="mm")
    ph = PT.photo_print("breaker_1", (300, 300), seed=5)
    pp.alpha_composite(ph, ((w - 300) // 2, 150))
    d = ImageDraw.Draw(pp)
    d.rectangle([(w - 300) // 2, 150, (w + 300) // 2, 450], outline=(40, 30, 30, 255), width=4)
    d.text((w / 2, 482), "\"KESTREL\"  //  REBEL_CELL LEAD", font=L.font(L.TYPE_B, 20), fill=(40, 30, 30, 255), anchor="mm")
    # heat bar with the 3 thresholds (25 / 50 / 75)
    x0, x1, y = 40, w - 40, 540
    d.text((x0, y - 6), "HEAT", font=L.font(L.ANTON, 34), fill=(180, 30, 30, 255), anchor="lb")
    d.text((x1, y - 6), str(heat), font=L.font(L.ANTON, 40), fill=(180, 30, 30, 255), anchor="rb")
    d.rectangle([x0, y, x1, y + 34], outline=(40, 30, 30, 255), width=3)
    d.rectangle([x0 + 3, y + 3, x0 + 3 + (x1 - x0 - 6) * heat / 100, y + 31], fill=(200, 40, 40, 255))
    for t in (25, 50, 75):
        xx = x0 + (x1 - x0) * t / 100
        d.line([(xx, y - 8), (xx, y + 42)], fill=(40, 30, 30, 255), width=3)
    d.text((w / 2, y + 74), "FLAGGED: raids escalate, elites more often", font=L.font(L.TYPE, 17), fill=(60, 50, 50, 255), anchor="mm")
    d.text((w / 2, y + 104), "REWARD FOR INFORMATION", font=L.font(L.TYPE_B, 18), fill=(60, 50, 50, 255), anchor="mm")
    if dispatch:
        st = L.stamp("OBSOLETE", 70, angle=-14, seed=3)
        pp.alpha_composite(st, ((w - st.width) // 2, 260))
    return pp


def screens(variant):
    disp = variant == "dispatch"
    S = {}
    if not disp:
        S["deck"] = grid_map(640, 480)
        S["deck_r"] = crt_content(640, 480, L.CYAN, "CELL STATUS", [("HOME   31 / 50", (255, 120, 140)), "EXPLOITS   1 / 3", "SITES   6 claimed", "ARMORY   4 / 6", ("SCHEMATICS   %d" % SCH, L.SCHEM), ("HEAT 52  FLAGGED", L.HEAT)], tag="STABLE", size=36, step=64)
        crew = [("rigger_1", "rigger", "idle", "SPROCKET"), ("ghost_2", "ghost", "stationed", "WREN // LANE 15"), ("breaker_3", "breaker", "idle", "SAFFRON"),
                ("botnet_1", "botnet", "dead", "SWARM"), ("phantom_1", "phantom", "hurt", "MIRAGE"), ("hivemind_2", "hivemind", "recruit", "OPEN SLOT")]
        for k, (n, cid, mode, lab) in enumerate(crew):
            S["roster_%d" % k] = roster_feed(n, cid, mode, 400, 320, lab, seed=k + 3)
        S["rack"] = crt_content(600, 360, L.CYAN, "HOME SERVER", [("31/50", (255, 120, 140)), "patch: 1 SCH / pt"], seed=5, size=60, step=90)
        S["market"] = roster_feed("contact_fixer", "ghost", "talk", 400, 320, "BLACK MARKET", seed=9)
        S["scrub"] = crt_content(600, 470, L.HEAT, "SCRUB HEAT", [("-5 HEAT", L.HEAT), "cost 25 SCH", "(+10 each)"], seed=6, size=56, step=96)
        S["poster"] = wanted_poster()
    else:
        S["deck"] = grid_map(640, 480, dispatch=True)
        S["deck_r"] = dispatch_screen(640, 480, "OBSOLETE: YOU", seed=2)
        for k in range(6):
            S["roster_%d" % k] = dispatch_screen(400, 320, ["UNLINKED", "", "NO MORE MAN", "UNLINKED", "", "FLESH IS A BUG"][k], seed=k + 4)
        S["rack"] = crt_content(600, 360, RED, "HOME SERVER", [("OWNED", (255, 80, 80)), "by REBEL_CELL"], seed=5, size=60, step=90)
        S["market"] = dispatch_screen(400, 320, "CONTACT LOST", seed=11)
        S["scrub"] = dispatch_screen(600, 470, "HEAT: IRRELEVANT", seed=12)
        S["poster"] = wanted_poster(dispatch=True)
    return S


# ------------------------------------------------------------------ window: rain + pencil
def rain(room, quad, seed=1, dispatch=False):
    m = Image.new("L", room.size, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in quad], fill=255)
    lay = Image.new("RGBA", room.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rng = random.Random(seed)
    xs = [p[0] for p in quad]
    ys = [p[1] for p in quad]
    for _ in range(420):
        x = rng.uniform(min(xs), max(xs))
        y = rng.uniform(min(ys), max(ys))
        l = rng.uniform(8, 26)
        d.line([(x, y), (x - l * 0.18, y + l)], fill=(200, 210, 255, rng.randint(40, 110)), width=1)
    for _ in range(90):
        x = rng.uniform(min(xs), max(xs))
        y = rng.uniform(min(ys), max(ys))
        r = rng.uniform(1.5, 3.5)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(230, 235, 255, 120))
    # streaks running down the glass
    for _ in range(14):
        x = rng.uniform(min(xs), max(xs))
        y0 = rng.uniform(min(ys), max(ys) - 60)
        pts = [(x + rng.uniform(-2, 2), y0 + i * 10) for i in range(rng.randint(5, 14))]
        d.line(pts, fill=(220, 230, 255, 90), width=2)
    # a faint reflection of the room on the glass
    tint = Image.new("RGBA", room.size, ((60, 20, 30) if dispatch else (40, 30, 70)) + (40,))
    lay = Image.alpha_composite(tint, lay) if False else lay
    out = room.copy()
    out.paste(Image.alpha_composite(Image.new("RGBA", room.size, (0, 0, 0, 0)), lay), (0, 0), ImageChops.multiply(m, lay.split()[3]))
    return out


def pencil_window(room, quad, dispatch=False):
    """Plans drawn on the window glass over the city (grease pencil; nothing else goes here)."""
    (x0, y0), (x1, _), (_, y1), _ = quad
    W_, H_ = x1 - x0, y1 - y0
    P = lambda u, v: (x0 + u * W_, y0 + v * H_)
    py = L.pen(L.GP_YELLOW, seed=91)
    py.circle(*P(0.47, 0.47), 34, 44, width=7)
    py.arrow([P(0.18, 0.86), P(0.3, 0.7), P(0.4, 0.58), P(0.45, 0.52)], width=7, head=18)
    py.text("LANE 15 - TONIGHT", *P(0.3, 0.93), 26, angle=-4)
    room = L.ink(room, py)
    pr = L.pen(L.GP_RED, seed=92)
    if dispatch:
        pr.stroke(SL.catmull([P(0.12, 0.6), P(0.5, 0.55), P(0.85, 0.5)], 6), width=9)
        pr.stroke(SL.catmull([P(0.15, 0.95), P(0.5, 0.75), P(0.85, 0.62)], 6), width=9)
        pr.circle(*P(0.62, 0.22), 70, 80, width=8)
        pr.text("IT WAS DISPATCH", *P(0.62, 0.48), 30, angle=-5)
    else:
        pr.circle(*P(0.78, 0.3), 30, 30, width=6)
        pr.text("DRONES", *P(0.8, 0.12), 22, angle=6)
    return L.ink(room, pr)


# ------------------------------------------------------------------ stickers on stations
def station_stickers(img, q, dispatch=False):
    def ctr(name, dy=0, dx=0):
        pts = q[name]
        return (sum(p[0] for p in pts) / 4 + dx, max(p[1] for p in pts) + dy)
    items = [
        (["JACK IN"], 50, ["pink"], ctr("deck", 50), -3),
        (["CREW"], 34, [(166, 255, 72)], (250, 690), 4),
        (["HOME"], 30, [(92, 225, 255)], ctr("rack", 40, -20), -6),
        (["BLACK MARKET"], 28, [(255, 190, 60)], (1745, 430), 3),
        (["SCRUB HEAT"], 20, [(255, 96, 64)], (600, 508), -4),
        (["REPAIR"], 24, [(166, 255, 72)], (958, 655), 2),
        (["STATUS"], 26, [(92, 225, 255)], ctr("deck_r", 40), 4),
    ]
    for lines, size, fill, (x, y), ang in items:
        sd = L.sticker_word(lines, size, fills=fill, seed=sum(map(ord, lines[0])), extrude=4, border=8)
        if dispatch:
            sd = L.greyscale(sd, 0.55)
            if lines[0] in ("JACK IN", "CREW"):
                sd = dict(sd)
                sd = SL.apply_curl(sd, corner="tr", amount=0.4)
        img = L.place_sticker(img, sd, x, y, angle=ang)
    # Cell fist / slogan stickers on the deck monitor bodies (lived-in)
    for (txt, x, y, a, f) in (("TRUST NO ONE", 1440, 650, 6, [(232, 230, 238)]),):
        sd = L.sticker_word([txt], 18, fills=[f] if isinstance(f, str) else f, seed=len(txt), extrude=3, border=6)
        if dispatch:
            sd = L.greyscale(sd, 0.5)
        img = L.place_sticker(img, sd, x, y, angle=a)
    return img


def neon_sign(img, q, dispatch=False):
    """A tube sign on the wall above the window (an object of the room: the Cell's slogan)."""
    (x0, y0), (x1, _), _, _ = q["window"]
    txt = "NEVER SLEEP" if not dispatch else "NO MORE MAN"
    col = (255, 61, 168) if not dispatch else (255, 40, 40)
    f = L.font(L.BAHN, 64, b"SemiBold Condensed")
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).text(((x0 + x1) / 2, y0 - 46), txt, font=f, fill=255, anchor="mm")
    edge = ImageChops.subtract(m.filter(ImageFilter.MaxFilter(5)), m.filter(ImageFilter.MinFilter(3)))
    glow = edge.filter(ImageFilter.GaussianBlur(12)).point(lambda v: min(255, v * 3))
    img = SL.over(img, col, glow)
    img = SL.over(img, tuple(min(255, c + 150) for c in col), edge)
    return img


def hatch_glow(img, dispatch=False):
    """Warm light inside the Black Market hatch (the fixer's side of the wall)."""
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).polygon([(1668, 520), (1885, 505), (1885, 690), (1668, 640)], fill=150)
    m = m.filter(ImageFilter.GaussianBlur(18))
    return SL.over(img, (255, 150, 60) if not dispatch else (255, 30, 30), m)


def build(variant):
    room = Image.open(os.path.join(ROOM, "room_%s.png" % variant)).convert("RGBA")
    q = json.load(open(os.path.join(ROOM, "quads_%s.json" % variant)))
    S = screens(variant)
    for name, content in S.items():
        room = warp_onto(room, content, q[name], keep_mask=True)
    room = spill(room, q, [n for n in S if n != "poster"], k=0.4 if variant == "home" else 0.55)
    room = rain(room, q["window"], dispatch=variant == "dispatch")
    room = L.bloom(room, 0.25, 0.7, 10)
    room = L.vignette(room, 0.45)
    room = neon_sign(room, q, dispatch=variant == "dispatch")
    room = hatch_glow(room, dispatch=variant == "dispatch")
    room = pencil_window(room, q["window"], dispatch=variant == "dispatch")
    room = station_stickers(room, q, dispatch=variant == "dispatch")
    if variant == "dispatch":
        a = np.asarray(room.convert("RGB"), np.float32)
        rng = np.random.default_rng(3)
        for _ in range(10):  # the whole room glitches
            y0 = int(rng.integers(0, 1040))
            hh = int(rng.integers(3, 18))
            a[y0:y0 + hh] = np.roll(a[y0:y0 + hh], int(rng.integers(-30, 30)), axis=1)
        room = Image.fromarray(a.astype(np.uint8)).convert("RGBA")
    return room, q


def make_room(variant):
    img, _ = build(variant)
    L.save(img, "hq_room.png" if variant == "home" else "hq_room_dispatch.png")
    img.save(os.path.join(ROOM, "final_%s.png" % variant))


# ------------------------------------------------------------------ actions
def action_bg(room, box, size):
    c = room.crop(box).resize(size, Image.LANCZOS)
    c = ImageEnhance.Brightness(c.filter(ImageFilter.GaussianBlur(3))).enhance(0.5)
    return c.convert("RGBA")


def panel_patch():
    c = L.CRT(600, 420, L.CYAN, "HOME SERVER // PATCH", tag="WALLET %d SCH" % SCH, seed=21)
    c.text((24, 58), "INTEGRITY", 22, (255, 140, 170))
    c.text((576, 50), "31 > 41", 40, (255, 140, 170), anchor="ra", fnt=L.f_num(44))
    x0, y0, w = 24, 104, 552
    c.d.rectangle([x0, y0, x0 + w, y0 + 34], outline=(255, 140, 170, 255), width=2)
    c.d.rectangle([x0 + 2, y0 + 2, x0 + 2 + (w - 4) * 31 / 50, y0 + 32], fill=(255, 100, 140, 255))
    c.d.rectangle([x0 + 2 + (w - 4) * 31 / 50, y0 + 2, x0 + 2 + (w - 4) * 41 / 50, y0 + 32], fill=(255, 100, 140, 110))
    c.text((24, 156), "+10 pts  x 1 SCH  =  10 SCH", 22, L.SCHEM)
    c.rule(196, dash=True)
    c.text((24, 212), "REPAIR NODES  (50% of install)", 20, L.CYAN)
    for k, (n, st, cost) in enumerate((("LANE 15 RELAY", "DISABLED", 10), ("CLINIC CACHE", "DISABLED", 15), ("YARD SAFEHOUSE", "OK", None))):
        y = 248 + k * 40
        c.text((24, y), n, 20, (220, 230, 240))
        c.text((330, y), st, 18, (255, 120, 120) if st != "OK" else (120, 255, 150))
        if cost:
            c.text((576, y), "%d SCH" % cost, 20, L.SCHEM, anchor="ra")
    return c.finish()


def panel_market():
    c = L.CRT(760, 420, (255, 190, 60), "BLACK MARKET", tag="WALLET %d SCH" % SCH, seed=22)
    f = roster_feed("contact_fixer", "ghost", "talk", 170, 150, "FIXER", seed=31)
    c.paste(f, 20, 52)
    c.text((210, 60), "\"Fresh rookies. Cash only.\"", 20, (255, 220, 160))
    c.text((210, 96), "RECRUIT  15 SCH", 22, L.SCHEM)
    for k, (n, cid) in enumerate((("overclocker_2", "overclocker"), ("phantom_3", "phantom"), ("rigger_3", "rigger"))):
        r = roster_feed(n, cid, "recruit", 150, 130, cid.upper(), seed=40 + k)
        c.paste(r, 210 + k * 176, 132)
    c.rule(286, dash=True)
    c.text((20, 302), "NEXT-RUN BOOSTS", 20, (255, 190, 60))
    c.text((20, 334), "+1 card draw   12      firmware crate   18", 18, (220, 210, 190))
    c.text((20, 366), "PROFILE UNLOCK   class: WRECKER   80", 18, (220, 210, 190))
    return c.finish()


def panel_roster():
    c = L.CRT(760, 420, L.LIME, "CREW // ROSTER", tag="2 READY  1 STATIONED", seed=23)
    rows = [("rigger_1", "rigger", "idle", "SPROCKET", "RANK 2", "READY", "LOADOUT  |  STATION"),
            ("ghost_2", "ghost", "stationed", "WREN", "RANK 1", "ON LANE 15", "RECALL"),
            ("botnet_1", "botnet", "dead", "SWARM", "RANK 1", "FLATLINED", "")]
    for k, (n, cid, mode, call, rk, st, orders) in enumerate(rows):
        y = 52 + k * 120
        c.paste(roster_feed(n, cid, mode, 120, 104, None, seed=50 + k), 20, y)
        c.text((160, y + 4), call, 30, (255, 255, 255) if mode != "dead" else (120, 120, 130), fnt=L.f_num(34))
        c.text((160, y + 48), cid.upper() + "  //  " + rk, 17, PT.COL[cid] if mode != "dead" else (110, 110, 120))
        c.text((740, y + 10), st, 18, (120, 255, 150) if st == "READY" else ((255, 90, 90) if mode == "dead" else PT.COL[cid]), anchor="ra")
        if orders:
            c.d.rounded_rectangle([450, y + 52, 740, y + 86], radius=6, outline=L.LIME + (255,), width=2)
            c.text((595, y + 58), orders, 17, L.LIME, anchor="ma")
        if mode == "dead":
            c.d.line([(156, y + 24), (300, y + 24)], fill=(255, 90, 90, 255), width=3)
    return c.finish()


def make_actions():
    home = Image.open(os.path.join(ROOM, "final_home.png")).convert("RGBA")
    canvas = Image.new("RGBA", (L.W, L.H), (11, 10, 16, 255))
    cells = [
        ((1300, 380, 1920, 720), panel_patch(), "PATCH HOME + REPAIR", "server rack: 1 Schematic per integrity point; repair 50% of install", ["HOME"], [(92, 225, 255)]),
        ((1480, 380, 1920, 720), panel_market(), "BLACK MARKET", "the fixer's hatch: recruit 15, next-run boosts, profile unlocks", ["BLACK MARKET"], [(255, 190, 60)]),
        ((0, 300, 480, 700), panel_roster(), "CREW ROSTER", "the TV wall: loadout, station / recall; the dead keep their slot", ["CREW"], [(166, 255, 72)]),
        ((440, 330, 760, 580), None, "SCRUB HEAT", "the WANTED poster + scrubber: -5 Heat for 25 (+10 each time)", ["SCRUB HEAT"], [(255, 96, 64)]),
    ]
    for k, (box, panel, title, sub, st, fill) in enumerate(cells):
        x, y = 20 + (k % 2) * 950, 20 + (k // 2) * 530
        bg = action_bg(home, box, (930, 510))
        canvas.alpha_composite(bg, (x, y))
        d = ImageDraw.Draw(canvas)
        d.rectangle([x, y, x + 929, y + 509], outline=(60, 56, 72, 255), width=2)
        if panel is not None:
            k_ = min(1.0, 880 / panel.width, 385 / panel.height)
            p2 = panel.resize((int(panel.width * k_), int(panel.height * k_)), Image.LANCZOS) if k_ < 1 else panel
            canvas = L.drop_shadow(canvas, p2, x + (930 - p2.width) // 2, y + 70, blur=14)
        else:
            poster = L.rotate_rgba(wanted_poster(heat=47).resize((290, 385), Image.LANCZOS), -2)
            canvas = L.drop_shadow(canvas, poster, x + 60, y + 66, blur=10)
            stp = L.stamp("-5 HEAT", 40, col=(255, 96, 64), angle=-12, seed=3)
            canvas.alpha_composite(stp, (x + 210, y + 330))
            sc = crt_content(440, 300, L.HEAT, "SCRUB HEAT", [("HEAT  52 > 47", L.HEAT), "band: FLAGGED", ("cost 25 SCH", L.SCHEM), "next scrub: 35", "wallet 64 > 39"], seed=7)
            canvas = L.drop_shadow(canvas, sc, x + 440, y + 110, blur=12)
        sd = L.sticker_word(st, 34, fills=fill, seed=k + 5, extrude=4, border=8)
        canvas = L.place_sticker(canvas, sd, x + 150, y + 38, angle=-3)
        d = ImageDraw.Draw(canvas)
        d.text((x + 300, y + 36), title, font=L.f_num(30), fill=(255, 255, 255, 255), anchor="lm")
        d.rectangle([x + 2, y + 474, x + 927, y + 507], fill=(8, 7, 12, 235))
        d.text((x + 20, y + 491), sub, font=L.f_mono(16), fill=(210, 210, 225, 255), anchor="lm")
    L.save(canvas, "hq_actions.png")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("home", "all"):
        make_room("home")
    if what in ("dispatch", "all"):
        make_room("dispatch")
    if what in ("actions", "all"):
        make_actions()
