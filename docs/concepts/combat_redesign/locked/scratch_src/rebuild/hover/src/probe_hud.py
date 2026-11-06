"""probe: render the rebuilt board (no hand) through hz_core and dump the HUD registries (hud2.R, obj2.R), INFO and a few masks' boxes"""
import sys, os, time, json
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
import hz_core as Z
import numpy as np
import obj2
OUT = 'D:/rc_scratch/combat_redesign/locked/rebuild/hover/dbg/'
t = time.time()
f = Z.A.J['f1']
Z.reset_checks()
img = Z.board('p1', f, f, Z.ftag(f, 'neutral'), True)
img.save(OUT + 'probe_board_p1.png')
out = dict(hud2={k: v for k, v in Z.hud2.R.items() if not k.startswith('_cols')}, obj2={k: v for k, v in obj2.R.items()},
           info={k: (v if isinstance(v, (int, float, str, list, tuple)) else str(v)) for k, v in Z.A.INFO.items()},
           masks={k: [int(x) for x in (np.nonzero(m)[1].min(), np.nonzero(m)[0].min(), np.nonzero(m)[1].max(), np.nonzero(m)[0].max())] for k, m in Z.MASKS.items() if m.any()})
json.dump(out, open(OUT + 'probe_hud.json', 'w'), indent=1, default=str)
print('ok', round(time.time() - t, 1))
for k in ('bill_frame', 'hero_pair', 'you_hp_tally', 'objectives_frame', 'ram_trace_frame', '_hp_pos', 'header_plate', '_column'):
    print(k, Z.hud2.R.get(k))
print('obj2', {k: v for k, v in obj2.R.items()})
print('hud_bottom', Z.A.INFO.get('hud_bottom'))
