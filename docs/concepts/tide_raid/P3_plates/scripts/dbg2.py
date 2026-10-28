import p1lib as L
w = L.load_world()
for sid in ('t1_a','t1_b','t1_c','t1_d','t2_breach','t2_intel','t2_virus'):
    s = w.sites[sid]; print(sid, s['tier'], [round(float(v)) for v in s['B']], round(float(s['B'][1]-{1:27,2:35,3:44}[s['tier']]*3.73)))
