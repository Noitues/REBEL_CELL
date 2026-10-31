"""Transitions storyboard v2 (ART CALL 49: the designer's 12). Writes only to transitions/v2/.
Run: python build2.py   (existing frames plus labelled mocks; no Godot)."""
import os, textwrap, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
R = 'D:/rc_art/art-pass/docs/concepts/'
OUT = R + 'transitions/v2/'
W, H = 1920, 1080
LIME = (150, 255, 70)
PINK = (255, 60, 180)
AMB = (255, 170, 60)
rnd = random.Random(49)


def F(sz, b=False):
    try:
        return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if b else 'C:/Windows/Fonts/arial.ttf', sz)
    except Exception:
        return ImageFont.load_default()


def MF(sz):
    try:
        return ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', sz)
    except Exception:
        return F(sz, True)


def L(rel, half=False):
    p = rel if ':' in rel else R + rel
    im = Image.open(p).convert('RGB')
    if half:
        im = im.crop((im.width // 2, 0, im.width, im.height))
    return im.resize((W, H), Image.LANCZOS)


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


def iris(a, b, r, cx=.5, cy=.5, col=LIME):
    m = Image.new('L', (W, H), 0)
    R_ = r * W
    box = (cx * W - R_, cy * H - R_, cx * W + R_, cy * H + R_)
    ImageDraw.Draw(m).ellipse(box, fill=255)
    out = Image.composite(b, a, m)
    ImageDraw.Draw(out).ellipse(box, outline=col, width=6)
    return out


def scan(im, a=.2):
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


def glow_line(im, pts, col=LIME, w=8):
    g = Image.new('RGB', (W, H), (0, 0, 0))
    d = ImageDraw.Draw(g)
    d.line([(x * W, y * H) for x, y in pts], fill=col, width=w * 3, joint='curve')
    g = g.filter(ImageFilter.GaussianBlur(14))
    out = Image.fromarray(__import__('numpy').clip(__import__('numpy').asarray(im).astype(int) + __import__('numpy').asarray(g).astype(int) * 0.8, 0, 255).astype('uint8'))
    ImageDraw.Draw(out).line([(x * W, y * H) for x, y in pts], fill=col, width=w, joint='curve')
    return out


def marker(im, cx, cy, kind):
    """Raid node: amber contested, lime held (check), pink lost (X)."""
    d = ImageDraw.Draw(im)
    x, y = cx * W, cy * H
    col = {'before': AMB, 'win': LIME, 'lose': PINK}[kind]
    for r, a in ((70, 2), (50, 4)):
        d.ellipse((x - r, y - r, x + r, y + r), outline=col, width=a)
    d.ellipse((x - 30, y - 30, x + 30, y + 30), fill=(10, 12, 16), outline=col, width=7)
    if kind == 'win':
        d.line((x - 15, y, x - 4, y + 13, x + 16, y - 13), fill=col, width=8)
    elif kind == 'lose':
        d.line((x - 15, y - 15, x + 15, y + 15), fill=col, width=8)
        d.line((x - 15, y + 15, x + 15, y - 15), fill=col, width=8)
    else:
        d.polygon([(x, y - 16), (x + 16, y + 12), (x - 16, y + 12)], fill=col)
    return im


def bits_to(im, src, dst, n=260, col=LIME, spread=60, size=22, seed=0):
    """Streams of binary digits from src to dst (normalised coords)."""
    r = random.Random(seed)
    out = im.copy()
    d = ImageDraw.Draw(out)
    f = MF(size)
    for i in range(n):
        t = r.random()
        sx, sy = src[0] * W, src[1] * H
        dx, dy = dst[0] * W, dst[1] * H
        mx, my = (sx + dx) / 2, (sy + dy) / 2 - 140 * (1 if i % 2 else -1) * r.random()
        x = (1 - t) ** 2 * sx + 2 * (1 - t) * t * mx + t * t * dx + r.gauss(0, spread) * math.sin(t * math.pi)
        y = (1 - t) ** 2 * sy + 2 * (1 - t) * t * my + t * t * dy + r.gauss(0, spread) * math.sin(t * math.pi)
        c = col if r.random() < .75 else PINK
        d.text((x, y), r.choice('01'), font=f, fill=c)
    return out


def bits_ring(im, c, rad, n=420, col=LIME, size=22, seed=1, rings=3):
    r = random.Random(seed)
    out = im.copy()
    d = ImageDraw.Draw(out)
    f = MF(size)
    for i in range(n):
        a = r.random() * math.tau
        rr = rad * (1 + .16 * r.randrange(rings)) + r.gauss(0, 6)
        d.text((c[0] * W + math.cos(a) * rr, c[1] * H + math.sin(a) * rr * .98), r.choice('01'), font=f, fill=col if r.random() < .7 else PINK)
    return out


def bits_dissolve(im, k, seed=3):
    """Board turns to bits: k in 0..1 share of the picture replaced by digits."""
    r = random.Random(seed)
    base = dark(im, 1 - .55 * k)
    d = ImageDraw.Draw(base)
    f = MF(20)
    for gy in range(0, H, 24):
        for gx in range(0, W, 16):
            if r.random() < k * .5:
                d.text((gx, gy), r.choice('01'), font=f, fill=LIME if r.random() < .75 else PINK)
    return base


def terminal_panel(im, box, title, lines, col=LIME):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(6, 14, 20), outline=col, width=5)
    d.rectangle((x0, y0, x1, y0 + 44), fill=(10, 36, 28))
    d.text((x0 + 16, y0 + 9), title, font=MF(22), fill=col)
    y = y0 + 70
    for t, c, s in lines:
        d.text((x0 + 28, y), t, font=MF(s), fill=c or col)
        y += int(s * 1.55)
    return im


L_NR = 'netrun_cel/godot_zoom/stage_%d_base.png'
MP = 'cohesion/map_pages_r42/'
TR = 'tide_raid/G1_parity/final_proposed/'
s1, s2, s3, s4, s5 = [L(L_NR % i) for i in range(1, 6)]
route = L(MP + 'route_page.png')
hq = L(MP + 'hq_idle.png')
hqs = L(MP + 'hq_node_selected.png')
rsetup = L(MP + 'raid_setup.png')
bare = L('combat_backdrop/v2/room_srv_bare.png')
room = L('combat_backdrop/v2/room_srv.png')
e10 = L('D:/rc_tmp/combat_critic/plates/waves_e10/p1_decide.png')
ev = L('solace_vertical/nodes/godot/frames/now_event.png')
frame4 = L('netrun_cel/frame4_solace_hq.png')
winB = L('solace_endscreens/v2/win_B.png')
loseB = L('solace_endscreens/v2/lose_B.png')
rb = {n: L(TR + n + '_side_by_side.png', half=True) for n in ['01_plan', '03_reveal', '04_impact', '06_aftermath', '07_city_lost']}
city = rb['01_plan']          # raid view: the real city plate (no HUD chrome in the plate)
RN = (.60, .40)               # raid node position on the raid view (mock marker)
NET = (.34, .58)              # a netrun entry on the raid view (mock marker)
FAIL_STAMP = None

# street with rooms (mock): stage_5 + lime route ribbon + node room tags
def street(sel=False):
    im = glow_line(s5, [(.02, .93), (.3, .86), (.5, .83), (.72, .86), (.98, .92)])
    d = ImageDraw.Draw(im)
    for i, (x, y) in enumerate([(.27, .5), (.52, .46), (.76, .5)]):
        d.rectangle((x * W - 70, y * H - 90, x * W + 70, y * H + 90), outline=LIME, width=5)
        d.rectangle((x * W - 70, y * H - 90, x * W + 70, y * H - 54), fill=(10, 40, 20))
        d.text((x * W - 56, y * H - 86), ['FIGHT', 'EVENT', 'FIGHT'][i], font=MF(24), fill=LIME)
    if sel:
        x, y = .52 * W, .46 * H
        d.rectangle((x - 82, y - 102, x + 82, y + 102), outline=(255, 255, 255), width=8)
    return im


def event_room():
    r = dark(bare, .45)
    card = ev.crop((int(.01 * W), int(.1 * H), int(.8 * W), int(.62 * H))).resize((int(W * .62), int(H * .36)), Image.LANCZOS)
    r.paste(card, (int(W * .19), int(H * .3)))
    return r


def fail_screen():
    im = dark(desat(route, .35), .35)
    d = ImageDraw.Draw(im)
    r = random.Random(5)
    for _ in range(14):  # glitch slices
        y = r.randrange(0, H - 40)
        h_ = r.randrange(8, 40)
        dx = r.randrange(-60, 60)
        im.paste(im.crop((0, y, W, y + h_)), (dx, y))
    im = Image.blend(im, Image.new('RGB', (W, H), (90, 10, 60)), .22)
    im = scan(im, .25)
    terminal_panel(im, (300, 250, 1620, 800), '> TERMINAL // SOLACE BIOSYSTEMS // TRACE COMPLETE', [
        ('CELL-9 SIGNAL LOST', PINK, 64),
        ('', None, 20),
        ('> netrun terminated at node 4 of 7', None, 28),
        ('> operative flatlined; home server holds', None, 28),
        ('> rewards forfeited, heat +2', AMB, 28),
        ('', None, 20),
        ('[ BACK TO CITY ]        [ VIEW TRACE LOG ]', LIME, 30)], col=PINK)
    d = ImageDraw.Draw(im)
    d.text((1180, 640), 'NETRUN LOST', font=F(72, True), fill=(255, 60, 100))
    return im


T = []


def add(**k):
    T.append(k)


# Each key: (label, image, 'R' real frame | 'M' mocked)
add(id='t01', file='t01_city_to_raid_view.jpg', title='T1  City Grid to raid view', dur='1.2 s', ease='smootherstep on log(zoom); no overshoot',
    keys=[('K1  0.00 s  City Grid, full plan, helix in frame', s1, 'R'),
          ('K2  0.40 s  push toward the raid focus, 1.25x', zblur(zc(s1, .55, .5, 1.25), .04), 'M'),
          ('K3  0.80 s  dissolve to the closer iso plate, 1.5x', blend(zc(s1, .55, .5, 1.5), city, .6), 'M'),
          ('K4  1.20 s  raid view, same city, raid HUD in', city, 'R')],
    cam='Same iso camera throughout (yaw 135, pitch 40); only the ortho width tightens from the City Grid plan to the raid-view plate camera (plate zoom 1.5 about px 722,500). No perspective, no cut: it is the same city getting closer.',
    ui='0.00-0.20 s: City Grid chrome (title, filters) fades. 0.20-0.90 s: none. 0.90-1.20 s: raid-view chrome (resource strip, raid forecast, VIEW LOADOUT, netrun and raid nodes) fades up with a 60 ms stagger; input at 1.20 s. The plate carries no chrome, so the chrome is not drawn.',
    rm='0.25 s cross-fade from City Grid to raid view; chrome appears with it.',
    feel='Leaning in from the whole city to the part of it you are fighting for.')
add(id='t02', file='t02_raid_to_select_jackin.jpg', title='T2  Raid view to select a netrun and jack in', dur='0.6 s (select, 0.2 s; jack-in press, 0.4 s)', ease='ease-out cubic for the card; the press is a 90 ms flash then ease-in dim',
    keys=[('K1  0.00 s  raid view, netrun entries lit', marker(city.copy(), *NET, 'before'), 'M'),
          ('K2  0.20 s  netrun selected, dossier card slides in', None, 'M'),
          ('K3  0.45 s  JACK IN pressed: flash, chrome dims', None, 'M'),
          ('K4  0.60 s  chrome gone, camera starts (hands to T3)', None, 'M')],
    cam='No camera move on selection (the raid view stays). On JACK IN the camera hands straight to T3, starting from this frame, so the zoom begins on the selected netrun.',
    ui='0.00-0.20 s: the selected node gets a lime ring pulse and its dossier card (file card, Site, threat, JACK IN) slides in from the right 40 px. 0.45 s: JACK IN flashes white for 90 ms. 0.45-0.60 s: all raid-view chrome fades out; the lime ring stays and is the zoom target for T3.',
    rm='Dossier appears instantly; JACK IN cross-fades 0.25 s into T3 start frame.',
    feel='Choosing a door and committing to it.')
add(id='t03', file='t03_jackin_zoom.jpg', title='T3  Jack-in zoom to the netrun street along the node route', dur='1.4 s', ease='smootherstep on log(ppb); the old wheel-circle zoom is removed',
    keys=[('K1  0.00 s  raid view, entry ring', city, 'R'),
          ('K2  0.30 s  push into the district, route ribbon begins', glow_line(zblur(s2, .05), [(.2, .9), (.4, .6), (.6, .5)]), 'M'),
          ('K3  0.65 s  iso at ppb ~15, ribbon follows the node route', glow_line(zblur(s3, .05), [(.1, .95), (.35, .7), (.6, .55), (.8, .4)]), 'M'),
          ('K4  0.95 s  dolly-zoom to perspective, pitch 40 to 12', glow_line(zblur(s4, .05), [(.05, .98), (.4, .85), (.7, .78)]), 'M'),
          ('K5  1.20 s  near street, horizon dropping', glow_line(blend(s4, s5, .6), [(.02, .95), (.4, .85), (.8, .84)]), 'M'),
          ('K6  1.40 s  the netrun street: node rooms along the route', street(), 'M')],
    cam='ZOOM_RULES 5.5 path: iso ortho push to the district (0.65 s), dolly-zoom fov 8 to 40 with pitch 40 to 12 (0.65-0.95 s), pitch to 0, lens shift and eye to 4 m (last 0.45 s). The camera rides the node route: the focus point slides along the lime ribbon, which is the connected path of rooms, ending framed on the first room on the street at a horizontal third. Frames K2-K5 are the real zoom stages with a mocked ribbon; K6 is the real street with mocked ribbon and room tags.',
    ui='Chrome is already gone (T2). 0.30 s: the route ribbon draws from the entry ring along the node route, tracking the camera. 1.10-1.40 s: room tags (type, state) pop onto the street rooms in 60 ms steps; the netrun HUD (resource strip, route legend, menu) fades up at 1.25 s; input at 1.40 s.',
    rm='0.25 s cross-fade from raid view to the netrun street with room tags and HUD already shown.',
    feel='Dropping through the city and landing in a single street that is yours to run.')
add(id='t04', file='t04_street_to_room.jpg', title='T4  Select a room on the netrun street and zoom into it (combat, or event/other Site)', dur='0.8 s', ease='ease-in cubic for the push, ease-out cubic for the room settle',
    keys=[('K1  0.00 s  netrun street, three rooms on the route', street(), 'M'),
          ('K2  0.15 s  room selected, white frame, tooltip', street(True), 'M'),
          ('K3  0.35 s  push into the room facade 3x', zblur(zc(street(True), .52, .46, 3.0), .05), 'M'),
          ('K4  0.55 s  iris opens: COMBAT room, the v2 cutaway', iris(zblur(zc(street(True), .52, .46, 3.4), .05), scan(bare), .22), 'M'),
          ('K5  0.80 s  COMBAT: iso cutaway settled (real v2 backdrop)', bare, 'R'),
          ('K5b 0.80 s  EVENT: Terminal interior (mock from the event card)', event_room(), 'M')],
    cam='The camera pushes at the chosen room window (3x), then a lime iris opens on the interior: the combat cutaway (combat_backdrop/v2) or an event/Site interior. Interiors are composed at the city iso angle so no camera swap is needed after the iris.',
    ui='0.00-0.15 s: room selected (white frame, tooltip with type and reward). 0.15-0.35 s: street HUD dims to 40 % and drifts out. 0.35-0.55 s: iris only. 0.55-0.80 s: the interior is quiet, then T5 (combat) starts, or the event card (title, choices) slides up from the bottom for events.',
    rm='0.25 s cross-fade from the street to the interior; no iris, no push.',
    feel='Choosing a door in the street and stepping inside it.')
add(id='t05', file='t05_room_to_combat.jpg', title='T5  Room to combat: the wheel flies in, enemy rings fly from the room as binary bits', dur='1.2 s', ease='wheel: ease-out cubic with a 4 % overshoot; bits: ease-in-out along curved paths; rings lock with a 90 ms snap',
    keys=[('K1  0.00 s  iso room, nothing on it (real)', bare, 'R'),
          ('K2  0.25 s  the wheel flies in from the camera, 1.6x to 1.0x', blend(bare, room, .6), 'M'),
          ('K3  0.55 s  streams of bits leave the room, curve toward the wheel', bits_to(blend(bare, room, .9), (.76, .62), (.27, .52), seed=1), 'M'),
          ('K4  0.85 s  bits surround the wheel in three rings', bits_ring(room, (.27, .52), 430), 'M'),
          ('K5  1.05 s  bits resolve into the enemy rings, HUD and hand slide in', blend(bits_ring(room, (.27, .52), 430, n=160), e10, .6), 'M'),
          ('K6  1.20 s  combat begins: E10 board (real)', e10, 'R')],
    cam='Fixed iso camera on the room; the camera does not move. The only motion is the wheel (scale 1.6 to 1.0, slight spin settle) and the bit streams, which start in the room (the building in the right half, where the enemy "lives") and curve to three ring radii around the wheel.',
    ui='0.00-0.25 s: nothing. 0.25-0.55 s: wheel in. 0.55-1.05 s: bits. 1.05-1.20 s: turn banner and wave ledger slide in from the top right, cards deal from the bottom (60 ms stagger), SEND IT last. No input until 1.20 s. The room dims to 55 % behind the board at the end (the E10 backdrop is currently the old crane plate, see questions).',
    rm='0.25 s cross-fade from the room to the board; the rings are simply there.',
    feel='The enemy pours out of the building as code and wraps around you; the fight is on.')
add(id='t06', file='t06_combat_to_netrun_or_fail.jpg', title='T6  Combat ends, the board dissolves to bits, back to the netrun, or the run fails', dur='0.8 s back to the netrun; 0.6 s plus hold for the failure screen', ease='bits: ease-in; street: ease-out cubic; failure: hard glitch cut, then a 0.3 s settle',
    keys=[('K1  0.00 s  combat won (real E10)', e10, 'R'),
          ('K2  0.20 s  the board starts to dissolve into bits', bits_dissolve(e10, .45), 'M'),
          ('K3  0.40 s  mostly bits over the empty room', bits_dissolve(bare, .75), 'M'),
          ('K4  0.80 s  back on the netrun street, room cleared', glow_line(street(), [(.02, .93), (.5, .83), (.98, .92)]), 'M'),
          ('K5  0.20 s  FAIL branch: signal glitch, board tears', None, 'M'),
          ('K6  0.60 s  FAIL: netrun-failure screen (concept)', fail_screen(), 'M')],
    cam='Combat: fixed iso camera; the board dissolves in place. Then the iris of T4 runs in reverse and the camera pulls back 3x to the street framing it was left in, which is the same framing T4 started from. Failure: no pull-out; the picture glitches (slice offsets) and cuts to the terminal screen over the dimmed route.',
    ui='0.00-0.20 s: SEND IT, hand and turn banner fade; the wheel and rings break into bits that scatter and drain toward the room. 0.40-0.80 s: pull-out, street HUD fades up, the cleared room shows a check. Failure: HUD out in 0.1 s, the terminal panel (title bar, CELL-9 SIGNAL LOST, three lines, two buttons) opens at 0.30 s, input at 0.60 s.',
    rm='0.25 s cross-fade combat to street; failure is a 0.25 s cross-fade to the terminal screen.',
    feel='Win: the fight evaporates like a closed process and you are on the street. Fail: a cold cut to a log.')
add(id='t07', file='t07_netrun_to_raid_view.jpg', title='T7  Netrun, win or lose, back up to the raid view (the raid node changes)', dur='1.2 s', ease='the T3 path in reverse: smootherstep; the node change is a 0.3 s pop after landing',
    keys=[('K1  0.00 s  netrun ends (street, or the end of the route)', street(), 'M'),
          ('K2  0.30 s  pull back, chrome out, ribbon retracts', glow_line(zblur(s4, .05), [(.05, .98), (.4, .85), (.7, .78)]), 'M'),
          ('K3  0.80 s  district, ppb 15', zblur(s2, .05), 'R'),
          ('K4  1.00 s  raid view, node still contested (before)', marker(city.copy(), *RN, 'before'), 'M'),
          ('K5  1.20 s  WIN: node turns lime with a check', marker(city.copy(), *RN, 'win'), 'M'),
          ('K6  1.20 s  LOSE: node turns pink with an X', marker(city.copy(), *RN, 'lose'), 'M')],
    cam='The T3 path in reverse, ending on the raid-view camera with the netrun entry the player came from centred in frame. Win and lose use the same path; only the final node pop differs.',
    ui='0.00-0.20 s: netrun HUD out. 0.20-0.90 s: no chrome. 0.90-1.20 s: raid-view chrome fades up; at 1.00 s the node pops: win = lime ring, check, short lime ripple on the city; lose = pink ring, X and a pink ripple that creeps along the nearest lane (Bloom). Input at 1.20 s.',
    rm='0.25 s cross-fade street to raid view, node already in its new state.',
    feel='Back in the big picture with proof that what you did down there mattered.')
add(id='t08', file='t08_raid_lose_to_dossier.jpg', title='T8  Raid view lose: the dossier folder ends the campaign (image slot B)', dur='1.6 s', ease='city dims: ease-in-out; folder: ease-out cubic slide, 0.3 s settle',
    keys=[('K1  0.00 s  the city is lost (real raid beat)', rb['07_city_lost'], 'R'),
          ('K2  0.50 s  city dims and drains to pink, grease marks start', desat(dark(rb['07_city_lost'], .5), .5), 'M'),
          ('K3  0.90 s  the folder drops in, tilt -2 deg', shrink_on(dark(rb['07_city_lost'], .35), loseB, .78, .5, .5, rot=-2), 'M'),
          ('K4  1.60 s  dossier, slot B: survey map, every node crossed (real v2)', loseB, 'R')],
    cam='No camera move. The camera locks on the lost city at 0.0 s; the folder is a UI card dropping from above onto the dimmed city.',
    ui='0.00-0.40 s: raid chrome out. 0.40-0.90 s: city to 35 %; the folder slides down 140 px, tilting -4 to -2 degrees. 0.90-1.60 s: FILED stamp thuds at 1.2 s, the survey map marks draw in (every node crossed out, the Bloom spreading), memo fields type in, MAIN MENU and NEW CAMPAIGN arm at 1.60 s. In the game the marks come from the player network on the real city plan.',
    rm='0.25 s cross-fade to the finished folder; stamp and marks pre-drawn.',
    feel='The corporation closing the file on you: quiet and final.')
add(id='t09', file='t09_raid_to_plan_and_back.jpg', title='T9  Raid view to planning the raid, and back', dur='0.7 s each way', ease='smootherstep in; ease-out cubic out',
    keys=[('K1  0.00 s  raid view (real)', city, 'R'),
          ('K2  0.25 s  chrome out, push 1.15x, planning cards slide in', blend(zc(city, .5, .5, 1.15), rsetup, .45), 'M'),
          ('K3  0.70 s  RAID SETUP page (real r42)', rsetup, 'R'),
          ('K4  0.40 s  planning: lane tray and threat intel in use (crop 1.6x)', zc(rsetup, .72, .72, 1.6), 'M'),
          ('K5  0.35 s  back: cards slide out, pull to the raid view', blend(city, rsetup, .35), 'M'),
          ('K6  0.70 s  raid view again (real)', city, 'R')],
    cam='A 15 % push on the same iso camera into the plan composition (the r42 setup page is the same city on the same camera, with the lanes drawn on it); back is the reverse. No cut, no perspective change.',
    ui='In: 0.00-0.20 s raid chrome fades; 0.20-0.70 s STRAIN AUDIT card from the left, THREAT INTEL from the right, lane tray rising from the bottom (80 ms stagger). Back: the cards slide out in 0.25 s, then raid chrome returns with any chosen lanes drawn on the city.',
    rm='0.25 s cross-fade each way.',
    feel='A calm move into the planning table and back out to the city, with your plan on it.')
add(id='t10', file='t10_raid_start_result_back.jpg', title='T10  Raid view to starting a raid, the result, and back to the raid view', dur='0.9 s in, raid plays, 1.0 s to result, 0.7 s back', ease='ease-out cubic for the raid; result: ease-in-out with a 0.3 s hold; back: smoothstep',
    keys=[('K1  0.00 s  raid view, raid warning (real)', city, 'R'),
          ('K2  0.90 s  raid begins, FX enter from the edge (real tide beat)', rb['03_reveal'], 'R'),
          ('K3  1.40 s  impact at the defended node (real)', rb['04_impact'], 'R'),
          ('K4  1.90 s  RESULT held: aftermath (real)', rb['06_aftermath'], 'R'),
          ('K5  1.90 s  RESULT lost: city lost (real, branch)', rb['07_city_lost'], 'R'),
          ('K6  2.60 s  back on the raid view, nodes updated', marker(city.copy(), *RN, 'win'), 'M')],
    cam='Raid camera is the plate camera (zoom 1.5 about px 722,500) throughout. 0.9 s, the raid starts with a settle only; the result is a slow 1.0 to 1.1x push on the impact point over 1.0 s; back is a 0.7 s pull to the raid-view framing.',
    ui='0.00-0.25 s: raid chrome out. 0.25-0.90 s: raid HUD (wave, defense) in. 1.90 s: HUD out; result banner (HELD or CITY LOST) and tally in; the lost branch desaturates the city to 60 % over 0.5 s. Back: banner dismisses, raid chrome returns, nodes in their result state.',
    rm='Each step is a 0.25 s cross-fade; the raid FX plays at normal speed in the raid step.',
    feel='A threat arrives, hits, and the aftermath settles; then the city is yours again, changed.')
add(id='t11', file='t11_raid_to_hq_netrun.jpg', title='T11  Raid view to the HQ netrun: a special fly-in to the hand-authored HQ', dur='1.8 s', ease='smootherstep on log(zoom); the final approach decelerates over the last 0.5 s',
    keys=[('K1  0.00 s  raid view, the HQ node selected', marker(city.copy(), .78, .30, 'before'), 'M'),
          ('K2  0.35 s  push toward the helix, 1.8x', zblur(zc(s1, .79, .30, 1.8), .05), 'M'),
          ('K3  0.80 s  descend to the avenue pointing at the helix', zblur(zc(s1, .80, .28, 3.5), .06), 'M'),
          ('K4  1.20 s  dissolve to the hand-authored HQ street (frame 4)', blend(zc(s1, .80, .28, 3.5), frame4, .6), 'M'),
          ('K5  1.55 s  the HQ avenue, helix straight ahead (frame 4, real concept)', frame4, 'R'),
          ('K6  1.80 s  HQ netrun page, JACK IN (real r42)', hqs, 'R')],
    cam='Not the T3 path: the HQ netrun is bespoke, so only the city behind it is procedural. The camera stays iso toward the helix (ortho 394 to about 95), then a 0.4 s dissolve to the authored set where the camera is the perspective street of frame 4 (eye low, the avenue pointing at the helix; ZOOM_RULES 2.8: landmarks are authored meshes with their own materials, and a Server Rack entrance can host layer 7). The city and authored cameras must be matched at the dissolve.',
    ui='0.00-0.25 s: raid chrome out. 0.25-1.35 s: only an avenue ribbon draws toward the helix. 1.45-1.80 s: HQ chrome (file card, node dossier, crew tray, JACK IN) fades up with a 60 ms stagger; input at 1.80 s.',
    rm='0.25 s cross-fade from the raid view to the HQ page.',
    feel='Approaching the corporation that built the city: slowly, and a little ominously.')
add(id='t12', file='t12_hq_to_win_dossier.jpg', title='T12  Custom HQ netrun to campaign win, then the dossier folder (win, image slot B)', dur='1.4 s plus 0.9 s folder', ease='helix recolour: ease-in-out; flash: 90 ms; folder: ease-out cubic slide, 0.3 s settle',
    keys=[('K1  0.00 s  HQ netrun, last node resolved (real)', hqs, 'R'),
          ('K2  0.40 s  the helix is hacked: lime to cyan sweeps up the strand', None, 'M'),
          ('K3  0.80 s  white flash, chrome out', None, 'M'),
          ('K4  1.40 s  the folder drops over the dimmed HQ avenue', shrink_on(dark(frame4, .4), winB, .78, .5, .5, rot=-2), 'M'),
          ('K5  2.30 s  dossier, slot B: red grease marks on the network (real v2)', winB, 'R')],
    cam='No camera move beyond a 4 % push toward the helix while it recolours; the folder is a UI card.',
    ui='0.00-0.30 s: HQ chrome out. 0.40-0.90 s: the lime-to-cyan sweep (the ruling colour story of the win). 1.40-2.30 s: the folder slides in, the ROUTED stamp thuds at 1.9 s, the survey map marks draw in red grease pencil, MAIN MENU and NEW CAMPAIGN arm at 2.30 s.',
    rm='0.25 s cross-fade from the HQ page to the finished folder.',
    feel='A quiet win: the helix changes colour, and the corporation files you as a case.')


def cyan(im, k):
    r, g, b = im.split()
    sw = Image.merge('RGB', (r, g, b.point(lambda v: min(255, int(v * 1.0))).copy()))
    mix = Image.merge('RGB', (r.point(lambda v: int(v * .6)), g, Image.blend(b, g, .9)))
    return Image.blend(sw, mix, k)


# fill in the keys that need composition
for t in T:
    if t['id'] == 't02':
        card = hqs.crop((1180, 440, 1920, 760))
        btn = hqs.crop((1500, 900, 1920, 1080))
        base = marker(city.copy(), *NET, 'before')
        k2 = base.copy()
        k2.paste(card, (1160, 380))
        k3 = k2.copy()
        k3.paste(btn, (1500, 900))
        k3 = Image.blend(k3, Image.new('RGB', (W, H), (255, 255, 255)), .35)
        t['keys'][1] = (t['keys'][1][0], k2, 'M')
        t['keys'][2] = (t['keys'][2][0], k3, 'M')
        t['keys'][3] = (t['keys'][3][0], dark(marker(city.copy(), *NET, 'before'), .75), 'M')
    if t['id'] == 't06':
        tear = bits_dissolve(e10, .0)
        r = random.Random(8)
        for _ in range(20):
            y = r.randrange(0, H - 40)
            h_ = r.randrange(10, 50)
            tear.paste(tear.crop((0, y, W, y + h_)), (r.randrange(-90, 90), y))
        t['keys'][4] = (t['keys'][4][0], Image.blend(tear, Image.new('RGB', (W, H), (80, 0, 50)), .25), 'M')
    if t['id'] == 't12':
        t['keys'][1] = (t['keys'][1][0], cyan(zc(hqs, .86, .3, 1.04), .7), 'M')
        t['keys'][2] = (t['keys'][2][0], Image.blend(cyan(hqs, 1.0), Image.new('RGB', (W, H), (255, 255, 255)), .7), 'M')


def strip(tr):
    n = len(tr['keys'])
    cols = 3
    rows = math.ceil(n / cols)
    tw, th = 616, 347
    g = 24
    lab = 36
    mx = 36
    blocks = [('DURATION', tr['dur']), ('EASING', tr['ease']), ('CAMERA PATH', tr['cam']), ('UI HAND-OVER', tr['ui']),
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
    d.text((mx, 18), tr['title'][:105], font=F(32, True), fill=LIME)
    for i, (lb, im, kind) in enumerate(tr['keys']):
        r, c = divmod(i, cols)
        x = mx + c * (tw + g)
        y = top + r * (th + lab + g)
        S.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        col = LIME if kind == 'R' else AMB
        d.rectangle((x - 2, y - 2, x + tw + 1, y + th + 1), outline=col, width=3)
        d.rectangle((x, y, x + (96 if kind == 'R' else 82), y + 26), fill=col)
        d.text((x + 6, y + 3), 'REAL' if kind == 'R' else 'MOCK', font=F(18, True), fill=(10, 10, 10))
        d.text((x, y + th + 6), lb[:78], font=F(17, True), fill=(235, 235, 240))
        if c < cols - 1 and i < n - 1:
            d.polygon([(x + tw + 4, y + th // 2 - 14), (x + tw + 20, y + th // 2), (x + tw + 4, y + th // 2 + 14)], fill=LIME)
    y = top + rows * (th + lab + g) + 8
    for h, wr in lines:
        d.text((mx, y), h, font=fb, fill=AMB)
        y += 25
        for w in wr:
            d.text((mx, y), w, font=f, fill=(215, 215, 222))
            y += 25
        y += 8
    return S


def flow():
    S = Image.new('RGB', (2200, 1270), (14, 15, 20))
    d = ImageDraw.Draw(S)
    d.text((40, 20), 'Transition flow: how the 12 connect (numbers are T1 to T12)', font=F(40, True), fill=LIME)
    B = {}

    def box(k, x, y, label, col=(60, 70, 90), w=300, h=84):
        B[k] = (x, y, w, h)
        d.rounded_rectangle((x, y, x + w, y + h), 12, fill=(26, 30, 40), outline=col, width=4)
        for j, t in enumerate(label.split('\n')):
            d.text((x + 14, y + 12 + j * 28), t, font=F(24, True), fill=(235, 235, 240))

    box('grid', 40, 520, 'CITY GRID')
    box('raid', 480, 520, 'RAID VIEW\n(main campaign city)', LIME, h=100)
    box('plan', 480, 140, 'RAID SETUP\n(planning)')
    box('run', 480, 900, 'RAID RUN\nthen RESULT')
    box('lost', 480, 1060, 'DOSSIER (LOSE)\nslot B, campaign over', PINK, w=420, h=84)
    box('jack', 960, 520, 'NETRUN STREET\n(jack-in lands here)', LIME, h=100)
    box('room', 1400, 330, 'ROOM\ncombat cutaway / event')
    box('combat', 1800, 330, 'COMBAT\nE10 board', AMB, w=330)
    box('fail', 1400, 720, 'NETRUN FAILURE\nterminal screen', PINK)
    box('hq', 960, 140, 'HQ NETRUN\n(hand-authored)', AMB)
    box('win', 1400, 60, 'DOSSIER (WIN)\nslot B, campaign won', LIME, w=420)

    def arrow(a, b, n, col=LIME, off=(0, 0), side=('r', 'l')):
        def pt(k, s):
            x, y, w, h = B[k]
            return {'l': (x, y + h / 2), 'r': (x + w, y + h / 2), 't': (x + w / 2, y), 'b': (x + w / 2, y + h)}[s]
        p, q = pt(a, side[0]), pt(b, side[1])
        p = (p[0] + off[0], p[1] + off[1])
        q = (q[0] + off[0], q[1] + off[1])
        d.line((p, q), fill=col, width=5)
        ang = math.atan2(q[1] - p[1], q[0] - p[0])
        d.polygon([q, (q[0] - 20 * math.cos(ang - .4), q[1] - 20 * math.sin(ang - .4)), (q[0] - 20 * math.cos(ang + .4), q[1] - 20 * math.sin(ang + .4))], fill=col)
        mx_, my_ = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        d.ellipse((mx_ - 20, my_ - 20, mx_ + 20, my_ + 20), fill=col)
        d.text((mx_ - (13 if n > 9 else 6), my_ - 13), str(n), font=F(22, True), fill=(10, 10, 10))

    arrow('grid', 'raid', 1)
    arrow('raid', 'jack', 2, off=(0, -20))
    arrow('raid', 'jack', 3, off=(0, 20))
    arrow('jack', 'room', 4, side=('r', 'l'))
    arrow('room', 'combat', 5)
    arrow('combat', 'jack', 6, AMB, side=('b', 'r'))
    arrow('jack', 'fail', 6, PINK, side=('b', 'l'))
    arrow('fail', 'raid', 7, PINK, side=('l', 'b'))
    arrow('jack', 'raid', 7, LIME, off=(0, 60), side=('l', 'r'))
    arrow('raid', 'lost', 8, PINK, side=('b', 't'))
    arrow('raid', 'plan', 9, side=('t', 'b'))
    arrow('raid', 'run', 10, side=('b', 't'), off=(60, 0))
    arrow('raid', 'hq', 11, AMB, side=('t', 'l'))
    arrow('hq', 'win', 12, LIME)
    d.text((40, 1200), 'Arrow colours: lime = normal flow, amber = combat or HQ special, pink = loss. 2 and 3 share the Raid view to Netrun street leg (select, then the zoom); 6 and 7 branch on result; 9, 10 and 7 return to the raid view.', font=F(22), fill=(215, 215, 222))
    return S


def sheet():
    tw, th = 270, 152
    g = 8
    lw = 300
    mx = 20
    cols = 6
    rowh = th + 24 + g
    S = Image.new('RGB', (mx * 2 + lw + cols * (tw + g), 64 + len(T) * rowh), (14, 15, 20))
    d = ImageDraw.Draw(S)
    d.text((mx, 14), 'REBEL_CELL transitions v2: the designer\'s 12 (green frame = real frame, amber = mocked)', font=F(26, True), fill=LIME)
    for r, t in enumerate(T):
        y = 64 + r * rowh
        for k, w in enumerate(textwrap.wrap(t['title'], 30)[:4]):
            d.text((mx, y + 4 + k * 20), w, font=F(16, True), fill=(235, 235, 240))
        d.text((mx, y + 100), textwrap.wrap(t['dur'], 32)[0], font=F(15), fill=LIME)
        for i, (lb, im, kind) in enumerate(t['keys'][:cols]):
            x = mx + lw + i * (tw + g)
            S.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
            d.rectangle((x, y, x + tw, y + th), outline=LIME if kind == 'R' else AMB, width=3)
            d.text((x, y + th + 3), lb[:44], font=F(12), fill=(200, 200, 208))
    return S


def md():
    o = ['# Transitions storyboard v2 (art-pass, 2026-10-30): the designer\'s 12 (ART CALL 49)\n',
         'Replaces nothing in v1 (the first storyboard, 962ebb45, is wrong and stays as a record). Built by `scripts/build2.py` from existing frames plus labelled mocks. No Godot work, no game design. Every key carries a badge: **REAL** (green frame) is an existing frame or an existing crop of one; **MOCK** (amber frame) is composed here (crops, blends, bit streams, marker overlays, a pasted card crop, the failure screen). Mocked frames show sequence and timing only.\n',
         '- `flow.jpg`: how the 12 connect. `sheet.jpg`: all strips on one page.\n',
         '## Master timing table\n', '| # | Transition | Duration | Easing | Reduced motion |', '|---|---|---|---|---|']
    for t in T:
        o.append('| %s | %s | %s | %s | 0.25 s cross-fade |' % (t['id'].upper(), t['title'][4:], t['dur'], t['ease']))
    o += ['', 'Consistency: the big zoom through the city (T3) is 1.4 s and T1 is a lighter 1.2 s; entering a room (T4) is 0.8 s and leaving it (T6) is 0.8 s; every UI card or folder slides in 0.3 to 0.5 s with a 60 to 80 ms stagger; no chrome is on screen while the camera moves; every reduced-motion variant is a 0.25 s cross-fade (under the 0.3 s cap).\n',
         '![flow](flow.jpg)\n']
    for t in T:
        o += ['## %s\n' % t['title'], '![%s](%s)\n' % (t['id'], t['file']),
              '- **Keys:** ' + '; '.join('%s [%s]' % (k[0].strip(), 'real' if k[2] == 'R' else 'mock') for k in t['keys']),
              '- **Duration:** ' + t['dur'], '- **Easing:** ' + t['ease'], '- **Camera path:** ' + t['cam'],
              '- **UI hand-over:** ' + t['ui'], '- **Reduced motion:** ' + t['rm'], '- **Feel:** ' + t['feel'], '']
    o += ['## What is missing (art to be made before these can be real frames)\n',
          '- **Event / shop / other Site interiors.** Only the combat server-room cutaway exists (combat_backdrop/v2). T4 K5b is a mock: the Terminal event card (solace_vertical/nodes, now_event) pasted over a dimmed cutaway. Each non-combat Site kind (Terminal, Mainframe/shop, Server Rack) needs its own interior kit room at the city iso angle.',
          '- **The netrun street with rooms.** No frame shows a street of connected node rooms; T3 K6 and T4 use the real street (stage 5) with mocked ribbon and room tags.',
          '- **Raid-view chrome and the raid node states** (contested, held, lost) are mocked markers; the plate has no HUD.',
          '- **Bits FX and the enemy-ring fly-out** (T5, T6) are drawn digits only; they need a real particle pass and a ring build-up.',
          '- **Netrun-failure screen** (T6 K6) is one concept frame in the Solace terminal look over the dimmed route page.',
          '- **HQ approach:** K2 to K4 are crops of the city frame; frame 4 is the v1 concept for the hand-authored HQ street, not a Godot render.',
          '- **The combat backdrop behind E10** is still the old crane plate; the cutaway has to replace it for T5 K6 to match K1.',
          '', '## Questions: assumptions I made about what the designer meant\n',
          '1. **City Grid vs raid view (T1).** I read the City Grid as the whole-city plan view and the raid view as the closer iso campaign view (the tide plate camera), so T1 is a zoom between the same iso camera. If they are two separate screens (the City Grid being a flat grid), T1 needs a different frame.',
          '2. **T2 and T3 are separate.** Select and jack-in (T2) is a UI beat with no camera move; the zoom to the street (T3) starts from the jack-in press. Should T2 end with the dossier card or go straight into the zoom?',
          '3. **T3 ends on the street, not the iso route page.** The route page (cohesion/map_pages_r42/route_page.png) is the iso route view; I treat the "netrun street" as the perspective street of ZOOM_RULES 5.5. Are these one screen or two?',
          '4. **Room selection (T4):** one click selects and zooms; the room type decides the interior. For events and shops the zoom ends on an interior with the card over it, not a flat panel on the street. Right?',
          '5. **T5 enemy origin.** "The enemy invading rings fly from the isometric room": I drew bits leaving the building/machines in the room, in three rings around the wheel. Do the rings stay three, or follow the encounter\'s ring count?',
          '6. **T6 failure:** I assumed "the run fails" means the player is flatlined at any node, and the failure screen goes to the raid view (T7 lose). Does a failed netrun cost anything the screen must show (heat, rewards lost)? The lines on the mock are placeholders.',
          '7. **T7 raid node:** I assumed one raid node per netrun entry, with three states (contested, held, lost). The marker design is mine (amber triangle, lime check, pink X).',
          '8. **T8 vs T10 lost.** Raid view lose (T8) is the campaign ending when the city is lost; a lost single raid (T10 lost branch) returns to the raid view and the campaign continues unless the city is lost. Right?',
          '9. **T12 win:** the helix recolour (lime to cyan) before the folder, with the slot B survey map in red grease pencil. Should the folder come over the HQ street or over the city?',
          '10. **Folder image slot:** B on both folders (win marks red, lose nodes crossed and Bloom spreading), as the designer picked. A is not used.', '']
    return '\n'.join(o)


os.makedirs(OUT, exist_ok=True)
for t in T:
    strip(t).save(OUT + t['file'], quality=90)
sheet().save(OUT + 'sheet.jpg', quality=88)
flow().save(OUT + 'flow.jpg', quality=90)
open(OUT + 'STORYBOARD.md', 'w', encoding='utf-8').write(md())
print('ok')
