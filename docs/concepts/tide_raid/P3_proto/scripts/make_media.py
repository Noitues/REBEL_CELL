"""Makes the P3 prototype media from a frames folder: MP4, contact strip, side-by-side with the P2 offline video and the P2 plate.

    python make_media.py --frames <dir> --out <prefix> [--ref <mp4>] [--plate <png> --peak N] [--strip 0,30,34,...] [--labels]

Run with D:/rc_scratch/tide_concepts/venv_vid/Scripts/python.exe (imageio-ffmpeg + Pillow). Never from stdin.
"""
import argparse
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FPS = 30


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        print(r.stderr.decode("utf-8", "replace")[-1500:])
        sys.exit(1)


def mp4(frames: Path, out: Path):
    run([FFMPEG, "-y", "-framerate", str(FPS), "-i", str(frames / "f_%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16",
         "-preset", "medium", str(out)])


def strip(frames: Path, out: Path, picks, cols=4, w=640):
    h = w * 9 // 16
    rows = (len(picks) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * h), (8, 6, 20))
    for i, n in enumerate(picks):
        p = frames / ("f_%04d.png" % n)
        if not p.exists():
            continue
        im = Image.open(p).convert("RGB").resize((w, h), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 92, 22), fill=(0, 0, 0))
        d.text((6, 5), "f%d  %.2fs" % (n, n / FPS), fill=(255, 255, 255))
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    sheet.save(out)


def side_video(mine: Path, ref: Path, out: Path):
    run([FFMPEG, "-y", "-i", str(mine), "-i", str(ref), "-filter_complex",
         "[0:v]scale=960:540,setsar=1[a];[1:v]scale=960:540,setsar=1[b];[a][b]hstack=inputs=2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(out)])


def side_plate(frame: Path, plate: Path, out: Path, w=960):
    h = w * 9 // 16
    a = Image.open(frame).convert("RGB").resize((w, h), Image.LANCZOS)
    b = Image.open(plate).convert("RGB").resize((w, h), Image.LANCZOS)
    sheet = Image.new("RGB", (2 * w, h + 26), (8, 6, 20))
    sheet.paste(a, (0, 26))
    sheet.paste(b, (w, 26))
    d = ImageDraw.Draw(sheet)
    d.text((8, 7), "P3 Godot prototype (live city, real shaders): " + frame.name, fill=(255, 255, 255))
    d.text((w + 8, 7), "P2 golden plate (offline Blender comp): " + plate.name, fill=(255, 255, 255))
    sheet.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref")
    ap.add_argument("--plate")
    ap.add_argument("--peak", type=int, default=0)
    ap.add_argument("--strip", default="")
    ap.add_argument("--cols", type=int, default=4)
    a = ap.parse_args()
    frames = Path(a.frames)
    out = Path(a.out)
    n = len(list(frames.glob("f_*.png")))
    mp4(frames, out.with_suffix(".mp4"))
    picks = [int(x) for x in a.strip.split(",") if x] or list(range(0, n, max(1, n // 12)))[:12]
    strip(frames, out.parent / (out.name + "_strip.png"), picks, cols=a.cols)
    if a.ref:
        side_video(out.with_suffix(".mp4"), Path(a.ref), out.parent / (out.name + "_vs_p2.mp4"))
    if a.plate:
        side_plate(frames / ("f_%04d.png" % a.peak), Path(a.plate), out.parent / (out.name + "_vs_plate.png"))
    print("frames", n)


main()
