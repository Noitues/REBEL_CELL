import sys,math; sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
im=np.asarray(Image.open('D:/rc_art/art-pass/docs/concepts/combat_e10_design/final/p1_decide.png').convert('RGB'),np.float32)
a=math.radians(330); t=(math.sin(a),-math.cos(a))
for r in np.arange(352,361,0.5):
    x=536+r*t[0]; y=540+r*t[1]
    print(r,(round(x,1),round(y,1)),im[int(round(y)),int(round(x))])
