import json, re
R = json.load(open('../out/coverage.json'))
rows = set(R['rows'])
ids = [l.split('\t') for l in open('D:/rc_scratch/e10_design/ad_r2/brief_ids.tsv').read().splitlines() if l.strip()]
brief = {a: b for a, b in ids}
dec = open('D:/rc_art/art-pass/docs/concepts/combat_e10_design/DECISIONS.md', encoding='utf-8').read()
txt = dec
# the ids that DECISIONS names anywhere (tables, prose)
missing = [i for i in brief if i not in rows]
named = {i: (i in txt) for i in missing}
print('brief ids', len(brief), 'rows in section 3', len(rows))
print('brief ids without own row:', missing)
print('named elsewhere in DECISIONS:', {k: v for k, v in named.items()})
extra = sorted(rows - set(brief))
print('rows not in brief list (added in 4 / section 8):', extra)
