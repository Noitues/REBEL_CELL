import numpy as np
from PIL import Image
im=Image.open('D:/rc_tmp/combat_critic/plates/waves_e10/p1_decide.png').convert('RGB')
a=np.asarray(im).astype(float)/255
print(im.size)
v=a.max(2); mn=a.min(2); s=(v-mn)/(v+1e-6)
# sample the old backdrop at right
for (x,y) in [(1500,600),(1300,500),(1700,800),(1100,650),(40,300),(60,600),(900,60),(1000,1000)]:
    print((x,y),a[y,x].round(2))
# backdrop stats region
reg=(slice(400,950),slice(1100,1900))
print('bd V range',np.percentile(v[reg],[1,50,99]),'S',np.percentile(s[reg],[1,50,99]))
