p='D:/rc_scratch/combat_redesign/locked/fx_o30b/cdhl/src/fxk_lib.py'
s=open(p).read()
s=s.replace("    def done(self):","""    def erase_circle(self, cx, cy, r):
        m = Image.new('L', self.im.size, 255)
        s = self.ss
        x, y = (cx - self.x0) * s, (cy - self.y0) * s
        ImageDraw.Draw(m).ellipse([x - r * s, y - r * s, x + r * s, y + r * s], fill=0)
        a = np.asarray(self.im).copy()
        a[:, :, 3] = (a[:, :, 3].astype(np.float32) * np.asarray(m) / 255).astype(np.uint8)
        self.im = Image.fromarray(a, 'RGBA')

    def done(self):""")
open(p,'w').write(s)
p='D:/rc_scratch/combat_redesign/locked/fx_o30b/cdhl/src/fx_cdhl.py'
s=open(p).read()
s=s.replace("""    # the unit token stays readable: its disc is redrawn clear of the flames by masking (never over the icon)
    if t >= 330 or red:""","""    for (x, y) in FW_TOK:                      # never over a unit token: the flames are cut clear of the disc
        lay.erase_circle(x, y, 31)
    if t >= 330 or red:""")
open(p,'w').write(s)
