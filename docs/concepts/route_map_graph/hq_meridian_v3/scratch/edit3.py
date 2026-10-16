p='meridian_landmark.py'
L=open(p,encoding='utf8').read().split('\n')
s='\n'.join(L)
# 1 rename entry, drop eager bpy import
s=s.replace('def build(K, rooms=True, rail=True):\n','def build_hq(K, rooms=True, rail=True):\n',1)
s=s.replace('    import bpy\n    hooks = {"accs"','    hooks = {"accs"',1)
# 2 guard material block
i0=s.index('    m, nt = K.new_mat("container")')
i1=s.index('    C = Acc("containers", m, 1, K.COLL["compound"])')
blk=s[i0:i1]
blk=''.join('    '+l if l.strip() else l for l in blk.splitlines(True))
s=s[:i0]+'    m = None\n    if not getattr(K, "CITY", False):          # the container shader (the city module has its own facade shader)\n'+blk+s[i1:]
# 3 guard rim
j0=s.index('    RIMRX = bpy.data.collections.new("rim_rx")')
j1=s.index('    hooks["post_build"] = post_build')
rim=s[j0:j1]
rim=''.join('    '+l if l.strip() else l for l in rim.splitlines(True))
s=s[:j0]+'    if getattr(K, "CITY", False):\n        hooks["post_build"] = lambda OBJ: None\n    else:\n        import bpy\n'+''.join('    '+l if l.strip() else l for l in rim.splitlines(True))+'    if not getattr(K, "CITY", False):\n    '+s[j1:].lstrip(' ').replace('hooks["post_build"] = post_build','hooks["post_build"] = post_build',1)
open(p,'w',encoding='utf8').write(s)
