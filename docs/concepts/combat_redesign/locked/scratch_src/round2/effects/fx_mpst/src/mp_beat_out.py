"""mp_beat_out.py: the published resolve beat files from the rendered frames and the meters
  locked/effects/resolve_beat_strip.jpg : header, track chart, keyframes (full motion), reduce-motion keyframes, a skip, flash results
  locked/effects/resolve_beat.gif       : the beat at 30 fps, 640 px wide (< 6 MB), then 0.5 s settled"""
import sys, os, json, glob
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
import mp_beat as B
import mp_beat_render as BR
from mp_lib import ME, OUTD, font, to_img, PINK, SCHED, VIOLET, P_STOCK

FC = {'T': PINK, 'M': PINK, 'S': VIOLET, 'P': P_STOCK, 'D': (255, 61, 168), 'L': (120, 230, 140), '-': (150, 150, 160)}
BG = (12, 12, 18)


def gif():
    fs = sorted(glob.glob(ME + 'work/beat/full_[0-9]*.npz'))
    rgb = np.concatenate([np.load(f)['rgb'] for f in fs])
    w = 640
    for w, step in ((640, 2), (560, 2), (480, 2), (480, 3)):
        h = int(round(w * 9 / 16))
        frames = []
        fnt = font('mono', 12)
        for i in range(0, len(rgb), step):
            T = i * 1000.0 / 60
            c = Image.new('RGB', (w, h + 20), BG)
            c.paste(Image.fromarray(rgb[i]).resize((w, h), Image.LANCZOS), (0, 0))
            dd = ImageDraw.Draw(c)
            act = '+'.join(n for n, s, du, f, cc in B.TRACKS if s <= T < s + du) or 'settled'
            cap = '%4d ms  %s' % (T, act)
            if T < B.TL['twist'] + B.DUR['twist']:
                cap += '  | ring +1 one sector back: NOT TO SHIP (rules question)'
            dd.text((4, h + 3), cap[:96], font=fnt, fill=(255, 140, 120) if 'NOT TO SHIP' in cap else (200, 204, 220))
            frames.append(c)
        frames += [frames[-1]] * int(15 / step * 2)
        # one palette for the whole GIF, from 32 sampled frames, median cut refined by k-means (gif_try.py: mean dE76 2.6, p95 8.4 against
        # the source frames; the 8-frame median cut it replaces was 4.0 / 15.9 and turned the slice inks: olive went tan, green went teal)
        pal = Image.fromarray(np.concatenate([np.asarray(frames[i]) for i in range(0, len(frames), max(1, len(frames) // 32))], 0)).quantize(colors=255, method=Image.Quantize.MEDIANCUT, kmeans=4)
        q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
        fp = OUTD + 'resolve_beat.gif'
        q[0].save(fp, save_all=True, append_images=q[1:], duration=int(round(1000 * step / 60.0)), loop=0, optimize=True, disposal=1)
        sz = os.path.getsize(fp)
        print('gif', w, step, len(q), sz, flush=True)
        if sz < 6e6:
            return dict(width=w, height=h, caption_px=20, fps=round(60 / step, 1), frames=len(q), bytes=sz)
    raise SystemExit('gif too big')


def chart(w, meter):
    rows = B.TRACKS
    rh = 24
    h = 40 + rh * len(rows) + 40
    im = Image.new('RGB', (w, h), (20, 20, 28))
    d = ImageDraw.Draw(im)
    x0, x1 = 420, w - 30
    T1 = 4000
    sx = lambda t: x0 + (x1 - x0) * t / T1
    f = font('mono', 15)
    for t in range(0, T1 + 1, 250):
        d.line([(sx(t), 30), (sx(t), h - 30)], fill=(46, 46, 60) if t % 1000 else (80, 80, 100), width=1)
        if t % 500 == 0:
            d.text((sx(t) - 14, 8), '%d' % t, font=f, fill=(170, 170, 190))
    d.line([(sx(B.TOTAL_MS), 30), (sx(B.TOTAL_MS), h - 30)], fill=(120, 230, 140), width=2)
    d.line([(sx(4000), 30), (sx(4000), h - 30)], fill=(255, 90, 80), width=2)
    for i, (nm, s, du, fam, what) in enumerate(rows):
        y = 36 + i * rh
        d.text((10, y + 2), what[:44], font=font('mono', 14), fill=(220, 220, 232))
        d.rectangle([sx(s), y + 4, sx(s + du), y + rh - 4], fill=FC.get(fam, (200, 200, 200)))
        d.text((sx(s + du) + 6, y + 3), '%s %d-%d' % (nm, s, s + du), font=font('mono', 12), fill=(170, 176, 196))
    flashes = meter['beat']['whole']['flash_ms']
    for (t, _) in flashes:
        d.line([(sx(t), 30), (sx(t), h - 30)], fill=(255, 214, 0), width=1)
    d.text((10, h - 26), 'green: the beat settles at %d ms; red: the 4 s limit; yellow ticks: whole-frame flashes (%d). Any input skips: the frame dissolves to the settled frame in %d ms.'
           % (B.TOTAL_MS, len(flashes), B.SKIP_MS), font=font('mono', 14), fill=(170, 176, 196))
    return im


def tile(fp_or_img, cap, w, col=(230, 232, 240), frame_col=None):
    im = fp_or_img if isinstance(fp_or_img, Image.Image) else Image.open(fp_or_img).convert('RGB')
    im = im.resize((w, int(w * 9 / 16)), Image.LANCZOS)
    out = Image.new('RGB', (w, im.height + 26), BG)
    out.paste(im, (0, 0))
    d = ImageDraw.Draw(out)
    if frame_col:
        d.rectangle([0, 0, w - 1, im.height - 1], outline=frame_col, width=3)
    d.text((2, im.height + 4), cap, font=font('mono', 14), fill=col)
    return out


HINT_ROW = {}
HINT_KEYS = (60, 1400, 3760)        # ms: fading in, mid beat, fading out
HINT_CROP = (1380, 560, 1920, 760)  # plate px: the HUD foot, the REFUND tab and the SKIP tab, at 1x


def hint_row(W_):
    """C12: the SKIP key hint at 1x (no resize), at three beat times, cropped from the full-size keyframe renders"""
    x0, y0, x1, y1 = HINT_CROP
    cw, chh = x1 - x0, y1 - y0
    f = font('mono', 15)
    out = Image.new('RGB', (W_, 40 + chh + 30), BG)
    d = ImageDraw.Draw(out)
    d.text((16, 8), 'C12 SKIP KEY HINT AT 1x (crops of the full-size beat frames, not resized): %s' % ', '.join('%d ms (opacity %.2f)' % (t, B.skip_hint_k(t)) for t in HINT_KEYS),
           font=font('mono', 18), fill=(120, 200, 255))
    x = 16
    HINT_ROW.update(crop=list(HINT_CROP), tiles=[])
    for t in HINT_KEYS:
        fr = to_img(B.frame(float(t))).crop(HINT_CROP)
        out.paste(fr, (x, 40))
        d.text((x, 40 + chh + 6), '%d ms' % t, font=f, fill=(200, 204, 220))
        HINT_ROW['tiles'].append(dict(t_ms=t, x0=x, y0=40, opacity=round(B.skip_hint_k(t), 3)))
        x += cw + 20
    return out


def main():
    mf = json.load(open(ME + 'work/beat/meter_full.json'))
    mr = json.load(open(ME + 'work/beat/meter_red.json'))
    g = gif()
    W_ = 2900
    tw = 470
    head = Image.new('RGB', (W_, 400), BG)
    d = ImageDraw.Draw(head)
    d.text((16, 6), 'RESOLVE BEAT  |  E10 p3, neutral skin, round-2 board 2026-11-04  |  %d ms (limit 4000), skip on any input' % B.TOTAL_MS, font=font('anton', 34), fill=(255, 255, 255))
    lines = [
        'Every effect is the set\'s own at its own timing, each <= 600 ms (VfxTier T2, no override): M/P/S/T from mp_eff, C/D/H/L from fx_cdhl (round 2: one source folder, the one the published sheets use). Concurrent tracks in the HUD chain order: SEND IT, 1 TWIST, 2 TRIGGER (Trace, hits, Packet 1 dies, refund), 4 GUNS, 3 BRACE + 5 LANDS, 6 RINGS STEP, W4 enters.  '
        'C12 (round 2): the SKIP key hint "ANY KEY  SKIP" (HUD label spec, Share Tech Mono 23) hangs under the HUD foot at its right end for the length of the beat; the 1x row at the foot of this strip shows it at full size.',
        'Layer (review 1.6): every effect is on the board under the HUD and the hand, except trace_add and refund (allowed to cross). Kill marks in the cause colour, CELL_PINK (review 1.8).',
        'Flash meter (60 fps, NOTES_MPST method): full motion: whole frame %d flash(es), worst region %d / s; reduce motion: worst region %d / s; skip at every 250 ms: worst region %d / s (full), %d / s (reduce). Limit 3 / s: %s.'
        % (mf['beat']['whole']['flashes'], mf['max_flashes_per_s_beat'], mr['max_flashes_per_s_beat'], mf['max_flashes_per_s_skips'], mr['max_flashes_per_s_skips'],
           'PASS' if (mf['passes'] and mr['passes']) else 'FAIL'),
        'NOT TO SHIP (rules question, REVIEW_RESPONSE "Shove bump, Twist render"): f2 already holds ring +1 where Twist leaves it, so this beat draws ring +1 one sector back from SEND IT until Twist turns it.',
    ]
    import textwrap
    y = 54
    fm = font('mono', 15)
    ncol = int((W_ - 40) / fm.getlength('n'))
    for i, s_ in enumerate(lines):
        for ln in textwrap.wrap(s_, ncol):
            d.text((16, y), ln, font=fm, fill=(255, 140, 120) if i == 3 else ((120, 230, 140) if i == 2 and mf['passes'] and mr['passes'] else (200, 204, 220)))
            y += 20
        y += 6
    head = head.crop((0, 0, W_, y + 6))
    ch = chart(W_, mf)
    keys = []
    for k in BR.KEYS:
        act = '+'.join(n for n, s, du, f, c in B.TRACKS if s <= k < s + du) or 'settled'
        keys.append(tile(ME + 'work/beat/key_full_%d.png' % k, '%d ms  %s' % (k, act[:52]), tw))
    reds = [tile(ME + 'work/beat/key_red_%d.png' % k, 'REDUCE %d ms' % k, tw, (255, 214, 0), (255, 214, 0)) for k in (250, 1160, 2250, 3000, 3650)]
    Ts = 1500
    skp = [tile(to_img(B.frame(Ts)), 'SKIP pressed at %d ms' % Ts, tw, (120, 200, 255), (120, 200, 255)),
           tile(to_img(B.skip_frame(Ts + 100, Ts, B.frame(Ts + 100))), 'skip + 100 ms (dissolving)', tw, (120, 200, 255), (120, 200, 255)),
           tile(to_img(B.settled()), 'skip + %d ms: settled' % B.SKIP_MS, tw, (120, 200, 255), (120, 200, 255))]
    per = 6
    rows = [keys[i:i + per] for i in range(0, len(keys), per)] + [reds[:per]] + [skp]
    th = keys[0].height
    one = hint_row(W_)
    Ht = head.height + ch.height + 20 + len(rows) * (th + 10) + 20 + one.height
    S = Image.new('RGB', (W_, Ht), BG)
    S.paste(head, (0, 0))
    S.paste(ch, (0, head.height))
    yy = head.height + ch.height + 20
    for r in rows:
        x = 16
        for t_ in r:
            S.paste(t_, (x, yy))
            x += tw + 10
        yy += th + 10
    S.paste(one, (0, yy + 10))
    HINT_ROW['strip_y0'] = yy + 10
    fp = OUTD + 'resolve_beat_strip.jpg'
    q = 90
    while True:
        S.save(fp, quality=q)
        if os.path.getsize(fp) < 3.5e6 or q < 60:
            break
        q -= 6
    print('strip', fp, S.size, os.path.getsize(fp), flush=True)
    json.dump(dict(gif=g, strip=dict(size=S.size, bytes=os.path.getsize(fp), quality=q), hint_row=HINT_ROW), open(ME + 'work/beat/out.json', 'w'))


if __name__ == '__main__':
    main()
