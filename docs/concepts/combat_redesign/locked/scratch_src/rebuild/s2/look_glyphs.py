"""stage 2 scratch: show the card BURN glyph, the atlas flame (placeholder_burn) and state_burning on dark, at 128 px and 24 px."""
import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw
OUT = 'D:/rc_scratch/combat_redesign/locked/rebuild/s2/'
srcs = [('card BURN', 'D:/rc_scratch/combat_redesign/locked/corp/src/glyphs/BURN.png'),
        ('atlas placeholder_burn', 'D:/rc_art/art-pass/docs/concepts/round17_slice_system/glyphs/placeholder_burn.png'),
        ('atlas state_burning', 'D:/rc_art/art-pass/docs/concepts/round17_slice_system/glyphs/state_burning.png')]
sheet = Image.new('RGB', (3 * 300, 360), (20, 22, 30))
d = ImageDraw.Draw(sheet)
for i, (nm, p) in enumerate(srcs):
    g = Image.open(p).convert('RGBA')
    a = g.split()[3] if g.mode == 'RGBA' else g.convert('L')
    if a.getextrema()[1] == 0:
        a = g.convert('L')
    for s, y in ((128, 30), (24, 200), (32, 250)):
        aa = a.resize((s, s), Image.LANCZOS)
        col = Image.new('RGB', (s, s), (255, 176, 0))
        sheet.paste(col, (i * 300 + 20, y), aa)
    d.text((i * 300 + 20, 320), nm, fill=(255, 255, 255))
sheet.save(OUT + 'glyphs.png')
print('ok')
