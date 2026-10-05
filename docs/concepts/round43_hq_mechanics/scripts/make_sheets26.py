"""Round 26 sheets: meridian_castle_options.png and hq_compare_v2.jpg."""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
SCR = os.path.join(OUT, "scratch")
F = "C:/Windows/Fonts/bahnschrift.ttf"
f1, f2, f3 = ImageFont.truetype(F, 34), ImageFont.truetype(F, 20), ImageFont.truetype(F, 16)
ORANGE = (255, 150, 40)

OPTS = [("concentric", "A  CONCENTRIC (Beaumaris)", ["low outer ring + small drums", "high inner square, big drum corners", "central keep", "busy: too many drums at map size"]),
        ("motte", "B  MOTTE & BAILEY  (CHOSEN)", ["one tall keep on a mound", "dark container ring wall", "clearest silhouette from afar:", "keep + ring + gate"]),
        ("star", "C  STAR FORT", ["five bastions, low thick walls", "stepped keep with white crown", "the star only reads from above"]),
        ("japan", "D  TIERED (Himeji)", ["stone base, shrinking tiers", "flared roofs", "reads as a pagoda, not a castle"])]


def options():
    W, H = 2400, 1090
    sh = Image.new("RGB", (W, H), (14, 13, 20))
    d = ImageDraw.Draw(sh)
    d.text((20, 14), "MERIDIAN  -  container castle silhouettes (night, combat camera face-on to the drawbridge)", font=f1, fill=(240, 236, 226))
    d.text((20, 58), "Readability kit used on all four: dark rust curtain walls vs FLOODLIT orange drum towers (lit toon), lit amber battlement lines, "
                     "long orange banners, glowing gate + portcullis, lit moat.", font=f3, fill=(200, 200, 210))
    cw = 590
    for i, (key, title, lines) in enumerate(OPTS):
        x = 15 + i * (cw + 8)
        im = Image.open(os.path.join(SCR, "opt", "meridian_hq_%s_beauty_night.png" % key)).convert("RGB")
        im = im.crop((240, 0, 1040, 720)).resize((cw, int(cw * 720 / 800)), Image.LANCZOS)
        sh.paste(im, (x, 100))
        d.text((x, 100 + im.height + 8), title, font=f2, fill=ORANGE if key == "motte" else (230, 230, 240))
        for k, ln in enumerate(lines):
            d.text((x, 100 + im.height + 38 + k * 22), ln, font=f3, fill=(200, 200, 210))
        sp = Image.open(os.path.join(SCR, "opt", "meridian_hq_%s_map_beauty.png" % key)).convert("RGBA")
        sp = sp.crop(sp.getbbox())
        y0 = 100 + im.height + 140
        d.text((x, y0), "on the city map (small  |  2x)", font=f3, fill=(255, 214, 64))
        box = Image.new("RGB", (cw, 270), (30, 26, 40))
        ks = min(0.42, 120 / sp.height)  # map scale (capped so the 2x copy fits)
        small = sp.resize((max(1, int(sp.width * ks)), max(1, int(sp.height * ks))), Image.LANCZOS)
        big = sp.resize((max(1, int(sp.width * ks * 2)), max(1, int(sp.height * ks * 2))), Image.LANCZOS)
        box.paste(small, (40, 250 - small.height), small)
        box.paste(big, (cw - big.width - 30, 260 - big.height), big)
        sh.paste(box, (x, y0 + 26))
        if key == "motte":
            d.rectangle([x - 4, 96, x + cw + 3, y0 + 300], outline=ORANGE, width=3)
    sh.save(os.path.join(OUT, "meridian_castle_options.png"), optimize=True)
    print("meridian_castle_options.png")


ROWS = [("meridian", "MERIDIAN  -  the Container Castle (motte & bailey)", (255, 140, 26),
         ["hq_meridian_city.jpg", "hq_meridian_close_night.jpg", "hq_meridian_close_day.jpg", None, "combat_meridian.jpg", "site_meridian_night.jpg"]),
        ("solace", "SOLACE  -  the Helix, lit (down-lights, spotlight, LED chaser)", (150, 255, 70),
         ["hq_solace_city.jpg", "hq_solace_close_night.jpg", "hq_solace_close_day.jpg", None, "combat_solace.jpg", "site_solace_night.jpg"]),
        ("halcyon", "HALCYON  -  the Civic Core and its scanning eye", (176, 120, 255),
         ["hq_halcyon_city.jpg", "hq_halcyon_close_night.jpg", "hq_halcyon_close_day.jpg", "site_halcyon_police_night.jpg", "combat_halcyon.jpg", "site_halcyon_sphinx_night.jpg"]),
        ("orbital", "ORBITAL  -  the Silo Crescent (silo in the ground, sliding doors)", (205, 240, 255),
         ["hq_orbital_city.jpg", "hq_orbital_close_night.jpg", "hq_orbital_close_day.jpg", "hq_orbital_close_night_open.jpg", "combat_orbital.jpg", "site_orbital_night.jpg"])]
COLS = ["CITY MAP", "CLOSE-UP NIGHT", "CLOSE-UP DAY", "VARIANT (police / silo open)", "COMBAT", "REGULAR SITE"]


def compare():
    tw, th = 380, 214
    W = 20 + 6 * (tw + 8)
    H = 92 + len(ROWS) * (th + 40)
    sh = Image.new("RGB", (W, H), (14, 13, 20))
    d = ImageDraw.Draw(sh)
    d.text((14, 12), "ROUND 26  -  HQ = boss target, closer combat framing, same model + roads as the map", font=f1, fill=(240, 236, 226))
    for c, t in enumerate(COLS):
        d.text((20 + c * (tw + 8), 60), t, font=f3, fill=(255, 214, 64))
    for r, (corp, cap, col, files) in enumerate(ROWS):
        y = 84 + r * (th + 40)
        d.text((20, y), cap, font=f3, fill=col)
        for c, fn in enumerate(files):
            if not fn or not os.path.exists(os.path.join(OUT, fn)):
                continue
            im = Image.open(os.path.join(OUT, fn)).convert("RGB")
            k = max(tw / im.width, th / im.height)
            im = im.resize((int(im.width * k + 1), int(im.height * k + 1)), Image.LANCZOS)
            x0, y0 = (im.width - tw) // 2, (im.height - th) // 2
            sh.paste(im.crop((x0, y0, x0 + tw, y0 + th)), (20 + c * (tw + 8), y + 20))
    sh.save(os.path.join(OUT, "hq_compare_v2.jpg"), quality=87)
    print("hq_compare_v2.jpg")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("options", "all"):
        options()
    if what in ("compare", "all"):
        compare()
