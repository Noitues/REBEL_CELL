"""luma.py: print the T5/T6 frame luma curves (new run vs the published metrics)."""
import json
B = 'D:/rc_scratch/combat_redesign/locked/fx_o30b/'
new = json.load(open(B + 'tr/out/neutral/metrics_neutral.json'))
old = json.load(open(B + 'bak/metrics.json'))['neutral']
for k in ('t5', 't6'):
    print(k, 'new', new[k].get('luma'))
    print(k, 'old', old[k].get('luma'))
print(list(new.keys()))
