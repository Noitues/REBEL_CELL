"""fx_dump: compact per-effect dump of effects/timings_CDHL.json and timings_MPST.json (exploration only).
usage: python fx_dump.py"""
import json

E = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/effects/'


def main():
    a = json.load(open(E + 'timings_CDHL.json', encoding='utf-8'))
    b = json.load(open(E + 'timings_MPST.json', encoding='utf-8'))
    print('CDHL keys', list(a.keys()))
    print('MPST keys', list(b.keys()))
    for eid, e in a['effects'].items():
        fl = e.get('flash', {})
        mx = {k: (v.get('max_flashes_per_s_footprint'), v.get('max_flashes_per_s_crop')) for k, v in fl.items()}
        print('CDHL', eid, e['family'], e.get('tier'), e.get('kind'), e['total_ms'], 'in/hold/out', e.get('in_ms'), e.get('hold_ms'), e.get('out_ms'),
              'ph', {k: v for k, v in e['phases'].items()}, 'skins', e.get('skins'), 'layer', e.get('layer'), 'flash', mx,
              'extra keys', sorted(set(e.keys()) - {'family', 'title', 'variant_of', 'tier', 'kind', 'scope', 'skins', 'total_ms', 'in_ms', 'hold_ms', 'out_ms',
                                                  'easing_summary', 'easing', 'phases', 'keyframes', 'reduce_motion', 'source', 'board_crop', 'base', 'layer',
                                                  'measured', 'flash'}))
    for eid, e in b['effects'].items():
        fc = e.get('flash_check', {})
        mx = {k: (v.get('full', {}).get('max_flashes_per_s'), v.get('reduce', {}).get('max_flashes_per_s')) for k, v in fc.items()}
        print('MPST', eid, e['family'], e.get('tier'), e['total_ms'], 'reduce', e.get('reduce_total_ms'),
              'ph', [(p['name'][:30], p['start_ms'], p['end_ms'], p.get('easing')) for p in e['phases']],
              'rph', [(p['name'][:20], p['start_ms'], p['end_ms'], p.get('easing')) for p in e.get('reduce_phases', [])],
              'skins', e.get('skins'), 'flash', mx, 'keys', sorted(e.keys()))
    rb = b['resolve_beat_e10']
    print('BEAT', rb['total_ms'], rb['limit_ms'], rb['skip_ms'])
    for t in rb['tracks']:
        print('  ', t)
    print('order:', rb['order'])
    print('not_to_ship:', rb['not_to_ship'])
    print('kill check keys', list(rb['kill_colour_check'].keys()))
    for k in ('rebuild_2026_11_03',):
        r = a[k]
        print('CDHL rb keys', list(r.keys()))
        print(json.dumps(r['loudness_order_neutral']['tiers'], indent=0)[:800])


if __name__ == '__main__':
    main()
