p='D:/rc_scratch/combat_redesign/locked/fx_o30b/cdhl/src/fx_cdhl.py'
s=open(p).read()
def rep(a,b):
    global s
    assert a in s, a[:70]
    s=s.replace(a,b,1)
rep("'A unit grows one more hit', (360, 170, 715, 335), 'p3alt'","'A unit grows one more hit', (360, 170, 715, 335), 'p3'")
rep("skins=SK3, post='p3', state=grow_state,","skins=SK3, post='p3grow', state=grow_state,")
rep("source='f2 Packet 5 (ring +1, sector 0, grown 1); pre-state rendered with grown 0'","source='f2 Packet 5 (ring +1, sector 0); post-state rendered with one more landing hit (land_hit = hit + 1), which the board draws as the hollow growth chevron'")
rep("[(0, 'anticipate: one solid chevron')","[(0, 'anticipate: two solid chevrons')")
rep("skins=SK3, post='p3alt', state=kill_state,","skins=SK3, post='p3kill', state=kill_state,")
rep("post-state rendered with the unit removed'","post-state rendered with Worm 2 and its shots removed (empty cell)'")
rep("'Shot weakened by the ward (gold)', (330, 580, 640, 940)","'Shot weakened by the ward (gold)', (420, 730, 650, 945)")
rep("end = (p1[0] + 84, p1[1] - 44)","end = (p1[0] + 78, p1[1] - 52)")
rep("        ram_coin(lay, q[0], q[1], k * 1.25)","        ram_coin(lay, q[0], q[1], k * 1.6)")
rep("lay.glow(lambda g: g.circle(q[0], q[1], 14 * k, fill=CYAN + (255,)), blur=5, op=0.45)","lay.glow(lambda g: g.circle(q[0], q[1], 22 * k, fill=CYAN + (255,)), blur=6, op=0.55)")
rep("lay.glow(lambda g: g.poly(ribbon(pts, lambda k: 0.5 + 7 * k), fill=CYAN + (255,)), blur=4, op=0.55)\n            lay.poly(ribbon(pts, lambda k: 0.3 + 4.5 * k), fill=(200, 246, 255, 255), op=0.8)",
    "lay.glow(lambda g: g.poly(ribbon(pts, lambda k: 0.5 + 11 * k), fill=CYAN + (255,)), blur=5, op=0.6)\n            lay.poly(ribbon(pts, lambda k: 0.3 + 7 * k), fill=(200, 246, 255, 255), outline=INK, w=1.2, op=0.9)")
rep("'Trigger-kill refund, +1 RAM', (400, 470, 1290, 815)","'Trigger-kill refund, +1 RAM', (410, 480, 1280, 800)")
rep("(400, 'coin flies, echo trail')","(400, 'coin flies, ribbon trail')")
rep("(420, 'flight on one curve (echo trail)')","(420, 'flight on one curve, ribbon trail')")
rep("'Nothing gets through (arc check)', (790, 170, 1010, 640)","'Nothing gets through (arc check)', (790, 175, 1010, 570)")
rep("""        p = math.sin(math.pi * seg(t, 0, 220))
        lay.line(ADJ_CELL + [ADJ_CELL[0]], GOLD, 3.2, op=p, key=1.0)""","""        p = math.sin(math.pi * seg(t, 0, 220))
        lay.poly(ADJ_CELL, fill=GOLD + (255,), op=0.22 * p)
        lay.line(ADJ_CELL + [ADJ_CELL[0]], (255, 236, 150), 4.4, op=p, key=1.4)""")
open(p,'w').write(s)
