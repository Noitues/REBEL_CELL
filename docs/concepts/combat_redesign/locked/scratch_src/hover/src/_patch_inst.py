import re
p='lw_install.py'
s=open(p).read()
s=s.replace("import lc_run as LR                 # imports f1_render + the linocut patches\n","")
s=s.replace("ROOT = 'D:/rc_scratch/corp_skin/material/'","ROOT = 'D:/rc_scratch/combat_redesign/locked/assembled/'")
# replace _remap with corp-independent tape remap
a=s.index("def _remap(L, mk):")
b=s.index("def ndi_open(b):")
new='''def _remap(L, mk):
    """the THIS TURN tape: one neutral treatment, applied for every corp (lw_skin.NeutralTape); the skin is not consulted"""
    from lw_skin import NeutralTape
    L.im.load()
    L.im.paste(NeutralTape.remap(L.im))


'''
s=s[:a]+new+s[b:]
# drop main
m=s.index("if __name__ == '__main__':")
s=s[:m]
open(p,'w').write(s)
