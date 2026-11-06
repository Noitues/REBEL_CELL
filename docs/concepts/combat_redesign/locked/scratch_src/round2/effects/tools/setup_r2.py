"""setup_r2.py: copy the round-1 effects sources (rebuild/fx_cdhl/src, rebuild/fx_mpst/src) into round2/effects/<set>/src with their
paths moved to round 2.  The round-1 folders are left as they are (they are the record of round 1).  Run once; refuses to overwrite."""
import os, shutil, sys
L = 'D:/rc_scratch/combat_redesign/locked/'
R2 = L + 'round2/effects/'
STAGE = R2 + 'out/'
SUBS = [
    ("ME + 'cdhl_snap'", "'%sfx_cdhl/src'" % R2),
    (L + 'rebuild/fx_mpst/cdhl_snap', R2 + 'fx_cdhl/src'),
    (L + 'rebuild/fx_cdhl/', R2 + 'fx_cdhl/'),
    (L + 'rebuild/fx_mpst/', R2 + 'fx_mpst/'),
    ('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/effects/', STAGE),
]
force = '--force' in sys.argv
for name in ('fx_cdhl', 'fx_mpst'):
    src = L + 'rebuild/%s/src/' % name
    dst = R2 + '%s/src/' % name
    if os.path.exists(dst) and not force:
        raise SystemExit('exists: ' + dst)
    os.makedirs(dst, exist_ok=True)
    for sub in ('work', 'logs', 'frames'):
        os.makedirs(R2 + '%s/%s' % (name, sub), exist_ok=True)
    n = 0
    for fn in sorted(os.listdir(src)):
        if not fn.endswith('.py'):
            continue
        s = open(src + fn, encoding='utf-8').read()
        for a, b in SUBS:
            s = s.replace(a, b)
        open(dst + fn, 'w', encoding='utf-8').write(s)
        n += 1
    print(name, n, 'files ->', dst)
os.makedirs(STAGE + 'strips', exist_ok=True)
print('stage', STAGE)
