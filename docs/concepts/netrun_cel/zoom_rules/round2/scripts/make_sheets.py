"""Builds the round-1 deliverables from the capture folders. Usage: python -P make_sheets.py <cmd> ...
cmds:
  squint <in> <out>                       1/16 area reduction + blur, back up to 960x540
  refvs <plate> <ours> <out>              plate | ours at 960 wide each
  strip <dir> <out>                       zoom_strip: five stages, layers on (top), off (bottom)
  ba <out> <label1> <img1> <label2> <img2> [crop x0 y0 x1 y1]   before / after side by side (optional crop box, 1920x1080 coords)
  gif <dir> <out> <fps> <width>           dolly_*.jpg -> gif
"""
import sys
import glob
from PIL import Image, ImageFilter, ImageDraw


def squint(src, out):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    small = im.resize((w // 4, h // 4), Image.BOX).filter(ImageFilter.GaussianBlur(1.0))
    small.resize((960, 540), Image.BICUBIC).save(out)


def refvs(plate, ours, out):
    a = Image.open(plate).convert("RGB").resize((960, 540), Image.LANCZOS)
    b = Image.open(ours).convert("RGB").resize((960, 540), Image.LANCZOS)
    s = Image.new("RGB", (1920, 540))
    s.paste(a, (0, 0))
    s.paste(b, (960, 0))
    d = ImageDraw.Draw(s)
    d.text((8, 6), "plate: street_overview", fill=(255, 255, 255))
    d.text((968, 6), "ours: street frame (round 2)", fill=(255, 255, 255))
    s.save(out, quality=90)


def strip(folder, out):
    names = ["city", "x2", "district", "near-street", "street"]
    s = Image.new("RGB", (1920, 432))
    for i in range(5):
        for row, kind in enumerate(["layers", "base"]):
            im = Image.open("%s/stage_%d_%s.png" % (folder, i + 1, kind)).convert("RGB").resize((384, 216), Image.LANCZOS)
            s.paste(im, (i * 384, row * 216))
        ImageDraw.Draw(s).text((i * 384 + 6, 4), "%d %s (rules on)" % (i + 1, names[i]), fill=(255, 255, 255))
        ImageDraw.Draw(s).text((i * 384 + 6, 220), "%d %s (rules off)" % (i + 1, names[i]), fill=(255, 255, 255))
    s.save(out, quality=90)


def ba(out, l1, p1, l2, p2, box=None):
    a = Image.open(p1).convert("RGB")
    b = Image.open(p2).convert("RGB")
    if box:
        a = a.crop(box)
        b = b.crop(box)
    w = 960
    h = int(w * a.height / a.width)
    s = Image.new("RGB", (w * 2, h))
    s.paste(a.resize((w, h), Image.LANCZOS), (0, 0))
    s.paste(b.resize((w, h), Image.LANCZOS), (w, 0))
    d = ImageDraw.Draw(s)
    d.text((8, 6), l1, fill=(255, 255, 255))
    d.text((w + 8, 6), l2, fill=(255, 255, 255))
    s.save(out, quality=90)


def gif(folder, out, fps, width):
    files = sorted(glob.glob(folder + "/dolly_*.jpg"))
    frames = []
    for f in files:
        im = Image.open(f).convert("RGB")
        im = im.resize((width, int(width * im.height / im.width)), Image.LANCZOS)
        frames.append(im.quantize(colors=128, method=Image.MEDIANCUT, dither=Image.NONE))
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0, optimize=True)
    print("frames", len(frames))


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "squint":
        squint(sys.argv[2], sys.argv[3])
    elif c == "refvs":
        refvs(sys.argv[2], sys.argv[3], sys.argv[4])
    elif c == "strip":
        strip(sys.argv[2], sys.argv[3])
    elif c == "ba":
        box = tuple(int(x) for x in sys.argv[7:11]) if len(sys.argv) >= 11 else None
        ba(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], box)
    elif c == "gif":
        gif(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
