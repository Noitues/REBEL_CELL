p='hq_graph.py'; s=open(p,encoding='utf8').read()
s=s.replace('''            "H_decision": (CR.decision(WALK_DEC), dict(walked=WALK_DEC))}''','''            "H_decision": (CR.decision(WALK_DEC), dict(walked=WALK_DEC)),
            "H_hover": (CR.hover(WALK_DEC, HOVER_DEC), dict(walked=WALK_DEC, hover=HOVER_DEC, hover_k=1.0))}''')
s=s.replace('WALK_DEC = CP["walk_dec"]\n','WALK_DEC = CP["walk_dec"]\nHOVER_DEC = "le1"                          # the option from o2 that climbs the E leg\n',1)
open(p,'w',encoding='utf8').write(s)
