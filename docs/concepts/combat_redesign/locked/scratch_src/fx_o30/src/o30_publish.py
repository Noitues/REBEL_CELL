"""o30_publish.py strip | gif : resolve_beat_strip.jpg (keyframes labelled with ms + the flash timeline) and resolve_beat.gif"""
import sys, os, json, math
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFont

O30 = 'D:/rc_scratch/combat_redesign/locked/fx_o30/'
OUT = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/effects/'
FD = 'D:/rc_scratch/combat_redesign/locked/corp/src/fonts/'


def F(kind, px):
    return ImageFont.truetype(FD + {'anton': 'Anton-Regular.ttf', 'mono': 'ShareTechMono-Regular.ttf'}[kind], px)


# (segment, local ms, caption, crop centre (x, y) on the 1920x1080 frame)
KEYS = [('commit', 330, 'SEND IT: pencil burns to paint', (520, 700)),
        ('twist', 330, 'TWIST: ring +1 turns a sector', (536, 540)),
        ('trace_add', 200, 'TRIGGER played: Trace 3 to 4', (1440, 700)),
        ('trigger_hit', 260, 'Payload trigger hits Packet 1 (s3)', (470, 720)),
        ('refund', 400, 'Packet 1 dead: refund, RAM 2 to 3', (900, 560)),
        ('gun_hit', 210, 'GUNS: s0 BURST hits Worm 2', (420, 360)),
        ('kill', 120, 'shot 2: Worm 2 dies', (420, 400)),
        ('ricochet_gold', 160, 's4 shots warded by Packet 6', (530, 830)),
        ('shield_block', 300, 'LANDS: Worm 3 on s1 SHIELD, absorbed 2', (760, 400)),
        ('soak_take', 520, 's1 soaked 1', (720, 440)),
        ('brace_block', 440, 's2 TURRET braced 3', (780, 650)),
        ('clear', 300, 'THROUGH 0: clear', (880, 380)),
        ('settle', 200, 'hand-off: ring 0 and arcs clear', (536, 540)),
        ('rings_step', 460, 'RINGS STEP: one ring in, +2', (536, 540)),
        ('wave_enter', 500, 'W4 enters ring +2', (330, 250)),
        ('wave_enter', 1060, 'settled (300 ms after)', (536, 540))]
TW, TH = 640, 360          # tile
CW, CH = 800, 450          # crop on the frame (scaled to the tile)


