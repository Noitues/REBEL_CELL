"""E10 plates: build state_e10.json from the E10 sim (read-only import of D4_E10/sim.py; importing it patches census.score to the HP-first score).
State: seed 49, turn 2 (greedy replay of turn 1 under the planner's best line). The hero line is the planner's best line, confirmed by census.enumerate_outcomes
over every line of the turn (END TURN soak choice included, not capped). Writes assert_log.txt. Every count drawn on a plate is a field of this file and is asserted here."""
import sys, json, random
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_polish/E7_waves/E10/src')
import pick10 as P
S = P.S
census = P.census
OUT = 'D:/rc_scratch/combat_polish/E7_waves/E10/'
SEED, TURN = 49, 2
LOG = []


def A(name, got, want):
    ok = got == want
    LOG.append('%s  %s: %s == %s' % ('PASS' if ok else 'FAIL', name, got, want))
    assert ok, (name, got, want)


def cl(x): return S.clone(x)


def tup(a): return [a[0], list(a[1])] if isinstance(a[1], tuple) else list(a)


A('sim is the E10 sim with the HP-first score on, Trigger refund = +1 RAM, cap 1', (S.SCORE_MODE, S.REFUND, S.REFCAP, census.score is S._score), ('hp', 'ram', 1, True))
st0 = [x for x in P.run(SEED, 3) if x[1] == TURN][0][2]
A('state is seed 49 turn 2', (st0['turn'], st0['hp']), (TURN, 15))
# ---------------------------------------------------------------- E10 opening facts (turn 2 of the harder opening)
A('player HP 15', (S.MAXHP, st0['hp']), (15, 15))
A('4-card hand on turn 2', len(st0['hand']), 4)
A('RAM 4 (E_RAMEARLY not adopted)', (st0['ram'], S.turn_ram(2)), (4, 4))
A('wave-1 units on ring NOW are the pre-grown ones (every NOW unit grown +1 or more)', all(u['g'] >= 1 for u in st0['rings'][0]['units']), True)
A('wave 1 was a full ring of 3 units (3 units now on ring NOW)', len(st0['rings'][0]['units']), 3)
# ---------------------------------------------------------------- the planner: every line of the turn
outs, capped = census.enumerate_outcomes(S.g, cl(st0), cap=5000)
A('planner enumerated every line (not capped)', capped, False)
LOG.append('NOTE  outcomes enumerated: %d (END TURN soak choice included)' % len(outs))
top = outs[0]
HERO = P.plan_of(top)
HERO_END = P.end_of(top)
A('planner best line: Twist ring+1 +1, Trigger unit 4, Brace slice 2, soak slice 1', (HERO, HERO_END), ([('Twist', (1, 1)), ('Trigger', 4), ('Brace', 2)], (1,)))
A('planner best line takes 0 HP', top['taken'], 0)
A('HP-first: no enumerated line takes fewer HP than the best (best takes the minimum)', min(o['taken'] for o in outs), top['taken'])
A('HP-first: among the 0-HP lines the best has the fewest slice pips lost', min(o['slost'] for o in outs if o['taken'] == 0), top['slost'])
A('ranking: HP lost never decreases down the ranked list (first 300)', all(outs[i]['taken'] <= outs[i + 1]['taken'] for i in range(300)), True)


def find_line(pred):
    for o in outs:
        if pred(P.plan_of(o)):
            return P.plan_of(o), P.end_of(o), o
    return None


def refund_trigger(pl):
    s_ = cl(st0)
    for a in pl:
        if a[0] == 'Trigger' and any(e[0] == 'refund' for e in S.trigger_preview(s_, a[1])):
            return True
        S.apply(s_, a)
    return False


L_TRIG = find_line(lambda pl: refund_trigger(pl) and not any(a[0] == 'Brace' for a in pl))
L_BRACE = find_line(lambda pl: any(a[0] == 'Brace' for a in pl) and not any(a[0] == 'Trigger' for a in pl))
L_IDLE = find_line(lambda pl: len(pl) == 0)
for nm, ln in (('Trigger-only', L_TRIG), ('Brace-only', L_BRACE), ('no-card', L_IDLE)):
    LOG.append('NOTE  best %s line: %s soak %s score %.1f taken %d slost %d dealt %d' % (nm, ln[0], ln[1], ln[2]['score'], ln[2]['taken'], ln[2]['slost'], ln[2]['dealt']))


