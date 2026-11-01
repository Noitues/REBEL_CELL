"""hv_run2: python hv_run2.py name ... renders each named plate to ../out/v2/<name>.png (one import, many plates); slips go to ../out/v2/slips.json"""
import sys, os, time, json
sys.dont_write_bytecode = True
import hv_plates2 as P

JOBS = {
    'h01': lambda: P.spin('Spin3'), 'h01_spin2': lambda: P.spin('Spin2'), 'h01_nudge': lambda: P.spin('Nudge'),
    'h02': lambda: P.brace(), 'h03': lambda: P.trigger(), 'h03_f2': lambda: P.trigger(True, 'f2'),
    'h04': lambda: P.twist(), 'h05': lambda: P.strike(), 'h06': lambda: P.shove(), 'h06_bump': lambda: P.shove(True, 1, 1, True),
    'h07': lambda: P.pull(), 'h08': lambda: P.hold(), 'h09': lambda: P.firewall(), 'h10': lambda: P.soak(), 'h11': lambda: P.unit(),
    'h01_nw': lambda: P.spin('Spin3', False), 'h02_nw': lambda: P.brace(False), 'h03_nw': lambda: P.trigger(False), 'h04_nw': lambda: P.twist(False),
}
if __name__ == '__main__':
    lift = os.environ.get('HV_LIFT', 'base')
    P.R.STYLE['lift'] = lift
    outd = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'out', 'v2' if lift == 'base' else 'v2_' + lift)
    os.makedirs(outd, exist_ok=True)
    sj = os.path.join(outd, 'slips.json')
    slips = json.load(open(sj)) if os.path.exists(sj) else {}
    for nm in sys.argv[1:]:
        t = time.time()
        try:
            im = JOBS[nm]()
        except Exception:
            import traceback; traceback.print_exc(); print('FAIL', nm, flush=True); continue
        im.save(os.path.join(outd, nm + '.png'))
        slips.update(P.SLIPS)
        if hasattr(im, 'info_xy') and im.info_xy: slips['bump_xy'] = list(im.info_xy)
        json.dump(slips, open(sj, 'w'), indent=1)
        print('ok', nm, round(time.time() - t, 1), flush=True)
