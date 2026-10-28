s = open('p1_final.py').read()
s = s.replace("NN = {'plan': '01',", "NN = {'tiers': 'T0', 'plan': '01',", 1)
s = s.replace("UI = {'plan': ui_plan,", """def ui_tiers(cv, B, w):
    import p1_beats
    for sid, tier in p1_beats.TIERS_AT:
        tile(cv, w, sid, tier, None, up=40, dy=-10)
    hy.hud(cv, 44, 50, 80, 8, 0)


UI = {'tiers': ui_tiers, 'plan': ui_plan,""", 1)
s = s.replace("beats = list(NN) if sys.argv[1] == 'all' else [sys.argv[1]]", "beats = [b for b in NN if b != 'tiers'] if sys.argv[1] == 'all' else [sys.argv[1]]")
open('p1_final.py', 'w').write(s)
print('ok')
