s = open('p2_post.py').read()
fn = '''

def tier_strip():
    """greyscale 320 px tier strip: the tiers plate at 320 px grey + the five tier marks (ring + tile) cropped from the 320 px image, enlarged x6 (nearest)."""
    f = PL + 'T0_tiers.png'
    if not os.path.exists(f):
        return
    import p1lib as L_
    w = L_.load_world()
    im = Image.open(f).convert('RGB')
    g320 = im.resize((320, 180), Image.LANCZOS).convert('L')
    tiers = [('t1_a', 'UNTOUCHED'), ('t1_b', 'HOLDS'), ('t1_c', 'SITES LOST'), ('t1_d', 'DAMAGED'), ('t2_breach', 'BREACHED')]
    out = Image.new('RGB', (5 * 252 + 12, 190 + 6 * 40 + 70), (8, 6, 20))
    out.paste(g320.resize((640, 360), Image.NEAREST).convert('RGB'), (6, 6))
    d = ImageDraw.Draw(out)
    d.text((660, 20), 'tiers plate, greyscale, 320 px (left, x2)', fill=(160, 170, 200), font=font(16))
    y0 = 380
    for i, (sid, name) in enumerate(tiers):
        b = w.sites[sid]['B'] / 6.0
        cx, cy = b[0], b[1] - 8
        box = (int(cx - 21), int(cy - 20), int(cx + 21), int(cy + 20))
        c = g320.crop(box).resize((252 - 6, 240), Image.NEAREST).convert('RGB')
        out.paste(c, (6 + i * 252, y0))
        d.text((10 + i * 252, y0 + 244), name, fill=(127, 239, 255), font=font(16))
    out = out.crop((0, 0, out.width, y0 + 270))
    out.save(OUT + 'tier_strip_gray_320.png')
    # all seven plates in greyscale at 320
    rows = []
    for nn, name, p2, hot, title in BEATS:
        f2 = PL + '%s_%s.png' % (nn, name)
        if os.path.exists(f2):
            rows.append(Image.open(f2).convert('RGB').resize((320, 180), Image.LANCZOS).convert('L').convert('RGB'))
    if rows:
        st = Image.new('RGB', (len(rows) * 326 + 6, 192), (8, 6, 20))
        for i, r in enumerate(rows):
            st.paste(r, (6 + i * 326, 6))
        st.save(OUT + 'squint/ALL_gray_320.png')
'''
s = s.replace("\n\nif __name__ == '__main__':\n    main()", fn + "\n\nif __name__ == '__main__':\n    main()\n    tier_strip()")
open('p2_post.py', 'w').write(s)
print('ok')
