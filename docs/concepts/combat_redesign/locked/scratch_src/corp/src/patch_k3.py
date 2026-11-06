b = open('build9.py').read()
b = b.replace("    if beat == 'p3':\n        pass\n", "    if beat == 'p3':\n        for e_ in f['log']:\n            if e_[0] == 'fire' and e_[3] is not None:\n                s_, dep_ = e_[1], e_[5]\n                L.line([ppx(C, RS['s1'] + 3, 60 * s_ + 3), pt(CB.ring_geom(dep_)[0] + 20, 60 * s_, 6)], CYAN + (170,), 2.4, dash=(5, 6))\n")
open('build9.py', 'w').write(b)
