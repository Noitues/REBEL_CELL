"""GLITCH VECTOR CRT - build every still: Blender renders, then the Pillow compositor.

python compose.py [--skip-render] [--keep-cache]
Renders go to ../_cache (deleted at the end unless --keep-cache). Stills -> ../stills/, sheet -> ../contact_sheet.jpg
Layer order everywhere: DIGITAL -> light spill -> CRT + heat glitch -> ANALOG (stickers, marker).
"""
import json, os, random, subprocess, sys, shutil, math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose_lib as cl
from compose_lib import PAL, font, W, H

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.abspath(os.path.join(HERE, ".."))
CACHE = os.path.join(DIR, "_cache")
STILLS = os.path.join(DIR, "stills")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
SKIP = "--skip-render" in sys.argv
os.makedirs(CACHE, exist_ok=True)
os.makedirs(STILLS, exist_ok=True)


def blender(script, *args):
    log = os.path.join(CACHE, os.path.basename(script) + "_" + (args[0] if args else "") .replace(os.sep, "_")[-30:] + ".log")
    cmd = [BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, script), "--"] + list(args)
    with open(log, "w") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, timeout=900)
    txt = open(log, errors="ignore").read()
    if "Traceback" in txt or r.returncode != 0:
        raise SystemExit("Blender failed: %s (see %s)" % (script, log))


def C(name):
    return os.path.join(CACHE, name)


def marker_render(name, jobs):
    p = C(name + "_jobs.json")
    json.dump(jobs, open(p, "w"), indent=1)
    if not SKIP:
        blender("marker.py", p, C(name + "_marker.png"))
    return Image.open(C(name + "_marker.png")).convert("RGBA")


def over(img, rgba):
    base = img.convert("RGBA")
    base.alpha_composite(rgba)
    return base.convert("RGB")


# ------------------------------------------------------------------ positions shared with marker jobs
EXEC_BOX = (1460, 905, 1895, 1030)
POSTER_C = (1735, 250)

# ------------------------------------------------------------------ Blender renders
if not SKIP:
    for mode in ("night", "heat", "nodes_off"):
        blender("city.py", mode, C("city_%s.png" % mode))
    blender("spinners.py", C("spin.png"), cl.FONTS)
    blender("modem_sign.py", C("sign.png"))


def top_bar(img, left, right_tags=()):
    cl.glass_panel(img, (0, 0, W - 1, 56), None, alpha=0.9)
    cl.text(img, (22, 16), left, font("mono", 22), PAL["text_mid"])
    return img


def tag_stickers(img, rng, tags, x=1220, y=30):
    """Top-bar tags are PAPER: little die-cut stickers slapped onto the glass."""
    for (label, val, col) in tags:
        w = 104
        st = cl.paper_texture((w, 46), rng, col).convert("RGBA")
        d = ImageDraw.Draw(st)
        d.text((8, 3), label, font=font("anton", 13), fill=PAL["ink"])
        d.text((8, 16), val, font=font("anton", 24), fill=PAL["ink"])
        st = cl.die_cut(st, 4)
        cl.place_sticker(img, st, (x, y + 6), rng.uniform(-4, 4), shadow=(4, 5))
        x += w + 12
    return img


