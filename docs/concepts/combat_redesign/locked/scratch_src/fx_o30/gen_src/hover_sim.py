"""hover_sim: builds sim frames (read-only import of the E10 sim) for hover plates: frame(cards, opt, tag, base=, hand=) -> same dict as dump10.frame (asserts removed)."""
import sys, os, json, pickle, copy, random
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pick10 as P
S = P.S
census = P.census
PK = os.path.join(os.path.dirname(HERE), 'work', 'st0.pkl')


def cl(x): return S.clone(x)


def tup(a): return [a[0], list(a[1])] if isinstance(a[1], tuple) else list(a)


def get_st0():
    if os.path.exists(PK):
        return pickle.load(open(PK, 'rb'))
    st0 = [x for x in P.run(49, 3) if x[1] == 2][0][2]
    pickle.dump(st0, open(PK, 'wb'))
    return st0


st0 = get_st0()


def unit_rec(st, d, u, fates, lose):
    df = S.defense(st, u, d)
    return dict(id=u['id'], kind=u['kind'], dep=d, s=u['s'], w=u['w'], hp=u['hp'], mx=u['mx'], sh=u['sh'], shmx=S.UNIT[u['kind']]['sh'] * u['w'],
                hit=S.unit_hit(u), grown=u['g'], df=df, warded=bool(S.warded(st, u)), consumed=False, trigdead=False,
                fate=fates.get(u['id'], dict(kind='waits', k=None, hits=[], tohp=0)), lose=lose.get(u['id'], [0, 0]))


def guns_from_log(st_c, log):
    out = {}
    for e in log:
        if e[0] != 'fire':
            continue
        out.setdefault(e[1], dict(sector=e[1], slice=e[2], shots=[]))
        uid = e[6]
        res = 'none'
        if uid is not None:
            if uid == 0:
                d_, s_, a = S.adjuster(st_c)
                df = S.defense(st_c, a, d_); u = a; wd = False
            else:
                d_, s_, u = S.find_unit(st_c, uid)
                df = S.defense(st_c, u, d_); wd = S.warded(st_c, u)
            if df == 'sealed': res = 'sealed'
            elif e[4] == 0 and df == 'armor': res = 'armor'
            elif e[4] == 0 and wd: res = 'ward'
            elif df == 'shield' and u['sh'] > 0 and e[4] > 0: res = 'shield'
            else: res = 'hit'
        out[e[1]]['shots'].append(dict(uid=uid, kind=e[3], dep=e[5], h=e[4], result=res))
    return [out[k] for k in sorted(out)]


def lose_from_log(st_c, log):
    m = {}
    for e in log:
        if e[0] == 'fire' and e[6] not in (None, 0):
            r = S.find_unit(st_c, e[6])
            if r is None: continue
            d_, s_, u = r
            cur = m.setdefault(e[6], [0, 0])
            sh_left = u['sh'] - cur[0]
            ds = min(sh_left, e[4])
            cur[0] += ds
            cur[1] += e[4] - ds
    return m


def next_bill(st_after):
    s3 = cl(st_after)
    S._advance(s3)
    pv = S.preview(s3)
    hits = [e for e in pv['log'] if e[0] == 'hit']
    return dict(taken=pv['taken'], raw=pv['raw'], absorbed=sum(e[6] for e in hits), slost=pv['slost'])


