"""daemon_row.png (the Daemon rack on the combat screen: idle, triggered, counters, Twin Pointer + Botnet Seed cues,
the terminal tooltip, a states inset) and daemon_trigger.gif (a Perfect fires three Daemons in turn).

python daemon_row.py [still|gif|all]
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

import fwlib as F
import fwfx as X
L = F.L

BG = os.path.join(L.CONCEPTS, "round31_meridian_combat", "combat_meridian.jpg")
WC = (478, 503)        # player wheel centre on the combat screen
RACK = ["kernel_sync", "clean_signal", "botnet_seed", "twin_pointer", "stolen_intent", "warm_boot"]
TS = 60                # tile size in the rack
RX, RY = 30, 206       # rack plate origin
SLOT = TS + 22
TOP_READ = (480, 330)  # top slice (ZERO-DAY 12) read block
BOT_READ = (480, 655)  # bottom slice (EXPLOIT 6) read block

_bg = {}


def background():
    if "bg" not in _bg:
        _bg["bg"] = Image.open(BG).convert("RGBA")
    return _bg["bg"].copy()


def tile_xy(i):
    return RX + 10, RY + 40 + i * SLOT


def rack(img, st):
    """st: dict per daemon id -> dict(t, fire, count, spent, hover)."""
    h = 40 + len(RACK) * SLOT + 4
    c = L.CRT(TS + 20, h, L.CYAN, None, header=False, seed=17)
    c.text(((TS + 20) / 2, 10), "DAEMONS", 12, L.CYAN, anchor="ma")
    c.rule(30)
    plate = c.finish(scan=0.12)
    img = L.crt_glow_under(img, (RX, RY, RX + TS + 20, RY + h), L.CYAN, 0.18)
    img.alpha_composite(plate, (RX, RY))
    for i, did in enumerate(RACK):
        s = st.get(did, {})
        x, y = tile_xy(i)
        fire = s.get("fire", 0.0)
        t = F.daemon_tile(did, TS, t=s.get("t", 0.1 * i), fire=fire, spent=s.get("spent", False))
        if fire > 0:
            img.alpha_composite(F._glow(img.size, [x - 14, y - 14, x + TS + 14, y + TS + 14], F.FAM[F.DM[did][3]], 14, fire), (0, 0))
        img.alpha_composite(t, (x, y))
        cs = F.counter_strip(did, TS, s.get("count", 0), fire)
        if cs is not None:
            img.alpha_composite(cs, (x, y + TS + 2))
        if s.get("hover"):
            d = ImageDraw.Draw(img)
            Lb = 12
            for (bx, by, sx, sy) in ((x - 5, y - 5, 1, 1), (x + TS + 4, y - 5, -1, 1), (x - 5, y + TS + 4, 1, -1), (x + TS + 4, y + TS + 4, -1, -1)):
                d.line([(bx, by), (bx + Lb * sx, by)], fill=L.LIME + (255,), width=3)
                d.line([(bx, by), (bx, by + Lb * sy)], fill=L.LIME + (255,), width=3)
    return img


def packet(img, p0, p1, col, u=1.0, k=1.0, bend=-60):
    """Dashed packet line from a tile to what it changes (quadratic bend), with a bright head at u."""
    pts = []
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + bend
    for j in range(31):
        t = j / 30
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * mx + t * t * p1[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * my + t * t * p1[1]
        pts.append((x, y))
    sub = X.sub_path(pts, u)
    m = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(m)
    for j in range(len(sub) - 1):
        if j % 2 == 0:
            d.line([sub[j], sub[j + 1]], fill=255, width=3)
    img = L.SL.over(img, col, m.filter(ImageFilter.GaussianBlur(4)).point(lambda v: min(255, int(v * 2 * k))))
    img = L.SL.over(img, col, m.point(lambda v: int(v * k)))
    if u < 1:
        x, y = sub[-1]
        p = Image.new("L", img.size, 0)
        ImageDraw.Draw(p).ellipse([x - 6, y - 6, x + 6, y + 6], fill=255)
        img = L.SL.over(img, col, p.filter(ImageFilter.GaussianBlur(5)))
        img = L.SL.over(img, (255, 255, 255), p)
    return img


def twin_pointer(img, k=1.0, pulse=0.0):
    """Twin Pointer's second pointer at the bottom of the player wheel, in the daemon's phosphor, sigil on it."""
    col = F.FAM["TURN"]
    x, y = WC[0], WC[1] + 240
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon([(x - 20, y + 40), (x + 20, y + 40), (x, y - 2)], fill=col + (255,), outline=L.INK + (255,))
    d.ellipse([x - 64, y + 6, x - 30, y + 40], fill=(8, 14, 22, 255), outline=col + (255,), width=2)
    m = F.icon("twin_pointer", 22)
    g = Image.new("RGBA", (22, 22), col + (0,))
    g.putalpha(m)
    lay.alpha_composite(g, (int(x - 58), int(y + 12)))
    a = lay.split()[3].point(lambda v: int(v * k))
    lay.putalpha(a)
    if pulse > 0:
        img.alpha_composite(F._glow(img.size, [x - 40, y - 20, x + 40, y + 80], col, 16, pulse))
    img.alpha_composite(lay)
    return img


def drone(img, x, y, k=1.0, drop=0.0):
    """Botnet Seed's 1-HP drone docked on the triggered slice (round 17 drone glyph, Botnet phosphor)."""
    col = F.FAM["PERFECT"]
    g = L.glyph("special_drone", 30, fill=(255, 255, 255), ow=3)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    yy = y - drop
    ImageDraw.Draw(lay).ellipse([x - 22, yy - 22, x + 22, yy + 22], fill=(18, 14, 6, 235), outline=col + (255,), width=3)
    lay.alpha_composite(g, (int(x - g.width / 2), int(yy - g.height / 2)))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([x + 10, yy + 10, x + 34, yy + 26], radius=4, fill=col + (255,))
    d.text((x + 22, yy + 18), "1", font=L.f_num(14), fill=L.INK + (255,), anchor="mm")
    lay.putalpha(lay.split()[3].point(lambda v: int(v * k)))
    img.alpha_composite(lay)
    return img


