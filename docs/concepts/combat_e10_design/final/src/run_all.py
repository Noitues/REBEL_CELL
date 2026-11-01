"""render the 5 states on the cutaway + p1 on the srv and gh rooms into combat_e10_design/final/ ; writes assert_draw_log.txt"""
import sys, os, json, time, shutil
sys.dont_write_bytecode = True
import asm_r2 as A
import build10 as B10
OUT = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/final/'
OUT2 = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/r2/assembly/'
BD = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v2/'
os.makedirs(OUT, exist_ok=True); os.makedirs(OUT2, exist_ok=True)
R3 = {'p1': 'r3_p1_decide', 'p2': 'r3_p2_preview', 'p2b': 'r3_p2b_hover', 'p3': 'r3_p3_resolve', 'nowords': 'r3_p1_nowords'}
t = time.time()
meta = {}
for b in ['p1', 'p2', 'p2b', 'p3', 'nowords']:
    im = A.render(b)
    im.save(OUT + A.OUTNAME[b] + '.png')
    im.save(OUT2 + R3[b] + '.png')
    meta[b] = dict(hud_bottom=A.INFO['hud_bottom'], stack=A.INFO['stack'], hover_tag_box=A.INFO.get('hover_tag_box'), badges=list(A.AU.BADGE_LOG))
    print(b, round(time.time() - t), 'hud bottom', A.INFO['hud_bottom'], flush=True)
for nm, rm in (('srv', 'room_srv_bare.png'), ('gh', 'room_gh_bare.png')):
    im = A.render('p1', room=BD + rm)
    im.save(OUT + 'p1_decide_%s.png' % nm)
    print(nm, round(time.time() - t), flush=True)
open(OUT + 'assert_draw_log.txt', 'w').write(chr(10).join(B10.LOGD) + chr(10))
open(B10.ROOT + 'assert_draw_log.txt', 'w').write(chr(10).join(B10.LOGD) + chr(10))
npass = sum(1 for l in B10.LOGD if l.startswith('PASS')); nfail = sum(1 for l in B10.LOGD if l.startswith('FAIL'))
print('draw asserts', len(B10.LOGD), 'PASS', npass, 'FAIL', nfail)
json.dump(meta, open(B10.ROOT + 'out/meta.json', 'w'), default=str, indent=1)
