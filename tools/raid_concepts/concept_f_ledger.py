"""Concept F: PLAN LEDGER. A pre-commit board with a guaranteed outcome: rows are threats, columns are the raid's
steps; each cell shows where the threat stands and what it does. Defenses are dropped onto the ledger (or the
small map) and every affected cell rewrites at once; the totals row is the per-node result. Sign the orders and
the map replays the ledger, hands-off."""

from __future__ import annotations

from rc_draw import *  # noqa: F403

NAME = "F PLAN LEDGER"
STEPS = 6
GX, GY, CW, CH = 200, 150, 120, 92
MINI = MapXf(980, 450, 0.36)
# Bare raid: per threat, per step: (node, dmg dealt, hp after).
BARE = {
    "COLLECTOR": [("RELAY", 5, 12), ("FW", 5, 9), ("HOME", 5, 9), None, None, None],
    "AUDITOR": [("VAULT", 3, 8), ("VAULT", 3, 8), ("VAULT", 3, 8), ("VAULT", 3, 8), ("VAULT", 3, 8), ("VAULT", 3, 8)],
    "ENFORCER": [("PROXY", 9, 25), ("PROXY", 9, 25), ("PROXY", 9, 25), ("PROXY", 9, 25), ("PROXY", 9, 25), ("PROXY", 9, 25)],
}
# With TURRET on VAULT, ICE LOCK on PROXY step 1, DECOY on SAFE.
PLAN = {
    "COLLECTOR": [("RELAY", 5, 8), ("FW", 5, 1), ("HOME", 0, 0), None, None, None],
    "AUDITOR": [("VAULT", 3, 4), ("VAULT", 0, 0), None, None, None, None],
    "ENFORCER": [("PROXY", 0, 25), ("PROXY", 0, 21), ("SAFE", 9, 17), ("SAFE", 9, 13), ("SAFE", 9, 9), ("SAFE", 0, 5)],
}
HELD = {("ENFORCER", 0), ("ENFORCER", 1)}
TOTALS_BARE = [("HOME", 50, 5, "HOLDS"), ("FW", 30, 5, "HOLDS"), ("RELAY", 15, 5, "HOLDS"), ("VAULT", 20, 18, "TAKEN"),
               ("PROXY", 15, 54, "TAKEN"), ("SAFE", 20, 0, "HOLDS")]
TOTALS_PLAN = [("HOME", 50, 0, "HOLDS"), ("FW", 30, 5, "HOLDS"), ("RELAY", 15, 5, "HOLDS"), ("VAULT", 20, 3, "HOLDS"),
               ("PROXY", 15, 0, "HOLDS"), ("SAFE", 20, 27, "DOWN")]


def grid(d, data, held=frozenset(), cursor: int | None = None, tur_cells=frozenset()) -> None:
    text(d, (GX - 20, GY - 32), "STEP", 13, DIM, anchor="ra")
    for s in range(STEPS):
        x = GX + s * CW
        col = CELL if cursor == s else DIM
        text(d, (x + CW / 2, GY - 34), str(s + 1), 18, col, "mono", anchor="ma")
    for r, (tid, row) in enumerate(data.items()):
        y = GY + r * CH
        threat(d, (GX - 80, y + CH / 2 - 8), tid, 20)
        for s, cell in enumerate(row):
            x = GX + s * CW
            box = (x + 3, y + 3, x + CW - 3, y + CH - 3)
            if cell is None:
                d.rectangle(box, fill=(18, 20, 36))
                continue
            k, dmg, hp = cell
            dead = hp <= 0
            fill = (40, 20, 24) if dmg and not dead else PANEL
            d.rectangle(box, fill=fill, outline=CELL if cursor == s else PANEL_EDGE, width=3 if cursor == s else 1)
            node_icon(d, (x + 28, y + 30), k, 30, CELL)
            if (tid, s) in held:
                for sx in range(0, CW, 12):
                    d.line([(x + sx, y + CH - 4), (x + sx + 20, y + 4)], fill=(50, 110, 120), width=2)
                asset_icon(d, (x + 90, y + 30), "ICE", 12, HOLD)
            elif dead:
                text(d, (x + 90, y + 14), "X", 30, DMG, "stamp", anchor="ma")
            elif dmg:
                text(d, (x + 92, y + 18), f"-{dmg}", 20, DMG, "mono", anchor="ma")
            mhp = THREATS[tid][1]
            d.rectangle((x + 10, y + 64, x + CW - 10, y + 74), outline=(60, 70, 110))
            d.rectangle((x + 10, y + 64, x + 10 + (CW - 20) * max(0, hp) / mhp, y + 74), fill=THREAT_LIGHT)
            if (tid, s) in tur_cells:
                asset_icon(d, (x + CW - 16, y + 54), "TURRET", 7)


