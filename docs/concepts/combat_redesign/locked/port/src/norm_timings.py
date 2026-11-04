"""norm_timings (port-2, 2026-11-04): merge the rebuilt effects/timings_CDHL.json and effects/timings_MPST.json (two schemas) into one
flat list for the Godot port (CombatFxTiming resources), with the resolve beat, the loudness order and the layer rule.

Nothing is typed here: every number comes from the two timing files (and, for the O-30 'before' lengths only, the port-1 merge kept in
scratch).  The script asserts the rebuild's rules on the data it writes and stops on any breach:
  - every total, phase end and reduce phase end <= the T2 cap (both files must carry the same cap), no per-effect override;
  - only the effects the CDHL / MPST layer fields mark as allowed draw above the HUD;
  - the resolve beat total < its limit;
  - every ease string maps to a code (no CUSTOM left).
usage: python norm_timings.py <out_json>"""
import json, sys, hashlib, os

SRC = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/effects/'
O30 = 'D:/rc_scratch/combat_redesign/locked/port/work/fx_timings.json'      # the port-1 merge of the O-30 timings (before lengths only)
EASE = {
    'ease-in-out cubic': 'IN_OUT_CUBIC', 'easeinoutcubic': 'IN_OUT_CUBIC', 'eio': 'IN_OUT_CUBIC',
    'ease-out cubic': 'OUT_CUBIC', 'easeoutcubic': 'OUT_CUBIC', 'eout': 'OUT_CUBIC',
    'ease-in cubic': 'IN_CUBIC', 'easeincubic': 'IN_CUBIC', 'ease-in': 'IN_CUBIC',
    'ease-out back': 'OUT_BACK', 'easeoutback': 'OUT_BACK', 'back': 'OUT_BACK', 'strong back': 'OUT_BACK',
    'easeinquad': 'IN_QUAD', 'ease-in quad': 'IN_QUAD', 'linear': 'LINEAR', 'sine': 'IN_OUT_SINE', 'easeinoutsine': 'IN_OUT_SINE',
}
FAMILY_ORDER = 'TMPDHLCS'          # VISUAL_PLAN G play-path order, as the port spec section 12 lists the families
CDHL_COMPARISON_ONLY = 'comparison only'     # the CDHL fx_shield_block title says it is the block-vs-break copy; MPST owns the P family


def ease_code(s):
    if s is None:
        return 'LINEAR'
    t = s.strip().lower()
    if t in ('-', 'hold', 'none', ''):
        return 'HOLD'
    if t.startswith('step'):
        return 'STEP'
    for k in sorted(EASE, key=len, reverse=True):
        if k in t.replace(' ', '') or k in t:
            return EASE[k]
    return 'CUSTOM:' + s


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def worst(vals):
    v = [x for x in vals if x is not None]
    return max(v) if v else None


def cdhl_rows(a):
    rows = []
    for eid, e in a['effects'].items():
        if CDHL_COMPARISON_ONLY in e.get('title', ''):
            continue
        ph = []
        for name, (s, t) in e['phases'].items():
            raw = e.get('easing', {}).get(name)
            ph.append(dict(name=name, start_ms=int(round(s)), end_ms=int(round(t)), ease=ease_code(raw), ease_raw=raw))
        fl = e.get('flash', {})
        full = worst([d.get('max_flashes_per_s_footprint') for k, d in fl.items() if not k.endswith('_reduce')])
        red = worst([d.get('max_flashes_per_s_footprint') for k, d in fl.items() if k.endswith('_reduce')])
        meas = e.get('measured', {})
        rows.append(dict(
            id=eid, family=e['family'], title=e.get('title', ''), kind=e.get('kind'), variant_of=e.get('variant_of'),
            scope=e.get('scope'), skins=e.get('skins', []), total_ms=int(e['total_ms']),
            in_ms=e.get('in_ms'), hold_ms=e.get('hold_ms'), out_ms=e.get('out_ms'), phases=ph,
            reduce_phases=[], reduce_phases_from='text (reduce_motion): CDHL keeps one still per effect',
            reduce_total_ms=None, keyframes_ms=[k['ms'] for k in e.get('keyframes', [])],
            reduce_motion=e.get('reduce_motion', ''), source=e.get('source', ''),
            layer='hud' if 'above the HUD' in e.get('layer', '') else 'board', layer_raw=e.get('layer', ''),
            max_flashes_per_s=full, reduce_max_flashes_per_s=red,
            loud_transient=dict((sk, m.get('loud_peak')) for sk, m in meas.items()),
            settles_ms=worst([m.get('settles_ms') for m in meas.values()]),
            px_on_hud_max=worst([m.get('over_px_on_hud_max') for m in meas.values()]),
            px_hidden_by_hud_max=worst([m.get('under_px_hidden_by_hud_max') for m in meas.values()]),
            in_sequence=e.get('in_sequence'), src_file='effects/timings_CDHL.json'))
    return rows


