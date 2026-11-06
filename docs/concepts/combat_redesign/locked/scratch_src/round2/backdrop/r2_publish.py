"""r2_publish.py [--stage] [--only name,name]   (2026-11-04 round 2, backdrop stage)
Re-composite the backdrop set on the round-2 p1 board (r2_fg_extract.py, one transfer per skin) with the unchanged rb2-1 room grade
(corp/src bd_grade.ROOMS, read only), measure every plate, and publish the plates that pass to docs/concepts/combat_redesign/locked/backdrop/:
p1_<room>.png (neutral, 7 kit rooms), p1_bio_solace.png, p1_shop_meridian.png, before_after.jpg, grade.json, checks.json.

Every plate is first written to round2/backdrop/out/ and measured THERE; only plates that pass every gate are copied to the published folder,
and the copy is compared byte for byte afterwards.  Gates per plate:
  C9   room mean L* 28-34 (rb_checks room region, UI scrim slabs cut out)                       - the call's gate
  C9   room as seen L* 28-34 (the same region with the UI scrim slabs kept; every backdrop plate is a p1 plate) - the backdrop brief
       room p95 + 1 <= ring-NOW occupied glass p95 (rb_checks b)
       room pink share < 0.1 %
       rb_checks a-i (the round-2 checks: cells, value order with C3 / C4, caps, palette with drawn colours C2 / C15 / C16, hand C6,
       pencil C1, tickets C5, HUD rows C8, HOT core C11), on the p1 capture of the plate's skin
  and, for the three plates that have a real render in locked/final/, composite vs the real render (mean <= 0.5/255, max <= 3/255).
--stage writes and measures only (nothing is published); --only limits the plates (stage only)."""
import sys, json, os, shutil, filecmp, hashlib, time
sys.dont_write_bytecode = True
HERE = 'D:/rc_scratch/combat_redesign/locked/round2/backdrop/'
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import r2_lib as L
import bd_grade as BG
import rb_checks as RC
import rb_tokens as TK

DST = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/backdrop/'
FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src/'
R1 = HERE + 'work/r1/'
OUTD = HERE + 'out/'
C14 = HERE + 'work/c14/c14_assert.json'
os.makedirs(OUTD, exist_ok=True)
stage = '--stage' in sys.argv
only = None
if '--only' in sys.argv:
    only = set(sys.argv[sys.argv.index('--only') + 1].split(','))
    stage = True
fnt = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 22)
JOBS = [(r, 'neutral', r, 'p1_%s' % r) for r in L.ROOMS] + [('bio', 'solace', 'bio', 'p1_bio_solace'), ('shop', 'meridian', 'shop_meridian', 'p1_shop_meridian')]
if only:
    JOBS = [j for j in JOBS if j[3] in only]
REAL = {'p1_bio': 'p1_decide.png', 'p1_bio_solace': 'p1_decide_solace.png', 'p1_shop_meridian': 'p1_decide_meridian.png'}
r1 = json.load(open(R1 + 'checks.json', encoding='utf-8'))


def grade_note(version, rows):
    p1 = rows.get('p1', {})
    return ('rb2-1 is unchanged (corp/src bd_grade.py, GRADE_VERSION %s, ROOMS as in "rooms").  Round 2 re-verified it on the round-2 board.  The '
            'board HUD now always reserves the option rows (C8), so on p1 the HUD mask ends at y %s and the HUD column UI scrim slab (hud2.scrim_layers: '
            'SCRIM #02030A, part of the board layer, not of this grade) darkens the room by 15 %% or more down to y %s (both measured from the round-2 '
            'p1 capture; the hand slab from y %s).  C9: the gate is on the room itself (scrim cut, L* 28-34); the room as seen with the scrim kept '
            'is gated 28-34 on these p1 plates too and reported on the other beats (locked/final/checks.json).'
            % (version, p1.get('hud_mask_bottom_y'), (p1.get('column_slab_y') or [None, None])[1], (p1.get('hand_slab_y') or [None])[0]))


