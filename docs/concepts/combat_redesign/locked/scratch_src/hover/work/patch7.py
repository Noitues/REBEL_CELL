p = 'D:/rc_scratch/combat_redesign/locked/hover/src/hz_core.py'
s = open(p, encoding='utf-8').read()
# ghost arcs -> own class (board element at plan value)
s = s.replace("""        out = alpha_img(Lg.done(), alpha)
        reg0 = len(RA.REG['arcs'])
        if arcs:
            La = L2()
            RA.landing_arcs(La, f_plan, {}, only=set(ids))
            out.alpha_composite(alpha_img(La.done(), alpha))
        rows = RA.REG['arcs'][reg0:]""", """        out = alpha_img(Lg.done(), alpha)
        reg0 = len(RA.REG['arcs'])
        if arcs:
            La = L2()
            RA.landing_arcs(La, f_plan, {}, only=set(ids))
            ga = alpha_img(La.done(), alpha)
            add_mask('arcs', ga, 128)
            GHOST_ARCS.append(ga)
        rows = RA.REG['arcs'][reg0:]""")
s = s.replace("def alpha_img(im, a):", "GHOST_ARCS = []\n\n\ndef alpha_img(im, a):", 1)
old = s[s.index("def compose(bg, lit_mask, ghosts, marks, hand_lay, stick, insets=(), top=()):"):s.index("def collision_report(")]
new = '''Z_ORDER = {}


def compose(bg, lit_mask, ghosts, marks, hand_lay, stick, insets=(), top=()):
    """dim, ghosts, hover marks, then the board's own marks (digits, labels, tags, badges, tickets) put back on top: a hover mark never covers
    game words.  The pixels a mark would have covered before that are counted in Z_ORDER (reported), and kept low by placing marks clear."""
    base = HL.dim_image(bg.convert('RGB'), lit_mask, k=K_DIM, desat=DESAT).convert('RGBA')
    img = base.copy()
    for g in GHOST_ARCS:
        img.alpha_composite(g)
    for g in ghosts:
        img.alpha_composite(g)
        add_mask('ghost', g, 160)
    for m in marks:
        img.alpha_composite(m)
        add_mask('hover', m, 128)
    for t in top:
        img.alpha_composite(t)
        add_mask('hover', t, 128)
    keep = np.zeros((H, W), bool)
    for c in MARKS:
        if c in MASKS and c != 'leader':
            keep |= MASKS[c]
    keep = np.asarray(Image.fromarray((keep * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))) > 0
    Z_ORDER.clear()
    for hk in ('ghost', 'hover'):
        if hk in MASKS:
            Z_ORDER['%s under board marks px' % hk] = int((MASKS[hk] & keep).sum())
            MASKS[hk] = MASKS[hk] & ~keep
    a = np.asarray(img).copy()
    b = np.asarray(base)
    a[keep] = b[keep]
    img = Image.fromarray(a, 'RGBA')
    img.alpha_composite(stick)
    img.alpha_composite(hand_lay)
    MASKS['hand'] = np.asarray(hand_lay.split()[3]) >= 128
    for ins in insets:
        img.alpha_composite(ins)
        add_mask('inset', ins, 128)
    return img.convert('RGB')


'''
s = s.replace(old, new)
s = s.replace("def reset_checks():\n", "def reset_checks():\n    GHOST_ARCS.clear() if 'GHOST_ARCS' in globals() else None\n", 1)
# lift weighting: prefer lifting a little less over sliding into the neighbour
s = s.replace("    for ly in (866, 876, 886, 896, 904):", "    for ly in (866, 874, 882, 890, 898, 906):")
s = s.replace("            if best is not None and dx + 0.6 * (ly - lift0) >= best[0]:", "            if best is not None and dx + 0.15 * (ly - lift0) >= best[0]:")
s = s.replace("                best = (dx + 0.6 * (ly - lift0), dx, ly)", "                best = (dx + 0.15 * (ly - lift0), dx, ly)")
open(p, 'w', encoding='utf-8').write(s)
p = 'D:/rc_scratch/combat_redesign/locked/hover/src/hz_plates.py'
s = open(p, encoding='utf-8').read()
s = s.replace("        r = rmid(u0['dep']) + 10\n        a_from = 60 * u0['s'] + 6", "        r = rmid(u0['dep']) - 15\n        a_from = 60 * u0['s'] + 6")
s = s.replace("               marks=changed, note=note,", "               marks=changed, note=note, z_order=dict(Z.Z_ORDER),")
open(p, 'w', encoding='utf-8').write(s)
print('ok', s.count('z_order'))
