"""tk_states: the fight states drawn by tk_render (data only).  Content follows the prototype (Campaign B v36) and build's
ENGINE_ORDER section A; words follow NAME_MAP (the old plan step WAVE is SURGE)."""
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
BOARD = dict(
    rot=0, ptrs=[0, 4, 8],
    segs=[seg('NODE', 'us', 6), seg('FIREWALL', 'us', 4), seg('FIREWALL', 'corp', 5, armed=1), seg('CACHE', 'corp', 3),
          seg('TURRET', 'corp', 6), seg('NODE', 'corp', 5, st=[('V1', 'runner')]), seg('RELAY', 'corp', 5, armed=1),
          seg('SPAWNER', 'corp', 4), seg('ICE', 'corp', 5), seg('NODE', 'corp', 5), seg('CORE', 'corp', 7, armed=1),
          seg('ICE', 'us', 3, st=[('G2', 'runner')])],
    hub=dict(top='CORP SPIN', big='−2', bot='then +1 +1 −2', arrow=-1),
    chips=[dict(hp=6), dict(hp=4), dict(hp=6, fires=1), dict(hp=3), dict(hp=6), dict(hp=4), dict(hp=5, fires=1), dict(hp=4),
           dict(hp=5), dict(hp=5), dict(hp=7, fires=1), dict(hp=0, k='lose')],
    retake_tags=[11],
    hud=dict(title='STATIC ALLEY · T1 FIGHT', kind='FIREWALL WHEEL',
             rule='A segment next to a corp FIREWALL takes 1 less per hit',
             energy=(3, 3), turn=3, esc='from turn 13', runner='RHEE · RUN HEALTH', hp=(27, 30), hp_loss=1,
             plan=[('STRIKE 2', 'your weakest segment'), ('WALL', 'both sides of CORE'), ('SURGE 3', 'from CORE, both ways')],
             status=[('SHROUD 1', 'buff'), ('TRACED', 'debuff')], piles=(7, 3), owned_after=2,
             forecast=[[('END TURN', HI), ('spin −2', SCHED), ('· arms FIREWALL, RELAY, CORE', MID)],
                       [('+0 taken', GAIN), ('−1 lost', HARM), ('→ owned 2', HI), ('· health 27 → 26', HARM)]]),
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
              chips=[dict(hp=6), dict(hp=4), dict(hp=3, k='take'), dict(hp=3), dict(hp=6), dict(hp=4), dict(hp=5, fires=1), dict(hp=4),
                     dict(hp=5), dict(hp=5), dict(hp=7, fires=1), dict(hp=0, k='lose')],
              hud=dict(energy=(3, 3), owned_after=3,
                       forecast=[[('BREACH', PLAN), ('on FIREWALL 2: 3 damage, takes it', HI)],
                                 [('then END TURN', MID), ('+1 taken', GAIN), ('−1 lost', HARM), ('→ owned 3', HI), ('· health 27 → 26', HARM)]]))

# ------------------------------------------------------------------ 2. FORECAST: END TURN hovered; the HUD itemises what END TURN will do, in order
FORECAST = derive(BOARD, hud=dict(fc_hot=True, forecast=[
    [('END TURN', HI), ('spin −2', SCHED), ('· arms FIREWALL, RELAY, CORE', MID)],
    [('1  FIREWALL', HI), ('shields its corp neighbors', MID)],
    [('2  RELAY', HI), ('repairs CORE +2', MID)],
    [('3  plan STRIKE 2', SCHED), ('hits your ICE: GUARD 2 blocks it', MID)],
    [('4  counterattack', HI), ('3 on your ICE → retaken', HARM)],
    [('+0 taken', GAIN), ('−1 lost', HARM), ('→ owned 2', HI), ('· health 27 → 26', HARM)]]))

# ------------------------------------------------------------------ 3. RESOLVE: the END TURN replay; pointers fire, the corp retakes your ICE
_res_segs = copy.deepcopy(BOARD['segs'])
_res_segs[11] = seg('ICE', 'corp', 2)
_res_segs[4]['armed'] = 1
RESOLVE = derive(BOARD, segs=_res_segs, chips=None, retake_tags=[], firing=[0, 4, 8], burst=[11],
                 arrows=[(4, 1, 'corp'), (0, 2, 'runner'), (10, 11, 'corp')],
                 hub=dict(top='END TURN', big='3 / 5', bot='SPACE skips', col=(255, 140, 26)),
                 hud=dict(owned_after=None, hp=(27, 30), hp_loss=1, forecast=[
                     [('REPLAY', SCHED), ('step 3 of 5: counterattack', HI)],
                     [('TURRET fires', HARM), ('3 on your FIREWALL → 1 left', MID)],
                     [('your NODE fires', (255, 61, 168)), ('2 on corp FIREWALL', MID)],
                     [('RETAKE', HARM), ('corp takes back ICE · health 27 → 26', HI)]]))

# ------------------------------------------------------------------ 4. WALL AND SEAL: both sides' walls and seals as physical pieces on the wheel
_ws_segs = copy.deepcopy(BOARD['segs'])
WALLSEAL = derive(BOARD, segs=_ws_segs, walls=[(3, 'corp'), (4, 'corp'), (0, 'runner')], seals=[(10, 'corp'), (1, 'runner')],
                  hud=dict(plan=[('WALL', 'both sides of TURRET'), ('SEAL', 'CORE, one turn'), ('SURGE 3', 'from CORE, both ways')],
                           forecast=[[('WALLS', HI), ('last one turn · a SEAL is immune to everything', MID)],
                                     [('corp WALL', (217, 225, 234)), ('around TURRET: you cannot cross it', MID)],
                                     [('your WALL', (255, 61, 168)), ('NODE | FIREWALL: corp hits stop there', MID)],
                                     [('SEALED', (184, 220, 204)), ('CORE · your SEAL on FIREWALL: it does not fire', MID)]]))

# ------------------------------------------------------------------ 5. WIN: the runner holds all 12 segments
WIN = derive(BOARD, segs=[dict(g, owner='us', armed=0, st=[]) for g in BOARD['segs']], chips=None, retake_tags=[],
             hub=dict(top='', big='', bot=''), banner=('WHEEL TAKEN', '12 / 12 · TURN 7'), hand=[], btn=('CONTINUE', ''),
             hud=dict(turn=7, hp=(24, 30), hp_loss=0, owned_after=None, plan=[], status=[], piles=(11, 4),
                      forecast=[[('FIGHT WON', GAIN), ('the site is yours', HI)],
                                [('health 24 / 30 kept for the street', HI), ('· +6 credits', (255, 210, 77))]]))

STATES = {'board': BOARD, 'play': PLAY, 'forecast': FORECAST, 'resolve': RESOLVE, 'wallseal': WALLSEAL, 'win': WIN}
