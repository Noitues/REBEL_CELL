"""ART-9 4B: renders the operative bust sets and packs them into the game's atlases.

Ported from art-pass 9a62cec (tag art-concepts-r43, docs/concepts/round39_portraits/scripts/
render_busts.py): the same headless Blender run of bust_rig.py, here for every class x
VARIANTS rookie seeds x FRAMES at a game size, then one atlas per class:

    assets/portraits/busts_<class>.png   columns = FRAMES, rows = VARIANTS, each CELL px

The layout must match scripts/ui/kit/portrait_bust.gd (VARIANTS, FRAMES, CELL).

    python tools/art_gen/portraits/render_busts.py [--scratch DIR]

Needs Blender 5.2 (BLENDER below) and Pillow. Every random choice in bust_rig.py is seeded,
so a re-run writes the same pictures.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ASSETS = os.path.join(ROOT, "assets", "portraits")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
CLASSES = ["breaker", "wrecker", "ghost", "phantom", "rigger", "overclocker", "botnet", "hivemind"]
# Rookie seeds: variant k of a class is seed SEEDS[k] (variant 0 = the class's own face).
SEEDS = [1, 2, 3, 4]
# Frames (columns): name, mouth, eyes. Order = PortraitBust.Frame.
FRAMES = [("idle", "closed", "open"), ("blink", "closed", "shut"), ("talk", "open", "open"), ("hurt", "grimace", "squint")]
CELL = (240, 266)
# The print's paper (Palette.PAPER_ALT-ish warm stock, as the feed shader's `paper`).
PAPER = np.array([0.83, 0.78, 0.68], dtype=np.float32)


def jobs():
    out = []
    for c in CLASSES:
        for s in SEEDS:
            for name, mouth, eyes in FRAMES:
                out.append(dict(name="%s_%d_%s" % (c, s, name), cls=c, seed=s, mouth=mouth, eyes=eyes))
    return out


def render(scratch):
    os.makedirs(os.path.join(scratch, "busts"), exist_ok=True)
    jf = os.path.join(scratch, "jobs.json")
    with open(jf, "w") as f:
        json.dump({"res": list(CELL), "jobs": jobs()}, f)
    log = os.path.join(scratch, "blender.log")
    with open(log, "w") as lf:
        subprocess.run([BLENDER, "-b", "--factory-startup", "-P", os.path.join(HERE, "bust_rig.py"), "--", jf,
                        os.path.join(scratch, "busts")], stdout=lf, stderr=subprocess.STDOUT, check=False)
    txt = open(log, errors="ignore").read()
    print("rendered", txt.count("RENDERED"), "of", len(jobs()))
    if "Traceback" in txt:
        i = txt.index("Traceback")
        print(txt[i:i + 2000])
        sys.exit(1)


def pack(scratch):
    os.makedirs(ASSETS, exist_ok=True)
    for c in CLASSES:
        sheet = Image.new("RGBA", (CELL[0] * len(FRAMES), CELL[1] * len(SEEDS)), (0, 0, 0, 0))
        for row, s in enumerate(SEEDS):
            for col, (name, _m, _e) in enumerate(FRAMES):
                im = Image.open(os.path.join(scratch, "busts", "%s_%d_%s.png" % (c, s, name))).convert("RGBA")
                sheet.paste(im, (col * CELL[0], row * CELL[1]))
        path = os.path.join(ASSETS, "busts_%s.png" % c)
        # Game-sized: a 256-colour palette (flat toon facets survive it; about a third of the
        # bytes of RGBA).
        sheet.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(path, optimize=True)
        print(path, os.path.getsize(path) // 1024, "KB")
        # The corp's photo print of each rookie (round 38 contexts: dossier, audit polaroid):
        # the idle frame on a flat backdrop, desaturated, warmed, grained. Same maths as the
        # feed shader's print mode (shaders/portrait_feed.gdshader, mode 6).
        col = np.zeros((CELL[1] * len(SEEDS), CELL[0], 3), dtype=np.float32)
        grain = np.random.default_rng(len(c)).random((CELL[1], CELL[0]), dtype=np.float32)
        yy, xx = np.mgrid[0:CELL[1], 0:CELL[0]].astype(np.float32)
        dist = np.sqrt(((xx + 0.5) / CELL[0] - 0.5) ** 2 + ((yy + 0.5) / CELL[1] - 0.5) ** 2)
        vig = np.clip((dist - 0.35) / (0.9 - 0.35), 0, 1)
        vig = vig * vig * (3 - 2 * vig) * 0.35
        for row, s in enumerate(SEEDS):
            im = np.asarray(Image.open(os.path.join(scratch, "busts", "%s_%d_idle.png" % (c, s))).convert("RGBA"), dtype=np.float32) / 255.0
            a = im[..., 3:4]
            p = PAPER * 0.62 * (1 - a) + im[..., :3] * a
            l = (p @ np.array([0.299, 0.587, 0.114], dtype=np.float32))[..., None]
            q = (l + (p - l) * 0.42) * np.array([1.05, 0.98, 0.86], dtype=np.float32)
            q *= (0.92 + grain * 0.12)[..., None]
            q = q * (1 - vig[..., None]) + PAPER * 0.5 * vig[..., None]
            col[row * CELL[1]:(row + 1) * CELL[1]] = q
        pr = Image.fromarray((np.clip(col, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
        ppath = os.path.join(ASSETS, "prints_%s.jpg" % c)
        pr.save(ppath, quality=85, optimize=True)
        print(ppath, os.path.getsize(ppath) // 1024, "KB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", default=os.path.join(os.environ.get("TEMP", HERE), "rebel_cell_busts"))
    ap.add_argument("--pack-only", action="store_true")
    a = ap.parse_args()
    if not a.pack_only:
        render(a.scratch)
    pack(a.scratch)


if __name__ == "__main__":
    main()