def src_hashes():
    return {fn: hashlib.sha1(open(SRC + fn, 'rb').read()).hexdigest()[:12] for fn in sorted(os.listdir(SRC)) if fn.endswith('.py')}


# provenance: corp/src must be the tree the three transfers were rendered from
now_h = src_hashes()
prov = {}
for corp in sorted({j[1] for j in JOBS}):
    fj = json.load(open(HERE + 'work/fg_%s_src.json' % corp))
    diff = sorted(k for k in set(now_h) | set(fj['src_sha1']) if now_h.get(k) != fj['src_sha1'].get(k))
    prov[corp] = dict(render_seconds=fj['seconds'], corp_src_changed_since_render=diff)
    assert not diff, ('corp/src changed since the %s transfer was rendered' % corp, diff)


def r1_row(name):
    p = r1['plates'].get(name)
    if not p:
        return None
    a = p['after']
    seen = [r for r in a.get('value_order', []) if r['family'].startswith('room as seen')]
    return dict(room=a['L']['room'], room_hull=a['L']['room_hull'], room_city=a['L']['room_city'], review_room_box=a['L']['review_room_box'],
                detail=a['L']['detail'], room_as_seen=dict(mean=seen[0]['mean'], p95=seen[0]['p95']) if seen else None, room_ref=a.get('room_ref'))


checks = dict(
    version='round 2 (2026-11-04)',
    method=dict(
        composite='plate = F + T * backdrop.  F, T: two renders of the round-2 p1 board (corp/src lw_render with rb_patch, rb2_patch, rb3_patch and '
                  'rb4_patch; read only) with flat 0 and 128 backdrops (round2/backdrop/r2_fg_extract.py), one per skin, in a fresh render cache.  '
                  'backdrop = r2_ground.scrim(bd_grade.grade(room_<n>_bare.png, bd_grade.ROOMS[key]), "P").  Cross-checked against the real '
                  'round-2 renders in locked/final/ (real_render_vs_composite).',
        room_numbers='rb_checks room region (x >= 1100, y >= 420, r > 505 from (536, 540), HUD / hand / SEND IT / UNDO / nameplate / YOU / hover tag '
                     'cut out, dilated 4 px), from the round-2 p1 capture of the skin (masks snapshotted to round2/backdrop/work/caps/).  "room": '
                     'the UI scrim slabs cut where they darken the room by 15 % or more (the C9 gate region).  "room as seen": the same region with '
                     'the scrim slabs kept.  L* = CIE L* of the region mean luminance; p95 = 95th percentile of per-pixel L*.',
        gates='C9: room mean L* 28-34 and room as seen mean L* 28-34 on every plate (all backdrop plates are p1); room p95 + 1 <= ring-NOW '
              'occupied glass p95; room pink share < 0.1 %; rb_checks a-i (round 2) on every plate; composite vs real render mean <= 0.5/255 '
              'and max <= 3/255 where a real render exists',
        squint='locked final_checks squint (1/16 BOX + 1 px blur, Rec709 luma, loud > 0.38), reported only (C10: the squint is not a gate)',
        before='round 1 (gate 1) as published: the plates in this folder before this pass (gate-1 board, the same rb2-1 grade), numbers from the '
               'round-1 checks.json (measured on those PNGs with the gate-1 masks)',
        after='round 2: the round-2 board, rb2-1 grade unchanged'),
    provenance=dict(transfers=prov, corp_src_sha1=now_h),
    plates={})
