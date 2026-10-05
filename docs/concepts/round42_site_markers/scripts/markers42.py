"""Round 42: City Grid SITE MARKERS: one system for every Site kind x status (GDD 3.3, 4.1; RC.SiteObjective).

Anatomy (bottom to top, all in the locked languages):
  1 PAD     the raid socket on the street (circuit inlay). Its colour = OWNERSHIP:
              corporate = dark pad, corp-orange pins | claimed = the Cell's lime raid node | seized = corp pad + red pins
  2 ICON    a disc in NORMAL colours (option A) = KIND (RC.SiteObjective):
              NONE regular Site    corp crest (Meridian crane-A, corp orange)
              EXPLOIT (T2)         gold key plate + the Exploit type glyph (INTEL magnifier / BREACH key / VIRUS bug)
              HEAT_REDUCTION       the dark-orange flame (Heat B colour)
              BOSS (corp HQ)       the corp HQ itself (landmark) + the red pencil TARGET circle; no disc
              CORE (home server)   the Cell's heart on a lime pad
  3 RING    option A state ring = AVAILABILITY: white = not yet | ORANGE = selectable (run now) | LIME = visited / yours
  4 PIPS    TIER: 1-3 square pips under the disc (T4 = the boss, no pips; it has the TARGET circle)
  5 BADGE   STATUS corner badge (top right of the disc), only when not plain corporate:
              CLEARED  grey check (disc greys, ring lime, PATROL on hover)  | CLAIMED  the disc becomes the Cell node icon
              SEIZED   red slash + RECLAIM run (ring orange when reclaimable) | DISABLED amber hazard, the claimed node's
              health fill drained (raid node health v2)
  LINKS     open = inlay traces (lime owned, orange border, white not-yet); LOCKED cross-link = grey dashes + a padlock
            disc at its midpoint (opens with an Intel Exploit or an objective)
Hidden-nodes rule (round 37), refined: regular Sites that are not next are hidden; objective Sites (Exploit, Heat
objective) stay PINNED as small white-ring markers so the campaign goals are always visible.
UI never sits on grease pencil: chips are placed clear of the TARGET circle and its word.

python markers42.py [key|map|all]
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

import r31lib as RL
import r32ui as U
import r35ui as R
import sticker_lib19 as SL
import city_view as CV
import route_d_city as RC_

MER, LIME, WHITE, GOLD = R.MER, R.LIME, R.WHITE, R.GOLD
GREY = (130, 126, 140)
RED = (255, 44, 52)
AMBER = (255, 176, 0)
HEATC = (206, 84, 18)
OUT = RL.OUT


# ------------------------------------------------------------------ parts
def disc(kind, px, exploit=None, status="corporate"):
    S = 4
    P = px * S
    im = Image.new("RGBA", (P, P), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fill = {"site": (30, 22, 18), "exploit": (70, 50, 8), "heat": (60, 22, 8)}[kind]
    d.ellipse([S, S, P - S, P - S], fill=fill + (255,), outline=(10, 9, 12, 255), width=2 * S)
    if kind == "site":
        s = P * 0.3
        c = (P / 2, P / 2 + S)
        d.line([(c[0] - s * 0.8, c[1] + s * 0.7), (c[0], c[1] - s), (c[0] + s * 0.8, c[1] + s * 0.7)], fill=MER + (255,), width=3 * S)
        d.line([(c[0] - s * 0.45, c[1] + s * 0.1), (c[0] + s * 0.45, c[1] + s * 0.1)], fill=MER + (255,), width=2 * S)
        d.line([(c[0] - s * 1.1, c[1] - s * 0.55), (c[0] + s * 1.2, c[1] - s * 0.75)], fill=MER + (255,), width=2 * S)
    elif kind == "exploit":
        g = RL.glyph("placeholder_key", int(P * 0.58), fill=GOLD, ow=0)
        im.alpha_composite(g, ((P - g.width) // 2 - int(P * 0.06), (P - g.height) // 2))
        if exploit:
            gname = {"INTEL": "placeholder_recon", "BREACH": "placeholder_key", "VIRUS": "slice_virus"}[exploit]
            r = P * 0.25
            cx, cy = P * 0.72, P * 0.7
            d = ImageDraw.Draw(im)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(18, 14, 4, 255), outline=GOLD + (255,), width=S)
            g2 = RL.glyph(gname, int(r * 1.4), fill=(255, 236, 170), ow=0)
            im.alpha_composite(g2, (int(cx - g2.width / 2), int(cy - g2.height / 2)))
    elif kind == "heat":
        g = RL.glyph("placeholder_burn", int(P * 0.62), fill=(255, 140, 50), ow=0)
        im.alpha_composite(g, ((P - g.width) // 2, (P - g.height) // 2))
    im = im.resize((px, px), Image.LANCZOS)
    if status == "cleared":
        a = im.split()[3]
        im = ImageEnhance.Brightness(im.convert("L").convert("RGB")).enhance(0.8).convert("RGBA")
        im.putalpha(a)
    return im


def cell_disc(kind, px, status="claimed"):
    """A claimed Site is a Cell raid node: lime pad icon (round 19/21 node key)."""
    S = 4
    P = px * S
    im = Image.new("RGBA", (P, P), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([S, S, P - S, P - S], fill=(16, 26, 4, 255), outline=(10, 9, 12, 255), width=2 * S)
    ic = RC_.cell_icon(kind, int(P * 0.62), LIME if status != "disabled" else AMBER)
    im.alpha_composite(ic, ((P - ic.width) // 2, (P - ic.height) // 2))
    im = im.resize((px, px), Image.LANCZOS)
    if status == "disabled":                      # health v2: the fill drains north -> south; the outline stays lit
        m = Image.new("L", (px, px), 0)
        ImageDraw.Draw(m).rectangle([0, 0, px, int(px * 0.62)], fill=150)
        dark = Image.new("RGBA", (px, px), (4, 4, 8, 255))
        dark.putalpha(ImageChops.multiply(m, im.split()[3]))
        im.alpha_composite(dark)
    return im


def pad(img, x, y, r, own, k=1.0):
    q = CV.diamond(x, y, r)
    col = {"corporate": MER, "claimed": LIME, "seized": RED, "cleared": GREY, "disabled": AMBER}[own]
    return U.pad(img, q, col, lit={"corporate": 0.7, "claimed": 1.0, "seized": 1.0, "cleared": 0.6, "disabled": 1.0}[own],
                 glow={"claimed": 0.7, "seized": 0.6, "disabled": 0.7}.get(own, 0.2), fill_a=215, k=0.85 * k)


def ring(img, x, y, r, col, w=4, glow=0.7):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse([x - r, y - r, x + r, y + r], outline=255, width=w)
    if glow:
        img = SL.over(img, col, SL.scale_mask(m.filter(ImageFilter.GaussianBlur(5)), glow))
    img = SL.over(img, (6, 5, 10), SL.shift(m, 1, 2))
    return SL.over(img, col, m)


def pips(img, x, y, n, col, s=5, gap=4):
    d = ImageDraw.Draw(img)
    w = n * s + (n - 1) * gap
    for i in range(n):
        x0 = x - w / 2 + i * (s + gap)
        d.rectangle([x0 - 1, y - 1, x0 + s + 1, y + s + 1], fill=(8, 8, 12, 255))
        d.rectangle([x0, y, x0 + s, y + s], fill=col + (255,))
    return img


def badge(img, x, y, status, r=10):
    d = ImageDraw.Draw(img)
    if status == "cleared":
        d.ellipse([x - r, y - r, x + r, y + r], fill=(40, 40, 48, 255), outline=(200, 200, 210, 255), width=2)
        d.line([(x - r * 0.5, y), (x - r * 0.1, y + r * 0.45), (x + r * 0.55, y - r * 0.45)], fill=(230, 230, 240, 255), width=3)
    elif status == "seized":
        d.ellipse([x - r, y - r, x + r, y + r], fill=(60, 6, 10, 255), outline=RED + (255,), width=2)
        d.line([(x - r * 0.5, y - r * 0.5), (x + r * 0.5, y + r * 0.5)], fill=RED + (255,), width=3)
        d.line([(x - r * 0.5, y + r * 0.5), (x + r * 0.5, y - r * 0.5)], fill=RED + (255,), width=3)
    elif status == "disabled":
        d.polygon([(x, y - r), (x + r, y + r * 0.8), (x - r, y + r * 0.8)], fill=AMBER + (255,), outline=(20, 14, 0, 255))
        d.text((x, y + r * 0.15), "!", font=RL.f_num(int(r * 1.4)), fill=(20, 14, 0, 255), anchor="mm")
    return img


AVAIL = {"next": MER, "notyet": WHITE, "yours": LIME}


def marker(img, x, y, kind, tier, status="corporate", avail="next", exploit=None, scale=1.0, label=None):
    """Draw one Site marker at street point (x, y). kind: site | exploit | heat | core | boss."""
    k = scale
    if kind == "core":
        img = pad(img, x, y, 26 * k, "claimed", k)
        ic = cell_disc("home", int(34 * k))
        img.alpha_composite(ic, (int(x - ic.width / 2), int(y - 16 * k - ic.height / 2)))
        img = ring(img, x, y - 16 * k, ic.width / 2 + 5, LIME, w=4, glow=0.9)
        return img
    own = {"claimed": "claimed", "disabled": "disabled", "seized": "seized", "cleared": "cleared"}.get(status, "corporate")
    img = pad(img, x, y, (17 if avail != "notyet" else 14) * k, own, k)
    px = int((30 if kind != "exploit" else 34) * k * (0.85 if avail == "notyet" else 1.0))
    if status in ("claimed", "disabled"):
        ic = cell_disc({"site": "relay", "exploit": "relay", "heat": "relay"}[kind], px, status)
        avail = "yours"
    else:
        ic = disc(kind, px, exploit, status)
    cy = y - 15 * k
    img.alpha_composite(ic, (int(x - ic.width / 2), int(cy - ic.height / 2)))
    rc = AVAIL[avail]
    if status == "cleared":
        rc = LIME
    if status == "seized":
        rc = MER if avail == "next" else WHITE
    if status == "disabled":
        rc = AMBER
    img = ring(img, x, cy, ic.width / 2 + 5, rc, w=4 if avail != "notyet" else 3, glow={"next": 0.9, "yours": 0.6}.get(avail, 0.0))
    if tier and status not in ("claimed", "disabled"):
        img = pips(img, x, cy + ic.width / 2 + 9, tier, GOLD if kind == "exploit" else (rc if avail != "notyet" else (210, 206, 220)),
                   s=int(5 * k), gap=int(3 * k))
    if status in ("cleared", "seized", "disabled"):
        img = badge(img, x + ic.width / 2 + 2, cy - ic.width / 2 + 2, status, r=int(9 * k))
    if label:
        img = U.chip(img, (x, y + 26 * k), label, rc if rc != WHITE else (220, 218, 228), int(12 * k), fill_a=230)
    return img


def locked_link(img, a, b, k=1.0):
    d = ImageDraw.Draw(img)
    pts = [a, b]
    tot = U.polyline_len(pts)
    s = 0
    while s < tot:
        seg = U.cut_poly(pts, s / tot, min(1, (s + 10) / tot))
        if len(seg) > 1:
            d.line(seg, fill=(150, 146, 168, 210), width=3)
        s += 18
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    r = 13 * k
    d.ellipse([mx - r, my - r, mx + r, my + r], fill=(24, 22, 32, 255), outline=(170, 166, 186, 255), width=2)
    g = RL.glyph("state_locked", int(r * 1.3), fill=(220, 216, 232), ow=0)
    img.alpha_composite(g, (int(mx - g.width / 2), int(my - g.height / 2)))
    return img


# ------------------------------------------------------------------ the key sheet
def key_sheet():
    W, H = 1920, 1080
    img = Image.new("RGBA", (W, H), (12, 11, 18, 255))
    # a dim street texture behind the cells (the markers sit on streets)
    bg = CV.base_map()
    bg = ImageEnhance.Brightness(bg).enhance(0.38).filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, bg)
    img = RL.place_sticker(img, RL.sticker_word(["SITE MARKERS"], 52, fills=["yellow"], seed=42), 210, 52, angle=-2)
    d = ImageDraw.Draw(img)
    d.text((420, 52), "KIND = icon   AVAILABILITY = ring (option A)   TIER = pips   STATUS = pad + corner badge", font=RL.f_ui(24, b"SemiBold"),
           fill=(235, 235, 240, 255), anchor="lm")
    cols = [("CORPORATE", "not yet", dict(status="corporate", avail="notyet")),
            ("CORPORATE", "selectable", dict(status="corporate", avail="next")),
            ("CLEARED", "used up, patrol", dict(status="cleared", avail="yours")),
            ("CLAIMED", "your node", dict(status="claimed", avail="yours")),
            ("DISABLED", "claimed, 0 integrity", dict(status="disabled", avail="yours")),
            ("SEIZED", "reclaim run", dict(status="seized", avail="next"))]
    rows = [("REGULAR SITE", "T1-T3 pips", dict(kind="site", tier=1)),
            ("", "", dict(kind="site", tier=3)),
            ("EXPLOIT SITE", "T2, gold key + type", dict(kind="exploit", tier=2, exploit="INTEL")),
            ("HEAT OBJECTIVE", "flame (Heat B)", dict(kind="heat", tier=1))]
    x0, y0, cw, rh = 340, 150, 228, 118
    for j, (t, sub, _) in enumerate(cols):
        x = x0 + j * cw
        d.text((x, y0 - 12), t, font=RL.f_ui(20, b"Bold"), fill=U.CYAN + (255,), anchor="mm")
        d.text((x, y0 + 12), sub, font=RL.f_mono(14), fill=(170, 190, 200, 255), anchor="mm")
    for i, (t, sub, kw) in enumerate(rows):
        y = y0 + 90 + i * rh
        d = ImageDraw.Draw(img)
        if t:
            d.text((30, y - 26), t, font=RL.f_ui(21, b"Bold"), fill=(235, 235, 240, 255))
            d.text((30, y + 2), sub, font=RL.f_mono(14), fill=(170, 190, 200, 255))
        for j, (_, _, kc) in enumerate(cols):
            x = x0 + j * cw
            img = marker(img, x, y + 18, kw["kind"], kw["tier"], kc["status"], kc["avail"], kw.get("exploit"), scale=1.0)
    # second band: exploit types, close zoom, CORE, BOSS, locked link
    yb = 700
    d = ImageDraw.Draw(img)
    d.line([(24, yb - 34), (W - 24, yb - 34)], fill=(70, 70, 90, 255), width=1)
    d.text((30, yb), "EXPLOIT TYPE", font=RL.f_ui(21, b"Bold"), fill=(235, 235, 240, 255))
    for i, ex in enumerate(("INTEL", "BREACH", "VIRUS")):
        x = 120 + i * 120
        img = marker(img, x, yb + 110, "exploit", 2, "corporate", "next", ex)
        ImageDraw.Draw(img).text((x, yb + 160), ex, font=RL.f_mono(14), fill=GOLD + (255,), anchor="mm")
    d = ImageDraw.Draw(img)
    d.text((500, yb), "CLOSE ZOOM (x1.7, labels)", font=RL.f_ui(21, b"Bold"), fill=(235, 235, 240, 255))
    img = marker(img, 600, yb + 120, "site", 2, "corporate", "next", label="T2  CUSTOMS 22", scale=1.7)
    img = marker(img, 820, yb + 120, "exploit", 2, "corporate", "notyet", "BREACH", label="CUSTOMS KEYS", scale=1.7)
    img = marker(img, 1040, yb + 120, "heat", 1, "cleared", "yours", label="SCRUB RECORDS", scale=1.7)
    d = ImageDraw.Draw(img)
    d.text((1180, yb), "CORE", font=RL.f_ui(21, b"Bold"), fill=(235, 235, 240, 255))
    img = marker(img, 1240, yb + 110, "core", 0)
    d = ImageDraw.Draw(img)
    d.text((1360, yb), "BOSS (T4)", font=RL.f_ui(21, b"Bold"), fill=(235, 235, 240, 255))
    pr = RL.pen(RL.GP_RED, seed=421)
    pr.circle(1450, yb + 100, 70, 46, width=8)
    pr.text("TARGET", 1440, yb + 186, 26, angle=-6)
    img = U.pad(img, CV.diamond(1450, yb + 110, 52), (255, 120, 90), lit=0.6, glow=0.3, fill_a=0, k=1.0)
    img = RL.ink(img, pr)
    img = U.chip(img, (1450, yb + 36), "CENTRAL SERVER // EXPLOITS 1/3", GOLD, 12)
    d = ImageDraw.Draw(img)
    d.text((1640, yb), "LOCKED LINK", font=RL.f_ui(21, b"Bold"), fill=(235, 235, 240, 255))
    img = locked_link(img, (1620, yb + 150), (1860, yb + 70))
    # rules strip
    c = RL.CRT(1876, 104, U.CYAN, "RULES", seed=43)
    c.text((16, 50), "Hidden by default: regular Sites that are not selectable. PINNED (always shown): Exploit, Heat objective, the boss, your", 15, (220, 232, 238))
    c.text((16, 74), "nodes. Seized Sites next to you are raid entry points (red pins). Pips: tier 1-3; the boss has the TARGET circle.", 15, (220, 232, 238))
    img = RL.paste(img, c.finish(scan=0.15), 22, 960)
    RL.save(img, "site_markers.png")


# ------------------------------------------------------------------ on the map
def on_map():
    nodes, links = CV.NET
    img = CV.base_map()
    rng = random.Random(42)
    # roles on the round 35 network
    owned = sorted([k for k in nodes if nodes[k]["state"] == "owned"], key=lambda k: (nodes[k]["p"], k))
    core = owned[0]
    disabled = owned[len(owned) // 2]
    avail = sorted([k for k in nodes if nodes[k]["state"] == "available"], key=lambda k: (nodes[k]["xy"][0], k))
    seized = avail[2]
    heat_av = avail[-1]
    white = [k for k in nodes if nodes[k]["state"] == "white"]
    t2 = sorted([k for k in white if nodes[k]["tier"] == 2], key=lambda k: (nodes[k]["xy"][0], k))
    exploits = {t2[2]: "INTEL", t2[len(t2) // 2]: "BREACH", t2[-3]: "VIRUS"}
    heat_pins = sorted([k for k in white if k not in exploits], key=lambda k: (nodes[k]["p"], k))
    heat_pins = [heat_pins[len(heat_pins) // 3], heat_pins[2 * len(heat_pins) // 3]]
    past = [k for k in nodes if nodes[k]["state"] == "past"]
    shown = set(owned) | set(avail) | set(past) | set(exploits) | set(heat_pins)
    # links: owned lime, border orange, others only between shown ones; one locked cross-link
    inl = U.Inlay()
    for a, b in links:
        if a not in shown or b not in shown:
            continue
        st = CV.link_state(nodes, a, b)
        pa, pb = nodes[a]["xy"], nodes[b]["xy"]
        col = {"owned": LIME, "border": MER, "past": LIME}.get(st, WHITE)
        inl.trace([pa, pb], col, width=2.6 if st in ("owned", "border") else 1.6, lanes=3 if st in ("owned", "border") else 2, gap=4.5,
                  glow=0.9 if st in ("owned", "border") else 0.1, alpha=1.0 if st in ("owned", "border", "past") else 0.6, pads=False)
    img = inl.lay(img)
    lk = sorted(exploits)[0]
    nb2 = min((k for k in avail if k != seized), key=lambda k: math.hypot(nodes[k]["xy"][0] - nodes[lk]["xy"][0], nodes[k]["xy"][1] - nodes[lk]["xy"][1]))
    img = locked_link(img, nodes[nb2]["xy"], nodes[lk]["xy"])
    for k in sorted(shown, key=lambda k: nodes[k]["xy"][1]):
        x, y = nodes[k]["xy"]
        n = nodes[k]
        if k == core:
            img = marker(img, x, y, "core", 0)
        elif k == disabled:
            img = marker(img, x, y, "site", 0, "disabled")
        elif n["state"] == "owned":
            img = marker(img, x, y, "site", 0, "claimed")
        elif k == seized:
            img = marker(img, x, y, "site", n["tier"], "seized", "next")
        elif k == heat_av:
            img = marker(img, x, y, "heat", n["tier"], "corporate", "next")
        elif n["state"] == "available":
            img = marker(img, x, y, "site", n["tier"], "corporate", "next")
        elif n["state"] == "past":
            img = marker(img, x, y, "site", n["tier"], "cleared", "yours")
        elif k in exploits:
            img = marker(img, x, y, "exploit", 2, "corporate", "notyet", exploits[k], scale=0.9)
        elif k in heat_pins:
            img = marker(img, x, y, "heat", n["tier"], "corporate", "notyet", scale=0.9)
    # the boss: TARGET circle (pencil) + its chip placed clear of the pencil
    hx, hy = CV.HQ
    img = U.pad(img, CV.diamond(hx, hy + 70, 110), (255, 120, 90), lit=0.6, glow=0.3, fill_a=0, k=1.4)
    pr = RL.pen(RL.GP_RED, seed=351)
    pr.circle(hx, hy + 30, 190, 120, width=10)
    pr.text("TARGET", hx - 210, hy + 160, 40, angle=-8)
    img = RL.ink(img, pr)
    img = U.chip(img, (hx + 40, hy + 205), "CENTRAL SERVER  //  EXPLOITS 0 / 3", GOLD, 14)
    img = CV.pan_cues(img)
    # a compact key strip (no panels on the pencil)
    c = RL.CRT(1500, 50, U.CYAN, None, header=False, seed=44)
    xk = 14
    for lab, f in (("next", lambda im, x: marker(im, x, 34, "site", 1, "corporate", "next", scale=0.55)),
                   ("cleared", lambda im, x: marker(im, x, 34, "site", 1, "cleared", "yours", scale=0.55)),
                   ("yours", lambda im, x: marker(im, x, 34, "site", 0, "claimed", scale=0.55)),
                   ("disabled", lambda im, x: marker(im, x, 34, "site", 0, "disabled", scale=0.55)),
                   ("seized", lambda im, x: marker(im, x, 34, "site", 1, "seized", "next", scale=0.55)),
                   ("exploit", lambda im, x: marker(im, x, 34, "exploit", 2, "corporate", "notyet", "INTEL", scale=0.55)),
                   ("heat obj.", lambda im, x: marker(im, x, 34, "heat", 1, "corporate", "notyet", scale=0.55))):
        c.im = f(c.im, xk + 16)
        c.d = ImageDraw.Draw(c.im)
        xk += 34 + int(c.text((xk + 34, 15), lab, 15, (215, 225, 230))) + 18
    c.text((xk + 4, 15), "| locked link: grey dashes + padlock   | HOVER: SHOW ALL", 15, U.CYAN)
    img = RL.paste(img, c.finish(scan=0.15), 210, 1018)
    RL.save(RL.bloom(img, 0.12, 0.82, 8), "site_markers_on_map.png")
    return dict(core=core, disabled=disabled, seized=seized, exploits=exploits)


if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv) > 1 else "all"
    if w in ("key", "all"):
        key_sheet()
    if w in ("map", "all"):
        print(on_map())
