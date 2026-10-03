"""Round 26: the deliverables from the finished renders.
  idea_<n>_<name>_{map,close,dispatch}.jpg, recommended_{map,map_dispatch,close,dispatch}.jpg, options_sheet.jpg
Inputs: ../scratch/mapcrops/rc26_<idea>[_dispatch].png (map26.py), ../scratch/backdrops/rc26_<idea>[_dispatch]_night.png (post26.py).
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
R26 = os.path.dirname(HERE)
MC = os.path.join(R26, "scratch", "mapcrops")
BD = os.path.join(R26, "scratch", "backdrops")
F = "C:/Windows/Fonts/bahnschrift.ttf"
IDEAS = [("tokyo", "1", "tokyo_street", "1  TOKYO STREET",
          "Map: the canyon + its tower in the palm; the fist is still the roads.  Close: the best street life (signs, wires, lanterns)."),
         ("roofs", "2", "painted_roofs", "2  PAINTED ROOFS",
          "Map: red roofs thicken the road fist (subtle, as asked).  Close: gritty painted roofs, no single HQ building."),
         ("skyline", "3", "hijacked_skyline", "3  HIJACKED SKYLINE",
          "Map: the hologram is the loudest fist, but it hides the road fist's fingers.  Close: a strong beacon above the wheels."),
         ("deck", "4", "knuckle_deck", "4  KNUCKLE DECK (own idea)",
          "Map: a parking deck whose plan IS the crest: reads at a glance, sits in the palm.  Close: four knuckle decks rise."),
         ("rec", "R", "recommended", "RECOMMENDED: KNUCKLE DECK AT THE HEAD OF A HIJACKED CANYON",
          "The deck (map crest, HQ silhouette) + the Tokyo canyon along the thumb road (street life) + screens/tags = the Cell's look.")]


def font(s):
    f = ImageFont.truetype(F, s)
    try:
        f.set_variation_by_name("Bold")
    except Exception:
        pass
    return f


def label(im, text, sub=None):
    im = im.copy()
    d = ImageDraw.Draw(im)
    f = font(max(18, im.width // 60))
    tw = d.textlength(text, font=f)
    d.rectangle([0, 0, tw + 30, f.size + 18], fill=(10, 9, 16))
    d.rectangle([0, 0, 6, f.size + 18], fill=(212, 255, 0))
    d.text((16, 8), text, font=f, fill=(240, 236, 226))
    return im


def save_jpg(im, name):
    im.convert("RGB").save(os.path.join(R26, name), quality=90, optimize=True)
    print("wrote", name)


def main():
    rows = []
    for idea, n, slug, title, verdict in IDEAS:
        mp = Image.open(os.path.join(MC, "rc26_%s.png" % idea)).convert("RGB")
        cl = Image.open(os.path.join(BD, "rc26_%s_night.png" % idea)).convert("RGB")
        dp = Image.open(os.path.join(BD, "rc26_%s_dispatch_night.png" % idea)).convert("RGB")
        if idea == "rec":
            save_jpg(label(mp, "CITY MAP - RECOMMENDED: the Knuckle Deck in the palm, canyon along the thumb road"), "recommended_map.jpg")
            mpd = os.path.join(MC, "rc26_rec_dispatch.png")
            if os.path.exists(mpd):
                save_jpg(label(Image.open(mpd), "CITY MAP - RECOMMENDED after the betrayal (DISPATCH)"), "recommended_map_dispatch.jpg")
            save_jpg(label(cl, "CLOSE-UP NIGHT - RECOMMENDED (the Cell's home)"), "recommended_close.jpg")
            save_jpg(label(dp, "CLOSE-UP NIGHT - RECOMMENDED as DISPATCH (after the betrayal)"), "recommended_dispatch.jpg")
        else:
            save_jpg(label(mp, "CITY MAP - " + title), "idea_%s_%s_map.jpg" % (n, slug))
            save_jpg(label(cl, "CLOSE-UP NIGHT - " + title), "idea_%s_%s_close.jpg" % (n, slug))
            save_jpg(label(dp, "DISPATCH - " + title), "idea_%s_%s_dispatch.jpg" % (n, slug))
        rows.append((title, verdict, mp, cl, dp))
    # options sheet: one row per idea (map | close-up | DISPATCH)
    MW, MH = 640, 490
    CW, CH = 871, 490
    pad, head, sub = 14, 54, 34
    W = pad * 4 + MW + CW * 2
    H = 70 + len(rows) * (head + MH + sub + pad)
    sh = Image.new("RGB", (W, H), (14, 12, 20))
    d = ImageDraw.Draw(sh)
    d.text((pad, 16), "ROUND 26  -  REBEL_CELL BASE: OPTIONS   (city map  |  close-up night  |  DISPATCH after the betrayal)", font=font(30),
           fill=(240, 236, 226))
    y = 70
    for (title, verdict, mp, cl, dp) in rows:
        rec = title.startswith("RECOMMENDED")
        d.rectangle([pad, y, W - pad, y + head - 8], fill=(36, 44, 6) if rec else (28, 24, 36))
        d.rectangle([pad, y, pad + 8, y + head - 8], fill=(212, 255, 0) if rec else (255, 61, 168))
        d.text((pad + 22, y + 8), title, font=font(28), fill=(240, 236, 226))
        y += head
        x = pad
        for im, (w, h) in ((mp, (MW, MH)), (cl, (CW, CH)), (dp, (CW, CH))):
            k = max(w / im.width, h / im.height)
            r = im.resize((int(im.width * k + 0.5), int(im.height * k + 0.5)), Image.LANCZOS)
            ox, oy = (r.width - w) // 2, (r.height - h) // 2
            sh.paste(r.crop((ox, oy, ox + w, oy + h)), (x, y))
            x += w + pad
        d.text((pad + 4, y + MH + 6), verdict, font=font(21), fill=(200, 196, 214))
        y += MH + sub + pad
    save_jpg(sh, "options_sheet.jpg")


if __name__ == "__main__":
    main()
