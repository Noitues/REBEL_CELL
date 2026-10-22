"""Concept E: COUNTDOWN + ALLOCATION. Frostpunk-style: the raid is announced two netruns ahead with a top-center
countdown and a visible front; each target node has a gauge with a notch (the strike it will take). Between netruns
the player spends a scarce pool (crew-hours from Schematics and stationed operatives) to fill gauges, or makes a
hard call (evacuate a node for a refund, go dark to delay the strike at a Heat cost). The strike auto-resolves."""

from __future__ import annotations

from rc_draw import *  # noqa: F403

NAME = "E COUNTDOWN + ALLOCATION"
XF = MapXf(220, 110, 0.85)
# node: (strike notch, defense filled before allocation)
GAUGE = {"HOME": (15, 12), "VAULT": (12, 6), "PROXY": (27, 8), "RELAY": (5, 6)}


def countdown(d, n: int, of: int = 2, label: str = "NETRUNS") -> None:
    x, y = 640, 92
    d.ellipse((x - 46, y - 46, x + 46, y + 46), fill=(16, 22, 52), outline=THREAT, width=5)
    for i in range(of):
        a0 = -90 + i * 360 / of + 6
        a1 = -90 + (i + 1) * 360 / of - 6
        d.arc((x - 56, y - 56, x + 56, y + 56), a0, a1, fill=THREAT if i < n else (40, 46, 80), width=8)
    text(d, (x, y - 30), str(n), 48, INK, "mono", anchor="ma")
    text(d, (x, y + 52), label, 13, THREAT_LIGHT, anchor="ma")


def front(d, x: int) -> None:
    for i in range(0, H, 18):
        d.line([(x, i), (x + 40, i + 30)], fill=(40, 60, 140), width=6)
    d.line([(x, 0), (x, H)], fill=THREAT, width=4)


def gauge(d, key: str, fill: int, notch: int, add: int = 0, scale: float = 3.0) -> None:
    x, y = XF.p(key)
    gx, gy = x + 42, y + 30
    hmax = 30 * scale
    d.rectangle((gx, gy - hmax, gx + 18, gy), fill=BG2, outline=PANEL_EDGE, width=2)
    if fill > 0:
        d.rectangle((gx + 2, gy - fill * scale, gx + 16, gy - 2), fill=CELL)
    if add:
        d.rectangle((gx + 2, gy - (fill + add) * scale, gx + 16, gy - fill * scale), fill=(255, 240, 160))
    ny = gy - notch * scale
    d.polygon([(gx - 10, ny - 7), (gx, ny), (gx - 10, ny + 7)], fill=THREAT)
    d.line([(gx - 2, ny), (gx + 22, ny)], fill=THREAT, width=3)
    text(d, (gx + 24, ny - 10), str(notch), 15, THREAT_LIGHT, "mono")


def base(d, states=None) -> None:
    states = states or {}
    draw_links(d, XF)
    for k in NODES:
        node(d, XF, k, states.get(k, "ok"), show_hp=False)


def pool(d, left: int, total: int = 6) -> None:
    panel(d, (20, 600, 360, 690))
    text(d, (36, 610), "CREW-HOURS", 14, DIM)
    for i in range(total):
        col = CELL if i < left else (60, 60, 70)
        d.rounded_rectangle((36 + i * 50, 638, 76 + i * 50, 676), radius=6, fill=col)
        asset_icon(d, (56 + i * 50, 652), "CREW", 11, BG if i < left else (40, 40, 50))


def f1():
    img, d = new_frame(NAME, "warning")
    front(d, 1180)
    base(d)
    heat_bar(d, 60, 22, 340, 51)
    countdown(d, 2)
    for k, (notch, fill) in GAUGE.items():
        gauge(d, k, fill, notch)
    panel(d, (930, 470, 1150, 690), edge=THREAT)
    shield(d, (958, 500), 13, THREAT)
    text(d, (980, 488), "STRIKE IN 2", 22, INK)
    flame(d, (958, 545), 9, HEAT)
    text(d, (975, 533), "HEAT 51 > 50", 18, HEAT, "mono")
    text(d, (948, 575), "TARGETS", 14, DIM)
    for i, k in enumerate(GAUGE):
        node_icon(d, (965 + i * 45, 615), k, 30, CELL)
    text(d, (948, 650), "notch = strike, fill = you", 13, DIM)
    header(d, NAME, 1, "Warning: top-center countdown (2 netruns); the front at the map edge; each target shows a gauge, cobalt notch = the strike it will take")
    return img


