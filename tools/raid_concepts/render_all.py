"""Render every raid concept's five key frames, plain and text-scrambled, plus one contact sheet each.

    python tools/raid_concepts/render_all.py [--only a,b] [--round r1]

Writes docs/design/raid_concepts/<concept>/<round>/mockups/*.png, .../scrambled/*.png and sheet.jpg / sheet_scrambled.jpg.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rc_draw  # noqa: E402

ROOT = HERE.parent.parent
OUT = ROOT / "docs" / "design" / "raid_concepts"
CONCEPTS = {
    "a": ("concept_a_telegraph", "a_telegraph"),
    "b": ("concept_b_lanes", "b_siege_lanes"),
    "c": ("concept_c_duel", "c_strength_duel"),
    "d": ("concept_d_loadout", "d_autobattler_loadout"),
    "e": ("concept_e_countdown", "e_countdown_allocation"),
    "f": ("concept_f_ledger", "f_plan_ledger"),
    "a2": ("concept_a2_telegraph", "a_telegraph"),
    "b2": ("concept_b2_lanes", "b_siege_lanes"),
    "c2": ("concept_c2_duel", "c_strength_duel"),
    "d2": ("concept_d2_loadout", "d_autobattler_loadout"),
    "e2": ("concept_e2_countdown", "e_countdown_allocation"),
    "f2": ("concept_f2_ledger", "f_plan_ledger"),
    "g3": ("concept_g3_merged", "g_merged_telegraph"),
    "g4": ("concept_g4_merged", "g_merged_telegraph"),
    "g5": ("concept_g5_merged", "g_merged_telegraph"),
    "h6": ("concept_h6_bastion", "h_bastion"),
    "p6": ("concept_p6_stakes", "p_stakes"),
    "hp6": ("concept_hp6_merged", "hp_bastion_stakes"),
    "h7": ("concept_h7_bastion", "h_bastion"),
    "f3": ("concept_f3_ledger", "f_plan_ledger"),
    "c3": ("concept_c3_duel", "c_strength_duel"),
    "d3": ("concept_d3_loadout", "d_autobattler_loadout"),
    "e3": ("concept_e3_countdown", "e_countdown_allocation"),
}
MOMENTS = ["1_warning", "2_planning", "3_forecast", "4_resolution", "5_aftermath", "6_next_raid"]


def sheet(paths: list[Path], out: Path) -> None:
    ims = [Image.open(p) for p in paths]
    tw, th = 640, 360
    rows = (len(ims) + 1) // 2
    s = Image.new("RGB", (tw * 2 + 30, th * rows + 10 * rows + 10), (8, 9, 18))
    for i, im in enumerate(ims):
        x, y = 10 + (i % 2) * (tw + 10), 10 + (i // 2) * (th + 10)
        s.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
    s.save(out, quality=88)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--round", default="r1")
    a = ap.parse_args()
    keys = [k for k in a.only.split(",") if k] or list(CONCEPTS)
    for k in keys:
        mod_name, folder = CONCEPTS[k]
        for scr in (False, True):
            rc_draw.SCRAMBLE = scr
            mod = importlib.reload(importlib.import_module(mod_name))
            sub = "scrambled" if scr else "mockups"
            paths = []
            for fn, m in zip(mod.FRAMES, getattr(mod, "MOMENTS", MOMENTS)):
                p = OUT / folder / a.round / sub / f"{m}.png"
                rc_draw.save(fn(), p)
                paths.append(p)
            sheet(paths, OUT / folder / a.round / ("sheet_scrambled.jpg" if scr else "sheet.jpg"))
        print("rendered", folder, a.round)


if __name__ == "__main__":
    main()
