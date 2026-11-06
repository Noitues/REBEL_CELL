"""half.py in out scale [x0 y0 x1 y1]"""
import sys
from PIL import Image
im=Image.open(sys.argv[1]).convert('RGB')
if len(sys.argv)>4: im=im.crop(tuple(int(v) for v in sys.argv[4:8]))
s=float(sys.argv[3]); im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS).save(sys.argv[2],quality=90)