def unit_rec(st, d, u, fates, lose, extra=None):
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
            d_, s_, u = S.find_unit(st_c, e[6])
            cur = m.setdefault(e[6], [0, 0])
            sh_left = u['sh'] - cur[0]
            ds = min(sh_left, e[4])
            cur[0] += ds
            cur[1] += e[4] - ds
    return m


def frame(cards, opt, tag):
    st = cl(st0)
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
    for d, u in S.board_units(st0):
        if u['id'] in on_now:
            d2, u2 = on_now[u['id']]
            units.append(unit_rec(st, d2, u2, fates, lose))
        else:
            units.append(dict(unit_rec(st0, d, u, {}, {}), consumed=u['id'] in trig_ids, trigdead=u['id'] not in trig_ids))
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
    raw0 = S.arrival_raw(st0)
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
    A('%s raw0 - triggered - shot == raw landing' % tag, raw0 - eq['triggered'] - eq['shot_down'], raw_land)
    A('%s lands == through + absorbed + soaked' % tag, lands, through + absorbed + soaked)
    A('%s through == sim preview taken' % tag, through + lock, pv['taken'])
    A('%s sim raw == raw landing + trigger tower' % tag, pv['raw'], raw_land + trig_land_v)
    A('%s soak only on marked slices' % tag, all(e[15] == 0 or e[3] in soak_sectors for e in hits_log), True)
    A('%s braced hits only on braced slices' % tag, all((not e[16]) or e[3] in brace_sectors for e in hits_log), True)
    A('%s log accounts' % tag, S.log_accounts(st, pv['after'], log), True) if not st['tlog'] else None
    A('%s chevrons never outnumber HP' % tag, all(u['hit'] <= max(u['hp'], 0) for u in units if not (u['consumed'] or u['trigdead'])), True)
    # E10 refund: RAM bookkeeping from the sim state and the Trigger log
    n_ref = sum(1 for e in st['tlog'] if e[0] == 'trig_refund')
    cost = sum(S.COST[a[0]] for a in cards)
    A('%s RAM after plays == RAM before - card costs + refunds' % tag, st['ram'], ram0 - cost + n_ref)
    A('%s refunds this turn never exceed the cap' % tag, n_ref <= S.REFCAP, True)
    A('%s refunds == Trigger kills capped' % tag, n_ref, min(S.REFCAP, sum(1 for e in st['tlog'] if e[0] == 'trig_unit' and e[7] == 0)))
    kills = [dict(dep=e[2], sector=e[1], uid=e[3], kind=e[4]) for e in st['tlog'] if e[0] == 'trig_unit' and e[7] == 0]
    # rim landing: hit at landing + per-sector HP through (k = 0 from this END TURN's log with Brace / soak; later turns from the sim forecast, no soak, nothing more played)
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
            A('%s unit %d landing sectors have a through value' % (tag, u['id']), sorted(u['land_through']), sorted(str(x) for x in u['land_sectors']))
        if fz_['kind'] == 'lands' and fz_['k'] == 0 and not (u['consumed'] or u['trigdead']):
            A('%s unit %d rim chip == end-turn log (hit at landing)' % (tag, u['id']), sorted(set((h[0], h[2]) for h in fz_['hits'])), sorted(set((e[1], e[4]) for e in hits_log if e[14] == u['id'])))
            A('%s unit %d per-sector HP through sums to the log' % (tag, u['id']), sum(u['land_through'].values()), sum(e[7] for e in hits_log if e[14] == u['id']))
    A('%s k=0 units: per-sector through sums to the HP through (no Trigger tower hits)' % tag, sum(sum(u.get('land_through', {}).values()) for u in units if u['fate']['k'] == 0 and 'land_through' in u), through - sum(e[4][7] for e in trig_t))
    return dict(tag=tag, turn=st['turn'], hp=st['hp'], maxhp=S.MAXHP, ram=st['ram'], ram0=ram0, ram_max=S.WHEELS[S.WHEEL]['ram'], trace=st['trace'], tcap=S.TRACE_CAP,
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
                consts=dict(MAXHP=S.MAXHP, EHP=S.EHP, STAR_CARD=S.STAR_CARD, STAR_HEAT=S.STAR_HEAT)), st, pv


def next_bill(st_after):
    s3 = cl(st_after)
    S._advance(s3)
    pv = S.preview(s3)
    hits = [e for e in pv['log'] if e[0] == 'hit']
    return dict(taken=pv['taken'], raw=pv['raw'], absorbed=sum(e[6] for e in hits), slost=pv['slost'])


