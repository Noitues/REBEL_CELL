import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import wr_build
import wr2_glyphs
from slicelib import glyph_rgba
from PIL import Image
names = ['WR_PACKET_R', 'WR_PACKET_V', 'WR_WORM_R', 'WR_WORM_V', 'WR_PAYLOAD_R', 'WR_PAYLOAD_V', 'WR_JAMMER_R', 'WR_JAMMER_V', 'WR_RING_R', 'WR_RING_V']
sizes = [16, 20, 28, 37, 44, 70, 160]
sh = Image.new('RGB', (len(sizes) * 100 + 20, len(names) * 100 + 10), (60, 36, 56))
for j, n in enumerate(names):
    x = 10
    for s in sizes:
        g = glyph_rgba(n, s, max(2, int(s * .075)))
        sh.paste(g, (x, 10 + j * 100 + (100 - s) // 2 if s < 100 else 10 + j * 100), g)
        x += 100 if s < 160 else 170
sh.save('D:/rc_scratch/e10_design/wave_rings/out2/gtest.png')
