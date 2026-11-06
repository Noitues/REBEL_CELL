import json, glob, os
for p in sorted(glob.glob('D:/rc_scratch/combat_redesign/locked/rebuild/hover/chk/h*.checks.json')):
    c = json.load(open(p))['pencil']
    print('%-28s L5 %s/%s chev %s' % (os.path.basename(p)[:-12], c['mask'].get('L5_wax'), c['mask'].get('L5_all'), c.get('L5_chevrons_reported')))
