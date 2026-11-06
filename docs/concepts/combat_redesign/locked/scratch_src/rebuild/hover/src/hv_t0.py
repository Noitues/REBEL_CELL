"""smoke test: does the old hover pipeline (corp/src hz_plates, imported read-only) still render on the rebuilt board?"""
import sys, os, time
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
import hz_core as Z
Z.HERE = 'D:/rc_scratch/combat_redesign/locked/rebuild/hover/'
import hz_plates as P
pid = sys.argv[1] if len(sys.argv) > 1 else 'h02'
t = time.time()
img, rep = P.BUILD[pid](True)
img.save(Z.HERE + 'dbg/t0_%s.png' % pid)
print('ok', pid, round(time.time() - t, 1), rep['asserts']['passed'], rep['asserts']['total'])
