"""bitstats.py (round 2; first written for the rebuild): the colours the bits take from their sources, per stream, over the bits that are
drawn (round 2 thins the far-side bits, fx3.far_keep), and a swatch sheet out/bits_<corp>.png (one row per stream: each bit's source pixel
above its drawn colour) for a look at 1x.
Review 3.12 re-measure: each drawn bit colour (the glyph's core pixel as the Overlay composes it at alpha 1, rounded to 8 bit) against the
colour of the board pixel it becomes, read on the PUBLISHED plate (locked/final/p1_decide[_solace].png) at the bit's point the same way the
source is read (90th percentile of C*ab over a 9 px disc), with the layers that sit above the source on the plate masked out.
Reports dE76 hue (a*, b*) and dE76 full (the L* clamp 55-80 is in the full value)."""
import sys, os, json
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fx3lib import *
import fx3 as M

A_ = {k: LY[k][..., 3] for k in LY if isinstance(LY[k], np.ndarray) and LY[k].ndim == 3 and LY[k].shape[2] == 4}
ZERO = np.zeros((H, W), np.float32)


def above(names):
    a = ZERO.copy()
    for k in names:
        a = np.maximum(a, A_.get(k, ZERO))
    return a


CARDS_ALL = ['card%d' % i for i in range(NCARD)]
UI = ['hud', 'you', 'name', 'send']
MASKS = {
    'ring': (A_['base'] > 0) & (above(['tower', 'guns'] + UI + CARDS_ALL) < 0.5 * 255),
    'core': (A_['tower'] > 0.5 * 255) & (above(['guns'] + UI + CARDS_ALL) < 0.5 * 255),
    'tick': (A_['tickets'] > 0.9 * 255) & (above(['enemy3'] + UI) < 0.5 * 255),
}


def plate_sample(x, y, mask):
    """fx3lib.sample on the published plate with a boolean mask (the source's own pixels that the plate shows)"""
    return sample(PLATE, x, y, alpha=mask.astype(np.float32) * 255.0)[0]


def drawn(col):
    """the glyph core pixel as composed at alpha 1 (Overlay.put: base * (1 - m) + col * m, m = 1), as the 8 bit frame stores it"""
    return tuple(float(np.clip(np.floor(c + 0.5), 0, 255)) for c in col)


def stats(raw, col, plate=None):
    lr = lab(np.array(raw)); lc = lab(np.array(col))
    C = np.hypot(lc[:, 1], lc[:, 2])
    o = dict(n=len(col), src_L_median=round(float(np.median(lr[:, 0])), 1), bit_L_median=round(float(np.median(lc[:, 0])), 1),
             bit_L_min=round(float(lc[:, 0].min()), 1), bit_L_max=round(float(lc[:, 0].max()), 1),
             bit_C_median=round(float(np.median(C)), 1), share_C20=round(float((C >= 20).mean()), 2),
             hue_dE_src_vs_bit_max=round(float(np.max(np.hypot(lr[:, 1] - lc[:, 1], lr[:, 2] - lc[:, 2]))), 2))
    if plate is not None:
        lp = lab(np.array(plate)); ld = lab(np.array([drawn(c) for c in col]))
        hue = np.hypot(lp[:, 1] - ld[:, 1], lp[:, 2] - ld[:, 2])
        full = np.sqrt(((lp - ld) ** 2).sum(-1))
        o.update(plate_src_L_median=round(float(np.median(lp[:, 0])), 1), plate_src_C_median=round(float(np.median(np.hypot(lp[:, 1], lp[:, 2]))), 1),
                 drawn_vs_plate_hue_dE_median=round(float(np.median(hue)), 2), drawn_vs_plate_hue_dE_p90=round(float(np.percentile(hue, 90)), 2),
                 drawn_vs_plate_hue_dE_max=round(float(hue.max()), 2), drawn_vs_plate_full_dE_median=round(float(np.median(full)), 2),
                 share_hue_dE_le_3=round(float((hue <= 3.0).mean()), 2))
    return o


def kept(G, pts_key=('gx', 'gy')):
    k = np.nonzero(G['keep'])[0] if 'keep' in G else np.arange(len(G['col']))
    return k


rows = []
for nm, G, mk in (('T5 ring NOW', M.G5[0], 'ring'), ('T5 ring +1', M.G5[1], 'ring'), ('T5 ring +2', M.G5[2], 'ring'), ('T5 frame band', M.G5[3], 'ring'),
                  ('T6 ring NOW', M.G6[0], 'ring'), ('T6 ring +1', M.G6[1], 'ring'), ('T6 ring +2', M.G6[2], 'ring'), ('T6 frame band', M.G6[3], 'ring'),
                  ('T6 spinner', M.G6[4], 'core'), ('tickets', M.TK, 'tick')):
    k = kept(G)
    pts = [(float(G['gx'][i]), float(G['gy'][i])) for i in k]
    rows.append((nm, [G['raw'][i] for i in k], [G['col'][i] for i in k], [plate_sample(x, y, MASKS[mk]) for x, y in pts], G, len(G['col'])))
for i in range(NCARD):
    C_ = M.CG[i]
    m = (A_['card%d' % i] > 0.97 * 255) & (above(CARDS_ALL[i + 1:] + ['name', 'send']) < 0.5 * 255)
    nm = 'card %s' % M.META['hand'][i] if i < len(M.META['hand']) else 'card %d' % i
    rows.append((nm, C_['raw'], C_['col'], [plate_sample(x, y, m) for x, y in C_['pts']], C_, len(C_['col'])))
out = {}
S = Image.new('RGB', (1500, 40 * len(rows) + 10), (12, 10, 22))
d = ImageDraw.Draw(S)
for k, (name, raw, col, plate, G, n_all) in enumerate(rows):
    out[name] = stats(raw, col, plate)
    out[name]['n_designed'] = n_all
    if 'bc' in G:
        out[name]['keyline_rgb'] = [int(round(v)) for v in G['bc']]
    y = 6 + 40 * k
    d.text((6, y + 10), name, fill=(230, 230, 236))
    for j, (r_, c_) in enumerate(zip(plate[:96], col[:96])):
        x = 150 + j * 14
        d.rectangle([x, y, x + 12, y + 14], fill=tuple(int(v) for v in r_))
        d.rectangle([x, y + 16, x + 12, y + 32], fill=tuple(int(v) for v in drawn(c_)))
S.save(HERE + 'out/bits_%s.png' % CORP)
json.dump(out, open(HERE + 'out/bits_%s.json' % CORP, 'w'), indent=1)
for k, v in out.items():
    print('%-16s' % k, v)
