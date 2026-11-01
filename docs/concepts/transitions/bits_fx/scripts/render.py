# Renders GIFs, key-frame strips, sheet and flash metrics for options A/B/C.  Run: python render.py
import sys, json, importlib, os
from fxlib import *
OUT = os.path.join(HERE, '..')
OPTS = {'A': 'fx_a', 'B': 'fx_b', 'C': 'fx_c'}
NAMES = {'A': 'A  glyph bits + ink keylines', 'B': 'B  pixel blocks into ring cells', 'C': 'C  cut-paper strip peel'}
N5, N6 = 15, 10
T5K = [(0.25, 'K2 0.25 s'), (0.55, 'K3 0.55 s'), (0.85, 'K4 0.85 s'), (1.05, 'K5 1.05 s'), (1.20, 'K6 1.20 s')]
T6K = [(0.0, 'K1 0.00 s'), (0.2, 'K2 0.20 s'), (0.4, 'K3 0.40 s'), (0.6, '0.60 s'), (0.8, 'K4 0.80 s')]
LABF = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 15)

def save_gif(frames, path):
    q = [f.quantize(colors=200, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=80, loop=0, optimize=False, disposal=1)
    return os.path.getsize(path) / 1e6

def luma_series(frames):
    return [luma(np.asarray(f).astype(np.float32)) for f in frames]

def flash_stats(fr):
    L = np.array(luma_series(fr)); d = np.diff(L)
    # general flash: opposing luma change >= 10 % of the screen luminance pair-wise; count sign-alternating big swings
    big = np.abs(d) > 0.10 * np.maximum(L[1:], L[:-1]).clip(0.02)
    return dict(max_abs_delta_luma=float(np.abs(d).max()), max_rel_change=float((np.abs(d) / np.maximum(L[1:], L[:-1]).clip(0.02)).max()),
                swings_over_10pct=int(big.sum()), max_frame_luma=float(L.max()), min_frame_luma=float(L.min()))

def key_tile(arr, label, w=384):
    im = to_pil(arr).resize((w, int(w * 9 / 16)), Image.LANCZOS)
    d = ImageDraw.Draw(im); d.rectangle([0, 0, 118, 21], fill=(12, 10, 22)); d.text((5, 3), label, font=LABF, fill=(242, 246, 255))
    return im

if __name__ == '__main__':
    only = sys.argv[1:] or list(OPTS)
    metrics = {}; tiles = {}
    for k in only:
        m = importlib.import_module(OPTS[k])
        f5 = [to_pil(m.t5(i * 1.2 / (N5 - 1))) for i in range(N5)]
        f6 = [to_pil(m.t6(i * 0.8 / (N6 - 1))) for i in range(N6)]
        s5 = save_gif(f5, os.path.join(OUT, 't5_%s.gif' % k)); s6 = save_gif(f6, os.path.join(OUT, 't6_%s.gif' % k))
        # key-frame strips (5 per transition)
        k5 = [np.asarray(m.t5(t)) for t, _ in T5K]; k6 = [np.asarray(m.t6(t)) for t, _ in T6K]
        t5t = [key_tile(a, 'T5 ' + l) for a, (_, l) in zip(k5, T5K)]
        t6t = [key_tile(a, 'T6 ' + l) for a, (_, l) in zip(k6, T6K)]
        tiles[k] = (t5t, t6t)
        tw, th = t5t[0].size
        strip = Image.new('RGB', (tw * 5 + 6 * 6, (th + 6) * 2 + 40), (12, 10, 22))
        dd = ImageDraw.Draw(strip); dd.text((8, 8), 'Option ' + NAMES[k], font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 20), fill=(150, 255, 70))
        for i, im in enumerate(t5t): strip.paste(im, (6 + i * (tw + 6), 36))
        for i, im in enumerate(t6t): strip.paste(im, (6 + i * (tw + 6), 36 + th + 6))
        strip.save(os.path.join(OUT, 'strip_%s.jpg' % k), quality=88)
        metrics[k] = dict(t5_gif_mb=round(s5, 2), t6_gif_mb=round(s6, 2), t5=flash_stats(f5), t6=flash_stats(f6),
                          t5_frames=N5, t6_frames=N6)
        print(k, metrics[k])
    if len(only) == 3:
        tw, th = tiles['A'][0][0].size
        sheet = Image.new('RGB', (tw * 5 + 6 * 6 + 0, 40 + 3 * (2 * (th + 4) + 30)), (12, 10, 22))
        dd = ImageDraw.Draw(sheet); BF = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 20)
        dd.text((8, 8), 'T5 / T6 bits FX: A glyph bits, B pixel blocks, C cut-paper strips  (same keys, same room, same plate)', font=BF, fill=(242, 246, 255))
        y = 40
        for k in 'ABC':
            dd.text((8, y + 4), 'Option ' + NAMES[k], font=BF, fill=(150, 255, 70)); y += 30
            for row in tiles[k]:
                for i, im in enumerate(row): sheet.paste(im, (6 + i * (tw + 6), y))
                y += th + 4
        sheet.save(os.path.join(OUT, 'sheet.jpg'), quality=88)
        json.dump(metrics, open(os.path.join(OUT, 'metrics.json'), 'w'), indent=1)
