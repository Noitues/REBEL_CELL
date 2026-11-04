"""bitstats.py: the colours the bits take from their sources (per stream: median L*, median C*ab, share with C*ab >= 20), and a swatch
sheet out/bits_<corp>.png (one row per stream, each bit's source pixel above its clamped colour) for a look at 1x."""
import sys, os, json
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fx3lib import *
import fx3 as M


def stats(raw, col):
    lr = lab(np.array(raw)); lc = lab(np.array(col))
    C = np.hypot(lc[:, 1], lc[:, 2])
    return dict(n=len(col), src_L_median=round(float(np.median(lr[:, 0])), 1), bit_L_median=round(float(np.median(lc[:, 0])), 1),
                bit_L_min=round(float(lc[:, 0].min()), 1), bit_L_max=round(float(lc[:, 0].max()), 1),
                bit_C_median=round(float(np.median(C)), 1), share_C20=round(float((C >= 20).mean()), 2),
                hue_dE_src_vs_bit_max=round(float(np.max(np.hypot(lr[:, 1] - lc[:, 1], lr[:, 2] - lc[:, 2]))), 2))


rows = [('T5 ring NOW', M.G5[0]), ('T5 ring +1', M.G5[1]), ('T5 ring +2', M.G5[2]), ('T5 frame band', M.G5[3]),
        ('T6 spinner', M.G6[4]), ('tickets', M.TK)] + [('card %s' % M.META['hand'][i] if i < len(M.META['hand']) else 'card %d' % i, M.CG[i]) for i in range(NCARD)]
out = {}
S = Image.new('RGB', (1500, 40 * len(rows) + 10), (12, 10, 22))
d = ImageDraw.Draw(S)
for k, (name, G) in enumerate(rows):
    out[name] = stats(G['raw'], G['col'])
    if 'bc' in G:
        out[name]['keyline_rgb'] = [int(round(v)) for v in G['bc']]
    y = 6 + 40 * k
    d.text((6, y + 10), name, fill=(230, 230, 236))
    for j, (r_, c_) in enumerate(zip(G['raw'][:96], G['col'][:96])):
        x = 150 + j * 14
        d.rectangle([x, y, x + 12, y + 14], fill=tuple(int(v) for v in r_))
        d.rectangle([x, y + 16, x + 12, y + 32], fill=tuple(int(v) for v in c_))
S.save(HERE + 'out/bits_%s.png' % CORP)
json.dump(out, open(HERE + 'out/bits_%s.json' % CORP, 'w'), indent=1)
for k, v in out.items():
    print('%-16s' % k, v)
