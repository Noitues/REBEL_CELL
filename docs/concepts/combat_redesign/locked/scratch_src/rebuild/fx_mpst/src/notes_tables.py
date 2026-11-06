"""notes_tables.py: print the markdown tables for NOTES_MPST.md "2026-11-03 rebuild" from the measured JSON (res_*, loud_order*, layer_*,
beat meters, pstock, guard, out) so the notes carry the measured numbers, not hand-typed ones"""
import sys, os, json
sys.dont_write_bytecode = True
import mp_eff as E
from mp_lib import ME
W = ME + 'work/'
before = json.load(open(W + 'timings_MPST_before_rebuild.json'))['effects']


def res(fid, sk):
    fp = W + 'res_%s_%s.json' % (fid, sk)
    return json.load(open(fp)) if os.path.exists(fp) else None


print('### per effect')
print('| id | fam | total ms (before) | reduce ms | gated loudness neutral / Solace / Meridian | brighter-only (neutral) | flash max per s full / reduce (all skins) | on opaque HUD px (neutral, full / reduce) |')
print('|---|---|---|---|---|---|---|---|')
for fid, s in E.FX.items():
    rs = [res(fid, sk) for sk in ('neutral', 'solace', 'meridian')]
    g = ' / '.join('%.0f' % r['loud']['gated']['peak'] if r else '-' for r in rs)
    fl = max(r['flash']['max_flashes_per_s'] for r in rs if r)
    fr = max(r['flash_reduce']['max_flashes_per_s'] for r in rs if r)
    lc = W + 'layer_%s_neutral.json' % fid
    if os.path.exists(lc):
        l = json.load(open(lc))
        lay = '%d / %d (of %d)' % (l['full']['max_px_on_opaque_hud'], l['reduce']['max_px_on_opaque_hud'], l['full']['opaque_hud_px_in_box']) if l['full']['opaque_hud_px_in_box'] else 'box holds no HUD px'
    else:
        lay = '?'
    print('| %s | %s | %d (%s) | %d | %s | %.0f | %d / %d | %s |' % (fid, s['fam'], s['timing']['total'], before.get(fid, {}).get('total_ms', '-'), max(p[2] for p in s['reduce_phases']), g,
                                                       rs[0]['loud']['av'], fl, fr, lay))
for sk in ('neutral', 'solace', 'meridian'):
    fp = W + ('loud_order.json' if sk == 'neutral' else 'loud_order_%s.json' % sk)
    if not os.path.exists(fp):
        continue
    o = json.load(open(fp))
    print('\n### order', sk, o['line'])
    for c in o['checks']:
        print('  %s min %s %.0f > %s max %s %.0f  margin %.0f  %s' % (c['louder'], c['min_louder'][0], c['min_louder'][1], c['quieter'], c['max_quieter'][0], c['max_quieter'][1], c['margin'], c['pass_']))
    if sk == 'neutral':
        print('| rank | id | fam | kind | loudness | px | at ms | from |')
        print('|---|---|---|---|---|---|---|---|')
        for i, r in enumerate(o['rows']):
            print('| %d | %s | %s | %s | %.0f | %d | %.0f | %s |' % (i + 1, r['id'], r['fam'], r['kind'], r['peak'], r['area_px'], r['t_ms'], r['src']))
for m in ('full', 'red'):
    fp = W + 'beat/meter_%s.json' % m
    if os.path.exists(fp):
        a = json.load(open(fp))
        b = a['beat']
        print('\n### beat', m, 'whole', b['whole']['flashes'], b['whole']['max_flashes_per_s'], 'boxes max', max(v['max_flashes_per_s'] for v in b['boxes'].values()),
              'tiles', {k: v['max_flashes_per_s'] for k, v in b['tiles'].items()}, 'skips max', a['max_flashes_per_s_skips'], {k: v['max_flashes_per_s_any_region'] for k, v in a['skips'].items()})
        for k, v in b['tiles'].items():
            print('   tile', k, v['worst'][:1])
for f in ('pstock.json', 'beat/guard.json', 'beat/out.json'):
    if os.path.exists(W + f):
        d = json.load(open(W + f))
        d.pop('method', None)
        print('\n###', f, json.dumps(d)[:1500])
