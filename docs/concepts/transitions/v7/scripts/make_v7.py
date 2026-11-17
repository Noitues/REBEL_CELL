"""Transitions v7 (art lane B): contact sheets and animations from tools/b_capture/street_motion_capture.gd frames.

Run: python make_v7.py <capture dir> <out dir>
For each move (node_in, node_out, t2, t4, t4_lost) found in <capture dir>/<move>/f_NNN.png: a contact sheet of 8 frames
evenly spaced over the move (first and last included) with their times, plus the landing screen, written to
<out dir>/<move>_sheet.jpg, and an animated WebP of every frame at the capture rate (<out dir>/<move>.webp).
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

FPS = 30.0
COLS = 4
THUMB_W = 640
PAD = 16
HEAD = 70
LABEL = 34
BG = (12, 13, 18)
INK = (230, 230, 225)
ACID = (200, 255, 60)
DIM = (150, 150, 160)

TITLES = {
    "node_in": ("Node zoom in", "street wide -> the current node, 0.5 s cubic in-out (zr_mo_node_*)"),
    "node_out": ("Node zoom out", "the current node -> street wide, 0.5 s cubic in-out"),
    "t2": ("T2 street to room", "camera only into the combat pose, 1.2 s; other walls come down 0.30-0.90 s; chrome out 0.15-0.35 s"),
    "t4": ("T4 won: back to the street", "the T2 move reversed, 0.8 s; the walls redissolve (ease-out); chrome back last 0.22 s"),
    "t4_lost": ("T4 lost: back, then the lost wall goes up", "0.8 s back while the others redissolve; the lost room's wall rises 0.45 s; 0.3 s beat"),
}


def font(size):
    for f in ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def frames_of(d):
    if not os.path.isdir(d):
        return []
    return sorted(os.path.join(d, f) for f in os.listdir(d) if f.startswith("f_") and f.endswith(".png"))


def pick(n, k):
    if n <= k:
        return list(range(n))
    return [round(i * (n - 1) / (k - 1)) for i in range(k)]


def sheet(move, frames, end_png, out):
    idx = pick(len(frames), 8)
    tiles = [(frames[i], "%.2f s" % (i / FPS)) for i in idx]
    if end_png and os.path.exists(end_png):
        tiles.append((end_png, "landed: the end screen"))
    im0 = Image.open(tiles[0][0])
    th = int(THUMB_W * im0.height / im0.width)
    rows = (len(tiles) + COLS - 1) // COLS
    w = PAD + COLS * (THUMB_W + PAD)
    h = HEAD + rows * (th + LABEL + PAD) + PAD
    sh = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(sh)
    title, sub = TITLES.get(move, (move, ""))
    d.text((PAD, 10), "v7 " + title + "  (Godot capture, real game flow)", font=font(30), fill=ACID)
    d.text((PAD, 46), sub, font=font(17), fill=DIM)
    for i, (p, lab) in enumerate(tiles):
        r, c = divmod(i, COLS)
        x = PAD + c * (THUMB_W + PAD)
        y = HEAD + r * (th + LABEL + PAD)
        t = Image.open(p).convert("RGB").resize((THUMB_W, th), Image.LANCZOS)
        sh.paste(t, (x, y))
        d.text((x, y + th + 6), lab, font=font(18), fill=INK)
    sh.save(out, quality=88)


def anim(frames, out):
    ims = [Image.open(p).convert("RGB").resize((960, int(960 * Image.open(p).height / Image.open(p).width)), Image.LANCZOS) for p in frames]
    if ims:
        ims[0].save(out, save_all=True, append_images=ims[1:], duration=int(1000 / FPS), loop=0, quality=80)


def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for move in TITLES:
        fr = frames_of(os.path.join(src, move))
        if not fr:
            print("no frames for", move)
            continue
        sheet(move, fr, os.path.join(src, move + "_end.png"), os.path.join(out, move + "_sheet.jpg"))
        anim(fr, os.path.join(out, move + ".webp"))
        print(move, len(fr), "frames")


if __name__ == "__main__":
    main()
