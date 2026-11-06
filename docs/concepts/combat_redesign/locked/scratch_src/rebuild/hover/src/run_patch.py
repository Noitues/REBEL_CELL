p = 'hv_run.py'
s = open(p, encoding='utf-8').read()
s = s.replace("""    lm = P.STATE.get('mask')
    if lm is not None:
        arrs['lit'] = lm.astype(np.uint8)
    np.savez_compressed(CHK + name + '.npz', **arrs)""", """    lm = P.STATE.get('mask')
    if lm is not None:
        arrs['lit'] = lm.astype(np.uint8)
    hf = P.STATE.get('hud_hero_full')
    if hf is not None:
        arrs['Zf__hud_hero_full'] = np.packbits(hf)
    for i, c in enumerate(K.FOCUS_CALLS):
        arrs['Fc__%03d' % i] = np.packbits(c['m'])
    np.savez_compressed(CHK + name + '.npz', **arrs)


def save_geometry(name):
    \"\"\"rb_capture geometry of the board frame (cell polygons, states, token discs) and the skin's empty-cell probe, for check a\"\"\"
    f_board = P.STATE.get('f_board')
    if f_board is None:
        return None
    geo = V.RBC.geometry(V.A, f_board, 'p1', P.STATE.get('hover_unit'))
    probe = V.RBC.empty_probe(V.R, V.A, f_board, 'p1')
    probe.save(CHK + name + '_probe.png')
    return geo""", 1)
s = s.replace("""        img.save(OUT + name + '.png')
        save_masks(name)""", """        img.save(OUT + name + '.png')
        save_masks(name)
        try:
            rep['geometry'] = save_geometry(name)
        except Exception:
            traceback.print_exc()
            rep['geometry'] = None
        rep['focus_calls'] = [dict(i=i, fn=c['fn'], thick=c['thick']) for i, c in enumerate(K.FOCUS_CALLS)]""", 1)
s = s.replace("""        rep['dash_calls'] = rep['snap'].get('dash')
        rep['dot_calls'] = rep['snap'].get('dot')
""", "", 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
