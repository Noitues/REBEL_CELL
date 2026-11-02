import sys,time
sys.dont_write_bytecode=True
import asm_r2 as A
t=time.time()
im=A.render('p1',room='D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_bio_bare.png',check=False)
im.save('D:/rc_scratch/combat_redesign/locked/assembled/out/base_p1.png')
print('ok',time.time()-t)
