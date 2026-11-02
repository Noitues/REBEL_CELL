"""asm_checks: aggregate the assembled-plate checks -> checks.json, before_after.jpg, squint images.
python asm_checks.py   (run after asm_render.py has written work/chk_*.json and out/as_*.png)"""
import sys, os, json, re, shutil
sys.dont_write_bytecode = True
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = 'D:/rc_scratch/combat_redesign/locked/assembled/'
OUT = HERE + 'out/'
WORK = HERE + 'work/'
DEL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/assembled/'
CONC = 'D:/rc_art/art-pass/docs/concepts/'
E10F = CONC + 'combat_e10_design/final/'
F1D = CONC + 'combat_redesign/finalist_1/'
WHD = CONC + 'combat_redesign/locked/wheel/'
FD = 'D:/rc_art/art-pass/assets/fonts/'
os.makedirs(DEL, exist_ok=True)
mo = ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', 22)
an = ImageFont.truetype(FD + 'Anton-Regular.ttf', 30)
J = json.load(open(HERE + 'state_e10.json'))
REP = {}

PL = [('p1_decide', 'p1'), ('p2_preview', 'p2'), ('p2b_hover', 'p2b'), ('p3_resolve', 'p3'), ('p1_nowords', 'nowords'), ('p1_decide_srv', 'p1_srv'), ('p1_decide_gh', 'p1_gh')]
SFX = {'p1': 'p1', 'p2': 'p2', 'p2b': 'p2b', 'p3': 'p3', 'nowords': 'nowords', 'p1_srv': 'p1_srv', 'p1_gh': 'p1_gh'}


def chk(sfx):
    fp = WORK + 'chk_%s.json' % sfx
    return json.load(open(fp)) if os.path.exists(fp) else None


# ------------------------------------------------------------------ 1. draw asserts + collision
C = {}
da = {}
for name, sfx in PL:
    c = chk(sfx)
    if not c:
        da[name] = 'missing'
        continue
    A_ = c['asserts']
    fails = [x for x in A_ if not x['ok']]
    cls = Counter()
    for x in A_:
        t = re.sub(r'\d+', 'N', x['name'])
        cls[(t, x['ok'])] += 1
    da[name] = dict(total=len(A_), passed=len(A_) - len(fails), failed=len(fails),
                    failures=[dict(name=x['name'], got=x['got'][:160], want=x['want'][:160]) for x in fails][:40])
    C[name] = dict(mask_px=c.get('mask_px'), overlap_px=c.get('overlap_px'))
REP['draw_asserts'] = da
REP['collision'] = C
REP['collision_total_px'] = {k: (sum(v['overlap_px'].values()) if v.get('overlap_px') else None) for k, v in C.items()}

# ------------------------------------------------------------------ 2. dash audit
dash = {}
for name, sfx in PL:
    c = chk(sfx)
    if c:
        dash[name] = dict(dashed_line_calls=c['dash_calls'], dotted_mark_calls=c['dot_calls'])
# code audit of the modules this assembly adds / swaps in
mods = ['card_render.py', 'lw_tower.py', 'lw_ui.py', 'lw_skin.py', 'lw_install.py', 'asm_render.py', 'f1_hand.py']
code = {}
for m in mods:
    s = open(HERE + 'src/' + m, encoding='utf-8').read()
    code[m] = dict(dash_args=len(re.findall(r'dash\s*=\s*\(', s)), dashed_fn=len(re.findall(r'dashed\w*\(', s)), setLineDash=len(re.findall(r'setLineDash', s)))
REP['dash_audit'] = dict(runtime=dash, code=code)

# ------------------------------------------------------------------ 3. squint
lum = lambda a: 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
Cc = (536, 540)


