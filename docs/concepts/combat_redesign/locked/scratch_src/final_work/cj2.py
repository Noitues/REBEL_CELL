import json
r = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/checks.json'))
for n, v in r['cards']['icon_disc'].items(): print(n, v['disc'], v['disc_vs_art_around'], v['glyph_vs_disc'])
print(r['cards']['trace_tab'], r['cards']['tower_vs_wave_grey'], r['cards']['bone_vs_paper_if_used'])
g = json.load(open('D:/rc_scratch/combat_redesign/locked/corp/work/grammar_check.json'))
for n, v in g['chevrons_sector0'].items(): print('s0', n, [(e['grammar'], e.get('luma_contrast'), e.get('dE2000')) for e in v])
print(r['corp'].get('kind_dE2000_swatches (cell code unchanged since the first pass)'))
