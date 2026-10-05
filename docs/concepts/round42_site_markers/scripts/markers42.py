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


# ------------------------------------------------------------------ v2 glyphs (designer round 42 review)
import crests15  # noqa: E402


def g_mask(fn, px):
    return fn().resize((px, px), Image.LANCZOS)


def scale_mask():
    """CUSTOMS (BREACH: Customs Override Keys): a weigh scale TIPPING to one side."""
    S = 512
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    d.polygon([(256, 120), (236, 420), (276, 420)], fill=255)                 # post
    d.rounded_rectangle([156, 410, 356, 450], radius=14, fill=255)           # foot
    a = math.radians(-16)                                                    # the beam tips
    L = 200
    p0 = (256 - L * math.cos(a), 140 - L * math.sin(a))
    p1 = (256 + L * math.cos(a), 140 + L * math.sin(a))
    d.line([p0, p1], fill=255, width=26)
    d.ellipse([236, 120, 276, 160], fill=255)
    for (px, py), drop in ((p0, 150), (p1, 110)):
        d.line([(px, py), (px - 46, py + drop)], fill=255, width=10)
        d.line([(px, py), (px + 46, py + drop)], fill=255, width=10)
        d.pieslice([px - 70, py + drop - 46, px + 70, py + drop + 46], 0, 180, fill=255)
    return m


def keyring_mask():
    """T2 EXPLOIT plate: a keyring with three keys dangling (not the single key of the old customs badge)."""
    S = 512
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([186, 40, 326, 180], outline=255, width=26)                     # the ring
    for ang in (-28, 0, 28):
        a = math.radians(90 + ang)
        bx, by = 256 + 70 * math.cos(a), 110 + 70 * math.sin(a)
        tx, ty = 256 + 330 * math.cos(a), 110 + 330 * math.sin(a)
        d.ellipse([bx - 44 + (tx - bx) * 0.12, by - 44 + (ty - by) * 0.12, bx + 44 + (tx - bx) * 0.12, by + 44 + (ty - by) * 0.12], fill=255)
        d.line([(bx + (tx - bx) * 0.12, by + (ty - by) * 0.12), (tx, ty)], fill=255, width=26)
        nx, ny = -math.sin(a), math.cos(a)
        for t in (0.78, 0.92):                                               # the bits
            qx, qy = bx + (tx - bx) * t, by + (ty - by) * t
            d.line([(qx, qy), (qx + nx * 40, qy + ny * 40)], fill=255, width=20)
    return m


def bolt_mask():
    S = 512
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).polygon([(300, 40), (130, 290), (240, 290), (200, 470), (380, 200), (270, 200)], fill=255)
    return m


def gate_mask():
    """BREACH / Customs Override: a customs BOOM GATE raised (the override lifts the barrier)."""
    S = 512
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([60, 300, 170, 470], radius=12, fill=255)              # the gate post / booth
    d.rectangle([84, 330, 146, 380], fill=0)                                     # booth window
    import math as _m
    a = _m.radians(-38)
    x0, y0 = 150, 320
    x1, y1 = x0 + 360 * _m.cos(a), y0 + 360 * _m.sin(a)
    d.line([(x0, y0), (x1, y1)], fill=255, width=46)                            # the raised boom
    for t in (0.25, 0.5, 0.75):                                                  # hazard bands
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        d.line([(cx - 18 * _m.cos(a), cy - 18 * _m.sin(a)), (cx + 18 * _m.cos(a), cy + 18 * _m.sin(a))], fill=0, width=30)
    d.ellipse([125, 295, 175, 345], fill=255)
    d.rectangle([40, 462, 470, 486], fill=255)                                   # the road line
    return m


