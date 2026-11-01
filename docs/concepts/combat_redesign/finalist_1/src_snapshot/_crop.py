import sys
from PIL import Image
im = Image.open('D:/rc_art/art-pass/docs/concepts/combat_e10_design/final/p1_decide.png').convert('RGB')
def c(box, k, name):
    x = im.crop(box); return x.resize((x.width*k, x.height*k), Image.LANCZOS)
a = c((576, 360, 676, 440), 6, 'a'); b = c((665, 190, 765, 270), 6, 'b')
s = Image.new('RGB', (1200, 480)); s.paste(a, (0, 0)); s.paste(b, (600, 0))
s.save('D:/rc_scratch/e10_design/assembled/out/spoke_crops.png')
