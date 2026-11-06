import sys
sys.dont_write_bytecode = True
from PIL import Image
O='../out/'
D='D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/hover/'
box=(0,0,1010,530)
ims=[Image.open(O+'as_p1_%s.png'%c).convert('RGB').crop(box).resize((2020,1060),Image.LANCZOS) for c in ('solace','meridian')]
s=Image.new('RGB',(2020,2130),(0,0,0)); s.paste(ims[0],(0,0)); s.paste(ims[1],(0,1070))
s.save(D+'rings_crop.jpg',quality=90)
