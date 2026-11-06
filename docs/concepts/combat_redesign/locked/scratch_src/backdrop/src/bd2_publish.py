"""bd2_publish.py : write the stage-2 backdrop deliverables (review 2.8, grade rb2-1) to docs/concepts/combat_redesign/locked/backdrop/.
p1_<room>.png (neutral, 7 rooms), p1_bio_solace.png, p1_shop_meridian.png, before_after.jpg, grade.json, checks.json.
Plates are F + T * backdrop from the current p1 board (fg_extract.py, rebuild stage 2 generator).  Every plate is run through the full
rb_checks (a-e) with the p1 capture of its skin, so the backdrop plates carry the same five checks as the final set; the room numbers
(rb_checks room region, L* of the mean luminance) and the reviewer's two probe boxes are reported before (step6-1) and after (rb2-1)."""
import sys, json, os
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/backdrop/src')
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import bd2_lib as L
import bd_grade as BG
import bd_measure as M
import rb_checks as RC
import rb_tokens as TK

DST = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/backdrop/'
BOARD = 'D:/rc_scratch/combat_redesign/locked/rebuild/board/'
TMP = L.HERE + 'work/pub2/'
os.makedirs(TMP, exist_ok=True)
fnt = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 22)
JOBS = [(r, 'neutral', r, 'p1_%s' % r) for r in L.ROOMS] + [('bio', 'solace', 'bio', 'p1_bio_solace'), ('shop', 'meridian', 'shop_meridian', 'p1_shop_meridian')]
SFX = {'neutral': 'p1', 'solace': 'p1_solace', 'meridian': 'p1_meridian'}
# before = the published step-6 grade of the room this skin used before stage 2 (Meridian was on the bio lab)
BEFORE_ROOM = {('shop', 'meridian'): 'bio'}

checks = dict(method=dict(
    composite='plate = F + T * backdrop; F, T from two renders of the current p1 board (corp/src generator with rb_patch + rb2_patch) with flat 0 and '
              '128 backdrops (fg_extract.py), per skin.  Cross-checked against the real renders in locked/rebuild/board/ (real_render_vs_composite).',
    room_numbers='rb_checks room region: x >= 1100, y >= 420, r > 505 from (536, 540), HUD / hand / SEND IT / UNDO / nameplate / YOU / hover tag cut out '
                 '(dilated 4 px), and the UI scrim slabs where they darken the room by 15 % or more; L* = CIE L* of the mean luminance (reviewer '
                 'measure.py); p95 = 95th percentile of per-pixel L*.  bd2_lib.stats uses the same region from the p1 capture of the skin.',
    gate='room mean L* 28-34 and room p95 + 1 <= ring-NOW occupied glass p95 (rb_checks b); plus all five rb_checks on every plate',
    squint='locked final_checks metric (1/16 BOX + 1 px blur, Rec709 luma, loud > 0.38), reported for continuity with step 6',
    before='step6-1: bd_grade.grade(ROOMS_STEP61[room]) + scrim(P), on the same current board', after='rb2-1: bd_grade.grade(ROOMS[key]) + scrim(P)'),
    plates={})
