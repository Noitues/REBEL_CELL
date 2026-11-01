"""render the F1 plate set into finalist_1/out and the deliverable folder"""
import sys, os, time, shutil, traceback
sys.dont_write_bytecode = True
import f1_render as R
DEL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/finalist_1/'
os.makedirs(DEL, exist_ok=True)
BIO = R.ROOM
SRV = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_srv_bare.png'
GH = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_gh_bare.png'
JOBS = [
    ('p1_decide', dict(beat='p1', check=True)),
    ('p1_nowords', dict(beat='nowords', check=True)),
    ('p2_preview', dict(beat='p2', check=True)),
    ('p2b_hover', dict(beat='p2b', check=True)),
    ('p3_resolve', dict(beat='p3', check=True)),
    ('p1_decide_srv', dict(beat='p1', room=SRV)),
    ('p1_decide_gh', dict(beat='p1', room=GH)),
    ('p2_preview_f2t', dict(beat='p2', key='f2t')),
    ('p2_preview_f2b', dict(beat='p2', key='f2b')),
]
want = sys.argv[1:] or [j[0] for j in JOBS]
t0 = time.time()
for nm, kw in JOBS:
    if nm not in want:
        continue
    try:
        im = R.render(**kw)
        im.save(R.OUT + nm + '.png')
        print(nm, 'ok', round(time.time() - t0), 'dash calls', len(R.DASH_LOG), 'dotted marks', len(R.DOT_LOG), flush=True)
    except Exception:
        print(nm, 'FAILED', flush=True)
        traceback.print_exc()

import build10 as B10
open(R.OUT + 'assert_draw_log.txt', 'w').write(chr(10).join(B10.LOGD) + chr(10))
print('draw asserts', len(B10.LOGD), 'PASS', sum(1 for l in B10.LOGD if l.startswith('PASS')), 'FAIL', sum(1 for l in B10.LOGD if l.startswith('FAIL')))
print('DASH_LOG', R.DASH_LOG[:5], 'DOT_LOG', R.DOT_LOG)
