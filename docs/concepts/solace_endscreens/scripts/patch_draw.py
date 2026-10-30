p='ui_lib.py'
s=open(p,encoding='utf-8').read()
old="""def draw(img):
    return ImageDraw.Draw(img, 'RGBA')
"""
new='''class BD:
    """ImageDraw wrapper that alpha-blends translucent fills/outlines onto RGBA images (plain ImageDraw replaces)."""

    def __init__(self, img):
        self.img = img
        self.d = ImageDraw.Draw(img)

    @staticmethod
    def _tr(c):
        return isinstance(c, tuple) and len(c) == 4 and c[3] < 255

    @staticmethod
    def _flat(xy):
        out = []
        for v in xy:
            if isinstance(v, (tuple, list)):
                out.extend(v)
            else:
                out.append(v)
        return out

    def _shift(self, xy, dx, dy):
        if isinstance(xy[0], (tuple, list)):
            return [(p[0] - dx, p[1] - dy) for p in xy]
        return [v - (dx if i % 2 == 0 else dy) for i, v in enumerate(xy)]

    def _blend(self, method, xy, pad, kwargs):
        f = self._flat(xy)
        xs, ys = f[0::2], f[1::2]
        x0 = max(0, int(min(xs) - pad)); y0 = max(0, int(min(ys) - pad))
        x1 = min(self.img.width, int(max(xs) + pad) + 1); y1 = min(self.img.height, int(max(ys) + pad) + 1)
        if x1 <= x0 or y1 <= y0:
            return
        box = (x0, y0, x1, y1)
        crop = self.img.crop(box)
        lay = Image.new('RGBA', crop.size, (0, 0, 0, 0))
        getattr(ImageDraw.Draw(lay), method)(self._shift(xy, x0, y0), **kwargs)
        crop.alpha_composite(lay)
        self.img.paste(crop, (x0, y0))

    def _any_tr(self, kw):
        return any(self._tr(kw.get(k)) for k in ('fill', 'outline', 'stroke_fill'))

    def _shape(self, method, xy, **kw):
        if self._any_tr(kw):
            self._blend(method, xy, int(kw.get('width', 1) or 1) + 3, kw)
        else:
            getattr(self.d, method)(xy, **kw)

    def line(self, xy, **kw): self._shape('line', xy, **kw)
    def polygon(self, xy, **kw): self._shape('polygon', xy, **kw)
    def ellipse(self, xy, **kw): self._shape('ellipse', xy, **kw)
    def rectangle(self, xy, **kw): self._shape('rectangle', xy, **kw)
    def rounded_rectangle(self, xy, **kw): self._shape('rounded_rectangle', xy, **kw)
    def arc(self, xy, start, end, **kw): self._shape('arc', xy, start=start, end=end, **kw)

    def text(self, xy, s, **kw):
        if self._any_tr(kw):
            bb = self.d.textbbox(xy, s, font=kw.get('font'), anchor=kw.get('anchor'), stroke_width=kw.get('stroke_width', 0))
            pad = 4
            x0, y0 = max(0, int(bb[0]) - pad), max(0, int(bb[1]) - pad)
            x1, y1 = min(self.img.width, int(bb[2]) + pad), min(self.img.height, int(bb[3]) + pad)
            crop = self.img.crop((x0, y0, x1, y1))
            lay = Image.new('RGBA', crop.size, (0, 0, 0, 0))
            ImageDraw.Draw(lay).text((xy[0] - x0, xy[1] - y0), s, **kw)
            crop.alpha_composite(lay)
            self.img.paste(crop, (x0, y0))
        else:
            self.d.text(xy, s, **kw)

    def multiline_text(self, xy, s, **kw):
        self.d.multiline_text(xy, s, **kw)


def draw(img):
    return BD(img)
'''
assert old in s
s=s.replace(old,new)
open(p,'w',encoding='utf-8').write(s)