grade = dict(version=BG.GRADE_VERSION, applies_to='room_<n>_bare.png (combat_backdrop/v3_1), before the board scrim; screen space 1920x1080',
             colour_space='all maths on gamma-encoded sRGB values in 0-1 (the PNG values); blur radii are gaussian radii at 1920x1080; scale with resolution',
             replaces='step6-1 (room mean L* 21 in the reviewer box: AD review 2.8 "the room grade switched the room off")',
             corp_room=BG.CORP_ROOM,
             tuning='shared recipe (bd2_solve.SHARED) + the step6-1 per-room chroma / contrast / pink pull; the shoulder ceiling ceil is solved per '
                    'room so the rb_checks room region reads p95 L* 38 on p1 composites (the mean follows; tone_lo 0.17 in every room).  On the 15 real '
                    'renders of the final set (locked/final/checks.json rb_checks) the room reads mean L* 31.2-32.2, p95 37.5-38.1 on every beat and skin.  '
                    'shop_meridian adds the Meridian corp light (hue 88-162 pulled to 20 deg by 0.88, '
                    'chroma 1.05, neon 0.9) and its spill colour is taken after that light.',
             order=['1 focus hull m: polygon hull_poly (the cutaway box: walls + floor slab), m = 1 - smoothstep(-pf0, pf1, sdf) (sdf in px, + outside); '
                    'd = the ellipse distance (cx, cy, rx, ry) for the vignette, spill and tone reach',
                    '2 blur ramp: hull_blur -> mid_blur -> city_blur, smoothsteps on the sdf from -pf0 to pf1 + blur_reach (one ramp, no cross-fade)',
                    '2b corp light (only when hue_amt > 0): w = window(hue_lo - hue_f .. hue_lo, hue_hi .. hue_hi + hue_f) * smoothstep(.10, .30, S); '
                    'rotate the pixel about the grey axis by (hue_to - hue) * hue_amt * w, Rec709 luma kept',
                    '3 chroma: lerp to Rec709 luma; k = chroma * (1 - (1 - neon_chroma) * neon) * (1 - (1 - pink_chroma) * pink) * (m + city_chroma * (1 - m))',
                    '4 contrast: c = pivot + (c - pivot) * contrast',
                    '5 value: * (hull_value * m + city_value * (1 - m))',
                    '5b local tone: x = gaussian(luma, tone_blur); target = tone_lo + (tone_hi - tone_lo) * (1 - exp(-x / tone_s)); g = clamp(target / x, 0, tone_gmax); '
                    'g = 1 + (g - 1) * (m + tone_out * (1 - m) * (1 - smoothstep(tone_d0, tone_d1, d))); rgb *= g',
                    '6 shoulder on luma above knee toward ceil: l2 = knee + (ceil - knee) * (1 - exp(-(l - knee) / (ceil - knee))); rgb *= l2 / l',
                    '7 haze: h = haze * m + haze_out * (1 - m); colour = mix(spill_rgb, haze_rgb, smoothstep(sp0, sp1, d)); rgb = rgb * (1 - h) + colour * h',
                    '8 vignette: * (1 - vignette * smoothstep(v0, v1, d)) * (1 - board_falloff * (1 - smoothstep(bx0, bx1, x)))',
                    'then the board scrim (unchanged): 6 px blur weighted 1 - smoothstep(300, 520, r), and SCRIM #02030A at 0.55 * (1 - smoothstep(330, 560, r)), r from (536, 540)'],
             rooms={k: {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in BG.ROOMS.items()},
             rooms_step61=BG.ROOMS_STEP61)
rows = []
res = {}
for room, corp, key, name in JOBS:
    P = BG.params_for(room, corp)
    assert P is BG.ROOMS[key], (room, corp, key)
    broom = BEFORE_ROOM.get((room, corp), room)
    bef = L.compose(np.clip(L.G2().scrim(BG.grade(L.bare(broom), BG.ROOMS_STEP61[broom]), 'P'), 0, 255), corp)
    aft = L.compose(L.backdrop(room, P), corp)
    Image.fromarray(aft.astype(np.uint8)).save(DST + name + '.png')
    Image.fromarray(bef.astype(np.uint8)).save(TMP + name + '_before.png')
    sb, sa = L.stats(bef, SFX[corp]), L.stats(aft, SFX[corp])
    reg = M.regions(corp)
    qb, qa = M.measure(bef, corp, reg), M.measure(aft, corp, reg)
    rk = RC.run(name, DST + name + '.png', SFX[corp])
    rkb = RC.run(name + '_before', TMP + name + '_before.png', SFX[corp])
    checks['plates'][name] = dict(room=room, corp=corp, grade_key=key, before_room=broom,
                                  before=dict(L=sb, squint=qb, rb_pass=rkb['pass'], room_failures=rkb['b_value_order']['failures']),
                                  after=dict(L=sa, squint=qa, rb_pass=rk['pass'], plate_pass=rk['plate_pass'], room_ref=rk['b_value_order']['room_ref'],
                                             value_order=rk['b_value_order']['sorted'], failures=rk['b_value_order']['failures'],
                                             cap_fails=rk['c_cap_height']['n_fail'], palette_fails=[(f['a'], f['b'], f['dE']) for f in rk['d_palette']['failures']]))
    ref = rk['b_value_order']['room_ref']['value']
    res[name] = dict(room_mean_28_34=TK.ROOM_MEAN_L[0] <= sa['room']['mean'] <= TK.ROOM_MEAN_L[1],
                     room_p95_below_ref=sa['room']['p95'] + TK.ORDER_MARGIN <= ref,
                     pink=sa['detail']['pink_share'] < 0.001,
                     rb_checks_all=rk['plate_pass'])
    # before/after row: plate before | after (1/2), room at 1:1 before | after, numbers
    RH = 36 + 540 + 8 + 300
    row = Image.new('RGB', (1920 + 1540 + 8, RH), (8, 8, 14))
    row.paste(Image.fromarray(bef.astype(np.uint8)).resize((960, 540), Image.LANCZOS), (0, 36))
    row.paste(Image.fromarray(aft.astype(np.uint8)).resize((960, 540), Image.LANCZOS), (960, 36))
    cr = (1150, 380, 1920, 840)
    row.paste(Image.fromarray(bef.astype(np.uint8)).crop(cr), (1928, 36))
    row.paste(Image.fromarray(aft.astype(np.uint8)).crop(cr), (1928 + 770, 36))
    d = ImageDraw.Draw(row)
    d.text((8, 6), '%s   BEFORE (step6-1 grade%s)' % (name, ', bio lab' if broom != room else ''), font=fnt, fill=(255, 255, 255))
    d.text((968, 6), 'AFTER (rb2-1 grade, %s)' % key, font=fnt, fill=(255, 255, 255))
    d.text((1936, 6), 'room crop, before | after (sheet at 2/3 scale; plates are the PNGs)', font=fnt, fill=(255, 255, 255))
    y0 = 36 + 540 + 8
    for i, (lab, s, rr) in enumerate((('before', sb, rkb), ('after', sa, rk))):
        t = ['%s: room region mean L* %.1f  p95 %.1f  (gate: mean 28-34, p95 + 1 <= %.1f)' % (lab, s['room']['mean'], s['room']['p95'], ref),
             '  box part %.1f / %.1f   street part %.1f / %.1f   (mean / p95 L*)' % (s['room_hull']['mean'], s['room_hull']['p95'], s['room_city']['mean'], s['room_city']['p95']),
             '  reviewer room box mean %.1f  p95 %.1f;  left city box mean %.1f' % (s['review_room_box']['mean'], s['review_room_box']['p95'], s['review_city_box']['mean']),
             '  room detail rel %.3f  sat %.3f  pink %.3f %%' % (s['detail']['detail_rel'], s['detail']['sat'], 100 * s['detail']['pink_share']),
             '  rb_checks ' + ' '.join('%s:%s' % (k[0], 'ok' if v else 'FAIL') for k, v in rr['pass'].items())]
        for k, tt in enumerate(t):
            d.text((i * 960 + 10, y0 + 4 + k * 28), tt, font=fnt, fill=(240, 240, 240) if lab == 'after' else (175, 175, 185))
    pt = ['grade "%s" (grade.json)' % key,
          'tone_lo %.4f  tone_hi %.2f  ceil %.2f  chroma %.3f  pink %.2f  contrast %.2f' % (P['tone_lo'], P['tone_hi'], P['ceil'], P['chroma'], P['pink_chroma'], P['contrast']),
          'haze %.2f -> %.2f  spill %s  city chroma %.2f' % (P['haze'], P['haze_out'], P['spill_rgb'], P['city_chroma'])]
    if P.get('hue_amt'):
        pt.append('corp light: hues %d-%d -> %d deg x %.2f' % (P['hue_lo'], P['hue_hi'], P['hue_to'], P['hue_amt']))
    for k, tt in enumerate(pt):
        d.text((1936, 36 + 460 + 20 + k * 30), tt, font=fnt, fill=(200, 220, 255))
    rows.append(row)
    print(name, 'room L* %.1f/%.1f -> %.1f/%.1f' % (sb['room']['mean'], sb['room']['p95'], sa['room']['mean'], sa['room']['p95']), 'ref', ref,
          'rb', rk['pass'], flush=True)
W_ = rows[0].width
sheet = Image.new('RGB', (W_, sum(r.height for r in rows)))
y = 0
for r in rows:
    sheet.paste(r, (0, y)); y += r.height
sheet = sheet.resize((W_ * 2 // 3, sheet.height * 2 // 3), Image.LANCZOS)
sheet.save(DST + 'before_after.jpg', quality=86)
# composite vs the real renders (the final set): same skin, same room
vr = {}
for name, real in (('p1_bio', 'p1_decide.png'), ('p1_bio_solace', 'p1_decide_solace.png'), ('p1_shop_meridian', 'p1_decide_meridian.png')):
    if os.path.exists(BOARD + real):
        a = np.asarray(Image.open(DST + name + '.png').convert('RGB'), np.float32)
        b = np.asarray(Image.open(BOARD + real).convert('RGB'), np.float32)
        e = np.abs(a - b)
        vr[name] = dict(real=real, mean_abs=round(float(e.mean()), 3), p999=round(float(np.percentile(e, 99.9)), 2), max=round(float(e.max()), 1))
checks['real_render_vs_composite'] = vr
checks['targets'] = dict(room_mean='L* 28-34 (rb_checks room region)', room_p95='+1 <= ring-NOW occupied glass p95 of the plate', pink='room pink share < 0.1 %',
                         rb_checks='a-e pass on every plate')
checks['pass'] = res
checks['all_pass'] = all(all(v.values()) for v in res.values())
json.dump(checks, open(DST + 'checks.json', 'w'), indent=1, default=str)
json.dump(grade, open(DST + 'grade.json', 'w'), indent=1)
print('all_pass', checks['all_pass'], json.dumps({k: [kk for kk, vv in v.items() if not vv] for k, v in res.items()}), json.dumps(vr))
