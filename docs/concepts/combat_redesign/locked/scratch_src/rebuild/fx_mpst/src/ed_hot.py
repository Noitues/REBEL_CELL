"""ed_hot.py: one-off text edit: the commit burn front is a thin white-hot edge (COMMIT_HOT), not 'white-hot for two frames' (it never was)"""
for P, pairs in (
    ('D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/src/mp_eff.py', [
        ('the burn front is white-hot for two frames;', 'a thin white-hot edge (1.8 % of the route length, 60 % white) rides the burn front;'),
        ('white-hot front for 2 frames;', 'thin white-hot edge on the front (quieter than every block: review 2.10);')]),
    ('D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/src/mp_sheets.py', [
        ('behind a white-hot front 2 frames deep;', 'behind a thin white-hot edge (1.8 % of the route length, 60 % white; it was 3.5 % and 75 %, louder than every block);')]),
):
    s = open(P, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (P, a)
        s = s.replace(a, b)
    open(P, 'w', encoding='utf-8').write(s)
print('ok')
