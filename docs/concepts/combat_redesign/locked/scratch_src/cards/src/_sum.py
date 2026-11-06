import json
j = json.load(open('D:/rc_scratch/combat_redesign/locked/cards/work/checks.json'))
for k, v in j.items():
    if k not in ('icon', 'titles'): print(k, v)
for n, t in j['titles'].items(): print(n, t)
for n, t in j['icon'].items(): print(n, t['disc_hex'], 'disc/around', t['disc_vs_around'], 'halo/around', t['halo_vs_around'], 'glyph/disc', t['glyph_vs_disc'])
