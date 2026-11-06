import sys,math; sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
im=np.asarray(Image.open('D:/rc_art/art-pass/docs/concepts/combat_e10_design/final/p1_decide.png').convert('RGB'),np.float32)
INK=np.array([12,10,22],np.float32)
C=(536,540)
for k in (0,5,1):
    a=math.radians(30+60*k); t=(math.sin(a),-math.cos(a)); n=(math.cos(a),math.sin(a))
    for r in (353,355,357,359,360):
        row=[]
        for off in range(-5,6):
            x=C[0]+r*t[0]+off*n[0]; y=C[1]+r*t[1]+off*n[1]
            p=im[int(round(y)),int(round(x))]
            row.append('I' if np.abs(p-INK).sum()<=40 else '.')
        print(k,r,''.join(row))
