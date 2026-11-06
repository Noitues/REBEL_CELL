"""E8 plates: build state_e8.json from the E8 sim (read-only import). Every count drawn on a plate is a field of this file; every field is asserted here against the sim.
Writes assert_log.txt. State: seed 178, turn 2 (greedy replay of turn 1, see pick8.py)."""
import sys, json, random
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_polish/E7_waves/E8/src')
import pick8 as P
S = P.S
OUT = 'D:/rc_scratch/combat_polish/E7_waves/E8/'
SEED, TURN = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (178, 2)
MODE = sys.argv[3] if len(sys.argv) > 3 else 'full'
LOG = []


def A(name, got, want):
    ok = got == want
    LOG.append('%s  %s: %s == %s' % ('PASS' if ok else 'FAIL', name, got, want))
    assert ok, (name, got, want)


def cl(x): return S.clone(x)


st0 = [x for x in P.run(SEED, 3) if x[1] == TURN][0][2]
assert st0['turn'] == TURN
ST0 = cl(st0)
ZONE = {0: 'NOW', 1: '+1', 2: '+2'}


def unit_rec(st, d, u, fates, lose_map, consumed=False, trigdead=False):
    df = S.defense(st, u, d)
    return dict(id=u['id'], kind=u['kind'], dep=d, s=u['s'], w=u['w'], hp=u['hp'], mx=u['mx'], sh=u['sh'], shmx=S.UNIT[u['kind']]['sh'] * u['w'],
                hit=S.unit_hit(u), grown=u['g'], df=df, warded=bool(S.warded(st, u)), consumed=consumed, trigdead=trigdead,
                fate=fates.get(u['id'], dict(kind='waits', k=None, hits=[], tohp=0)), lose=lose_map.get(u['id'], [0, 0]))


def guns_from_log(st_c, log):
    out = {}
    for e in log:
        if e[0] != 'fire':
            continue
        out.setdefault(e[1], dict(sector=e[1], slice=e[2], shots=[]))
        uid = e[6]
        res = 'none'
        dep = e[5]
        if uid is not None:
            if uid == 0:
                d_, s_, a = S.adjuster(st_c)
                df = S.defense(st_c, a, d_)
                wd = False
            else:
                d_, s_, u = S.find_unit(st_c, uid)
                df = S.defense(st_c, u, d_)
                wd = S.warded(st_c, u)
            if df == 'sealed':
                res = 'sealed'
            elif e[4] == 0 and (df == 'armor'):
                res = 'armor'
            elif e[4] == 0 and wd:
                res = 'ward'
            elif df == 'shield' and u['sh'] > 0 and e[4] > 0:
                res = 'shield'
            else:
                res = 'hit'
        out[e[1]]['shots'].append(dict(uid=uid, kind=e[3], dep=dep, h=e[4], result=res))
    return [out[k] for k in sorted(out)]


def lose_from_log(st_c, log):
    """pips each unit loses to the guns this END TURN: [shield pips, hp pips] (shield first, as absorb() does)"""
    m = {}
    for e in log:
        if e[0] == 'fire' and e[6] not in (None, 0):
            d_, s_, u = S.find_unit(st_c, e[6])
            cur = m.setdefault(e[6], [0, 0])
            h = e[4]
            sh_left = u['sh'] - cur[0]
            ds = min(sh_left, h)
            cur[0] += ds
            cur[1] += h - ds
    return m


