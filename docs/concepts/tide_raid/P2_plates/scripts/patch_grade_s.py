s = open('p2_grade.py').read()
s = s.replace("W, H = 1920, 1080\n", "W, H = C.W, C.H\nS = C.S\n", 1)
s = s.replace("green = ndi.binary_dilation(ndi.binary_opening(green, iterations=1), iterations=2)\n    park = ndi.gaussian_filter(green.astype(np.float32), 6) > .25",
              "green = ndi.binary_dilation(ndi.binary_opening(green, iterations=S), iterations=2 * S)\n    park = C.blur(green.astype(np.float32), 6) > .25")
s = s.replace("z = np.load(L.WORK + 'recon15.npz')", "z = np.load(L.WORK + C.REC)")
s = s.replace("loc = lum - ndi.gaussian_filter(lum, 5)", "loc = lum - C.blur(lum, 5)")
s = s.replace("wmask = ndi.gaussian_filter((idm == 7).astype(np.float32), 2.5)", "wmask = C.blur((idm == 7).astype(np.float32), 2.5)")
s = s.replace("yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)\n    sky = np.array([0.006, 0.05, 0.085], np.float32) * (1.2 - yy[..., None] / 600)\n    streak = (C.noise2(5, 24) > .6) * np.exp(-((yy - 200) / 300) ** 2) * 0.012",
              "yy, xx = (np.mgrid[0:H, 0:W].astype(np.float32) / S)\n    sky = np.array([0.006, 0.05, 0.085], np.float32) * (1.2 - yy[..., None] / 600)\n    streak = (C.noise2(5, 24) > .6) * np.exp(-((yy - 200) / 300) ** 2) * 0.012")
s = s.replace("""    R = np.zeros_like(E)
    for y in range(1, H):
        R[y] = np.maximum(E[y] * 0.6, R[y - 1] * decay)
    R = np.stack([ndi.gaussian_filter(R[..., i], (1.2, sx)) for i in range(3)], -1)
    rip = 0.55 + 0.9 * ndi.gaussian_filter(np.random.RandomState(4).rand(H, W).astype(np.float32), (0.6, 5))""", """    R = np.zeros_like(E)
    dec = decay ** (1.0 / S)
    for y in range(1, H):
        R[y] = np.maximum(E[y] * 0.6, R[y - 1] * dec)
    R = np.stack([ndi.gaussian_filter(R[..., i], (1.2 * S, sx * S)) for i in range(3)], -1)
    rn = np.random.RandomState(4).rand(1080, 1920).astype(np.float32)
    if S > 1:
        rn = ndi.zoom(rn, S, order=1)
    rip = 0.55 + 0.9 * ndi.gaussian_filter(rn, (0.6 * S, 5 * S))""")
open('p2_grade.py', 'w').write(s)
print('ok')
