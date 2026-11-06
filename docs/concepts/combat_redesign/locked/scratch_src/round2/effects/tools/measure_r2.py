"""measure_r2.py [folder]: round-2 effects numbers measured on the PUBLISHED files (default: the published effects folder; or the staging
folder before the copy).  CIE L* of sRGB luminance and dE76 in CIE Lab (rb_tokens maths, read-only).  -> <R2>/work/measure_<tag>.json
  guard     every sheet, strip and the beat strip: px within dE76 15 of FOCUS #D4FF00 and of the retired lime / Solace leaf #96FE46
  pstock    fx_P_protect.png and fx_block_vs_break.png: px within dE76 8 of P_STOCK #F6C8DE (rb_tokens) and of the card bone PAPER, median L*
  pencil    fx_D_damage.png, the C1 1x inset: the board's check f (rb_checks_r2.check_pencil) on the published pixels
  skip      resolve_beat_strip.jpg, the C12 1x row: the SKIP tab's word and key text, cap height (px rows of the text at half contrast), L*;
            resolve_beat.gif: the SKIP tab region per GIF frame against the settled last frame (present while the beat runs, gone after)
  solace    strips/fx_wave_enter_solace.jpg: the scan line's drawn colour (the chromatic px of the corp-hue scan line class) vs GAIN and the
            hub HP ring green (C16)"""
import sys, os, json, glob
import numpy as np
from PIL import Image, ImageSequence
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import rb_tokens as RT
R2 = 'D:/rc_scratch/combat_redesign/locked/round2/effects/'
PUB = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/effects/'
D = (sys.argv[1].rstrip('/') + '/') if len(sys.argv) > 1 else PUB
TAG = 'staged' if D.startswith(R2) else 'published'
FOCUS, LIME = RT.TOKENS['FOCUS'], (150, 254, 70)
out = dict(folder=D, method=__doc__)


def lab_of(fp):
    return RT.lab(np.asarray(Image.open(fp).convert('RGB'), np.float64))


def near(lab, c, d):
    return np.linalg.norm(lab - RT.lab(np.array(c, np.float64)), axis=-1) < d


# ---------------------------------------------------------------- guard
g = {}
files = sorted(glob.glob(D + 'fx_*.png') + glob.glob(D + 'strips/*.jpg') + [D + 'resolve_beat_strip.jpg'])
for fp in files:
    lab = lab_of(fp)
    g[os.path.relpath(fp, D).replace('\\', '/')] = dict(focus_px=int(near(lab, FOCUS, 15).sum()), lime_px=int(near(lab, LIME, 15).sum()))
out['guard'] = dict(files=len(g), focus_px_total=sum(v['focus_px'] for v in g.values()), lime_px_total=sum(v['lime_px'] for v in g.values()),
                    nonzero={k: v for k, v in g.items() if v['focus_px'] or v['lime_px']})
print('guard', out['guard']['files'], 'files; FOCUS px', out['guard']['focus_px_total'], 'lime px', out['guard']['lime_px_total'], flush=True)

# ---------------------------------------------------------------- P stock
ps = {}
PAPER = RT.NEUTRALS['PAPER']
for nm in ('fx_P_protect.png', 'fx_block_vs_break.png'):
    lab = lab_of(D + nm)
    r = {}
    for k, c in (('p_stock', RT.P_STOCK), ('paper', PAPER)):
        m = near(lab, c, 8)
        r[k] = dict(px=int(m.sum()), median_L=round(float(np.median(lab[..., 0][m])), 1) if m.any() else None)
    ps[nm] = r
ps['p_stock_hex'] = '#%02X%02X%02X' % tuple(RT.P_STOCK)
ps['p_stock_vs_paper_dE76'] = round(float(RT.de76(RT.P_STOCK, PAPER)), 1)
out['pstock'] = ps
print('pstock', ps, flush=True)