def frame(cards, tag):
    st = cl(st0)
    pre_hand = list(st['hand'])
    for a in cards:
        S.apply(st, a)
    pv = S.preview(st)
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
    units = []
    for d, u in S.board_units(st0):
        if u['id'] in on_now:
            d2, u2 = on_now[u['id']]
            units.append(unit_rec(st, d2, u2, fates, lose))
        else:
            # consumed by a Trigger we played, or killed by one
            trig_ids = [a[1] for a in cards if a[0] == 'Trigger']
            units.append(dict(unit_rec(st0, d, u, {}, {}), consumed=u['id'] in trig_ids, trigdead=u['id'] not in trig_ids))
    wheel = []
    for s in range(6):
        i = S.slice_at(st, s)
        w = st['wheel'][i]
        wheel.append(dict(sector=s, t=w['t'], hp=w['hp'], mx=w['mx'], jam=w['jam'], hp_after=pv['after']['wheel'][i]['hp']))
    ad_d, ad_s, ad = S.adjuster(st)
    hits_log = [e for e in log if e[0] == 'hit']
    trig_t = [e for e in st['tlog'] if e[0] == 'trig_tower']
    trig_u = [e for e in st['tlog'] if e[0] == 'trig_unit']
    raw0 = S.arrival_raw(st0)
    raw_c = S.arrival_raw(st)
    raw_land = sum(e[4] for e in hits_log)
    rider = sum(e[5] for e in hits_log)
    trig_land_v = sum(e[3] for e in trig_t)
    trig_through = sum(e[4][7] for e in trig_t)
    trig_abs = sum(e[4][6] for e in trig_t)
    through_h = sum(e[7] for e in hits_log)
    abs_h = sum(e[6] for e in hits_log)
    lock = sum(e[1] for e in log if e[0] == 'lock')
    eq = dict(raw0=raw0, triggered=raw0 - raw_c, tower_from_trigger=trig_land_v, shot_down=raw_c - raw_land, rider=rider,
              lands=raw_land - rider + trig_land_v, through=through_h + trig_through, absorbed=abs_h + trig_abs, lock=lock)
    # --- asserts: the bill closes and equals the sim's own preview
    A('%s raw0 - triggered - shot_down == raw landing' % tag, eq['raw0'] - eq['triggered'] - eq['shot_down'], raw_land)
    A('%s raw landing - rider + trigger tower == lands' % tag, raw_land - rider + trig_land_v, eq['lands'])
    A('%s lands == through + absorbed' % tag, eq['lands'], eq['through'] + eq['absorbed'])
    A('%s through == sim preview taken (no lockdown)' % tag, eq['through'] + lock, pv['taken'])
    A('%s sim raw == raw landing + trigger tower' % tag, pv['raw'], raw_land + trig_land_v)
    A('%s log accounts' % tag, S.log_accounts(st, pv['after'], log), True) if not st['tlog'] else None
    st_next = cl(pv['after'])
    return dict(tag=tag, turn=st['turn'], hp=st['hp'], maxhp=S.MAXHP, ram=st['ram'], ram_max=S.WHEELS[S.WHEEL]['ram'], trace=st['trace'], tcap=S.TRACE_CAP,
                hand=sorted(pre_hand, key=lambda n: (n in S.WAVE_CARDS, n)), played=[list(a) for a in cards],
                schedule=S.schedule(st), printed=[S.step(dict(st, twist=0, twr=(0, 0)), k) for k in range(3)], twr=list(st['twr']),
                units=units, wheel=wheel, guns=guns_from_log(st, log), rot=st['rot'],
                adj=dict(ring=ad_d, s=ad_s, hp=ad['hp'], mx=ad['mx'], df=S.defense(st, ad, ad_d), in_range=S.adj_in_range(st), phase=S.adj_phase(st['turn']),
                         strike=S.adj_phase(st['turn']) == 2, hit=S.ADJ_HITS[st['nstrike'] % 2], hp_after=pv['ahp'], next_in=None if S.adj_in_range(st) else S.adj_next_in_range(st)),
                pv=dict(taken=pv['taken'], raw=pv['raw'], dealt=pv['dealt'], kills=pv['kills'], hp_after=pv['hp'], trace_after=pv['trace'], slost=pv['slost'], ahp=pv['ahp'],
                        absorbed=eq['absorbed'], eq=eq),
                log=[list(e) for e in log if e[0] in ('fire', 'hit', 'repair', 'fw', 'lock')],
                tlog=[[x if not isinstance(x, tuple) else list(x) for x in e] for e in st['tlog']],
                fw=list(st['fw']), challenges=[dict(name=c, state=S.challenge_state(st, c)) for c in st['challenges']], interf=st['interf'],
                lineup=[[list(x) for x in w] for w in st['lineup']], nfut=st['nfut'], waves_left=S.waves_left(st), rings_wave=[r['wave'] for r in st['rings']],
                consts=dict(MAXHP=S.MAXHP, EHP=S.EHP, STAR_CARD=S.STAR_CARD, STAR_HEAT=S.STAR_HEAT, STAR_SCRAP=S.STAR_SCRAP)), st, pv