def mpst_rows(b):
    rows = []
    for eid, e in b['effects'].items():
        ph = [dict(name=p['name'], start_ms=int(p['start_ms']), end_ms=int(p['end_ms']), ease=ease_code(p.get('easing')), ease_raw=p.get('easing'))
              for p in e['phases']]
        rph = [dict(name=p['name'], start_ms=int(p['start_ms']), end_ms=int(p['end_ms']), ease=ease_code(p.get('easing')), ease_raw=p.get('easing'))
               for p in e.get('reduce_phases', [])]
        fc = e.get('flash_check', {})
        lc = e.get('layer_check_neutral', {})
        rows.append(dict(
            id=eid, family=e['family'], title=e.get('title', ''), kind=e.get('tier'), variant_of=None, scope=None,
            skins=e.get('skins', []), total_ms=int(e['total_ms']), in_ms=None, hold_ms=None, out_ms=None, phases=ph,
            reduce_phases=rph, reduce_phases_from='timings_MPST.json reduce_phases', reduce_total_ms=e.get('reduce_total_ms'),
            keyframes_ms=e.get('keyframes_ms', []), reduce_motion=e.get('reduce_motion', ''), source=e.get('source', ''),
            layer='hud' if e.get('layer', '').startswith('over the HUD') else 'board', layer_raw=e.get('layer', ''),
            max_flashes_per_s=worst([d.get('full', {}).get('max_flashes_per_s') for d in fc.values()]),
            reduce_max_flashes_per_s=worst([d.get('reduce', {}).get('max_flashes_per_s') for d in fc.values()]),
            loud_transient=dict((sk, m.get('gated_peak')) for sk, m in e.get('loudness', {}).items()),
            settles_ms=None,
            px_on_hud_max=worst([lc.get(k, {}).get('max_px_on_opaque_hud') for k in ('full', 'reduce')]),
            px_hidden_by_hud_max=None, in_sequence=None, src_file='effects/timings_MPST.json'))
    return rows


def beat_of(b, ids):
    rb = b['resolve_beat_e10']
    tracks = []
    for t in rb['tracks']:
        nm = t['name']
        eid = 'fx_' + nm if 'fx_' + nm in ids else None
        if eid is None and nm.startswith('kill'):
            eid = 'fx_kill'
        if eid is None and nm.startswith('gun_'):
            eid = 'fx_gun_hit'
        tracks.append(dict(name=nm, effect=eid, start_ms=t['start_ms'], dur_ms=t['dur_ms'], end_ms=t['start_ms'] + t['dur_ms'],
                           family=t['family'], what=t['what']))
    ff, fr = rb['flash_full'], rb['flash_reduce']
    return dict(skin=rb['skin'], total_ms=rb['total_ms'], limit_ms=rb['limit_ms'], skip_ms=rb['skip_ms'], skip=rb['skip'], order=rb['order'],
                not_to_ship=rb['not_to_ship'], tracks=tracks,
                flash=dict(full=dict(whole_frame=ff['whole_frame']['max_flashes_per_s'], track_boxes=ff['track_boxes_max_flashes_per_s'],
                                     tiles={k: v['max_flashes_per_s'] for k, v in ff['tiles'].items()}, beat=ff['max_flashes_per_s_beat'],
                                     skips=ff['max_flashes_per_s_skips'], passes=ff['passes']),
                           reduce=dict(whole_frame=fr['whole_frame']['max_flashes_per_s'], track_boxes=fr['track_boxes_max_flashes_per_s'],
                                       tiles={k: v['max_flashes_per_s'] for k, v in fr['tiles'].items()}, beat=fr['max_flashes_per_s_beat'],
                                       skips=fr['max_flashes_per_s_skips'], passes=fr['passes'])),
                kill_colour=dict((k, v) for k, v in rb['kill_colour_check'].items() if k != 'method'),
                gif=rb.get('gif'), files=rb.get('files'))