def totals(d, rows, y: int = 455) -> None:
    text(d, (GX - 20, y + 6), "=", 30, DIM, anchor="ra")
    for i, (k, hp, dmg, v) in enumerate(rows):
        x = GX + i * CW
        vcol = {"HOLDS": HOLD, "DOWN": INK, "TAKEN": THREAT_LIGHT}[v]
        d.rectangle((x + 3, y, x + CW - 3, y + 88), fill=BG2, outline=vcol, width=2)
        node_icon(d, (x + 24, y + 24), k, 28, CELL)
        text(d, (x + 42, y + 12), f"{hp}-{dmg}" if dmg < 99 else "", 16, INK, "mono")
        text(d, (x + CW / 2, y + 52), v, 18, vcol, anchor="ma")


def mini_map(d, positions=None, marks=None) -> None:
    positions, marks = positions or {}, marks or {}
    panel(d, (960, 430, 1265, 690))
    for a, b in LINKS:
        d.line([MINI.p(a), MINI.p(b)], fill=CELL_DIM, width=2)
    for k in NODES:
        x, y = MINI.p(k)
        if k.startswith("C"):
            shield(d, (x, y), 7, CORP)
        else:
            st = marks.get(k)
            col = DOWN_GREY if st == "DOWN" else (THREAT_LIGHT if st == "TAKEN" else CELL)
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(34, 36, 58), outline=col, width=2)
            if st == "DOWN":
                bolt(d, (x, y), 8)
    for tid, k in positions.items():
        x, y = MINI.p(k)
        threat(d, (x + 12, y - 12), tid, 8, show_hp=False)


def tray(d, used=()) -> None:
    for i, a in enumerate(("TURRET", "ICE", "DECOY")):
        x = 200 + i * 90
        d.rounded_rectangle((x, 600, x + 76, 680), radius=6, fill=PANEL, outline=CELL if a not in used else (50, 54, 70), width=2)
        asset_icon(d, (x + 38, 630), a, 16, CELL if a not in used else DIM)


def f1():
    img, d = new_frame(NAME, "warning")
    heat_bar(d, 470, 22, 340, 51)
    # The intercepted strike order, as a dossier, on HQ: three silhouettes, six steps, targets.
    panel(d, (300, 90, 980, 560), fill=(232, 226, 205), edge=(120, 110, 90))
    text(d, (330, 105), "INTERCEPTED STRIKE ORDER", 26, (40, 40, 50))
    flame(d, (345, 160), 9, HEAT)
    text(d, (362, 148), "HEAT 51 > 50", 18, (160, 60, 20), "mono")
    text(d, (560, 148), "EXECUTES ON RETURN TO HQ", 18, (40, 40, 50))
    for r, tid in enumerate(BARE):
        y = 210 + r * 100
        threat(d, (360, y + 30), tid, 22, show_hp=False)
        name, hp, dmg, spd, rt, ent, tgt = THREATS[tid]
        arrow(d, (400, y + 30), (500, y + 30), THREAT, 4, 12, shorten=0)
        node_icon(d, (530, y + 30), tgt, 40, (40, 40, 50))
        text(d, (580, y + 10), f"{hp}", 22, THREAT, "mono")
        swords(d, (640, y + 22), 8)
        text(d, (660, y + 10), f"{dmg}", 22, DMG, "mono")
        text(d, (720, y + 14), rt, 16, (80, 80, 90))
    stamp(img, (850, 480), "DECRYPTED", (40, 140, 90), 36, -8)
    header(d, NAME, 1, "Warning: the intercepted strike order arrives as a dossier (who, target, HP, damage, routing) with why and when")
    return img