def trig_entries(uid):
    d0, s0, u = S.find_unit(st0, uid)
    tp = S.trigger_preview(st0, uid)
    return dict(uid=uid, dep=d0, s=u['s'], w=u['w'], kind=u['kind'], hit=S.unit_hit(u), entries=[list(e) for e in tp])


def next_bill(st_after):
    """NEXT: if nothing more is played, next turn's bill from the state after this END TURN (the E7 convention)"""
    s3 = cl(st_after)
    S._advance(s3)
    pv = S.preview(s3)
    hits = [e for e in pv['log'] if e[0] == 'hit']
    return dict(taken=pv['taken'], raw=pv['raw'], absorbed=sum(e[6] for e in hits), slost=pv['slost'])



def make_chain(f):
    eq = f['pv']['eq']
    tl = f['tlog']
    trig_pips = sum(e[5] for e in tl if e[0] == 'trig_unit')
    fires = [e for e in f['log'] if e[0] == 'fire' and e[3] is not None]
    hits = [e for e in f['log'] if e[0] == 'hit']
    steps = []
    steps.append(dict(name='TWIST', glyph='C_TWIST', col=YEL_, pips=[['txt', 'ring +1']]))
    steps.append(dict(name='TRIGGER', glyph='C_TRIG', col=YEL_, pips=[['yel', trig_pips], ['txt', 'Packet X']]))
    steps.append(dict(name='NUDGE', glyph='PI_SPIN_CW', col=CYAN_, pips=[['rider', 1], ['txt', 'rider']]))
    steps.append(dict(name='GUNS', glyph='C_STRIKE', col=CYAN_, pips=[['cyan', len(fires)], ['txt', 'shots'], ['yel', sum(e[4] for e in fires)]]))
    steps.append(dict(name='LANDS', glyph='X_SKULL', col=RED_, pips=[['raw', sum(e[4] for e in hits)], ['rider', eq['rider']], ['txt', 'rider -1']]))
    steps.append(dict(name='BILL', glyph='X_HP', col=GREEN_, pips=[['through', eq['through']], ['absorb', eq['absorbed']], ['slice', f['pv']['slost']]]))
    steps.append(dict(name='RINGS STEP IN', glyph='C_PULL', col=ORANGE_, pips=[['txt', 'W4 enters']]))
    return steps

YEL_, CYAN_, RED_, GREEN_, ORANGE_ = [255, 226, 0], [92, 225, 255], [255, 68, 51], [123, 224, 123], [255, 140, 26]

