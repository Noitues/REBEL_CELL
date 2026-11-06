"""ed_layer.py: one-off edit of layer_check.py: an effect drawn over the whole frame (fx_trace_add, allowed to cross) has no HUD layer of
its own; count every px it changes instead (all of it is on the HUD or the hand)"""
P = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/src/layer_check.py'
s = open(P, encoding='utf-8').read()
a = """            if a is None or a.shape != f.shape[:2]:
                raise SystemExit('no HUD layer captured for %s' % fid)
            op = a >= 250
"""
b = """            if a is None or a.shape != f.shape[:2]:
                if fid != 'fx_trace_add':
                    raise SystemExit('no HUD layer captured for %s' % fid)
                a = np.full(f.shape[:2], 255.0)           # trace_add draws over the HUD (allowed): every px it changes counts
            op = a >= 250
"""
assert s.count(a) == 1
s = s.replace(a, b)
open(P, 'w', encoding='utf-8').write(s)
print('ok')
