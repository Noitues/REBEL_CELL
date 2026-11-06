"""publish_r2.py [--dry]: copy the staged round-2 effects (round2/effects/out/) over the published round-1 files in
docs/concepts/combat_redesign/locked/effects/ (same names, same folders), then byte-compare every copy.  Refuses if a published image or
strip would be left without a round-2 replacement (so no round-1 plate stays beside the round-2 set), or if the staging folder holds a
name the published set does not (a new name must be added on purpose).  The notes are written in place, not by this script."""
import sys, os, shutil, filecmp, glob, json
R2 = 'D:/rc_scratch/combat_redesign/locked/round2/effects/'
SRC = R2 + 'out/'
PUB = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/effects/'
dry = '--dry' in sys.argv
KINDS = ('*.png', '*.jpg', '*.gif', '*.json')


def names(root):
    s = set()
    for k in KINDS:
        s |= {os.path.basename(p) for p in glob.glob(root + k)}
        s |= {'strips/' + os.path.basename(p) for p in glob.glob(root + 'strips/' + k)}
    return s


staged, published = names(SRC), names(PUB)
missing = sorted(published - staged)
extra = sorted(staged - published)
print('staged', len(staged), 'published', len(published))
if missing:
    raise SystemExit('published files with no round-2 replacement: %s' % missing)
if extra:
    raise SystemExit('staged files the published set does not have: %s' % extra)
rep = []
for n in sorted(staged):
    a, b = SRC + n, PUB + n
    if not dry:
        shutil.copyfile(a, b)
    same = filecmp.cmp(a, b, shallow=False)
    rep.append(dict(name=n, bytes=os.path.getsize(a), identical_after_copy=same))
    print('%-44s %9d  %s' % (n, os.path.getsize(a), 'ok' if same else ('DIFFERS' if not dry else 'would replace')))
bad = [r['name'] for r in rep if not r['identical_after_copy']]
json.dump(dict(dry=dry, files=rep, differ=bad), open(R2 + 'work/publish%s.json' % ('_dry' if dry else ''), 'w'), indent=1)
if bad and not dry:
    raise SystemExit('copies differ: %s' % bad)
print('ok', 'dry' if dry else 'published', len(rep))
