p = 'D:/rc_scratch/combat_redesign/locked/hover/src/hz_core.py'
s = open(p, encoding='utf-8').read()
old = s[s.index("    HOV['i'] = hand.index(lift) if lift is not None else None"):s.index("    HOV['used_dx'] = HOV['dx']")]
new = '''    HOV['i'] = hand.index(lift) if lift is not None else None
    yy_, xx_ = np.mgrid[0:H, 0:W]
    d_ = np.hypot(xx_ - C[0], yy_ - C[1])
    lift0 = 866
    best = None

    def draw(dx, ly):
        HOV['dx'] = float(dx)
        FH.LIFT_CY = ly
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        FH.draw_hand(lay, A.J, 'p1', nw=not words, lift=lift, dim_others=HAND_K / FH.REST_V)
        hm = np.asarray(lay.split()[3]) >= 128
        return lay, not (hm & (d_ < FH.HAND_MIN_R)).any()
    # the lifted card must keep every pixel outside wheel radius 455 (O-29 fix 3): first lift it a little less, then slide it right; least total move wins
    for ly in (866, 876, 886, 896, 904):
        for dx in range(0, 61, 4):
            if best is not None and dx + 0.6 * (ly - lift0) >= best[0]:
                break
            lay, ok = draw(dx, ly)
            if ok:
                best = (dx + 0.6 * (ly - lift0), dx, ly)
                break
        if lift is None:
            break
    if best is None:
        best = (0, 0, lift0)
    hand_lay, ok = draw(best[1], best[2])
    HOV['lift_cy'] = best[2]
    FH.LIFT_CY = lift0
'''
s = s.replace(old, new)
s = s.replace("HL.pencil_oval(L, xt + tw / 2, cy, tw / 2 + 11, 26, seed=3)", "HL.pencil_oval(L, xt + tw / 2, cy, tw / 2 + 13, 24, seed=3)")
s = s.replace("HL.pencil_oval(L, box[0] + 6 + lw / 2, cy, lw / 2 + 11, 26, seed=4)", "HL.pencil_oval(L, box[0] + 6 + lw / 2, cy, lw / 2 + 13, 24, seed=4)")
s = s.replace("    cy = (box[1] + box[3]) / 2 - 3\n", "    cy = (box[1] + box[3]) / 2 + 7\n")
open(p, 'w', encoding='utf-8').write(s)
p = 'D:/rc_scratch/combat_redesign/locked/hover/src/hz_plates.py'
s = open(p, encoding='utf-8').read()
s = s.replace("""    NOW['words'] = words
    Lm = L2()
    changed = marks_fn(Lm) or {}
    top = []
    if top_fn:
        Lx = L2()
        top_fn(Lx)
        top.append(Lx.done())""", """    NOW['words'] = words
    Z.CAP['on'] = False
    Lm = L2()
    changed = marks_fn(Lm) or {}
    top = []
    if top_fn:
        Lx = L2()
        top_fn(Lx)
        top.append(Lx.done())
    Z.CAP['on'] = True""")
s = s.replace("""    NOW['words'] = words
    Lm = L2()
    marks_fn(Lm)
    img = HL.dim""", """    NOW['words'] = words
    Z.CAP['on'] = False
    Lm = L2()
    marks_fn(Lm)
    Z.CAP['on'] = True
    img = HL.dim""")
s = s.replace("lift_dx=Z.HOV.get('used_dx'))", "lift_dx=Z.HOV.get('dx'), lift_cy=Z.HOV.get('lift_cy'))")
s = s.replace("HL.pencil(L, HL.arc(rr + HALF + 4.5, it['a0'] + 3, it['a1'] - 2), w=3.0, ink=1.7, seed=it['u']['id'], cap=False)",
              "HL.pencil(L, HL.arc(rr + HALF + 2.0, it['a0'] + 3, it['a1'] - 2), w=2.6, ink=1.5, seed=it['u']['id'], cap=False)")
s = s.replace("HL.arc(r, 60 * (it['s0'] + q) - 17, 60 * (it['s0'] + q) + 17), w=3.6", "HL.arc(r - 2.5, 60 * (it['s0'] + q) - 13, 60 * (it['s0'] + q) + 13), w=3.4")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
