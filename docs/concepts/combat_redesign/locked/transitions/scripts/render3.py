"""render3 (2026-11-04 round 2; first written for the rebuild): T5 / T6 on the round-2 board, every frame rendered at 1920x1080 from the
generator's layers.  Round 2 (C13): the bit density over the dark city (fx3.far_keep), the PULL=2 pull-out attempt (sbkit.pull_out2).
CORP=neutral|solace python render3.py
 -> out/<corp>/t5_A.gif, t6_A.gif (960 px, 12.5 fps = 80 ms), keys/t5_XXX.png, t6_XXX.png (1920x1080), strip_t5.jpg, strip_t6.jpg,
    metrics_<corp>.json (flash, frame L*, the wheel-face check, the bit colours, end frames)."""
import sys, json, os, time, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
T0 = time.time()
from fx3lib import *
import fx3 as M
import sbkit as SB
OUT = HERE + 'out/%s/' % CORP
os.makedirs(OUT + 'keys', exist_ok=True)
T5_LEN, T6_LEN, FPS = 1.2, 0.8, 25
T5K = [(0.0, 'K1 0.00 s'), (0.38, 'K2 0.38 s'), (0.55, 'K3 0.55 s'), (0.70, '0.70 s'), (0.85, 'K4 0.85 s'), (1.00, 'lock 1.00 s'), (1.12, 'K5 1.12 s'), (1.20, 'K6 1.20 s')]
T6K = [(0.0, 'K1 0.00 s'), (0.08, '0.08 s'), (0.2, 'K2 0.20 s'), (0.3, '0.30 s'), (0.4, 'K3 0.40 s'), (0.52, '0.52 s'), (0.64, '0.64 s'), (0.8, 'end 0.80 s')]
LABF = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 15)
TAGF = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 13)
PULL_MODE = os.environ.get('PULL', '0')      # 1: the round-1 T4-reverse iris + pull-out (sbkit.pull_out, lime ring); 2: the round-2 attempt
PULL = PULL_MODE in ('1', '2')                # (sbkit.pull_out2: no bright ring, street HUD 40 -> 100 %, motion-blurred zoom); 0: camera holds on the room
IRIS = os.environ.get('IRIS', 'ink')          # PULL=2 iris edge: ink | soft | lime


def t6_full(t, log=None):
    """the T6 win path: the dissolve on the room view (camera held); with PULL=1 / 2 also the T4 iris and pull-out to the street"""
    a = to_pil(M.t6(t, log))
    if PULL_MODE == '1':
        return np.asarray(SB.pull_out(a, t).convert('RGB'))
    if PULL_MODE == '2':
        return np.asarray(SB.pull_out2(a, t, IRIS).convert('RGB'))
    return np.asarray(a)


def render(fn, t, log=None):
    if fn == 't5':
        return np.asarray(to_pil(M.t5(t, log)))
    return t6_full(t, log)


def lin_y(a):
    c = a.astype(np.float32) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def Lst(y): return float(116 * np.cbrt(y) - 16) if y > 0.008856 else float(903.3 * y)


def pairs(sig):
    """opposing swings -> flash pairs; sig: sequence of -1 / 0 / +1"""
    nz = [s for s in sig if s != 0]
    rev = sum(1 for i in range(1, len(nz)) if nz[i] != nz[i - 1])
    return (rev + 1) // 2 if nz else 0


def window_max(sig, n):
    best = 0
    for i in range(max(1, len(sig) - n + 1)):
        best = max(best, pairs(sig[i:i + n]))
    return best


def whole(frames):
    Y = np.array([lin_y(f).mean() for f in frames])
    G = np.array([float((f.astype(np.float32) * np.array([.2126, .7152, .0722])).sum(-1).mean() / 255.0) for f in frames])
    dG = np.diff(G); dY = np.diff(Y)
    rel = (np.abs(dG) > 0.10 * np.maximum(G[1:], G[:-1]).clip(0.02)) * np.sign(dG)
    absw = ((np.abs(dY) >= 0.10) & (np.minimum(Y[1:], Y[:-1]) < 0.80)) * np.sign(dY)
    return dict(frame_mean_Lstar=[round(Lst(y), 1) for y in Y], max_frame_Lstar=round(Lst(Y.max()), 1), min_frame_Lstar=round(Lst(Y.min()), 1),
                max_step_Lstar=round(float(np.max(np.abs(np.diff([Lst(y) for y in Y])))), 2),
                rel10_swings=int(np.abs(rel).sum()), rel10_flash_pairs=pairs(rel), wcag_abs_swings=int(np.abs(absw).sum()), wcag_abs_flash_pairs=pairs(absw))


