"""mp_order.py [skin]: the review 2.10 loudness order over all eight families on ONE meter (the shared gated meter, fxk_lib.loud_frame):
  M / P / S / T : work/res_<id>_<skin>.json (mp_run.py, every 60 fps frame)
  C / D / H / L : the C/D/H/L designer's own results (fx_cdhl/work/flash/<id>_<skin>.json, read-only; their fx_shield_block is a
                  comparison copy for the block-vs-break sheet, so the real P shield block (mp_eff) stands for it)
Kinds: damage (D, H), kill, block (P, ricochets), state (C, M, S, T and L gain, which the C/D/H/L designer ranks with state).
Pass = damage min > kill max, kill min > block max, block min > state max.  -> work/loud_order.json"""
import sys, os, json, glob
sys.dont_write_bytecode = True
import mp_eff as E
from mp_lib import ME
skin = sys.argv[1] if len(sys.argv) > 1 else 'neutral'
CDW = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_cdhl/work/flash/'
sys.path.insert(1, ME + 'cdhl_snap')
import fx_cdhl as CD
rows = []
for fid, s in E.FX.items():
    fp = ME + 'work/res_%s_%s.json' % (fid, skin)
    if not os.path.exists(fp):
        fp = ME + 'work/res_%s_neutral.json' % fid
    r = json.load(open(fp))
    kind = 'block' if s['fam'] == 'P' else 'state'
    rows.append(dict(id=fid, fam=s['fam'], kind=kind, peak=r['loud']['gated']['peak'], area_px=r['loud']['gated']['area_px'], t_ms=r['loud']['gated']['t_ms'], skin=r['skin'], src='mp_run'))
for f in CD.FX:
    fid = f['id']
    fp = CDW + '%s_%s.json' % (fid, skin)
    if not os.path.exists(fp):
        fp = CDW + '%s_neutral.json' % fid
    if not os.path.exists(fp):
        continue
    r = json.load(open(fp))['full']
    kind = {'gain': 'state'}.get(f['kind'], f['kind'])
    rows.append(dict(id=fid, fam=f['fam'], kind=kind, peak=r['loud_peak'], area_px=r['loud_peak_area_px'], t_ms=r['loud_peak_ms'], skin=os.path.basename(fp).split('_')[-1][:-5], src='fx_cdhl'))
rows.sort(key=lambda d: -d['peak'])
ORDER = ('damage', 'kill', 'block', 'state')
g = {k: [r for r in rows if r['kind'] == k] for k in ORDER}
checks = []
ok = True
for a, b in zip(ORDER, ORDER[1:]):
    lo = min(g[a], key=lambda d: d['peak'])
    hi = max(g[b], key=lambda d: d['peak'])
    p = lo['peak'] > hi['peak']
    ok &= p
    checks.append(dict(louder=a, quieter=b, min_louder=(lo['id'], lo['peak']), max_quieter=(hi['id'], hi['peak']), margin=round(lo['peak'] - hi['peak'], 1), pass_=p))
line = '  >  '.join('%s %.0f-%.0f' % (k, min(r['peak'] for r in g[k]), max(r['peak'] for r in g[k])) for k in ORDER) + ('   PASS' if ok else '   FAIL')
out = dict(skin=skin, meter='shared gated meter: fxk_lib.loud_frame (dE76 > 5 vs the no-effect frame AND vs the settled frame, x L* / 100), peak over the full-motion frames',
           rows=rows, checks=checks, line=line, **{'pass': ok})
json.dump(out, open(ME + 'work/loud_order%s.json' % ('' if skin == 'neutral' else '_' + skin), 'w'), indent=1)
for i, r in enumerate(rows):
    print('%2d %8.0f  %-22s %-6s %s (%s)' % (i + 1, r['peak'], r['id'], r['kind'], r['fam'], r['src']))
for c in checks:
    print(c)
print(line)
