import sys; sys.dont_write_bytecode=True
import asm_r2 as A, kscene2 as K
from PIL import Image
push=int(sys.argv[1]); hs=float(sys.argv[2])
K.HOV_PUSH=push
K.FANS['P']['hov_s']=hs
im=A.render('p2',check=False)
im.crop((1000,720,1920,1080)).save('../out/hand_%d_%s.png'%(push,sys.argv[2]))
