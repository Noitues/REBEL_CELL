"""asm_render: render one assembled plate (locked wheel + locked WPAP cards) with checks captured.
python asm_render.py <beat> [room bio|srv|gh] [check 0|1]
 -> out/as_<beat>[_<room>].png ; work/chk_<beat>[_<room>].json (draw asserts, collision overlaps, dash log)"""
import sys, os, json, time
sys.dont_write_bytecode = True
beat = sys.argv[1] if len(sys.argv) > 1 else 'p1'
room = sys.argv[2] if len(sys.argv) > 2 else 'bio'
check = (sys.argv[3] if len(sys.argv) > 3 else '1') == '1'
from PIL import ImageDraw
TEXTLOG = []
_otext = ImageDraw.ImageDraw.text


def _t(self, xy, text, *a, **k):
    TEXTLOG.append(str(text))
    return _otext(self, xy, text, *a, **k)


ImageDraw.ImageDraw.text = _t
import lw_render as LW
import card_render as CR
CARDLOG = {}
_CUR = [None]
_orb = CR.render_base
_otx = CR.text


def _rb(spec, nowords=False, R=4.0, seed=0):
    _CUR[0] = (spec['name'], bool(nowords))
    return _orb(spec, nowords, R, seed)


def _tx(cv, txt, *a, **k):
    if _CUR[0] is not None:
        CARDLOG.setdefault('%s|%d' % _CUR[0], []).append(txt)
    return _otx(cv, txt, *a, **k)


