"""r2_table.py -- the NOTES table rows, printed from the PUBLISHED backdrop checks.json (round 2, with the round-1 numbers it carries) and
round2/backdrop/work/verify.json (re-measured on the published PNGs), so no number is copied by hand."""
import sys, json
sys.dont_write_bytecode = True
D = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/backdrop/'
ck = json.load(open(D + 'checks.json', encoding='utf-8'))
vf = json.load(open('D:/rc_scratch/combat_redesign/locked/round2/backdrop/work/verify.json', encoding='utf-8'))
lab = {'p1_bio': 'bio', 'p1_srv': 'srv', 'p1_gh': 'gh', 'p1_rec': 'rec', 'p1_lobby': 'lobby', 'p1_event': 'event', 'p1_shop': 'shop',
       'p1_bio_solace': 'bio, Solace', 'p1_shop_meridian': 'shop, Meridian'}
f1 = lambda v: '%.1f' % (v + 1e-9)
print('| Plate | Room, round 1 | Room, round 2 (mean / p95) | As seen, round 1 | As seen, round 2 | Box part | Street part | Ring-NOW glass p95 | Detail rel | Sat | Pink | a-i |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for n, p in ck['plates'].items():
    b, a = p['before_round1'], p['after']['L']
    v = vf[n]
    print('| %s | %s / %s | %s / %s | %s | %s | %s | %s | %s | %.3f | %.3f | %.3f %% | %s |' % (
        lab[n], f1(b['room']['mean']), f1(b['room']['p95']), f1(a['room']['mean']), f1(a['room']['p95']), f1(b['room_as_seen']['mean']),
        f1(a['room_as_seen']['mean']), f1(a['room_hull']['mean']), f1(a['room_city']['mean']), f1(p['after']['room_ref']['value']),
        a['detail']['detail_rel'], a['detail']['sat'], 100 * a['detail']['pink_share'], 'pass' if p['after']['plate_pass'] else 'FAIL'))
    assert v['matches_checks_json']
print()
for n, p in ck['plates'].items():
    b, a = p['before_round1'], p['after']['L']
    print(n, 'as-seen drop', round(a['room_as_seen']['mean'] - b['room_as_seen']['mean'], 2), 'room drop', round(a['room']['mean'] - b['room']['mean'], 2),
          'squint room', p['after']['squint']['room'], 'board', p['after']['squint']['board'], 'rbox', a['review_room_box'],
          'det rms', a['detail']['detail_rms'], 'hue', a.get('hull_median_lab'))
