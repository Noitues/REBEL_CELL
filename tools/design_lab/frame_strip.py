"""Frame strip for motion review (ANIMATION_HANDOFF 5-6): montages 6-10 Movie Maker frames
into one PNG, each labelled with its time in ms from the start of the motion.

    python tools/design_lab/frame_strip.py <frames_dir> <out.png> [--start 6] [--count 8]
        [--step 1] [--fps 30] [--crop x,y,w,h] [--scale 0.5] [--cols 4] [--title TEXT]

<frames_dir> holds the numbered PNGs written by `--write-movie <dir>/f.png` (f00000000.png,
f00000001.png, ...). --start is the frame the motion starts on (the motion lab's
DEMO_START_FRAME, printed as "motion_lab: <id> starts on frame N"); frames are picked from
there every --step frames. --crop cuts a region (1280x720 coordinates) before scaling.
Needs Pillow. Run it as a file (never `python -`).
"""
import argparse
import glob
import os
import sys

from PIL import Image, ImageDraw, ImageFont

LABEL_H = 26
TITLE_H = 30
GAP = 6
BG = (16, 12, 28)
INK = (255, 61, 168)
TEXT = (235, 235, 225)


def _font(size):
    for name in ("consola.ttf", "DejaVuSansMono.ttf", "cour.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("frames_dir")
    ap.add_argument("out")
    ap.add_argument("--start", type=int, default=6)
    ap.add_argument("--count", type=int, default=8)
    ap.add_argument("--step", type=int, default=1)
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--crop", default="")
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--title", default="")
    a = ap.parse_args()

    files = sorted(glob.glob(os.path.join(a.frames_dir, "*.png")))
    if not files:
        sys.exit("no PNG frames in %s" % a.frames_dir)
    picks = []
    for k in range(a.count):
        i = a.start + k * a.step
        if i >= len(files):
            break
        picks.append(i)
    if not picks:
        sys.exit("--start %d is past the last frame (%d frames)" % (a.start, len(files)))

    shots = []
    for i in picks:
        img = Image.open(files[i]).convert("RGB")
        if a.crop:
            x, y, w, h = (int(v) for v in a.crop.split(","))
            img = img.crop((x, y, x + w, y + h))
        if a.scale != 1.0:
            img = img.resize((max(1, int(img.width * a.scale)), max(1, int(img.height * a.scale))), Image.LANCZOS)
        shots.append((i, img))

    w, h = shots[0][1].size
    cols = max(1, min(a.cols, len(shots)))
    rows = (len(shots) + cols - 1) // cols
    top = TITLE_H if a.title else 0
    sheet = Image.new("RGB", (cols * (w + GAP) + GAP, top + rows * (h + LABEL_H + GAP) + GAP), BG)
    draw = ImageDraw.Draw(sheet)
    font = _font(16)
    if a.title:
        draw.text((GAP + 2, 6), a.title, fill=TEXT, font=_font(18))
    for n, (i, img) in enumerate(shots):
        cx = GAP + (n % cols) * (w + GAP)
        cy = top + GAP + (n // cols) * (h + LABEL_H + GAP)
        sheet.paste(img, (cx, cy + LABEL_H))
        ms = round((i - a.start) * 1000.0 / a.fps)
        draw.text((cx + 4, cy + 4), "%+d ms  (f%d)" % (ms, i), fill=INK, font=font)
    sheet.save(a.out)
    print("wrote %s: %d frames, %dx%d" % (a.out, len(shots), sheet.width, sheet.height))


if __name__ == "__main__":
    main()
