import sys
from PIL import Image
v=sys.argv[1]
im=Image.open('../out/plate_%s.png'%v)
w=im.crop((340,340,740,740)).resize((800,800),Image.LANCZOS)
h=im.crop((840,760,1640,1080))
w.save('../out/_w_%s.png'%v); h.save('../out/_h_%s.png'%v)
