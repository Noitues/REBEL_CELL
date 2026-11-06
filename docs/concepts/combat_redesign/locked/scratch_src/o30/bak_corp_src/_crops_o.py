import sys
from PIL import Image, ImageDraw, ImageFont
B='D:/rc_scratch/e10_design/assembled/before/'
A='D:/rc_art/art-pass/docs/concepts/combat_e10_design/final/'
FD='D:/rc_art/art-pass/assets/fonts/'
mo=ImageFont.truetype(FD+'ShareTechMono-Regular.ttf',18)
# (label, plate, box)
items=[('O1 warded badge (unit 3) p1','p1_decide',(590,330,740,450)),
 ('O2 HOLD NEXT label p1','p1_decide',None),
 ('O3 soak X p2','p2_preview',None),
 ('O4a live label nowords','p1_nowords',None),
 ('O4b Spin card nowords','p1_nowords',None)]
