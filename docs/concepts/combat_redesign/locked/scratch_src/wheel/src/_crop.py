import sys
from PIL import Image
im=Image.open(sys.argv[1]); x0,y0,x1,y1=map(int,sys.argv[3:7]); s=float(sys.argv[7]) if len(sys.argv)>7 else 2
c=im.crop((x0,y0,x1,y1)); c=c.resize((int(c.width*s),int(c.height*s)),Image.LANCZOS); c.save(sys.argv[2])