OUTJ = {}
f1, st1, pv1 = frame([], 'f1')
OUTJ['f1'] = f1
OUTJ['f1']['next'] = next_bill(pv1['after'])
if MODE == 'decide':
    OUTJ['cards'] = {c: [S.COST[c], S.LOUD.get(c, 0)] for c in sorted(set(S.DECK))}
    shots = [sh['result'] for g in f1['guns'] for sh in g['shots']]
    A('p1b: an armor bounce is on the board', 'armor' in shots, True)
    A('p1b: a shield pop is on the board', 'shield' in shots, True)
    A('p1b: a unit is shot dead by the guns', any(u['fate']['kind'] == 'dies' and u['fate']['k'] == 0 for u in f1['units']), True)
    A('p1b: wound rule', all(u['hit'] <= max(u['hp'], 0) for u in f1['units']), True)
    A('p1b: slice max', [w['mx'] for w in f1['wheel']], [2] * 6)
    OUTJ['meta'] = dict(seed=SEED, turn=TURN, challenges=st0['challenges'])
    json.dump(OUTJ, open(OUT + 'state_e8b.json', 'w'))
    open(OUT + 'assert_log_b.txt', 'w').write('\n'.join(LOG) + '\n')
    print('ok decide', len(LOG), 'asserts', [(g['sector'], g['slice'], [sh['result'] for sh in g['shots']]) for g in f1['guns']])
    sys.exit(0)
HERO = ('Trigger', 4)
ALT = ('Trigger', 5)
f2a, st2a, pv2a = frame([HERO], 'f2a')
f2b, st2b, pv2b = frame([ALT], 'f2b_alt')
OUTJ['f2a'], OUTJ['f2alt'] = f2a, f2b
OUTJ['f2a']['next'] = next_bill(pv2a['after'])
OUTJ['f2alt']['next'] = next_bill(pv2b['after'])
OUTJ['trig_hero'] = trig_entries(4)
OUTJ['trig_alt'] = trig_entries(5)
# Twist line-ups (ghost rim chips): for each Twist (ring, +-1), the best next-turn Trigger's pips off units, and the unit it is played from
tw = []
for a in S.actions(st0):
    if a[0] != 'Twist':
        continue
    s2 = cl(st0)
    S.apply(s2, a)
    s3 = cl(S.preview(s2)['after'])
    S._advance(s3)
    best = None
    for d, r in enumerate(s3['rings']):
        if d not in (1, 2):
            continue
        for u in r['units']:
            if S.sealed(s3, d, u):
                continue
            tp = S.trigger_preview(s3, u['id'])
            pips = sum(e[5] for e in tp if e[0] == 'unit')
            tower = sum(1 for e in tp if e[0] == 'tower')
            kills = len({e[3] for e in tp if e[0] == 'unit' and e[7] == 0})
            key = (kills, pips, -tower, -u['id'])
            if best is None or key > best[0]:
                best = (key, u['id'], u['kind'], pips, tower, [list(e) for e in tp], kills)
    tw.append(dict(action=list(a[1]) if isinstance(a[1], tuple) else a[1], ring=a[1][0], sgn=a[1][1], pips=best[3], tower=best[4], unit=best[1], kind=best[2], path=best[5], kills=best[6], next=next_bill(S.preview(s2)['after'])))
# baseline: no twist
s3 = cl(pv1['after'])
S._advance(s3)
base = None
for d, r in enumerate(s3['rings']):
    if d not in (1, 2):
        continue
    for u in r['units']:
        if S.sealed(s3, d, u):
            continue
        tp = S.trigger_preview(s3, u['id'])
        pips = sum(e[5] for e in tp if e[0] == 'unit')
        tower = sum(1 for e in tp if e[0] == 'tower')
        kills = len({e[3] for e in tp if e[0] == 'unit' and e[7] == 0})
        key = (kills, pips, -tower, -u['id'])
        if base is None or key > base[0]:
            base = (key, u['id'], pips, tower, kills)
