import sys
sys.dont_write_bytecode=True
import wr2_lib as W
VIO=(160,60,255); L1=(120,170,255); CY=(92,225,255)
def lum(c): return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
res=[]
cands=[]
for r in range(30,70,4):
    for g in range(90,135,4):
        cands.append((r,g,255))
for c in [(0x2F,0x6B,0xFF),(0x33,0x70,0xFF),(0x3A,0x78,0xFF)]+cands:
    ok=True; mins=[]
    for m in ('normal','deutan','protan','tritan'):
        s=(lambda x:x) if m=='normal' else (lambda x,m=m:W.sim_rgb(x,m))
        d1=W.dE(s(c),s(VIO)); d2=W.dE(s(c),s(L1)); mins.append((round(d1,1),round(d2,1)))
        if d1<10 or d2<10: ok=False
    dc=W.dE(c,CY)
    print(c, '#%02X%02X%02X'%c, 'OK' if ok else '--', mins, 'dCY',round(dc,1),'lum',round(lum(c)),'<L1',lum(c)<lum(L1))
    if ok: pass
