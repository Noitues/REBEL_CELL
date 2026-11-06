"""bd_publish.py <params.json> : write the step 6 deliverables to docs/concepts/combat_redesign/locked/backdrop/.
p1_<room>.png (neutral), p1_bio_solace.png, p1_bio_meridian.png, before_after.jpg, grade.json, checks.json.
Plates are composed as F + T * backdrop from the extracted final p1 board (fg_extract.py; exact to <= 1.7/255)."""
import sys, json, os, shutil
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/backdrop/src')
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import bd_measure as M
import bd_grade as BG

PJ = json.load(open(sys.argv[1]))
DST = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/backdrop/'
os.makedirs(DST, exist_ok=True)
fnt = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 22)
fsm = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 17)
JOBS = [(r, 'neutral') for r in M.ROOMS] + [('bio', 'solace'), ('bio', 'meridian')]
checks = dict(method=dict(
    composite='plate = F + T * backdrop; F, T from two renders of the final p1 board (corp/src generator, unchanged) with flat 0 and 128 backdrops. '
              'Verified against a real render on bio neutral: mean abs error 0.09/255, max 1.7/255.',
    squint='locked final_checks metric: 1/16 BOX downscale + 1 px gaussian, Rec709 luma; loud = share of 16 px cells above 0.38',
    regions=dict(plate='whole 1920x1080', board='r <= 500 round (536, 540)', rings='r 214-430', room='focus hull ellipse (1500, 600; 330 x 270; m > 0.5) where the backdrop shows through (T > 0.5), cells >= 90 % inside',
                 backdrop_visible='every cell >= 90 % backdrop (T > 0.5): room + city'),
    board_vs_room='mean_ratio = (board squint mean + 0.05) / (room squint mean + 0.05); p95_ratio likewise; loud_ratio = board loud / room loud (room floored at 0.001)',
    detail='detail_rms = RMS of luma minus a 6 px gaussian inside the room (0-1); detail_rel = detail_rms / room luma mean (Weber legibility, brightness-independent); '
           'sat = mean HSV saturation in the room; pink_share = room pixels of player-pink hue (295-350 deg, S > 0.35, V > 0.15)'),
    before='the locked final grade: r2_ground.grade(P) (hull x0.595 and neon sat 0.55->0.33 on the v3.1 bare room; city 2 px blur x0.85) + scrim(P)',
    after='bd_grade.grade(per-room params) + the same scrim(P)', plates={})
grade = dict(version='step6-1', applies_to='room_<n>_bare.png (combat_backdrop/v3_1), before the board scrim; screen space 1920x1080',
             colour_space='all maths on gamma-encoded sRGB values in 0-1 (the PNG values); a Godot post shader must work on the sRGB-encoded colour '
                          '(or linear_to_srgb first, srgb_to_linear after). Blur radii are gaussian sigma-ish PIL radii at 1920x1080; scale with resolution.',
             replaces='r2_ground.grade(P): hull x0.595 with neon saturation x0.6, city 2 px blur x0.85',
             tuning='hull_value and chroma are solved per room (bd_solve.py): room squint mean 0.135, room mean saturation = min(before, 0.44). '
                    'Everything else is shared, except event (contrast 1.24, shoulder ceil 0.32, pink_chroma 0.42). haze is in the recipe but 0 everywhere.',
             order=['1 focus hull mask m: ellipse (cx, cy, rx, ry), smoothstep(f0, f1) on the normalised distance d, m = 1 inside',
                    '2 blur: gaussian hull_blur px inside, city_blur px outside, mixed by m',
                    '3 chroma: lerp to Rec709 luma; k = chroma * (1 - (1 - neon_chroma) * neon) * (1 - (1 - pink_chroma) * pink); neon = smoothstep(.35,.60,S)*smoothstep(.35,.65,V); pink = smoothstep(296,308,hue) * (1 - smoothstep(345,358,hue)) * smoothstep(.18,.35,S)',
                    '4 contrast: c = pivot + (c - pivot) * contrast (0-1 units)',
                    '5 value: * (hull_value * m + city_value * (1 - m))',
                    '6 shoulder on luma above knee toward ceil: l2 = knee + (ceil - knee) * (1 - exp(-(l - knee) / (ceil - knee))); rgb *= l2 / l',
                    '7 haze: mix toward haze_rgb by haze',
                    '8 vignette: * (1 - vignette * smoothstep(v0, v1, d)) * (1 - board_falloff * (1 - smoothstep(bx0, bx1, x)))',
                    'then the board scrim (unchanged): 6 px blur weighted 1 - smoothstep(300, 520, r), and SCRIM #02030A at 0.55 * (1 - smoothstep(330, 560, r)), r from (536, 540)'],
             rooms={})
