import sys
sys.dont_write_bytecode=True
import wr2_lib as W
VIO=(160,60,255); L1=(120,170,255)
out=[]
for r in range(0,100,4):
    for g in range(60,150,4):
        for b in (255,235):
            c=(r,g,b); mn=99; rows=[]
            for m in ('normal','deutan','protan','tritan'):
                s=(lambda x:x) if m=='normal' else (lambda x,m=m:W.sim_rgb(x,m))
                d1=W.dE(s(c),s(VIO)); d2=W.dE(s(c),s(L1)); mn=min(mn,d1,d2); rows.append((round(d1,1),round(d2,1)))
            out.append((mn,c,rows))
out.sort(reverse=True)
for mn,c,rows in out[:12]: print(round(mn,1),'#%02X%02X%02X'%c,rows)
print('--- in 2F6B..3A78 neighbourhood')
for mn,c,rows in sorted(out):
    pass
