import sys
from PIL import Image
S='D:/rc_art/art-pass/docs/concepts/tide_raid/H2_jack_in_settle/'
names=sys.argv[2:]
rows=[]
for n in names:
    a=Image.open(S+'squint/%s_320.png'%n).resize((640,360),Image.LANCZOS)
    b=Image.open(S+'squint/%s_blur4.png'%n).resize((640,360),Image.LANCZOS)
    c=Image.open(S+'colorblind/%s_tritan.png'%n).resize((640,360),Image.LANCZOS)
    rows.append((a,b,c))
sh=Image.new('RGB',(1920,360*len(rows)))
for i,r in enumerate(rows):
    for j,im in enumerate(r): sh.paste(im,(j*640,i*360))
sh.save(sys.argv[1])
