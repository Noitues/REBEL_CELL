import os,sys,time,inspect,json,collections
sys.dont_write_bytecode=True
import asm_r2 as A
import cv_lib, wr_geo, wc2
LOG=[]
def site(skip=('wr_geo.py','cv_lib.py','t1.py')):
    out=[]
    for fr in inspect.stack()[2:8]:
        b=os.path.basename(fr.filename)
        if b in skip: continue
        out.append('%s:%d:%s'%(b,fr.lineno,fr.function))
        if len(out)>=2: break
    return out
def patch(name, fn):
    for m in list(sys.modules.values()):
        if m is not None and getattr(m,name,None) is not None and m.__name__ not in ('t1',):
            try: setattr(m,name,fn)
            except Exception: pass
o_dp=wr_geo.dash_path
def dash_path(L,pts,col,w,dash,gap,closed=True,start=0.0):
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    LOG.append(dict(kind='dash_path',site=site(),col=list(col)[:4],w=w,dash=[dash,gap],bbox=[min(xs),min(ys),max(xs),max(ys)],n=len(pts)))
    # draw with a flag so inner L.line is not re-logged
    return o_dp(L,pts,col,w,dash,gap,closed,start)
patch('dash_path',dash_path)
o_dl=wc2.dash_line
def dash_line(L,p0,p1,col,w,dash=(12,6),ink_w=None,alpha=255):
    LOG.append(dict(kind='dash_line',site=site(),col=list(col)[:4],w=w,dash=list(dash),bbox=[min(p0[0],p1[0]),min(p0[1],p1[1]),max(p0[0],p1[0]),max(p0[1],p1[1])],n=2))
    return o_dl(L,p0,p1,col,w,dash,ink_w,alpha)
patch('dash_line',dash_line)
orig=cv_lib.L2.line
def line(self,pts,col,w=2,dash=None):
    if dash is not None:
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        LOG.append(dict(kind='L.line',site=site(),col=list(col)[:4],w=w,dash=list(dash),bbox=[min(xs),min(ys),max(xs),max(ys)],n=len(pts)))
    return orig(self,pts,col,w,dash)
cv_lib.L2.line=line
beats=sys.argv[1:] or ['p1']
for b in beats:
    n0=len(LOG)
    im=A.render(b,room='D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_bio_bare.png',check=False)
    for l in LOG[n0:]: l['beat']=b
json.dump(LOG,open('../out/dash_log.json','w'),indent=0)
c=collections.Counter((l['beat'],l['kind'],tuple(l['site']),tuple(l['dash'])) for l in LOG)
for k,v in sorted(c.items()): print(k,v)
