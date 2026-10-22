"""Concept H, round 6: BASTION, the defense persists across the campaign (each rule a designer decision).
- No per-raid draft. Every piece you buy stays where you put it, raid after raid; a TAKEN node's pieces are destroyed.
- Each HQ visit before a raid: buy up to 2 pieces (turret 6, sentry 7, railgun 10, ICE 5, decoy 4) and station the crew.
- All three raids of this campaign leg are telegraphed on the Heat bar (rosters, entries), from the first visit.
- The shop shows a FORTRESS FORECAST: the current raid AND the telegraphed raids after it, run with this fortress and no
  further buys (pieces persist, repairs paid). It is an honest projection, not a solver's hint.
- Payout per raid: +4 salvage per kill, +6 if CLEAN, minus the full repair bill; +12 netrun income between raids.
Numbers: sim.py with the round-5 package, on bastion_campaign.py's campaign 1 (its seeded rosters). The two lines shown are
that campaign's two measured lines: the home fortress (railgun + decoy at home) and the forward fortress (sentry + decoy
on the corp side)."""
from __future__ import annotations

from r2_kit import *  # noqa: F403
from sim import NODE_HP as SIM_HP, Plan, run, summary

import concept_g3_merged as G3
import concept_g4_merged as G4
import concept_g5_merged as G5
from bastion_campaign import COST, INCOME, RULE, START, campaigns
from concept_g4_merged import dial, kills, piece, skull, xsign
from depth_harness import net, price

NAME = "H BASTION r6"
MOMENTS = ["0_campaign", "1_shop", "2_forecast", "3_resolution", "4_aftermath", "5_visit2", "6_visit3", "7_record"]
XF, SHADE, OFF = G3.XF, G3.SHADE, G3.OFF
CAMP = campaigns()[0]
HEATS = (26, 51, 76)
HOME_LINE = [({"HOME": ["RAILGUN"], "FW": ["DECOY"]}, "HOME"),
             ({"VAULT": ["TURRET"], "RELAY": ["ICE"]}, "HOME"),
             ({"VAULT": ["RAILGUN"], "PROXY": ["ICE"]}, "VAULT")]
FWD_LINE = [({"PROXY": ["SENTRY"], "RELAY": ["DECOY"]}, "PROXY"),
            ({"RELAY": ["DECOY"]}, "PROXY"),
            ({"PROXY": ["DECOY"]}, "PROXY")]


def merge(a: dict, b: dict) -> dict:
    out = {k: list(v) for k, v in a.items()}
    for k, v in b.items():
        out.setdefault(k, []).extend(v)
    return out


def spend(buy: dict) -> int:
    return sum(COST[p] for v in buy.values() for p in v)


def play(line, upto=3):
    """Run the campaign leg along a line of buys. Returns per raid: (fortress before, result, bank after raid)."""
    bank, fort, out = START, {}, []
    for i in range(upto):
        buy, crew = line[i]
        fort = merge(fort, buy)
        bank -= spend(buy)
        r = run(Plan(fort, crew, dict(RULE)), threats=list(CAMP[i]))
        bank += net(r)
        out.append((dict(fort), r, bank, crew))
        for k, v in r.nodes.items():
            if v["outcome"] == "taken":
                fort.pop(k, None)
        bank += INCOME if i < 2 else 0
    return out


def projection(fort: dict, crew: str, from_raid: int, bank: int):
    """The fortress forecast: this fortress, no further buys, through the telegraphed raids."""
    f = {k: list(v) for k, v in fort.items()}
    rows = []
    for i in range(from_raid, 3):
        r = run(Plan(f, crew, dict(RULE)), threats=list(CAMP[i]))
        bank += net(r)
        rows.append((i, r, bank))
        for k, v in r.nodes.items():
            if v["outcome"] == "taken":
                f.pop(k, None)
        bank += INCOME if i < 2 else 0
    return rows


HOME_RUN, FWD_RUN = play(HOME_LINE), play(FWD_LINE)
PROJ_HOME = projection(HOME_LINE[0][0], HOME_LINE[0][1], 0, START - spend(HOME_LINE[0][0]))
PROJ_FWD = projection(FWD_LINE[0][0], FWD_LINE[0][1], 0, START - spend(FWD_LINE[0][0]))


def lost(r) -> int:
    return sum(1 for v in r.nodes.values() if v["outcome"] in ("down", "taken"))


# ---------- glyphs ----------
def roster_chips(d, x, y, roster, scale=0.5, gap=70) -> None:
    for i, (tid, entry) in enumerate(roster):
        threat_chip(d, (x + i * gap, y), tid, scale=scale)
        shield(d, (x + i * gap, y + 36 * scale + 14), 5, CORP)
        text(d, (x + i * gap + 8, y + 36 * scale + 6), entry[1], 11, DIM, "mono")


