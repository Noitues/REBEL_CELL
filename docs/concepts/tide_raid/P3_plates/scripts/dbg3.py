import p1lib as L
w = L.load_world()
for sid, s in w.sites.items():
    print(sid, s['tier'], [round(float(v)) for v in s['B']])
