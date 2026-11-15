"""tk_states: the fight states drawn by tk_render (data only).  Content follows the prototype (Campaign B v36) and build's
ENGINE_ORDER section A; words follow NAME_MAP (the old plan step WAVE is SURGE).
B-088 (designer on A-116): no itemised forecast list.  Each wedge carries its cumulative END TURN outcome; hovering a wedge
draws every arrow and effect feeding it, tagged with a resolution number = ENGINE_ORDER A3 step . order inside the step."""
import copy

TYPE_WORD = {'CACHE': 'CACHE', 'CORE': 'CORE', 'FIREWALL': 'FIREWALL', 'ICE': 'ICE', 'NODE': 'NODE', 'RELAY': 'RELAY',
             'SPAWNER': 'SPAWNER', 'TURRET': 'TURRET'}
HI = (242, 246, 255); MID = (175, 192, 214); GAIN = (123, 224, 123); HARM = (255, 68, 51); SCHED = (255, 140, 26)
PLAN = (255, 226, 0)


def seg(t, owner, hp, **kw):
    d = dict(type=t, owner=owner, hp=hp); d.update(kw); return d


# the hand: base = the locked card whose icon and band art the concept borrows (placeholder art); fam = the plate word
CARDS = {
    'NUDGE':    dict(base='Nudge',   nm='NUDGE',     txt='Spin 1 more or 1 less', cost=0, fam='CONTROL'),
    'WORM':     dict(base='Hold',    nm='WORM',      txt='1 virus on 3 corp segments', cost=1, fam='VIRUS'),
    'BREACH':   dict(base='Strike',  nm='BREACH',    txt='3 damage next to yours', cost=1, fam='FIRE'),
    'GUARD':    dict(base='Brace',   nm='GUARD',     txt='Block 3 on yours', cost=1, fam='BLOCK'),
    'TIMEBOMB': dict(base='Trigger', nm='TIME BOMB', txt='6 damage in 2 turns', cost=4, fam='DELAY'),
}


def hand(*names, why=None):
    out = []
    for n in names:
        c = dict(CARDS[n])
        if why and n in why:
            c['why'] = why[n]
        out.append(c)
    return out


# ------------------------------------------------------------------ BOARD: turn 3, play phase, nothing hovered (the rest state)
# END TURN (spin -2, arms FIREWALL, RELAY, CORE): virus ticks corp NODE 5 -> 4 (A3 step 5), RELAY repairs CORE 7 -> 9 (step 8),
# plan STRIKE 2 on your ICE is blocked by GUARD 2 (step 11), CORE's counterattack 3 retakes your ICE (step 13), -1 HP (step 16)
BOARD = dict(
    rot=0, ptrs=[0, 4, 8],
    segs=[seg('NODE', 'us', 6), seg('FIREWALL', 'us', 4), seg('FIREWALL', 'corp', 5, armed=1), seg('CACHE', 'corp', 3),
          seg('TURRET', 'corp', 6), seg('NODE', 'corp', 5, st=[('V1', 'runner')]), seg('RELAY', 'corp', 5, armed=1),
          seg('SPAWNER', 'corp', 4), seg('ICE', 'corp', 5), seg('NODE', 'corp', 5), seg('CORE', 'corp', 7, armed=1),
          seg('ICE', 'us', 3, st=[('G2', 'runner')])],
    hub=dict(top='CORP SPIN', big='−2', bot='then +1 +1 −2', arrow=-1),
    outcomes={5: dict(k='hp', t='→ 4'), 10: dict(k='hp', t='→ 9'), 11: dict(k='lose', t='LOST −1 HP')},
    hud=dict(title='STATIC ALLEY · T1 FIGHT', kind='FIREWALL WHEEL',
             rule='A segment next to a corp FIREWALL takes 1 less per hit',
             energy=(3, 3), turn=3, esc='from turn 13', runner='RHEE · RUN HEALTH', hp=(27, 30), hp_loss=1,
             plan=[('STRIKE 2', 'your weakest segment'), ('WALL', 'both sides of CORE'), ('SURGE 3', 'from CORE, both ways')],
             status=[('SHROUD 1', 'buff'), ('TRACED', 'debuff')], piles=(7, 3), owned_after=2,
             # designer 2026-11-15 (on A-116 Q2): at rest the forecast is on both, the wedges and the HUD (one totals line)
             forecast=[[('END TURN', HI), ('+0 taken', GAIN), ('−1 lost', HARM), ('→ owned 2', HI), ('· HP 27 → 26', HARM)]]),
    hand=hand('NUDGE', 'WORM', 'BREACH', 'GUARD', 'TIMEBOMB', why={'TIMEBOMB': 'needs 4 energy'}),
)


def derive(base, **kw):
    s = copy.deepcopy(base)
    hud = kw.pop('hud', None)
    s.update(kw)
    if hud:
        s['hud'].update(hud)
    return s


