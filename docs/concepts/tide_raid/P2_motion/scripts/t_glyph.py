from m2 import *
im = Image.new('RGB', (600, 120), (40, 40, 60))
P = Pl((0, 0, 600, 120))
for i, k in enumerate(['UNTOUCHED', 'HOLDS', 'SITES_LOST', 'DAMAGED', 'BREACHED']):
    glyph(P, k, (60 + i * 110, 60), 50, PAL['WARM'])
a, al = P.arrays()
arr = np.asarray(im, np.float32) / 255
arr = arr * (1 - al[..., None]) + a * al[..., None]
Image.fromarray(u8(arr)).resize((1200, 240)).save('D:/rc_scratch/tide_concepts/p2m_work/glyphs.png')