def tint(mask, col):
    im = Image.new("RGBA", mask.size, col + (255,))
    im.putalpha(mask)
    return im

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
            if exploit == "BREACH":
                g2 = tint(g_mask(gate_mask, int(r * 1.6)), (255, 236, 170))
            else:
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
    ic = RC_.cell_icon(kind, int(P * 0.62), LIME)
    im.alpha_composite(ic, ((P - ic.width) // 2, (P - ic.height) // 2))
    im = im.resize((px, px), Image.LANCZOS)
    if False:                                     # v3: disabled is the greyed marker + a white bolt (see marker())
        m = Image.new("L", (px, px), 0)
        ImageDraw.Draw(m).rectangle([0, 0, px, int(px * 0.62)], fill=150)
        dark = Image.new("RGBA", (px, px), (4, 4, 8, 255))
        dark.putalpha(ImageChops.multiply(m, im.split()[3]))
        im.alpha_composite(dark)
    return im


def pad(img, x, y, r, own, k=1.0):
    q = CV.diamond(x, y, r)
    col = {"corporate": MER, "claimed": LIME, "seized": RED, "cleared": GREY, "disabled": LIME}[own]
    return U.pad(img, q, col, lit={"corporate": 0.7, "claimed": 1.0, "seized": 1.0, "cleared": 0.6, "disabled": 0.45}[own],
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
        rc = LIME                                     # v2: disabled stays in the player colour
    img = ring(img, x, cy, ic.width / 2 + 5, rc, w=4 if avail != "notyet" else 3, glow={"next": 0.9, "yours": 0.6}.get(avail, 0.0))
    if tier and status not in ("claimed", "disabled"):
        img = pips(img, x, cy + ic.width / 2 + 9, tier, GOLD if kind == "exploit" else (rc if avail != "notyet" else (210, 206, 220)),
                   s=int(5 * k), gap=int(3 * k))
    if status in ("cleared", "seized"):
        img = badge(img, x + ic.width / 2 + 2, cy - ic.width / 2 + 2, status, r=int(9 * k))
    if status == "disabled":                          # v3: the WHOLE marker greys out, a plain white bolt across it
        R0 = ic.width / 2 + 9
        box = (int(x - R0), int(cy - R0), int(x + R0), int(cy + R0 + 6))
        reg = img.crop(box)
        a = reg.split()[3]
        g = ImageEnhance.Brightness(reg.convert("L").convert("RGB")).enhance(0.75).convert("RGBA")
        g.putalpha(a)
        m = Image.new("L", reg.size, 0)
        ImageDraw.Draw(m).ellipse([0, 0, reg.width - 1, reg.height - 7], fill=255)
        img.paste(Image.composite(g, reg, m), box[:2])
        b = tint(g_mask(bolt_mask, int(R0 * 2.1)), (250, 250, 250))
        sh = tint(g_mask(bolt_mask, int(R0 * 2.1)), (8, 8, 12))
        img.alpha_composite(sh, (int(x - b.width / 2 + 2), int(cy - b.height / 2 + 3)))
        img.alpha_composite(b, (int(x - b.width / 2), int(cy - b.height / 2)))
    if label:
        img = U.chip(img, (x, y + 26 * k), label, rc if rc != WHITE else (220, 218, 228), int(12 * k), fill_a=230)
    return img


def depowered(img, segs):
    """A de-powered link: a dim grey double trace, broken in the middle (a cut with two loose ends)."""
    d = ImageDraw.Draw(img)
    for a, b in segs:
        L_ = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        ux, uy = (b[0] - a[0]) / L_, (b[1] - a[1]) / L_
        nx, ny = -uy, ux
        m0 = 0.5 - 12 / L_
        m1 = 0.5 + 12 / L_
        for o in (-2.5, 2.5):
            for t0, t1 in ((0.0, m0), (m1, 1.0)):
                p = (a[0] + (b[0] - a[0]) * t0 + nx * o, a[1] + (b[1] - a[1]) * t0 + ny * o)
                q = (a[0] + (b[0] - a[0]) * t1 + nx * o, a[1] + (b[1] - a[1]) * t1 + ny * o)
                d.line([p, q], fill=(140, 140, 156, 255), width=3)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2       # the cut: two bent loose ends
        for sgn in (-1, 1):
            ex, ey = mx - sgn * ux * 12, my - sgn * uy * 12
            d.line([(ex, ey), (ex + nx * 9 * sgn, ey + ny * 9 * sgn)], fill=(190, 190, 205, 255), width=3)
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


# ------------------------------------------------------------------ plain-language legend (v3)
LEGEND = [  # (draw fn, title, what it means in the game)
    (lambda im, x, y: marker(im, x, y, "site", 1, "corporate", "next", scale=0.9), "CORP CREST",
     "A corporate Site you can run (Meridian's crane). Clear it, then claim it to grow your network."),
    (lambda im, x, y: marker(im, x, y, "exploit", 2, "corporate", "next", scale=0.9), "GOLD KEY",
     "An Exploit Site (always T2). It holds one Exploit: you need 3 to breach the Central Server."),
    (lambda im, x, y: marker(im, x, y, "exploit", 2, "corporate", "next", "INTEL", scale=0.9), "MAGNIFIER (INTEL)",
     "Intel Exploit: reveals the boss's moves and opens locked links on the Grid."),
    (lambda im, x, y: marker(im, x, y, "exploit", 2, "corporate", "next", "BREACH", scale=0.9), "BOOM GATE (BREACH)",
     "Breach Exploit (customs override): the boss starts with one fewer pointer."),
    (lambda im, x, y: marker(im, x, y, "exploit", 2, "corporate", "next", "VIRUS", scale=0.9), "VIRUS",
     "Virus Exploit: the boss starts the fight with CORRUPTED slices."),
    (lambda im, x, y: marker(im, x, y, "heat", 1, "corporate", "next", scale=0.9), "FLAME",
     "A Heat objective Site: clearing it lowers campaign Heat (about -5 to -8) and never provokes a raid."),
    (lambda im, x, y: marker(im, x, y, "core", 0, scale=0.9), "HEART",
     "CORE, your home server. If its integrity reaches 0 you lose the campaign."),
    (lambda im, x, y: marker(im, x, y, "site", 0, "claimed", scale=0.9), "RELAY (LIME)",
     "Your node: a claimed Site with a node installed. Raids attack these; runs start from them."),
    (lambda im, x, y: marker(im, x, y, "site", 1, "cleared", "yours", scale=0.9), "GREY + CHECK",
     "Cleared: already run and used up, not claimed. It can still be patrolled for loot, Heat and Rank."),
    (lambda im, x, y: marker(im, x, y, "site", 0, "disabled", scale=0.9), "WHITE BOLT",
     "Disabled: your node hit 0 integrity. No bonus and no power to its links until you repair it."),
    (lambda im, x, y: marker(im, x, y, "site", 1, "seized", "next", scale=0.9), "RED X",
     "Seized: the corp took the Site back. Run a Reclaim (one fight) to retake it; it is a raid entry point."),
    (None, "RINGS", "White = not yet reachable.  Orange = you can run it now.  Lime = yours or already visited."),
    (None, "PIPS", "Tier 1-3 of the Site (harder runs, better rewards). Gold pips = an Exploit Site."),
    (None, "TARGET", "The corp HQ: the Central Server boss fight. Needs 3 Exploits (the chip counts them)."),
    (None, "PADLOCK", "A locked link: opens with an Intel Exploit or an objective. De-powered links: grey, broken."),
]


def legend(img, y0):
    d = ImageDraw.Draw(img)
    d.line([(24, y0 - 14), (1896, y0 - 14)], fill=(70, 70, 90, 255), width=1)
    d.text((30, y0 + 8), "WHAT EACH ICON MEANS IN THE GAME", font=RL.f_ui(24, b"Bold"), fill=GOLD + (255,), anchor="lm")
    cols = 2
    rh = 62
    for i, (fn, title, text) in enumerate(LEGEND):
        cx = 30 + (i % cols) * 940
        cy = y0 + 64 + (i // cols) * rh
        if fn:
            img = fn(img, cx + 34, cy + 18)
        d = ImageDraw.Draw(img)
        d.text((cx + 84, cy - 10), title, font=RL.f_ui(18, b"Bold"), fill=(235, 235, 240, 255))
        d.text((cx + 84, cy + 14), text, font=RL.f_ui(16, b"Regular"), fill=(190, 200, 210, 255))
    return img


# ------------------------------------------------------------------ the key sheet
def key_sheet():
    W, H = 1920, 1640
    img = Image.new("RGBA", (W, H), (12, 11, 18, 255))
    # a dim street texture behind the cells (the markers sit on streets)
    bg = CV.base_map()
    bg = ImageEnhance.Brightness(bg).enhance(0.38).filter(ImageFilter.GaussianBlur(3)).resize((int(1920 * H / 1080), H))
    img.alpha_composite(bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H)))
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
    top = RL.ink(img.crop((0, 0, 1920, 1080)), pr)          # the pen canvas is 1920 x 1080
    img.paste(top, (0, 0))
    img = U.chip(img, (1450, yb + 36), "CENTRAL SERVER // EXPLOITS 1/3", GOLD, 12)
    d = ImageDraw.Draw(img)
    d.text((1640, yb), "LOCKED LINK", font=RL.f_ui(21, b"Bold"), fill=(235, 235, 240, 255))
    img = locked_link(img, (1620, yb + 150), (1860, yb + 70))
    img = legend(img, 940)
    # rules strip
    c = RL.CRT(1876, 104, U.CYAN, "RULES", seed=43)
    c.text((16, 50), "Hidden by default: regular Sites that are not selectable. PINNED (always shown): Exploit, Heat objective, the boss, your", 15, (220, 232, 238))
    c.text((16, 74), "nodes. Seized Sites next to you are raid entry points (red pins). Pips: tier 1-3; the boss has the TARGET circle.", 15, (220, 232, 238))
    img = RL.paste(img, c.finish(scan=0.15), 22, H - 124)
    RL.save(img, "site_markers_v3.png")


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
    dead = []
    for a, b in links:
        if a not in shown or b not in shown:
            continue
        if {a, b} & {seized, disabled}:                 # v3: no power to / from a seized or disabled node
            dead.append((a, b))
            continue
        st = CV.link_state(nodes, a, b)
        pa, pb = nodes[a]["xy"], nodes[b]["xy"]
        col = {"owned": LIME, "border": MER, "past": LIME}.get(st, WHITE)
        inl.trace([pa, pb], col, width=2.6 if st in ("owned", "border") else 1.6, lanes=3 if st in ("owned", "border") else 2, gap=4.5,
                  glow=0.9 if st in ("owned", "border") else 0.1, alpha=1.0 if st in ("owned", "border", "past") else 0.6, pads=False)
    img = inl.lay(img)
    img = depowered(img, [(nodes[a]["xy"], nodes[b]["xy"]) for a, b in dead])
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
    RL.save(RL.bloom(img, 0.12, 0.82, 8), "site_markers_on_map_v3.png")
    return dict(core=core, disabled=disabled, seized=seized, exploits=exploits)


if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv) > 1 else "all"
    if w in ("key", "all"):
        key_sheet()
    if w in ("map", "all"):
        print(on_map())
