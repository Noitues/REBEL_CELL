s = open('a2_hover.py').read()
s = s.replace("    anc, pl = _path(base_ang)\n    for dg in", "    anc, pl = _path(base_ang)\n    print('LEADER badges', bad, 'tp', tp, 'log', [(e_['uid'], e_['side'], e_['size']) for e_ in AU.BADGE_LOG], 'u', u['id'], flush=True)\n    for dg in")
open('a2_hover.py','w').write(s)
