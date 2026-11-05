"""verify_pub.py (round 2): measure the transitions as they are published, not as the code means them.
Decodes the GIFs (published neutral t5_A.gif / t6_A.gif; the Solace GIFs from out/solace/, which stay in scratch), expands the stored
frames to the 12.5 fps timeline by their durations, and measures CIE L* (frame mean of relative luminance), the local flash on 60 px tiles
of the 960 px GIF (= 120 px at 1080p), rel10 and WCAG, in any 1 s (13 frames at 12.5 fps), and the whole-frame flash.  T5 frame 0: K1 room
values (frame mean, the reviewer's room box 1200-1800 x 450-800 at 1080p = 600-900 x 225-400 at 960: mean and p95).  End frames against
the published plate (or the street) reduced to 960 px.  Also the strips: size, and the L* of K1 in the strip tile.
python verify_pub.py  -> out/verify_pub.json"""
import sys, os, json
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from lstar import lum, Lstar_y


class R3:
    """render3.pairs / window_max (copied, so this check does not load the layers)"""
    @staticmethod
    def pairs(sig):
        nz = [s for s in sig if s != 0]
        rev = sum(1 for i in range(1, len(nz)) if nz[i] != nz[i - 1])
        return (rev + 1) // 2 if nz else 0

    @staticmethod
    def window_max(sig, n):
        best = 0
        for i in range(max(1, len(sig) - n + 1)):
            best = max(best, R3.pairs(sig[i:i + n]))
        return best

DST = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/transitions/'
WK = 'D:/rc_scratch/combat_redesign/locked/round2/transitions/'
FIN = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'


def frames(path):
    im = Image.open(path)
    out = []
    i = 0
    while True:
        try:
            im.seek(i)
        except EOFError:
            break
        d = im.info.get('duration', 80)
        f = np.asarray(im.convert('RGB')).copy()
        out += [f] * max(1, int(round(d / 80.0)))
        i += 1
    return out, i


def tile_flash(fr, cell=60, n_win=13):
    G = np.stack([(f.astype(np.float32) * np.array([.2126, .7152, .0722])).sum(-1) / 255.0 for f in fr])
    Y = np.stack([lum(f) for f in fr])
    n, h, w = G.shape
    def tl(A): return A[:, :h // cell * cell, :w // cell * cell].reshape(n, h // cell, cell, w // cell, cell).mean((2, 4))
    Gt, Yt = tl(G), tl(Y)
    dG, dY = np.diff(Gt, axis=0), np.diff(Yt, axis=0)
    rel = (np.abs(dG) > 0.10 * np.maximum(Gt[1:], Gt[:-1]).clip(0.02)) * np.sign(dG)
    absw = ((np.abs(dY) >= 0.10) & (np.minimum(Yt[1:], Yt[:-1]) < 0.80)) * np.sign(dY)
    res = {}
    for nm, S in (('rel10', rel), ('wcag_abs', absw)):
        best, where = 0, None
        for i in range(S.shape[1]):
            for j in range(S.shape[2]):
                v = R3.window_max(list(S[:, i, j]), n_win)
                if v > best:
                    best, where = v, [j * 120, i * 120]
        res[nm] = dict(worst_tile_any_1s=best, at_1080=where)
    Yw = Y.mean((1, 2)); Gw = G.mean((1, 2))
    dGw = np.diff(Gw); dYw = np.diff(Yw)
    relw = (np.abs(dGw) > 0.10 * np.maximum(Gw[1:], Gw[:-1]).clip(0.02)) * np.sign(dGw)
    absww = ((np.abs(dYw) >= 0.10) & (np.minimum(Yw[1:], Yw[:-1]) < 0.80)) * np.sign(dYw)
    res['whole_frame'] = dict(rel10=R3.pairs(list(relw)), wcag_abs=R3.pairs(list(absww)))
    res['frame_mean_Lstar'] = [round(float(Lstar_y(y)), 1) for y in Yw]
    return res


def box(f, x0, y0, x1, y1):
    y = lum(f[y0:y1, x0:x1])
    return round(float(Lstar_y(y.mean())), 1), round(float(Lstar_y(np.percentile(y, 95))), 1)


if __name__ == '__main__':
    out = {}
    plates = {'neutral': FIN + 'p1_decide.png', 'solace': FIN + 'p1_decide_solace.png'}
    for corp, base in (('neutral', DST), ('solace', WK + 'out/solace/')):
        pl = np.asarray(Image.open(plates[corp]).convert('RGB').resize((960, 540), Image.BOX)).astype(int)
        r = {}
        for fn in ('t5', 't6'):
            p = base + '%s_A.gif' % fn
            fr, stored = frames(p)
            m = tile_flash(fr)
            m.update(file=p, mb=round(os.path.getsize(p) / 1e6, 2), stored_frames=stored, timeline_frames=len(fr))
            f0, fl = fr[0].astype(int), fr[-1].astype(int)
            if fn == 't5':
                mean0 = round(float(Lstar_y(lum(fr[0]).mean())), 1)
                bm, bp = box(fr[0], 600, 225, 900, 400)
                m['k1'] = dict(frame_mean_Lstar=mean0, room_box_mean_Lstar=bm, room_box_p95_Lstar=bp)
                m['last_vs_plate_960_maxdiff'] = int(np.abs(fl - pl).max())
                m['last_vs_plate_960_meandiff'] = round(float(np.abs(fl - pl).mean()), 2)
            else:
                m['first_vs_plate_960_maxdiff'] = int(np.abs(f0 - pl).max())
                m['first_vs_plate_960_meandiff'] = round(float(np.abs(f0 - pl).mean()), 2)
                m['last_frame_mean_Lstar'] = round(float(Lstar_y(lum(fr[-1]).mean())), 1)
            r[fn] = m
            print(corp, fn, {k: v for k, v in m.items() if k != 'frame_mean_Lstar'}, flush=True)
        out[corp] = r
    out['files'] = {f: round(os.path.getsize(DST + f) / 1e6, 2) for f in sorted(os.listdir(DST)) if os.path.isfile(DST + f)}
    json.dump(out, open(WK + 'out/verify_pub.json', 'w'), indent=1)
    print('files', out['files'])
    if len(sys.argv) > 1 and sys.argv[1] == 'merge':
        mj = json.load(open(DST + 'metrics.json'))
        mj['published_check'] = out
        json.dump(mj, open(DST + 'metrics.json', 'w'), indent=1)
        print('merged into', DST + 'metrics.json')
