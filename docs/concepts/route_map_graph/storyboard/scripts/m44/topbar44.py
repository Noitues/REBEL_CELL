"""Round 44 A: the resource bar by page (REVIEW f "Resource top bar", Q1).

python topbar44.py -> topbar_by_page.png (run hq44.py and route44.py first: their top bands are reused as rows 1-2)
One terminal style everywhere (kit44.topbar): icon + mono label + bare Anton value; Heat = number, band word, strip.
  HQ / City Grid   the full bar (the only page that keeps it) + VIEW LOADOUT
  netrun pages     Heat, HP, Cycles
  MAINFRAME shop   Cycles
  combat           no bar: a 120 x 32 terminal Heat chip top left (number, band word, strip)
  loot / event     only what the choice on that page changes
Rows 3-6 are drawn over the locked concept screens (round 33 shop v3, round 41 combat v4, round 32 loot v2, round 31
event) at their real 1080p position.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw  # noqa: E402

import kit44 as KT  # noqa: E402
import ui31 as K  # noqa: E402

BAND = 130
ROW = 160
TOP = 84


def band(src, y0=0):
    im = Image.open(src).convert("RGBA").crop((0, y0, 1920, y0 + BAND))
    return im


def heat_chip(img, x, y, v=52):
    """Combat: 120 x 32 terminal chip, number + band word + strip (bible 3.15 keeps Heat out of the HUD otherwise)."""
    name, _, bc = KT.heat_band(v)
    box = (x, y, x + 120, y + 32)
    img = KT.term(img, box, None, accent=bc, header=False, seed=5, chamfer=6)
    img = K.live_number(img, (x + 7, y + 17), str(v), 24, bc, "lm", 0.6, 0.35)
    K.text(img, (x + 42, y + 9), name, KT.F(K.MONO, 11), bc, "lm", 1.0)
    d = K.BD(img)
    bx, bw = x + 42, 70
    d.rectangle([bx, y + 19, bx + bw, y + 24], fill=tuple(int(c * 0.25) for c in bc) + (255,))
    d.rectangle([bx, y + 19, bx + bw * v / 100, y + 24], fill=bc + (255,))
    for t in (25, 50, 75):
        d.line([(bx + bw * t / 100, y + 17), (bx + bw * t / 100, y + 26)], fill=(235, 240, 250, 255), width=1)
    return img


def caption(img, y, title, text):
    K.text(img, (20, y + BAND + 15), title, KT.F(K.ANTON, 18), (240, 240, 246), "lm", 0.8)
    x = 20 + KT.F(K.ANTON, 18).getlength(title) + 16
    K.text(img, (x, y + BAND + 15), text, KT.F(K.MONO, 15), (165, 175, 192), "lm", 0.5)


def build():
    sheet = Image.new("RGBA", (1920, 1080), (10, 9, 16, 255))
    K.text(sheet, (22, 30), "RESOURCE BAR BY PAGE", KT.F(K.ANTON, 40), (244, 244, 248), "lm", 0.8)
    K.text(sheet, (24, 66), "one terminal style (bible 1.2 / 4.13): glyph + mono label + bare Anton value.  Heat = number + band word + "
                            "strip, never a stamp.  Each row is the top of that page at 1:1 (1080p).", KT.F(K.MONO, 15), (160, 168, 186), "lm", 0.4)
    rows = []
    # 1. HQ / City Grid: the full bar (from hq_idle.png)
    rows.append((band(os.path.join(KT.OUT, "hq_idle.png")), "HQ / CITY GRID",
                 "the full bar: Heat, Schematics, Home, Exploits, Raids, ICE, Crew + VIEW LOADOUT.  The only page that keeps it."))
    # 2. netrun (route page, transit, HQ run): Heat, HP, Cycles (from route_page.png)
    rows.append((band(os.path.join(KT.OUT, "route_page.png")), "NETRUN PAGES",
                 "route, transit, HQ run: Heat, HP, Cycles.  Everything else is behind VIEW LOADOUT / the dossier."))
    # 3. shop: Cycles (the counter sits after the MAINFRAME sign, never over it)
    im = band(os.path.join(KT.CONC, "round33_shop", "shop_v3_layout.png"))
    im, _ = KT.topbar(im, 236, 12, [dict(kind="cycles", label="CYCLES", value="160")])
    rows.append((im, "MAINFRAME SHOP", "Cycles only, after the sign (the clerk's WALLET line folds into it)."))
    # 4. combat: no bar, the Heat chip top left
    im = band(os.path.join(KT.CONC, "round41_wheel_stack", "combat_typical_v4.png"))
    im = heat_chip(im, 16, 14, 52)
    rows.append((im, "COMBAT", "no bar (Q1 c): a 120 x 32 terminal Heat chip, top left.  HP, RAM and piles stay on the HUD."))
    # 5. loot: the pick changes the deck
    im = band(os.path.join(KT.CONC, "round32_shop_reward", "reward_screen_v2.png"))
    im, _ = KT.topbar(im, 540, 30, [dict(kind="deck", label="DECK", value="17", max="+1")], scale=0.9)
    rows.append((im, "LOOT", "only what the pick changes: DECK (beside FIGHT WON).  The PAYOUT terminal is the fight's result, not a bar."))
    # 6. event: the choices change HP, Cycles, crew
    im = band(os.path.join(KT.CONC, "round31_reward_event", "event_screen.png"))
    im, _ = KT.topbar(im, 16, 12, [dict(kind="hp", label="HP", value="41", max="/60"), dict(kind="cycles", label="CYCLES", value="160"),
                                   dict(kind="crew", label="CREW", value="4")])
    rows.append((im, "EVENT", "only what its choices change (HP, Cycles, crew); replaces the RUN panel. A Heat choice adds the Heat cell."))
    y = TOP + 8
    for im, title, text in rows:
        sheet.alpha_composite(im, (0, y))
        d = ImageDraw.Draw(sheet)
        d.rectangle([0, y, 1919, y + BAND - 1], outline=(60, 64, 80, 255), width=1)
        caption(sheet, y, title, text)
        y += ROW
    return sheet


if __name__ == "__main__":
    KT.save(build(), "topbar_by_page.png")