res = {}
rows = []
t0 = time.time()
for room, corp, key, name in JOBS:
    P = BG.params_for(room, corp)
    assert P is BG.ROOMS[key], (room, corp, key)
    sfx = L.SFX[corp]
    aft = L.compose(L.backdrop(room, P), corp).astype(np.uint8)
    fp = OUTD + name + '.png'
    Image.fromarray(aft).save(fp)
    pl = np.asarray(Image.open(fp).convert('RGB'))          # measure the written PNG, not the array
    sa = L.stats(pl, sfx)
    qa = L.squint(pl.astype(np.float32), corp)
    rk = RC.run(name, fp, sfx)
    b = rk['b_value_order']
    ref = b['room_ref']['value']
    tab = {r['family']: r for r in b['sorted']}
    r1r = r1_row(name)
    checks['plates'][name] = dict(
        room=room, corp=corp, grade_key=key, capture=sfx,
        before_round1=r1r,
        after=dict(L=sa, squint=qa, room_ref=b['room_ref'], value_order=b['sorted'], order_failures=b['failures'],
                   round2_bright=dict(unclassed_bright_px=b['round2'].get('unclassed_px'), pass_=b['round2']['pass_']) if 'round2' in b else None,
                   rb_pass=rk['pass'], plate_pass=rk['plate_pass'],
                   cap_fails=rk['c_cap_height']['n_fail'], palette_fails=[(f['a'], f['b'], f['dE']) for f in rk['d_palette']['failures']],
                   cells_lowest_ratio=min((r['ratio'] for r in rk['a_cell_contrast']['rows'] if r['gated'] and r['ratio'] is not None), default=None),
                   hand=dict(hand_x_send_px=rk['e_hand']['hand_x_send_px'], hand_x_undo_px=rk['e_hand']['hand_x_undo_px'])))
    res[name] = dict(room_mean_28_34=TK.ROOM_MEAN_L[0] <= sa['room']['mean'] <= TK.ROOM_MEAN_L[1],
                     room_as_seen_28_34=TK.ROOM_MEAN_L[0] <= sa['room_as_seen']['mean'] <= TK.ROOM_MEAN_L[1],
                     room_p95_below_ref=sa['room']['p95'] + TK.ORDER_MARGIN <= ref,
                     room_matches_rb_b=abs(tab['room']['mean'] - sa['room']['mean']) <= 0.06,
                     pink=sa['detail']['pink_share'] < 0.001,
                     rb_checks_a_to_i=rk['plate_pass'])
    if name in REAL:
        a = pl.astype(np.float32)
        bb = np.asarray(Image.open(FINAL + REAL[name]).convert('RGB'), np.float32)
        e = np.abs(a - bb)
        vr = dict(real=REAL[name], mean_abs=round(float(e.mean()), 3), mean_signed=round(float((a - bb).mean()), 3),
                  p999=round(float(np.percentile(e, 99.9)), 2), max=round(float(e.max()), 1), px_over_2=int((e.max(-1) > 2).sum()),
                  px_differing=int((e.max(-1) > 0).sum()))
        checks['plates'][name]['real_render_vs_composite'] = vr
        res[name]['composite_matches_real'] = vr['mean_abs'] <= 0.5 and vr['max'] <= 3
    print(name, 'room %.1f/%.1f seen %.1f ref %.1f' % (sa['room']['mean'], sa['room']['p95'], sa['room_as_seen']['mean'], ref),
          'rb', {k[0]: v for k, v in rk['pass'].items()}, checks['plates'][name].get('real_render_vs_composite', ''),
          round(time.time() - t0, 1), flush=True)
    # ---- before / after row: round 1 | round 2 (1/2), the room under the HUD at 1:1 round 1 | round 2, numbers
    bef = np.asarray(Image.open(R1 + name + '.png').convert('RGB')) if os.path.exists(R1 + name + '.png') else np.zeros_like(pl)
    RH = 36 + 540 + 8 + 300
    row = Image.new('RGB', (1920 + 1540 + 8, RH), (8, 8, 14))
    row.paste(Image.fromarray(bef).resize((960, 540), Image.LANCZOS), (0, 36))
    row.paste(Image.fromarray(pl).resize((960, 540), Image.LANCZOS), (960, 36))
    cr = (1150, 570, 1920, 1030)
    row.paste(Image.fromarray(bef).crop(cr), (1928, 36))
    row.paste(Image.fromarray(pl).crop(cr), (1928 + 770, 36))
    d = ImageDraw.Draw(row)
    d.text((8, 6), '%s   BEFORE (round 1 as published: gate-1 board, rb2-1)' % name, font=fnt, fill=(255, 255, 255))
    d.text((968, 6), 'AFTER (round 2 board, rb2-1 "%s")' % key, font=fnt, fill=(255, 255, 255))
    d.text((1936, 6), 'room under the HUD (x 1150-1920, y 570-1030) at 1:1, before | after', font=fnt, fill=(255, 255, 255))
    y0 = 36 + 540 + 8
    t_b = ['before: room mean L* %.1f  p95 %.1f   as seen %s' % (r1r['room']['mean'], r1r['room']['p95'],
                                                                ('%.1f' % r1r['room_as_seen']['mean']) if r1r and r1r['room_as_seen'] else '-'),
           '  box part %.1f   street part %.1f   (mean L*)' % (r1r['room_hull']['mean'], r1r['room_city']['mean']),
           '  reviewer room box mean %.1f  p95 %.1f' % (r1r['review_room_box']['mean'], r1r['review_room_box']['p95']),
           '  detail rel %.3f  sat %.3f  pink %.3f %%' % (r1r['detail']['detail_rel'], r1r['detail']['sat'], 100 * r1r['detail']['pink_share']),
           '  (round-1 checks.json, gate-1 masks)'] if r1r else ['before: -']
    t_a = ['after: room mean L* %.1f  p95 %.1f   as seen %.1f' % (sa['room']['mean'], sa['room']['p95'], sa['room_as_seen']['mean']),
           '  box part %.1f   street part %.1f   gate 28-34 both; p95+1 <= %.1f' % (sa['room_hull']['mean'], sa['room_city']['mean'], ref),
           '  reviewer room box mean %.1f  p95 %.1f' % (sa['review_room_box']['mean'], sa['review_room_box']['p95']),
           '  detail rel %.3f  sat %.3f  pink %.3f %%' % (sa['detail']['detail_rel'], sa['detail']['sat'], 100 * sa['detail']['pink_share']),
           '  rb_checks ' + ' '.join('%s:%s' % (k[0], 'ok' if v else 'FAIL') for k, v in rk['pass'].items())]
    for i, tt_ in enumerate((t_b, t_a)):
        for k, tt in enumerate(tt_):
            d.text((i * 960 + 10, y0 + 4 + k * 28), tt, font=fnt, fill=(240, 240, 240) if i else (175, 175, 185))
    pt = ['grade "%s" (grade.json, rb2-1, unchanged)' % key,
          'tone_lo %.4f  tone_hi %.2f  ceil %.3f  chroma %.3f  pink %.2f  contrast %.2f' % (P['tone_lo'], P['tone_hi'], P['ceil'], P['chroma'], P['pink_chroma'], P['contrast']),
          'haze %.2f -> %.2f  spill %s  city chroma %.2f' % (P['haze'], P['haze_out'], P['spill_rgb'], P['city_chroma'])]
    if P.get('hue_amt'):
        pt.append('corp light: hues %d-%d -> %d deg x %.2f' % (P['hue_lo'], P['hue_hi'], P['hue_to'], P['hue_amt']))
    for k, tt in enumerate(pt):
        d.text((1936, 36 + 460 + 20 + k * 30), tt, font=fnt, fill=(200, 220, 255))
    rows.append(row)

