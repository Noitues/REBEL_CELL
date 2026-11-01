import importlib
from render import *
for k, mod in OPTS.items():
    m = importlib.import_module(mod)
    for nm, fn, n, dur in (('t5', m.t5, N5, 1.2), ('t6', m.t6, N6, 0.8)):
        L = np.array(luma_series([to_pil(fn(i * dur / (n - 1))) for i in range(n)])); d = np.diff(L)
        sig = [int(np.sign(x)) for x in d if abs(x) > 0.004]
        rev = sum(1 for a, b in zip(sig, sig[1:]) if a != b)
        print(k, nm, 'sign reversals (>0.4% steps):', rev, 'steps', np.round(d, 3).tolist())
