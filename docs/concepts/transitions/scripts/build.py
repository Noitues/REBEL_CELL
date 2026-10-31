"""Build the transitions storyboard strips, sheet.jpg and STORYBOARD.md.
Run: python build.py   (inputs are existing frames only; no Godot)."""
import os, textwrap, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
R = 'D:/rc_art/art-pass/docs/concepts/'
OUT = R + 'transitions/'
W, H = 1920, 1080
LIME = (150, 255, 70)


def F(sz, b=False):
    try:
        return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if b else 'C:/Windows/Fonts/arial.ttf', sz)
    except Exception:
        return ImageFont.load_default()


def L(rel, half=False):
    p = rel if ':' in rel else R + rel
    im = Image.open(p).convert('RGB')
    if half:
        im = im.crop((im.width // 2, 0, im.width, im.height))
    return im.resize((W, H), Image.LANCZOS)


NR = 'netrun_cel/godot_zoom/stage_%d_base.png'
MP = 'cohesion/map_pages_r42/'
TR = 'tide_raid/G1_parity/final_proposed/'


def zc(im, cx, cy, z):
    w, h = W / z, H / z
    x0 = min(max(cx * W - w / 2, 0), W - w)
    y0 = min(max(cy * H - h / 2, 0), H - h)
    return im.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.LANCZOS)


def blend(a, b, t):
    return Image.blend(a, b, t)


def zblur(im, amt=0.06, n=7):
    acc = None
    for i in range(n):
        z = 1 + amt * i / (n - 1)
        f = zc(im, .5, .5, z) if z > 1 else im
        acc = f if acc is None else Image.blend(acc, f, 1 / (i + 1))
    return acc


def dark(im, k):
    return ImageEnhance.Brightness(im).enhance(k)


def desat(im, k):
    return ImageEnhance.Color(im).enhance(k)


def vig(im, k=.55):
    m = Image.new('L', (W // 8, H // 8), 0)
    ImageDraw.Draw(m).ellipse((-W // 16, -H // 16, W // 8 + W // 16, H // 8 + H // 16), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(40)).resize((W, H))
    return Image.composite(im, dark(im, k), m)


def iris(a, b, r, cx=.5, cy=.5):
    m = Image.new('L', (W, H), 0)
    R_ = r * W
    box = (cx * W - R_, cy * H - R_, cx * W + R_, cy * H + R_)
    ImageDraw.Draw(m).ellipse(box, fill=255)
    out = Image.composite(b, a, m)
    ImageDraw.Draw(out).ellipse(box, outline=LIME, width=6)
    return out


def scanlines(im, a=.18):
    m = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(m)
    for y in range(0, H, 4):
        d.line((0, y, W, y), fill=int(255 * a))
    return Image.composite(dark(im, .6), im, m)


def shrink_on(base, top, s, cx=.5, cy=.5, rot=0):
    t = top.resize((int(W * s), int(H * s)), Image.LANCZOS).convert('RGBA')
    if rot:
        t = t.rotate(rot, expand=True, resample=Image.BICUBIC)
    out = base.convert('RGBA')
    sh = Image.new('RGBA', t.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 170), (0, 0, t.width, t.height), t.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(24))
    out.alpha_composite(sh, (int(cx * W - t.width / 2 + 18), int(cy * H - t.height / 2 + 26)))
    out.alpha_composite(t, (int(cx * W - t.width / 2), int(cy * H - t.height / 2)))
    return out.convert('RGB')


def check(im, cx, cy):
    d = ImageDraw.Draw(im)
    x, y = cx * W, cy * H
    d.ellipse((x - 34, y - 34, x + 34, y + 34), outline=LIME, width=7)
    d.line((x - 16, y, x - 4, y + 14, x + 18, y - 14), fill=LIME, width=8)
    return im


NODE = (.49, .46)  # the chosen fight node on route_page

T = []


def add(**k):
    T.append(k)


city = L(NR % 1)
dist = L(NR % 2)
near = L(NR % 3)
st4 = L(NR % 4)
st5 = L(NR % 5)
route = L(MP + 'route_page.png')
hq = L(MP + 'hq_idle.png')
hqs = L(MP + 'hq_node_selected.png')
rsetup = L(MP + 'raid_setup.png')
bare = L('combat_backdrop/v2/room_srv_bare.png')
room = L('combat_backdrop/v2/room_srv.png')
e10 = L('D:/rc_tmp/combat_critic/plates/waves_e10/p1_decide.png')
winA = L('solace_endscreens/v2/win_A.png')
loseA = L('solace_endscreens/v2/lose_A.png')
rb = {n: L(TR + n + '_side_by_side.png', half=True) for n in
      ['01_plan', '02_forecast', '03_reveal', '04_impact', '05_home_hit', '06_aftermath', '07_city_lost']}

add(id='t1', file='t1_city_to_netrun.jpg', title='1  City Grid to netrun: zoom into the district and street',
    dur='1.4 s', ease='smootherstep on log(ppb), no overshoot; about 2.1 octaves per s peak (see open point 1)',
    keys=[('K1  0.00 s  City Grid, JACK IN pressed', hq),
          ('K2  0.30 s  chrome out, iso ortho push', zblur(zc(city, .62, .5, 1.25), .05)),
          ('K3  0.65 s  district, ppb ~15, still iso', zblur(dist, .06)),
          ('K4  0.95 s  dolly-zoom to perspective, pitch 40 to 12', blend(zblur(near, .06), st4, .35)),
          ('K5  1.20 s  near street, horizon dropping', blend(st4, st5, .55)),
          ('K6  1.40 s  street camera, route chrome in', vig(st5, .8))],
    cam='ZOOM_RULES 5.5, one continuous path, no cut and no ortho/perspective jump. City plan (iso, yaw 135, pitch 40, ortho 394) to district (ortho 130) in the first 0.65 s; a dolly-zoom (fov 8 to 40, distance shrinking so the focus ppb stays constant) between 0.65 and 0.95 s; pitch 12 to 0, lens shift 0 to 0.24 and eye 30 m to 4 m for the last 0.45 s. The focus lot (the first route node) stays on the screen thirds throughout, so the geometry seen in the city is the geometry the player lands in.',
    ui='0.00-0.25 s: city HUD (resource strip, VIEW LOADOUT, JACK IN, crew tray) slides 24 px outward and fades. 0.25-0.95 s: no chrome, only the lime route ribbon fading in over the pavement from 0.6 s. 1.05-1.40 s: NETRUN tab, route legend and the threat card fade up in 4 staggered 60 ms steps; input unlocks at 1.40 s. Chrome never overlaps the camera dolly.',
    rm='Cut with a 0.2 s cross-fade from the city to the street frame (K1 to K6); route chrome appears with the fade. No camera motion, no zoom blur.',
    feel='Falling into one specific street of the city you were just looking at, fast and committed, then landing still.')
add(id='t2', file='t2_route_to_combat.jpg', title='2  Netrun route to combat: into the chosen building (cutaway)',
    dur='0.8 s', ease='ease-in (cubic) for the push, ease-out (cubic) for the room settle; the wheel scales in with a 90 ms overshoot of 4 %',
    keys=[('K1  0.00 s  route page, node chosen', route),
          ('K2  0.20 s  push into the node, chrome dims', zblur(dark(zc(route, *NODE, 2.2), .8), .05)),
          ('K3  0.40 s  lime iris from the node opens on the cutaway', iris(zblur(zc(route, *NODE, 3.2), .06), scanlines(bare), .22)),
          ('K4  0.55 s  room settles, iso cutaway, board absent', bare),
          ('K5  0.70 s  wheel scales in 0.8 to 1.0, HUD slides in', blend(bare, room, .55)),
          ('K6  0.80 s  E10 combat board, input live', e10)],
    cam='The camera keeps pushing at the chosen node (the building on the street) with a 3.2x total scale; an iris in the route colour (lime) opens from the node centre and reveals the iso cutaway of its interior (kit room chosen by Site kind). The room is already composed at the same iso angle as the city (yaw 135, pitch 40), so the last 0.25 s is no camera move, only a 2 % settle.',
    ui='0.00-0.20 s: route chrome (NETRUN tab, dossier card, legend, footer) dims to 40 % and drifts out. 0.20-0.55 s: no chrome; the iris edge is the only graphic. 0.55-0.80 s: turn banner and wave ledger slide in from the top right, the wheel scales in from 0.8, cards deal from the bottom edge (60 ms stagger), SEND IT last. No input until 0.80 s.',
    rm='Cross-fade 0.25 s from the route page to the combat board; no iris, no push, no deal animation (the UI is simply there).',
    feel='Breaking through the wall into the room you picked: a hard, short beat, then the board owns the screen.')
add(id='t3', file='t3_combat_to_route.jpg', title='3  Combat back to the route',
    dur='0.7 s', ease='ease-in-out (smoothstep); the pull-out is ease-out cubic',
    keys=[('K1  0.00 s  combat won, E10 board', e10),
          ('K2  0.20 s  wheel collapses, HUD out', blend(blend(e10, bare, .55), room, .15)),
          ('K3  0.35 s  bare cutaway room', bare),
          ('K4  0.50 s  iris closes, pull-out to the street', iris(zblur(zc(route, *NODE, 3.2), .06), scanlines(bare), .10)),
          ('K5  0.60 s  route page, node shows cleared', check(zblur(dark(zc(route, *NODE, 1.4), .85), .03), .5, .5)),
          ('K6  0.70 s  route page, next layer lit', check(route.copy(), *NODE))],
    cam='The reverse of T2 at a shorter run: board and wheel collapse toward the centre (scale 1.0 to 0.8), the iso room holds for a beat, an iris closes on the node, and the camera pulls out 3.2x to 1.0x onto the route page. The route page lands on the framing it was left in (no camera drift between nodes).',
    ui='0.00-0.20 s: SEND IT, hand, turn banner and wave ledger fade; the wheel scales to 0.8 with a 40 % fade. 0.20-0.35 s: only the empty room. 0.35-0.55 s: iris and pull-out. 0.50-0.70 s: route chrome fades up and the cleared-node check stamps in at 0.60 s with a 120 ms pop; the next layer starts its lime pulse at 0.70 s. Reward and shop screens, if any, slot in before K5 as a panel over the room (not drawn here).',
    rm='Cross-fade 0.25 s from the combat board to the route page; the cleared check is already drawn.',
    feel='Stepping back out of the building with the job done, and the route still where you left it.')
add(id='t4', file='t4_netrun_end_to_city.jpg', title='4  Netrun end to City Grid, then the win or lose file folder',
    dur='1.9 s (1.0 s zoom-out, 0.9 s folder)', ease='zoom-out: the T1 path in reverse, smootherstep; folder: ease-out cubic slide with a 0.3 s settle',
    keys=[('K1  0.00 s  last node resolved, route page', route),
          ('K2  0.40 s  zoom out begins, route chrome fading', zblur(blend(route, dist, .6), .05)),
          ('K3  1.00 s  City Grid, helix visible, city dimmed', dark(city, .6)),
          ('K4  1.30 s  folder drops on the city (tilt -2 deg)', shrink_on(dark(city, .45), winA, .78, .5, .5, rot=-2)),
          ('K5  1.90 s  WIN: folder open, ROUTED stamp, helix lime to cyan', winA),
          ('K6  1.90 s  LOSE: nodes crossed out, helix pink (branch of K5)', loseA)],
    cam='Zoom-out along the T1 path in reverse (street to district to city) for 1.0 s; it stops at the city plan camera, not a closer one, so the helix and the corp district are on screen. The end screen is a UI card, not a camera move: the folder comes down from above the frame onto the dimmed city, and the camera is locked from K3 on.',
    ui='0.00-0.35 s: route chrome fades. 0.35-1.00 s: nothing but the zoom. 1.00-1.30 s: the city darkens to 45 %; the folder (crest tab, hazard strip, routing slip) slides down from 140 px above, tilting from -4 to -2 degrees. 1.30-1.90 s: the ROUTED (win) or FILED (lose) stamp thuds on at 1.6 s, the summary fields type in line by line (30 ms per char), the grease-pencil marks draw last (WIN: red marks on the network; LOSE: nodes crossed out, Bloom spreading). MAIN MENU and NEW CAMPAIGN arm at 1.90 s.',
    rm='Cut from the route page to the folder with a 0.25 s cross-fade over the dimmed city; the stamp and all marks are pre-drawn; no slide, no typing.',
    feel='The run is over and the corporation is already filing it: relief on a win, a quiet chill on a loss.')
add(id='t5', file='t5_city_to_raid.jpg', title='5  City Grid to raid setup, defense, result',
    dur='0.9 s to setup + 0.6 s to defense + 1.0 s to result = 2.5 s of motion', ease='setup: smootherstep (T1 at a gentler angle); defense start: ease-out cubic; result: ease-in-out, with a 0.3 s hold on the last frame before the panel',
    keys=[('K1  0.00 s  city plan, raid warning has fired', rb['01_plan']),
          ('K2  0.90 s  RAID SETUP: threat intel and lane tray in', rsetup),
          ('K3  1.50 s  START DEFENSE: the raid arrives on the lane', rb['03_reveal']),
          ('K4  2.00 s  impact at the defended node', rb['04_impact']),
          ('K5  2.50 s  RESULT held: the city stands, aftermath', rb['06_aftermath']),
          ('K6  2.50 s  RESULT lost: CITY LOST (branch of K5)', desat(dark(rb['07_city_lost'], .8), .6))],
    cam='City plan camera 1.0 to 1.5x about the raid target (the plate camera used by the raid beats, zoom 1.5 about plate px 722,500), 0.9 s, so the iso angle never changes and the setup panels lie over the same city. START DEFENSE: no camera move, 0.6 s of UI swap while the raid FX start from the edge. Defense runs in the same camera (gameplay, not storyboarded). Result: a slow 1.0 to 1.1x push on the impact point over 1.0 s.',
    ui='0.00-0.25 s: city HUD out. 0.25-0.90 s: the STRAIN AUDIT file card slides in from the left, THREAT INTEL from the right, the lane tray rises from the bottom (80 ms stagger). 0.90-1.50 s: on START DEFENSE the setup cards slide out, the wave and defense HUD slide in; the first raid beats are the forecast then the reveal. 2.00-2.50 s: HUD out, a result banner (HELD or CITY LOST) and the aftermath tally; CITY LOST also desaturates the city to 60 % over 0.5 s.',
    rm='Each of the three steps is a 0.25 s cross-fade between its two screens; the raid FX plays at normal speed in the defense step; no push, no slides.',
    feel='Seeing the threat come for your city, then the weight of the hit: setup is calm, impact is sharp, the result is quiet.')
add(id='t6', file='t6_city_to_hq.jpg', title='6  City to HQ approach (a unique, hand-authored netrun)',
    dur='1.2 s plus 0.4 s settle', ease='smootherstep on log(ppb) for the descent; the lateral slide eases in-out; the HQ page then holds still',
    keys=[('K1  0.00 s  City Grid, HQ avenue pointing at the helix', city),
          ('K2  0.30 s  push toward the helix 1.6x', zblur(zc(city, .79, .30, 1.6), .05)),
          ('K3  0.65 s  2.6x, helix grows, district behind', zblur(zc(city, .80, .28, 2.6), .06)),
          ('K4  0.95 s  4x, plaza, avenue lights streak', zblur(zc(city, .80, .28, 4.0), .06)),
          ('K5  1.20 s  authored HQ page takes over, chrome in', blend(zc(city, .80, .28, 4.0), hq, .55)),
          ('K6  1.60 s  HQ netrun idle, node picked, JACK IN', hqs)],
    cam='Not the T1 path: the HQ netrun is hand-authored, so only the city behind it is procedural. The camera stays iso (no perspective swap) and slides along the HQ avenue toward the helix: ortho width 394 to about 95 over 1.2 s with a 6 degree yaw settle, ending on the composition of the HQ page. K5 is a 0.25 s cross-dissolve to the authored plate; zoom blur is on for K2 to K4 only. These keys are crops of the city frame, so the dissolve is a proof of concept; the real one is a Godot cross-dissolve with the city camera and the HQ plate camera matched.',
    ui='0.00-0.20 s: city HUD out. 0.20-1.00 s: only a thin lime avenue ribbon draws along the road toward the helix. 1.00-1.60 s: HQ chrome in (file card on the left, node dossier on the right, crew tray, JACK IN) with a 60 ms stagger; input unlocks at 1.60 s.',
    rm='Cut with a 0.25 s cross-fade from the city to the HQ page; the avenue ribbon is not drawn.',
    feel='Approaching the corporation that built the city, deliberately and a little ominously, with the helix growing as the street narrows.')


def thumb_strip(tr):
    n = len(tr['keys'])
    cols = 3
    rows = math.ceil(n / cols)
    tw, th = 616, 347
    g = 24
    lab = 36
    mx = 36
    blocks = [('DURATION', tr['dur']), ('EASING', tr['ease']), ('CAMERA', tr['cam']), ('UI HAND-OVER', tr['ui']),
              ('REDUCED MOTION', tr['rm']), ('FEEL', tr['feel'])]
    f = F(19)
    fb = F(19, True)
    lines = [(h, textwrap.wrap(t, 150) or ['']) for h, t in blocks]
    th_text = sum(len(w) for _, w in lines) * 25 + len(lines) * 33 + 20
    top = 70
    Wd = mx * 2 + cols * tw + (cols - 1) * g
    Ht = top + rows * (th + lab + g) + th_text + 20
    S = Image.new('RGB', (Wd, Ht), (14, 15, 20))
    d = ImageDraw.Draw(S)
    d.text((mx, 18), tr['title'], font=F(34, True), fill=LIME)
    for i, (lb, im) in enumerate(tr['keys']):
        r, c = divmod(i, cols)
        x = mx + c * (tw + g)
        y = top + r * (th + lab + g)
        S.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        d.rectangle((x - 1, y - 1, x + tw, y + th), outline=(70, 75, 90))
        d.text((x, y + th + 6), lb, font=F(18, True), fill=(235, 235, 240))
        if c < cols - 1 and i < n - 1:
            d.polygon([(x + tw + 4, y + th // 2 - 14), (x + tw + 20, y + th // 2), (x + tw + 4, y + th // 2 + 14)], fill=LIME)
    y = top + rows * (th + lab + g) + 8
    for h, wr in lines:
        d.text((mx, y), h, font=fb, fill=(255, 170, 60))
        y += 25
        for w in wr:
            d.text((mx, y), w, font=f, fill=(215, 215, 222))
            y += 25
        y += 8
    return S


def sheet():
    tw, th = 300, 169
    lab = 22
    g = 10
    lw = 330
    mx = 24
    cols = max(len(t['keys']) for t in T)
    Wd = mx * 2 + lw + cols * (tw + g)
    rowh = th + lab + g
    S = Image.new('RGB', (Wd, 60 + len(T) * rowh + 10), (14, 15, 20))
    d = ImageDraw.Draw(S)
    d.text((mx, 14), 'REBEL_CELL transitions storyboard: six strips, existing frames only', font=F(26, True), fill=LIME)
    for r, t in enumerate(T):
        y = 60 + r * rowh
        d.text((mx, y + 4), t['title'][:1], font=F(34, True), fill=(255, 170, 60))
        for k, w in enumerate(textwrap.wrap(t['title'][3:], 26)[:4]):
            d.text((mx + 36, y + 6 + k * 20), w, font=F(16, True), fill=(235, 235, 240))
        d.text((mx, y + 100), textwrap.wrap(t['dur'], 34)[0], font=F(16), fill=LIME)
        for i, (lb, im) in enumerate(t['keys']):
            x = mx + lw + i * (tw + g)
            S.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
            d.text((x, y + th + 3), lb[:46], font=F(13), fill=(200, 200, 208))
    return S


def md():
    o = ['# Transitions storyboard (art-pass, 2026-10-30)\n',
         'Concept job, assembled from existing frames (netrun_cel/godot_zoom, cohesion/map_pages_r42, combat_backdrop/v2, solace_endscreens/v2, tide_raid/G1_parity/final_proposed, the E10 plate) with crops, scaling, blends, iris and zoom blur. No Godot work, no game design. Intermediate frames are fakes: crops of the nearest real frame, soft at 3x to 4x. They prove sequence and timing, not polish. Built by `scripts/build.py`.\n',
         '`sheet.jpg` shows all six strips; one jpg per transition follows.\n',
         '## Timing table\n', '| # | Transition | Full motion | Reduced motion | Easing |', '|---|---|---|---|---|']
    for t in T:
        o.append('| %s | %s | %s | 0.25 s cross-fade | %s |' % (t['id'], t['title'][3:], t['dur'], t['ease']))
    o += ['', 'Consistency rules used: scripted zoom between bands 1.4 s; a hard entry into a building 0.8 s; leaving it 0.7 s (shorter than entering: the player already knows where they are); no UI on screen while the camera moves through the district; every reduced-motion variant is a cross-fade of 0.25 s (under the 0.3 s cap) with the chrome appearing with it.\n']
    for t in T:
        o += ['## %s\n' % t['title'], '![%s](%s)\n' % (t['id'], t['file']),
              '- **Keys:** ' + '; '.join(k[0].strip() for k in t['keys']),
              '- **Duration:** ' + t['dur'], '- **Easing:** ' + t['ease'], '- **Camera path:** ' + t['cam'],
              '- **UI hand-over:** ' + t['ui'], '- **Reduced motion:** ' + t['rm'], '- **Feel:** ' + t['feel'], '']
    o += ['## Open points (raised for art-pass; not decided here)\n',
          '1. **T1 speed vs ZOOM_RULES 5.5.** 5.5 caps the zoom at 0.5 octaves of ppb per second (a x3 zoom takes about 2.2 s). The full path from city (ppb 4.9) to street (ppb 38) is about 3 octaves, so the cap gives about 6 s, not 1.4 s. This storyboard assumes the cap is the rate for the player-driven wheel zoom and that the scripted JACK IN move is exempt (peak about 2.1 octaves per s at smootherstep). If the cap must stay, T1 becomes about 6 s and needs a skip. Designer or build to decide; the roadmap asks for about 1.4 s.',
          '2. **Street camera vs route page.** T1 lands on the street camera (K6); T2 and T3 start and end on the iso route page, because that is the existing frame. Whether these are one screen or two is a build question.',
          '3. **T2/T3 assume the interior kit room is composed at the city iso angle** (as the v2 backdrops are), so the cutaway reveal needs no camera swap. A procedural kit render for the real Site kinds is still to come.',
          '4. **T4 stops the zoom-out at the city plan camera** so the folder lands on the city; the designer may prefer the folder over the street. Cheap to change (K3).',
          '5. **T5** shows the held and lost results as branches; the forecast beat is the opening 0.3 s of the defense step and has no key. raid_setup is the existing r42 map page.',
          '6. **T6 K2 to K5 are crops of the city frame** (soft at 4x). The real HQ approach needs a render of the avenue-to-helix camera, and the city and HQ plate cameras must match for the dissolve to read.',
          '7. **End screens** use v2 variant A as the stand-in (the designer picked image slot B).', '']
    return '\n'.join(o)


os.makedirs(OUT, exist_ok=True)
for t in T:
    thumb_strip(t).save(OUT + t['file'], quality=90)
sheet().save(OUT + 'sheet.jpg', quality=88)
open(OUT + 'STORYBOARD.md', 'w', encoding='utf-8').write(md())
print('ok')
