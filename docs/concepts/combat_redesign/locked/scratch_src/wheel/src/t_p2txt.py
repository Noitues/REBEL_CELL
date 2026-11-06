import sys, os, glob, json
sys.dont_write_bytecode=True
from PIL import ImageDraw
LOG=[]
_o=ImageDraw.ImageDraw.text
def _t(self,xy,text,*a,**k):
    LOG.append(str(text)); return _o(self,xy,text,*a,**k)
ImageDraw.ImageDraw.text=_t
import f1_render as R, f1_hand as FH
tmp='D:/rc_scratch/combat_redesign/locked/wheel/work_text/'
for fp in glob.glob(tmp+'*'): os.remove(fp)
FH.CACHE=tmp; FH._mem.clear(); FH._ui.clear()
R.render('p2')
E10=json.load(open('D:/rc_art/art-pass/docs/concepts/combat_e10_design/final/text_e10.json',encoding='utf-8'))
from collections import Counter
mine=Counter(x.strip() for x in LOG if len(x.strip())>1)
e=Counter(x.strip() for x in E10['p2'] if len(x.strip())>1)
print('only e10', dict(e-mine)); print('only f1', dict(mine-e))
