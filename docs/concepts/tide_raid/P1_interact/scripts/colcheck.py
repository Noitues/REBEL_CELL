"""colour candidates: dE76 in Lab under normal / deutan / tritan (Machado 2009). python colcheck.py"""
import numpy as np, itertools, sys
from lib import *
DEUT = np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]])
TRIT = np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]])
def lin(a): return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
def unlin(a):
    a=np.clip(a,0,1); return np.where(a<=.0031308,a*12.92,1.055*a**(1/2.4)-.055)
def sim(c,M): return unlin(M@lin(np.array(c,float)))
def lab(c):
    l=lin(np.clip(c,0,1)); X=np.array([[.4124,.3576,.1805],[.2126,.7152,.0722],[.0193,.1192,.9505]])@l
    X=X/np.array([.9505,1,1.089]); f=np.where(X>.008856,np.cbrt(X),7.787*X+16/116)
    return np.array([116*f[1]-16,500*(f[0]-f[1]),200*(f[1]-f[2])])
def de(a,b,M=None):
    if M is not None: a,b=sim(a,M),sim(b,M)
    return float(np.linalg.norm(lab(a)-lab(b)))
def report(name_cols, pairs):
    for a,b in pairs:
        A,B=name_cols[a],name_cols[b]
        print('%-10s %-10s N %5.1f  D %5.1f  T %5.1f'%(a,b,de(A,B),de(A,B,DEUT),de(A,B,TRIT)))
if __name__=='__main__':
    bg=base_city('default')
    reg=bg[480:700,1000:1400].reshape(-1,3)
    city_med=np.median(reg,0); city_hi=np.percentile(reg,90,axis=0)
    print('city med',np.round(city_med*255),'p90',np.round(city_hi*255))
    C={'city':city_med,'cityhi':city_hi,'INK':INK}
    for n,h in [('Dold','3D86FF'),('Dnew','5AA8FF'),('Dnew2','4FB0FF'),('D3','66B8FF'),('Eold','FFD800'),('Enew','FFF04A'),('E2','FFEB3B'),
                ('amb_old','FFB21E'),('amb2','E8890C'),('amb3','F29A1A'),('amb4','D9820F'),('ora','FF6A1A'),('red','FF3347'),('mint','B8FFF2'),('teal','19C9B4'),
                ('towOld','7FEFFF'),('tow','8497C4'),('tow2','7F8FB8'),('N','FF40D6'),('lime','C6FF2E')]:
        C[n]=hexc(h)
    for grp in [[('Dold','city'),('Dnew','city'),('Dnew2','city'),('D3','city'),('Dnew','INK'),('Dnew','tow'),('Dnew','teal'),('Dnew','mint'),('D3','tow2'),('Dnew','N')],
                [('Eold','amb_old'),('Enew','amb_old'),('Enew','amb2'),('Enew','amb3'),('Enew','amb4'),('Eold','amb2'),('amb2','ora'),('amb3','ora'),('amb4','ora'),('amb_old','ora'),('Enew','lime'),('Enew','mint')],
                [('tow','city'),('tow','cityhi'),('tow2','city'),('tow','mint'),('tow','teal'),('mint','teal'),('N','city'),('N','cityhi')]]:
        report(C,grp); print()