def tooltip(did, filled):
    _, name, rar, fam, eff, counter = F.DM[did]
    fc = F.FAM[fam]
    c = L.CRT(440, 252, L.CYAN, "%s" % name.upper(), tag=None, seed=23)
    d = c.d
    d.text((300, 20), "DAEMON", font=L.f_mono(13), fill=(120, 170, 190, 255), anchor="rm")
    d.rectangle([310, 9, 392, 31], outline=F.RAR_COL[rar] + (255,), width=1)
    d.text((351, 20), F.RAR_NAME[rar], font=L.f_mono(13), fill=F.RAR_COL[rar] + (255,), anchor="mm")
    rows = [(did, eff, (240, 240, 245)),
            (None, "Streak %d/3: the next Perfect fires it." % filled, fc),
            ("kernel_sync", "PERFECT family: yellow phosphor.", fc),
            (None, "Runs all run. Kept on extraction, lost on death.", (170, 190, 205))]
    y = 54
    for icon, txt, col in rows:
        c.d.rounded_rectangle([14, y, 42, y + 28], radius=4, fill=(14, 20, 30, 255), outline=(60, 90, 110, 255))
        if icon == did:
            m = F.icon(did, 20)
            g = Image.new("RGBA", (20, 20), fc + (0,))
            g.putalpha(m)
            c.paste(g, 18, y + 4)
        elif icon is None and "Streak" in txt:
            for j in range(3):
                c.d.rectangle([18 + j * 7, y + 10, 22 + j * 7, y + 18], fill=(fc if j < filled else tuple(v // 4 for v in fc)) + (255,))
        elif icon is None:
            c.d.ellipse([22, y + 8, 34, y + 20], outline=(170, 190, 205, 255), width=2)
        else:
            c.d.rectangle([20, y + 6, 36, y + 22], fill=fc + (255,))
        for k, ln in enumerate(F.wrap(txt, L.f_ui(18, b"Regular"), 370)[:2]):
            c.d.text((54, y + 3 + k * 20), ln, font=L.f_ui(18, b"Regular"), fill=col + (255,))
        y += 46 if len(F.wrap(txt, L.f_ui(18, b"Regular"), 370)) > 1 else 40
    c.rule(216, dash=True)
    c.text((14, 224), "[RMB] inspect    (Y) codex    drag: n/a", 14, (150, 200, 220))
    return c.finish(scan=0.16)


def perfect_flash(img, k):
    if k <= 0:
        return img
    x, y = WC[0], 238
    img.alpha_composite(F._glow(img.size, [x - 90, y - 40, x + 90, y + 120], (255, 240, 180), 30, 0.9 * k))
    chip = X.term_chip("PERFECT", L.YEL, 18)
    return X.pop(img, chip, x + 150, y - 10, k)


def compose(st, fx_list=(), hover_tip=False, perfect=0.0, twin=(1.0, 0.0), drone_k=0.0, drone_drop=0.0):
    img = background()
    img = perfect_flash(img, perfect)
    img = twin_pointer(img, *twin)
    if drone_k > 0:
        img = drone(img, 572, 262, drone_k, drone_drop)
    img = rack(img, st)
    for fx in fx_list:
        img = fx(img)
    if hover_tip:
        tx, ty = 760, 236
        tp = tooltip("clean_signal", st.get("clean_signal", {}).get("count", 0))
        x, y = tile_xy(1)
        d = ImageDraw.Draw(img)
        d.line([(x + TS + 8, y + TS / 2), (230, y + TS / 2)], fill=L.LIME + (120,), width=2)
        img = L.crt_glow_under(img, (tx, ty, tx + tp.width, ty + tp.height), L.CYAN, 0.2)
        img.alpha_composite(tp, (tx, ty))
        d = ImageDraw.Draw(img)
        d.line([(230, y + TS / 2), (tx, ty + 30)], fill=L.LIME + (90,), width=2)
    return img


def states_inset(img, x0, y0):
    c = L.CRT(380, 296, L.CYAN, "TILE STATES", tag="60 px", seed=29)
    im = c.finish(scan=0.12)
    img.alpha_composite(im, (x0, y0))
    items = [("IDLE", "warm_boot", dict(t=0.5)), ("FIRE", "adrenal_loop", dict(fire=1.0)),
             ("PIPS", "cascade", dict(count=1)), ("STACK", "kernel_sync", dict(count=3)),
             ("ONCE", "stolen_intent", dict(count=0)), ("SPENT", "stolen_intent", dict(count=1, spent=True))]
    d = ImageDraw.Draw(img)
    for k, (lab, did, s) in enumerate(items):
        x = x0 + 22 + (k % 3) * 120
        y = y0 + 52 + (k // 3) * 122
        t = F.daemon_tile(did, TS, t=s.get("t", 0.2), fire=s.get("fire", 0.0), spent=s.get("spent", False))
        if s.get("fire"):
            img.alpha_composite(F._glow(img.size, [x - 12, y - 12, x + TS + 12, y + TS + 12], F.FAM[F.DM[did][3]], 12, 1.0))
        img.alpha_composite(t, (x, y))
        cs = F.counter_strip(did, TS, s.get("count", 0))
        if cs is not None:
            img.alpha_composite(cs, (x, y + TS + 2))
        d = ImageDraw.Draw(img)
        d.text((x + TS + 8, y + 10), lab, font=L.f_num(18), fill=(230, 235, 245, 255))
    return img


def still():
    st = {
        "kernel_sync": dict(fire=1.0, count=3, t=0.02),
        "clean_signal": dict(count=2, hover=True, t=0.3),
        "botnet_seed": dict(fire=0.8, count=1, t=0.02),
        "twin_pointer": dict(t=0.7),
        "stolen_intent": dict(count=0, t=0.5),
        "warm_boot": dict(t=0.9),
    }
    ks = tile_xy(0)
    bs = tile_xy(2)

    def fx_k(c):
        c = packet(c, (ks[0] + TS + 4, ks[1] + TS / 2), (TOP_READ[0] + 40, TOP_READ[1] - 20), F.FAM["PERFECT"], bend=-120)
        return X.pop(c, X.term_chip("+3 DMG", F.FAM["PERFECT"], 16), TOP_READ[0] + 118, TOP_READ[1] - 10)

    def fx_b(c):
        return packet(c, (bs[0] + TS + 4, bs[1] + TS / 2), (560, 268), F.FAM["PERFECT"], bend=-40, k=0.8)

    def fx_t(c):
        c = X.pop(c, X.term_chip("TWIN READ: EXPLOIT 6", F.FAM["TURN"], 14), WC[0] + 190, WC[1] + 262)
        return c
    img = compose(st, (fx_b, fx_k, fx_t), hover_tip=True, perfect=0.6, twin=(1.0, 0.8), drone_k=1.0)
    img = states_inset(img, 760, 520)
    p = L.pen(L.GP_YELLOW, seed=41)
    p.text("2nd pointer", 300, 890, 24, angle=-4)
    p.arrow([(380, 872), (420, 830), (462, 790)], width=5, head=12)
    img = L.ink(img, p)
    L.save(img, "daemon_row.png")


def ease_out(t):
    return 1 - (1 - t) ** 3


def gif():
    crop = (0, 190, 780, 800)
    GK = 0.9
    frames, durs = [], []
    base_st = {"kernel_sync": dict(count=2), "clean_signal": dict(count=2), "botnet_seed": dict(count=0),
               "twin_pointer": dict(), "stolen_intent": dict(count=0), "warm_boot": dict()}

    def snap(st, **kw):
        im = compose(st, **kw).crop(crop).convert("RGB")
        return im.resize((int(im.width * GK), int(im.height * GK)), Image.LANCZOS)

    def S(phase, **over):
        st = {k: dict(v) for k, v in base_st.items()}
        for i, did in enumerate(RACK):
            st[did]["t"] = (phase + i * 0.17) % 1.0
        for k, v in over.items():
            st[k].update(v)
        return st
    ph = 0.0
    # idle
    for f in range(8):
        ph += 0.06
        frames.append(snap(S(ph), twin=(1.0, 0.0)))
        durs.append(80)
    # Perfect lands (+ twin pointer reads the bottom too)
    for f in range(4):
        ph += 0.06
        frames.append(snap(S(ph), perfect=1 - f * 0.15, twin=(1.0, 1 - f * 0.2)))
        durs.append(60)
    ks, cs_, bs = tile_xy(0), tile_xy(1), tile_xy(2)
    # 1 Kernel Sync: fire, packet to the read block, +3
    for f in range(8):
        ph += 0.04
        u = (f + 1) / 8
        fire = 1.0 - f / 10
        cnt = 3 if f >= 4 else 2

        def fx(c, u=u, f=f):
            c = packet(c, (ks[0] + TS + 4, ks[1] + TS / 2), (TOP_READ[0] + 40, TOP_READ[1] - 20), F.FAM["PERFECT"], u=u, bend=-120)
            if f >= 4:
                c = X.pop(c, X.term_chip("+3 DMG", F.FAM["PERFECT"], 16), TOP_READ[0] + 118, TOP_READ[1] - 10)
            return c
        frames.append(snap(S(ph, kernel_sync=dict(fire=fire, count=cnt)), fx_list=(fx,), perfect=0.4))
        durs.append(50)
    # 2 Clean Signal: pip 3 fills -> fires -> -2 HEAT, pips reset
    for f in range(8):
        ph += 0.04
        fire = 1.0 - f / 9
        cnt = 3 if f < 5 else 0

        def fx(c, f=f):
            c = X.pop(c, X.term_chip("+3 DMG", F.FAM["PERFECT"], 16), TOP_READ[0] + 118, TOP_READ[1] - 10, 1 - f / 8)
            return X.pop(c, X.term_chip("CLEAN SIGNAL  -2 HEAT", L.HEAT, 16), cs_[0] + 240, cs_[1] + 30, min(1.0, f / 2), rise=f * 3)
        frames.append(snap(S(ph, kernel_sync=dict(count=3), clean_signal=dict(fire=fire, count=cnt)), fx_list=(fx,)))
        durs.append(55)
    # 3 Botnet Seed: drone drops onto the slice
    for f in range(9):
        ph += 0.04
        u = ease_out((f + 1) / 9)
        fire = 1.0 - f / 10

        def fx(c, u=u):
            return packet(c, (bs[0] + TS + 4, bs[1] + TS / 2), (560, 268), F.FAM["PERFECT"], u=u, bend=-40, k=0.8)
        frames.append(snap(S(ph, kernel_sync=dict(count=3), clean_signal=dict(count=0), botnet_seed=dict(fire=fire, count=1)),
                           fx_list=(fx,), drone_k=min(1.0, u * 1.5), drone_drop=40 * (1 - u)))
        durs.append(50)
    # settle: idle loop with the new state
    for f in range(10):
        ph += 0.06
        frames.append(snap(S(ph, kernel_sync=dict(count=3), clean_signal=dict(count=0), botnet_seed=dict(count=1)), drone_k=1.0))
        durs.append(80)
    durs[-1] = 1200
    pal = Image.new("RGB", (frames[0].width, frames[0].height * 2))
    pal.paste(frames[20], (0, 0))
    pal.paste(frames[38], (0, frames[0].height))
    pal = pal.quantize(colors=200, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [fr.quantize(palette=pal, dither=Image.NONE) for fr in frames]
    path = os.path.join(F.OUT, "daemon_trigger.gif")
    q[0].save(path, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=True, disposal=1)
    print("wrote", path, len(frames), "frames", os.path.getsize(path) / 1e6, "MB")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("still", "all"):
        still()
    if what in ("gif", "all"):
        gif()
