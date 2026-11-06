"""summarise locked/backdrop/checks.json and grade.json per plate / room"""
import sys, json
sys.dont_write_bytecode = True
D = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/backdrop/'
J = json.load(open(D + 'checks.json'))
G = json.load(open(D + 'grade.json'))
print('all_pass', J['all_pass'], 'real vs composite', J.get('real_render_vs_composite'))
for nm, p in J['plates'].items():
    b, a = p['before']['L'], p['after']['L']
    qa, qb = p['after']['squint'], p['before']['squint']
    print('%-18s room %5.1f/%5.1f -> %5.1f/%5.1f | box %4.1f -> %4.1f | street %4.1f -> %4.1f | revbox %4.1f -> %4.1f | city box %4.1f -> %4.1f | drms %.4f -> %.4f rel %.3f -> %.3f | sat %.3f -> %.3f | pink %.5f -> %.5f | ref %s | rb %s' % (
        nm, b['room']['mean'], b['room']['p95'], a['room']['mean'], a['room']['p95'], b['room_hull']['mean'], a['room_hull']['mean'],
        b['room_city']['mean'], a['room_city']['mean'], b['review_room_box']['mean'], a['review_room_box']['mean'],
        b['review_city_box']['mean'], a['review_city_box']['mean'], b['detail']['detail_rms'], a['detail']['detail_rms'],
        b['detail']['detail_rel'], a['detail']['detail_rel'], b['detail']['sat'], a['detail']['sat'], b['detail']['pink_share'], a['detail']['pink_share'],
        p['after']['room_ref']['value'], p['after']['plate_pass']))
    print('   squint keys', list(qa.keys())[:8])
for k, v in G['rooms'].items():
    print(k, {kk: v[kk] for kk in ('ceil', 'tone_lo', 'chroma', 'contrast', 'pink_chroma', 'spill_rgb', 'hue_amt') if kk in v})
