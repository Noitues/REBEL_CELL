p = 'D:/rc_scratch/combat_redesign/locked/fx_o30/src/o30_publish.py'
s = open(p, encoding='utf-8').read()
a = """    def build(step, w, fp, colors=128):
        frames = []
        for f in files[::step]:
            im = Image.open(jd + f).convert('RGB')
            if im.width != w:
                im = im.resize((w, int(w * 9 / 16)), Image.LANCZOS)
            frames.append(im.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))"""
b = """    def build(step, w, fp, colors=128):
        h = int(w * 9 / 16)
        # one global palette from a montage of 16 frames across the beat (keeps the spot inks saturated, compresses better)
        pick = files[::max(1, len(files) // 16)][:16]
        mont = Image.new('RGB', (w * 4, h * 4))
        for k, f in enumerate(pick):
            mont.paste(Image.open(jd + f).convert('RGB').resize((w, h), Image.LANCZOS), ((k % 4) * w, (k // 4) * h))
        pal = mont.quantize(colors=colors, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
        frames = []
        for f in files[::step]:
            im = Image.open(jd + f).convert('RGB')
            if im.width != w:
                im = im.resize((w, h), Image.LANCZOS)
            frames.append(im.quantize(palette=pal, dither=Image.Dither.NONE))"""
assert a in s; s = s.replace(a, b)
s = s.replace("for step, w, col in ((3, 640, 128), (3, 560, 112), (4, 560, 96), (4, 480, 96), (5, 480, 80)):",
              "for step, w, col in ((3, 640, 192), (3, 640, 128), (3, 560, 128), (4, 560, 96), (4, 480, 96)):")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