CR.render_base = _rb
CR.text = _tx
import numpy as np
from PIL import Image
R = LW.R
A = R.A
ROOMS = {'bio': R.ROOM, 'srv': 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_srv_bare.png',
         'gh': 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/room_gh_bare.png'}
HERE = 'D:/rc_scratch/combat_redesign/locked/corp/'
sfx = beat + ('' if room == 'bio' else '_' + room)
CORP = os.environ.get('CORP', 'neutral')
if CORP != 'neutral':
    sfx = sfx + '_' + CORP

# ---- non raising AD
LOGD = []
B10 = A.B10


def AD(name, got, want):
    ok = got == want
    LOGD.append(dict(name=name, ok=bool(ok), got=str(got), want=str(want)))


B10.AD = AD

# ---- mask capture per element class
MASKS = {}


def _cap(cls, fn_owner, fn_name, Lidx=0):
    orig = getattr(fn_owner, fn_name)

    def wrap(*a, **k):
        L = a[Lidx]
        T = R.L2()
        a2 = list(a)
        a2[Lidx] = T
        r = orig(*a2, **k)
        L.im.alpha_composite(T.im)
        al = T.im.split()[3].resize((1920, 1080), Image.BOX)
        m = np.asarray(al) >= 128
        MASKS[cls] = MASKS.get(cls, np.zeros((1080, 1920), bool)) | m
        return r
    setattr(fn_owner, fn_name, wrap)


if check:
    _cap('digits', A.S2, 'digits')
    _cap('labels', A.S2, 'labels')
    _cap('tags', A.M2, 'ring_tags')
    _cap('tags', A.P2, 'refund_place')
    _cap('badges', A.P2, 'twist_badge')
    _cap('badges', A.AU, 'warded_badge')
    _cap('badges', A.AU, 'dead_badge')
    _cap('tags', A.H2, 'hover_tag')
    _cap('leader', A.H2, 'leader')        # the hover leader line (inside hover_tag): its own class, see ALLOWED
    _cap('tickets', A.M2, 'future')
    # O-29: occluders.  The THIS TURN tape (cell, label, chevrons), the hold / +N label plates, and the hand.
    _cap('tape', A.S2, 'live_cell')
    _cap('tape', A.S2, 'live_label')
    _cap('tape', A.S2, 'chevrons')
    _cap('plates', A.S2, 'hold_cell')
    _cap('plates', A.S2, 'hold_live')
    _cap('plates', A.S2.S, 'plus_cell')
    _odh = R.FH.draw_hand

    def _hand(base, *a, **k):
        from PIL import Image as _I
        T = _I.new('RGBA', base.size, (0, 0, 0, 0))
        r = _odh(T, *a, **k)
        base.alpha_composite(T)
        MASKS['hand'] = np.asarray(T.split()[3]) >= 128
        return r
    R.FH.draw_hand = _hand
OCCLUDERS = ('tape', 'plates', 'hand')
MARKS = ('digits', 'labels', 'tags', 'badges', 'tickets', 'leader')
# a HOLD label is printed on its own plate by design; the 1.6 px hover leader has to cross the schedule band to reach its tag
# outside the board (it is keylined and crosses at one point); it may never touch a digit, label, badge or the hand
ALLOWED = {('labels', 'plates'), ('leader', 'tape'), ('leader', 'plates')}

t = time.time()
im = R.render(beat, room=ROOMS[room], check=False)
if check:
    # draw asserts (non raising) on the same frame
    f = A.J[R.KEY[beat]]
    for e_ in A.AU.BADGE_LOG:
        for k_ in ('tag', 'tray', 'chev', 'glyph', 'band'):
            AD('%s unit %d %s badge (%s side) px on %s' % (beat, e_['uid'], e_['badge'], e_['side'], k_), e_['hits'][k_], 0)
    try:
        B10.draw_asserts(beat, f)
    except Exception as e:
        LOGD.append(dict(name='draw_asserts crashed', ok=False, got=repr(e)[:200], want=''))
os.makedirs(HERE + 'out', exist_ok=True)
im.save(HERE + 'out/as_%s.png' % sfx)
rep = dict(textlog=TEXTLOG, cardlog=CARDLOG, beat=beat, room=room, asserts=LOGD, dash_calls=len(R.DASH_LOG), dot_calls=len(R.DOT_LOG), dash_log=[str(x) for x in R.DASH_LOG])
if check:
    # the schedule layer is punched round every digit after drawing (r2_sched.punch_digits): apply the same holes to the tape / plate masks
    yy_, xx_ = np.mgrid[0:1080, 0:1920]
    holes = np.zeros((1080, 1920), bool)
    for s_ in range(6):
        hx_, hy_ = A.S2.digit_xy(s_)
        holes |= np.hypot(xx_ - hx_, yy_ - hy_) <= A.S2.BOSS_R + A.S2.DIGIT_GAP
    for c_ in ('tape', 'plates'):
        if c_ in MASKS:
            MASKS[c_] = MASKS[c_] & ~holes
    if 'leader' in MASKS and 'tags' in MASKS:
        MASKS['tags'] = MASKS['tags'] & ~MASKS['leader']
    occ = {}
    for mk in MARKS:
        for oc in OCCLUDERS:
            if (mk, oc) in ALLOWED or mk not in MASKS or oc not in MASKS:
                continue
            occ['%s x %s' % (mk, oc)] = int((MASKS[mk] & MASKS[oc]).sum())
    hb = {}
    if 'hand' in MASKS:
        hm = MASKS['hand']
        d_ = np.hypot(xx_ - 536, yy_ - 540)
        hb['hand_min_r_px'] = round(float(d_[hm].min()), 1) if hm.any() else None
        hb['hand_px_inside_r455'] = int((hm & (d_ < R.FH.HAND_MIN_R)).sum())
        hb['hand_px_on_board_marks'] = int(sum((hm & MASKS[c_]).sum() for c_ in MARKS + ('tape', 'plates') if c_ in MASKS))
        hb['pass'] = hb['hand_px_inside_r455'] == 0 and hb['hand_px_on_board_marks'] == 0
    rep['occlusion_px'] = occ
    rep['occlusion_pass'] = all(v == 0 for v in occ.values())
    rep['hand_vs_board'] = hb
    cls = sorted(MASKS)
    ov = {}
    for i in range(len(cls)):
        for j in range(i + 1, len(cls)):
            ov['%s x %s' % (cls[i], cls[j])] = int((MASKS[cls[i]] & MASKS[cls[j]]).sum())
    rep['mask_px'] = {c: int(MASKS[c].sum()) for c in cls}
    rep['overlap_px'] = ov
    np.savez_compressed(HERE + 'work/masks_%s.npz' % sfx, **{c: np.packbits(MASKS[c]) for c in cls})
json.dump(rep, open(HERE + 'work/chk_%s.json' % sfx, 'w'), indent=1)
print('ok', sfx, round(time.time() - t, 1), 'asserts', len(LOGD), 'fail', sum(1 for x in LOGD if not x['ok']), flush=True)
