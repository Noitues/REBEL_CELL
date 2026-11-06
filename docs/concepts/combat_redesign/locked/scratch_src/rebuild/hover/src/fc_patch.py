p = 'hv_comp.py'
s = open(p, encoding='utf-8').read()
s = s.replace("""    m = np.asarray(T_.done().split()[3]) >= 96
    FOCUS_MASK['m'] = FOCUS_MASK.get('m', np.zeros((H, W), bool)) | m
    return r
""", """    m = np.asarray(T_.done().split()[3]) >= 96
    FOCUS_MASK['m'] = FOCUS_MASK.get('m', np.zeros((H, W), bool)) | m
    FOCUS_CALLS.append(dict(fn=getattr(fn, '__name__', '?'), thick=bool(a[-1]) if a and isinstance(a[-1], bool) else bool(k.get('thick')), m=m))
    return r


FOCUS_CALLS = []
""", 1)
s = s.replace("""    FOCUS_MASK.clear()
    V.FIT_LOG.clear()""", """    FOCUS_MASK.clear()
    del FOCUS_CALLS[:]
    V.FIT_LOG.clear()""", 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok', s.count('FOCUS_CALLS'))