def strip():
    import o30_render as RR
    segs, n = RR.timeline()
    byname = {s['name']: s for s in segs}
    meters = {m: json.load(open(O30 + 'work/meter_%s.json' % m)) for m in ('full', 'red') if os.path.exists(O30 + 'work/meter_%s.json' % m)}
    cols = 4
    rows = (len(KEYS) + cols - 1) // cols
    pad, lab = 12, 44
    head, tlh = 120, 230
    Wd = pad + cols * (TW + pad)
    Hd = head + tlh + rows * (TH + lab + pad) + pad
    sh = Image.new('RGB', (Wd, Hd), (14, 14, 20))
    d = ImageDraw.Draw(sh)
    d.text((pad, 8), 'E10 p3 RESOLVE BEAT, SEQUENCED (O-30)', font=F('anton', 40), fill=(255, 255, 255))
    total = segs[-1]['start'] + segs[-1]['dur']
    d.text((pad, 62), 'Neutral skin, final board. Order = the HUD chain (TWIST, TRIGGER, BRACE, GUNS, LANDS, RINGS STEP / W4), opened by SEND IT. '
           'Each effect starts 100 ms after the previous one ends (GODOT_PORT_SPEC 8.2); 400 ms hold before RINGS STEP. Beat total %d ms.' % total, font=F('mono', 17), fill=(200, 205, 220))
    mtxt = []
    for m, M in meters.items():
        mtxt.append('%s motion: max %d flash/s in any region (whole frame %d, effect boxes %d, tiles 240/120/60 px %d/%d/%d) -> %s' % (
            'full' if m == 'full' else 'reduce', M['max_flashes_per_s_any_region'], M['whole']['max_flashes_per_s'],
            max(b['max_flashes_per_s'] for b in M['boxes'].values()), M['tiles']['240']['max_flashes_per_s'], M['tiles']['120']['max_flashes_per_s'],
            M['tiles']['60']['max_flashes_per_s'], 'PASS (<= 3)' if M['passes'] else 'FAIL'))
    for i, t in enumerate(mtxt):
        d.text((pad, 86 + i * 0 + (i * 18) - 0), t, font=F('mono', 15), fill=(120, 230, 140))
    # timeline
    x0, x1 = pad + 120, Wd - pad - 10
    y = head + 20
    pre = 100
    span = total + 300 + pre

    def X(ms):
        return x0 + (ms + pre) / span * (x1 - x0)
    pal = [(255, 61, 168), (92, 225, 255), (255, 226, 0), (160, 60, 255), (123, 224, 123), (255, 140, 26), (217, 225, 234)]
    for k, s in enumerate(segs):
        c = pal[k % len(pal)]
        d.rectangle([X(s['start']), y, X(s['start'] + s['dur']), y + 40], fill=tuple(int(v * 0.55) for v in c), outline=c, width=2)
        d.text((X(s['start']) + 3, y + 44 + (k % 2) * 18), s['name'], font=F('mono', 14), fill=c)
    for ms in range(0, total + 301, 1000):
        d.line([X(ms), y + 88, X(ms), y + 96], fill=(160, 160, 170), width=2)
        d.text((X(ms) - 10, y + 98), '%d s' % (ms // 1000), font=F('mono', 13), fill=(160, 160, 170))
    d.text((pad, y + 10), 'sequence', font=F('mono', 15), fill=(230, 230, 240))
    yy = y + 124
    for m, M in meters.items():
        d.text((pad, yy - 2), 'flashes %s' % ('full' if m == 'full' else 'reduce'), font=F('mono', 15), fill=(230, 230, 240))
        d.line([x0, yy + 8, x1, yy + 8], fill=(60, 60, 70), width=1)
        pts = set()
        for tdict in [M['whole']] + list(M['boxes'].values()) + [t for v in M['tiles'].values() for t in v['worst']]:
            for (tms, nm) in tdict['flash_ms']:
                pts.add(round(tms))
        for tms in sorted(pts):
            d.line([X(tms), yy, X(tms), yy + 16], fill=(255, 214, 0), width=2)
        yy += 30
    d.text((pad, yy + 2), 'yellow tick = a counted flash in any measured region (whole frame, effect box, or a 240/120/60 px tile); the limit is 3 in any 1 s window per region.',
           font=F('mono', 13), fill=(170, 170, 180))
    # keyframes
    ty = head + tlh
    for k, (nm, lt, cap, (cx, cy)) in enumerate(KEYS):
        s = byname[nm]
        T = s['start'] + lt
        i = RR.seg_at(segs, T)
        RR._cv.clear()
        fr = RR.render_c(segs, i, T - segs[i]['start'], False, 'full')
        im = Image.fromarray(np.clip(fr, 0, 255).astype(np.uint8))
        cw, ch = (CW, CH) if nm not in ('twist', 'settle', 'rings_step') and lt < 1000 else (1600, 900)
        bx = int(min(max(cx - cw // 2, 0), 1920 - cw))
        by = int(min(max(cy - ch // 2, 0), 1080 - ch))
        tile = im.crop((bx, by, bx + cw, by + ch)).resize((TW, TH), Image.LANCZOS)
        x = pad + (k % cols) * (TW + pad)
        yk = ty + (k // cols) * (TH + lab + pad)
        sh.paste(tile, (x, yk))
        d.text((x, yk + TH + 4), '%d ms   %s +%d' % (T, nm, lt), font=F('mono', 18), fill=(255, 214, 0))
        d.text((x, yk + TH + 24), cap, font=F('mono', 15), fill=(230, 232, 240))
        print('key', k, nm, T, flush=True)
    fp = OUT + 'resolve_beat_strip.jpg'
    q = 90
    while True:
        sh.save(fp, quality=q)
        if os.path.getsize(fp) < 4.5e6 or q < 60:
            break
        q -= 5
    print('strip', fp, os.path.getsize(fp), sh.size)


def gif(mode='full'):
    jd = O30 + 'frames/%s/' % mode
    files = sorted(f for f in os.listdir(jd) if f.endswith('.jpg'))
    # big version (scratch): 960 px at 30 fps
    def build(step, w, fp, colors=128):
        h = int(w * 9 / 16)
        # one global palette from a montage of 16 frames across the beat (keeps the spot inks saturated, compresses better)
        pick = files[::max(1, len(files) // 16)][:16]
        mont = Image.new('RGB', (w * 4, h * 4))
        for k, f in enumerate(pick):
            mont.paste(Image.open(jd + f).convert('RGB').resize((w, h), Image.LANCZOS), ((k % 4) * w, (k // 4) * h))
        pal = mont.quantize(colors=colors, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
        frames = []
        for f in files[::step]:
            im = Image.open(jd + f).convert('RGB')
            if im.width != w:
                im = im.resize((w, h), Image.LANCZOS)
            frames.append(im.quantize(palette=pal, dither=Image.Dither.NONE))
        dur = int(round(1000.0 / 60 * step))
        frames[0].save(fp, save_all=True, append_images=frames[1:], duration=dur, loop=0, optimize=True, disposal=1)
        return os.path.getsize(fp)
    big = O30 + 'resolve_beat_%s_960_30fps.gif' % mode
    print('big', build(2, 960, big, 160))
    fp = OUT + 'resolve_beat.gif'
    for step, w, col in ((3, 960, 192), (3, 640, 192), (3, 640, 128), (3, 560, 128), (4, 560, 96), (4, 480, 96)):
        sz = build(step, w, fp, col)
        print('gif', step, w, col, sz, flush=True)
        if sz < 6e6:
            break


if __name__ == '__main__':
    if sys.argv[1] == 'strip':
        strip()
    else:
        gif(sys.argv[2] if len(sys.argv) > 2 else 'full')
