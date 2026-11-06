import mp_eff as E
import numpy as np
m = E.cmask('neutral', 'p1', 'tickets')
col = m.any(0)
runs = []
x = 0
while x < len(col):
    if col[x]:
        x0 = x
        while x < len(col) and col[x]:
            x += 1
        runs.append((x0, x))
    x += 1
for a, b in runs:
    ys = np.nonzero(m[:, a:b].any(1))[0]
    print(a, b, ys.min(), ys.max() + 1, int(m[:, a:b].sum()))
