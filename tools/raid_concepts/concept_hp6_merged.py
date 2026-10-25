"""Concept HP, round 6: BASTION + STAKES merged (each rule a designer decision).
- H: the fortress persists; buy up to 2 pieces per HQ visit; all raids of the leg are telegraphed; the shop shows the
  fortress forecast through the telegraphed raids.
- P: every node has a job (Vault +3/netrun, Relay +1 branch, Safehouse = crew, Firewall = home's gun, Proxy = intel),
  and threats that survive a raid JOIN THE NEXT ONE (the forecast's later raids grow when you let threats live).
Numbers: sim.py with the round-5 package on bastion_campaign's campaign 1; survivors carry into the next roster with a
"#n" id. The home line and the forward line are H's two measured buy lines, re-run under the carry rule."""
from __future__ import annotations

from r2_kit import *  # noqa: F403
from sim import Plan, run, summary

import concept_g3_merged as G3
import concept_g4_merged as G4
import concept_g5_merged as G5
import concept_h6_bastion as H
import concept_p6_stakes as P
from bastion_campaign import COST, INCOME, RULE, START
from concept_g4_merged import piece
from depth_harness import net, price

NAME = "HP BASTION+STAKES r6"
MOMENTS = ["0_campaign", "1_shop", "2_forecast", "3_aftermath", "4_visit2", "5_record"]
XF = G3.XF
CAMP = H.CAMP


def carry(roster, r, n):
    """Next roster plus this raid's survivors (they fall back to their corp site and rejoin)."""
    dead = {t for ev in r.steps for t, _ in ev["kills"]}
    out = list(roster)
    for tid in r.routes:
        if tid not in dead and not tid.startswith("CASCADE"):
            base = tid.split("#")[0]
            entry = r.paths[tid][0]
            out.append((f"{base}#{n}", entry))
    return out


def play(line):
    bank, fort, out, roster = START, {}, [], list(CAMP[0])
    for i in range(3):
        buy, crew = line[i]
        fort = H.merge(fort, buy)
        bank -= H.spend(buy)
        r = run(Plan(fort, crew, dict(RULE)), threats=list(roster))
        bank += net(r)
        out.append((dict(fort), r, bank, crew, list(roster)))
        for k, v in r.nodes.items():
            if v["outcome"] == "taken":
                fort.pop(k, None)
        if i < 2:
            bank += INCOME
            roster = carry(CAMP[i + 1], r, i + 2)
    return out


def forecast(fort, crew, bank, i0, roster):
    """Fortress forecast with the carry rule: no further buys."""
    f = {k: list(v) for k, v in fort.items()}
    rows = []
    for i in range(i0, 3):
        r = run(Plan(f, crew, dict(RULE)), threats=list(roster))
        bank += net(r)
        rows.append((i, r, bank, list(roster)))
        for k, v in r.nodes.items():
            if v["outcome"] == "taken":
                f.pop(k, None)
        if i < 2:
            bank += INCOME
            roster = carry(CAMP[i + 1], r, i + 2)
    return rows


HOME_RUN, FWD_RUN = play(H.HOME_LINE), play(H.FWD_LINE)
FC_HOME = forecast(H.HOME_LINE[0][0], H.HOME_LINE[0][1], START - H.spend(H.HOME_LINE[0][0]), 0, list(CAMP[0]))
FC_FWD = forecast(H.FWD_LINE[0][0], H.FWD_LINE[0][1], START - H.spend(H.FWD_LINE[0][0]), 0, list(CAMP[0]))


def strip(d, x, y, rows, label, on=True, w=616) -> None:
    """Per telegraphed raid: roster size (survivors who rejoin in cobalt outline), lost jobs struck, bank after."""
    d.rounded_rectangle((x, y, x + w, y + 92), radius=6, fill=(50, 46, 30) if on else BG2,
                        outline=CELL if on else PANEL_EDGE, width=3 if on else 1)
    text(d, (x + 10, y + 6), label, 22, CELL if on else DIM, "mono")
    cw = (w - 40) // 3
    for j, (i, r, bank, roster) in enumerate(rows):
        cx = x + 36 + j * cw
        for k, (tid, e) in enumerate(roster[:6]):
            back = "#" in tid
            threat(d, (cx + 12 + k * 20, y + 18), tid.split("#")[0], 6, show_hp=False, ghost=back)
        lost_ = P.lostjobs(r)
        for k, jb in enumerate(lost_[:3]):
            P.job_icon(d, (cx + 14 + k * 30, y + 50), jb, 7, DIM, struck=True)
        if not lost_:
            check(d, (cx + 14, y + 50), 6, STAMP_CLEAN)
        coin(d, (cx + 14, y + 78), 7)
        text(d, (cx + 24, y + 70), str(bank), 15, STAMP_CLEAN if bank > 0 else DMG, "mono")


def f0():
    img = H.f0()
    d = ImageDraw.Draw(img)
    P.jobs_on_map(d)
    d.rectangle((0, H_ if False else 694, 1280, 720), fill=BG)
    header(d, NAME, 0, "Campaign leg: three telegraphed raids; each node's job drawn on it; the fortress starts empty, bank 14")
    return img


