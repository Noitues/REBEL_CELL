"""share_bases.py: the stock plates are rendered once and shared between the two effect sets (one generator render, one source):
  fx_cdhl base_neutral_p1 / base_neutral_p3  ->  fx_mpst bases neutral_p1 / neutral_p3
  fx_mpst bases <corp>_p3                    ->  fx_cdhl base_<corp>_p3   (corp = solace, meridian)
Then every stock base is compared with the published round-2 plate (px over 8 / 255, max)."""
import shutil, os, json
import numpy as np
from PIL import Image
R2 = 'D:/rc_scratch/combat_redesign/locked/round2/effects/'
C = R2 + 'fx_cdhl/work/'
M = R2 + 'fx_mpst/work/bases/'
FIN = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
for var in ('p1', 'p3'):
    for part, mp in (('_below', '_below'), ('_above', '_above'), ('', '_full')):
        shutil.copyfile(C + 'base_neutral_%s%s.png' % (var, part), M + 'neutral_%s%s.png' % (var, mp))
for sk in ('solace', 'meridian'):
    for part, mp in (('_below', '_below'), ('_above', '_above'), ('', '_full')):
        shutil.copyfile(M + '%s_p3%s.png' % (sk, mp), C + 'base_%s_p3%s.png' % (sk, part))
out = {}
for sk in ('neutral', 'solace', 'meridian'):
    for kind, plate in (('p1', 'p1_decide'), ('p2', 'p2_preview'), ('p3', 'p3_resolve')):
        fp = M + '%s_%s_full.png' % (sk, kind)
        if not os.path.exists(fp):
            continue
        a = np.asarray(Image.open(fp).convert('RGB')).astype(int)
        b = np.asarray(Image.open(FIN + plate + ('' if sk == 'neutral' else '_' + sk) + '.png').convert('RGB')).astype(int)
        d = np.abs(a - b).max(2)
        out['%s_%s' % (sk, kind)] = dict(px_over_8=int((d > 8).sum()), px_over_3=int((d > 3).sum()), max=int(d.max()), mean=round(float(d.mean()), 4))
        print(sk, kind, out['%s_%s' % (sk, kind)], flush=True)
json.dump(out, open(R2 + 'work/bases_vs_final.json', 'w'), indent=1)
