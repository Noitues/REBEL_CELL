s = open('p1_bl.py').read()
s = s.replace("        from scipy import ndimage as ndi\n        arr = np.stack([ndi.zoom(arr[..., c], (RES[1] / ih, RES[0] / iw), order=1) for c in range(4)], -1)",
"""        def lin_up(a, n, axis):
            src = (np.arange(n) + 0.5) * (a.shape[axis] / n) - 0.5
            i0 = np.clip(np.floor(src).astype(int), 0, a.shape[axis] - 1); i1 = np.clip(i0 + 1, 0, a.shape[axis] - 1)
            t = (src - np.floor(src)).astype(np.float32)
            sh = [1, 1, 1]; sh[axis] = n
            return np.take(a, i0, axis=axis) * (1 - t.reshape(sh)) + np.take(a, i1, axis=axis) * t.reshape(sh)
        arr = lin_up(lin_up(arr.astype(np.float32), RES[1], 0), RES[0], 1)""")
open('p1_bl.py', 'w').write(s)
print('ok')