rows = []
for room, corp in JOBS:
    P = dict(BG.BASE, **PJ[room])
    reg = M.regions(corp)
    bef = np.asarray(Image.open(M.HERE + 'work/before_%s_%s.png' % (room, corp)), np.float32)
    aft = M.compose(M.after_backdrop(room, P), corp)
    name = 'p1_%s' % room if corp == 'neutral' else 'p1_%s_%s' % (room, corp)
    Image.fromarray(aft.astype(np.uint8)).save(DST + name + '.png')
    sb, sa = M.measure(bef, corp, reg), M.measure(aft, corp, reg)
    checks['plates'][name] = dict(before=sb, after=sa)
    if corp == 'neutral':
        grade['rooms'][room] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in P.items()}
    # before/after row: plate before | plate after (1/2), room crop before | after (full res), squint before | after
    RH = 36 + 540 + 8 + 252 + 12
    row = Image.new('RGB', (1920 + 1540 + 8, RH), (8, 8, 14))
    row.paste(Image.fromarray(bef.astype(np.uint8)).resize((960, 540), Image.LANCZOS), (0, 36))
    row.paste(Image.fromarray(aft.astype(np.uint8)).resize((960, 540), Image.LANCZOS), (960, 36))
    cr = (1150, 380, 1920, 840)
    row.paste(Image.fromarray(bef.astype(np.uint8)).crop(cr), (1928, 36))
    row.paste(Image.fromarray(aft.astype(np.uint8)).crop(cr), (1928 + 770, 36))
    d = ImageDraw.Draw(row)
    d.text((8, 6), '%s   BEFORE (locked final grade)' % name, font=fnt, fill=(255, 255, 255))
    d.text((968, 6), 'AFTER (step 6 grade)', font=fnt, fill=(255, 255, 255))
    d.text((1936, 6), 'room at 1:1   before | after', font=fnt, fill=(255, 255, 255))
    y0 = 36 + 540 + 8
    for i, (lab, im, s) in enumerate((('before', bef, sb), ('after', aft, sa))):
        sq = M.squint_grid(im)
        g = Image.fromarray((np.clip(sq, 0, 1) * 255).astype(np.uint8)).resize((448, 252), Image.NEAREST).convert('RGB')
        ov = Image.fromarray(((sq > 0.38) * 255).astype(np.uint8)).resize((448, 252), Image.NEAREST)
        g.paste((255, 60, 60), (0, 0), ov.point(lambda v: 110 if v else 0))
        row.paste(g, (i * 960, y0))
        t = ['squint  mean / p95 / loud (red cells)',
             'plate   %.3f / %.3f / %.1f%%' % (s['plate']['mean'], s['plate']['p95'], 100 * s['plate']['loud']),
             'board   %.3f / %.3f / %.1f%%' % (s['board']['mean'], s['board']['p95'], 100 * s['board']['loud']),
             'room    %.3f / %.3f / %.1f%%' % (s['room']['mean'], s['room']['p95'], 100 * s['room']['loud']),
             'city+rm %.3f / %.3f / %.1f%%' % (s['backdrop_visible']['mean'], s['backdrop_visible']['p95'], 100 * s['backdrop_visible']['loud']),
             'board/room  mean %.2f  p95 %.2f' % (s['board_vs_room']['mean_ratio'], s['board_vs_room']['p95_ratio']),
             'room detail %.3f  rel %.2f' % (s['room_detail']['detail_rms'], s['room_detail']['detail_rel']),
             'room sat %.2f   pink %.2f%%' % (s['room_detail']['sat'], 100 * s['room_detail']['pink_share'])]
        for k, tt in enumerate(t):
            d.text((i * 960 + 460, y0 + 4 + k * 30), tt, font=fnt, fill=(240, 240, 240) if lab == 'after' else (180, 180, 190))
    pt = ['grade "%s" (grade.json)' % room,
          'hull_value %.3f  city_value %.2f  chroma %.3f  neon %.2f  pink %.2f' % (P['hull_value'], P['city_value'], P['chroma'], P['neon_chroma'], P['pink_chroma']),
          'contrast %.2f @ %.2f  shoulder %.2f -> %.2f  haze %.2f' % (P['contrast'], P['pivot'], P['knee'], P['ceil'], P['haze']),
          'blur hull %.1f px  city %.1f px  vignette %.2f  board falloff %.2f' % (P['hull_blur'], P['city_blur'], P['vignette'], P['board_falloff'])]
    for k, tt in enumerate(pt):
        d.text((1936, 36 + 460 + 24 + k * 32), tt, font=fnt, fill=(200, 220, 255))
    rows.append(row)
    print(name, 'room mean %.3f->%.3f' % (sb['room']['mean'], sa['room']['mean']), flush=True)