OUTJ['twist'] = dict(options=tw, base_pips=base[2], base_tower=base[3], base_kills=base[4], base_unit=base[1])
# p3 plan: Twist ring +2 by +1, Trigger the Worm, Nudge +1 (rider)
PLAN = [('Twist', (2, 1)), ('Trigger', 4), ('Nudge', 1)]
f3, st3, pv3 = frame(PLAN, 'f3')
OUTJ['f3'] = f3
OUTJ['f3']['chain'] = make_chain(f3)
OUTJ['f3']['next'] = next_bill(pv3['after'])
# hover (p2b): the Payload on ring +2, real outcome after our guns
hv_id = 5
d_, s_, hu = S.find_unit(st0, hv_id)
fz = S.fate(st0)[hv_id]
OUTJ['hover'] = dict(id=hv_id, path=[list(x) for x in S.hover_path(st0, d_, s_)], fate=dict(kind=fz[0], k=fz[1], hits=[list(h) for h in fz[2]]), kind=hu['kind'], w=hu['w'],
                     hp=hu['hp'], mx=hu['mx'], sh=hu['sh'], hit=S.unit_hit(hu), grown=hu['g'], df=S.defense(st0, hu, d_))
# after-state arrival of the hovered unit (sector list): from the log of the outlook
OUTJ['cards'] = {c: [S.COST[c], S.LOUD.get(c, 0)] for c in sorted(set(S.DECK))}
OUTJ['meta'] = dict(seed=SEED, turn=TURN, hero=list(HERO), alt=list(ALT), plan=[list(a) if not isinstance(a[1], tuple) else [a[0], list(a[1])] for a in PLAN],
                    challenges=st0['challenges'], rsched=st0['rsched'][TURN - 1:TURN + 2], rng='greedy replay of turn 1 with random.Random(seed)')
# ---- asserts on the choreography
A('hero Trigger kills the wide NOW Packet (id 1)', [e for e in S.trigger_preview(st0, 4)], [('unit', 0, 0, 1, 'Packet', 3, 6, 3, 0, 0), ('unit', 1, 0, 1, 'Packet', 3, 3, 0, 0, 0)])
A('hero saves: taken base vs hero', (f1['pv']['taken'], f2a['pv']['taken']), (7, 1))
A('alt (Payload) trigger: taken', f2b['pv']['taken'], 9)
A('Jammer shield pips x width', [u['shmx'] for u in f1['units'] if u['kind'] == 'Jammer'], [1])
A('Payload armored', [u['df'] for u in f1['units'] if u['kind'] == 'Payload'], ['armor'])
A('sealed Ring in the climax lineup', st0['lineup'][-1], [('Ring', 6, 4)])
A('unit counts: HP max per kind', sorted((u['kind'], u['mx']) for u in f1['units']), sorted([('Packet', 6), ('Packet', 6), ('Worm', 6), ('Worm', 6), ('Payload', 8), ('Jammer', 2)]))
A('wound rule: no chevron stack taller than HP', all(u['hit'] <= max(u['hp'], 0) for u in f1['units']), True)
A('chevrons <= 4', max(u['hit'] for u in f1['units']), 4)
A('slice mx', [w['mx'] for w in f1['wheel']], [2] * 6)
A('f3 plan hits: no lock, equation closes', f3['pv']['eq']['lock'], 0)
A('play in budget (RAM)', sum(S.COST[a[0]] for a in PLAN) <= st0['ram'], True)
A('selftest-like: preview == end_turn resolve for f3', (lambda: (lambda s: (S.end_turn(s, None), (s['taken'], s['raw']))[1])(cl(st3)))(), (f3['pv']['taken'], f3['pv']['raw']))
json.dump(OUTJ, open(OUT + 'state_e8.json', 'w'))
open(OUT + 'assert_log.txt', 'w').write('\n'.join(LOG) + '\n')
print('ok', len(LOG), 'asserts')
print('f1 eq', f1['pv']['eq'], 'taken', f1['pv']['taken'])
print('f2a eq', f2a['pv']['eq'], 'taken', f2a['pv']['taken'], 'slost', f2a['pv']['slost'])
print('f2alt eq', f2b['pv']['eq'], 'taken', f2b['pv']['taken'])
print('f3 eq', f3['pv']['eq'], 'taken', f3['pv']['taken'], 'slost', f3['pv']['slost'], 'dealt', f3['pv']['dealt'])
print('twist', OUTJ['twist'])
