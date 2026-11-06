"""Render t5/t6 GIFs, key strips and flash metrics for the recoloured option A.
CORP=neutral|solace python render2.py [fps_mult]
 -> out/<corp>/t5_A.gif, t6_A.gif, strip_t5.jpg, strip_t6.jpg, keys (png per key), metrics_<corp>.json"""
import sys, json, os
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fx2lib import *
import fx_a2 as M
OUT = HERE + 'out/%s/' % CORP
os.makedirs(OUT + 'keys', exist_ok=True)
N5, N6 = 15, 10                     # 12.5 fps, as bits_fx/metrics.json
T5K = [(0.0, 'K1 0.00 s'), (0.38, 'wheel in 0.38 s'), (0.55, 'K3 0.55 s'), (0.70, '0.70 s'), (0.85, 'K4 0.85 s'), (1.00, 'lock 1.00 s'), (1.12, 'K5 1.12 s'), (1.20, 'K6 1.20 s')]
T6K = [(0.0, 'K1 0.00 s'), (0.08, '0.08 s'), (0.2, 'K2 0.20 s'), (0.3, '0.30 s'), (0.4, 'K3 0.40 s'), (0.5, '0.50 s'), (0.6, '0.60 s'), (0.8, 'end 0.80 s')]
LABF = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 15)


def save_gif(frames, path):
    q = [f.quantize(colors=200, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=int(round(1000 * 1.2 / (N5 - 1))) if 't5' in path else int(round(1000 * 0.8 / (N6 - 1))), loop=0, optimize=False, disposal=1)
    return os.path.getsize(path) / 1e6


def flash_stats(fr):
    """same method as bits_fx/metrics.json: mean frame luma, frame-to-frame change, swings over 10 % of the brighter frame"""
    L = np.array([luma(np.asarray(f).astype(np.float32)) for f in fr]); d = np.diff(L)
    big = np.abs(d) > 0.10 * np.maximum(L[1:], L[:-1]).clip(0.02)
    # opposing pairs of big swings = flashes (a flash is a rise and a fall)
    sgn = np.sign(d) * big
    nz = sgn[sgn != 0]
    flashes = int(np.sum(nz[1:] != nz[:-1])) // 2 + (1 if len(nz) > 1 and np.sum(nz[1:] != nz[:-1]) % 2 else 0) if len(nz) > 1 else 0
    return dict(max_abs_delta_luma=float(np.abs(d).max()), max_rel_change=float((np.abs(d) / np.maximum(L[1:], L[:-1]).clip(0.02)).max()),
                swings_over_10pct=int(big.sum()), flash_pairs=flashes, max_frame_luma=float(L.max()), min_frame_luma=float(L.min()),
                luma=[round(float(x), 4) for x in L])


def local_flash(fr, cell=60):
    """stricter local check: per 60 px tile (about 10 degrees of view at 960 px), count opposing luma swings over 10 % of the tile luma"""
    A = np.stack([(np.asarray(f).astype(np.float32) * np.array([.2126, .7152, .0722])).sum(-1) / 255.0 for f in fr])
    n, h, w = A.shape
    T = A[:, :h // cell * cell, :w // cell * cell].reshape(n, h // cell, cell, w // cell, cell).mean((2, 4))
    d = np.diff(T, axis=0)
    big = np.abs(d) > 0.10 * np.maximum(T[1:], T[:-1]).clip(0.02)
    s = np.sign(d) * big
    worst = 0
    for i in range(s.shape[1]):
        for j in range(s.shape[2]):
            nz = s[:, i, j][s[:, i, j] != 0]
            rev = int(np.sum(nz[1:] != nz[:-1])) if len(nz) > 1 else 0
            worst = max(worst, (rev + 1) // 2)
    return dict(tile_px=cell, worst_tile_flash_pairs=worst)


def tile(arr, label, w=384):
    im = to_pil(arr).resize((w, int(w * 9 / 16)), Image.LANCZOS)
    d = ImageDraw.Draw(im); tw = d.textlength(label, font=LABF) + 10
    d.rectangle([0, 0, tw, 21], fill=(12, 10, 22)); d.text((5, 3), label, font=LABF, fill=(242, 246, 255))
    return im


def strip(arrs, labels, title, path):
    ts = [tile(a, l) for a, l in zip(arrs, labels)]
    tw, th = ts[0].size
    cols = 4
    rows = (len(ts) + cols - 1) // cols
    S = Image.new('RGB', (tw * cols + 6 * (cols + 1), 40 + rows * (th + 6)), (12, 10, 22))
    d = ImageDraw.Draw(S); d.text((8, 8), title, font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 20), fill=(255, 61, 168))
    for i, im in enumerate(ts):
        r, c = divmod(i, cols)
        S.paste(im, (6 + c * (tw + 6), 36 + r * (th + 6)))
    S.save(path, quality=90)


if __name__ == '__main__':
    f5 = [to_pil(M.t5(i * 1.2 / (N5 - 1))) for i in range(N5)]
    f6 = [to_pil(M.t6(i * 0.8 / (N6 - 1))) for i in range(N6)]
    s5 = save_gif(f5, OUT + 't5_A.gif'); s6 = save_gif(f6, OUT + 't6_A.gif')
    # 25 fps check frames (stricter sampling of the same motion; not saved as GIF)
    g5 = [to_pil(M.t5(i * 1.2 / 30)) for i in range(31)]
    g6 = [to_pil(M.t6(i * 0.8 / 20)) for i in range(21)]
    k5 = [M.t5(t) for t, _ in T5K]; k6 = [M.t6(t) for t, _ in T6K]
    for (t, l), a in zip(T5K, k5): to_pil(a).save(OUT + 'keys/t5_%03d.png' % int(round(t * 100)))
    for (t, l), a in zip(T6K, k6): to_pil(a).save(OUT + 'keys/t6_%03d.png' % int(round(t * 100)))
    nm = {'neutral': 'neutral skin', 'solace': 'Solace skin'}[CORP]
    strip(k5, ['T5 ' + l for _, l in T5K], 'T5 room to combat, option A recoloured on the final locked board (%s)' % nm, OUT + 'strip_t5.jpg')
    strip(k6, ['T6 ' + l for _, l in T6K], 'T6 combat to netrun (win path), option A recoloured on the final locked board (%s)' % nm, OUT + 'strip_t6.jpg')
    end5 = float(np.abs(np.asarray(f5[-1]).astype(int) - np.clip(PLATE, 0, 255).astype(np.uint8).astype(int)).max())
    end6 = float(np.abs(np.asarray(f6[-1]).astype(int) - np.clip(BARE, 0, 255).astype(np.uint8).astype(int)).max())
    m = dict(corp=CORP, t5_gif_mb=round(s5, 2), t6_gif_mb=round(s6, 2), t5_frames=N5, t6_frames=N6, fps=12.5,
             t5=flash_stats(f5), t6=flash_stats(f6), t5_25fps=flash_stats(g5), t6_25fps=flash_stats(g6),
             t5_local_25fps=local_flash(g5), t6_local_25fps=local_flash(g6),
             t5_last_frame_vs_plate_maxdiff=end5, t6_last_frame_vs_bare_room_maxdiff=end6)
    json.dump(m, open(OUT + 'metrics_%s.json' % CORP, 'w'), indent=1)
    print(json.dumps({k: v for k, v in m.items() if not isinstance(v, dict)}, indent=0))
    for k in ('t5', 't6', 't5_25fps', 't6_25fps'):
        print(k, {a: b for a, b in m[k].items() if a != 'luma'})
    print(m['t5_local_25fps'], m['t6_local_25fps'])
