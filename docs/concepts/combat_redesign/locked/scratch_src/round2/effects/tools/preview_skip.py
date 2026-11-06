"""preview_skip.py: the SKIP tab composited on the published p3 (look only) -> work/look/skip_preview.png (1x crop) and _x3.png (zoomed)"""
from PIL import Image
P = Image.open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/p3_resolve.png').convert('RGBA')
T = Image.open('D:/rc_scratch/combat_redesign/locked/round2/effects/fx_mpst/work/skip_tab.png').convert('RGBA')
P.alpha_composite(T)
c = P.crop((1100, 600, 1920, 760)).convert('RGB')
c.save('D:/rc_scratch/combat_redesign/locked/round2/effects/work/look/skip_preview.png')
z = P.crop((1690, 655, 1905, 715)).convert('RGB')
z.resize((z.width * 4, z.height * 4), Image.NEAREST).save('D:/rc_scratch/combat_redesign/locked/round2/effects/work/look/skip_preview_x4.png')
