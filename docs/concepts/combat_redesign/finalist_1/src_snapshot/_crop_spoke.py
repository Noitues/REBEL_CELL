import sys; sys.dont_write_bytecode=True
from PIL import Image
im=Image.open('D:/rc_art/art-pass/docs/concepts/combat_e10_design/final/p1_decide.png').convert('RGB')
out=Image.new('RGB',(1200,600))
for i,(x,y) in enumerate(((714,232),(358,232))):
    c=im.crop((x-50,y-50,x+50,y+50)).resize((600,600),Image.NEAREST); out.paste(c,(i*600,0))
out.save('../out/spoke_k0k5.png')