def squint(img, region=None):
    s = img.resize((img.width // 16, img.height // 16), Image.BOX).filter(ImageFilter.GaussianBlur(1.0))
    l = lum(np.asarray(s, np.float32) / 255.0)
    if region is not None:
        yy, xx = np.mgrid[0:l.shape[0], 0:l.shape[1]]
        l = l[region(xx * 16 + 8, yy * 16 + 8)]
    return dict(mean=round(float(l.mean()), 4), p95=round(float(np.percentile(l, 95)), 4), loud=round(float((l > 0.38).mean()), 4))


d_ = lambda x, y: np.hypot(x - Cc[0], y - Cc[1])
REG = {'plate': None, 'board_disc_r<=490': lambda x, y: d_(x, y) <= 490, 'tower_r<=212': lambda x, y: d_(x, y) <= 212,
       'rings_r214-430': lambda x, y: (d_(x, y) >= 214) & (d_(x, y) <= 430),
       'hand_zone': lambda x, y: (x >= 840) & (x <= 1660) & (y >= 780), 'send_it': lambda x, y: (x >= 1660) & (x <= 1900) & (y >= 900) & (y <= 1020),
       'hud': lambda x, y: (x >= 1070) & (y <= 400)}
sq = {}
src = {}
for name, sfx in PL[:5]:
    imgs = {'e10': E10F + name + '.png', 'f1': F1D + name + '.png', 'locked': OUT + 'as_%s.png' % sfx}
    sq[name] = {}
    for rn, rf in REG.items():
        sq[name][rn] = {k: squint(Image.open(v).convert('RGB'), rf) for k, v in imgs.items() if os.path.exists(v)}
REP['squint'] = sq
REP['squint_note'] = '1/16 BOX downscale + 1 px blur, relative luminance; loud = share of 16 px cells above 0.38. hand_zone x>=840 (the wheel hand reaches x=840).'

# ------------------------------------------------------------------ 4. game information
info = {}
import importlib
sys.path.insert(0, HERE + 'src')
import card_render as CR
import build10 as B10m
E10C = B10m.CARDS
rows = {}
for n, (cost, loud) in J['cards'].items():
    sp = CR.CARDS[n]
    e = E10C[n]
    rows[n] = dict(state_cost=cost, state_trace=loud, drawn_cost=sp['cost'], drawn_trace=sp['loud'], e10_name=e.get('nm'), drawn_name=sp['nm'], e10_text=e.get('txt'), drawn_text=sp['txt'], e10_type=e.get('fam'), drawn_type=sp['fam'],
                   e10_mult=e.get('mult', e.get('num')), drawn_mult=sp.get('mult'),
                   ok=bool(cost == sp['cost'] and loud == sp['loud'] and e.get('nm') == sp['nm'] and e.get('txt') == sp['txt'] and e.get('fam') == sp['fam']))
info['cards_table'] = rows
info['cards_table_all_ok'] = all(r['ok'] for r in rows.values())

norm = lambda s: re.sub(r'[^A-Z0-9]', '', str(s).upper().replace('\u00d7', 'X'))
drawn = {}
beats_hand = {'p1': J['f1']['hand'], 'p2': J['f2']['hand'], 'p2b': J['f1']['hand'], 'p3': [c for c in J['f1']['hand'] if c not in [a[0] for a in J['f2']['played']]], 'p1_srv': J['f1']['hand'], 'p1_gh': J['f1']['hand']}
for name, sfx in PL:
    c = chk(sfx)
    if not c or sfx == 'nowords':
        continue
    cl = c['cardlog']
    r = {}
    for card in beats_hand[sfx]:
        keys = [k for k in cl if k.startswith(card + '|0')]
        strs = cl[keys[0]] if keys else []
        sp = CR.CARDS[card]
        exp = [sp['nm'], sp['fam'], sp['txt'], str(sp['cost'])] + (['+' + str(sp['loud'])] if sp['loud'] else []) + (['\u00d7' + sp['mult']] if sp.get('mult') else [])
        miss = [e for e in exp if e not in strs]
        extra = [s for s in strs if s not in exp and s != 'PLAYED']      # PLAYED is the played-slot liner word (p3), not a card field
        st_cost, st_loud = J['cards'][card]
        r[card] = dict(drawn_strings=strs, expected=exp, missing=miss, extra=extra, state_cost=st_cost, state_trace=st_loud,
                       cost_in_plate=str(st_cost) in strs, trace_in_plate=(('+' + str(st_loud)) in strs) if st_loud else ('no trace tab (state 0)' if not any(s.startswith('+') for s in strs) else 'UNEXPECTED trace tab'), ok=not miss and not extra)
    drawn[name] = r
info['cards_drawn'] = drawn
info['cards_drawn_all_ok'] = all(v['ok'] for b in drawn.values() for v in b.values())

# text inventory vs E10 final
E10T = json.load(open(E10F + 'text_e10.json', encoding='utf-8'))


def chars(lst):
    cc = Counter()
    for t in lst:
        for ch in str(t).upper().replace(chr(215), 'X').replace(chr(0xfffd), 'X'):
            if ch.isalnum():
                cc[ch] += 1
    return cc


inv = {}
words_in = {}
f = J['f1']
f2 = J['f2']
req = {
    'p1': ['TURN', 'SHIFTING WAVES', 'WAVES %d LEFT' % f['waves_left'], 'W4', 'W5', 'W6', 'NOW W1', '+1 W2', '+2 W3', 'YOU', 'LANDS', 'THROUGH', 'RAW', 'SHOT', 'BRACE', 'RIDER', 'SPLIT', 'ABSORBED', 'SOAK', 'NEXT', 'WIN', 'SLICES KEPT', 'KILL ADJUSTER', 'TRACE LOW', 'RAM', 'TRACE', 'ENDS = HEAT', 'BREAKER', 'SEND IT', 'UNDO', 'CELL-9'],
}
for name, sfx in PL:
    c = chk(sfx)
    if not c:
        continue
    log = c['textlog']
    mine = chars(log)
    key = {'p1': 'p1', 'p2': 'p2', 'p2b': 'p2b', 'p3': 'p3', 'nowords': 'nowords', 'p1_srv': 'p1', 'p1_gh': 'p1'}[sfx]
    e10 = chars(E10T[key]) if key in E10T else Counter()
    inv[name] = dict(chars_locked=sum(mine.values()), chars_e10=sum(e10.values()),
                     missing_vs_e10={k: v - mine.get(k, 0) for k, v in e10.items() if v > mine.get(k, 0)},
                     extra_vs_e10={k: v - e10.get(k, 0) for k, v in mine.items() if v > e10.get(k, 0)})
    joined = ' '.join(log)
    jn = norm(''.join(log))
    if sfx != 'nowords':
        need = req['p1']
        words_in[name] = {w: (norm(w) in jn) for w in need}
info['text_inventory_vs_e10'] = inv
info['required_words_present'] = words_in
info['required_words_missing'] = {k: [w for w, v in d.items() if not v] for k, d in words_in.items()}
nw = chk('nowords')
if nw:
    alnum = [t for t in nw['textlog'] if any(ch.isalnum() for ch in t)]
    info['nowords_alnum_strings_drawn_by_text_calls'] = dict(count=len(alnum), sample=alnum[:30])
REP['game_info'] = info

json.dump(REP, open(OUT + 'checks_partial.json', 'w'), indent=1, default=str)
print('checks_partial.json written')


# ------------------------------------------------------------------ 5. before / after
def L_(im, text, xy=(10, 6), col=(255, 226, 0)):
    ImageDraw.Draw(im).text(xy, text, font=mo, fill=col)


names = [('E10 design final (before)', E10F + 'p1_decide.png'), ('F1 black-book (previous)', F1D + 'p1_decide.png'), ('Locked: wheel + WPAP cards (after)', OUT + 'as_p1.png')]
W3, H3 = 960, 540
hc = (830, 740, 1910, 1080)
hs = W3 / (hc[2] - hc[0])
Hh = int((hc[3] - hc[1]) * hs)
wc = (330, 300, 760, 760)
sheet = Image.new('RGB', (W3 * 3 + 40, 56 + H3 + 10 + Hh + 10 + 460 + 10 + H3 // 2), (14, 12, 22))
dd = ImageDraw.Draw(sheet)
dd.text((16, 12), 'p1_decide, bio cutaway: E10 design final  |  F1  |  locked (xerox/linocut spinner, neutral corp side, WPAP cards)', font=an, fill=(255, 255, 255))
for i, (t, p) in enumerate(names):
    im = Image.open(p).convert('RGB')
    x = 16 + i * (W3 + 4)
    a = im.resize((W3, H3), Image.LANCZOS)
    L_(a, t)
    sheet.paste(a, (x, 56))
    c = im.crop(hc).resize((W3, Hh), Image.LANCZOS)
    sheet.paste(c, (x, 56 + H3 + 10))
    w_ = im.crop(wc)
    w_ = w_.resize((int(w_.width * 460 / w_.height), 460), Image.LANCZOS)
    sheet.paste(w_, (x + (W3 - w_.width) // 2, 56 + H3 + 10 + Hh + 10))
    s = im.resize((im.width // 16, im.height // 16), Image.BOX).filter(ImageFilter.GaussianBlur(1.0)).resize((W3 // 2, H3 // 2), Image.NEAREST)
    sheet.paste(s, (x + (W3 - s.width) // 2, 56 + H3 + 10 + Hh + 10 + 470))
sheet.save(DEL + 'before_after.jpg', quality=90)
print('before_after written')

# ------------------------------------------------------------------ 6. numbers + write
nfp = WORK + 'numbers.json'
if os.path.exists(nfp):
    REP['game_info']['tower_numbers'] = json.load(open(nfp))
json.dump(REP, open(DEL + 'checks.json', 'w'), indent=1, default=str)
print('checks.json written')
