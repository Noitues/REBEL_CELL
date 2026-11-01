"""Build everything: three finals, placeholder overlays, key strips, flash report, squints, sheet.jpg. Compositing only."""
import sys, json, os, importlib
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/transitions/netrun_fail/scripts')
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from nf_lib import OUT, ph_overlay, FONTS, ROOT
import nf_trans as T

PLATE = Image.open(ROOT + 'combat_e10_design/final/p1_decide.png').convert('RGB')
DES = [('A', 'A_crt_feed', 'CRT FEED CUTS TO SIGNAL LOST', 'The netrun street feed tears and drops; DISPATCH speaks; the run log reads out the loss.'),
       ('B', 'B_route_map', 'THE ROUTE, STRUCK', 'The run as a node route: lime where we walked, a red grease X where we fell, the loss written on the HUD chips.'),
       ('C', 'C_trace_printout', 'SOLACE PRINTS THE TRACE REPORT', 'The corp prints its own intrusion report over the dimmed street; the Cell pins one note to it.')]


def F(n, s):
    return ImageFont.truetype(FONTS[n], s)


KEYT = [0.0, 0.12, 0.20, 0.34, 0.60]
KEYL = ['0.00 s  combat lost (E10 plate)', '0.12 s  HUD out, board tears', '0.20 s  hard cut, tear on new feed', '0.34 s  panel opens, tear settles', '0.60 s  settled, input live']
RT = [0.0, 0.125, 0.25]


def lin(a):
    a = a / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def luma_lin(im):
    a = lin(np.asarray(im.convert('RGB'), np.float32))
    return a @ np.array([0.2126, 0.7152, 0.0722], np.float32)


def flash_report(a, bg, full):
    size = (480, 270)
    frames = [T.frame(a, bg, full, k / 60.0, size=size) for k in range(0, 37)]
    Ls = [luma_lin(f) for f in frames]
    means = [float(l.mean()) for l in Ls]
    ev = []
    maxd = 0.0
    maxarea = 0.0
    for i in range(1, len(Ls)):
        d = Ls[i] - Ls[i - 1]
        inc = float((d >= 0.10).mean())
        dec = float((d <= -0.10).mean())
        maxd = max(maxd, abs(means[i] - means[i - 1]))
        maxarea = max(maxarea, inc, dec)
        if inc >= 0.25:
            ev.append(1)
        elif dec >= 0.25:
            ev.append(-1)
    flashes = sum(1 for i in range(1, len(ev)) if ev[i] != ev[i - 1])
    gm = [float(np.asarray(f.convert('L'), np.float32).mean() / 255) for f in frames]
    rev = 0
    last = 0
    for i in range(1, len(gm)):
        d = gm[i] - gm[i - 1]
        if abs(d) >= 0.10 * max(gm[i], gm[i - 1], 1e-3):
            s = 1 if d > 0 else -1
            if last and s != last:
                rev += 1
            last = s
    return dict(frames=len(frames), fps=60, duration_s=0.6, mean_linear_first=round(means[0], 4), mean_linear_last=round(means[-1], 4),
                max_step_mean_linear=round(maxd, 4), max_area_changed_ge_0p10=round(maxarea, 4),
                wcag_style_flash_pairs=flashes, strict_mean_reversals=rev,
                flashes_per_second_extrapolated=round(max(flashes, rev) / 0.6, 2), limit_per_second=3)


def keystrip(name, a, bg, full, title):
    tw_, th_ = 372, 209
    Wd = 1920
    img = Image.new('RGB', (Wd, 790), (8, 10, 18))
    d = ImageDraw.Draw(img)
    d.text((16, 10), 'NETRUN FAIL  %s   0.6 s glitch-in, 5 key frames   (%s)' % (name, title), font=F('mono', 24), fill=(150, 255, 70))
    for i, t in enumerate(KEYT):
        fr = T.frame(a, bg, full, t).resize((tw_, th_), Image.LANCZOS)
        x = 16 + i * (tw_ + 15)
        img.paste(fr, (x, 52))
        tag = 'REAL' if i == 0 else 'CONCEPT'
        col = (150, 255, 70) if i == 0 else (255, 160, 50)
        d.rectangle([x, 52, x + 20 + d.textlength(tag, font=F('anton', 20)), 82], fill=col)
        d.text((x + 10, 56), tag, font=F('anton', 20), fill=(12, 10, 22))
        d.text((x, 52 + th_ + 8), 'K%d  %s' % (i + 1, KEYL[i]), font=F('mono', 17), fill=(215, 215, 222))
    y0 = 52 + th_ + 56
    d.text((16, y0), 'REDUCED MOTION: 0.25 s cross-fade, combat plate to the screen (frames at 0.00, 0.125, 0.25 s); no tear, static or scanline pulse', font=F('mono', 19), fill=(92, 225, 255))
    for i, t in enumerate(RT):
        fr = T.reduced(a, full, t).resize((tw_, th_), Image.LANCZOS)
        x = 16 + i * (tw_ + 15)
        img.paste(fr, (x, y0 + 38))
        d.text((x, y0 + 38 + th_ + 8), 'R%d  %.3f s' % (i + 1, t), font=F('mono', 17), fill=(215, 215, 222))
    x = 16 + 3 * (tw_ + 15)
    notes = ['Timing (T6 FAIL branch, STORYBOARD):', 'hard glitch cut at 0.20 s, 0.3 s settle,', 'panel opens 0.30 s, input at 0.60 s.', '',
             'Safety: tearing only moves rows (no', 'brightening), one luminance step (the cut).', 'See flash_report.json.', '',
             'Reduce-effects ON: tear, static, scanlines', 'and chroma split drop out; no effect', 'carries information.']
    for k, s in enumerate(notes):
        d.text((x, y0 + 44 + k * 24), s, font=F('mono', 17), fill=(175, 192, 214))
    img = img.crop((0, 0, Wd, min(790, y0 + 38 + th_ + 60)))
    img.save(OUT + 'keys_%s.jpg' % name, quality=90)


