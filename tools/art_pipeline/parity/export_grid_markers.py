"""M14 asset parity: the City Grid's Site markers v4 (ART-5 5d) from round 42's own generator.

Runs `docs/concepts/round42_site_markers/scripts/markers42.py` (tag art-concepts-r43) unchanged: its
`disc`, `cell_disc`, `seizure_memo`, `badge`, `pad` and `bolt_mask` draw every marker part, which this
wrapper saves one item per transparent PNG at 2x the v4 key sheet's size (disc 30 px -> 60 px, Exploit
34 -> 68, pad r 17 -> 34, the slip 1.25 x the disc). The concept's strokes are fixed pixel widths, so
a 2x item reads like the sheet's close zoom (x1.7), which the concept draws the same way.

    python tools/art_pipeline/parity/export_grid_markers.py --concepts <extracted>/docs/concepts

Output: assets/city/grid_markers/*.png + manifest.json.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parity_common as PC  # noqa: E402

ROUND = "round42_site_markers"
OUT = PC.ROOT / "assets" / "city" / "grid_markers"
X2 = 2
# The corps' primary hues (ART_BIBLE v2 2.4), for the corporate pads' pins: the concept draws
# Meridian's (markers42.MER); the same `pad` call draws the others with their own hue.
CORP_HUE = {"meridian": (255, 140, 26), "solace": (150, 255, 70), "halcyon": (176, 110, 255),
            "orbital": (205, 240, 255), "rebel_cell": (232, 20, 30)}


def main() -> int:
    a = PC.args(__doc__.splitlines()[0])
    scripts = PC.use_round(a.concepts, ROUND)
    from PIL import Image

    import markers42 as M
    import r32ui as U

    man = PC.Manifest(OUT, "grid_markers", "M14 asset parity: City Grid Site markers v4 (ART_BIBLE v2 4.5; round 42 site_markers_v4).",
                      ROUND, ["markers42.py", "r32ui.py", "r35ui.py", "r31lib.py", "sticker_lib19.py", "route_d_city.py", "city_view.py"],
                      "tools/art_pipeline/parity/export_grid_markers.py")

    # The icon discs (KIND), corporate and cleared (the concept greys a cleared disc).
    site_px, exploit_px = 30 * X2, 34 * X2
    for status in ("corporate", "cleared"):
        suffix = "" if status == "corporate" else "_cleared"
        man.add(M.disc("site", site_px, None, status), "disc_site_meridian" + suffix, "markers42.disc('site', %d, None, '%s')" % (site_px, status),
                "Meridian's crane-A crest disc (the concept's regular Site)")
        man.add(M.disc("heat", site_px, None, status), "disc_heat" + suffix, "markers42.disc('heat', %d, None, '%s')" % (site_px, status))
        man.add(M.disc("exploit", exploit_px, None, status), "disc_exploit" + suffix, "markers42.disc('exploit', %d, None, '%s')" % (exploit_px, status))
        for ex in ("INTEL", "BREACH", "VIRUS"):
            man.add(M.disc("exploit", exploit_px, ex, status), "disc_exploit_%s%s" % (ex.lower(), suffix),
                    "markers42.disc('exploit', %d, '%s', '%s')" % (exploit_px, ex, status))
    # Yours: the lime fist (thumb tucked); CORE: the lime heart (the concept's CORE disc is 34 px).
    man.add(M.cell_disc("relay", site_px), "disc_claimed", "markers42.cell_disc('relay', %d)" % site_px, "the rebel fist, thumb tucked (fist_mask)")
    man.add(M.cell_disc("home", 34 * X2), "disc_core", "markers42.cell_disc('home', %d)" % (34 * X2), "CORE's heart (route_d_city.cell_icon)")

    # TAKEN: the corp SEIZURE NOTICE slip (Meridian's letterhead mark; tilted -8 deg by the concept).
    memo_px = int(site_px * 1.25)
    man.add(M.seizure_memo(memo_px), "slip_taken", "markers42.seizure_memo(%d)" % memo_px, "already tilted -8 deg; Meridian crane-A letterhead")

    # The CLEARED corner badge (grey check), drawn on a clear canvas at 2x its radius.
    r = 9 * X2
    can = Image.new("RGBA", (r * 2 + 8, r * 2 + 8), (0, 0, 0, 0))
    man.add(M.badge(can, can.width / 2, can.height / 2, "cleared", r=r), "badge_cleared", "markers42.badge(canvas, cx, cy, 'cleared', r=%d)" % r)

    # DOWN: the white bolt (bolt_mask), one white mask; the view draws its ink shadow from it too.
    man.add(M.tint(M.g_mask(M.bolt_mask, 256), (250, 250, 250)), "bolt_down", "markers42.tint(markers42.g_mask(markers42.bolt_mask, 256), (250, 250, 250))",
            "the v3/v4 DOWN bolt; drawn 2.1 x (disc / 2 + 9) across, its shadow the same mask in ink offset (2, 3)")

    # The pads (raid socket, OWNERSHIP), r 17 at 2x, on a canvas wide enough for the glow.
    pr = 17 * X2
    k = float(X2)
    side = int(pr * 2 + 40 * k)
    PAD_NOTE = "square canvas %d px, the pad's centre at its centre, half-width (r) %d px" % (side, pr)

    def pad_png(own: str):
        can = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        return M.pad(can, side / 2, side / 2, pr, own, k)

    for own, name in (("claimed", "pad_claimed"), ("sei" + "zed", "pad_taken"), ("cleared", "pad_cleared"), ("dis" + "abled", "pad_down")):
        man.add(pad_png(own), name, "markers42.pad(canvas, cx, cy, %d, '%s', %.1f)" % (pr, own, k), PAD_NOTE)
    for corp, hue in CORP_HUE.items():
        can = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        q = M.CV.diamond(side / 2, side / 2, pr)
        # markers42.pad's own 'corporate' arguments, with this corp's hue for the pins.
        im = U.pad(can, q, hue, lit=0.7, glow=0.2, fill_a=215, k=0.85 * k)
        man.add(im, "pad_corporate_" + corp, "r32ui.pad(canvas, city_view.diamond(cx, cy, %d), %s, lit=0.7, glow=0.2, fill_a=215, k=%.2f)" % (pr, hue, 0.85 * k),
                PAD_NOTE + "; markers42.pad's corporate call with this corp's hue (the concept shows Meridian's)")

    man.write(scripts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
