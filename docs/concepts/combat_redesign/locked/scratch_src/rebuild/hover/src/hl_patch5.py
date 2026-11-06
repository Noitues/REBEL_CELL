p = 'hv_comp.py'
s = open(p, encoding='utf-8').read()
old_a = s.index("def _integral(mask):")
old_b = s.index("_cross = {}")
new = '''def _integral(mask):
    """the integral image of mask over its own bbox window (most masks here are a few small polygons): (S, x0, y0, x1, y1)"""
    rows = np.nonzero(mask.any(1))[0]
    if not len(rows):
        return (None, 0, 0, 0, 0)
    cols = np.nonzero(mask.any(0))[0]
    y0, y1, x0, x1 = int(rows[0]), int(rows[-1]) + 1, int(cols[0]), int(cols[-1]) + 1
    S = np.zeros((y1 - y0 + 1, x1 - x0 + 1), np.int32)
    S[1:, 1:] = mask[y0:y1, x0:x1].astype(np.int32).cumsum(0).cumsum(1)
    return (S, x0, y0, x1, y1)


def _box_sum(Si, x0, y0, x1, y1):
    S, wx0, wy0, wx1, wy1 = Si
    if S is None:
        return 0
    x0, y0, x1, y1 = max(wx0, x0), max(wy0, y0), min(wx1, x1), min(wy1, y1)
    if x1 <= x0 or y1 <= y0:
        return 0
    x0, x1, y0, y1 = x0 - wx0, x1 - wx0, y0 - wy0, y1 - wy0
    return int(S[y1, x1] - S[y0, x1] - S[y1, x0] + S[y0, x0])


'''
s = s[:old_a] + new + s[old_b:]
open(p, 'w', encoding='utf-8').write(s)
print('ok')
