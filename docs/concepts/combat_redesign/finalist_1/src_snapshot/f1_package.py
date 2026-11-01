"""f1_package: copy the finished plates + sheets into the deliverable folder and snapshot the generator source"""
import os, shutil, glob, sys
sys.dont_write_bytecode = True
OUT = 'D:/rc_scratch/combat_redesign/finalist_1/out/'
DEL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/finalist_1/'
SRC = 'D:/rc_scratch/combat_redesign/finalist_1/src/'
os.makedirs(DEL, exist_ok=True)
names = ['p1_decide', 'p1_nowords', 'p2_preview', 'p2b_hover', 'p3_resolve', 'p1_decide_srv', 'p1_decide_gh', 'p2_preview_f2t', 'p2_preview_f2b', 'p3_resolve_f2t', 'p3_resolve_f2b',
         'fx_moment_1_block_vs_break', 'fx_moment_2_brace_soak', 'hover_brace', 'hover_twist', 'hover_trigger', 'legend_f1']
got = []
for n in names:
    p = OUT + n + '.png'
    if os.path.exists(p):
        shutil.copy(p, DEL + n + '.png')
        got.append(n)
for extra in ('assert_draw_log.txt',):
    if os.path.exists(OUT + extra):
        shutil.copy(OUT + extra, DEL + extra)
snap = DEL + 'src_snapshot/'
os.makedirs(snap, exist_ok=True)
n = 0
for f in glob.glob(SRC + '*.py'):
    shutil.copy(f, snap + os.path.basename(f))
    n += 1
print('plates', got)
print('src files', n)