OUTJ = {}
f1, st1, pv1 = frame([], None, 'f1')
f2, st2, pv2 = frame(HERO, HERO_END, 'f2_best')
f2t, st2t, pv2t = frame(L_TRIG[0], L_TRIG[1], 'f2_trigger_only')
f2b, st2b, pv2b = frame(L_BRACE[0], L_BRACE[1], 'f2_brace_only')
for f_, pv_ in ((f1, pv1), (f2, pv2), (f2t, pv2t), (f2b, pv2b)):
    f_['next'] = next_bill(pv_['after'])
OUTJ.update(f1=f1, f2=f2, f2t=f2t, f2b=f2b)
OUTJ['cards'] = {c: [S.COST[c], S.LOUD.get(c, 0)] for c in sorted(set(S.DECK))}
# the Twist payoff: the best line with and without the Twist, NEXT bill if nothing more is played
sB = cl(st0)
for a in HERO:
    if a[0] != 'Twist':
        S.apply(sB, a)
pvB = S.preview(sB, HERO_END)
nb_with = f2['next']
nb_without = next_bill(pvB['after'])
OUTJ['twist_payoff'] = dict(with_=nb_with, without=nb_without)
A('Twist payoff: this turn is identical with and without the Twist (HP through, dealt)', (pvB['taken'], pvB['dealt']), (pv2['taken'], pv2['dealt']))
A('Twist payoff: with the Twist the NEXT bill takes less HP than without', nb_with['taken'] < nb_without['taken'], True)
LOG.append('NOTE  NEXT bill with Twist %s, without %s' % (nb_with, nb_without))
_st = cl(st0)
TRIGS = []
for a in HERO:
    if a[0] == 'Trigger':
        d0_, s0_, u_ = S.find_unit(_st, a[1])
        TRIGS.append(dict(uid=a[1], dep=d0_, s=u_['s'], w=u_['w'], kind=u_['kind'], hit=S.unit_hit(u_), entries=[list(e) for e in S.trigger_preview(_st, a[1])]))
    S.apply(_st, a)
OUTJ['trigs'] = TRIGS
_flat = [e for t in TRIGS for e in t['entries']]
_tl = [e for e in f2['tlog']]
A('Trigger previews == the resolve (every entry, in order, refund entries included)', [(e[0], e[1]) for e in _flat], [('unit' if e[0] == 'trig_unit' else ('refund' if e[0] == 'trig_refund' else 'tower'), e[1]) for e in _tl])
A('Trigger preview carries the refund entry', sum(1 for e in _flat if e[0] == 'refund'), 1)
A('the Trigger kills a unit (hp_after 0)', [(e[3], e[4], e[7]) for e in _flat if e[0] == 'unit' and e[7] == 0] != [], True)
A('refund pays +1 RAM: RAM before and after the best line', (f2['ram0'], f2['ram']), (4, 3))
A('hero line planner score vs the others', (top['score'] >= L_TRIG[2]['score'], top['score'] >= L_BRACE[2]['score']), (True, True))
print('LINES', pv2['taken'], pv2['slost'], pv2['dealt'], '|', pv2t['taken'], pv2t['slost'], pv2t['dealt'], L_TRIG[0], L_TRIG[1], '|', pv2b['taken'], pv2b['slost'], pv2b['dealt'], L_BRACE[0], L_BRACE[1]); sys.stdout.flush()
A('hero line takes 0 HP; the Trigger-only and Brace+soak-only lines each take 1 HP and lose more slice pips', (pv2['taken'], pv2t['taken'], pv2b['taken'], pv2t['slost'] > pv2['slost'], pv2b['slost'] > pv2['slost']), (0, 1, 1, True, True))
A('Trigger-only option still earns the refund (its Trigger kills), Brace-only does not', (pv2t['after']['refn'], pv2b['after']['refn']), (1, 0))
A('Brace is a tower card costing 1 RAM, 0 Trace; Hold costs 0 Trace', (S.COST['Brace'], S.LOUD.get('Brace', 0), S.LOUD.get('Hold', 0)), (1, 0, 0))
A('Twist costs 0 RAM', S.COST['Twist'], 0)
A('Ring is plain (no seal)', S.UNIT['Ring']['defense'], 'plain')
A('schedule has a 0 step', 0 in S.schedule(st0), True)
A('hand', f1['hand'], sorted(st0['hand'], key=lambda n: (n in S.WAVE_CARDS, n)))
A('slice max', [w['mx'] for w in f1['wheel']], [2] * 6)
A('SHIELD slices on the tower', sum(1 for w in f1['wheel'] if w['t'] == 'SHIELD'), 2)
A('Adjuster in range on ring +1 (its body is drawn on that ring)', (f1['adj']['ring'], f1['adj']['in_range']), (1, True))
A('the Adjuster is not in its strike phase this turn', f1['adj']['strike'], False)
A('a unit is shot dead by our guns before landing (the green X is exercised)', [u['id'] for u in f1['units'] if u['fate']['kind'] == 'dies'], [2])
# hover (p2b): the 3-wide Packet on ring +2 (its real outcome after our guns)
hv_id = 6
d_, s_, hu = S.find_unit(st0, hv_id)
fzz = S.fate(st0)[hv_id]
OUTJ['hover'] = dict(id=hv_id, path=[list(x) for x in S.hover_path(st0, d_, s_)], fate=dict(kind=fzz[0], k=fzz[1], hits=[list(h) for h in fzz[2]]), kind=hu['kind'], w=hu['w'],
                     hp=hu['hp'], mx=hu['mx'], sh=hu['sh'], hit=S.unit_hit(hu), grown=hu['g'], df=S.defense(st0, hu, d_))