W_ = rows[0].width
sheet = Image.new('RGB', (W_, sum(r.height for r in rows)))
y = 0
for r in rows:
    sheet.paste(r, (0, y)); y += r.height
sheet = sheet.resize((W_ * 2 // 3, sheet.height * 2 // 3), Image.LANCZOS)
sheet.save(DST + 'before_after.jpg', quality=86)
# targets
T = dict(room_squint_mean='0.13-0.14 (was 0.17-0.20)', room_loud='0 %', room_p95='<= 0.25', board_vs_room_mean_ratio='>= 1.55',
         detail_rel_retained='>= 0.80 of before', sat='within 0.05 of before (capped at 0.44)', pink_share='< 0.1 %')
res = {}
for n, v in checks['plates'].items():
    a, b = v['after'], v['before']
    res[n] = dict(room_mean=0.125 <= a['room']['mean'] <= 0.145, room_loud=a['room']['loud'] == 0, room_p95=a['room']['p95'] <= 0.25,
                  board_vs_room=a['board_vs_room']['mean_ratio'] >= 1.55,
                  detail_rel=a['room_detail']['detail_rel'] >= 0.80 * b['room_detail']['detail_rel'],
                  sat=abs(a['room_detail']['sat'] - min(b['room_detail']['sat'], 0.44)) <= 0.05,
                  pink=a['room_detail']['pink_share'] < 0.001,
                  board_unchanged=abs(a['board']['mean'] - b['board']['mean']) < 0.005)
vr = {}
for r in M.ROOMS:
    lf = M.HERE + 'logs/verify_%s.log' % r
    if os.path.exists(lf):
        ln = [l for l in open(lf).read().splitlines() if l.startswith('{')]
        if ln:
            vr[r] = json.loads(ln[-1])
checks['real_render_vs_composite'] = dict(note='p1 rendered by the corp/src generator with r2_ground.grade swapped for bd_grade (bd_verify.py), vs the published p1_<room>.png; 0-255 units',
                                          rooms=vr)
checks['targets'] = T
checks['pass'] = res
checks['all_pass'] = all(all(v.values()) for v in res.values())
json.dump(checks, open(DST + 'checks.json', 'w'), indent=1)
json.dump(grade, open(DST + 'grade.json', 'w'), indent=1)
print('all_pass', checks['all_pass'], json.dumps({k: [kk for kk, vv in v.items() if not vv] for k, v in res.items()}))
