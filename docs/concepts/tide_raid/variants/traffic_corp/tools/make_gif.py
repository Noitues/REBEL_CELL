"""traffic_motion.gif (r43 | variant, zoom 4 on lot -57,3: surface streets at left, a highway deck diagonal at upper right) and traffic_motion_plan.gif (variant, plan zoom), from Movie Maker frames at 30 fps, every 2nd frame = 15 fps. Run by path."""
import os
from PIL import Image, ImageDraw
S = "D:/rc_scratch/traffic/"
OUT = "D:/rc_art/art-pass/docs/concepts/tide_raid/variants/traffic_corp/"


def lab(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 + 7 * len(t), 16), fill=(8, 8, 20))
    d.text((4, 3), t, fill=(255, 255, 255))
    return im


def save(frames, name):
    frames[0].save(OUT + name, save_all=True, append_images=frames[1:], duration=67, loop=0, optimize=True)
    print(name, os.path.getsize(OUT + name) / 1e6, "MB", len(frames), "frames")


box = (200, 0, 1280, 640)
W, H = 480, 285
fr = []
for i in range(110, 270, 2):
    a = lab(Image.open(S + "movie_b/f%08d.png" % i).convert("RGB").crop(box).resize((W, H), Image.LANCZOS), "r43")
    b = lab(Image.open(S + "movie/f%08d.png" % i).convert("RGB").crop(box).resize((W, H), Image.LANCZOS), "variant")
    f = Image.new("RGB", (W * 2, H))
    f.paste(a, (0, 0))
    f.paste(b, (W, 0))
    fr.append(f.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
save(fr, "traffic_motion.gif")
fr = []
for i in range(110, 230, 2):
    im = lab(Image.open(S + "movie_plan/f%08d.png" % i).convert("RGB").resize((800, 450), Image.LANCZOS), "variant, plan zoom")
    fr.append(im.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
save(fr, "traffic_motion_plan.gif")
