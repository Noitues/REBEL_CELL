"""Write a 2x2 strip of chosen GIF frames to scratch/ for checking: python scripts/inspect_gif.py file.gif 0 21 31 40"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def main(path, idx):
    im = Image.open(path)
    frames = []
    for i in range(im.n_frames):
        im.seek(i)
        frames.append(im.convert('RGB'))
    w, h = frames[0].size
    out = Image.new('RGB', (w * 2, h * ((len(idx) + 1) // 2)))
    for k, i in enumerate(idx):
        out.paste(frames[i], ((k % 2) * w, (k // 2) * h))
    p = os.path.join(ROOT, 'scratch', 'inspect.png')
    out.save(p)
    print(p, im.n_frames, 'frames', im.info.get('duration'), 'ms', round(os.path.getsize(path) / 1e6, 2), 'MB')


if __name__ == '__main__':
    main(sys.argv[1], [int(v) for v in sys.argv[2:]])