def squint(im):
    return im.resize((120, 68), Image.BOX).filter(ImageFilter.GaussianBlur(0.7)).resize((1920, 1080), Image.BICUBIC)


def stats(sq):
    a = np.asarray(sq, np.float32) / 255
    l = a @ np.array([0.299, 0.587, 0.114], np.float32)
    return dict(mean=float(l.mean()), p95=float(np.percentile(l, 95)), loud=float((l > 0.38).mean()))


def main():
    res = {}
    imgs = {}
    for k, fn, title, idea in DES:
        m = importlib.import_module('build_' + k)
        bg, full, ph = m.build()
        full.save(OUT + fn + '.png')
        ph_overlay(full, ph).save(OUT + fn + '_placeholders.png')
        sq = squint(full)
        sq.save(OUT + 'squint_' + k + '.png')
        res[k] = dict(file=fn + '.png', title=title, idea=idea, squint=stats(sq), flash=flash_report(PLATE, bg, full), ph=sorted(set(n for _, n in ph)))
        keystrip(k, PLATE, bg, full, title)
        imgs[k] = (full, sq)
        print(k, res[k]['squint'], res[k]['flash'])
    res['plate_squint'] = stats(squint(PLATE))
    json.dump(res, open(OUT + 'flash_report.json', 'w'), indent=1)
    Wd, tw_, th_ = 1920, 624, 351
    sh = Image.new('RGB', (Wd, 960), (8, 10, 18))
    d = ImageDraw.Draw(sh)
    d.text((16, 10), 'NETRUN-FAILURE SCREEN (T6 FAIL)   three designs at 1920x1080   Solace slice, CELL-9 // BREAKER', font=F('mono', 26), fill=(150, 255, 70))
    for i, (k, fn, title, idea) in enumerate(DES):
        x = 12 + i * (tw_ + 12)
        sh.paste(imgs[k][0].resize((tw_, th_), Image.LANCZOS), (x, 56))
        d.rectangle([x, 56, x + 44, 92], fill=(255, 160, 50))
        d.text((x + 10, 58), k, font=F('anton', 30), fill=(12, 10, 22))
        d.text((x, 56 + th_ + 6), title, font=F('anton', 26), fill=(92, 225, 255))
        words = idea.split()
        line = ''
        yy = 56 + th_ + 40
        for w in words:
            if d.textlength(line + ' ' + w, font=F('mono', 16)) > tw_:
                d.text((x, yy), line, font=F('mono', 16), fill=(215, 215, 222))
                yy += 20
                line = w
            else:
                line = (line + ' ' + w).strip()
        d.text((x, yy), line, font=F('mono', 16), fill=(215, 215, 222))
    y2 = 56 + th_ + 120
    d.text((16, y2 - 4), 'SQUINT  1/16 scale + blur 0.7   (mean luminance / p95 / loud share > 0.38)', font=F('mono', 20), fill=(255, 160, 50))
    for i, (k, fn, title, idea) in enumerate(DES):
        x = 12 + i * (tw_ + 12)
        sh.paste(imgs[k][1].resize((tw_, th_), Image.LANCZOS), (x, y2 + 28))
        s = res[k]['squint']
        d.text((x, y2 + 28 + th_ + 6), '%s   mean %.2f   p95 %.2f   loud %.1f%%' % (k, s['mean'], s['p95'], s['loud'] * 100), font=F('mono', 20), fill=(150, 255, 70))
    sh.save(OUT + 'sheet.jpg', quality=90)


main()
