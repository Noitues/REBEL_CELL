"""round 2 publish (2026-11-04): copy the board plates that pass every check from locked/rebuild/board/ into locked/final/, with the sheets
(grammar_check, grey_proof, before_after, card_sheet), checks.json and checks_tables.txt, and refresh final/src_snapshot (every
non-underscore .py of corp/src).  A plate that fails any check is NOT copied and is listed.  Refuses to publish anything unless the C14
determinism assert passed.
python publish_r2.py [--dry]"""
import os, sys, json, shutil, glob
sys.dont_write_bytecode = True
BOARD = 'D:/rc_scratch/combat_redesign/locked/rebuild/board/'
FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src/'
C14 = 'D:/rc_scratch/combat_redesign/locked/round2/board/work/c14/c14_assert.json'
dry = '--dry' in sys.argv
ck = json.load(open(BOARD + 'checks.json'))
c14 = json.load(open(C14)) if os.path.exists(C14) else None
if not (c14 and c14.get('pass')):
    raise SystemExit('C14 determinism assert missing or failed: nothing published')
plates, held = [], {}
for name, r in ck['rb_checks'].items():
    if not isinstance(r, dict):
        held[name] = 'missing'
        continue
    bad = [k for k, v in r['pass'].items() if not v]
    # the per-plate gates outside rb_checks: draw asserts, mark collisions, occlusion, hand vs board, dashes, pixel dot runs, stage 2 measures
    da = ck['draw_asserts'].get(name)
    if not (isinstance(da, dict) and da['passed'] == da['total']):
        bad.append('draw_asserts')
    if not ck['collisions_marks'].get(name, {}).get('pass_'):
        bad.append('collisions')
    if not ck['occlusion'].get(name, {}).get('pass_'):
        bad.append('occlusion')
    if not (ck['hand_vs_board'].get(name) or {}).get('pass'):
        bad.append('hand_vs_board')
    dd = ck['dash_audit'].get(name, {})
    if dd.get('dashed_line_calls') or dd.get('dotted_mark_calls') or dd.get('pixel_dot_runs', 1):
        bad.append('dashes / dot runs')
    s2 = ck['stage2_measures'].get(name, {})
    if not (s2.get('hand_margin_pass') and s2.get('ticket_pass')):
        bad.append('stage2')
    if bad:
        held[name] = bad
    else:
        plates.append(name)
print('pass:', len(plates), plates)
print('held (not published):', held)
if dry:
    raise SystemExit(0)
for n in plates:
    shutil.copyfile(BOARD + n + '.png', FINAL + n + '.png')
for f in ('grammar_check.jpg', 'grey_proof.jpg', 'before_after.jpg', 'card_sheet.jpg', 'checks.json', 'checks_tables.txt'):
    if os.path.exists(BOARD + f):
        shutil.copyfile(BOARD + f, FINAL + f)
snap = FINAL + 'src_snapshot/'
k = 0
for f in sorted(glob.glob(SRC + '*.py')):
    b = os.path.basename(f)
    if b.startswith('_'):
        continue
    shutil.copyfile(f, snap + b)
    k += 1
os.makedirs(snap + 'round2_tools/', exist_ok=True)
j = 0
for f in sorted(glob.glob('D:/rc_scratch/combat_redesign/locked/round2/board/*.py')):
    shutil.copyfile(f, snap + 'round2_tools/' + os.path.basename(f))
    j += 1
print('published plates', len(plates), '; src_snapshot .py', k, '; round2_tools', j)
json.dump(dict(published=plates, held=held, c14=c14.get('pass')), open('D:/rc_scratch/combat_redesign/locked/round2/board/work/publish_r2.json', 'w'), indent=1)
