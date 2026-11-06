"""Dump frames of a GIF into one contact sheet with frame index and duration.
Usage: python gif_frames.py <gif> <out.jpg> <tile_w> <cols> [step]"""
import sys
from PIL import Image, ImageDraw, ImageSequence

def main():
    g, out, tw, cols = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    step = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    im = Image.open(g)
    frames = []
    t = 0
    for i, fr in enumerate(ImageSequence.Iterator(im)):
        d = fr.info.get('duration', 0)
        if i % step == 0:
            f = fr.convert('RGB')
            h = round(f.height * tw / f.width)
            frames.append((i, t, d, f.resize((tw, h), Image.LANCZOS)))
        t += d
    th = frames[0][3].height + 18
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw, rows * th), (16, 16, 22))
    dr = ImageDraw.Draw(sheet)
    for k, (i, t0, d, f) in enumerate(frames):
        x, y = (k % cols) * tw, (k // cols) * th
        sheet.paste(f, (x, y + 18))
        dr.text((x + 4, y + 3), f'#{i} t={t0}ms d={d}', fill=(255, 226, 0))
    sheet.save(out, quality=88)
    print(out, sheet.size, 'frames total', i + 1, 'ms total', t)

if __name__ == '__main__':
    main()