# ------------------------------------------------------------------ 1. PLAY: BREACH lifted; legal targets in FOCUS corners; the aimed take in grease pencil
_play_segs = copy.deepcopy(BOARD['segs']); _play_segs[2]['hp'] = 2
PLAY = derive(BOARD, segs=_play_segs, lift=2, focus=[2, 10], aim=2, pencil='TAKE',
              outcomes={2: dict(k='take', t='TAKEN'), 5: dict(k='hp', t='→ 4'), 10: dict(k='hp', t='→ 9'),
                        11: dict(k='lose', t='LOST −1 HP')},
              hud=dict(energy=(3, 3), owned_after=3,
                       forecast=[[('BREACH', PLAN), ('on FIREWALL 2: 3 damage, takes it', HI)],
                                 [('END TURN', HI), ('+1 taken', GAIN), ('−1 lost', HARM), ('→ owned 3', HI), ('· HP 27 → 26', HARM)]]))

# ------------------------------------------------------------------ 2. FORECAST: your ICE hovered; every arrow and effect feeding its outcome, numbered
_fc_segs = copy.deepcopy(BOARD['segs']); _fc_segs[11]['st'] = []       # the hover shows the GUARD as a numbered block plate instead
FORECAST = derive(BOARD, segs=_fc_segs, hover=11,
                  outcomes={5: dict(k='hp', t='→ 4'), 10: dict(k='hp', t='→ 9'), 11: dict(k='lose', t='LOST\n−1 HP', n='16.1')},
                  trace=[dict(src=('hub',), to=11, side='corp', n='11.1', amt='−2', da0=0.0, da1=0.12, r_to=262, bend=170, at_u=0.0),
                         dict(src=('self',), to=11, side='block', n='11.2', amt='BLOCK 2', at=(470, -0.12)),
                         dict(src=('seg', 10), to=11, side='corp', n='13.1', amt='−3', r0=330, da0=0.0, da1=-0.08, r_to=330, bend=430, at_u=0.5)],
                  # designer 2026-11-15: on hover, the numbered arrows on the wheel AND the same steps listed in the HUD
                  hud=dict(fc_hot=False, hp_n='16.1', forecast=[
                      [('YOUR ICE', (92, 225, 255)), ('3 → retaken', HARM), ('· health −1', HARM)],
                      [('11.1', SCHED), ('plan STRIKE: −2', MID)],
                      [('11.2', SCHED), ('your GUARD blocks 2', MID)],
                      [('13.1', SCHED), ('CORE counterattack: −3 → retaken', MID)],
                      [('16.1', SCHED), ('lost: run health 27 → 26', MID)]]))

# ------------------------------------------------------------------ 3. RESOLVE: the END TURN replay, at step 13; the played steps keep their numbered arrows
_res_segs = copy.deepcopy(BOARD['segs'])
_res_segs[11] = seg('ICE', 'corp', 2)
_res_segs[10]['hp'] = 9; _res_segs[5]['hp'] = 4; _res_segs[5]['st'] = []
RESOLVE = derive(BOARD, segs=_res_segs, outcomes={}, firing=[0, 4, 8], burst=[11],
                 trace=[dict(src=('seg', 6), to=10, side='corp', n='8.1', amt='+2', r0=340, da1=0.08, r_to=340, bend=420, at_u=0.5),
                        dict(src=('hub',), to=11, side='corp', n='11.1', amt='−2', da0=0.0, da1=0.12, r_to=262, bend=170, at_u=0.0),
                        dict(src=('self',), to=11, side='block', n='11.2', amt='BLOCK 2', at=(470, -0.12)),
                        dict(src=('seg', 10), to=11, side='corp', n='13.1', amt='−3', r0=330, da0=0.0, da1=-0.08, r_to=330, bend=430, at_u=0.5)],
                 hub=dict(top='END TURN', big='13', bot='COUNTER', col=(255, 140, 26)),
                 hud=dict(owned_after=None, hp=(27, 30), hp_loss=1, forecast=[]))

# ------------------------------------------------------------------ 4. WALL AND SEAL: both sides' walls and seals as physical pieces on the wheel
WALLSEAL = derive(BOARD, walls=[(3, 'corp'), (4, 'corp'), (0, 'runner')], seals=[(10, 'corp'), (1, 'runner')],
                  outcomes={5: dict(k='hp', t='→ 4'), 11: dict(k='lose', t='LOST −1 HP')},
                  hud=dict(plan=[('WALL', 'both sides of TURRET'), ('SEAL', 'CORE, one turn'), ('SURGE 3', 'from CORE, both ways')],
                           forecast=[[('END TURN', HI), ('+0 taken', GAIN), ('−1 lost', HARM), ('→ owned 2', HI), ('· HP 27 → 26', HARM)],
                                     [('WALL', HI), ('one turn', MID), ('SEAL', HI), ('immune this turn', MID)]]))

# ------------------------------------------------------------------ 5. WIN: the runner holds all 12 segments
WIN = derive(BOARD, segs=[dict(g, owner='us', armed=0, st=[]) for g in BOARD['segs']], outcomes={},
             hub=dict(top='', big='', bot=''), banner=('WHEEL TAKEN', '12 / 12 · TURN 7'), hand=[], btn=('CONTINUE', ''),
             hud=dict(turn=7, hp=(24, 30), hp_loss=0, owned_after=None, plan=[], status=[], piles=(11, 4),
                      forecast=[[('FIGHT WON', GAIN), ('the site is yours', HI)],
                                [('health 24 / 30 kept for the street', HI), ('· +6 credits', (255, 210, 77))]]))

STATES = {'board': BOARD, 'play': PLAY, 'forecast': FORECAST, 'resolve': RESOLVE, 'wallseal': WALLSEAL, 'win': WIN}
