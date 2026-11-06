"""fx_table.py: print the published effect registry (title, total, phase names, reduce note, layer) from the two timings files,
for the VISUAL_PLAN G rewrite.  Reads only; writes nothing.  usage: python fx_table.py"""
import json

FX = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/effects/'
M = json.load(open(FX + 'timings_MPST.json', encoding='utf-8'))
C = json.load(open(FX + 'timings_CDHL.json', encoding='utf-8'))

print('== MPST')
for k, e in M['effects'].items():
    ph = ' | '.join('%s %d-%d' % (p['name'], p['start_ms'], p['end_ms']) for p in e.get('phases', []))
    print(k, e.get('family'), e.get('total_ms'), '::', e.get('title'))
    print('   phases:', ph)
    print('   reduce:', e.get('reduce_motion', '')[:220])
print('== CDHL top keys', list(C.keys())[:30])
eff = C.get('effects', C)
for k, e in eff.items():
    if not isinstance(e, dict) or not k.startswith('fx_'):
        continue
    keys = list(e.keys())
    ph = e.get('phases') or []
    phs = ' | '.join('%s %s-%s' % (p.get('name'), p.get('start_ms', p.get('t0')), p.get('end_ms', p.get('t1'))) for p in ph if isinstance(p, dict))
    print(k, e.get('family'), e.get('total_ms'), '::', (e.get('title') or e.get('still') or '')[:200])
    print('   keys:', keys[:25])
    print('   phases:', phs[:400])
    for f in ('still', 'style_must_keep', 'reduce_motion', 'reduce', 'layer'):
        if f in e:
            print('   %s: %s' % (f, str(e[f])[:260]))
