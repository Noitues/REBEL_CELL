"""hv_job: python hv_job.py <plate-name> ... renders each named plate to ../out/final/hover_<name>.png"""
import sys, os, time
sys.dont_write_bytecode = True
import hv_plates as P

JOBS = {
    'brace': lambda: P.brace(),
    'spin3': lambda: P.spin('Spin3'),
    'spin2': lambda: P.spin('Spin2'),
    'nudge': lambda: P.spin('Nudge'),
    'trigger': lambda: P.trigger(),
    'trigger_f2': lambda: P.trigger(True, 'f2'),
    'twist': lambda: P.twist(),
    'strike': lambda: P.strike(),
    'shove': lambda: P.shove(),
    'shove_bump': lambda: P.shove(True, 1, 1, True),
    'pull': lambda: P.pull(),
    'hold': lambda: P.hold(),
    'firewall': lambda: P.firewall(),
    'brace_nowords': lambda: P.brace(False),
    'spin3_nowords': lambda: P.spin('Spin3', False),
    'trigger_nowords': lambda: P.trigger(False),
    'twist_nowords': lambda: P.twist(False),
}

if __name__ == '__main__':
    outd = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'out', 'final')
    os.makedirs(outd, exist_ok=True)
    for nm in sys.argv[1:]:
        t = time.time()
        im = JOBS[nm]()
        im.save(os.path.join(outd, 'hover_%s.png' % nm))
        print('ok', nm, round(time.time() - t, 1), flush=True)
