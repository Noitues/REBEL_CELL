"""peek_port: print the shape of the three port data files compactly (exploration)."""
import json

P = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/port/'
s = json.load(open(P + 'skin_tables.json', encoding='utf-8'))
for k in ('tokens', 'neutrals', 'marks', 'slice_inks', 'card_types', 'trace_tab', 'targets', 'time_grade', 'rooms', 'retired_skin_fields',
          'plan_badge_v', 'boss_gold_old'):
    v = s.get(k)
    print('==', k, json.dumps(v)[:900])
print('== cells keys', list(s['cells'].keys()))
print('== clock keys', list(s['clock'].keys()), json.dumps({k: s['clock'][k] for k in s['clock'] if k != 'functions'})[:700])
print('== clock fns', {k: len(v.get('layers', [])) if isinstance(v, dict) else v for k, v in s['clock']['functions'].items()})
sk = s['skins']['solace']
print('== skin keys', list(sk.keys()))
print('== solace inks', json.dumps(sk['inks'])[:600])
print('== solace pal', json.dumps(sk['pal'])[:900])
print('== solace material_means', json.dumps(sk['material_means'])[:900])
print('== solace measured', json.dumps(sk['measured_on_plates'])[:500])
f = json.load(open(P + 'fx_timings.json', encoding='utf-8'))
print('== fx keys', list(f.keys()))
print('== fx effect0', json.dumps(f['effects'][0])[:1500])
print('== fx beat', json.dumps(f['resolve_beat'])[:1500])
print('== fx loud', json.dumps(f['loudness_order'])[:800])
print('== fx misc', json.dumps({k: f[k] for k in ('cap_ms', 'per_effect_overrides', 'tier_vfx', 'layer_rule', 'hud_layer_effects', 'fps', 'p_stock', 'loudness_rule', 'loudness_metric', 'count', 'families')})[:1500])
