import sys
from PIL import Image
fs=sys.argv[2:]
n=len(fs); cols=2
rows=(n+1)//2
tw,th=960,540
sh=Image.new('RGB',(cols*tw,rows*th))
for i,f in enumerate(fs):
    im=Image.open(f).convert('RGB').resize((tw,th),Image.LANCZOS)
    sh.paste(im,((i%cols)*tw,(i//cols)*th))
sh.save(sys.argv[1])
