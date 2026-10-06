"""Round 44 A: contact_A.jpg - each new render beside the build capture it replaces (build left, concept right).

python contact44.py [probe]   (probe: writes scratch/probe_builds.jpg with just the build crops, to check the boxes)
Build captures are read from D:\\Godot\\rebel_cell (read only).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw  # noqa: E402

import kit44 as KT  # noqa: E402
import ui31 as K  # noqa: E402

AR = r"D:\Godot\rebel_cell\docs\art_review"
G = os.path.join(AR, "HQ_REDESIGN", "build", "g_final.jpg")
MV = os.path.join(AR, "PARITY", "fixes", "MAPVIEW.jpg")
HA = os.path.join(AR, "PARITY", "fixes", "HEAT_ALL.jpg")
RC = os.path.join(AR, "PARITY", "fixes", "ROUTE_c.jpg")

ROWS = [
    ("hq_idle.png", G, (980, 50, 1945, 592), "build: HQ_REDESIGN/build/g_final.jpg  s1.0 idle"),
    ("hq_node_selected.png", G, (980, 3604, 1945, 4146), "build: g_final.jpg  s1.0 claim (a node selected)"),
    ("route_page.png", RC, (644, 52, 1282, 402), "build: PARITY/fixes/ROUTE_c.jpg  after, Meridian 1.0"),
    ("route_page_hover_all.png", MV, (1282, 2023, 1920, 2356), "build: PARITY/fixes/MAPVIEW.jpg  after, route start (hover: all nodes)"),
    ("raid_setup.png", HA, (402, 1517, 800, 1745), "build: PARITY/fixes/HEAT_ALL.jpg  raid_setup x1.6"),
    ("topbar_by_page.png", HA, (0, 250, 1200, 1250), "build: PARITY/fixes/HEAT_ALL.jpg  route, combat, event, loot: every page carries the bar"),
]
CW, CH = 940, 529
LAB = 34


def fit(im, w, h, bg=(14, 13, 20)):
    k = min(w / im.width, h / im.height)
    r = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    out = Image.new("RGB", (w, h), bg)
    out.paste(r, ((w - r.width) // 2, (h - r.height) // 2))
    return out


def build(probe=False):
    W = 20 + CW + 20 + CW + 20
    H = 70 + len(ROWS) * (CH + LAB + 18) + 10
    sheet = Image.new("RGBA", (W, H), (10, 9, 16, 255))
    K.text(sheet, (20, 34), "ROUND 44 A  //  MAP SCREENS:  BUILD (LEFT)  vs  CONCEPT (RIGHT)", KT.F(K.ANTON, 30), (244, 244, 248), "lm", 0.8)
    y = 70
    for name, src, box, lab in ROWS:
        b = fit(Image.open(src).convert("RGB").crop(box), CW, CH)
        sheet.paste(b, (20, y + LAB))
        K.text(sheet, (22, y + 16), lab, KT.F(K.MONO, 16), (190, 120, 120), "lm", 0.4)
        if not probe:
            c = fit(Image.open(os.path.join(KT.OUT, name)).convert("RGB"), CW, CH)
            sheet.paste(c, (40 + CW, y + LAB))
            K.text(sheet, (42 + CW, y + 16), "concept: " + name, KT.F(K.MONO, 16), (140, 230, 160), "lm", 0.4)
        y += CH + LAB + 18
    out = sheet.convert("RGB")
    if probe:
        out.save(os.path.join(KT.SCR, "probe_builds.jpg"), quality=80)
    else:
        out.save(os.path.join(KT.OUT, "contact_A.jpg"), quality=86, optimize=True)
    print("ok")


if __name__ == "__main__":
    build("probe" in sys.argv)
