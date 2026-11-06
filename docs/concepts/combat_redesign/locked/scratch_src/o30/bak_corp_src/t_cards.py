import sys
sys.dont_write_bytecode=True
import f1_geo
import asm_r2 as A
A.setup()
import st_cards as K
from PIL import Image
names=['Brace','Spin3','Trigger','Twist']
rows=[]
for nw in (False,True):
    K.NW[0]=nw
    ims=[K.render_card(n,'A',seed=i*3+1,ss=4,scale=2) for i,n in enumerate(names)]
    rows.append(ims)
w=rows[0][0].width; h=rows[0][0].height
sh=Image.new('RGBA',(w*4+50,h*2+30),(40,36,52,255))
for r,ims in enumerate(rows):
    for i,im in enumerate(ims): sh.alpha_composite(im,(10+i*(w+6),10+r*(h+10)))
sh.save('../out/t_cards.png'); print(sh.size)