def exec_button(img, label="EXECUTE", sub="[SPACE]", box=EXEC_BOX):
    """The washed-out digital system word the marker is scrawled over (feedback 9)."""
    cl.glass_panel(img, box, None, edge=(70, 110, 130), alpha=0.8)
    x0, y0, x1, y1 = box
    lay = Image.new("RGB", img.size, (0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text(((x0 + x1) / 2, (y0 + y1) / 2 - 8), label, font=font("mono", 50), fill=(70, 120, 130), anchor="mm")
    d.text(((x0 + x1) / 2, y1 - 16), sub, font=font("mono", 16), fill=(60, 90, 100), anchor="mm")
    lay = cl.rgb_split(lay, 2)
    return ImageChops.add(img, lay)


# ================================================================== 01 COMBAT
def still_combat():
    rng = random.Random(101)
    pos = json.load(open(C("spin.json")))
    city = Image.open(C("city_nodes_off.png")).convert("RGB")
    bg = cl.recede(city, desat=0.3, dim=0.46, blur=2.5)
    bg = cl.tilt_shift(bg, (0.3, 0.85), 8)
    # dark scrims under the wheels so the holograms own their space
    scrim = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(scrim)
    for k in ("op", "en"):
        cx, cy = pos[k]["center"]
        d.ellipse((cx - 330, cy - 320, cx + 330, cy + 360), fill=150)
    scrim = scrim.filter(ImageFilter.GaussianBlur(70))
    bg = Image.composite(Image.new("RGB", (W, H), (2, 4, 8)), bg, scrim)
    spin = Image.open(C("spin.png")).convert("RGB")
    img = cl.add(bg, spin)
    # damage number (digital): white-hot with harm pairing (down-triangle glyph)
    hx, hy = pos["hit"]
    lay = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(lay)
    nx, ny = hx + 30, hy - 250
    glow = Image.new("RGB", (W, H))
    ImageDraw.Draw(glow).text((nx, ny), "-8", font=font("anton", 100), fill=PAL["harm"])
    img = cl.add(img, ImageEnhance.Brightness(glow.filter(ImageFilter.GaussianBlur(12))).enhance(1.6))
    d = ImageDraw.Draw(img)
    d.text((nx, ny), "-8", font=font("anton", 100), fill=(255, 246, 240), stroke_width=4, stroke_fill=(40, 6, 6))
    d.polygon([(nx - 42, ny + 40), (nx - 8, ny + 40), (nx - 25, ny + 68)], fill=PAL["harm"])
    # HP numbers
    for k, hp, col in (("op", "60/60", PAL["gain"]), ("en", "27/40", PAL["gain"])):
        x, y = pos[k]["hp_label"]
        cl.text(img, (x, y + 10), hp, font("mono", 36), col, anchor="mm")
    # glass UI
    top_bar(img, "TURN 1  //  FREE NUDGE 1  //  Q/E NUDGE YOUR WHEEL  //  W NUDGE THE TARGET")
    left = (24, 96, 262, 460)
    right = (1690, 96, 1896, 470)
    cl.glass_panel(img, left, "OPERATIVE")
    for i, (a, b) in enumerate((("CLASS", "BREAKER"), ("RAM", "3 / 12"), ("STATUS", "OK"), ("NUDGES", "1 FREE"))):
        cl.text(img, (40, 336 + i * 28), a, font("mono", 17), PAL["text_lo"])
        cl.text(img, (150, 336 + i * 28), b, font("mono", 17), PAL["text_hi"])
    cl.glass_panel(img, right, "HOSTILE", rule=PAL["orange"])
    lines = [("COLLECTIONS", PAL["text_hi"]), ("AGENT", PAL["text_hi"]), ("MERIDIAN FREIGHT", PAL["orange"]),
             ("", None), ("INTENT", PAL["text_lo"]), ("AFFLICT 14", PAL["violet"]), ("CORRUPTS ON HIT", PAL["text_mid"]),
             ("", None), ("BLOCK", PAL["text_lo"]), ("+6 NEXT TURN", PAL["cyan"])]
    for i, (s, c) in enumerate(lines):
        if s:
            cl.text(img, (1708, 150 + i * 28), s, font("mono", 18), c)
    img = exec_button(img)
    # light spill from the wheels onto every glass surface nearby (feedback 10)
    img = cl.light_spill(img, spin, [left, right, (0, 0, W - 1, 56), EXEC_BOX], k=0.6, blur=70)
    img = cl.crt(img, rng)
    img = cl.glitch(img, 0.1, random.Random(7))  # Heat 34 NOTICED: a whisper of glitch
    # -------- ANALOG: stickers + marker (never glitched, never lit)
    tag_stickers(img, rng, [("HEAT", "34/100", PAL["note_yellow"]), ("HP", "60/60", PAL["paper"]), ("CYCLES", "120", PAL["sticker_pink"])], x=1560)
    # Polaroid of the operative on the operative panel
    pol = cl.paper_texture((150, 176), rng, (248, 246, 240)).convert("RGBA")
    pd = ImageDraw.Draw(pol)
    pd.rectangle((12, 12, 138, 138), fill=(30, 22, 34))
    ph = cl.halftone((126, 126), rng, PAL["pink"], 5, 0.4, fn=lambda u, v: max(0.0, 1 - math.hypot(u - 0.5, (v - 0.62) * 0.9) * 1.9))
    pol.alpha_composite(ph, (12, 12))
    pd.ellipse((52, 32, 98, 84), fill=(17, 17, 17))  # head silhouette
    pd.polygon([(30, 138), (50, 92), (100, 92), (120, 138)], fill=(17, 17, 17))
    pd.line((88, 40, 118, 14), fill=(17, 17, 17), width=5)  # crowbar-antenna
    pd.text((75, 158), "BREAKER", font=font("marker", 17), fill=PAL["ink"], anchor="mm")
    cl.place_sticker(img, cl.die_cut(pol, 2), (142, 236), -5, shadow=(5, 6))
    tp = cl.tape((70, 22), rng)
    cl.place_sticker(img, tp, (142, 152), 8, shadow=(0, 0))
    # forecast tags (PAPER) above each wheel, at radius + 66 or wider
    for k, title, chips, col in (("op", "DEFEND  HALF POWER", [("+4 BLOCK", PAL["ink"]), ("YOU GET CORRUPTED", PAL["harm_ink"])], PAL["paper"]),
                                 ("en", "AFFLICT  GOOD AIM", [("CORRUPTED ON YOU", PAL["harm_ink"]), ("+6 BLOCK", PAL["ink"])], PAL["paper"])):
        tw = 330
        st = cl.paper_texture((tw, 70), rng, col).convert("RGBA")
        sd = ImageDraw.Draw(st)
        sd.text((12, 6), title, font=font("anton", 22), fill=PAL["ink"])
        x = 12
        for (s, c) in chips:
            wtxt = sd.textlength(s, font=font("plex", 15)) + 14
            sd.rectangle((x, 38, x + wtxt, 62), outline=c, width=2)
            sd.text((x + 7, 41), s, font=font("plex", 15), fill=c)
            x += wtxt + 8
        st = cl.die_cut(st, 5)
        cx, _ = pos[k]["center"]
        ty = pos[k]["top"][1] - 110
        cl.place_sticker(img, st, (cx, ty), rng.uniform(-3, 3), shadow=(6, 7))
    # hand of cards: slapped on as stickers, the newest one still mid-slap (feedback 8)
    hand = [("JOLT", 1, ["Spin a wheel 3", "ticks."], "paper", "common", "spin"),
            ("FINE TUNE", 1, ["+-1 nudge on", "one ring."], "pink", "uncommon", "nudge"),
            ("BRACE", 2, ["+4 BLOCK this", "turn."], "black", "common", "shield"),
            ("BRUTE SPIN", 2, ["Spin a wheel 6", "ticks."], "paper", "rare", "bolt")]
    for i, (t, c, r, kind, rar, g) in enumerate(hand):
        st = cl.card_sticker(rng, t, c, r, kind, rar, g)
        cl.place_sticker(img, st, (150 + i * 178, 955), rng.uniform(-5, 5), shadow=(7, 9))
    st = cl.card_sticker(rng, "OVERCLOCK", 3, ["Next spin x2.", "Heat +2."], "pink", "rare", "bolt")
    st = cl.peel_corner(st, 0.2)
    cl.place_sticker(img, st, (880, 915), 11, lift=1.0, slap_blur=1)
    # marker SEND IT over the washed-out EXECUTE
    mk = marker_render("combat", [{"text": "SEND IT", "x": 1484, "y": 1000, "cap": 66, "seed": 11, "write": 1.0,
                                   "drip": "forming", "drips": 4, "rot": -7}])
    img = over(img, mk)
    img.save(os.path.join(STILLS, "01_combat.png"))
    return img


# ================================================================== 02 CITY NIGHT
def hq_keep(near=None):
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    d.polygon([(700, 110), (950, 110), (960, 800), (690, 800)], fill=255)
    for (x, y) in (near or {}).get("helis", []):  # gunships fly high = near the ortho camera: sharp
        d.ellipse((x - 190, y - 150, x + 190, y + 150), fill=255)
    return m.filter(ImageFilter.GaussianBlur(30))


def city_post(city, rng, fog_tint=(50, 110, 130), fog_strength=0.42, n_fog=16, max_blur=9, soften=True, fog_scale=1.0, near=None):
    img = cl.tilt_shift(city, (0.34, 0.8), max_blur, keep=hq_keep(near))
    img = cl.fog_patches(img, rng, n_fog, fog_tint, fog_strength, region=(0, 80, W, 760), soften=soften, scale=fog_scale)
    return img


def still_night():
    rng = random.Random(202)
    city = Image.open(C("city_night.png")).convert("RGB")
    img = city_post(city, rng)
    top_bar(img, "CITY GRID  //  NIGHT  02:14  //  MERIDIAN FREIGHT DISTRICT  //  3 SITES IN REACH")
    leg = (24, 800, 360, 1040)
    cl.glass_panel(img, leg, "LEGEND")
    d = ImageDraw.Draw(img)
    items = [("CELL TURF", PAL["acid"], "solid"), ("OPEN LINK", PAL["cyan"], "thin"), ("CORP THREAT", PAL["orange"], "chev"), ("HQ", PAL["pink"], "hex")]
    for i, (s, c, kind) in enumerate(items):
        y = 862 + i * 42
        if kind == "solid":
            d.line((44, y, 104, y), fill=c, width=5)
        elif kind == "thin":
            d.line((44, y, 104, y), fill=c, width=2)
        elif kind == "chev":
            for k in range(4):
                x = 48 + k * 15
                d.line((x, y - 6, x + 7, y, x, y + 6), fill=c, width=3)
        else:
            d.regular_polygon((74, y, 12), 6, outline=c, width=3)
        cl.text(img, (124, y - 11), s, font("mono", 20), PAL["text_hi"])
    img = exec_button(img, "DEPLOY", "[ENTER]")
    emis = city
    img = cl.light_spill(img, emis, [leg, (0, 0, W - 1, 56), EXEC_BOX], k=0.45, blur=60)
    img = cl.crt(img, rng)
    img = cl.glitch(img, 0.04, random.Random(3))  # COOL: almost nothing
    tag_stickers(img, rng, [("HEAT", "12/100", PAL["paper"]), ("CYCLES", "120", PAL["sticker_pink"])], x=1500)
    mk = marker_render("night", [{"text": "JACK IN", "x": 1484, "y": 1000, "cap": 60, "seed": 5, "write": 1.0,
                                  "drip": "forming", "drips": 4, "rot": -5}])
    img = over(img, mk)
    img.save(os.path.join(STILLS, "02_city_night.png"))
    return img


# ================================================================== 03 HEAT
def still_heat():
    rng = random.Random(303)
    city = Image.open(C("city_heat.png")).convert("RGB")
    base = city_post(city, rng, fog_tint=(70, 20, 30), fog_strength=0.3, n_fog=10, max_blur=5, soften=False, fog_scale=0.7,
                     near=json.load(open(C("city_heat.json"))))
    base = ImageEnhance.Color(base).enhance(0.75)  # HUNTED grade: -25% saturation
    # the WORLD layer takes the full glitch; the GLASS UI layer on top takes a lighter pass (readability first)
    img = cl.glitch(cl.crt(base, random.Random(1)), 1.0, random.Random(99), rain_col=(255, 80, 70))
    cl.glass_panel(img, (0, 0, W - 1, 56), None, edge=PAL["harm"], alpha=0.9)
    cl.text(img, (22, 16), "CITY GRID  //  HEAT 82  HUNTED  //  CORP SWEEP IN PROGRESS", font("mono", 22), PAL["harm"])
    alert = (24, 96, 420, 330)
    cl.glass_panel(img, alert, "!  SWEEP DETECTED", edge=PAL["harm"], rule=PAL["harm"])
    for i, s in enumerate(("GUNSHIPS      3", "DRONE SWARM   70", "SEARCHLIGHTS  6", "HQ EXPOSURE   HIGH", "RAID ETA      2 TURNS")):
        cl.text(img, (44, 150 + i * 32), s, font("mono", 20), PAL["text_hi"] if i < 3 else PAL["harm"])
    opt = (24, 1000, 420, 1050)
    cl.glass_panel(img, opt, None)
    cl.text(img, (40, 1012), "OPTIONS > HEAT GLITCH FX  [ ON ]", font("mono", 18), PAL["text_mid"])
    img = cl.light_spill(img, city, [alert, (0, 0, W - 1, 56)], k=0.5, blur=60)
    img = cl.glitch(img, 0.3, random.Random(98), rain_col=(255, 80, 70))
    # the scale: same city, four Heat bands (concept annotation, drawn after the glitch)
    band = (440, 846, 1896, 1060)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rectangle(band, fill=(2, 4, 10, 235), outline=(200, 210, 220, 200))
    img = over(img, ov)
    cl.text(img, (458, 852), "HEAT GLITCH SCALE  (same frame, glitch level by Heat band)", font("mono", 18), PAL["text_mid"])
    src = cl.crt(base.crop((560, 180, 1520, 720)).resize((960, 540)), random.Random(5))
    tw, th = 336, 170
    for i, (name, lvl, col) in enumerate((("COOL 0-24", 0.04, PAL["text_mid"]), ("NOTICED 25+", 0.3, PAL["amber"]),
                                          ("FLAGGED 50+", 0.62, PAL["flagged"]), ("HUNTED 75+", 1.0, PAL["harm"]))):
        g = cl.glitch(src, lvl, random.Random(40 + i), rain_col=(255, 80, 70)).resize((tw, th), Image.LANCZOS)
        x = 458 + i * (tw + 20)
        img.paste(g, (x, 880))
        ImageDraw.Draw(img).rectangle((x, 880, x + tw, 880 + th), outline=col, width=2)
        cl.text(img, (x + 8, 884), name, font("mono", 18), col)
    # analog: the Heat poster (PAPER) - untouched by the glitch
    pw, ph = 250, 330
    poster = cl.paper_texture((pw, ph), rng, PAL["note_yellow"]).convert("RGBA")
    pd = ImageDraw.Draw(poster)
    pd.text((pw / 2, 40), "HEAT", font=font("anton", 44), fill=PAL["ink"], anchor="mm")
    pd.text((pw / 2, 130), "82", font=font("anton", 120), fill=PAL["harm_ink"], anchor="mm")
    pd.rectangle((0, 205, pw, 250), fill=PAL["harm_ink"])
    pd.text((pw / 2, 228), "HUNTED", font=font("anton", 34), fill=PAL["paper"], anchor="mm")
    ht = cl.halftone((pw, 70), rng, PAL["ink"], 6, 0.5, fn=lambda u, v: 0.2 + 0.6 * v)
    poster.alpha_composite(ht, (0, 258))
    poster = cl.die_cut(poster, 3)
    cl.place_sticker(img, poster, POSTER_C, 5, shadow=(9, 11))
    for (dx, dy, r) in ((-80, -170, -18), (80, -170, 16)):
        cl.place_sticker(img, cl.tape((84, 26), rng), (POSTER_C[0] + dx, POSTER_C[1] + dy), r, shadow=(0, 0))
    mk = marker_render("heat", [{"text": "RUN", "x": POSTER_C[0] - 118, "y": POSTER_C[1] + 180, "cap": 86, "seed": 9, "write": 1.0,
                                 "drip": "running", "drip_len": 170, "drips": 3, "rot": -8}])
    img = over(img, mk)
    img.save(os.path.join(STILLS, "03_heat.png"))
    return img


# ================================================================== 04 MODEM
def chip_icon(d, cx, cy, s, col):
    d.rectangle((cx - s, cy - s, cx + s, cy + s), outline=col, width=2)
    d.rectangle((cx - s * 0.45, cy - s * 0.45, cx + s * 0.45, cy + s * 0.45), outline=col, width=2)
    for k in range(-2, 3):
        o = k * s * 0.35
        for (a, b, c2, e) in ((cx + o, cy - s, cx + o, cy - s - 8), (cx + o, cy + s, cx + o, cy + s + 8),
                              (cx - s, cy + o, cx - s - 8, cy + o), (cx + s, cy + o, cx + s + 8, cy + o)):
            d.line((a, b, c2, e), fill=col, width=2)


def still_modem():
    rng = random.Random(404)
    city = Image.open(C("city_nodes_off.png")).convert("RGB")
    bg = cl.recede(city, desat=0.5, dim=0.38, blur=3.0)
    sign = Image.open(C("sign.png")).convert("RGB")
    img = cl.add(bg, sign)
    top_bar(img, "05  MODEM CYBER SHOP")
    micro = (380, 84, 1000, 470)
    cards = (1030, 84, 1896, 470)
    slices = (380, 500, 770, 880)
    daem = (790, 500, 1000, 880)
    remove = (1030, 500, 1896, 880)
    for b, t, rule in ((micro, "MICROCHIPS", PAL["pink"]), (cards, "CARDS", PAL["pink"]), (slices, "SLICES", PAL["amber"]),
                       (daem, "DAEMONS", PAL["violet"]), (remove, "REMOVE A CARD", PAL["acid"])):
        cl.glass_panel(img, b, t, rule=rule)
    lay = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(lay)
    # microchips: vector icons + mono prices on glass
    for i, (name, price, desc) in enumerate((("BARBED WIRE", 141, ["DEF slice also deals", "2 dmg to the pointer."]),
                                             ("SHUNT", 129, ["Resolves the neighbour", "on the landing side."]))):
        x = 400 + i * 300
        d.rectangle((x, 140, x + 280, 400), outline=(40, 90, 110), width=1)
        chip_icon(d, x + 140, 200, 30, PAL["cyan"])
        d.text((x + 140, 262), name, font=font("mono", 20), fill=PAL["text_hi"], anchor="mm")
        for k, s in enumerate(desc):
            d.text((x + 140, 292 + k * 22), s, font=font("mono", 15), fill=PAL["text_mid"], anchor="mm")
        d.text((x + 140, 372), "(o) %d" % price, font=font("mono", 22), fill=PAL["acid"], anchor="mm")
    d.rectangle((400, 416, 980, 452), outline=(70, 120, 140), width=1)
    d.text((412, 424), "SOCKET INTO  > SLOT 1 : CRIT 12", font=font("mono", 17), fill=PAL["text_mid"])
    # slices: vector sector shapes
    for i, (g, v, c) in enumerate((("SHD", 5, PAL["cyan"]), ("ATK", 10, PAL["pink"]), ("EVD", 2, PAL["gain"]))):
        x = 400 + i * 124
        cx, cy = x + 56, 700
        # a slice as the wheel draws it: annulus sector, bright outer rim, translucent fill
        ocx, ocy = cx, 830
        poly = [(ocx + 190 * math.cos(math.radians(a)), ocy + 190 * math.sin(math.radians(a))) for a in range(252, 289, 4)]
        poly += [(ocx + 95 * math.cos(math.radians(a)), ocy + 95 * math.sin(math.radians(a))) for a in range(288, 251, -4)]
        fill_l = Image.new("RGB", (W, H))
        ImageDraw.Draw(fill_l).polygon(poly, fill=tuple(v // 5 for v in c))
        lay.paste(ImageChops.add(lay, fill_l))
        d = ImageDraw.Draw(lay)
        d.line(poly[:10], fill=c, width=4)
        d.line(poly[9:] + [poly[0]], fill=c, width=2)
        d.text((cx, 600), g, font=font("mono", 20), fill=c, anchor="mm")
        d.text((cx, 700), str(v), font=font("mono", 38), fill=PAL["text_hi"], anchor="mm")
        d.text((cx, 840), "(o) 100", font=font("mono", 18), fill=PAL["acid"], anchor="mm")
    chip_icon(d, 895, 640, 34, PAL["violet"])
    d.text((895, 710), "SCRUBBER", font=font("mono", 19), fill=PAL["text_hi"], anchor="mm")
    for k, s in enumerate(("Capture a rack:", "-1 Heat instead", "of adding it.")):
        d.text((895, 740 + k * 20), s, font=font("mono", 14), fill=PAL["text_mid"], anchor="mm")
    d.text((895, 840), "(o) 218", font=font("mono", 18), fill=PAL["acid"], anchor="mm")
    # remove a card: shredder vector + wheel preview
    d.rectangle((1060, 560, 1260, 780), outline=(40, 90, 110), width=1)
    d.rectangle((1110, 690, 1210, 712), outline=PAL["acid"], width=3)
    for k in range(9):
        d.line((1116 + k * 11, 716, 1116 + k * 11, 748), fill=PAL["acid"], width=2)
    d.text((1160, 800), "SHRED  (o) 50", font=font("mono", 20), fill=PAL["acid"], anchor="mm")
    d.text((1300, 570), "CYCLES", font=font("mono", 18), fill=PAL["text_lo"])
    d.text((1300, 592), "120", font=font("mono", 44), fill=PAL["text_hi"])
    for k, c in enumerate((PAL["pink"], PAL["pink"], PAL["cyan"], PAL["pink"], PAL["gain"], PAL["pink"])):
        d.arc((1560, 560, 1760, 760), -90 + k * 60 + 3, -90 + (k + 1) * 60 - 3, fill=c, width=26)
    d.text((1660, 790), "SPINNER", font=font("mono", 18), fill=PAL["text_mid"], anchor="mm")
    for k in range(3):
        x = 1090 + k * 270
        d.text((x + 100, 440), "(o) %d" % (69, 61, 75)[k], font=font("mono", 22), fill=PAL["acid"], anchor="mm")
    img = ImageChops.add(img, lay)
    img = exec_button(img, "EXIT SHOP", "[ESC]")
    img = cl.light_spill(img, ImageChops.add(sign, lay.point(lambda v: v // 3)), [micro, slices, (0, 0, W - 1, 56), daem], k=0.7, blur=80)
    img = cl.crt(img, rng)
    img = cl.glitch(img, 0.06, random.Random(8))
    tag_stickers(img, rng, [("HEAT", "0/100", PAL["paper"]), ("CYCLES", "120", PAL["note_yellow"]), ("CARDS", "10", PAL["sticker_pink"])], x=1400)
    # the cards on offer, stickered onto the glass
    for k, (t, c, r, kind, rar, g) in enumerate((("MIRROR FLIP", 3, ["Flip a wheel.", "Blocked by resist."], "paper", "common", "spin"),
                                                  ("ENCRYPT", 1, ["A slice absorbs", "the next status."], "black", "uncommon", "shield"),
                                                  ("TAP TAP", 2, ["Three +-1 nudges", "on one ring."], "pink", "rare", "nudge"))):
        st = cl.card_sticker(rng, t, c, r, kind, rar, g, w=150, h=210)
        cl.place_sticker(img, st, (1190 + k * 270, 260), rng.uniform(-5, 5), shadow=(7, 9))
    # a zine sticker slapped on the microchip panel corner
    zs = Image.new("RGBA", (130, 130), (0, 0, 0, 0))
    zd = ImageDraw.Draw(zs)
    pts = [(65 + (60 if k % 2 == 0 else 38) * math.cos(k * math.pi / 8), 65 + (60 if k % 2 == 0 else 38) * math.sin(k * math.pi / 8)) for k in range(16)]
    zd.polygon(pts, fill=PAL["acid"])
    zd.text((65, 56), "NO", font=font("anton", 26), fill=PAL["ink"], anchor="mm")
    zd.text((65, 82), "REFUNDS", font=font("anton", 18), fill=PAL["ink"], anchor="mm")
    cl.place_sticker(img, cl.die_cut(zs, 5), (960, 120), 14, shadow=(5, 6))
    mk = marker_render("modem", [{"text": "LEAVE", "x": 1530, "y": 1002, "cap": 70, "seed": 21, "write": 1.0,
                                  "drip": "forming", "drips": 3, "rot": -6},
                                 {"shape": "circle", "x": 1730, "y": 262, "rx": 110, "ry": 142, "cap": 60, "seed": 3, "weight": 0.1}])
    img = over(img, mk)
    img.save(os.path.join(STILLS, "04_hq_modem.png"))
    return img


# ================================================================== 05 MARKER STRIP
def still_strip():
    rng = random.Random(505)
    city = Image.open(C("city_nodes_off.png")).convert("RGB")
    bg = cl.recede(city, desat=0.4, dim=0.4, blur=2.0)
    canvas = Image.new("RGB", (W, H), (8, 10, 14))
    PW, PY0, PY1 = 610, 120, 1050
    xs = [25 + k * (PW + 30) for k in range(3)]
    jobs = []
    heads = [("1  WRITE-ON", "stroke by stroke, pen tip wet"), ("2  DRIPS FORM, THEN PAUSE", "the game waits for the player"),
             ("3  PAGE LEAVES, DRIPS RUN", "on press: ink keeps running down")]
    for k, x0 in enumerate(xs):
        crop = bg.crop((300 + k * 200, 80, 300 + k * 200 + PW, 80 + (PY1 - PY0)))
        panel = crop.copy()
        bx = (60, 380, PW - 60, 520)
        panel = cl.glass_panel(panel, (20, 20, PW - 20, 70), None)
        cl.text(panel, (36, 34), "COMBAT // TURN 3", font("mono", 20), PAL["text_mid"])
        panel = exec_button(panel, "EXECUTE", "[SPACE]", box=bx)
        if k == 2:
            # the page is leaving: digital layer tears upward and glitches out, next page scrolls in
            nxt = Image.new("RGB", panel.size, (4, 6, 10))
            nd = ImageDraw.Draw(nxt)
            for gy in range(0, panel.height, 40):
                nd.line((0, gy, panel.width, gy), fill=(14, 40, 44))
            for gx in range(0, panel.width, 40):
                nd.line((gx, 0, gx, panel.height), fill=(14, 40, 44))
            cl.text(nxt, (36, panel.height - 60), "RESOLVING...", font("mono", 22), PAL["cyan"])
            shifted = Image.new("RGB", panel.size)
            shifted.paste(panel.crop((0, 260, panel.width, panel.height)), (0, 0))
            m = cl.vgrad_mask(panel.size, [(0, 255), (0.45, 255), (0.62, 0), (1, 0)])
            panel = Image.composite(shifted, nxt, m)
            panel = cl.glitch(panel, 0.7, random.Random(12))
        panel = cl.crt(panel, random.Random(k))
        canvas.paste(panel, (x0, PY0))
        ImageDraw.Draw(canvas).rectangle((x0 - 1, PY0 - 1, x0 + PW, PY1), outline=(90, 100, 110), width=2)
        cl.text(canvas, (x0, 40), heads[k][0], font("mono", 30), PAL["text_hi"])
        cl.text(canvas, (x0, 80), heads[k][1], font("mono", 18), PAL["text_lo"])
        tx, ty = x0 + 45, PY0 + (bx[3] if k < 2 else 250) - 25
        job = {"text": "SEND IT", "x": tx, "y": ty, "cap": 74, "seed": 11, "rot": -7}
        if k == 0:
            job.update(write=0.63, drip="none")
        elif k == 1:
            job.update(write=1.0, drip="forming", drips=5)
        else:
            job.update(write=1.0, drip="running", drip_len=PY1 - ty - 10, drips=5)
        jobs.append(job)
    mk = marker_render("strip", jobs)
    # clip the marker to the panels
    clip = Image.new("L", (W, H), 0)
    cd = ImageDraw.Draw(clip)
    for x0 in xs:
        cd.rectangle((x0, PY0, x0 + PW - 1, PY1 - 1), fill=255)
    a = ImageChops.multiply(mk.split()[3], clip)
    mk.putalpha(a)
    img = over(canvas, mk)
    img.save(os.path.join(STILLS, "05_marker_strip.png"))
    return img


def contact_sheet(imgs):
    tw, th = 960, 540
    names = ["01 COMBAT", "02 CITY NIGHT", "03 HEAT (HUNTED + SCALE)", "04 MODEM CYBER SHOP", "05 MARKER STRIP"]
    sheet = Image.new("RGB", (tw * 2 + 60, (th + 50) * 3 + 110), (10, 12, 16))
    cl.text(sheet, (20, 18), "E / GLITCH VECTOR CRT  -  the net through a vector-display cyberdeck; the Cell writes on the glass",
            font("mono", 26), PAL["text_hi"])
    for i, im in enumerate(imgs):
        x = 20 + (i % 2) * (tw + 20)
        y = 80 + (i // 2) * (th + 50)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + 34))
        cl.text(sheet, (x, y + 4), names[i], font("mono", 24), PAL["pink"])
    sheet.save(os.path.join(DIR, "contact_sheet.jpg"), quality=88)


if __name__ == "__main__":
    ims = [still_combat(), still_night(), still_heat(), still_modem(), still_strip()]
    contact_sheet(ims)
    if "--keep-cache" not in sys.argv:
        shutil.rmtree(CACHE, ignore_errors=True)
    print("ALL DONE")
