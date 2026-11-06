"""run_r2.py [-j N] [stage ...]: the round-2 effects build after the bases (bases_r2.py, share_bases.py, prep_refund.py, trig_layers.py).
Stages (default: all, in order):
  frames   fx_cdhl fx_build per effect (all its skins), mp_run per effect x skin, layer_check per M/P/S/T effect (neutral),
           mp_beat_render (full and reduce, 4 chunks each)
  measure  mp_order (3 skins), mp_beat_meter full / red, beat_guard
  out      fx_sheets all, mp_beat_out, mp_sheets, pstock_measure
Each job runs as its own process (logs in round2/effects/logs/<job>.log); a stage starts when the one before has finished; any failed job
stops the run."""
import sys, os, subprocess, time
sys.dont_write_bytecode = True
R2 = 'D:/rc_scratch/combat_redesign/locked/round2/effects/'
CS, MS = R2 + 'fx_cdhl/src/', R2 + 'fx_mpst/src/'
PY = sys.executable
CD_IDS = ['fx_grow', 'fx_ward_on', 'fx_gun_hit', 'fx_strike', 'fx_trigger_hit', 'fx_kill', 'fx_ricochet', 'fx_ricochet_gold', 'fx_firewall_burn',
          'fx_hit_land', 'fx_hit_land_worm', 'fx_hit_land_adjuster', 'fx_shield_break', 'fx_slice_crack', 'fx_slice_break', 'fx_hp_through',
          'fx_refund', 'fx_clear', 'fx_repair_mend', 'fx_shield_block']
MP = {'fx_spin': ['neutral'], 'fx_twist': 3, 'fx_pull': 3, 'fx_shove': 3, 'fx_shove_bump': 3, 'fx_rings_step': 3, 'fx_hold': 3, 'fx_wave_enter': 3,
      'fx_shield_block': 3, 'fx_brace_block': 3, 'fx_soak_take': ['neutral'], 'fx_trace_add': ['neutral'], 'fx_commit': 3}
SK3 = ['neutral', 'solace', 'meridian']
N_BEAT = 241                       # mp_beat_render.N for TOTAL_MS 3800 + TAIL 200 at 60 fps


def stage_jobs(st):
    J = []
    if st == 'frames':
        # the slowest first
        for fid, sks in MP.items():
            for sk in (SK3 if sks == 3 else sks):
                J.append(('mprun_%s_%s' % (fid, sk), [PY, MS + 'mp_run.py', fid, sk], MS))
        for m in ('full', 'red'):
            for i0 in range(0, N_BEAT, 61):
                J.append(('beat_%s_%d' % (m, i0), [PY, MS + 'mp_beat_render.py', m, str(i0), str(i0 + 61)], MS))
        for fid in CD_IDS:
            J.append(('cdbuild_%s' % fid, [PY, CS + 'fx_build.py', fid], CS))
        for fid in MP:
            J.append(('layer_%s' % fid, [PY, MS + 'layer_check.py', 'neutral', fid], MS))
    elif st == 'measure':
        for sk in SK3:
            J.append(('order_%s' % sk, [PY, MS + 'mp_order.py', sk], MS))
        J.append(('meter_full', [PY, MS + 'mp_beat_meter.py', 'full'], MS))
        J.append(('meter_red', [PY, MS + 'mp_beat_meter.py', 'red'], MS))
        J.append(('beat_guard', [PY, MS + 'beat_guard.py'], MS))
    elif st == 'out':
        J.append(('cd_sheets', [PY, CS + 'fx_sheets.py', 'all'], CS))
        J.append(('beat_out', [PY, MS + 'mp_beat_out.py'], MS))
    elif st == 'out2':
        J.append(('mp_sheets', [PY, MS + 'mp_sheets.py'], MS))
    elif st == 'out3':
        J.append(('pstock', [PY, MS + 'pstock_measure.py'], MS))
    return J


def run(jobs, j):
    todo, live, t0, bad = list(jobs), [], time.time(), []
    while todo or live:
        while todo and len(live) < j and not bad:
            nm, cmd, cwd = todo.pop(0)
            lf = open(R2 + 'logs/%s.log' % nm, 'w')
            p = subprocess.Popen(cmd, cwd=cwd, stdout=lf, stderr=subprocess.STDOUT)
            live.append((p, nm, lf))
            print('start', nm, 'pid', p.pid, flush=True)
        time.sleep(2)
        for r in live[:]:
            if r[0].poll() is not None:
                r[2].close()
                print('done', r[1], 'exit', r[0].returncode, round(time.time() - t0), flush=True)
                if r[0].returncode != 0:
                    bad.append(r[1])
                live.remove(r)
        if bad and not live:
            break
    return bad


if __name__ == '__main__':
    a = sys.argv[1:]
    j = 6
    if a and a[0] == '-j':
        j = int(a[1]); a = a[2:]
    stages = a or ['frames', 'measure', 'out', 'out2', 'out3']
    os.makedirs(R2 + 'logs', exist_ok=True)
    for st in stages:
        print('== stage', st, flush=True)
        bad = run(stage_jobs(st), j)
        if bad:
            raise SystemExit('failed: %s' % bad)
    print('all stages done', flush=True)
