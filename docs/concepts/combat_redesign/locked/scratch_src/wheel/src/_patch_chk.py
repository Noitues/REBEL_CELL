p = 'checks_asm.py'
s = open(p, encoding='utf-8').read()
helper = '''
# O2: label boxes of the hold cells (angle range of the HOLD text + glyph disc, radial band B0-1 .. B1+1); the spoke continuity metric is measured outside them
def _label_boxes():
    sch = A.J['f1']['schedule']
    cum = 0; out = []
    for v in sch:
        if v == 0:
            out.append((cum + 4.0, cum + 40.0)); cum += 40
        else:
            cum += 60 * v
    return out
LABELS = _label_boxes()
def in_label(k, r):
    a = (30 + 60 * k) % 360
    return r >= 357.4 and r <= 385.0 and any(lo <= a <= hi for lo, hi in LABELS)
'''
s = s.replace("# ---- 3. spoke continuity\n", "# ---- 3. spoke continuity\n" + helper, 1)
s = s.replace('''        for r in np.arange(lo, hi + 0.01, 0.5):
            for off in (-3.0, 0.0, 3.0):''', '''        for r in np.arange(lo, hi + 0.01, 0.5):
            if in_label(k, r):
                continue
            for off in (-3.0, 0.0, 3.0):''')
s = s.replace("ws = [run_w(C[0] + r * t[0], C[1] + r * t[1], nrm[0], nrm[1]) for r in np.arange(lo, hi + 0.01, 0.5)]", "ws = [run_w(C[0] + r * t[0], C[1] + r * t[1], nrm[0], nrm[1]) for r in np.arange(lo, hi + 0.01, 0.5) if not in_label(k, r)]")
s = s.replace("min_run=round(min(ws), 1)", "min_run=round(min(ws), 1) if ws else None")
open(p, 'w', encoding='utf-8').write(s)
