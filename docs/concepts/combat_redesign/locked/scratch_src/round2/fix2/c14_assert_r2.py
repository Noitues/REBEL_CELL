"""C14 determinism assert on the PUBLISH path (2026-11-04, round 2 gate-1 fix; gate: "the C14 assert does not test the publish path",
round2/board/c14_assert.py's p3 differed from the published p3 plate in 1629 px over 2/255, max 47, because it rendered without the capture
hooks that asm_render.py installs for every published plate).

In ONE process, with asm_render.py's hooks installed (round2/effects/tools/asm_hooks.py: rb_capture.install, asm_render's layer captures, the
hand capture; checked line for line against asm_render.py below), render p3 <skin> (its own room, check=False as asm_render does), then
p1_clean (f1 with no units, no guns, no arcs), then p3 <skin> again.  Pass = the two p3 renders are pixel-identical, each p3 equals the plate
rb_set published for publish (locked/rebuild/board/p3_resolve[_<skin>].png) at 0 px, the KA_* glyph registry holds after every render
(rb4_patch.registry_ok) and the old e10 card library loaded (so the restore was exercised).  A fresh tower cache (<outdir>/tower_cache/).
Exit 0 = pass, 1 = fail.  Writes <outdir>/c14_assert_r2_<skin>.json.
python c14_assert_r2.py <skin> <outdir>"""
import sys, os, copy, time, json, re
sys.dont_write_bytecode = True
skin = sys.argv[1]
OUT = sys.argv[2]
os.environ['CORP'] = skin
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
TOOLS = 'D:/rc_scratch/combat_redesign/locked/round2/effects/tools'
BOARD = 'D:/rc_scratch/combat_redesign/locked/rebuild/board/'
sys.path.insert(0, SRC)
sys.path.insert(1, TOOLS)
os.chdir(SRC)
os.makedirs(OUT, exist_ok=True)
CW = OUT + '/tower_cache_%s/' % skin
os.makedirs(CW, exist_ok=True)
for f in os.listdir(CW):
    os.remove(CW + f)

# the hook copy must be asm_render's own sequence: every _cap(...) line and the rb_capture / hand installs, in order
_src_asm = open(SRC + '/asm_render.py', encoding='utf-8').read()
_src_hk = open(TOOLS + '/asm_hooks.py', encoding='utf-8').read()
caps_asm = re.findall(r"^\s*_cap\(([^)]*)\)", _src_asm, re.M)
caps_hk = re.findall(r"^\s*_cap\(([^)]*)\)", _src_hk, re.M)
hooks_same = caps_asm == caps_hk and 'RBC.install(R, A, R.FH, MASKS, beat)' in _src_asm and 'RBC.install(R, A, R.FH, MASKS, beat)' in _src_hk \
    and 'R.FH.draw_hand = _hand' in _src_asm and 'R.FH.draw_hand = _hand' in _src_hk

import lw_render as LW
import bd_grade as BG
import numpy as np
from PIL import Image
import rb4_patch as RB4
import wr2_units as W2U
import asm_hooks as AH
R = LW.R
R.WORK = CW
A = R.A
AH.install(R, A, 'p3')
ROOM = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_%s_bare.png' % BG.CORP_ROOM.get(skin, 'bio')
J = A.J
pub = BOARD + 'p3_resolve' + ('' if skin == 'neutral' else '_' + skin) + '.png'
ref = np.asarray(Image.open(pub).convert('RGB'), np.int16) if os.path.exists(pub) else None
rep = dict(skin=skin, path='asm_render hooks (round2/effects/tools/asm_hooks.py), check=False render, the skin room', hooks_match_asm_render=hooks_same,
           cap_lines=len(caps_asm), published_candidate=pub, steps=[])
ims = []
for i, kind in enumerate(('p3', 'p1_clean', 'p3')):
    t = time.time()
    if kind == 'p3':
        im = R.render('p3', room=ROOM, check=False)
    else:
        f1 = copy.deepcopy(J['f1'])
        ids = tuple(u['id'] for u in f1['units'])
        f1['units'] = []
        og = R.FG.make_guns
        R.FG.make_guns = lambda f, k, w: (Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)), None)
        try:
            im = R.render('p1', room=ROOM, frame=f1, tag='r2_f1clean', arcs_skip=ids)
        finally:
            R.FG.make_guns = og
    ok, bad = RB4.registry_ok()
    st = dict(i=i, kind=kind, s=round(time.time() - t, 1), registry_ok=ok, registry_bad=bad, old_library_loaded='k' in W2U._LIB,
              restored=RB4.INFO.get('c14_library_restored'))
    if kind == 'p3':
        a = np.asarray(im.convert('RGB'), np.int16)
        ims.append(a)
        im.save(OUT + '/%d_p3_%s.png' % (i, skin))
        if ref is not None:
            d = np.abs(a - ref).max(axis=2)
            st.update(vs_published_max_diff=int(d.max()), vs_published_px_differing=int((d > 0).sum()), vs_published_px_over_2=int((d > 2).sum()))
    rep['steps'].append(st)
    print(st, flush=True)
d = np.abs(ims[0] - ims[1]).max(axis=2)
rep['p3_vs_p3_max_diff'] = int(d.max())
rep['p3_vs_p3_px_differing'] = int((d > 0).sum())
vs_pub = [s.get('vs_published_px_differing') for s in rep['steps'] if s['kind'] == 'p3']
rep['p3_vs_published_px_differing'] = vs_pub
rep['pass'] = bool(hooks_same and ref is not None and rep['p3_vs_p3_px_differing'] == 0 and all(v == 0 for v in vs_pub)
                   and all(s['registry_ok'] for s in rep['steps']) and any(s['old_library_loaded'] for s in rep['steps']))
json.dump(rep, open(OUT + '/c14_assert_r2_%s.json' % skin, 'w'), indent=1)
print('C14 ASSERT (publish path)', skin, 'PASS' if rep['pass'] else 'FAIL', 'p3 vs p3', rep['p3_vs_p3_px_differing'], 'px; p3 vs published', vs_pub,
      'hooks match', hooks_same, flush=True)
sys.exit(0 if rep['pass'] else 1)
