"""notes_write.py: NOTES_MPST.md for the 2026-11-03 rebuild. Replaces the gate-1 status line, inserts the rebuild section (work/notes_rebuild.md)
after the intro paragraph, and keeps every older section under one 'History' heading (each old heading one level down). Keeps a copy of the
file as it was in work/NOTES_MPST_before_rebuild.md. Run once: refuses if the rebuild section is already there."""
import shutil
P = 'D:/rc_scratch/combat_redesign/locked/round2/effects/out/NOTES_MPST.md'
ME = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_mpst/'
s = open(P, encoding='utf-8').read()
assert '## 2026-11-03 rebuild' not in s, 'already written'
shutil.copy(P, ME + 'work/NOTES_MPST_before_rebuild.md')
L = s.split('\n')
assert L[0].startswith('# Effects on the locked board'), L[0]
assert L[2].startswith('**Status 2026-11-04 (gate 1): not re-rendered.**'), L[2]
assert L[4].startswith('This section covers the four families'), L[4]
new = open(ME + 'work/notes_rebuild.md', encoding='utf-8').read().rstrip('\n').split('\n')
head = ['# Effects on the locked board: M motion, P protect, S system, T commit', '']
status = new[0]
body = new[1:]
old = L[4:]
hist = ['', '## History (before the 2026-11-03 rebuild; superseded)', '',
        'Everything below is the record of the earlier passes (roadmap step 4, O-30, O-30 board). Its totals, echoes, flash numbers and file sizes '
        'describe plates that no longer exist; the rebuild section above replaces them. It is kept so earlier reviews can be traced.', '']
for ln in old:
    if ln.startswith('## '):
        ln = '### ' + ln[3:]
    elif ln.startswith('### '):
        ln = '#### ' + ln[4:]
    hist.append(ln)
out = head + [status, ''] + body + hist
open(P, 'w', encoding='utf-8').write('\n'.join(out).rstrip('\n') + '\n')
print('ok', len(out), 'lines')
