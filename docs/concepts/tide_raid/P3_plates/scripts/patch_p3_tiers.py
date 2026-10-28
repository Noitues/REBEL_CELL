s = open('p1_final.py').read()
s = s.replace("""    for sid, tier in p1_beats.TIERS_AT:
        tile(cv, w, sid, tier, None, off=(0, -56), r=44, tag='tiers')""", """    OFF = {'t1_a': (-46, -30), 't1_b': (30, -52), 't1_c': (-34, -48), 't1_d': (0, -56), 't2_breach': (0, -56)}
    for sid, tier in p1_beats.TIERS_AT:
        tile(cv, w, sid, tier, None, off=OFF[sid], r=44, tag='tiers')""")
open('p1_final.py', 'w').write(s)
t = open('p2_post.py').read()
a = t.index("    y0 = 380")
b = t.index("    out = out.crop(")
new = '''    y0 = 380
    import json as _j
    tl = {e['site']: e for e in _j.load(open(OUT + 'tile_distances_tiers.json'))}
    for i, (sid, name) in enumerate(tiers):
        b = w.sites[sid]['B'] / 6.0
        c = np.array(tl[sid]['centre']) / 6.0
        cx = (b[0] + c[0]) / 2
        box = (int(cx - 24), int(c[1] - 10), int(cx + 24), int(b[1] + 8))
        cr = g320.crop(box)
        sc = 4.6
        cc = cr.resize((int(cr.width * sc), int(cr.height * sc)), Image.NEAREST).convert('RGB')
        out.paste(cc.crop((0, 0, 228, min(cc.height, 300))), (6 + i * 252, y0))
        d.text((10 + i * 252, y0 + 304), name, fill=(127, 239, 255), font=font(16))
'''
t = t[:a] + new + t[b:]
t = t.replace("out = Image.new('RGB', (5 * 252 + 12, 700), (8, 6, 20))", "out = Image.new('RGB', (5 * 252 + 12, 760), (8, 6, 20))")
t = t.replace("out = out.crop((0, 0, out.width, y0 + 272))", "out = out.crop((0, 0, out.width, y0 + 332))")
open('p2_post.py', 'w').write(t)
