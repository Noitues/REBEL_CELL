"""V3 AAA deliverables from the passes.

python finish_aaa.py still <look> [hover]   -> ../AAA<n>_<name>[_hover].png (+ plates/AAA<n>_..._plate.png, no UI)
python finish_aaa.py compare                -> ../compare_aaa.jpg (V3 dynamic O_overview | AAA-1 | AAA-2 | AAA-3, labelled)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw  # noqa: E402

import post_aaa  # noqa: E402
import compose_aaa  # noqa: E402
import ui31 as K  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
NAMES = {"cel": "AAA1_premium_cel", "real": "AAA2r3", "hybrid": "AAA3_hybrid"}     # r3: only "real" is rebuilt
LABELS = {"cel": "AAA-1  PREMIUM CEL", "real": "AAA-2  REALISTIC NIGHT", "hybrid": "AAA-3  HYBRID"}


def still(look, hover=False, q=""):
    tag = look + ("_hover" if hover else "")
    bl = os.path.join(SCR, "bl_%s" % tag + ("_" + q if q else ""))          # jobs_aaa.py final quality writes here
    os.makedirs(os.path.join(ROOT, "plates"), exist_ok=True)
    name = NAMES[look] + ("_hover" if hover else "") + ("_" + q if q else "")
    plate = os.path.join(ROOT, "plates", name + "_plate.png")
    post_aaa.finish(bl, look).save(plate)
    compose_aaa.compose(plate, bl, os.path.join(ROOT, name + ".png"), hover)


def compare():
    """3 x 2: the current V3 dynamic overview, the critiqued test (before), then AAA-1, AAA-2, AAA-3 and the hover."""
    sys.path.insert(0, HERE)
    import stats_aaa
    tiles = [("V3 DYNAMIC  O_overview (current)", os.path.join(os.path.dirname(ROOT), "v3_dynamic", "O_overview.png")),
             ("BEFORE  c_real_test (critiqued)", os.path.join(ROOT, "keep", "c_real_test_designer_liked.png"))]
    tiles += [(LABELS[l], os.path.join(ROOT, NAMES[l] + ".png")) for l in ("cel", "real", "hybrid")]
    tiles.append(("AAA-3  HYBRID  hover: option 2 (Rack)", os.path.join(ROOT, NAMES["hybrid"] + "_hover.png")))
    tw, th = 1280, 720
    out = Image.new("RGB", (tw * 2 + 30, (th + 40) * 3 + 20), (10, 9, 14))
    d = ImageDraw.Draw(out)
    for k, (lab, p) in enumerate(tiles):
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = 10 + (k % 2) * (tw + 10), 10 + (k // 2) * (th + 40)
        out.paste(im, (x, y))
        st = stats_aaa.stats(p)
        d.text((x + 6, y + th + 6), lab, font=K.F(K.MONO, 22), fill=(212, 255, 0))
        d.text((x + 560, y + th + 8), "median %.2f  <0.10 %d %%  >0.85 %.1f %%" % (st["median"], st["under"], st["over"]),
               font=K.F(K.MONO, 18), fill=(190, 200, 220))
    out.save(os.path.join(ROOT, "compare_aaa.jpg"), quality=92)
    print("saved compare_aaa.jpg")


def _main():
    if sys.argv[1] == "compare_r2":
        compare_r2()
    elif sys.argv[1] == "still":
        still(sys.argv[2], "hover" in sys.argv[3:], next((a for a in sys.argv[3:] if a in ("test", "mini")), ""))
    else:
        compare()


def compare_r2():
    """2 x 2: AAA-2 before (round 1), AAA-2 r2, the r2 hover, the r2 plate; each with the critic's numbers."""
    import stats_aaa
    tiles = [("BEFORE  AAA-2 realistic night (round 1)", os.path.join(os.path.dirname(ROOT), "AAA2_realistic_night.png")),
             ("AAA-2 r2  (wax links, streak traffic, new shapes)", os.path.join(ROOT, "AAA2r2.png")),
             ("AAA-2 r2  hover: option 2 (Rack), power cut", os.path.join(ROOT, "AAA2r2_hover.png")),
             ("AAA-2 r2  plate (no UI)", os.path.join(ROOT, "plates", "AAA2r2_plate.png"))]
    tw, th = 1280, 720
    out = Image.new("RGB", (tw * 2 + 30, (th + 46) * 2 + 20), (10, 9, 14))
    d = ImageDraw.Draw(out)
    for k, (lab, p) in enumerate(tiles):
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = 10 + (k % 2) * (tw + 10), 10 + (k // 2) * (th + 46)
        out.paste(im, (x, y))
        st = stats_aaa.stats(p)
        d.text((x + 6, y + th + 8), lab, font=K.F(K.MONO, 22), fill=(212, 255, 0))
        d.text((x + 700, y + th + 10), "median %.3f  p95 %.2f  <0.10 %.0f %%  >0.85 %.1f %%" % (
            st["median"], st["p95"], st["under"], st["over"]), font=K.F(K.MONO, 18), fill=(190, 200, 220))
    out.save(os.path.join(ROOT, "compare_r2.jpg"), quality=92)
    print("saved compare_r2.jpg")


if __name__ == "__main__":
    _main()