A('hover unit is the 3-wide Packet on ring +2', (hu['kind'], hu['w'], d_), ('Packet', 3, 2))


def make_chain():
    f = f2
    eq = f['pv']['eq']
    tl = f['tlog']
    hits_ = [e for e in f['log'] if e[0] == 'hit']
    fires_ = [e for e in f['log'] if e[0] == 'fire' and e[3] is not None]
    pips1 = sum(e[5] for e in tl if e[0] == 'trig_unit')
    c = []
    c.append(dict(name='TWIST', glyph='C_TWIST', col=[255, 226, 0], pips=[['txt', 'ring +1 turns']]))
    c.append(dict(name='TRIGGER', glyph='C_TRIG', col=[255, 226, 0], pips=[['yel', pips1], ['txt', TRIGS[0]['kind'] + ' dead: refund'], ['refund', 1]]))
    c.append(dict(name='BRACE', glyph='C_BRACE', col=[255, 244, 214], pips=[['txt', 'one slice']]))
    c.append(dict(name='GUNS', glyph='C_STRIKE', col=[92, 225, 255], pips=[['cyan', len(fires_)], ['txt', 'shots']]))
    land = [['raw', sum(e[4] for e in hits_)]]
    if eq['braced']:
        land += [['txt', 'brace'], ['braced', eq['braced']]]
    if eq['rider']:
        land += [['txt', 'rider'], ['rider', eq['rider']]]
    c.append(dict(name='LANDS', glyph='X_SKULL', col=[255, 68, 51], pips=land))
    c.append(dict(name='RINGS STEP', glyph='C_PULL', col=[255, 140, 26], pips=[['txt', 'W4 enters']]))
    return c


f2['chain'] = make_chain()
OUTJ['meta'] = dict(seed=SEED, turn=TURN, hero=[tup(a) for a in HERO], hero_end=list(HERO_END), challenges=st0['challenges'],
                    lines=dict(trigger=[[tup(a) for a in L_TRIG[0]], L_TRIG[1]], brace=[[tup(a) for a in L_BRACE[0]], L_BRACE[1]], idle=[L_IDLE[0], L_IDLE[1]]))
json.dump(OUTJ, open(OUT + 'state_e10.json', 'w'), default=lambda o: list(o) if isinstance(o, tuple) else str(o))
open(OUT + 'assert_log.txt', 'w').write('\n'.join(LOG) + '\n')
print('ok', len(LOG), 'lines')
for k in ('f1', 'f2', 'f2t', 'f2b'):
    print(k, OUTJ[k]['pv']['eq'], 'taken', OUTJ[k]['pv']['taken'], 'slost', OUTJ[k]['pv']['slost'], 'soak', OUTJ[k]['soak_opt'], 'brace', OUTJ[k]['brace_sectors'], 'ram', OUTJ[k]['ram'], 'refunds', OUTJ[k]['refunds'])
print('trig line', OUTJ['meta']['lines'])
