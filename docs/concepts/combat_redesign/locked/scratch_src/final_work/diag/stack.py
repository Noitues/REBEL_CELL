"""stack.py out.png in1 in2 ... (vertical stack, grey bg)"""
import sys
from PIL import Image
ims=[Image.open(p).convert('RGBA') for p in sys.argv[2:]]
W=max(i.width for i in ims); H=sum(i.height for i in ims)+10*len(ims)
o=Image.new('RGBA',(W,H),(90,90,100,255)); y=0
for i in ims:
    o.alpha_composite(i,(0,y)); y+=i.height+10
o.convert('RGB').save(sys.argv[1])
