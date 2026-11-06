p='D:/rc_scratch/combat_redesign/locked/fx_cdhl/src/fxk_lib.py'
s=open(p).read()
a=s.index("        waves = []\n        for t in range(T):"); b=s.index("        ts = [w[1] for w in waves]")
s=s[:a]+'''        waves = []
        ev = []
        for t in range(T):
            if u[t] > area and (t == 0 or u[t - 1] <= area):
                ev.append((t, 'u'))
            if d[t] > area and (t == 0 or d[t - 1] <= area):
                ev.append((t, 'd'))
        for t, k in sorted(ev):
            if not waves or waves[-1][0] != k:
                waves.append((k, t))
'''+s[b:]
open(p,'w').write(s)
