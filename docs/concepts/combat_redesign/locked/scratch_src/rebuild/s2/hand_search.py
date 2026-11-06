"""stage 2: hand layout search for AD review 2.7 (whole card visible, 12 px margin above y = 1080) under the existing hand rules:
no hand pixel inside r455 of the board centre, none under SEND IT / UNDO, the lifted card (p2) clear of every sibling's cost hex and rules block.
Card scale stays 1.10 (card text cap heights depend on it).  Prints the best layouts; nothing is written to the generator."""
import sys, math, json, itertools
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image, ImageDraw
import card_render as CR

WORK = 'D:/rc_scratch/combat_redesign/locked/corp/work/'
J = json.load(open('D:/rc_scratch/combat_redesign/locked/corp/state_e10.json'))
z = np.load(WORK + 'masks_p1.npz')
um = lambda k: np.unpackbits(z[k])[:1080 * 1920].reshape(1080, 1920).astype(bool)
SEND, UNDO = um('send'), um('undo')
HH = 1200
SEND2 = np.zeros((HH, 1920), bool); SEND2[:1080] = SEND
UNDO2 = np.zeros((HH, 1920), bool); UNDO2[:1080] = UNDO
yy, xx = np.mgrid[0:HH, 0:1920]
D = np.hypot(xx - 536, yy - 540)
SCALE, LIFT_S = 1.10, 1.10
BOTTOM_MAX = 1068
_cache = {}


def card_alpha(name, mode, ang, scale):
    key = (name, mode, round(ang, 3), scale)
    if key not in _cache:
        im = CR.draw_card(name, 352, mode)
        k = scale / 2.0
        a = im.split()[3].resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
        if ang:
            a = a.rotate(ang, resample=Image.BICUBIC, expand=True)
        _cache[key] = (np.asarray(a) >= 128, im.width, im.height)
    return _cache[key]


def place(m, cx, cy):
    out = np.zeros((HH, 1920), bool)
    h, w = m.shape
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    xs0, ys0 = max(0, x0), max(0, y0)
    xs1, ys1 = min(1920, x0 + w), min(HH, y0 + h)
    out[ys0:ys1, xs0:xs1] = m[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0]
    return out


def slots(n, left, step, cy0, fan, droop=905.0):
    o = []
    for i in range(n):
        a = (i - (n - 1) / 2) * -fan
        th = math.radians(a)
        o.append(dict(cx=left + i * step, cy=cy0 + droop * th * th, ang=a))
    return o


def regions(name, cx, cy, ang, scale, w2, h2):
    sp = CR.CARDS[name]
    m2 = CR.margin_px(352)
    k = scale / 2.0
    W2, H2 = w2 * k, h2 * k
    a = math.radians(ang)

    def tr(p):
        x, y = (m2 + 2 * p[0]) * k - W2 / 2, (m2 + 2 * p[1]) * k - H2 / 2
        return (cx + x * math.cos(a) + y * math.sin(a), cy - x * math.sin(a) + y * math.cos(a))
    hx_, hy_ = CR.COST_C
    cost = [(hx_ + 22 * math.cos(math.radians(30 + 60 * q)), hy_ + 22 * math.sin(math.radians(30 + 60 * q))) for q in range(6)]
    rules = CR.rules_box(sp['txt'])
    img = Image.new('L', (1920, HH), 0)
    d = ImageDraw.Draw(img)
    d.polygon([tr(p) for p in cost], fill=255)
    d.polygon([tr(p) for p in rules], fill=255)
    return np.asarray(img) > 0


def hand_for(beat):
    BE = {'p1': 'f1', 'p2': 'f2', 'p3': 'f2'}
    f = J[BE[beat]]
    played = [a[0] for a in f['played']]
    hand = list(f['hand'])
    if beat == 'p3':
        hand = list(J['f1']['hand'])
        for c in played:
            hand.remove(c)
    return hand, (played if beat == 'p3' else [])


def evaluate(beat, left, step, cy0, fan, lift=None):
    hand, played = hand_for(beat)
    n = len(hand) + len(played)
    sl = slots(n, left, step, cy0, fan)
    hov = hand.index('Trigger') if (beat == 'p2') else None
    if hov is not None:
        for q in range(hov + 1, n):
            sl[q]['cx'] += lift['push']
    allm = np.zeros((HH, 1920), bool)
    rest = []
    for i, nm in enumerate(hand):
        if i == hov:
            continue
        m, w2, h2 = card_alpha(nm, 'normal', sl[i]['ang'], SCALE)
        pm = place(m, sl[i]['cx'], sl[i]['cy'])
        allm |= pm
        rest.append((nm, sl[i], w2, h2))
    for j, nm in enumerate(played):
        s = sl[len(hand) + j]
        m, _, _ = card_alpha(nm, 'played', 0.0, SCALE)          # played slots upright (2.3)
        allm |= place(m, s['cx'], s['cy'])
    res = {}
    if hov is not None:
        s = sl[hov]
        m, w2, h2 = card_alpha('Trigger', 'hover', 0.0, LIFT_S * SCALE)
        lm = place(m, s['cx'] + lift['dx'], lift['cy'])
        allm |= lm
        sib = 0
        for nm, s2, w2_, h2_ in rest:
            sib += int((lm & regions(nm, s2['cx'], s2['cy'], s2['ang'], SCALE, w2_, h2_)).sum())
        res['sib'] = sib
    rows = np.where(allm.any(1))[0]
    res['bottom'] = int(rows.max()) if len(rows) else 0
    res['minr'] = float(D[allm].min())
    res['send'] = int((allm & SEND2).sum())
    res['undo'] = int((allm & UNDO2).sum())
    cols = np.where(allm.any(0))[0]
    res['x'] = (int(cols.min()), int(cols.max()))
    res['ok'] = res['bottom'] <= BOTTOM_MAX and res['minr'] >= 455.0 and res['send'] == 0 and res['undo'] == 0 and res.get('sib', 0) == 0
    return res


if __name__ == '__main__':
    print('current p1', evaluate('p1', 1023, 168, 924, 4.0))
    best = []
    for fan in (4.0, 3.5, 3.0, 2.5, 2.0):
        for left in range(1023, 1046, 2):
            for cy0 in range(924, 896, -2):
                r1 = evaluate('p1', left, 168, cy0, fan)
                if not r1['ok']:
                    continue
                r3 = evaluate('p3', left, 168, cy0, fan)
                if not r3['ok']:
                    continue
                best.append((fan, left, cy0, r1, r3))
                break
        if best:
            pass
    best.sort(key=lambda b: (-b[0], -b[2], b[1]))
    for b in best[:12]:
        print('fan %.1f left %d cy0 %d  p1 %s  p3 %s' % b)
    json.dump([dict(fan=b[0], left=b[1], cy0=b[2], p1=b[3], p3=b[4]) for b in best], open('D:/rc_scratch/combat_redesign/locked/rebuild/s2/hand_search.json', 'w'), indent=1)
