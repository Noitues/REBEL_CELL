"""o30_json.py: write the O-30 changes into effects/timings_MPST.json, effects/timings_CDHL.json and port/fx_timings.json.
 - fx_shield_block, fx_brace_block: new reduce-motion timing (reduce_phases), re-measured flash numbers on all three skins
 - fx_refund: source line corrected (RAM 2 + 1 = 3)
 - fx_trigger_hit: the in-sequence form (after fx_commit the pencil ignite is not drawn again)
 - port only: resolve_beat_e10, the sequenced beat and its measured flash numbers"""
import json, os, sys
sys.dont_write_bytecode = True
LOCK = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/'
WK = 'D:/rc_scratch/combat_redesign/locked/fx_o30/work/'

RED = {
    'fx_shield_block': dict(
        text='No slam and no sparks: plate, tint, ticks and the two chevrons stopped at the plate edge fade in over 120 ms (linear), hold, and dissolve out over 300 ms (620-920, linear). O-30: the step-4 form (100 ms ease-out in, 160 ms out at 600-760) counted 2 flashes per second against 1 in full motion.',
        phases=[('appear: plate, tint, ticks, stopped chevrons', 0, 120, 'LINEAR', 'linear'), ('hold', 120, 620, 'HOLD', '-'), ('dissolve out', 620, 920, 'LINEAR', 'linear')]),
    'fx_brace_block': dict(
        text='No closing or crumple motion: lane, clamp, bar, the crumpled chevrons and the stamp fade in over 120 ms (linear), hold, then everything but the stamp dissolves out over 300 ms (760-1060, linear); the stamp stays. O-30: the step-4 form (120 ms ease-out in, 160 ms out at 760-920) counted 2 flashes per second against 1 in full motion.',
        phases=[('appear: lane, clamp, bar, crumpled chevrons, stamp', 0, 120, 'LINEAR', 'linear'), ('hold', 120, 760, 'HOLD', '-'), ('dissolve out (stamp stays)', 760, 1060, 'LINEAR', 'linear')]),
}
REFUND_SRC = 'f2: Trigger kills Packet 1 (tlog trig_refund), refund 1 RAM: RAM 2 + 1 = 3 (4 at turn start; Trigger 1 and Brace 1 paid, Twist 0; f2 ram 3). O-30: was "ram 3 + 1", the frames were right (2 lit, slot 3 lights).'
TRIG_SEQ = 'In the resolve beat fx_commit has already burned the pencil route and Xs into paint, so the sequenced fx_trigger_hit draws only the bursts and speed lines (same clock: s3 at 230, s4 at 420); the pencil-yellow ignite plays only when the effect runs without a commit before it (O-30).'


def res(fid, skin):
    return json.load(open(WK + 'res_%s_%s.json' % (fid, skin)))


def mpst():
    p = LOCK + 'effects/timings_MPST.json'
    d = json.load(open(p, encoding='utf-8'))
    for fid, r in RED.items():
        e = d['effects'][fid]
        e['reduce_motion'] = r['text']
        e['reduce_phases'] = [dict(name=n, start_ms=a, end_ms=b, easing=raw) for n, a, b, _, raw in r['phases']]
        for skin in e['skins']:
            q = res(fid, skin)
            fc, fr = q['flash'], q['flash_reduce']
            keep = ('footprint_px', 'frames', 'flashes', 'flash_frames', 'max_flashes_per_s', 'max_area_swing_up', 'max_area_swing_down', 'max_mean_step', 'mean_range', 'passed')
            e['flash_check'][skin] = dict(full={k: fc[k] for k in keep if k in fc}, reduce={k: fr[k] for k in keep if k in fr})
        e['o30'] = 'reduce-motion timing changed and re-measured on all three skins (fx_o30/src/fx_eff.py RED_SHIELD / RED_BRACE)'
    json.dump(d, open(p, 'w', encoding='utf-8'), indent=1)
    print('MPST ok')


def cdhl():
    p = LOCK + 'effects/timings_CDHL.json'
    d = json.load(open(p, encoding='utf-8'))
    E = d['effects']
    get = (lambda k: E[k]) if isinstance(E, dict) else (lambda k: [x for x in E if x.get('id') == k][0])
    get('fx_refund')['source'] = REFUND_SRC
    get('fx_trigger_hit')['in_sequence'] = TRIG_SEQ
    json.dump(d, open(p, 'w', encoding='utf-8'), indent=1)
    print('CDHL ok')


def port():
    p = LOCK + 'port/fx_timings.json'
    d = json.load(open(p, encoding='utf-8'))
    by = {e['id']: e for e in d['effects']}
    for fid, r in RED.items():
        e = by[fid]
        e['reduce_motion'] = r['text']
        e['reduce_phases'] = [dict(name=n, start_ms=a, end_ms=b, ease=code, ease_raw=raw) for n, a, b, code, raw in r['phases']]
        e['reduce_max_flashes_per_s'] = max(res(fid, s)['flash_reduce']['max_flashes_per_s'] for s in e['skins'])
        e['max_flashes_per_s'] = max(res(fid, s)['flash']['max_flashes_per_s'] for s in e['skins'])
    by['fx_refund']['source'] = REFUND_SRC
    by['fx_trigger_hit']['in_sequence'] = TRIG_SEQ
    if os.path.exists(WK + 'meter_full.json'):
        tl = json.load(open(WK + 'timeline.json'))
        segs, meta = tl[:-1], tl[-1]
        mf = json.load(open(WK + 'meter_full.json'))
        mr = json.load(open(WK + 'meter_red.json')) if os.path.exists(WK + 'meter_red.json') else None

        def summ(M):
            return dict(max_flashes_per_s_any_region=M['max_flashes_per_s_any_region'], whole_frame=M['whole']['max_flashes_per_s'],
                        effect_boxes=max(b['max_flashes_per_s'] for b in M['boxes'].values()),
                        tiles_240=M['tiles']['240']['max_flashes_per_s'], tiles_120=M['tiles']['120']['max_flashes_per_s'], tiles_60=M['tiles']['60']['max_flashes_per_s'],
                        worst_tile=M['tiles']['60']['worst'][0] if M['tiles']['60']['worst'] else None, passes=M['passes'])
        d['resolve_beat_e10'] = dict(
            doc='The E10 p3 resolve beat sequenced on the final board (O-30): SEND IT, then the HUD chain order. Each effect starts '
                '100 ms after the previous one ends; the END TURN hand-off (settle) holds 400 ms before RINGS STEP. settle is a sequencer '
                'step (260 ms dissolve: the landed unit and spent gun marks leave ring 0, the old arcs lift off the lanes), not an effect. '
                'Use as the golden sequence for FlashLimiter.stream_is_safe in test_combat_fx_timings.gd.',
            gap_ms=100, gap_after={'settle': 400}, total_ms=meta['total'] - 300,
            steps=[dict(step=s['name'], effect=s['fid'], start_ms=s['start'], dur_ms=s['dur']) for s in segs],
            measured_full=summ(mf), measured_reduce=summ(mr) if mr else None,
            meter='60 fps, WCAG relative luminance, the NOTES_MPST method per region (whole frame, each effect box over the whole beat, 240/120/60 px tiles)')
    json.dump(d, open(p, 'w', encoding='utf-8'), indent=1)
    print('port ok')


if __name__ == '__main__':
    mpst()
    cdhl()
    port()
