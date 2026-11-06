s = open('dump9.py').read()
s = s.replace("SEED, TURN = 4, 2", "SEED, TURN = 9, 2")
s = s.replace("A('planner best line: Trigger Worm, Nudge -1, Brace slice 0, soak slice 1', (HERO, HERO_END), ([('Trigger', 3), ('Nudge', -1), ('Brace', 0)], (1,)))\nA('planner best line takes 0 HP', top['taken'], 0)",
              "A('planner best line: Trigger Payload, Spin2 +2, Trigger Packet, Brace slice 5, soak slice 4', (HERO, HERO_END), ([('Trigger', 5), ('Spin2', 2), ('Trigger', 3), ('Brace', 5)], (4,)))\nA('planner best line takes 1 HP', top['taken'], 1)")
s = s.replace("LOG.append('NOTE  an equal-score tie (Hold added, costs 0 RAM / 0 Trace) exists; the shown line is the first in the planner order: %s' % [P.plan_of(o) for o in outs[1:2]])\n", "")
i0 = s.index("OUTJ['trig_hero'] = trig_entries(3)")
i1 = s.index("A('hero line planner score vs the others'")
new = '''_st = cl(st0)
TRIGS = []
for a in HERO:
    if a[0] == 'Trigger':
        d0_, s0_, u_ = S.find_unit(_st, a[1])
        TRIGS.append(dict(uid=a[1], dep=d0_, s=u_['s'], w=u_['w'], kind=u_['kind'], hit=S.unit_hit(u_), entries=[list(e) for e in S.trigger_preview(_st, a[1])]))
    S.apply(_st, a)
OUTJ['trigs'] = TRIGS
_flat = [e for t in TRIGS for e in t['entries']]
_tl = [e for e in f2['tlog']]
A('Trigger previews == the resolve (every entry, in order)', [(e[0], e[1]) for e in _flat], [('unit' if e[0] == 'trig_unit' else 'tower', e[1]) for e in _tl])
A('Triggers hit units (second Trigger preview taken after the first resolved)', [sum(1 for e in t['entries'] if e[0] == 'unit') for t in TRIGS], [sum(1 for e in _flat[:2] if e[0] == 'unit'), sum(1 for e in _flat[2:] if e[0] == 'unit')])
'''
s = s[:i0] + new + s[i1:]
s = s.replace("A('hero line takes 0, trigger-only line takes more, brace-only line takes more', (pv2['taken'], pv2t['taken'] > 0, pv2b['taken'] > 0), (0, True, True))",
              "A('hero line takes 1; trigger-only takes more HP; brace-only takes 0 HP but breaks more slice pips', (pv2['taken'], pv2t['taken'] > 1, pv2b['taken'], pv2b['slost'] > pv2['slost']), (1, True, 0, True))")
# chain
j0 = s.index("def make_chain():")
j1 = s.index("f2['chain'] = make_chain()")
chain = '''def make_chain():
    f = f2
    eq = f['pv']['eq']
    tl = f['tlog']
    hits_ = [e for e in f['log'] if e[0] == 'hit']
    fires_ = [e for e in f['log'] if e[0] == 'fire' and e[3] is not None]
    n1 = len(TRIGS[0]['entries'])
    pips1 = sum(e[5] for e in tl[:n1] if e[0] == 'trig_unit')
    pips2 = sum(e[5] for e in tl[n1:] if e[0] == 'trig_unit')
    c = []
    c.append(dict(name='TRIGGER', glyph='C_TRIG', col=[255, 226, 0], pips=[['yel', pips1], ['txt', TRIGS[0]['kind']]]))
    c.append(dict(name='SPIN +2', glyph='PI_SPIN_CW', col=[92, 225, 255], pips=[['rider', 1], ['txt', 'rider']]))
    c.append(dict(name='TRIGGER', glyph='C_TRIG', col=[255, 226, 0], pips=[['yel', pips2], ['txt', TRIGS[1]['kind']]]))
    c.append(dict(name='BRACE', glyph='C_BRACE', col=[255, 244, 214], pips=[['txt', 'one slice']]))
    c.append(dict(name='GUNS', glyph='C_STRIKE', col=[92, 225, 255], pips=[['cyan', len(fires_)], ['txt', 'shots']]))
    c.append(dict(name='LANDS', glyph='X_SKULL', col=[255, 68, 51], pips=[['raw', sum(e[4] for e in hits_)], ['txt', 'brace -%d' % eq['braced']], ['txt', 'rider -%d' % eq['rider']]]))
    c.append(dict(name='BILL', glyph='X_HP', col=[123, 224, 123], pips=[['through', eq['through']], ['soak', eq['soaked']], ['absorb', eq['absorbed']]]))
    c.append(dict(name='RINGS STEP', glyph='C_PULL', col=[255, 140, 26], pips=[['txt', 'W4 enters']]))
    return c


'''
s = s[:j0] + chain + s[j1:]
s = s.replace("hv_id = 5", "hv_id = 6")
open('dump9.py', 'w').write(s)
