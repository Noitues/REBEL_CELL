s = open('p1_spec.py').read()
# cage -25 %
s = s.replace("strength=0.28 * k, wire_strength=0.5 * k, col=CAGE_COL", "strength=0.21 * k, wire_strength=0.375 * k, col=CAGE_COL")
# ribbon width scale + ghost on ring/block/glow
s = s.replace("def ribbon(self, rid, s0=None, s1=None, k=1.0, w=None, alpha=1.0, grp='world', head=True):",
              "def ribbon(self, rid, s0=None, s1=None, k=1.0, w=None, alpha=1.0, grp='world', head=True, wk=1.0):")
s = s.replace("typ=R.typ, pts=R.bw.tolist(), w=w or W_BU[R.typ], h=0.5,", "typ=R.typ, pts=R.bw.tolist(), w=(w or W_BU[R.typ]) * wk, h=0.5,")
s = s.replace("def ring(self, sid, tier, k=1.0, r=None, strong=True):", "def ring(self, sid, tier, k=1.0, r=None, strong=True, ghost=0.55):")
s = s.replace("tex=L.WORK + 'tex/ring_%s.png' % tier, strength=3.0 * k, z=0.5))\n        self.spec['glows'].append(dict(pos=b.tolist(), r=r * 1.05, col=c, strength=1.1 * k, power=1.5, z=0.42))",
              "tex=L.WORK + 'tex/ring_%s.png' % tier, strength=3.0 * k, z=0.5, ghost=ghost))\n        self.spec['glows'].append(dict(pos=b.tolist(), r=r * 1.05, col=c, strength=1.1 * k, power=1.5, z=0.42, ghost=ghost))")
s = s.replace("def block(self, rid, s, tier, k=1.0, length=10.0, across=13.5):", "def block(self, rid, s, tier, k=1.0, length=10.0, across=13.5, ghost=0.55):")
s = s.replace("tex=L.WORK + 'tex/block_%s.png' % tier, strength=4.0 * k))", "tex=L.WORK + 'tex/block_%s.png' % tier, strength=4.0 * k, ghost=ghost))")
open('p1_spec.py', 'w').write(s)

b = open('p1_beats.py').read()
b = b.replace("""    B.spec['rings'].append(dict(id='lime_' + sid, pos=b.tolist(), r=11.5, w=1.3, col='C6FF2E', strength=8.0 * k, z=0.55, fill=1.0))""",
              """    B.spec['rings'].append(dict(id='lime_' + sid, pos=b.tolist(), r=11.5, w=1.3, col='C6FF2E', strength=8.0 * k, z=0.55, fill=1.0, ghost=0.55))""")
b = b.replace("def tier_target(B, rid, s_stop, tier, k=1.0, ring=True, block=True):\n    sid = TARGET[rid][0]\n    if ring:\n        B.ring(sid, tier, k=k)\n    if block:\n        B.block(rid, s_stop - 2, tier, k=k)",
              "def tier_target(B, rid, s_stop, tier, k=1.0, ring=True, block=True, ghost=0.55):\n    sid = TARGET[rid][0]\n    if ring:\n        B.ring(sid, tier, k=k, ghost=ghost)\n    if block:\n        B.block(rid, s_stop - 2, tier, k=k, ghost=ghost)")
# plan: hero beam = K3 (the E the card is dragged onto), others recede
b = b.replace("""    for rid in ('K1', 'K2', 'K3'):
        R = B.routes[rid]
        B.ribbon(rid, R.ext, None)
        B.head(rid, R.ext + RUN[rid])
    B.wall('t1_c', 'D')
    lime_ring(B, 't2_intel')""", """    for rid in ('K1', 'K2', 'K3'):
        R = B.routes[rid]
        hero = (rid == HERO['plan'])
        B.ribbon(rid, R.ext, None, k=(1.25 if hero else 0.55), wk=(1.15 if hero else 0.72))
        B.head(rid, R.ext + RUN[rid], k=1.0)
        B.ui.setdefault('hero', {})['plan'] = HERO['plan']
    B.wall('t1_c', 'D')
    lime_ring(B, 't2_intel')""")
b = b.replace("""        B.ribbon(rid, R.ext, s_stop + 20)
        B.ribbon(rid, s_stop + 40, None, k=0.22, alpha=0.45)
        tier_target(B, rid, s_stop, tier)
        B.head(rid, R.ext + RUN[rid])
        B.ui.setdefault('stops', {})[rid] = dict(site=sid, tier=tier, s=s_stop)
    B.wall('t1_c', 'D')
    home_deck(B, 44, 50, preview=6)""", """        hero = (rid == HERO['forecast'])
        B.ribbon(rid, R.ext, s_stop + 20, k=(1.3 if hero else 0.5), wk=(1.2 if hero else 0.7))
        if hero:
            B.ribbon(rid, s_stop + 40, None, k=0.14, alpha=0.4, wk=0.8)
        tier_target(B, rid, s_stop, tier, ghost=(0.55 if hero else 0.0))
        B.head(rid, R.ext + RUN[rid])
        B.ui.setdefault('stops', {})[rid] = dict(site=sid, tier=tier, s=s_stop)
    B.ui.setdefault('hero', {})['forecast'] = HERO['forecast']
    B.wall('t1_c', 'D')
    home_deck(B, 44, 50, preview=6)""")
b = b.replace("TARGET = {'K1'", "HERO = {'plan': 'K3', 'forecast': 'K1', 'reveal': 'K3', 'impact': 'K1', 'home_hit': 'K2'}\nTARGET = {'K1'", 1)
# aftermath rings ambient
b = b.replace("B.ring('t1_b', 'SITES_LOST', k=0.8)\n    B.ring('t1_c', 'HOLDS', k=0.8)", "B.ring('t1_b', 'SITES_LOST', k=0.8, ghost=0.0)\n    B.ring('t1_c', 'HOLDS', k=0.8, ghost=0.0)")
# tiers test: all visible
b = b.replace("    for sid, tier in TIERS_AT:\n        B.ring(sid, tier)", "    for sid, tier in TIERS_AT:\n        B.ring(sid, tier, ghost=1.0)")
open('p1_beats.py', 'w').write(b)
print(s.count('ghost'), b.count('ghost'), b.count('HERO'))
