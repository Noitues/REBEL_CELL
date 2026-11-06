p = 'hv_comp.py'
s = open(p, encoding='utf-8').read()
a = s.index("def _mask_cross(m):")
b = s.index("def _shifts(")
new = '''def _mask_cross(m):
    """two rectangles fully inside a card mask (the card's rounded corners and any transparent margin excluded): a hit inside them is a hit.
    (rows over the middle row's span, columns over the middle column's span)"""
    k_ = id(m)
    if k_ not in _cross:
        h, w = m.shape
        boxes = []
        mr = np.nonzero(m[h // 2])[0]
        mc = np.nonzero(m[:, w // 2])[0]
        if len(mr) and len(mc):
            c0, c1 = int(mr[0]), int(mr[-1]) + 1
            r0, r1 = int(mc[0]), int(mc[-1]) + 1
            rows = np.nonzero(m[:, c0:c1].all(1))[0]
            cols = np.nonzero(m[r0:r1, :].all(0))[0]
            if len(rows):
                boxes.append((c0, int(rows[0]), c1, int(rows[-1]) + 1))
            if len(cols):
                boxes.append((int(cols[0]), r0, int(cols[-1]) + 1, r1))
        _cross[k_] = boxes
    return _cross[k_]


def _fast_hit(S, full, m, x0, y0):
    """_hit via the windowed integral image S of full: 0 when the bbox is clear, 1 when a fully covered box of the card holds a pixel, else exact"""
    h, w = m.shape
    if _box_sum(S, x0, y0, x0 + w, y0 + h) == 0:
        return 0
    for bx0, by0, bx1, by1 in _mask_cross(m):
        if _box_sum(S, x0 + bx0, y0 + by0, x0 + bx1, y0 + by1) > 0:
            return 1
    return _hit(full, m, x0, y0)


'''
s = s[:a] + new + s[b:]
open(p, 'w', encoding='utf-8').write(s)
print('ok')