checks['pass'] = res
checks['all_pass'] = all(all(v.values()) for v in res.values())
# the UI scrim slabs as captured (rb_capture 'scrim': where the slab darkens the room by 15 % or more), inside the room box x >= 1100, y >= 420
SCRIM_ROWS = {}
for corp, sfx in L.SFX.items():
    Ms = RC.load_masks(sfx)
    s = Ms.get('scrim')
    if s is None:
        continue
    col = s[:, 1100:1920]
    ys = np.where(col[:700].any(1))[0]
    yh = np.where(col[700:].any(1))[0] + 700
    hb = Ms.get('hud')
    SCRIM_ROWS[sfx] = dict(column_slab_y=[int(ys.min()), int(ys.max())] if ys.size else None, hand_slab_y=[int(yh.min()), int(yh.max())] if yh.size else None,
                           hud_mask_bottom_y=int(np.where(hb[:, 1100:1920].any(1))[0].max()) if hb is not None and hb.any() else None)
checks['ui_scrim_rows'] = SCRIM_ROWS
c14 = json.load(open(C14)) if os.path.exists(C14) else None
checks['c14_determinism'] = dict(source=C14, pass_=bool(c14 and c14.get('pass')),
                                 p3_vs_p3_px_differing=(c14 or {}).get('p3_vs_p3_px_differing'), steps=(c14 or {}).get('steps'))
