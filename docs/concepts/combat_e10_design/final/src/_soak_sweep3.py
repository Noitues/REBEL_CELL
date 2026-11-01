import sys
sys.dont_write_bytecode=True
import wr2_lib as W
VIO=(160,60,255); L1=(120,170,255); CY=(92,225,255); ref=(0x33,0x70,0xFF)
out=[]
for r in range(20,110,2):
    for g in range(80,150,2):
        for b in range(215,256,4):
            c=(r,g,b); mn=99; rows=[]
            for m in ('normal','deutan','protan','tritan'):
                s=(lambda x:x) if m=='normal' else (lambda x,m=m:W.sim_rgb(x,m))
                d1=W.dE(s(c),s(VIO)); d2=W.dE(s(c),s(L1)); mn=min(mn,d1,d2); rows.append((round(d1,1),round(d2,1)))
            if mn>=10:
                dist=sum((a-b_)**2 for a,b_ in zip(c,ref))**.5
                out.append((dist,c,rows,round(W.dE(c,CY),1),round(0.2126*r+0.7152*g+0.0722*b)))
out.sort()
for o in out[:10]: print(o[0].__round__(1),'#%02X%02X%02X'%o[1],o[2],'dCY',o[3],'lum',o[4])
