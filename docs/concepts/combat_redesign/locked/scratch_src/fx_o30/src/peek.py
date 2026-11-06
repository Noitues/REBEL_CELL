import sys, numpy as np
from PIL import Image
F='D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/p3_resolve.png'
W='D:/rc_scratch/combat_redesign/locked/fx_o30/work/'
a=np.asarray(Image.open(F).convert('RGB')).astype(int)
b=np.asarray(Image.open(W+'base_neutral_p3.png').convert('RGB')).astype(int)
e=np.asarray(Image.open(W+'base_neutral_p3_empty.png').convert('RGB')).astype(int)
print('final vs my p3 >6 px', (np.abs(a-b).max(2)>6).sum())
o=Image.new('RGB',(2120,1080)); o.paste(Image.open(F).crop((0,0,1060,1080)),(0,0)); o.paste(Image.open(W+'base_neutral_p3_empty.png').crop((0,0,1060,1080)),(1060,0))
o.resize((1060,540)).save(W+'peek_empty.png')
