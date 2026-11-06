"""gif_try.py: palette options for resolve_beat.gif, measured: mean and p95 dE76 (CIE Lab) of the quantized 640 px frame against the
LANCZOS-resized source frame, over every 10th frame, and the file size of the whole GIF (written to work/gif_try_<k>.gif, not published)"""
import sys, os, glob
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from mp_lib import ME
sys.path.insert(1, ME + 'cdhl_snap')
import fxk_lib as K

fs = sorted(glob.glob(ME + 'work/beat/full_[0-9]*.npz'))
rgb = np.concatenate([np.load(f)['rgb'] for f in fs])
w, h = 640, 360
src = [Image.fromarray(rgb[i]).resize((w, h), Image.LANCZOS) for i in range(0, len(rgb), 2)]


def lab(a):
    return K.RT.lab(np.asarray(a, np.float64))


def de(a, b):
    la, lb = lab(a), lab(b)
    d = np.sqrt(((la - lb) ** 2).sum(-1))
    return float(d.mean()), float(np.percentile(d, 95))


def build(kind):
    if kind == 'old':
        pal = Image.fromarray(np.concatenate([np.asarray(src[i]) for i in range(0, len(src), max(1, len(src) // 8))], 0)).quantize(colors=255, method=Image.Quantize.MEDIANCUT)
        q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in src]
    elif kind == 'mc32':
        pal = Image.fromarray(np.concatenate([np.asarray(src[i]) for i in range(0, len(src), max(1, len(src) // 32))], 0)).quantize(colors=256, method=Image.Quantize.MEDIANCUT, kmeans=4)
        q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in src]
    elif kind == 'mc32fs':
        pal = Image.fromarray(np.concatenate([np.asarray(src[i]) for i in range(0, len(src), max(1, len(src) // 32))], 0)).quantize(colors=256, method=Image.Quantize.MEDIANCUT, kmeans=4)
        q = [f.quantize(palette=pal, dither=Image.Dither.FLOYDSTEINBERG) for f in src]
    elif kind == 'oct32fs':
        pal = Image.fromarray(np.concatenate([np.asarray(src[i]) for i in range(0, len(src), max(1, len(src) // 32))], 0)).quantize(colors=256, method=Image.Quantize.FASTOCTREE)
        q = [f.quantize(palette=pal, dither=Image.Dither.FLOYDSTEINBERG) for f in src]
    return q


for kind in sys.argv[1:]:
    q = build(kind)
    errs = [de(np.asarray(src[i]), np.asarray(q[i].convert('RGB'))) for i in range(0, len(src), 10)]
    fp = ME + 'work/gif_try_%s.gif' % kind
    q[0].save(fp, save_all=True, append_images=q[1:], duration=33, loop=0, optimize=True, disposal=1)
    print(kind, 'mean dE %.2f' % np.mean([e[0] for e in errs]), 'p95 dE %.2f' % np.mean([e[1] for e in errs]), 'bytes', os.path.getsize(fp), flush=True)
