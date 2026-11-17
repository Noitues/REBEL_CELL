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

K = 12
PITCH = {}
TITLES = {
    "t1_jack_in": ("T1 jack-in on the real street", "the dive now in the street night grade (the dress builds in); REVEAL: rooms light L->R, fronts to bits; MARK; ZOOM"),
    "t2_t3": ("T2 + T3 street to fight", "camera into the combat pose (warm slot room), walls down; then bits draw the ring from 12 and the board comes up"),
    "fight_won": ("Fight end, won", "only the wheel breaks to bits into the room; the room turns our colour; the reward page blooms from the room"),
    "t4_won": ("T4 won", "the reward page back into the room, bits to the purse and the deck; the move back; walls redissolve"),
    "fight_lost": ("Fight end, lost", "the wheel to bits; the lost flicker (3 Hz cap); the loss page rises from the bottom as bits and types on"),
    "t5_lost": ("T5 lost: wall up, then the 6.82 s jack-out", "held on the lost room, wall up; street side backwards: rooms go dark R->L, fronts back to bits; the dive back off the dress, band free; CRT"),
}


def font(size):
    for f in ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def frames_of(d):
    if not os.path.isdir(d):
        return []
    return sorted(os.path.join(d, f) for f in os.listdir(d) if f.startswith("f_") and (f.endswith(".png") or f.endswith(".jpg")))


def pick(n, k):
    if n <= k:
        return list(range(n))
    return [round(i * (n - 1) / (k - 1)) for i in range(k)]


def sheet(move, frames, end_png, out):
    idx = pick(len(frames), K)
    tiles = [(frames[i], "%.2f s" % (i / FPS) + PITCH.get(i, "")) for i in idx]
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
    d.text((PAD, 10), "v7 b3 " + title + "  (Godot capture, real game flow)", font=font(30), fill=ACID)
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
    ims = [Image.open(p).convert("RGB").resize((800, 450), Image.LANCZOS) for p in frames]
    if ims:
        ims[0].save(out, save_all=True, append_images=ims[1:], duration=int(1000 / FPS), loop=0, quality=70, method=4)


def load_pitch(path):
    PITCH.clear()
    if not os.path.exists(path):
        return
    for ln in open(path, encoding="utf-8").read().splitlines()[1:]:
        c = ln.split(",")
        if len(c) > 2 and c[2]:
            PITCH[int(c[0])] = "  pitch %.1f  %s" % (float(c[2]), c[6] if len(c) > 6 else "")


def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for move in TITLES:
        fr = frames_of(os.path.join(src, move))
        if not fr:
            print("no frames for", move)
            continue
        load_pitch(os.path.join(src, move + ".csv"))
        sheet(move, fr, os.path.join(src, move + "_end.png"), os.path.join(out, move + "_b3_sheet.jpg"))
        anim(fr, os.path.join(out, move + "_b3.webp"))
        print(move, len(fr), "frames")


if __name__ == "__main__":
    main()