def campaign_bar(d, x=300, y=40, w=680, now=0) -> None:
    """Heat bar with the three telegraphed raids pinned at their thresholds."""
    heat_bar(d, x, y, w, (HEATS + (80,))[now], raid_at=None)
    for i, (h, roster) in enumerate(zip((25, 50, 75), CAMP)):
        tx = x + w * h / 100
        col = THREAT if i >= now else (60, 70, 110)
        d.line([(tx, y + 14), (tx, y + 40)], fill=col, width=3)
        n = len(roster)
        panel(d, (tx - 22 * n, y + 40, tx + 22 * n, y + 84), edge=col)
        for j, (tid, e) in enumerate(roster):
            threat(d, (tx - 22 * n + 22 + j * 44, y + 62), tid, 9, show_hp=False, ghost=i < now)


def place_fort(d, fort: dict, crew: str | None, new: dict | None = None) -> None:
    """Installed pieces (solid); this visit's purchases ringed in white."""
    new = new or {}
    for n, aa in fort.items():
        x, y = XF.p(n)
        nn = list(new.get(n, []))
        for i, a in enumerate(aa):
            px, py = x - 50, y + 12 + i * 28
            fresh = a in nn
            if fresh:
                nn.remove(a)
            d.ellipse((px - 14, py - 14, px + 14, py + 14), fill=(50, 46, 30), outline=INK if fresh else CELL, width=3 if fresh else 2)
            piece(d, (px, py), a, 8)
    if crew:
        x, y = XF.p(crew)
        asset_icon(d, (x + 46, y + 22), "CREW", 10)
        G4.chevron(d, (x + 46, y + 2), 6)


def shop(d, x, y, sel=(), bank=START) -> None:
    panel(d, (x, y, x + 600, y + 150), edge=CELL)
    coin(d, (x + 24, y + 26), 11)
    text(d, (x + 40, y + 12), str(bank), 26, INK, "mono")
    for i, a in enumerate(COST):
        cx = x + 90 + i * 100
        on = a in sel
        d.rounded_rectangle((cx, y + 12, cx + 90, y + 138), radius=8, fill=(50, 46, 30) if on else PANEL,
                            outline=CELL if on else PANEL_EDGE, width=3 if on else 2)
        piece(d, (cx + 45, y + 44), a, 15)
        coin(d, (cx + 26, y + 108), 9)
        text(d, (cx + 40, y + 95), str(COST[a]), 22, INK, "mono")
        for k in range(2):
            d.rectangle((cx + 8 + k * 14, y + 128, cx + 18 + k * 14, y + 132), fill=CELL if on and k == 0 else PANEL_EDGE)


def proj_strip(d, x, y, rows, label, on=True, w=400) -> None:
    """Fortress forecast: one cell per telegraphed raid: threats, home, nodes lost, clean check, bank after."""
    d.rounded_rectangle((x, y, x + w, y + 92), radius=6, fill=(50, 46, 30) if on else BG2,
                        outline=CELL if on else PANEL_EDGE, width=3 if on else 1)
    text(d, (x + 10, y + 6), label, 22, CELL if on else DIM, "mono")
    cw = (w - 40) // 3
    for j, (i, r, bank) in enumerate(rows):
        cx = x + 36 + j * cw
        flame(d, (cx + 10, y + 20), 7, HEAT)
        text(d, (cx + 22, y + 9), str(HEATS[i]), 14, HEAT, "mono")
        hl = r.home_before - r.home_after
        node_icon(d, (cx + 14, y + 50), "HOME", 18, CELL)
        text(d, (cx + 26, y + 40), f"-{hl}", 15, DMG if hl else HOLD, "mono")
        G5.lost_nodes(d, cx + 66, y + 50, r, 16)
        coin(d, (cx + 14, y + 78), 7)
        text(d, (cx + 24, y + 70), f"{bank}", 15, STAMP_CLEAN if bank > 0 else DMG, "mono")
        if r.clean:
            check(d, (cx + cw - 18, y + 20), 6, STAMP_CLEAN)


