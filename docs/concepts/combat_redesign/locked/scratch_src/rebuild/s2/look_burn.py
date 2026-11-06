import sys
sys.dont_write_bytecode = True
from PIL import Image
g = Image.open('D:/rc_scratch/combat_redesign/locked/corp/src/glyphs/BURN.png')
print(g.mode, g.size, g.getextrema())
g.convert('L').resize((128, 128)).save('D:/rc_scratch/combat_redesign/locked/rebuild/s2/burn_card.png')
