import sys
from PIL import Image
a=Image.open(sys.argv[1]); b=Image.open(sys.argv[2])
x0,y0,x1,y1=[int(v) for v in sys.argv[4:8]]
ca=a.crop((x0,y0,x1,y1)); cb=b.crop((x0,y0,x1,y1))
k=3
ca=ca.resize((ca.width*k,ca.height*k),Image.LANCZOS); cb=cb.resize((cb.width*k,cb.height*k),Image.LANCZOS)
o=Image.new('RGB',(ca.width*2+10,ca.height),(30,30,30)); o.paste(ca,(0,0)); o.paste(cb,(ca.width+10,0)); o.save(sys.argv[3])
