from PIL import Image, ImageDraw
G = "D:/rc_art/art-pass/docs/concepts/tide_raid/G1_parity/"
names = ["01_plan","02_forecast","03_reveal","04_impact","05_home_hit","06_aftermath","07_city_lost"]
sheet = Image.new("RGB", (1920, 540 * 7))
for i, n in enumerate(names):
    for j, (d, t) in enumerate((("final/", "old (r13)"), ("final_proposed/", "proposed (r42)"))):
        im = Image.open(G + d + n + "_side_by_side.png").convert("RGB")
        w = im.width // 2
        g = im.crop((w, 0, im.width, im.height)).resize((960, 540))
        dr = ImageDraw.Draw(g)
        dr.rectangle((0, 20, 330, 40), fill=(8, 8, 20)); dr.text((6, 24), n + "  " + t, fill=(255, 255, 255))
        sheet.paste(g, (j * 960, i * 540))
sheet.save(G + "final_proposed/old_vs_new.jpg", quality=84)
