"""notes_table.py : the measured table for NOTES_CDHL.md "2026-11-03 rebuild" (markdown, from work/flash/*.json), sorted by the neutral transient loudness"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_cdhl as F
from fxk_lib import W, CROSS_OK
ALL = F.FX + [F.SHIELD_BLOCK]
rows = []
for fx in ALL:
    fl = {sk: json.load(open(W + 'flash/%s_%s.json' % (fx['id'], sk))) for sk in fx['skins']}
    n = fl['neutral']['full']
    worst = max(max(r['full']['max_flashes_per_s_footprint'], r['full']['max_flashes_per_s_crop']) for r in fl.values())
    red = fl['neutral'].get('reduce', {}).get('max_flashes_per_s_footprint', 0)
    loud = ' / '.join('%.0f' % fl[sk]['full']['loud_peak'] for sk in fx['skins'])
    settle = max(r['full']['settles_ms'] or 0 for r in fl.values())
    hid = max(r['full']['under_px_hidden_by_hud_max'] for r in fl.values())
    cross = max(r['full']['over_px_on_hud_max'] for r in fl.values())
    g = {}
    for r in fl.values():
        for k, v in r['full']['guard_px'].items():
            g[k] = max(g.get(k, 0), v)
    rows.append((n['loud_peak'], '| `%s` | %s | %s | %d | %s | %s | %.0f @ %.0f | %d | %.0f | %.0f | %d | %d | %d / %d / %d | %d | %d |' % (
        fx['id'], fx['fam'], fx['kind'], fx['dur'], ','.join(s[:3] for s in fx['skins']), loud, n['loud_peak_mean_L'], n['loud_peak_ms'], n['loud_peak_area_px'],
        n['loud_total_peak'], settle, hid, cross, g.get('GAIN', 0), g.get('FOCUS', 0), g.get('LIME', 0), worst, red)))
print('| Effect | Fam | Tier | Total ms | Skins | Loudness, transient (neu / sol / mer) | Mean L* @ ms (neu) | Area px (neu) | Loudness, total (neu) | Settles ms | Under-layer px under the HUD | Px drawn on the HUD | GAIN / FOCUS / lime px | Max flashes/s | Reduce flashes/s |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for _, r in sorted(rows, key=lambda x: -x[0]):
    print(r)
