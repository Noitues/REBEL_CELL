import re
s = open('p1_comp.py').read()
s = s.replace("W, H = 1920, 1080\n", "S = int(os.environ.get('P2_S', '1'))          # render scale: 1 = 1920x1080 plates, 2 = native 3840x2160 (true-2x crops)\nW, H = 1920 * S, 1080 * S\nDEP = 'depth15/' if S == 1 else 'depth30/'\nREC = 'recon15.npz' if S == 1 else 'recon30.npz'\n", 1)
s = s.replace("Image.open(WORK + 'depth15/window_nonet.png')", "Image.open(WORK + DEP + 'window_nonet.png')")
s = s.replace("np.load(WORK + 'recon15.npz')", "np.load(WORK + REC)")
s = s.replace("""def blur(a, s):
    if a.ndim == 3:
        return np.stack([ndi.gaussian_filter(a[..., i], s, mode='nearest') for i in range(a.shape[2])], -1)
    return ndi.gaussian_filter(a, s, mode='nearest')""", """def blur(a, s):
    \"\"\"gaussian blur; sigma s is in 1920-frame px (scaled by S).\"\"\"
    s = tuple(v * S for v in s) if isinstance(s, (tuple, list)) else s * S
    if a.ndim == 3:
        return np.stack([ndi.gaussian_filter(a[..., i], s, mode='nearest') for i in range(a.shape[2])], -1)
    return ndi.gaussian_filter(a, s, mode='nearest')""")
s = s.replace("""    g = rng.rand(shape[0] // sc + 3, shape[1] // sc + 3).astype(np.float32)
    z = ndi.zoom(g, sc, order=3)[:shape[0], :shape[1]]""", """    g = rng.rand((shape[0] // S) // sc + 3, (shape[1] // S) // sc + 3).astype(np.float32)     # same random grid at every S
    z = ndi.zoom(g, sc * S, order=3)[:shape[0], :shape[1]]""")
s = s.replace("""    for p in polys_px:
        d.line([tuple(q) for q in p], fill=255, width=3)""", """    for p in polys_px:
        d.line([(q[0] * S, q[1] * S) for q in p], fill=255, width=3 * S)""")
s = s.replace("""    im = Image.new('L', (W * 2, H * 2), 0)
    d = ImageDraw.Draw(im)
    for _ in range(density):
        x = rng.randint(0, W * 2); y = rng.randint(0, H * 2); ln = rng.randint(*length) * 2
        d.line([(x, y), (x - ln * slope, y + ln)], fill=int(rng.randint(60, 220)), width=1 + int(rng.rand() < .3))""", """    im = Image.new('L', (W * 2, H * 2), 0)
    d = ImageDraw.Draw(im)
    for _ in range(density):
        x = rng.randint(0, 1920 * 2) * S; y = rng.randint(0, 1080 * 2) * S; ln = rng.randint(*length) * 2 * S
        d.line([(x, y), (x - ln * slope, y + ln)], fill=int(rng.randint(60, 220)), width=(1 + int(rng.rand() < .3)) * S)""")
s = s.replace("a = ndi.gaussian_filter(emis[..., c], (sy, sx), mode='nearest')", "a = ndi.gaussian_filter(emis[..., c], (sy * S, sx * S), mode='nearest')")
s = s.replace("out[..., c] = ndi.gaussian_filter(emis[..., c], (sy, sx), mode='nearest')", "out[..., c] = ndi.gaussian_filter(emis[..., c], (sy * S, sx * S), mode='nearest')")
open('p1_comp.py', 'w').write(s)
print('patched')
