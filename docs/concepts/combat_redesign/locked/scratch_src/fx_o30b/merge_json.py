"""merge_json.py: keep the hand-kept O-30 timings JSON (backup) and replace only the measured flash fields with the fresh ones.
timings_MPST.json: per effect 'flash_check' (and 'strips'); timings_CDHL.json: per effect 'flash'. Timing fields are not touched."""
import json, sys
BAK = 'D:/rc_scratch/combat_redesign/locked/fx_o30b/bak/'
OUT = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/effects/'
which = sys.argv[1:] or ['MPST', 'CDHL']
for nm, keys, cont in (('MPST', ('flash_check', 'strips'), 'effects'), ('CDHL', ('flash',), 'effects')):
    if nm not in which:
        continue
    old = json.load(open(BAK + 'timings_%s.json' % nm))
    new = json.load(open(OUT + 'timings_%s.json' % nm))
    oe = old[cont] if cont else old
    ne = new[cont] if cont else new
    n = 0
    for fid, e in oe.items():
        if not isinstance(e, dict) or fid not in ne:
            continue
        # timing must be unchanged
        for tk in ('total_ms', 'phases', 'keyframes_ms', 'in', 'hold', 'out', 'dur', 'keys_ms'):
            if tk in e and tk in ne[fid] and e[tk] != ne[fid][tk]:
                print('TIMING DIFF', nm, fid, tk)
        for k in keys:
            if k in ne[fid]:
                if k == 'flash_check' and isinstance(e.get(k), dict):
                    # keep any extra O-30 fields inside a skin entry, refresh the measured ones
                    for sk, v in ne[fid][k].items():
                        tgt = e[k].setdefault(sk, {})
                        for mode, d in v.items():
                            tgt.setdefault(mode, {}).update(d)
                else:
                    e[k] = ne[fid][k]
                n += 1
    old['o30_pass'] = ('Flash fields re-measured on the O-30 board (new room grade, solid FAR stroke, HUD occluders), '
                       '2026-11-02; timings unchanged.')
    json.dump(old, open(OUT + 'timings_%s.json' % nm, 'w'), indent=1)
    print(nm, 'merged', n)
