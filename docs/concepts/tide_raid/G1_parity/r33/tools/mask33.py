import json, sys
from PIL import Image, ImageDraw
def run(name, out):
    d = json.load(open("D:/rc_scratch/g1/r33/%s_mask.json" % name))
    im = Image.open("D:/rc_scratch/g1/r33/%s.png" % name).convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(ov)
    cr = d["city_rect"]
    cnt = {}
    for x, y, fl, h in d["rows"]:
        if fl & 2: c = (0, 200, 255, 150); k = "river"
        elif fl & 1: c = (0, 90, 255, 150); k = "water(bay/sea)"
        elif h <= 0: c = (255, 0, 255, 130); k = "terrain<=0 but not plan water"
        else: c = (0, 255, 0, 40); k = "land"
        cnt[k] = cnt.get(k, 0) + 1
        g.rectangle((x - 5, y - 4, x + 5, y + 4), fill=c)
    res = Image.alpha_composite(im, ov).convert("RGB")
    res.save(out)
    print(name, cnt, "coarse", d["coarse"], "city", cr)
run(sys.argv[1], sys.argv[2])
