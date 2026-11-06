import sys,time
sys.dont_write_bytecode=True
import gram_render as R
OUT='D:/rc_art/art-pass/docs/concepts/combat_redesign/explore/grammar/'
SETS={'base':dict(time='A',hp='A',wave='A'),'time_B':dict(time='B',hp='A',wave='A'),'time_C':dict(time='C',hp='A',wave='A'),
 'hp_B':dict(time='A',hp='B',wave='A'),'hp_C':dict(time='A',hp='C',wave='A'),'wave_B':dict(time='A',hp='A',wave='B'),'wave_none':dict(time='A',hp='A',wave=None)}
for n in sys.argv[1:]:
    t=time.time()
    im=R.render('p1',cfg=SETS[n]); im.save(OUT+'plate_%s.png'%n); print(n,time.time()-t,flush=True)