def f1():
    img, d = new_frame(NAME, "shop + forecast")
    fort, r, bank, crew, roster = HOME_RUN[0]
    G4.base(d)
    H.campaign_bar(d, now=0)
    G5.routes(d, r)
    P.jobs_on_map(d)
    H.place_fort(d, H.HOME_LINE[0][0], crew, new=H.HOME_LINE[0][0])
    H.shop(d, 20, 560, sel=("RAILGUN", "DECOY"), bank=START - H.spend(H.HOME_LINE[0][0]))
    panel(d, (636, 506, 1272, 704))
    strip(d, 646, 512, FC_HOME, "1", True)
    strip(d, 646, 608, FC_FWD, "2", False)
    header(d, NAME, 1, f"Shop + fortress forecast with the carry rule: survivors (outlined) swell the later raids; home line ends {FC_HOME[-1][2]}, forward line {FC_FWD[-1][2]}")
    return img


def f2():
    fort, r, bank, crew, roster = HOME_RUN[0]
    img, d = new_frame(NAME, "forecast")
    G4.base(d, r)
    H.campaign_bar(d, now=0)
    G5.routes(d, r)
    G4.tags(d, r)
    P.jobs_on_map(d, r)
    H.place_fort(d, fort, crew)
    G5.net_box(d, 1018, 130, r, price(r))
    panel(d, (900, 250, 1268, 330))
    sv = P.survivors(r)
    for i, t in enumerate(sv):
        threat(d, (930 + i * 40, 290), t.split("#")[0], 10, show_hp=False)
    arrow(d, (940 + len(sv) * 40, 290), (980 + len(sv) * 40, 290), THREAT, 3, 8, shorten=0)
    G4.netrun_hex(d, (1000 + len(sv) * 40, 290), 9, THREAT)
    button(d, (1060, 640, 1268, 690), "START RAID")
    header(d, NAME, 2, f"Raid 1 forecast: lost jobs {', '.join(P.lostjobs(r)) or 'none'}; {len(sv)} survivor(s) will rejoin raid 2; net {net(r):+d}")
    return img


def f3():
    fort, r, bank, crew, roster = HOME_RUN[0]
    img, d = new_frame(NAME, "aftermath")
    G4.base(d, r)
    H.campaign_bar(d, now=1)
    G4.tags(d, r)
    P.jobs_on_map(d, r)
    H.place_fort(d, fort, crew)
    G5.stamp_box(img, d, (1010, 150), r)
    G5.net_box(d, 886, 210, r, price(r))
    nxt = HOME_RUN[1][4]
    panel(d, (20, 560, 860, 700))
    for i, (tid, e) in enumerate(nxt):
        threat_chip(d, (70 + i * 90, 625), tid.split("#")[0], scale=0.6)
        if "#" in tid:
            G4.netrun_hex(d, (70 + i * 90, 680), 7, THREAT)
    header(d, NAME, 3, f"Raid 1 aftermath: {len(nxt) - len(CAMP[1])} survivor(s) rejoin; raid 2 now has {len(nxt)} threats; bank {bank} (+{INCOME})")
    return img


def f4():
    fort, r, bank_after, crew, roster = HOME_RUN[1]
    buy = H.HOME_LINE[1][0]
    bank_before = HOME_RUN[0][2] + INCOME
    img, d = new_frame(NAME, "visit 2")
    G4.base(d, r)
    H.campaign_bar(d, now=1)
    G5.routes(d, r)
    G4.tags(d, r)
    P.jobs_on_map(d, r)
    H.place_fort(d, fort, crew, new=buy)
    H.shop(d, 20, 560, sel=tuple(p for v in buy.values() for p in v), bank=bank_before - H.spend(buy))
    rows = forecast(fort, crew, bank_before - H.spend(buy), 1, roster)
    strip(d, 636, 600, rows, "2", True, w=420)
    G5.net_box(d, 1018, 130, r, price(r))
    header(d, NAME, 4, f"Visit 2: {len(roster)} threats (survivors included); buy turret + ICE; forecast CLEAN={r.clean}, net {net(r):+d}")
    return img


def f5():
    fort, r, bank, crew, roster = HOME_RUN[2]
    img, d = new_frame(NAME, "record")
    G4.base(d, r)
    G4.tags(d, r)
    P.jobs_on_map(d, r)
    H.place_fort(d, fort, crew)
    H.campaign_bar(d, now=3)
    s1 = [START] + [b for _, _, b, _, _ in HOME_RUN]
    s2 = [START] + [b for _, _, b, _, _ in FWD_RUN]
    H.bank_line(d, 760, 420, 500, 270, [s1, s2], [CELL, DIM])
    G4.record(d, 60, 640, 3, sum(1 for _, rr, _, _, _ in HOME_RUN if rr.clean))
    header(d, NAME, 5, f"Campaign record under the carry rule: home line {s1}, forward line {s2}")
    return img


H_ = 720
FRAMES = [f0, f1, f2, f3, f4, f5]

if __name__ == "__main__":
    for nm, line in (("HOME", HOME_RUN), ("FWD", FWD_RUN)):
        for fort, r, bank, crew, roster in line:
            print(nm, len(roster), [t for t, _ in roster], summary(r)[:120], "net", net(r), "bank", bank, "surv", P.survivors(r))
    print("FC_HOME", [(i, len(ro), b) for i, r, b, ro in FC_HOME])
    print("FC_FWD", [(i, len(ro), b) for i, r, b, ro in FC_FWD])
