import sys; sys.dont_write_bytecode=True
import asm_r2 as A, measure_regions as M
BD='D:/rc_art/art-pass/docs/concepts/combat_backdrop/v2/'
for nm,rm in (('bio','room_bio_bare.png'),('srv','room_srv_bare.png'),('gh','room_gh_bare.png')):
    im=A.render('p1',room=BD+rm,check=False)
    im.save(A.ROOT+'out/rm_%s.png'%nm)
    print(nm,M.measure(im),flush=True)
