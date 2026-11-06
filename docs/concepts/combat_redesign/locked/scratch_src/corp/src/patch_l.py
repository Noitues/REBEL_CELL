p = 'D:/rc_scratch/combat_polish/E7_waves/E10/src/e10lib.py'
t = open(p).read()


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:90])
    t = t.replace(old, new)


rep("def unit_mask(f, keep_all=False):", "def unit_mask(f, keep_all=False, only=None, skip=None):")
rep("        if not keep_all and (u['consumed'] or u['trigdead']):\n            continue\n        ri, ro = CB.ring_geom(u['dep'])\n        a0, a1 = span(u)\n        if u['w'] == 6:\n            d.ellipse", "        if not keep_all and (u['consumed'] or u['trigdead']):\n            continue\n        if only is not None and u['id'] not in only:\n            continue\n        if skip is not None and u['id'] in skip:\n            continue\n        ri, ro = CB.ring_geom(u['dep'])\n        a0, a1 = span(u)\n        if u['w'] == 6:\n            d.ellipse")
rep("def grade_units(board, f, keep_all=False):", "def grade_units(board, f, keep_all=False, dim_ids=None, dim_k=0.5):")
rep("    a[..., :3] = rgb * (1 - mk) + g * mk\n    return", "    a[..., :3] = rgb * (1 - mk) + g * mk\n    if dim_ids:\n        md = (_np.asarray(unit_mask(f, keep_all, only=set(dim_ids)).filter(_F.GaussianBlur(0.8)), _np.float32) / 255.0)[..., None]\n        a[..., :3] = a[..., :3] * (1 - md * (1 - dim_k))\n    return")
open(p, 'w').write(t)
p = 'D:/rc_scratch/combat_polish/E7_waves/E10/src/build10.py'
t = open(p).read()
rep("    bg.alpha_composite(grade_units(render_board(board_frame(f, keep_all=(beat == 'p2')), CONS), f, keep_all=(beat == 'p2')))",
    "    dim_ids = [u['id'] for u in f['units'] if u['id'] != J['hover']['id']] if beat == 'p2b' else None\n    bg.alpha_composite(grade_units(render_board(board_frame(f, keep_all=(beat == 'p2')), CONS), f, keep_all=(beat == 'p2'), dim_ids=dim_ids))")
rep("        Lh = L2()\n        draw_units(Lh, f, only={hv['id']})\n", "        Lh = L2()\n        draw_units(Lh, f, only={hv['id']})\n        hu_ = [u for u in f['units'] if u['id'] == hv['id']][0]\n        cell_outline(Lh, hu_, col=YEL, w=5)\n")
open(p, 'w').write(t)