def bank_line(d, x, y, w, h, series, cols) -> None:
    panel(d, (x, y, x + w, y + h))
    lo, hi = min(min(s) for s in series) - 5, max(max(s) for s in series) + 5
    zy = y + h - 20 - (0 - lo) / (hi - lo) * (h - 40)
    d.line([(x + 20, zy), (x + w - 20, zy)], fill=PANEL_EDGE, width=1)
    for s, col in zip(series, cols):
        pts = [(x + 40 + i * (w - 80) / (len(s) - 1), y + h - 20 - (v - lo) / (hi - lo) * (h - 40)) for i, v in enumerate(s)]
        d.line(pts, fill=col, width=4)
        for p_, v in zip(pts, s):
            d.ellipse((p_[0] - 5, p_[1] - 5, p_[0] + 5, p_[1] + 5), fill=col)
            text(d, (p_[0] + 8, p_[1] - 22), str(v), 16, col, "mono")


# ---------- frames ----------
def f0():
    img, d = new_frame(NAME, "campaign")
    G4.base(d)
    campaign_bar(d, now=0)
    coin(d, (60, 160), 12)
    text(d, (78, 146), str(START), 28, INK, "mono")
    for i, roster in enumerate(CAMP):
        roster_chips(d, 940, 210 + i * 130, roster, 0.5, 66)
        flame(d, (900, 212 + i * 130), 8, HEAT)
        text(d, (870, 202 + i * 130), str((25, 50, 75)[i]), 14, HEAT, "mono", anchor="ra")
    header(d, NAME, 0, "Campaign leg: all three raids telegraphed on the Heat bar (who, from which corp site); the fortress starts empty, bank 14")
    return img


def f1():
    img, d = new_frame(NAME, "shop + fortress forecast")
    r = HOME_RUN[0][1]
    G4.base(d)
    campaign_bar(d, now=0)
    G5.routes(d, r)
    place_fort(d, HOME_LINE[0][0], HOME_LINE[0][1], new=HOME_LINE[0][0])
    shop(d, 20, 560, sel=("RAILGUN", "DECOY"), bank=START - spend(HOME_LINE[0][0]))
    panel(d, (636, 506, 1272, 704))
    proj_strip(d, 646, 512, PROJ_HOME, "1", True, w=616)
    proj_strip(d, 646, 608, PROJ_FWD, "2", False, w=616)
    for k, (buy, crew) in enumerate((HOME_LINE[0], FWD_LINE[0])):
        for j, (n, aa) in enumerate(buy.items()):
            for a in aa:
                piece(d, (662, 556 + j * 24 + k * 96), a, 7)
    header(d, NAME, 1, f"Visit 1 shop: railgun + decoy at home; the fortress forecast runs all 3 telegraphed raids with no more buys: home line ends {PROJ_HOME[-1][2]}, forward line {PROJ_FWD[-1][2]}")
    return img


def f2():
    img, d = new_frame(NAME, "forecast")
    fort, r, bank, crew = HOME_RUN[0]
    G4.base(d, r)
    campaign_bar(d, now=0)
    G5.routes(d, r)
    G4.tags(d, r)
    place_fort(d, fort, crew)
    G5.net_box(d, 1018, 130, r, price(r))
    proj_strip(d, 300, 600, PROJ_HOME, "1", True, w=616)
    button(d, (1060, 640, 1268, 690), "START RAID")
    header(d, NAME, 2, f"Raid 1 forecast: CLEAN={r.clean}; net {net(r):+d} (the railgun cost 10 now and pays in raids 2-3); fortress forecast below")
    return img


def f3():
    img, d = new_frame(NAME, "resolution")
    fort, r, bank, crew = HOME_RUN[0]
    s = min(2, len(r.steps))
    G4.base(d, r, step=s)
    campaign_bar(d, now=0)
    G5.routes(d, r, faint=True)
    place_fort(d, fort, crew)
    ev = r.steps[s - 1]
    pos = {}
    for tid, (site, hp, alive, hold) in ev["threats"].items():
        dead = any(k[0] == tid for k in ev["kills"])
        if not alive and not dead:
            continue
        x, y = XF.p(site)
        p = (x + 44, y - 8 + OFF.get(tid, 0) * 3)
        pos[tid] = p
        threat(d, p, tid, 15, hp=hp, ghost=dead)
        if dead:
            pencil_x(d, p, 16, seed=4)
        if hold:
            asset_icon(d, (p[0] + 24, p[1] - 22), "ICE", 8, HOLD)
    for i, (site, gun, tid, dmg, left) in enumerate(ev["shots"]):
        sx, sy = XF.p(site)
        if tid in pos:
            d.line([(sx, sy), pos[tid]], fill=CELL, width=4)
            order_badge(d, lerp((sx, sy), pos[tid], 0.5), i + 1, CELL)
            text(d, (pos[tid][0] + 18, pos[tid][1] - 44), f"-{dmg}", 22, CELL, "mono")
    speed_controls(d, 1060, 660)
    header(d, NAME, 3, f"Raid 1 playout, no input (step {s} of {len(r.steps)}): numbered shots from the installed pieces")
    return img


