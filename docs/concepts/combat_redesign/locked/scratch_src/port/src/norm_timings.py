"""norm_timings: merge timings_CDHL.json and timings_MPST.json (two schemas) into one flat list for the Godot port
(CombatFxTiming resources), and print a markdown table for GODOT_PORT_SPEC.md.
usage: python norm_timings.py <out_json> <out_md>"""
import json, sys, re

SRC = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/effects/'
EASE = {
    'ease-in-out cubic': 'IN_OUT_CUBIC', 'easeinoutcubic': 'IN_OUT_CUBIC', 'eio': 'IN_OUT_CUBIC',
    'ease-out cubic': 'OUT_CUBIC', 'easeoutcubic': 'OUT_CUBIC', 'eout': 'OUT_CUBIC',
    'ease-in cubic': 'IN_CUBIC', 'easeincubic': 'IN_CUBIC', 'ease-in': 'IN_CUBIC',
    'ease-out back': 'OUT_BACK', 'easeoutback': 'OUT_BACK', 'back': 'OUT_BACK', 'strong back': 'OUT_BACK',
    'easeinquad': 'IN_QUAD', 'linear': 'LINEAR', 'sine': 'IN_OUT_SINE', 'easeinoutsine': 'IN_OUT_SINE',
}


def ease_code(s):
    if s is None:
        return 'LINEAR'
    t = s.strip().lower()
    if t in ('-', 'hold', 'none'):
        return 'HOLD'
    if t.startswith('step'):
        return 'STEP'
    for k in sorted(EASE, key=len, reverse=True):
        if k in t.replace(' ', '') or k in t:
            return EASE[k]
    return 'CUSTOM:' + s


def flash_max(fl):
    best = 0
    for sk, d in (fl or {}).items():
        if sk.endswith('_reduce'):
            continue
        if isinstance(d, dict):
            if 'max_flashes_per_s_footprint' in d:
                best = max(best, d['max_flashes_per_s_footprint'])
            elif 'full' in d:
                best = max(best, d['full'].get('max_flashes_per_s', 0))
    return best


def flash_reduce(fl):
    best = 0
    for sk, d in (fl or {}).items():
        if sk.endswith('_reduce') and isinstance(d, dict):
            best = max(best, d.get('max_flashes_per_s_footprint', d.get('max_flashes_per_s', 0)))
        elif isinstance(d, dict) and 'reduce' in d:
            best = max(best, d['reduce'].get('max_flashes_per_s', 0))
    return best


def main(out_json, out_md):
    a = json.load(open(SRC + 'timings_CDHL.json', encoding='utf-8'))['effects']
    b = json.load(open(SRC + 'timings_MPST.json', encoding='utf-8'))['effects']
    rows = []
    for eid, e in a.items():
        ph = []
        for name, (s, t) in e['phases'].items():
            ph.append(dict(name=name, start_ms=int(s), end_ms=int(t), ease=ease_code(e.get('easing', {}).get(name)), ease_raw=e.get('easing', {}).get(name)))
        rows.append(dict(id=eid, family=e['family'], title=e.get('title', ''), variant_of=e.get('variant_of'),
                         tier=e.get('tier'), scope=e.get('scope'), skins=e.get('skins', []), total_ms=int(e['total_ms']),
                         in_ms=e.get('in_ms'), hold_ms=e.get('hold_ms'), out_ms=e.get('out_ms'), phases=ph,
                         keyframes_ms=[k['ms'] for k in e.get('keyframes', [])], reduce_motion=e.get('reduce_motion', ''),
                         source=e.get('source', ''), max_flashes_per_s=flash_max(e.get('flash')),
                         reduce_max_flashes_per_s=flash_reduce(e.get('flash')), src_file='timings_CDHL.json'))
    for eid, e in b.items():
        if eid in a:            # fx_shield_block is in both; MPST owns the P family
            rows = [r for r in rows if r['id'] != eid]
        ph = [dict(name=p['name'], start_ms=int(p['start_ms']), end_ms=int(p['end_ms']), ease=ease_code(p.get('easing')), ease_raw=p.get('easing')) for p in e['phases']]
        rows.append(dict(id=eid, family=e['family'], title=e.get('title', ''), variant_of=e.get('variant_of'),
                         tier=None, scope=None, skins=e.get('skins', []), total_ms=int(e['total_ms']),
                         in_ms=None, hold_ms=None, out_ms=None, phases=ph, keyframes_ms=e.get('keyframes_ms', []),
                         reduce_motion=e.get('reduce_motion', ''), source=e.get('source', ''),
                         max_flashes_per_s=flash_max(e.get('flash_check')), reduce_max_flashes_per_s=flash_reduce(e.get('flash_check')),
                         src_file='timings_MPST.json'))
    order = 'MPCDHLST'
    rows.sort(key=lambda r: (order.index(r['family'][0]) if r['family'][0] in order else 9, r['id']))
    unknown = sorted({p['ease'] for r in rows for p in r['phases'] if p['ease'].startswith('CUSTOM')})
    json.dump(dict(version='port-1', doc='Merged from effects/timings_CDHL.json and timings_MPST.json by norm_timings.py. '
                   'Times in ms at 60 fps; phases are [start_ms, end_ms] on the effect clock; ease codes map to Godot Tween '
                   'TRANS/EASE pairs (see GODOT_PORT_SPEC.md section 7). fx_shield_block appears once (MPST owns the P family).',
                   count=len(rows), unknown_ease=unknown, effects=rows), open(out_json, 'w', encoding='utf-8'), indent=1)
    with open(out_md, 'w', encoding='utf-8') as f:
        f.write('| id | fam | total ms | phases (name start-end ease) | reduce motion | flashes/s full / reduce |\n|---|---|---|---|---|---|\n')
        for r in rows:
            ph = '; '.join('%s %d-%d %s' % (re.sub(r'[|]', '/', p['name'])[:34], p['start_ms'], p['end_ms'], p['ease'].replace('CUSTOM:', '~')) for p in r['phases'])
            rm = re.sub(r'[|\n]', ' ', r['reduce_motion'])
            f.write('| `%s` | %s | %d | %s | %s | %s / %s |\n' % (r['id'], r['family'], r['total_ms'], ph, rm, r['max_flashes_per_s'], r['reduce_max_flashes_per_s']))
    print('effects', len(rows), 'unknown ease', unknown)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
