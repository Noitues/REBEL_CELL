import sys
sys.dont_write_bytecode=True
import f1_geo
import asm_r2 as A
A.setup()
import f1_tower as FT
sys.argv=['x']+sys.argv[1:]
import runpy
exec(open('f1_tower.py').read().split("if __name__ == '__main__':")[1].replace('\n    ','\n') if False else '')
import json,time
from PIL import Image
t=time.time()
J=json.load(open('../state_e10.json'))
key=sys.argv[1] if len(sys.argv)>1 else 'f1'
im,_=FT.render_tower(J[key])
bg=Image.new('RGBA',im.size,(20,18,32,255)); bg.alpha_composite(im); bg.save('../out/tower_%s.png'%key)
print(time.time()-t)
