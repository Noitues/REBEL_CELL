import numpy as np
from PIL import Image
import p1lib as L
T = ['UNTOUCHED','HOLDS','SITES_LOST','DAMAGED','BREACHED']
bg = np.array([40,34,70],np.float32)/255
tiles=[]
for t in T:
    im = np.asarray(Image.open(L.WORK+'tex/ring_%s.png'%t).convert('RGBA'),np.float32)/255
    a = im[...,3:4]; rgb = im[...,:3]*0+im[...,:3]
    out = bg*(1-a)+rgb*a*1.0
    img = Image.fromarray((out*255).astype(np.uint8)).resize((256,128),Image.LANCZOS)  # iso squash
    tiles.append(np.asarray(img))
row = np.concatenate(tiles,1)
Image.fromarray(row).save('D:/rc_scratch/tide_concepts/p3_work/prev_rings.png')
g = Image.fromarray(row).convert('L').resize((row.shape[1]//4,row.shape[0]//4),Image.LANCZOS).resize((row.shape[1],row.shape[0]//1),Image.NEAREST)
g.save('D:/rc_scratch/tide_concepts/p3_work/prev_rings_g.png')