# ---------------------------------------------------------------- pencil (C1) on the D sheet inset
pj = json.load(open(R2 + 'fx_cdhl/work/pencil_inset.json'))
import rb_checks_r2 as RC2
im = np.asarray(Image.open(D + 'fx_D_damage.png').convert('RGB'), np.float64)
x0, y0, x1, y1 = pj['plate_box']
ix, iy = pj['inset_xy_1x'][0], pj['inset_xy_1x'][1] + pj['y0']
crop = im[iy:iy + (y1 - y0), ix:ix + (x1 - x0)]
rgb = np.zeros((1080, 1920, 3), np.float64)
rgb[y0:y1, x0:x1] = crop
ty = np.asarray(Image.open(R2 + 'fx_cdhl/work/trig_yel.png').convert('RGBA'))
m = np.zeros((1080, 1920), bool)
m[y0:y1, x0:x1] = ty[y0:y1, x0:x1, 3] >= 128
pc = RC2.check_pencil(rgb, RT.lum(rgb), {'pen_L6_all': m})
p2 = np.asarray(Image.open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/p2_preview.png').convert('RGB'), np.float64)
op = ty[..., 3] >= 254
dd = np.abs(rgb - p2).max(-1)[op]
out['pencil'] = dict(sheet='fx_D_damage.png', inset_xy=[ix, iy], plate_box=pj['plate_box'], check_f=pc,
                     vs_published_p2_on_opaque_pencil_px=dict(px=int(op.sum()), max=int(dd.max()), mean=round(float(dd.mean()), 3)))
print('pencil', pc['rows'], 'vs p2 max', int(dd.max()), flush=True)

# ---------------------------------------------------------------- SKIP hint (C12)
st = json.load(open(R2 + 'fx_mpst/work/skip_tab.json'))
bo = json.load(open(R2 + 'fx_mpst/work/beat/out.json'))
hr = bo['hint_row']
S = np.asarray(Image.open(D + 'resolve_beat_strip.jpg').convert('RGB'), np.float64)
cx0, cy0 = hr['crop'][0], hr['crop'][1]
sk = dict(tab=st['tab'], key=st['key'], word_x=st['word_x'], label_px=st['label_px'], tiles=[])
for t in hr['tiles']:
    ox, oy = t['x0'] - cx0, hr['strip_y0'] + t['y0'] - cy0          # strip px = plate px + (ox, oy)
    res = dict(t_ms=t['t_ms'], opacity=t['opacity'])
    for nm, (a, b) in (('word SKIP', (st['word_x'], st['tab'][2] - 8)), ('key ANY KEY', (st['key'][0] + 4, st['key'][2] - 4))):
        ya, yb = int(st['tab'][1]) + 3, int(st['tab'][3]) - 3
        reg = S[oy + ya:oy + yb, ox + int(a):ox + int(b)]
        L = RT.lstar(RT.lum(reg))
        bg, fg = float(np.median(L)), float(np.percentile(L, 99))
        thr = (bg + fg) / 2
        rows = np.nonzero((L > thr).sum(1) >= 2)[0]
        res[nm] = dict(text_L_p99=round(fg, 1), ground_L=round(bg, 1), cap_px=int(rows.max() - rows.min() + 1) if len(rows) else 0)
    sk['tiles'].append(res)
# the GIF: the tab region per frame vs the settled last frame
gif = Image.open(D + 'resolve_beat.gif')
gw = gif.size[0]
sc = gw / 1920.0
gb = [int(st['tab'][0] * sc), int(st['tab'][1] * sc), int(np.ceil(st['tab'][2] * sc)), int(np.ceil(st['tab'][3] * sc))]
fr = [np.asarray(f.convert('RGB'), np.float64) for f in ImageSequence.Iterator(gif)]
last = RT.lab(fr[-1][gb[1]:gb[3], gb[0]:gb[2]])
dur = gif.info.get('duration', 33)
pres = []
for i, f in enumerate(fr):
    d_ = np.linalg.norm(RT.lab(f[gb[1]:gb[3], gb[0]:gb[2]]) - last, axis=-1)
    pres.append(round(float((d_ > 10).mean()), 3))
on = [i for i, v in enumerate(pres) if v > 0.2]
sk['gif'] = dict(frames=len(fr), frame_ms=dur, tab_box_gif_px=gb, share_of_tab_px_differing_from_settled=pres,
                 first_frame_shown=on[0] if on else None, last_frame_shown=on[-1] if on else None,
                 shown_ms=[round(on[0] * dur), round((on[-1] + 1) * dur)] if on else None)
out['skip'] = sk
print('skip', [(t['t_ms'], t['word SKIP'], t['key ANY KEY']) for t in sk['tiles']], 'gif shown', sk['gif']['shown_ms'], flush=True)

# ---------------------------------------------------------------- Solace wave scan line (C16)
sl = {}
fp = D + 'strips/fx_wave_enter_solace.jpg'
if os.path.exists(fp):
    # the strip (mp_run layout): tiles at x = 10 + i (tw + 10), y 84; keys 0, 70, 220, 380 (scan in), 460, 600, then the reduce tile.
    # The scan line is the one corp-hue mark and it is only drawn while a cell scans in: the px of the 380 ms tile that are chromatic
    # (LCh chroma > 15) and differ by dE76 > 20 from both the 0 ms and the settled 600 ms tile.
    rs = json.load(open(R2 + 'fx_mpst/work/res_fx_wave_enter_solace.json'))
    tw, th = Image.open(rs['tiles'][0][2]).size
    S = np.asarray(Image.open(fp).convert('RGB'), np.float64)
    keys = [t[0] for t in rs['tiles']]
    til = {k: S[84:84 + th, 10 + i * (tw + 10):10 + i * (tw + 10) + tw] for i, k in enumerate(keys)}
    lab = {k: RT.lab(v) for k, v in til.items()}
    ki = 380 if 380 in lab else keys[3]
    chroma = np.hypot(lab[ki][..., 1], lab[ki][..., 2])
    m = (chroma > 15) & (np.linalg.norm(lab[ki] - lab[0], axis=-1) > 20) & (np.linalg.norm(lab[ki] - lab[600], axis=-1) > 20)
    teal = RT.SKIN_INKS['solace']['teal']
    sl = dict(scan_ink_token='#%02X%02X%02X' % tuple(teal), tile_ms=ki, tile_px=[tw, th], scan_px=int(m.sum()),
              lime_px_strip=int(near(RT.lab(S), LIME, 15).sum()))
    if m.sum() >= 10:
        med = np.median(til[ki][m], 0)
        sl['drawn_median_hex'] = '#%02X%02X%02X' % tuple(int(round(v)) for v in med)
        sl['drawn_vs_teal_dE76'] = round(float(RT.de76(med, teal)), 1)
        sl['drawn_vs_GAIN_dE76'] = round(float(RT.de76(med, RT.TOKENS['GAIN'])), 1)
        sl['drawn_vs_hub_HP_green_dE76'] = round(float(RT.de76(med, RT.HUB_HP_GREEN)), 1)
        sl['drawn_vs_leaf_green_dE76'] = round(float(RT.de76(med, LIME)), 1)
out['solace_scan'] = sl
print('solace scan', sl, flush=True)
json.dump(out, open(R2 + 'work/measure_%s.json' % TAG, 'w'), indent=1)
print('ok', TAG, flush=True)