def f2():
    img, d = new_frame(NAME, "planning")
    heat_bar(d, 470, 22, 340, 51)
    grid(d, BARE)
    totals(d, TOTALS_BARE)
    tray(d)
    # Dragging ICE onto ENFORCER step 1: ghost over the cell, what-if label.
    x, y = GX, GY + 2 * CH
    d.rounded_rectangle((x + 10, y + 10, x + 70, y + 70), radius=6, fill=(50, 46, 30), outline=CELL, width=3)
    asset_icon(d, (x + 40, y + 40), "ICE", 16)
    dashed(d, (328, 600), (x + 40, y + 70), CELL, 3)
    label_tag(d, (x + 130, y + CH - 4), "HOLDS STEPS 1-2: PROXY -18 > 0", BG, CELL)
    mini_map(d)
    header(d, NAME, 2, "Planning: rows = threats, columns = steps; each cell = where it stands and what it hits; dragging ICE onto a cell shows the rewrite")
    return img


def f3():
    img, d = new_frame(NAME, "forecast")
    heat_bar(d, 470, 22, 340, 51)
    tur = {("COLLECTOR", 0), ("COLLECTOR", 2), ("AUDITOR", 0), ("AUDITOR", 1), ("ENFORCER", 1)}
    grid(d, PLAN, HELD, tur_cells=tur)
    totals(d, TOTALS_PLAN)
    tray(d, used=("TURRET", "ICE", "DECOY"))
    panel(d, (960, 90, 1265, 260), edge=STAMP_HOLD)
    text(d, (975, 100), "GUARANTEED", 14, DIM)
    text(d, (975, 120), "CELL HOLDS", 30, STAMP_HOLD, "stamp")
    text(d, (975, 170), "1 DOWN: SAFEHOUSE", 17, INK)
    text(d, (975, 200), "REPAIR 10 · NO HEAT", 17, DIM)
    button(d, (975, 220, 1250, 255), "SIGN ORDERS", True, 16)
    mini_map(d, marks={"SAFE": "DOWN"})
    header(d, NAME, 3, "Forecast: turret marks every cell it reaches, ICE hatches two cells, DECOY redirects the Enforcer to SAFEHOUSE; totals row = guaranteed result")
    return img


def f4():
    img, d = new_frame(NAME, "resolution")
    heat_bar(d, 470, 22, 340, 51)
    grid(d, PLAN, HELD, cursor=2)
    text(d, (640, 70), "AUTO-PLAYING  ·  STEP 3 / 6", 15, DIM, anchor="ma")
    # Big map replay replaces the totals row while playing.
    bm = MapXf(220, 430, 0.5)
    for a, b in LINKS:
        d.line([bm.p(a), bm.p(b)], fill=CELL_DIM, width=3)
    for k in NODES:
        x, y = bm.p(k)
        if k.startswith("C"):
            shield(d, (x, y), 10, CORP)
        else:
            d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=(34, 36, 58), outline=CELL, width=3)
            node_icon(d, (x, y), k, 18, CELL)
    sx, sy = bm.p("SAFE")
    threat(d, (sx + 22, sy - 16), "ENFORCER", 11, show_hp=False)
    dmg_badge(d, (sx - 30, sy - 22), 9, size=14)
    hx, hy = bm.p("HOME")
    text(d, (hx, hy - 40), "X", 26, DMG, "stamp", anchor="ma")
    speed_controls(d, 1060, 660)
    header(d, NAME, 4, "Resolution: a cursor walks the ledger column by column while the map replays it; what you signed is what happens")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    heat_bar(d, 470, 22, 340, 51)
    totals(d, TOTALS_PLAN, y=420)
    stamp(img, (560, 230), "CELL HOLDS", STAMP_HOLD, 72, -6, "1 DOWN · REPAIR 10 · NO HEAT")
    mini_map(d, marks={"SAFE": "DOWN"})
    panel(d, (200, 540, 900, 690))
    text(d, (216, 552), "PAID", 14, DIM)
    for i, (a, s) in enumerate((("TURRET", "10 > 2"), ("ICE", "SPENT"), ("DECOY", "12 > 0"))):
        asset_icon(d, (250 + i * 160, 610), a, 16, CELL if s not in ("SPENT", "12 > 0") else DIM)
        text(d, (250 + i * 160, 642), s, 16, INK, "mono", anchor="ma")
    button(d, (1090, 380, 1265, 420), "BACK TO HQ")
    header(d, NAME, 5, "Aftermath: the totals row becomes the receipt; stamp with the cost; spent and worn defenses listed; DOWN bolt on the map")
    return img


FRAMES = [f1, f2, f3, f4, f5]