def frame(cards, opt, tag, base=None, hand=None):
    """cards = list of sim actions; base = sim state to start from (default st0); hand = override the hand list first"""
    st = cl(base or st0)
    if hand is not None:
        st['hand'] = list(hand)
    st_pre = cl(st)
    pre_hand = list(st['hand'])
    ram0 = st['ram']
    for a in cards:
        S.apply(st, a)
    pv = S.preview(st, opt)
    log = pv['log']
    fz = S.fate(st)
    fates = {}
    for uid, v in fz.items():
        if v[0] == 'lands':
            fates[uid] = dict(kind='lands', k=v[1], hits=[list(h) for h in v[2]], tohp=sum(h[3] for h in v[2]))
        elif v[0] == 'dies':
            fates[uid] = dict(kind='dies', k=v[1], hits=[], tohp=0)
        else:
            fates[uid] = dict(kind='waits', k=None, hits=[], tohp=0)
    lose = lose_from_log(st, log)
    on_now = {u['id']: (d, u) for d, u in S.board_units(st)}
    trig_ids = [a[1] for a in cards if a[0] == 'Trigger']
    units = []
    for d, u in S.board_units(st_pre):
        if u['id'] in on_now:
            d2, u2 = on_now[u['id']]
            units.append(unit_rec(st, d2, u2, fates, lose))
        else:
            units.append(dict(unit_rec(st_pre, d, u, {}, {}), consumed=u['id'] in trig_ids, trigdead=u['id'] not in trig_ids))
    brace_sectors = [S.sector_of(st, i) for i in range(6) if st['brace'][i]]
    soak_idx = [] if opt is None else (list(range(6)) if opt == 'all' else list(opt))
    soak_sectors = [S.sector_of(st, i) for i in soak_idx]
    hits_log = [e for e in log if e[0] == 'hit']
    wheel = []
    for s in range(6):
        i = S.slice_at(st, s)
        w = st['wheel'][i]
        h_after = pv['after']['wheel'][i]['hp']
        soaked_here = sum(e[15] for e in hits_log if e[3] == s)
        braced_here = any(e[16] for e in hits_log if e[3] == s)
        wheel.append(dict(sector=s, t=w['t'], hp=w['hp'], mx=w['mx'], jam=w['jam'], hp_after=h_after, brace=s in brace_sectors, soak=s in soak_sectors, soaked=soaked_here, braced_hit=braced_here))
    ad_d, ad_s, ad = S.adjuster(st)
    trig_t = [e for e in st['tlog'] if e[0] == 'trig_tower']
    raw0 = S.arrival_raw(st_pre)
    raw_c = S.arrival_raw(st)
    raw_land = sum(e[4] for e in hits_log)
    braced = sum(e[4] for e in hits_log if e[16])
    rider = sum(min(e[13], e[4]) for e in hits_log if not e[16])
    trig_land_v = sum(e[3] for e in trig_t)
    through = sum(e[7] for e in hits_log) + sum(e[4][7] for e in trig_t)
    absorbed = sum(e[6] for e in hits_log) + sum(e[4][6] for e in trig_t)
    soaked = sum(e[15] for e in hits_log) + sum(e[4][15] for e in trig_t)
    lock = sum(e[1] for e in log if e[0] == 'lock')
    lands = raw_land - braced - rider + trig_land_v
    eq = dict(raw0=raw0, triggered=raw0 - raw_c, tower_from_trigger=trig_land_v, shot_down=raw_c - raw_land, braced=braced, rider=rider, lands=lands, through=through, absorbed=absorbed,
              soaked=soaked, lock=lock)
    n_ref = sum(1 for e in st['tlog'] if e[0] == 'trig_refund')
    kills = [dict(dep=e[2], sector=e[1], uid=e[3], kind=e[4]) for e in st['tlog'] if e[0] == 'trig_unit' and e[7] == 0]
    for u in units:
        fz_ = u['fate']
        if fz_['kind'] == 'lands' and fz_['hits'] and not (u['consumed'] or u['trigdead']):
            u['land_hit'] = fz_['hits'][0][2]
            u['land_sectors'] = [h[0] for h in fz_['hits']]
            u['wear'] = 1 if u['kind'] == 'Worm' else 0
            u['jam'] = 1 if u['kind'] == 'Jammer' else 0
            if fz_['k'] == 0:
                mine = [e for e in hits_log if e[14] == u['id']]
                u['land_through'] = {str(e[1]): e[7] for e in mine}
                u['land_soak'] = {str(e[1]): e[15] for e in mine}
                u['land_brace'] = {str(e[1]): int(e[16]) for e in mine}
                u['land_abs'] = {str(e[1]): e[6] for e in mine}
            else:
                u['land_through'] = {str(h[0]): h[3] for h in fz_['hits']}
                u['land_soak'] = {str(h[0]): 0 for h in fz_['hits']}
                u['land_brace'] = {str(h[0]): 0 for h in fz_['hits']}
                u['land_abs'] = {str(h[0]): h[2] - h[3] for h in fz_['hits']}
    f = dict(tag=tag, turn=st['turn'], hp=st['hp'], maxhp=S.MAXHP, ram=st['ram'], ram0=ram0, ram_max=S.WHEELS[S.WHEEL]['ram'], trace=st['trace'], tcap=S.TRACE_CAP,
             hand=sorted(pre_hand, key=lambda n: (n in S.WAVE_CARDS, n)), played=[tup(a) for a in cards], soak_opt=None if opt is None else list(opt),
             schedule=S.schedule(st), twr=list(st['twr']), twist=st['twist'],
             units=units, wheel=wheel, guns=guns_from_log(st, log), rot=st['rot'], brace_sectors=brace_sectors, soak_sectors=soak_sectors,
             refunds=n_ref, kills=kills,
             adj=dict(ring=ad_d, s=ad_s, hp=ad['hp'], mx=ad['mx'], df=S.defense(st, ad, ad_d), in_range=S.adj_in_range(st), phase=S.adj_phase(st['turn']),
                      strike=S.adj_phase(st['turn']) == 2, hit=S.ADJ_HITS[st['nstrike'] % 2], hp_after=pv['ahp']),
             pv=dict(taken=pv['taken'], raw=pv['raw'], dealt=pv['dealt'], hp_after=pv['hp'], trace_after=pv['trace'], slost=pv['slost'], ahp=pv['ahp'], absorbed=absorbed, soaked=soaked, eq=eq),
             log=[list(e) for e in log if e[0] in ('fire', 'hit', 'repair', 'fw', 'lock')],
             tlog=[[x if not isinstance(x, tuple) else list(x) for x in e] for e in st['tlog']],
             challenges=[dict(name=c, state=S.challenge_state(st, c)) for c in st['challenges']], interf=st['interf'],
             lineup=[[list(x) for x in w] for w in st['lineup']], nfut=st['nfut'], waves_left=S.waves_left(st), rings_wave=[r['wave'] for r in st['rings']],
             consts=dict(MAXHP=S.MAXHP, EHP=S.EHP, STAR_CARD=S.STAR_CARD, STAR_HEAT=S.STAR_HEAT))
    f['next'] = next_bill(pv['after'])
    f['fw'] = list(st['fw'])
    f['hold'] = st['hold']
    f['apull'] = st['apull']
    f['hover_paths'] = {u['id']: [list(x) for x in S.hover_path(st, d, u['s'])] for d, u in S.board_units(st)}
    return f, st, pv


def legal(base=None, hand=None, ram=None):
    st = cl(base or st0)
    if hand is not None: st['hand'] = list(hand)
    if ram is not None: st['ram'] = ram
    return S.actions(st)


if __name__ == '__main__':
    print(sorted(st0['hand']), st0['ram'], st0['turn'], st0['rot'], S.schedule(st0))
    for c in ['Nudge', 'Spin2', 'Spin3', 'Brace', 'Firewall', 'Pull', 'Shove', 'Twist', 'Hold', 'Trigger', 'Strike']:
        print(c, legal(hand=[c], ram=9))
