import sys
from PIL import Image
f,x0,y0,x1,y1,out=sys.argv[1],*map(int,sys.argv[2:6]),sys.argv[6]
im=Image.open(f).crop((x0,y0,x1,y1)); k=1080/ (y1-y0) if len(sys.argv)<8 else float(sys.argv[7])
im=im.resize((int(im.width*k),int(im.height*k)),Image.LANCZOS); im.save(out)