json.dump(checks, open(OUTD + 'checks.json', 'w'), indent=1, default=str)
W_ = rows[0].width
sheet = Image.new('RGB', (W_, sum(r.height for r in rows)))
y = 0
for r in rows:
    sheet.paste(r, (0, y)); y += r.height
sheet = sheet.resize((W_ * 2 // 3, sheet.height * 2 // 3), Image.LANCZOS)
sheet.save(OUTD + 'before_after.jpg', quality=86)

# ---- grade.json: the rb2-1 grade is unchanged; round 2 records the board it was verified on and the as-seen numbers
g1 = json.load(open(R1 + 'grade.json', encoding='utf-8'))
g = dict(g1)
seen = {n: v['after']['L']['room_as_seen']['mean'] for n, v in checks['plates'].items()}
gate = {n: v['after']['L']['room']['mean'] for n, v in checks['plates'].items()}
g['round2'] = dict(
    date='2026-11-04',
    grade_changed=False,
    note=grade_note(BG.GRADE_VERSION, SCRIM_ROWS),
    room_mean_L_gate_region={k: gate[k] for k in sorted(gate)},
    room_mean_L_as_seen={k: seen[k] for k in sorted(seen)},
    ui_scrim=dict(source='corp/src hud2.scrim_layers (board layer, drawn on the room before the board plate; not part of this grade)',
                  column='rounded rect from the HUD panel left edge - 18 px to x 1920, y 0 to the HUD bottom + 14, radius 18, rgba(2, 3, 10, 140), gaussian 12',
                  hand='rounded rect x 960-1920, y 836-1080, radius 24, rgba(2, 3, 10, 120), gaussian 12',
                  measured_cut_rows=SCRIM_ROWS))
g['rooms'] = {k: {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in BG.ROOMS.items()}
assert g['rooms'] == g1['rooms'], 'the grade table differs from the published rb2-1 grade.json'
json.dump(g, open(OUTD + 'grade.json', 'w'), indent=1)
print('all_pass', checks['all_pass'], json.dumps({k: [kk for kk, vv in v.items() if not vv] for k, v in res.items()}), 'c14', checks['c14_determinism']['pass_'], flush=True)

if stage:
    raise SystemExit(0)
# ---- publish: only passing plates; nothing unless C14 passed and every plate passed
if not checks['c14_determinism']['pass_']:
    raise SystemExit('C14 determinism assert missing or failed: nothing published')
held = {n: [k for k, v in r.items() if not v] for n, r in res.items() if not all(r.values())}
pub = [n for n in res if n not in held]
for n in pub:
    shutil.copyfile(OUTD + n + '.png', DST + n + '.png')
files = ['before_after.jpg', 'checks.json', 'grade.json']
if not held:
    for f in files:
        shutil.copyfile(OUTD + f, DST + f)
same = {f: filecmp.cmp(OUTD + f, DST + f, shallow=False) for f in [n + '.png' for n in pub] + (files if not held else [])}
json.dump(dict(published=pub, held=held, byte_identical=same), open(HERE + 'work/publish.json', 'w'), indent=1)
print('published', pub, 'held', held, 'byte identical', all(same.values()))
