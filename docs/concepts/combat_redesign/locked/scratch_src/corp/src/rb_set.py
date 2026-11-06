"""rb_set (2026-11-03 rebuild): render plates in parallel with checks on, then copy them to locked/rebuild/board/ and run rb_checks on each.
python rb_set.py [-j N] [--clear] job ...      job = beat[:corp]   (all = the 15 plates: p1 p2 p2b p3 nowords x neutral solace meridian)
--clear deletes the rebuild tower cache first (needed after any lw_tower / rb_patch tower change)."""
import sys, os, subprocess, time, json, shutil, glob
sys.dont_write_bytecode = True
SRC = os.path.dirname(os.path.abspath(__file__))
HERE = 'D:/rc_scratch/combat_redesign/locked/corp/'
BOARD = 'D:/rc_scratch/combat_redesign/locked/rebuild/board/'
LOG = 'D:/rc_scratch/combat_redesign/locked/rebuild/logs/'
NAME = {'p1': 'p1_decide', 'p2': 'p2_preview', 'p2b': 'p2b_hover', 'p3': 'p3_resolve', 'nowords': 'p1_nowords'}
BEATS = ['p1', 'p2', 'p2b', 'p3', 'nowords']
CORPS = ['neutral', 'solace', 'meridian']


def plate_name(beat, corp):
    return NAME[beat] + ('' if corp == 'neutral' else '_' + corp)


def sfx(beat, corp):
    return beat + ('' if corp == 'neutral' else '_' + corp)


def main():
    a = sys.argv[1:]
    j = 5
    if a and a[0] == '-j':
        j = int(a[1]); a = a[2:]
    if a and a[0] == '--clear':
        for f in glob.glob(HERE + 'work/rb_cache/tower_*.png'):
            os.remove(f)
        a = a[1:]
    if a == ['all']:
        a = ['%s:%s' % (b, c) for c in CORPS for b in BEATS]
    jobs = [(x.split(':') + ['neutral'])[:2] for x in a]
    os.makedirs(BOARD, exist_ok=True)
    os.makedirs(LOG, exist_ok=True)
    run, t0 = [], time.time()
    while jobs or run:
        while jobs and len(run) < j:
            beat, corp = jobs.pop(0)
            env = dict(os.environ, CORP=corp)
            lf = open(LOG + '%s_%s.log' % (beat, corp), 'w')
            # 'auto': the skin's own room (stage 2: Meridian renders on the shop under its corp light)
            p = subprocess.Popen([sys.executable, 'asm_render.py', beat, 'auto', '1'], cwd=SRC, env=env, stdout=lf, stderr=subprocess.STDOUT)
            run.append((p, beat, corp, lf))
        time.sleep(2)
        for r in run[:]:
            if r[0].poll() is not None:
                r[3].close()
                beat, corp = r[1], r[2]
                tail = open(LOG + '%s_%s.log' % (beat, corp)).read().strip().splitlines()[-1:]
                print(beat, corp, 'exit', r[0].returncode, round(time.time() - t0), tail, flush=True)
                if r[0].returncode == 0:
                    shutil.copyfile(HERE + 'out/as_%s.png' % sfx(beat, corp), BOARD + plate_name(beat, corp) + '.png')
                run.remove(r)


if __name__ == '__main__':
    main()
