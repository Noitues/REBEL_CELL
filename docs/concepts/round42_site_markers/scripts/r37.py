"""Round 37: hidden nodes by default, calm Heat B, and the mixed transition (terminal connect > wheel lens).

Locked: node outlines option A (normal icon colours, the state is the ring), the node backdrop, Heat B, Exploits on T2.

  city_default.png        only owned, the selectable next Sites, visited (cleared) Sites and the TARGET show
  city_legend_hover.png   the cursor rests on the map legend: every node fades in (white rings = not yet)
  city_node_hover.png     the cursor rests on an empty area: the hidden node under it is revealed with its links
  city_visibility.gif     default > node hover > legend hover > default
  city_heat_calm.png/.gif Heat B calmed: two slow searchlight sweeps, one gentle circling light per hardened node
  transition_mix.gif      terminal connect (typed, binary rain along the link) > the window despawns > the operative's
                          wheel spins up on the link > the wheel-lens zoom into the transit view
  transition_storyboard.png  the same as key frames with timings

python r37.py [vis|heat|mix|all]
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import r31lib as L
import r32ui as U
import r35ui as R
import sticker_lib19 as SL
import city_view as CV
import states36 as S6
import zoom36 as Z

W, H = 1920, 1080
NODES, LINKS = CV.NET
SEL = CV.pick_selected()

# ------------------------------------------------------------------ Exploits back on T2 (GDD 4.1)
for n in NODES.values():
    n.pop("key", None)
_t2 = sorted([k for k in NODES if NODES[k]["tier"] == 2 and NODES[k]["state"] == "white"], key=lambda k: (NODES[k]["xy"][0], k))
for k in (_t2[2], _t2[len(_t2) // 2], _t2[-3]):
    NODES[k]["key"] = True
EXPLOIT_NAMES = ["SHIPPING MANIFESTS", "CUSTOMS OVERRIDE KEYS", "ROGUE ROUTING TABLE"]


def visible(k, mode, hover):
    st = NODES[k]["state"]
    return mode == "all" or st in ("owned", "available", "past") or k == hover


def city_layer(base, mode="default", hover=None, fade=1.0):
    """Option A rings; hidden nodes and their links are not drawn (fade blends the 'all' reveal in)."""
    img = base.copy()
    inl = U.Inlay()
    for a, b in LINKS:
        va, vb = visible(a, mode, hover), visible(b, mode, hover)
        if not (va and vb):
            continue
        st = CV.link_state(NODES, a, b)
        pa, pb = NODES[a]["xy"], NODES[b]["xy"]
        if st == "owned":
            inl.trace([pa, pb], R.LIME, width=2.6, lanes=3, gap=4.5, glow=1.0, pads=False)
        elif st == "border":
            inl.trace([pa, pb], R.MER, width=2.6, lanes=3, gap=4.5, glow=0.9, pads=False)
        elif st == "past":
            inl.trace([pa, pb], R.LIME, width=2.0, lanes=2, gap=4.0, glow=0.3, alpha=0.7, pads=False)
        else:
            inl.trace([pa, pb], R.WHITE, width=1.4, lanes=2, gap=3.5, glow=0.0, alpha=0.5 * fade, pads=False)
    img = inl.lay(img)
    for k in sorted(NODES, key=lambda k: NODES[k]["xy"][1]):
        if not visible(k, mode, hover):
            continue
        n = NODES[k]
        x, y = n["xy"]
        st = n["state"]
        if st == "owned":
            img = U.pad(img, CV.diamond(x, y, 20), R.LIME, lit=1.0, glow=0.7, fill_a=215, k=0.85)
            continue
        kd = S6.kind_of(k, n)
        ic = S6.site_icon(kd, 30 if kd != "key" else 34)
        if st == "white" and fade < 1:
            a = ic.split()[3].point(lambda v: int(v * fade))
            ic.putalpha(a)
        img = U.pad(img, CV.diamond(x, y, 16), (90, 86, 100), lit=0.5 * (fade if st == "white" else 1), glow=0.0, fill_a=int(200 * (fade if st == "white" else 1)),
                    k=0.7, pins=False)
        img.alpha_composite(ic, (int(x - ic.width / 2), int(y - 14 - ic.height / 2)))
        img = S6.ring(img, x, y - 14, ic.width / 2 + 5, S6.STATE_RING[st], w=4 if st != "white" else 3,
                      glow={"available": 0.9, "past": 0.6, "white": 0.0}[st])
        col = (200, 196, 210) if st == "white" else (R.LIME if st == "past" else R.MER)
        img = U.chip(img, (x + 22, y - 30), "T%d" % n["tier"], col, 11, fill_a=225)
    hx, hy = CV.HQ
    img = U.pad(img, CV.diamond(hx, hy + 70, 110), (255, 120, 90), lit=0.6, glow=0.3, fill_a=0, k=1.4)
    pr = L.pen(L.GP_RED, seed=351)
    pr.circle(hx, hy + 30, 190, 120, width=10)
    pr.text("TARGET", hx - 210, hy + 160, 40, angle=-8)
    img = L.ink(img, pr)
    img = U.chip(img, (hx, hy + 170), "CENTRAL SERVER  //  EXPLOITS 0 / 3", R.GOLD, 14)
    img = S6.patrol_affordance(img, "a")
    x, y = NODES[SEL]["xy"]
    d = ImageDraw.Draw(img)
    for (cx, cy, sx, sy) in ((x - 30, y - 46, 1, 1), (x + 30, y - 46, -1, 1), (x - 30, y + 14, 1, -1), (x + 30, y + 14, -1, -1)):
        d.line([(cx, cy), (cx + sx * 12, cy)], fill=R.LIME + (255,), width=3)
        d.line([(cx, cy), (cx, cy + sy * 12)], fill=R.LIME + (255,), width=3)
    return img


def legend(img, hot=False):
    ImageDraw.Draw(img).rectangle([396, 1022, 1484, 1076], fill=(8, 8, 14, 255))
    c = L.CRT(1080, 46, U.LIME if hot else U.CYAN, None, header=False, seed=354)
    x0 = 16
    for col, s in ((R.LIME, "owned / visited"), (R.MER, "selectable"), (R.WHITE, "not yet (hidden)")):
        c.d.ellipse([x0 + 2, 13, x0 + 22, 33], outline=col + (255,), width=3)
        x0 += 30 + int(c.text((x0 + 30, 13), s, 15, (215, 225, 230))) + 24
    c.text((x0 + 10, 13), "|   HOVER HERE: SHOW ALL NODES" if not hot else "|   SHOWING ALL NODES", 15, U.LIME if hot else U.CYAN)
    return L.paste(img, c.finish(scan=0.15), 400, 1026)


def options_inset(img, on=False):
    c = L.CRT(400, 74, U.CYAN, None, header=False, seed=355)
    c.text((14, 12), "OPTIONS > MAP", 14, (150, 190, 200))
    c.text((14, 38), "Always show all nodes", 19, (225, 235, 240))
    c.d.rounded_rectangle([318, 34, 384, 62], radius=14, outline=U.CYAN + (255,), width=2, fill=(R.LIME if on else (30, 34, 44)) + (255,))
    c.d.ellipse([352 if on else 322, 38, 378 if on else 348, 58], fill=(240, 240, 240, 255))
    return L.paste(img, c.finish(scan=0.15), 1498, 970)


def cursor(img, x, y):
    d = ImageDraw.Draw(img)
    pts = [(x, y), (x, y + 30), (x + 8, y + 23), (x + 14, y + 36), (x + 20, y + 33), (x + 14, y + 21), (x + 24, y + 21)]
    d.polygon([(px + 2, py + 3) for px, py in pts], fill=(0, 0, 0, 140))
    d.polygon(pts, fill=(250, 250, 250, 255), outline=(10, 10, 14, 255))
    return img


def hud(img, sel, legend_hot=False, opt_on=False):
    img = S6.hud_heat_b(img, sel)
    img = legend(img, legend_hot)
    return options_inset(img, opt_on)


_base = {}


def base():
    if "b" not in _base:
        _base["b"] = CV.base_map()
    return _base["b"]




def hover_pick():
    """A hidden Exploit Site (T2) near the frontier: the interesting one to reveal."""
    ks = [k for k in NODES if NODES[k].get("key")]
    return sorted(ks, key=lambda k: NODES[k]["xy"][0])[0]


def tooltip(img, k):
    x, y = NODES[k]["xy"]
    n = NODES[k]
    lines = ["T%d  //  EXPLOIT: %s" % (n["tier"], EXPLOIT_NAMES[0]) if n.get("key") else "T%d SITE" % n["tier"], "not yet available: claim a neighbour first"]
    c = L.CRT(470, 74, R.WHITE, None, header=False, seed=356)
    c.text((14, 12), lines[0], 17, R.GOLD if n.get("key") else (230, 230, 240))
    c.text((14, 42), lines[1], 14, (190, 196, 210))
    return L.paste(img, c.finish(scan=0.15), x + 40, y - 110)


def frame(mode="default", hover=None, cur=None, fade=1.0, legend_hot=False):
    img = city_layer(base(), mode, hover, fade)
    img = CV.pan_cues(img)
    img = hud(img, SEL, legend_hot)
    if hover:
        img = tooltip(img, hover)
    if cur:
        img = cursor(img, *cur)
    return img


def vis():
    hv = hover_pick()
    hx, hy = NODES[hv]["xy"]
    d0 = frame()
    L.save(L.bloom(d0, 0.12, 0.82, 8), "city_default.png")
    nh = frame(hover=hv, cur=(hx + 6, hy - 6))
    L.save(L.bloom(nh, 0.12, 0.82, 8), "city_node_hover.png")
    lh = frame("all", cur=(1220, 1040), legend_hot=True)
    L.save(L.bloom(lh, 0.12, 0.82, 8), "city_legend_hover.png")
    frames, durs = [d0], [1400]
    for t in (0.4, 0.8):
        frames.append(frame(cur=(1500 + (hx - 1500) * t, 900 + (hy - 900) * t)))
        durs.append(160)
    frames.append(nh)
    durs.append(1800)
    for t in (0.5,):
        frames.append(frame(cur=(hx + (1220 - hx) * t, hy + (1040 - hy) * t)))
        durs.append(160)
    frames.append(frame("all", cur=(1220, 1040), fade=0.5, legend_hot=True))
    durs.append(140)
    frames.append(lh)
    durs.append(1800)
    out = os.path.join(L.OUT, "city_visibility.gif")
    print("wrote", out, U.save_gif([f.convert("RGB") for f in frames], durs, out, size=(960, 540)))


# ------------------------------------------------------------------ Heat B, calm
def hot():
    av = sorted([k for k in NODES if NODES[k]["state"] == "available"], key=lambda k: (NODES[k]["xy"][0], k))
    picks = [av[1], av[-2]]
    return list(zip(picks, ["+1 ELITE", "+1 RESISTANCE"]))


def calm_ring(img, x, y, ang, r=46):
    W_, H_ = img.size
    m = Image.new("L", (W_, H_), 0)
    ImageDraw.Draw(m).ellipse([x - r, y - r * 0.55, x + r, y + r * 0.55], outline=200, width=2)
    img = SL.over(img, S6.HEATC, m)
    g = Image.new("L", (W_, H_), 0)
    ImageDraw.Draw(g).ellipse([x - 54, y - 34, x + 54, y + 22], fill=90)
    img = SL.over(img, S6.HEATC, g.filter(ImageFilter.GaussianBlur(16)))
    # one soft light travelling round the ring, red and blue alternating per half turn
    col = (255, 60, 60) if math.cos(ang) > 0 else (80, 130, 255)
    px, py = x + r * math.cos(ang), y + r * 0.55 * math.sin(ang)
    g = Image.new("L", (W_, H_), 0)
    ImageDraw.Draw(g).ellipse([px - 14, py - 9, px + 14, py + 9], fill=150)
    return SL.over(img, col, g.filter(ImageFilter.GaussianBlur(7)))


def heat_calm():
    hs = hot()
    base_img = city_layer(base(), "default")
    base_img = CV.pan_cues(base_img)
    frames = []
    N = 12
    for f in range(N):
        t = f / N
        img = base_img.copy()
        beams = []
        for i, (sx, sy, cx, cy, amp) in enumerate(((1820, -80, 1000, 420, 260), (240, -90, 700, 640, 200))):
            a = math.sin(2 * math.pi * t + i * 1.7)
            beams.append((sx, sy, cx + amp * a, cy + 60 * math.cos(2 * math.pi * t + i), 85))
        img = R.heat_diegetic(img, beams, [], k=0.6)
        img = L.vignette(img, 0.25, color=(60, 18, 4))
        for i, (k, lab) in enumerate(hs):
            x, y = NODES[k]["xy"]
            img = calm_ring(img, x, y - 14, 2 * math.pi * t + i * math.pi / 2)
            img = U.chip(img, (x, y + 30), "HEAT: " + lab, S6.HEATC, 13, bright=True)
        img = hud(img, SEL)
        frames.append(img)
    L.save(L.bloom(frames[0], 0.12, 0.82, 8), "city_heat_calm.png")
    out = os.path.join(L.OUT, "city_heat_calm.gif")
    print("wrote", out, U.save_gif([f.convert("RGB") for f in frames], [220] * N, out, size=(800, 450)))


# ------------------------------------------------------------------ the mixed transition
def term_panel(n_lines, cursor_on=True):
    c = L.CRT(720, 220, R.LIME, "CELL://JACK", tag="CELL-9", seed=97)
    for i, ln in enumerate(Z.LINES[:n_lines]):
        c.text((20, 56 + i * 36), ln, 22, R.LIME if not ln.startswith("> C") else (255, 255, 255))
    if cursor_on:
        last = Z.LINES[n_lines - 1]
        c.d.rectangle([20 + 13 * len(last), 56 + (n_lines - 1) * 36, 34 + 13 * len(last), 80 + (n_lines - 1) * 36], fill=R.LIME + (255,))
    return c.finish()


def with_term(img, panel, sy=1.0, sx=1.0, alpha=1.0):
    im = img.convert("RGBA")
    w, h = max(2, int(panel.width * sx)), max(2, int(panel.height * sy))
    p = panel.resize((w, h), Image.BILINEAR)
    if alpha < 1:
        p.putalpha(p.split()[3].point(lambda v: int(v * alpha)))
    im.alpha_composite(p, (int(600 + (720 - w) / 2), int(420 + (220 - h) / 2)))
    return im


def link_rain(img, a, b, t, seed=7):
    """Binary rain only along the link: columns between the two ends, heads sliding down onto the link line."""
    rng = random.Random(seed)
    im = img.convert("RGBA")
    d = ImageDraw.Draw(im)
    f = L.f_mono(18)
    x0, x1 = min(a[0], b[0]) - 40, max(a[0], b[0]) + 40
    for col in range(int(x0), int(x1), 18):
        u = (col - a[0]) / (b[0] - a[0] or 1)
        ly = a[1] + (b[1] - a[1]) * min(1, max(0, u))
        head = ly - 260 + t * 320 + rng.uniform(-40, 40)
        for k in range(14):
            y = min(head, ly) - k * 20
            v = max(0, 255 - k * 18)
            d.text((col, y), rng.choice("01"), font=f, fill=(255, 255, 255, v) if k == 0 else (212, 255, 0, v))
    return im


def spin_blur(city, inner, c, ro, ri, rot, spread):
    fr = [np.asarray(Z.lens_frame(city, inner, c, ro, ri, rot + s, 1), np.float32) for s in np.linspace(0, spread, 4)]
    return Image.fromarray(np.clip(sum(fr) / len(fr), 0, 255).astype(np.uint8))


def mix():
    city = frame().convert("RGB")
    tr = S6.transit_png("a", label=False).convert("RGB")
    nb = [a_ if b_ == SEL else b_ for (a_, b_) in LINKS if SEL in (a_, b_) and NODES[a_ if b_ == SEL else b_]["state"] == "owned"][0]
    a, b = NODES[nb]["xy"], NODES[SEL]["xy"]
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 10)
    frames, durs, beats = [], [], []

    def add(im, ms, beat=None):
        frames.append(im.convert("RGB"))
        durs.append(ms)
        if beat:
            beats.append((len(frames) - 1, beat, ms))

    add(city, 800, "0  JACK IN pressed")
    # 1) terminal connect
    for n in (1, 2, 3):
        add(with_term(city, term_panel(n)), 200, "1  terminal types the connection" if n == 1 else None)
    full = term_panel(4, cursor_on=False)
    for i, t in enumerate((0.3, 0.65, 1.0)):
        add(link_rain(with_term(city, full), a, b, t), 120, "2  CONNECTED: binary rain runs down the link" if i == 0 else None)
    # 2) the window despawns (CRT collapse: squash to a line, then a dot)
    rained = link_rain(city, a, b, 1.0)
    for i, (sx, sy) in enumerate(((1.0, 0.25), (1.0, 0.03), (0.05, 0.03))):
        add(with_term(rained, full, sy=sy, sx=sx), 70, "3  the terminal window despawns" if i == 0 else None)
    # 3) the operative's wheel spins up on the link (slap in, then faster spins, blurred)
    add(Z.lens_frame(city, city, mid, 200, 64, -20, 1), 90, "4  the operative's wheel slaps onto the link and spins up")
    add(Z.lens_frame(city, city, mid, 150, 48, 0, 1), 110)
    for rot, spread in ((40, 10), (110, 30), (220, 60)):
        add(spin_blur(city, city, mid, 150, 48, rot, spread), 90)
    # 4) wheel lens: the hub opens on the link, the ring flies past the camera
    for k, ro in enumerate((220, 420, 820, 1500)):
        c = (mid[0] + (960 - mid[0]) * (k + 1) / 4, mid[1] + (540 - mid[1]) * (k + 1) / 4)
        add(spin_blur(city, tr, c, ro, ro * 0.62, 300 + 60 * k, 40), 90, "5  wheel lens: the hub opens onto the transit view" if k == 0 else None)
    add(tr, 1600, "6  the run")
    out = os.path.join(L.OUT, "transition_mix.gif")
    size = U.save_gif(frames, durs, out, size=(800, 450))
    if size > 4_000_000:
        size = U.save_gif(frames, durs, out, size=(720, 405))
    print("wrote", out, size, "total ms", sum(durs))
    storyboard(frames, durs, beats)


def storyboard(frames, durs, beats):
    img = Image.new("RGBA", (W, H), (9, 8, 14, 255))
    img = L.place_sticker(img, L.sticker_word(["JACK IN: CONNECT > SPIN > LENS"], 44, fills=["yellow"], seed=71), 520, 52, angle=-2)
    tw, th = 440, 248
    t_ms = 0
    starts = []
    for i, d in enumerate(durs):
        starts.append(t_ms)
        t_ms += d
    for n, (idx, text, ms) in enumerate(beats):
        x = 22 + (n % 4) * (tw + 30)
        y = 110 + (n // 4) * (th + 230)
        img.alpha_composite(frames[idx].resize((tw, th), Image.LANCZOS).convert("RGBA"), (x, y))
        d = ImageDraw.Draw(img)
        d.rectangle([x, y, x + tw, y + th], outline=U.CYAN + (255,), width=2)
        words, line, lines = text.split(" "), "", []
        for wd in words:
            if len(line + " " + wd) > 40:
                lines.append(line)
                line = wd
            else:
                line = (line + " " + wd).strip()
        lines.append(line)
        for k, ln in enumerate(lines):
            d.text((x, y + th + 14 + k * 26), ln, font=L.f_ui(21, b"SemiBold"), fill=(235, 235, 240, 255))
        d.text((x, y + th + 14 + len(lines) * 26 + 6), "t = %.2f s" % (starts[idx] / 1000), font=L.f_mono(16), fill=U.CYAN + (255,))
    c = L.CRT(W - 44, 60, U.LIME, None, header=False, seed=72)
    c.text((16, 18), "total about %.1f s, skippable at any beat (Skip snaps to the run). Beats 1-3 can be cut to 0.6 s once players know them." % (t_ms / 1000), 17,
           (225, 240, 225))
    img = L.paste(img, c.finish(scan=0.15), 22, 1004)
    L.save(img, "transition_storyboard.png")


if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv) > 1 else "all"
    if w in ("vis", "all"):
        vis()
    if w in ("heat", "all"):
        heat_calm()
    if w in ("mix", "all"):
        mix()
