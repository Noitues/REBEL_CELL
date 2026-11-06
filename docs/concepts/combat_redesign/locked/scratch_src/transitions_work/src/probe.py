import numpy as np
Z = np.load('D:/rc_scratch/combat_redesign/locked/transitions_work/layers/neutral_p1.npz')
for k in Z.files:
    a = Z[k]
    print(k, a.shape, 'tickets', int((a[20:90, 20:300, 3] > 128).sum()) if a.shape[2] == 4 else '-', 'nameplate', int((a[960:1060, 30:250, 3] > 128).sum()) if a.shape[2] == 4 and a.shape[0] >= 1060 else '-')
