"""traffic_motion.gif: r43 (left) | variant (right), the downtown close-up (zoom 5 at lot -57,3), Movie Maker frames at 30 fps, every 2nd frame = 15 fps, 5.3 s, from frame 110 (the close-up camera is up), cropped to the street side. Run by path."""
import os
from PIL import Image, ImageDraw
S = "D:/rc_scratch/traffic/"
out = "D:/rc_art/art-pass/docs/concepts/tide_raid/variants/traffic_corp/traffic_motion.gif"
box = (0, 0, 800, 720)
W, H = 400, 360


def lab(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 + 7 * len(t), 16), fill=(8, 8, 20))
    d.text((4, 3), t, fill=(255, 255, 255))
    return im


frames = []
for i in range(110, 270, 2):
    a = lab(Image.open(S + "movie_b/f%08d.png" % i).convert("RGB").crop(box).resize((W, H), Image.LANCZOS), "r43")
    b = lab(Image.open(S + "movie/f%08d.png" % i).convert("RGB").crop(box).resize((W, H), Image.LANCZOS), "variant")
    f = Image.new("RGB", (W * 2, H))
    f.paste(a, (0, 0))
    f.paste(b, (W, 0))
    frames.append(f.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
frames[0].save(out, save_all=True, append_images=frames[1:], duration=67, loop=0, optimize=True)
print(os.path.getsize(out) / 1e6, "MB", len(frames), "frames")
