s = open('a2_hover.py').read()
import re
i = s.index("    def _path(ang):")
j = s.index("    def _clear(pl_):")
s = s[:i] + """    def _path(ang):
        an = (tp[0] + math.cos(ang) * 20, tp[1] + math.sin(ang) * 20)
        p1 = (tp[0] + math.cos(ang) * 52, tp[1] + math.sin(ang) * 52)
        return an, [an, p1, (mid[0] - 40, st[1] + (p1[1] - st[1]) * 0.1), mid, st]

""" + s[j:]
s = re.sub(r"    print\('LEADER badges'.*\n", "", s)
s = s.replace("    anc, pl = _path(base_ang)\n    for dg in (0, 15, -15, 30, -30, 45, -45, 60, -60, 75, -75, 90, -90, 110, -110, 130, -130):", "    anc, pl = _path(base_ang)\n    for dg in (0, 15, -15, 30, -30, 45, -45, 60, -60, 75, -75, 90, -90, 110, -110, 130, -130, 150, -150, 180):")
open('a2_hover.py','w').write(s)
