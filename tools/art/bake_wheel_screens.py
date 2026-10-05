"""Bake the wheel slice CRT screens (ART-2 2A; ART_BIBLE v2 3.4, 6.2) from the concept recipes.

The slice screens of family C "Screens & Data" are drawn by the concept generator scripts on tag
`art-concepts-r43` (round 41 copy: `docs/concepts/round41_wheel_stack/scripts/`: programs.py,
screens10.py, skins.py, scenes18.py). This runs those recipes unchanged and packs their frames into
flipbook atlases the wheel shader (`shaders/wheel/wheel_disc.gdshader`) samples:

- `assets/wheel/screens/<kit>_screen.png`: per slice kind (rows, RC.SliceType order + SPECIAL), FRAMES
  columns of the screen texture in the slice's own polar texture space (x = arc length from the
  midline, y = distance in from the outer rim), with the recipe's phosphor glow already added.
- `assets/wheel/screens/<kit>_scene.png` (corp kits only): the corp animation, drawn upright in screen
  space over the darkened material (round 16), same layout.
- `assets/wheel/screens/meta.json`: cell size, frames, the master geometry and each corp's scene row.

Fonts: the recipes' concept-only faces (Consolas, Bahnschrift) are remapped to the shipped faces
(Share Tech Mono, Anton, IBM Plex Sans Condensed; ART_BIBLE 2.9 "Consolas ... MUST NOT ship").

Usage (never from stdin on this machine):
    git archive -o %TEMP%\\a2a\\c.tar art-concepts-r43 docs/concepts/round41_wheel_stack/scripts
    (extract it) then
    python tools/art/bake_wheel_screens.py --src <extracted>/docs/concepts/round41_wheel_stack/scripts
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT = ROOT / "assets" / "wheel" / "screens"

FRAMES = 12
SCALE = 0.5
SPAN = 60.0
# RC.SliceType order (scripts/data/rc.gd) -> the recipe's program name; row 9 is the corp special.
KINDS = ["EXPLOIT", "ZERO-DAY", "FIREWALL", "PROXY", "SANDBOX", "TROJAN", "PATCH", "VIRUS", "NULL", "SPECIAL"]
KITS = ["player", "meridian", "solace", "halcyon", "orbital", "rebel_cell"]
SPECIALS = {"meridian": "priority", "solace": "dose", "halcyon": "citation", "orbital": "solar_flare", "rebel_cell": "dose"}


def remap_fonts(SL) -> None:
    """Point the recipes' font loader at the shipped faces."""
    from PIL import ImageFont

    cache: dict = {}

    def font(name, px, variation=None):
        n = name.lower()
        if n.startswith("consola"):
            path = FONTS / "ShareTechMono-Regular.ttf"
        elif n.startswith("bahnschrift") and variation is not None and b"Condensed" in variation and b"Bold" in variation:
            path = FONTS / "Anton-Regular.ttf"
        else:
            path = FONTS / "IBMPlexSansCondensed-Medium.ttf"
        key = (str(path), int(px))
        if key not in cache:
            cache[key] = ImageFont.truetype(str(path), max(4, int(px)))
        return cache[key]

    SL.font = font
    SL._font_cache = cache


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="the round 41 concept scripts folder (from the tag)")
    ap.add_argument("--kits", default=",".join(KITS))
    args = ap.parse_args()
    sys.path.insert(0, args.src)
    import numpy as np
    from PIL import Image, ImageFilter

    import slicelib as SL

    remap_fonts(SL)
    import programs as PR
    import screens10 as S10
    import skins as SK

    S10.select(virus="OOZE", proxy="TURN")  # the round 11 picks the combat mocks use
    ss = 1
    Ro, Ri = SL.R_OUT * ss, SL.R_IN * ss
    gap, bw = 1.6 * ss, 8.5 * ss
    r_out_s = Ro - gap - bw
    r_in_s = Ri + gap + bw * 0.85
    W = int(r_out_s * math.radians(SPAN) + 8 * ss)
    H = int(r_out_s - r_in_s + 4 * ss)
    cw, ch = round(W * SCALE), round(H * SCALE)
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {"frames": FRAMES, "cell": [cw, ch], "tex": [W, H], "scale": SCALE, "span": SPAN, "r_out": SL.R_OUT,
            "r_in": SL.R_IN, "r_out_s": r_out_s, "r_in_s": r_in_s, "kinds": KINDS, "scene": {}}
    for kit in args.kits.split(","):
        screen = Image.new("RGB", (cw * FRAMES, ch * len(KINDS)))
        scene = Image.new("RGBA", (cw * FRAMES, ch * len(KINDS)), (0, 0, 0, 0)) if kit not in ("player",) else None
        has_scene = False
        for row, prog in enumerate(KINDS):
            special = None
            name = prog
            if prog == "SPECIAL":
                if kit == "player":
                    continue
                special = SPECIALS[kit]
                name = "EXPLOIT"
            col = SL.PROGRAMS[name]["col"]
            for f in range(FRAMES):
                t = f / FRAMES
                ctx = SL.Ctx(W, H, t, ss, SPAN, r_out_s, col, kit, name, row + 1)
                ctx.opts = {"glyph_scale": 1.0, "tex_gain": 1.0, "plate": 0.62, "number_scale": 1.0, "icons": True}
                ctx.special = special
                img = PR.texture(ctx).convert("RGB")
                tex = np.asarray(img, np.float32) / 255.0
                g1 = np.asarray(img.filter(ImageFilter.GaussianBlur(5 * ss)), np.float32) / 255.0
                g2 = np.asarray(img.filter(ImageFilter.GaussianBlur(14 * ss)), np.float32) / 255.0
                tex = np.clip(tex + g1 * 0.55 + g2 * 0.35, 0, 1)
                cell = Image.fromarray((tex * 255 + 0.5).astype(np.uint8)).resize((cw, ch), Image.LANCZOS)
                screen.paste(cell, (f * cw, row * ch))
                req = getattr(ctx, "scene_req", None)
                if req is not None and scene is not None:
                    sc_img, yc, cut = req
                    has_scene = True
                    meta["scene"][kit] = {"yc": yc, "cut": (cut / H) if cut is not None else -1.0}
                    scene.paste(sc_img.convert("RGBA").resize((cw, ch), Image.LANCZOS), (f * cw, row * ch))
            print("baked", kit, prog, flush=True)
        screen.save(OUT / f"{kit}_screen.png", optimize=True)
        if scene is not None and has_scene:
            scene.save(OUT / f"{kit}_scene.png", optimize=True)
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
