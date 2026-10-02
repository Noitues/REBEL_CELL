"""Storyboards (one labelled PNG per GIF, with timings) and motion_layers.png (the layer breakdown)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import cm
import fx
import make_heat
import make_incursion

BG = (16, 15, 20)
INK = (236, 228, 210)
DIM = (150, 144, 160)
PW, PH = 640, 360


def sheet(title, sub, panels, cols, timeline=None, path=None):
    """panels: [(img, caption, note)]."""
    rows = (len(panels) + cols - 1) // cols
    pad = 24
    top = 92
    tl_h = 50 + 20 * len({s[2].split(":")[0] for s in timeline[2]}) if timeline else 0
    W = cols * PW + (cols + 1) * pad
    H = top + rows * (PH + 78) + pad + tl_h
    sh = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(sh)
    d.text((pad, 20), title, font=cm.font(34), fill=INK)
    d.text((pad, 62), sub, font=cm.font(16, False), fill=DIM)
    for n, (im, cap, note) in enumerate(panels):
        r, c = divmod(n, cols)
        x = pad + c * (PW + pad)
        y = top + r * (PH + 78)
        sh.paste(im.resize((PW, PH), Image.LANCZOS), (x, y))
        d.rectangle([x, y, x + PW - 1, y + PH - 1], outline=(60, 56, 70))
        d.text((x, y + PH + 8), cap, font=cm.font(18), fill=(212, 255, 0))
        _wrap(d, (x, y + PH + 32), note, cm.font(14, False), DIM, PW)
    if timeline:
        _timeline(d, pad, H - tl_h + 10, W - 2 * pad, timeline)
    sh.save(path, optimize=True)
    print('wrote', os.path.basename(path), sh.size)


def _wrap(d, xy, text, f, col, w):
    x, y = xy
    line = ''
    for word in text.split(' '):
        t = (line + ' ' + word).strip()
        if d.textlength(t, font=f) > w - 4:
            d.text((x, y), line, font=f, fill=col)
            y += 18
            line = word
        else:
            line = t
    if line:
        d.text((x, y), line, font=f, fill=col)


def _timeline(d, x, y, w, tl):
    total, ms, spans = tl
    d.text((x, y), 'TIMELINE  (%d frames x %d ms = %.2f s, loops)' % (total, ms, total * ms / 1000), font=cm.font(16),
           fill=INK)
    y0 = y + 30
    lane_h = 16
    lanes = {}
    for a, b, label, col in spans:
        lane = lanes.setdefault(label.split(':')[0], len(lanes))
    for a, b, label, col in spans:
        ln = lanes[label.split(':')[0]]
        yy = y0 + ln * (lane_h + 4)
        xa, xb = x + w * a / total, x + w * b / total
        d.rectangle([xa, yy, xb, yy + lane_h], fill=col)
        d.text((xa + 4, yy + lane_h / 2), label, font=cm.font(12), fill=(10, 9, 16), anchor='lm')
    for k in range(0, total + 1, 12):
        xx = x + w * k / total
        d.line([(xx, y0 - 6), (xx, y0 - 2)], fill=DIM)
        d.text((xx, y0 - 8), '%.1fs' % (k * ms / 1000), font=cm.font(10, False), fill=DIM, anchor='mb')


def boards():
    out = cm.ROOT
    # ---- ambient
    for th in ('night', 'day'):
        s = cm.Scene(th)
        N = 48
        p = []
        notes = {
            0: 'f0  0.00 s. Double-deck highway A on avenue j=4 (lower deck pink rails, upper cyan) crosses high deck B '
               '(amber rails) over the Sprawl; both ramp down to street level.',
            12: 'f12  0.96 s. Headlights one way, tail lights the other on every avenue; cars hide behind towers '
                '(depth buffer from the layout prims). Billboards switch panel with a wipe.',
            24: 'f24  1.92 s. Fog banks drift and blur what is under them (blur amount follows fog density); '
                'fog thins round district labels so HQs stay readable.',
            36: 'f36  2.88 s. Flying cars on three sky lanes (chase-light markers), aviation lights blink on the '
                'tallest 26 towers, steam puffs from street and roof vents.' + (' Rain + splashes.' if th == 'night' else ''),
        }
        for f in (0, 12, 24, 36):
            p.append((s.frame(f, N), 'f%d  /  %.2f s' % (f, f * 0.08), notes[f]))
        tl = (48, 80, [(0, 48, 'traffic: lanes move 1-3 car gaps per loop', (255, 236, 200)),
                       (0, 16, 'holo: panel A', (255, 60, 200)), (16, 32, 'holo: panel B', (60, 230, 255)),
                       (32, 48, 'holo: panel C', (255, 170, 40)),
                       (0, 3, 'blink', (255, 60, 60)), (24, 27, 'blink', (255, 60, 60)),
                       (0, 48, 'fog/rain/steam: one seamless loop (fog = crossfaded drift)', (170, 160, 230))])
        sheet('CITY AMBIENT  -  %s  (calm Heat)' % th.upper(),
              'city_ambient_%s.gif  -  960x540, 48 frames x 80 ms = 3.84 s seamless loop. Base: round 6 approved restyle '
              '(%s). Every moving layer is placed from city_layout.json.' % (th, 'restyle_%s_full.png' % th), p, 2, tl,
              os.path.join(out, 'storyboard_ambient_%s.png' % th))
    # ---- heat
    s = cm.Scene('night')
    h = make_heat.Heat(s)
    p = []
    notes = {
        14: 'NOTICED (Heat 31, 0.0-3.1 s): three rotating alarm beacons on side buildings round the turf. Nothing on '
            'the target. The Cell\'s Sites (lime pads) + links stay visible.',
        38: 'FLAGGED cut (3.1 s): the Heat chip flashes orange and counts 31 -> 58 over 8 frames; side beacons off.',
        56: 'FLAGGED (Heat 58, 3.1-6.1 s): two searchlights sweep the sky from side blocks (30-frame sweep), two alarms '
            'ON the target roofs.',
        76: 'HUNTED cut (6.1 s): chip flashes red, police clusters pop in one by one along the turf\'s streets.',
        96: 'HUNTED (Heat 82): two choppers circle the turf (60 / 44-frame orbits) with jiggling spotlights, six drones '
            'with mini spots, two searchlights on the target.',
        114: 'HUNTED end: a third chopper has entered from the right edge, crossed the turf and leaves top-left; then '
             'the loop cuts back to NOTICED.',
    }
    for f in notes:
        im = s.frame(f, 40, extra=h.draw, opts=dict(rain=False, fog_drift=False))
        h.hud(im, f)
        p.append((im, 'f%d  /  %.2f s' % (f, f * 0.085), notes[f]))
    tl = (120, 85, [(0, 36, 'band: NOTICED 31', (255, 196, 40)), (36, 72, 'band: FLAGGED 58', (255, 128, 32)),
                    (72, 120, 'band: HUNTED 82', (255, 70, 80)),
                    (0, 36, 'fx: 3 side beacons', (255, 120, 60)), (36, 72, 'fx: 2 sky lights + 2 target alarms', (214, 230, 255)),
                    (72, 120, 'fx: police x13, 2 lights, alarms', (120, 150, 255)),
                    (72, 120, 'air: 2 circling choppers + 6 drones; 3rd chopper crosses in/out', (200, 205, 220))])
    sheet('CITY HEAT LEVELS  -  NOTICED > FLAGGED > HUNTED',
          'city_heat_levels.gif  -  800x450 (rendered 960x540), 120 frames x 85 ms = 10.2 s. Locked language: round 22 '
          'heat_city_v4 (backdrop) + round 19/20 raid choppers and drones.', p, 3, tl,
          os.path.join(out, 'storyboard_heat_levels.png'))
    # ---- incursion
    inc = make_incursion.Incursion(s)
    p = []
    notes = {
        4: 'f4  calm night; the Cell\'s two Sites + CORE link (lime) on the turf.',
        10: 'f6-11  Halcyon HQ raises the alarm: violet rings pulse off the pyramid, amber beacons on its corners; '
            'INCURSION WARNING banner drops in.',
        22: 'f12-32  two threat routes draw along real avenues toward two Cell Sites (violet trace, amber chevrons '
            'flowing toward the Cell).',
        30: 'f22+  armoured carriers (violet hull, white roof plate, amber light bar, violet street spill) roll out '
            'in two convoys of three.',
        44: 'f22-40  three choppers lift off the HQ top, climb, then peel away on separate arcs; spotlights switch on '
            'once airborne.',
        60: 'f58  RAID INBOUND line under the banner; the two targeted Sites ring red.',
        72: 'f60-84  choppers orbit the targets with jiggling spots; convoys close to their last block.',
        83: 'f83  end frame (convoys parked on the approach), loop cuts to calm.',
    }
    for f in notes:
        im = s.frame(f, 42, extra=inc.draw, opts=dict(rain=False, fog_drift=False))
        inc.ui(im, f)
        p.append((im, 'f%d  /  %.2f s' % (f, f * 0.085), notes[f]))
    tl = (84, 85, [(6, 84, 'hq: HQ alarm rings + beacons', (140, 123, 255)), (6, 84, 'ui: banner', (255, 80, 90)),
                   (12, 36, 'route: routes draw', (220, 210, 255)), (22, 84, 'conv: convoys roll (52-frame ease)', (255, 176, 40)),
                   (22, 84, 'air: choppers lift, peel off, orbit', (200, 205, 220)), (58, 84, 'ui2: RAID INBOUND + Site warning rings', (255, 52, 60))])
    sheet('CITY INCURSION WARNING  -  HALCYON CIVIC -> REBEL_CELL',
          'city_incursion.gif  -  960x540, 84 frames x 85 ms = 7.1 s. Corp livery from round 20 (Halcyon: violet + amber).',
          p, 4, tl, os.path.join(out, 'storyboard_incursion.png'))


def layers():
    s = cm.Scene('night')
    f, N = 18, 48
    t = f / N
    tiles = []

    def blank():
        im = Image.new('RGB', (cm.W * cm.SS, cm.H * cm.SS), (0, 0, 0))
        return im, ImageDraw.Draw(im, 'RGBA')

    def show(im, bloom=True):
        if bloom:
            im = cm._add_bloom(Image.new('RGB', im.size), im, 1.0)
        return im.resize((cm.W, cm.H), Image.LANCZOS)

    tiles.append((s.base1, '0  BASE', 'Round 6 restyle, static (one big texture or the baked city). Everything below sits on it.'))
    im, d = blank()
    s.draw_traffic(d, d, t)
    tiles.append((show(im), '1  STREET TRAFFIC', 'Path2D per avenue run, cars = MultiMesh quads on PathFollow2D offsets; '
                  'occluded by a depth mask baked from the building prims.'))
    im = Image.new('RGB', (cm.W * cm.SS, cm.H * cm.SS), (24, 22, 30))
    d = ImageDraw.Draw(im, 'RGBA')
    s.draw_highways(d, d, t, True)
    s.draw_highways(d, d, t, False)
    tiles.append((show(im, False), '2  ELEVATED HIGHWAYS', 'Static deck sprites (A double-deck, B high) + rails; lane traffic '
                  'on Path2D at deck height. Drawn above the base, below fog.'))
    im, d = blank()
    s.draw_billboards(im, im, d, f)
    s.draw_avlights(d, f)
    tiles.append((show(im), '3  HOLOS + AVIATION LIGHTS', 'Billboards: quad + shader (UV scroll, scanlines, flicker, panel '
                  'wipe) on an atlas of illegible glyph panels. Blinkers: one shader, phase per instance.'))
    im, d = blank()
    s.draw_flyers(d, d, t)
    tiles.append((show(im), '4  SKY LANES', 'Flying cars on 3 Path2D lanes 70-120 px up, Line2D trails, chase-light lane '
                  'markers. Drawn above fog.'))
    dens = s.fog_density(t)
    fog = (np.clip(dens[..., None] * np.array((170, 160, 230)) * 1.6, 0, 255)).astype(np.uint8)
    tiles.append((Image.fromarray(fog), '5  FOG DENSITY', 'Two tileable noise samples crossfaded while drifting (seamless loop); '
                  'density drives both tint and blur. Thinned round district labels.'))
    arr = np.zeros((cm.H * cm.SS, cm.W * cm.SS, 3), np.float32)
    st = s.apply_steam(arr, t)
    lay = s.apply_rain(Image.fromarray(np.clip(st, 0, 255).astype(np.uint8)), t)
    tiles.append((lay.resize((cm.W, cm.H), Image.LANCZOS), '6  RAIN + STEAM', 'GPUParticles2D: rain (2 depths, '
                  'streak texture), splash sub-emitter on visible streets, steam puffs from 13 vents.'))
    m = s.tilt_mask(dens)
    tiles.append((Image.fromarray((m * 255).astype(np.uint8)).convert('RGB'), '7  TILT-SHIFT MASK',
                  'Post pass: blur(mask) where mask = top/bottom bands max fog density. Labels/HUD drawn after.'))
    tiles.append((s.frame(f, N), '8  COMPOSITE', 'All layers, bloom on light layers, labels on top.'))
    sheet('MOTION LAYERS  -  how the living city is built', 'Night, f18. Order bottom -> top. See NOTES.md for the Godot 4.7 build.',
          tiles, 3, None, os.path.join(cm.ROOT, 'motion_layers.png'))


if __name__ == '__main__':
    which = sys.argv[1:] or ['boards', 'layers']
    if 'boards' in which:
        boards()
    if 'layers' in which:
        layers()
