import sys
from PIL import Image
W='D:/rc_scratch/combat_redesign/locked/fx_cdhl/work/'
a=Image.open(W+'kf/%s_0.png'%sys.argv[1]); b=Image.open(W+'kf/%s_%s.png'%(sys.argv[1],sys.argv[2]))
x0,y0,x1,y1=map(int,sys.argv[3:7])
a=a.crop((x0,y0,x1,y1)); b=b.crop((x0,y0,x1,y1)); s=3
o=Image.new('RGB',((x1-x0)*s*2+10,(y1-y0)*s))
o.paste(a.resize(((x1-x0)*s,(y1-y0)*s)),(0,0)); o.paste(b.resize(((x1-x0)*s,(y1-y0)*s)),((x1-x0)*s+10,0)); o.save(W+'cmp.png')
