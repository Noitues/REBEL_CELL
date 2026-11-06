import sys, os, time, json
sys.dont_write_bytecode = True
from a_render import *
from a_opts import ELEMS
OUTD = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/r1/actions/'
CR = OUTD + 'crops/'
os.makedirs(CR, exist_ok=True)
ids = sys.argv[1:]
_cache = {}
def get(beat, sel, tgt, idle):
    k = (beat, json.dumps(sel, sort_keys=True), tgt, idle)
    if k not in _cache:
        if len(_cache) > 6:
            _cache.clear()
        _cache[k] = render(beat, sel, tgt=tgt, idle=idle)
    return _cache[k]
for el in ELEMS:
    if ids and el['id'] not in ids:
        continue
    t = time.time()
    for opt in ['cur', 'A', 'B', 'C']:
        sel0 = el['keys'](opt)
        for vi, v in enumerate(el['views']):
            beat, cx, cy, hw, hh, sc, ex = v
            sel = dict(sel0)
            if 'only' in ex and opt not in ex['only']:
                ex = dict(ex); ex.pop('sel', None)
            sel.update(ex.get('sel', {}))
            reg = ex.get('reg', {}).get(opt)
            if reg:
                cx, cy, hw, hh = reg
            tgt = ex.get('tgt') if opt != 'cur' else None
            idle = (4, opt) if (el.get('idle') and opt != 'cur') else None
            im = get(beat, sel, tgt, idle)
            c = crop2(im, (int(cx - hw), int(cy - hh), int(cx + hw), int(cy + hh)), sc)
            c.save(CR + '%s__%s__v%d.png' % (el['id'], opt, vi))
    print(el['id'], round(time.time() - t, 1), flush=True)
