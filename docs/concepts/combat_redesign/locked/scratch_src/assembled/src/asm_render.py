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
HERE = 'D:/rc_scratch/combat_redesign/locked/assembled/'
sfx = beat + ('' if room == 'bio' else '_' + room)

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
    _cap('tickets', A.M2, 'future')

t = time.time()
im = R.render(beat, room=ROOMS[room], check=False)
if check:
    # draw asserts (non raising) on the same frame
    f = A.J[R.KEY[beat]]
    for e_ in A.AU.BADGE_LOG:
        for k_ in ('tag', 'tray', 'chev', 'glyph'):
            AD('%s unit %d %s badge (%s side) px on %s' % (beat, e_['uid'], e_['badge'], e_['side'], k_), e_['hits'][k_], 0)
    try:
        B10.draw_asserts(beat, f)
    except Exception as e:
        LOGD.append(dict(name='draw_asserts crashed', ok=False, got=repr(e)[:200], want=''))
os.makedirs(HERE + 'out', exist_ok=True)
im.save(HERE + 'out/as_%s.png' % sfx)
rep = dict(textlog=TEXTLOG, cardlog=CARDLOG, beat=beat, room=room, asserts=LOGD, dash_calls=len(R.DASH_LOG), dot_calls=len(R.DOT_LOG), dash_log=[str(x) for x in R.DASH_LOG])
if check:
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
