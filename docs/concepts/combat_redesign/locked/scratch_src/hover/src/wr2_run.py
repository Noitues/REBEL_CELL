"""Render every plate the R2 sheets need: out2/pl_<ver>_<state>.png (board box 0,0,1100,1080).  ver = R1 (the R1 favourites) | R2 (all picks) | V_<element> (R2 with one element at V)."""
import sys, os, time, traceback
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import wr_run as R
import wr_config as CFG
import wr_crops as CR
from wr2_picks import R1, R2
OUT2 = 'D:/rc_scratch/e10_design/wave_rings/out2/'
BOX = (0, 0, 1100, 1080)
LABOF = {e[0]: e[3] for e in CFG.EL}
BEATS = ('p1', 'p2', 'p2b')


def states_of(eid):
    out = []
    for (label, st, specs) in CR.STATES.get(eid, []):
        out.append(LABOF[eid] if st == 'lab' else st)
    if eid in CR.EXTRA:
        out += CR.EXTRA[eid]
    seen = []
    for s in out:
        if s not in seen:
            seen.append(s)
    return seen


def render_state(state, opts):
    if state in BEATS:
        return R.plate(state, None, opts)
    return R.plate('p1', state, opts)


def job(ver, state, opts):
    fn = OUT2 + 'pl_%s_%s.png' % (ver, state)
    if os.path.exists(fn):
        return
    t = time.time()
    try:
        render_state(state, opts).crop(BOX).save(fn)
        print(ver, state, round(time.time() - t, 1), flush=True)
    except Exception:
        print('FAIL', ver, state, traceback.format_exc(), flush=True)


if __name__ == '__main__':
    only = sys.argv[1:]
    all_states = []
    for eid in CFG.ORDER:
        for s in states_of(eid):
            if s not in all_states:
                all_states.append(s)
    if not only or 'base' in only:
        for s in all_states:
            job('R1', s, dict(R1))
            job('R2', s, dict(R2))
        for s in ('place', 'kinds'):
            pass
        for m in ('E', 'R', 'V', 'C'):
            job('place_' + m, 'place', dict(R2, token_placement=m))
        for m in ('E', 'R', 'V', 'C'):
            job('kinds_' + m, 'kinds', dict(R2, kind_colour_set=m))
    if not only or 'var' in only:
        for eid in CFG.ORDER:
            import wr2_config as C2
            if eid in ('unit_screen_bezel', 'unit_screen_code_text', 'screen_motif_skull') or C2.EL2[eid][2] == '-':
                continue
            for s in states_of(eid):
                o = dict(R2)
                o[eid] = 'V'
                job('V_' + eid, s, o)
