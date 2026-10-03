"""Round 27 sheets: meridian_fortress_options.png, halcyon_site_options.png, hq_compare_v3.jpg.
Locked round 26 images (Solace, Halcyon HQ, Orbital) are read from ../round26_hq_targets (read-only)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
R26 = os.path.join(OUT, "..", "round26_hq_targets")
SCR = os.path.join(OUT, "scratch")
F = "C:/Windows/Fonts/bahnschrift.ttf"
f1, f2, f3 = ImageFont.truetype(F, 34), ImageFont.truetype(F, 20), ImageFont.truetype(F, 16)
ORANGE, VIOLET = (255, 150, 40), (176, 120, 255)

FORTS = [("wall", "A  THE CONTAINER WALL  (CHOSEN)", ["straight crenellated curtain, 4 courses", "square stacked corner towers", "square gatehouse, drawbridge, moat",
                                                   "a regular MERIDIAN FREIGHT office inside"]),
         ("bunker", "B  STEPPED BUNKER", ["four receding container terraces", "angular prows, slit windows", "reads as a ziggurat again (Halcyon clash)"]),
         ("yard", "C  WALLED FREIGHT YARD", ["low wall, four lattice watchtowers", "stacks + gantry inside", "least 'fortress' from afar"]),
         ("citadel", "D  CITADEL GATEHOUSE FACE", ["a towering gate block + bastions", "strong face-on, but a slab", "on the map: one blocky mass"])]
SITES = [("sphinx2", "A  SCULPTED SPHINX", ["smooth tube-sculpted body, chest, paws", "nemes with amber bands, eye on brow", "still lumpy at Site scale"]),
         ("court", "B  HALCYON COURT + JUSTICE  (RECOMMENDED)", ["temple front, pediment with the eye", "giant Justice statue: the eye in place", "of the blindfold, lit amber scales",
                                                             "reads instantly as 'civic power'"]),
         ("obelisk", "C  SURVEILLANCE OBELISK", ["faceted obelisk, camera rings", "red camera lights, the eye at the tip", "strong but close to Orbital's mast idea"])]


def tile(path, w, h):
    im = Image.open(path).convert("RGB")
    k = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * k + 1), int(im.height * k + 1)), Image.LANCZOS)
    x0, y0 = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x0, y0, x0 + w, y0 + h))


def fortress_options():
    W, H = 2400, 1100
    sh = Image.new("RGB", (W, H), (14, 13, 20))
    d = ImageDraw.Draw(sh)
    d.text((20, 14), "MERIDIAN  -  angular container FORTRESS takes (night, face-on to the gate)", font=f1, fill=(240, 236, 226))
    d.text((20, 58), "No round shapes. Kit: dark rust curtain walls vs floodlit orange square towers, lit battlement lines, banners, glowing gate, lit moat.",
           font=f3, fill=(200, 200, 210))
    cw = 590
    for i, (key, title, lines) in enumerate(FORTS):
        x = 15 + i * (cw + 8)
        im = tile(os.path.join(SCR, "opt", "meridian_hq_%s_beauty_night.png" % key), cw, 520)
        sh.paste(im, (x, 100))
        d.text((x, 630), title, font=f2, fill=ORANGE if key == "wall" else (230, 230, 240))
        for k, ln in enumerate(lines):
            d.text((x, 660 + k * 22), ln, font=f3, fill=(200, 200, 210))
        sp = Image.open(os.path.join(SCR, "opt", "meridian_hq_%s_map_beauty.png" % key)).convert("RGBA")
        sp = sp.crop(sp.getbbox())
        d.text((x, 760), "on the city map (small  |  2x)", font=f3, fill=(255, 214, 64))
        box = Image.new("RGB", (cw, 290), (30, 26, 40))
        ks = min(0.42, 125 / sp.height)
        small = sp.resize((max(1, int(sp.width * ks)), max(1, int(sp.height * ks))), Image.LANCZOS)
        big = sp.resize((max(1, int(sp.width * ks * 2)), max(1, int(sp.height * ks * 2))), Image.LANCZOS)
        box.paste(small, (40, 270 - small.height), small)
        box.paste(big, (cw - big.width - 30, 280 - big.height), big)
        sh.paste(box, (x, 786))
        if key == "wall":
            d.rectangle([x - 4, 96, x + cw + 3, 1080], outline=ORANGE, width=3)
    sh.save(os.path.join(OUT, "meridian_fortress_options.png"), optimize=True)
    print("meridian_fortress_options.png")


def halcyon_options():
    W, H = 2400, 900
    sh = Image.new("RGB", (W, H), (14, 13, 20))
    d = ImageDraw.Draw(sh)
    d.text((20, 14), "HALCYON  -  regular Site landmark options (same plot, night)", font=f1, fill=(240, 236, 226))
    cw = 785
    for i, (key, title, lines) in enumerate(SITES):
        x = 15 + i * (cw + 8)
        sh.paste(tile(os.path.join(OUT, "site_halcyon_%s_night.jpg" % key), cw, 600), (x, 70))
        d.text((x, 685), title, font=f2, fill=VIOLET if key == "court" else (230, 230, 240))
        for k, ln in enumerate(lines):
            d.text((x, 716 + k * 24), ln, font=f3, fill=(200, 200, 210))
        if key == "court":
            d.rectangle([x - 4, 66, x + cw + 3, 820], outline=VIOLET, width=3)
    sh.save(os.path.join(OUT, "halcyon_site_options.png"), optimize=True)
    print("halcyon_site_options.png")


def src(fn):
    for base in (OUT, R26):
        p = os.path.join(base, fn)
        if os.path.exists(p):
            return p
    return None


ROWS = [("MERIDIAN  -  the Container Wall fortress (new)", (255, 140, 26),
         ["hq_meridian_city.jpg", "hq_meridian_close_night.jpg", "hq_meridian_close_day.jpg", None, "combat_meridian.jpg", "site_meridian_night.jpg"]),
        ("SOLACE  -  locked (round 26)", (150, 255, 70),
         ["hq_solace_city.jpg", "hq_solace_close_night.jpg", "hq_solace_close_day.jpg", None, "combat_solace.jpg", "site_solace_night.jpg"]),
        ("HALCYON  -  HQ locked; new Site: Halcyon Court + Justice", (176, 120, 255),
         ["hq_halcyon_city.jpg", "hq_halcyon_close_night.jpg", "hq_halcyon_close_day.jpg", "site_halcyon_police_night.jpg", "combat_halcyon.jpg", "site_halcyon_court_night.jpg"]),
        ("ORBITAL  -  locked (round 26)", (205, 240, 255),
         ["hq_orbital_city.jpg", "hq_orbital_close_night.jpg", "hq_orbital_close_day.jpg", "hq_orbital_close_night_open.jpg", "combat_orbital.jpg", "site_orbital_night.jpg"])]
COLS = ["CITY MAP", "CLOSE-UP NIGHT", "CLOSE-UP DAY", "VARIANT", "COMBAT", "REGULAR SITE"]


def compare():
    tw, th = 380, 214
    W = 20 + 6 * (tw + 8)
    H = 92 + len(ROWS) * (th + 40)
    sh = Image.new("RGB", (W, H), (14, 13, 20))
    d = ImageDraw.Draw(sh)
    d.text((14, 12), "ROUND 27  -  HQ = boss target (map = close-up); new Meridian fortress, new Halcyon Site", font=f1, fill=(240, 236, 226))
    for c, t in enumerate(COLS):
        d.text((20 + c * (tw + 8), 60), t, font=f3, fill=(255, 214, 64))
    for r, (cap, col, files) in enumerate(ROWS):
        y = 84 + r * (th + 40)
        d.text((20, y), cap, font=f3, fill=col)
        for c, fn in enumerate(files):
            p = src(fn) if fn else None
            if p:
                sh.paste(tile(p, tw, th), (20 + c * (tw + 8), y + 20))
    sh.save(os.path.join(OUT, "hq_compare_v3.jpg"), quality=87)
    print("hq_compare_v3.jpg")


if __name__ == "__main__":
    fortress_options()
    halcyon_options()
    compare()