def f2():
    img, d = new_frame(NAME, "planning")
    front(d, 1180)
    base(d)
    heat_bar(d, 60, 22, 340, 51)
    countdown(d, 2)
    for k, (notch, fill) in GAUGE.items():
        gauge(d, k, fill, notch, add=6 if k == "VAULT" else 0)
    vx, vy = XF.p("VAULT")
    for i, s in enumerate(("+", "-")):
        button(d, (vx + 70, vy - 60 + i * 40, vx + 102, vy - 28 + i * 40), s, i == 0, 18)
    label_tag(d, (vx + 110, vy - 56), "6 + 6 = 12 : HOLDS", BG, CELL)
    pool(d, 4)
    # Hard calls card.
    panel(d, (930, 300, 1150, 590))
    text(d, (945, 310), "HARD CALLS", 14, DIM)
    node_icon(d, (965, 360), "PROXY", 34, CELL)
    arrow(d, (990, 360), (1030, 360), INK, 3, 9, shorten=0)
    text(d, (1040, 348), "EVACUATE", 16, INK)
    text(d, (945, 385), "TAKEN, refund 6", 14, DIM)
    countdown_icon = (965, 450)
    d.ellipse((945, 430, 985, 470), outline=THREAT, width=3)
    text(d, (965, 438), "+1", 16, INK, "mono", anchor="ma")
    text(d, (1000, 438), "GO DARK", 16, INK)
    text(d, (945, 480), "delay strike, +4 Heat", 14, DIM)
    header(d, NAME, 2, "Planning (at HQ between netruns): spend crew-hours into gauges (+2 VAULT shown); or evacuate PROXY for a refund, or go dark to delay")
    return img


def f3():
    img, d = new_frame(NAME, "forecast")
    front(d, 1050)
    base(d, states={"PROXY": "ok"})
    heat_bar(d, 60, 22, 340, 53)
    countdown(d, 1)
    fills = {"HOME": 15, "VAULT": 12, "PROXY": 8, "RELAY": 6}
    for k, (notch, _) in GAUGE.items():
        gauge(d, k, fills[k], notch)
    for k in ("HOME", "VAULT", "RELAY", "FW", "SAFE"):
        mark(d, XF, k, "HOLDS")
    mark(d, XF, "PROXY", "TAKEN")
    pool(d, 0)
    panel(d, (760, 470, 1030, 690), edge=STAMP_HOLD)
    text(d, (775, 480), "IF IT STRIKES NOW", 14, DIM)
    text(d, (775, 500), "CELL HOLDS", 30, STAMP_HOLD, "stamp")
    node_icon(d, (790, 570), "PROXY", 30, THREAT_LIGHT)
    text(d, (815, 558), "EVACUATED: +6", 17, INK, "mono")
    text(d, (775, 600), "NOT CLEAN: +0 HEAT", 16, DIM)
    text(d, (775, 640), "1 NETRUN TO GO", 16, THREAT_LIGHT)
    header(d, NAME, 3, "Forecast: after one netrun every gauge is compared with its notch; PROXY evacuated (TAKEN, refunded); the front has moved in")
    return img


def f4():
    img, d = new_frame(NAME, "resolution")
    base(d)
    front(d, 560)
    heat_bar(d, 60, 22, 340, 55)
    countdown(d, 0, label="STRIKE")
    fills = {"HOME": 15, "VAULT": 12, "PROXY": 0, "RELAY": 6}
    for k, (notch, _) in GAUGE.items():
        if k in ("PROXY",):
            gauge(d, k, 0, notch)
        elif k == "RELAY":
            gauge(d, k, 1, notch)
        else:
            gauge(d, k, fills[k], notch)
    rx, ry = XF.p("RELAY")
    dmg_badge(d, (rx - 40, ry - 50), 5)
    text(d, (640, 160), "AUTO-PLAYING", 13, DIM, anchor="ma")
    speed_controls(d, 1060, 660)
    header(d, NAME, 4, "Resolution: the front sweeps right to left; each gauge drains by its notch as the front crosses it; no input")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    base(d, states={"PROXY": "taken"})
    heat_bar(d, 60, 22, 340, 55, raid_at=None)
    for k in ("HOME", "VAULT", "RELAY", "FW", "SAFE"):
        mark(d, XF, k, "HOLDS")
    mark(d, XF, "PROXY", "TAKEN")
    stamp(img, (980, 220), "CELL HOLDS", STAMP_HOLD, 64, -6, "1 TAKEN (EVACUATED) · NO HEAT")
    panel(d, (20, 540, 520, 690))
    text(d, (36, 552), "RESULT OF YOUR CALLS", 14, DIM)
    node_icon(d, (60, 600), "PROXY", 34, THREAT_LIGHT)
    text(d, (90, 588), "PROXY TAKEN · REFUND +6", 18, INK)
    flame(d, (60, 650), 10, HEAT)
    text(d, (85, 638), "NEXT STRIKE AT HEAT 75", 18, HEAT)
    button(d, (1090, 640, 1265, 690), "BACK TO HQ")
    header(d, NAME, 5, "Aftermath: stamp with the cost; TAKEN node keeps its pencil X; the trade you chose (refund) is named")
    return img


FRAMES = [f1, f2, f3, f4, f5]
