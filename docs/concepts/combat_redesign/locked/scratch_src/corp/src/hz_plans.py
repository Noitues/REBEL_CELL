"""print what each hover plan changes (sim, read only)"""
import sys
sys.dont_write_bytecode = True
import hover_sim as HS

H4 = ['Brace', 'Spin3', 'Trigger', 'Twist']
PLANS = {
    'h01': ([('Spin3', 3)], H4, None), 'h01_spin2': ([('Spin2', 2)], ['Brace', 'Spin2', 'Trigger', 'Twist'], None),
    'h01_nudge': ([('Nudge', 1)], ['Brace', 'Nudge', 'Trigger', 'Twist'], None),
    'h02': ([('Brace', 2)], H4, None), 'h03': ([('Trigger', 4)], H4, None), 'h03_f2': ([('Twist', (1, 1)), ('Trigger', 4)], H4, None),
    'h04': ([('Twist', (1, 1))], H4, None), 'h05': ([('Strike', 5)], ['Strike', 'Brace', 'Trigger', 'Twist'], None),
    'h06': ([('Shove', (5, 1))], ['Shove', 'Brace', 'Trigger', 'Twist'], None), 'h06_bump': ([('Shove', (5, -1))], ['Shove', 'Brace', 'Trigger', 'Twist'], None),
    'h07': ([('Pull', 7)], ['Pull', 'Brace', 'Trigger', 'Twist'], None), 'h08': ([('Hold', 0)], ['Hold', 'Brace', 'Trigger', 'Twist'], None),
    'h09': ([('Firewall', 0)], ['Firewall', 'Brace', 'Trigger', 'Twist'], None), 'h10': ([], H4, [1]),
}


def us(f):
    return {u['id']: (u['kind'], u['dep'], u['s'], u['w'], u['hp'], u['lose'], u['fate']['kind'], u['fate']['k'], u.get('land_sectors'), u.get('land_through'), u['consumed'], u['trigdead']) for u in f['units']}


if __name__ == '__main__':
    live, _, _ = HS.frame([], None, 'live', hand=H4)
    L = us(live)
    print('LIVE eq', live['pv']['eq'], 'ram', live['ram'], 'trace', live['trace'], 'hp_after', live['pv']['hp_after'], 'adj', live['adj'])
    for k, v in L.items():
        print('  ', k, v)
    print('  wheel', [(w['sector'], w['t'], w['hp'], w['hp_after']) for w in live['wheel']])
    for nm, (cards, hand, opt) in PLANS.items():
        try:
            f, st, pv = HS.frame(cards, opt, nm, hand=hand)
        except Exception as e:
            print(nm, 'FAIL', e); continue
        P = us(f)
        print('==', nm, cards, 'eq', f['pv']['eq'], 'ram', f['ram'], 'trace', f['trace'], 'hp_after', f['pv']['hp_after'], 'rot', f['rot'], 'sched', f['schedule'], 'twist', f['twist'], 'twr', f['twr'])
        print('   refunds', f['refunds'], 'kills', f['kills'], 'fw', f['fw'], 'hold', f['hold'], 'adj', f['adj'])
        print('   tlog', f['tlog'])
        for k in sorted(set(L) | set(P)):
            if L.get(k) != P.get(k):
                print('   unit', k, L.get(k), '->', P.get(k))
        print('   wheel', [(w['sector'], w['t'], w['hp'], w['hp_after'], w['brace'], w['soak']) for w in f['wheel']])
        print('   guns', [(g['sector'], [(s['uid'], s['result']) for s in g['shots']]) for g in f['guns']])