def main(out_json):
    fa, fb = SRC + 'timings_CDHL.json', SRC + 'timings_MPST.json'
    a = json.load(open(fa, encoding='utf-8'))
    b = json.load(open(fb, encoding='utf-8'))
    cap_a, cap_b = a['rebuild_2026_11_03']['t2_cap_ms'], b['cap_ms']
    assert cap_a == cap_b, ('the two effect sets disagree on the cap', cap_a, cap_b)
    assert a['rebuild_2026_11_03']['per_effect_overrides'] == [], 'per-effect overrides found'
    rows = cdhl_rows(a) + mpst_rows(b)
    ids = {r['id'] for r in rows}
    assert len(ids) == len(rows), 'duplicate effect id'
    before = {}
    if os.path.exists(O30):
        o = json.load(open(O30, encoding='utf-8'))
        assert o.get('version') == 'port-1', 'the O-30 merge in scratch is not the port-1 file'
        before = {r['id']: r['total_ms'] for r in o['effects']}
    mp_before = {k: e.get('total_ms_before_rebuild') for k, e in b['effects'].items()}
    for r in rows:
        r['total_ms_o30'] = mp_before.get(r['id']) or before.get(r['id'])
        r['tier_vfx'] = 'T2'
        assert r['total_ms'] <= cap_a, (r['id'], 'total over the cap')
        for p in r['phases'] + r['reduce_phases']:
            assert 0 <= p['start_ms'] <= p['end_ms'] <= cap_a, (r['id'], p['name'], 'phase outside the cap')
            assert p['end_ms'] <= max(r['total_ms'], r['reduce_total_ms'] or 0), (r['id'], p['name'], 'phase past the total')
        if r['reduce_total_ms'] is not None:
            assert r['reduce_total_ms'] <= cap_a, (r['id'], 'reduce total over the cap')
        assert (r['max_flashes_per_s'] or 0) <= 3 and (r['reduce_max_flashes_per_s'] or 0) <= 3, (r['id'], 'flash over 3 per s')
    hud = sorted(r['id'] for r in rows if r['layer'] == 'hud')
    allowed_txt = a['rebuild_2026_11_03']['layer']
    for h in hud:
        assert h in allowed_txt, (h, 'draws above the HUD but is not in the allowed list')
    rows.sort(key=lambda r: (FAMILY_ORDER.index(r['family']) if r['family'] in FAMILY_ORDER else 9, r['id']))
    unknown = sorted({p['ease'] for r in rows for p in r['phases'] + r['reduce_phases'] if p['ease'].startswith('CUSTOM')})
    assert not unknown, ('unmapped ease strings', unknown)
    beat = beat_of(b, ids)
    assert beat['total_ms'] < beat['limit_ms'], 'resolve beat over its limit'
    assert max(t['end_ms'] for t in beat['tracks']) <= beat['total_ms'], 'a beat track ends past the beat'
    fam = {}
    for r in rows:
        fam[r['family']] = fam.get(r['family'], 0) + 1
    loud = dict(cdhl={k[len('loudness_order_'):]: v for k, v in a['rebuild_2026_11_03'].items() if k.startswith('loudness_order_')},
                mpst={'neutral' if k == 'loudness_order' else k[len('loudness_order_'):]: dict(line=v['line'], passes=v['pass'], checks=v['checks'])
                      for k, v in b.items() if k.startswith('loudness_order')})
    out = dict(
        version='port-2',
        doc='Merged by port/src/norm_timings.py from effects/timings_CDHL.json and effects/timings_MPST.json (the 2026-11-03 rebuild of the '
            'effects on the gate-1 board). Times in ms at 60 fps on the effect clock. Ease codes map to Godot Tween TRANS / EASE pairs '
            '(GODOT_PORT_SPEC.md 8.1). fx_shield_block appears once: the MPST P-family effect; the CDHL copy is the block-vs-break comparison '
            'only. reduce_phases are data for M/P/S/T; C/D/H/L keep one still per effect, described in reduce_motion.',
        sources={os.path.basename(fa): md5(fa), os.path.basename(fb): md5(fb)},
        cap_ms=cap_a, per_effect_overrides=[], tier_vfx='T2 for every effect (VfxTier T2 outcome, max 0.6 s; REVIEW_RESPONSE 2.11)',
        layer_rule=allowed_txt, hud_layer_effects=hud, fps=b.get('fps'),
        p_stock=a['rebuild_2026_11_03']['p_stock'], loudness_rule=a['rebuild_2026_11_03']['loudness_order_neutral']['rule'],
        loudness_metric=a['rebuild_2026_11_03']['loudness_metric'], loudness_order=loud,
        count=len(rows), families=fam, effects=rows, resolve_beat=beat)
    json.dump(out, open(out_json, 'w', encoding='utf-8'), indent=1)
    print('effects', len(rows), fam, 'hud', hud, 'beat', beat['total_ms'], '/', beat['limit_ms'])


if __name__ == '__main__':
    main(sys.argv[1])
