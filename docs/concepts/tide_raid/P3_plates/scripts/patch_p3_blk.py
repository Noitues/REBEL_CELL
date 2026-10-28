s = open('p2_tex.py').read()
s = s.replace("""    fillc = ink if tier == 'SITES_LOST' else col + (255,)
    d.polygon(octo(b2), fill=fillc)
""", """    # P3 value ladder on the block: UNTOUCHED hollow | HOLDS filled bright | DAMAGED half-filled | BREACHED dark red | SITES LOST ink
    fillc = {'SITES_LOST': ink, 'UNTOUCHED': (0, 0, 0, 0), 'BREACHED': (118, 16, 28, 255)}.get(tier, col + (255,))
    d.polygon(octo(b2), fill=fillc)
    if tier == 'DAMAGED':
        d.rectangle([W_ / 2, b2 + 1, W_ - b2 - 1, H_ - b2 - 1], fill=(0, 0, 0, 0))
""")
s = s.replace("""    pc = np.array(ink[:3] if inkpat else col, np.float32)
    arr = np.asarray(im, np.float32)
""", """    pc = np.array(ink[:3] if inkpat else col, np.float32)
    arr = np.asarray(im, np.float32).copy()
    if tier == 'UNTOUCHED':
        pc = np.array(col, np.float32); arr[..., 3] = np.maximum(arr[..., 3], mask * 255)
    if tier == 'BREACHED':
        pc = np.array(col, np.float32)
    if tier == 'DAMAGED':
        mask = mask * (np.arange(W_)[None, :] < W_ / 2)
""")
s = s.replace("""        for i in range(6):
            cx = W_ * (i + .5) / 6
            pd.ellipse([cx - H_ * .12, H_ / 2 - H_ * .12, cx + H_ * .12, H_ / 2 + H_ * .12], fill=255)
        inkpat = True""", """        for i in range(6):
            cx = W_ * (i + .5) / 6
            pd.ellipse([cx - H_ * .12, H_ / 2 - H_ * .12, cx + H_ * .12, H_ / 2 + H_ * .12], fill=255)
        inkpat = False""")
open('p2_tex.py', 'w').write(s)