def tiles(frames, fps, cell=60):
    """per 60 px tile at 960 px (120 px at 1080p; about 1/16 of the frame width): the strict relative check (opposing luma swings over
    10 % of the brighter tile) and the WCAG absolute check (relative luminance change >= 0.10, darker below 0.80); worst tile in the
    clip and in any 1 s window"""
    sm = [np.asarray(Image.fromarray(f).resize((960, 540), Image.BOX)) for f in frames]
    G = np.stack([(s.astype(np.float32) * np.array([.2126, .7152, .0722])).sum(-1) / 255.0 for s in sm])
    Y = np.stack([lin_y(s) for s in sm])
    n, h, w = G.shape
    def tl(A): return A[:, :h // cell * cell, :w // cell * cell].reshape(n, h // cell, cell, w // cell, cell).mean((2, 4))
    Gt, Yt = tl(G), tl(Y)
    dG, dY = np.diff(Gt, axis=0), np.diff(Yt, axis=0)
    rel = (np.abs(dG) > 0.10 * np.maximum(Gt[1:], Gt[:-1]).clip(0.02)) * np.sign(dG)
    absw = ((np.abs(dY) >= 0.10) & (np.minimum(Yt[1:], Yt[:-1]) < 0.80)) * np.sign(dY)
    out = {}
    for nm, S in (('rel10', rel), ('wcag_abs', absw)):
        worst, worst_w, where = 0, 0, None
        for i in range(S.shape[1]):
            for j in range(S.shape[2]):
                s = list(S[:, i, j])
                p = pairs(s)
                pw = window_max(s, fps)
                if pw > worst_w or (pw == worst_w and p > worst):
                    where = [j * cell * 2, i * cell * 2]
                worst = max(worst, p); worst_w = max(worst_w, pw)
        out[nm] = dict(worst_tile_flash_pairs_clip=worst, worst_tile_flash_pairs_any_1s=worst_w, worst_tile_xy_1080=where)
    out['tile_px_1080'] = cell * 2
    return out


def face_check(log):
    """ART_BIBLE 1.2: bits never travel across the wheel face.  Inside the rim (r < 492) a ring / ticket bit may only sit on its own
    target angle (radial in / out); a card bit never enters the rim."""
    bad, inside, n = 0, 0, 0
    worst = 0.0
    for e in log:
        x, y, kind, stream, tht = e
        n += 1
        r = math.hypot(x - CX, y - CY)
        if r >= 492:
            continue
        inside += 1
        if kind == 'card':
            bad += 1
            continue
        dev = abs(math.degrees(wrap(math.atan2(y - CY, x - CX) - tht)))
        worst = max(worst, dev)
        if dev > 2.0:
            bad += 1
    return dict(glyph_draws=n, draws_inside_rim=inside, draws_off_their_radial=bad, worst_angle_deviation_deg=round(worst, 3))


def save_gif(frames, path, dur_ms):
    sm = [Image.fromarray(f).resize((960, 540), Image.BOX) for f in frames]
    q = [s.quantize(colors=200, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for s in sm]
    q[0].save(path, save_all=True, append_images=q[1:], duration=dur_ms, loop=0, optimize=False, disposal=1)
    return os.path.getsize(path) / 1e6


BADGE = {'R': ('REAL', (150, 255, 70)), 'G': ('RENDER', (180, 150, 255)), 'C': ('COMP', (70, 200, 255))}


def tile(arr, label, kind, w=384):
    im = Image.fromarray(arr).resize((w, int(w * 9 / 16)), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    tw = d.textlength(label, font=LABF) + 10
    d.rectangle([0, 0, tw, 21], fill=(12, 10, 22)); d.text((5, 3), label, font=LABF, fill=(242, 246, 255))
    bt, bc = BADGE[kind]
    bw = d.textlength(bt, font=TAGF) + 10
    d.rectangle([w - bw, 0, w, 18], fill=bc); d.text((w - bw + 5, 2), bt, font=TAGF, fill=(10, 10, 10))
    return im


def strip(arrs, labels, kinds, title, path):
    ts = [tile(a, l, k) for a, l, k in zip(arrs, labels, kinds)]
    tw, th = ts[0].size
    cols = 4
    rows = (len(ts) + cols - 1) // cols
    S = Image.new('RGB', (tw * cols + 6 * (cols + 1), 40 + rows * (th + 6)), (12, 10, 22))
    d = ImageDraw.Draw(S); d.text((8, 8), title, font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 20), fill=(255, 61, 168))
    for i, im in enumerate(ts):
        r, c = divmod(i, cols)
        S.paste(im, (6 + c * (tw + 6), 36 + r * (th + 6)))
    S.save(path, quality=90)


if __name__ == '__main__':
    print('setup', round(time.time() - T0, 1), flush=True)
    res = {}
    for fn, LEN, KEYS in (('t5', T5_LEN, T5K), ('t6', T6_LEN, T6K)):
        n = int(round(LEN * FPS)) + 1
        times = [round(i / FPS, 4) for i in range(n)]
        log = []
        fr = {}
        for t in times:
            fr[t] = render(fn, t, log)
        for t, _ in KEYS:
            if t not in fr:
                fr[t] = render(fn, t, log)
        print(fn, 'frames', len(fr), round(time.time() - T0, 1), flush=True)
        seq25 = [fr[t] for t in times]
        seq12 = seq25[::2]
        mb = save_gif(seq12, OUT + '%s_A.gif' % fn, 80)
        for t, _ in KEYS:
            Image.fromarray(fr[t]).save(OUT + 'keys/%s_%03d.png' % (fn, int(round(t * 100))))
        res[fn] = dict(gif_mb=round(mb, 2), gif_frames=len(seq12), gif_fps=12.5, gif_ms=80,
                       whole_12p5fps=whole(seq12), whole_25fps=whole(seq25), tiles_25fps=tiles(seq25, FPS), wheel_face=face_check(log))
        res[fn]['keys'] = [dict(t=t, label=l) for t, l in KEYS]
        if fn == 't5':
            res[fn]['first_frame_vs_room_bare_maxdiff'] = float(np.abs(fr[0.0].astype(int) - np.clip(K1ROOM + 0.5, 0, 255).astype(np.uint8).astype(int)).max())
            res[fn]['last_frame_vs_plate_maxdiff'] = float(np.abs(fr[1.2].astype(int) - PLATE.astype(int)).max())
            res[fn]['frame_1p16_vs_plate_maxdiff'] = float(np.abs(fr[1.16].astype(int) - PLATE.astype(int)).max())
        else:
            res[fn]['first_frame_vs_plate_maxdiff'] = float(np.abs(fr[0.0].astype(int) - PLATE.astype(int)).max())
            ref = np.asarray(SB.STREET_CLEARED) if PULL else np.clip(K1ROOM + 0.5, 0, 255).astype(np.uint8)
            res[fn]['last_frame_vs_%s_maxdiff' % ('street' if PULL else 'room_bare')] = float(np.abs(fr[0.8].astype(int) - ref.astype(int)).max())
            res[fn]['pull_out_composited'] = PULL
        nm = {'neutral': 'neutral skin', 'solace': 'Solace skin'}[CORP]
        kinds = []
        for t, _ in KEYS:
            if fn == 't5':
                kinds.append('R' if t in (0.0, 1.2) else 'G')
            else:
                kinds.append('R' if (t == 0.0 or (t == 0.8 and not PULL)) else ('C' if t == 0.8 else 'G'))
        title = {'t5': 'T5 room to combat, bits option A on the round-2 board, every frame rendered from the generator (%s)' % nm,
                 't6': 'T6 combat to netrun (win path), bits option A on the round-2 board, camera holds on the room (%s)' % nm}[fn]
        if fn == 't6' and PULL:
            title = 'T6 combat to netrun (win path), bits option A on the round-2 board, with the T4-reverse pull-out (%s)' % nm
        strip([fr[t] for t, _ in KEYS], ['%s %s' % (fn.upper(), l) for _, l in KEYS], kinds, title, OUT + 'strip_%s.jpg' % fn)
        print(fn, {k: v for k, v in res[fn].items() if k in ('gif_mb', 'wheel_face')}, flush=True)
        print('  whole12.5', {k: v for k, v in res[fn]['whole_12p5fps'].items() if k != 'frame_mean_Lstar'}, flush=True)
        print('  tiles25', res[fn]['tiles_25fps'], flush=True)
        del fr, seq25, seq12
    res['corp'] = CORP
    res['bits'] = json.load(open(HERE + 'out/bits_%s.json' % CORP)) if os.path.exists(HERE + 'out/bits_%s.json' % CORP) else None
    res['params'] = dict(bit_font='Share Tech Mono (corp/src/fonts/ShareTechMono-Regular.ttf), outline 1/22 of size in the bit colour',
                         bit_L_clamp=list(BIT_L), sample_disc_px=SAMPLE_R, sample_chroma_percentile=SAMPLE_PCT, white_hot_s=WHITE_HOT_S,
                         white_hot_rgb=list(HOT_WHITE), flip_s=FLIP_S, orbit_r_px=list(R_ORBIT), rim_r_px=R_RIM, k1_room='v3.1 bare room (T4 end frame)',
                         bit_alpha=M.BIT_A,
                         density_c13=dict(rule='a ring / spinner / ticket bit whose route goes d degrees round the rim from the lab is kept with '
                                               'p = near - (near - far) * clamp((d - d0) / (180 - d0)); card bits are not thinned',
                                          d0_deg=M.DARK_D0, t5_near=M.DARK_NEAR, t5_far=M.DARK_KEEP, t6_near=M.DARK_NEAR6, t6_far=M.DARK_KEEP6,
                                          t5_bits_kept=dict((nm, '%d of %d' % (int(G['keep'].sum()), G['n'])) for nm, G in
                                                            zip(('ring NOW', 'ring +1', 'ring +2', 'frame band'), M.G5)),
                                          t5_ticket_bits_kept='%d of %d' % (int(M.TK['keep'].sum()), M.NTK),
                                          t6_bits_kept=dict((nm, '%d of %d' % (int(G['keep'].sum()), G['n'])) for nm, G in
                                                            zip(('ring NOW', 'ring +1', 'ring +2', 'frame band', 'spinner'), M.G6)),
                                          t6_ticket_bits_kept='%d of %d' % (int(M.TK['keep6'].sum()), M.NTK)),
                         pull_out=dict(mode=PULL_MODE, iris=IRIS if PULL_MODE == '2' else None))
    json.dump(res, open(OUT + 'metrics_%s.json' % CORP, 'w'), indent=1)
    print('done', round(time.time() - T0, 1))
