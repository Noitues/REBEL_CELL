"""f1_infocheck: game-information checks for the F1 plates.
 A. text audit: the character inventory of everything drawn as text, F1 vs the approved E10 plate (order-free)
 B. tower numbers: pips / HP blocks / trim zones / guns recounted from the state against what the drawing functions are told to draw
 python f1_infocheck.py [text] [numbers]"""
import sys, os, json
sys.dont_write_bytecode = True
from collections import Counter
from PIL import ImageDraw
LOG = []
_orig = ImageDraw.ImageDraw.text


def _t(self, xy, text, *a, **k):
    LOG.append(str(text))
    return _orig(self, xy, text, *a, **k)


ImageDraw.ImageDraw.text = _t
import f1_render as R
import f1_tower as FT
import asm_r2 as A
J = A.J
E10 = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_e10_design/final/text_e10.json', encoding='utf-8'))
DEL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/xerox_flyer/'


def chars(lst):
    c = Counter()
    for t in lst:
        for ch in str(t).upper().replace(chr(215), 'X').replace(chr(0xfffd), 'X'):
            if ch.isalnum():
                c[ch] += 1
    return c


def text_audit():
    import f1_hand as FH
    tmp = 'D:/rc_scratch/combat_redesign/locked/wheel/work_text/'
    os.makedirs(tmp, exist_ok=True)
    FH.CACHE = tmp                 # render the card text again in this process so it is captured (the plates use cached card images)
    FH._mem.clear()
    FH._ui.clear()
    out = {}
    import glob
    for b in ('p1', 'p2', 'p2b', 'p3'):
        for fp in glob.glob(tmp + '*'):
            os.remove(fp)
        FH._mem.clear()
        FH._ui.clear()
        LOG.clear()
        R.render(b)
        mine = chars(LOG)
        e10 = chars(E10[b])
        miss = {k: v - mine.get(k, 0) for k, v in e10.items() if v > mine.get(k, 0)}
        extra = {k: v - e10.get(k, 0) for k, v in mine.items() if v > e10.get(k, 0)}
        out[b] = dict(chars_f1=sum(mine.values()), chars_e10=sum(e10.values()), missing_vs_e10=miss, extra_vs_e10=extra)
        print(b, out[b], flush=True)
    return out


def numbers():
    rep = {}
    for k in ('f1', 'f2', 'f2t', 'f2b'):
        f = J[k]
        r = {}
        ok = True
        for w in f['wheel']:
            st = FT.pip_states(w)
            ha = w.get('hp_after', w['hp'])
            exp_pending = max(0, w['hp'] - ha)
            got_pending = sum(1 for s in st if s in ('harm', 'soak'))
            got_soak = sum(1 for s in st if s == 'soak')
            ok &= (len(st) == w['mx'] and got_pending == exp_pending and got_soak == min(w.get('soaked', 0), exp_pending))
        r['slice_pips_match'] = bool(ok)
        hs = FT.hp_states(f['hp'], f['pv']['hp_after'], f['maxhp'])
        r['hp_ring'] = dict(blocks=len(hs), lit=hs.count('lit'), pending=hs.count('harm'), expected_lit=f['pv']['hp_after'], expected_pending=f['hp'] - f['pv']['hp_after'])
        r['hp_ring_match'] = r['hp_ring']['lit'] == r['hp_ring']['expected_lit'] and r['hp_ring']['pending'] == r['hp_ring']['expected_pending'] and len(hs) == f['maxhp']
        tz = FT.trim_data(f)
        exp = {}
        for u in f['units']:
            fz = u['fate']
            if fz['kind'] != 'lands' or u['consumed'] or u['trigdead']:
                continue
            for (sec, sl, hit, tohp) in fz['hits']:
                exp.setdefault(sec, set()).add(fz['k'])
        r['trim_zones'] = {str(s): sorted(v) for s, v in tz.items()}
        r['trim_match'] = {int(s): set(v) for s, v in tz.items()} == exp
        shots = sum(1 for g in f['guns'] for sh in g['shots'] if sh['uid'] is not None)
        r['guns'] = dict(shots=shots, idle=sum(1 for g in f['guns'] if not [s for s in g['shots'] if s['uid'] is not None]))
        rep[k] = r
    print(json.dumps({k: {x: v[x] for x in ('slice_pips_match', 'hp_ring_match', 'trim_match')} for k, v in rep.items()}))
    return rep


if __name__ == '__main__':
    want = sys.argv[1:] or ['numbers', 'text']
    res = {}
    if 'numbers' in want:
        res['numbers'] = numbers()
    if 'text' in want:
        res['text'] = text_audit()
    json.dump(res, open(DEL + 'game_info_check.json', 'w'), indent=1, default=str)
