"""fdiag.py (round 2, C13): render T5 and / or T6 at 25 fps and map the local flash per 120 px tile (60 px at 960), rel10 and WCAG, as
render3.tiles measures it.  CORP=neutral|solace [PULL=1] [knobs of fx3 by env] python fdiag.py t5,t6 [tag]
-> out/fdiag_<corp>_<tag>.json (per clip: worst tile, the per-tile any-1 s map, the swing series and luma of the 8 worst tiles)
   and out/fdiag_<corp>_<tag>_<clip>.png (the any-1 s rel10 count drawn per tile over the frame at the time of the worst swing)."""
import sys, os, json, time
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
T0 = time.time()
import render3 as R3
from fx3lib import *
import fx3 as M

clips = (sys.argv[1] if len(sys.argv) > 1 else 't5,t6').split(',')
tag = sys.argv[2] if len(sys.argv) > 2 else 'x'
FPS = 25
LEN = {'t5': R3.T5_LEN, 't6': R3.T6_LEN}
res = dict(corp=CORP, tag=tag, env={k: v for k, v in os.environ.items() if k in ('BIT_A', 'DARK_KEEP', 'DARK_D0', 'PULL', 'IRIS', 'SAMPLE_PCT')})


def tile_series(frames, cell=60):
    sm = [np.asarray(Image.fromarray(f).resize((960, 540), Image.BOX)) for f in frames]
    G = np.stack([(s.astype(np.float32) * np.array([.2126, .7152, .0722])).sum(-1) / 255.0 for s in sm])
    Y = np.stack([R3.lin_y(s) for s in sm])
    n, h, w = G.shape
    def tl(A): return A[:, :h // cell * cell, :w // cell * cell].reshape(n, h // cell, cell, w // cell, cell).mean((2, 4))
    Gt, Yt = tl(G), tl(Y)
    dG, dY = np.diff(Gt, axis=0), np.diff(Yt, axis=0)
    rel = (np.abs(dG) > 0.10 * np.maximum(Gt[1:], Gt[:-1]).clip(0.02)) * np.sign(dG)
    absw = ((np.abs(dY) >= 0.10) & (np.minimum(Yt[1:], Yt[:-1]) < 0.80)) * np.sign(dY)
    return Gt, rel, absw


for fn in clips:
    n = int(round(LEN[fn] * FPS)) + 1
    times = [round(i / FPS, 4) for i in range(n)]
    fr = [R3.render(fn, t) for t in times]
    Gt, rel, absw = tile_series(fr)
    th, tw = Gt.shape[1:]
    cnt = np.zeros((th, tw), int)
    cnt_w = np.zeros((th, tw), int)
    for i in range(th):
        for j in range(tw):
            s = list(rel[:, i, j])
            cnt[i, j] = R3.pairs(s)
            cnt_w[i, j] = R3.window_max(s, FPS)
    wc = max(R3.window_max(list(absw[:, i, j]), FPS) for i in range(th) for j in range(tw))
    order = np.dstack(np.unravel_index(np.argsort(-cnt_w.ravel(), kind='stable'), cnt_w.shape))[0][:8]
    worst = []
    for (i, j) in order:
        worst.append(dict(x=int(j * 120), y=int(i * 120), any_1s=int(cnt_w[i, j]), swings=''.join({1: '+', -1: '-', 0: '.'}[int(v)] for v in rel[:, i, j]),
                          luma=[round(float(v), 3) for v in Gt[:, i, j]]))
    res[fn] = dict(worst_rel10_any_1s=int(cnt_w.max()), worst_wcag_any_1s=int(wc), tiles_at_or_over_3=int((cnt_w >= 3).sum()),
                   tiles_at_2=int((cnt_w == 2).sum()), map_any_1s=cnt_w.tolist(), worst=worst)
    # picture: the frame at the worst tile's first swing, with the per-tile count
    i0, j0 = order[0]
    k = int(np.nonzero(rel[:, i0, j0])[0][0]) + 1 if np.any(rel[:, i0, j0]) else 0
    im = Image.fromarray(fr[k]).resize((960, 540), Image.BOX)
    d = ImageDraw.Draw(im)
    for i in range(th):
        for j in range(tw):
            c = cnt_w[i, j]
            if c:
                col = {1: (120, 200, 255), 2: (255, 210, 60)}.get(c, (255, 60, 60))
                d.rectangle([j * 60, i * 60, j * 60 + 59, i * 60 + 59], outline=col, width=2 if c < 3 else 4)
                d.text((j * 60 + 4, i * 60 + 3), str(c), fill=col)
    d.text((6, 524), '%s %s %s frame t=%.2f s  worst %d' % (CORP, tag, fn, times[k], cnt_w.max()), fill=(255, 255, 255))
    im.save(HERE + 'out/fdiag_%s_%s_%s.png' % (CORP, tag, fn))
    print(fn, 'worst rel10 any 1 s', int(cnt_w.max()), 'wcag', wc, 'tiles >=3', int((cnt_w >= 3).sum()), 'tiles at 2', int((cnt_w == 2).sum()),
          round(time.time() - T0, 1), flush=True)
    for w_ in worst[:5]:
        print('   x%4d y%4d  %d  %s' % (w_['x'], w_['y'], w_['any_1s'], w_['swings']), flush=True)
    del fr
json.dump(res, open(HERE + 'out/fdiag_%s_%s.json' % (CORP, tag), 'w'), indent=1)
print('done', round(time.time() - T0, 1))