def f4():
    img, d = new_frame(NAME, "aftermath")
    fort, r, bank, crew = HOME_RUN[0]
    G4.base(d, r)
    campaign_bar(d, now=1)
    G4.tags(d, r)
    place_fort(d, fort, crew)
    G5.stamp_box(img, d, (1010, 150), r)
    G5.net_box(d, 886, 210, r, price(r))
    panel(d, (20, 560, 700, 700))
    coin(d, (50, 600), 11)
    text(d, (68, 586), f"{bank}", 24, STAMP_CLEAN if bank > 0 else DMG, "mono")
    text(d, (130, 586), f"+{INCOME}", 24, INK, "mono")
    netrun_hex = G4.netrun_hex
    netrun_hex(d, (200, 600), 10, INK)
    arrow(d, (230, 600), (270, 600), INK, 3, 8, shorten=0)
    coin(d, (300, 600), 11)
    text(d, (318, 586), f"{bank + INCOME}", 24, INK, "mono")
    for i, (n, aa) in enumerate(fort.items()):
        for j, a in enumerate(aa):
            piece(d, (420 + (i * 2 + j) * 40, 600), a, 10)
    check(d, (420, 650), 8, STAMP_CLEAN)
    header(d, NAME, 4, f"Raid 1 aftermath: {'CLEAN' if r.clean else 'HOLDS'}, bank {bank} (+{INCOME} from netruns); every piece stays installed for raid 2")
    return img


def visit(n: int):
    fort, r, bank_after, crew = HOME_RUN[n]
    buy = HOME_LINE[n][0]
    bank_before = HOME_RUN[n - 1][2] + INCOME
    img, d = new_frame(NAME, f"visit {n + 1}")
    G4.base(d, r)
    campaign_bar(d, now=n)
    for a, b in getattr(r, "frozen", []):
        G5.frozen_link(d, XF, a, b)
    G5.routes(d, r)
    G4.tags(d, r)
    place_fort(d, fort, crew, new=buy)
    shop(d, 20, 560, sel=tuple(p for v in buy.values() for p in v), bank=bank_before - spend(buy))
    rows = projection(fort, crew, n, bank_before - spend(buy))
    proj_strip(d, 636, 600, rows, str(n + 1), True, w=420)
    G5.net_box(d, 1018, 130, r, price(r))
    return img, d, r, rows


def f5():
    img, d, r, rows = visit(1)
    header(d, NAME, 5, f"Visit 2 (Heat 51): the railgun is already installed; buy turret + ICE; raid 2 forecast CLEAN={r.clean}, net {net(r):+d}; fortress forecast to raid 3")
    return img


def f6():
    img, d, r, rows = visit(2)
    fz = ", ".join(f"{a}-{b}" for a, b in r.frozen) or "none"
    header(d, NAME, 6, f"Visit 3 (Heat 76, 4 threats, Lockdown freezes {fz}): buy railgun + ICE; raid 3 forecast CLEAN={r.clean}, net {net(r):+d}")
    return img


def f7():
    img, d = new_frame(NAME, "record")
    fort, r, bank, crew = HOME_RUN[2]
    G4.base(d, r)
    G4.tags(d, r)
    place_fort(d, fort, crew)
    campaign_bar(d, now=3)
    s1 = [START] + [b for _, _, b, _ in HOME_RUN]
    s2 = [START] + [b for _, _, b, _ in FWD_RUN]
    bank_line(d, 760, 420, 500, 270, [s1, s2], [CELL, DIM])
    piece(d, (790, 440), "RAILGUN", 8)
    node_icon(d, (816, 440), "HOME", 18, CELL)
    piece(d, (790, 466), "SENTRY", 8, DIM)
    node_icon(d, (816, 466), "PROXY", 18, DIM)
    G4.record(d, 60, 640, 3, sum(1 for _, rr, _, _ in HOME_RUN if rr.clean))
    header(d, NAME, 7, f"Campaign record: the home fortress grew 2 pieces a visit: bank {s1}; the forward fortress (sentry+decoy at PROXY) would read {s2}")
    return img


FRAMES = [f0, f1, f2, f3, f4, f5, f6, f7]

if __name__ == "__main__":
    for nm, line in (("HOME", HOME_RUN), ("FWD", FWD_RUN)):
        for fort, r, bank, crew in line:
            print(nm, fort, crew, summary(r), "net", net(r), "bank", bank)
    print("PROJ_HOME", [(i, r.clean, b) for i, r, b in PROJ_HOME])
    print("PROJ_FWD", [(i, r.clean, b) for i, r, b in PROJ_FWD])
