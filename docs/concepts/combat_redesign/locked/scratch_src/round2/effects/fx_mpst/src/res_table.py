"""res_table.py: one line per effect x skin from work/res_*.json (flash full / reduce, gated loudness, brighter-only, strip bytes)"""
import json, glob, os
ME = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_mpst/'
for fp in sorted(glob.glob(ME + 'work/res_*.json')):
    r = json.load(open(fp))
    g = r['loud'].get('gated', {})
    print('%-16s %-8s total %3d red %3d | flash %d (%d) /s %d, reduce %d (%d) /s %d | gated %6.0f @%5.0f %5d px | bright %6.0f | strip %7d %s' % (
        r['id'], r['skin'], r['total_ms'], r['reduce_total_ms'], r['flash']['flashes'], r['flash']['footprint_px'], r['flash']['max_flashes_per_s'],
        r['flash_reduce']['flashes'], r['flash_reduce']['footprint_px'], r['flash_reduce']['max_flashes_per_s'], g.get('peak', -1), g.get('t_ms', -1), g.get('area_px', -1),
        r['loud']['av'], r['strip_bytes'], os.path.basename(r['strip'])))
