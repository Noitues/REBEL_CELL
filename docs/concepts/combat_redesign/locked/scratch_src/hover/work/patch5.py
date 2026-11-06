p = 'D:/rc_scratch/combat_redesign/locked/hover/src/hz_core.py'
s = open(p, encoding='utf-8').read()
s = s.replace("# ------------------------------------------------------------------------------------------------ lit mask helpers\n", '''# ------------------------------------------------------------------------------------------------ lit mask helpers
def _annulus_or(self, r0, r1, c=C):
    """lit annulus that ADDS to the mask (hv_lib's version clears the inner disc, which erased earlier lit regions)"""
    s_ = self.ss
    m = Image.new('L', self.im.size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse([(c[0] - r1) * s_, (c[1] - r1) * s_, (c[0] + r1) * s_, (c[1] + r1) * s_], fill=255)
    d.ellipse([(c[0] - r0) * s_, (c[1] - r0) * s_, (c[0] + r0) * s_, (c[1] + r0) * s_], fill=0)
    self.im = ImageChops.lighter(self.im, m)
    self.d = ImageDraw.Draw(self.im)


HL.Lit.annulus = _annulus_or


''', 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
