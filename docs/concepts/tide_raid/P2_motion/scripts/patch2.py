s = open('m2.py').read()
s = s.replace("""    def __init__(self, rid):
        w = world()
        r = w.routes[rid]
        self.rid = rid
        self.typ = r['typ']
        self.ext = float(r['ext'])
        p = np.asarray(r['path'], float)""", """    def __init__(self, rid, path=None, typ=None):
        w = world()
        r = w.routes[rid] if path is None else dict(path=path, typ=typ, ext=0.0, sites=[])
        self.rid = rid
        self.typ = r['typ']
        self.ext = float(r['ext'])
        p = np.asarray(r['path'], float)""")
open('m2.py', 'w').write(s)
