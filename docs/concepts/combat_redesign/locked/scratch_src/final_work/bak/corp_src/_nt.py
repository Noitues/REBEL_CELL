from PIL import Image
OUT = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/final/'
im = Image.open(OUT + 'p2_preview.png').convert('RGB')
s = im.resize((320, 180), Image.LANCZOS)
sh = Image.new('RGB', (1920, 700), (10, 12, 20))
sh.paste(s.resize((960, 540), Image.NEAREST), (0, 0))
c = im.crop((560, 420, 760, 560)).resize((600, 420), Image.LANCZOS); sh.paste(c, (980, 0))
c2 = im.crop((1260, 195, 1560, 245)).resize((900, 150), Image.LANCZOS); sh.paste(c2, (980, 440))
c3 = im.crop((880, 330, 1000, 420)).resize((360, 270), Image.LANCZOS); sh.paste(c3, (1600, 0))
sh.save(OUT + 'checks_soak_notch.jpg', quality=90)
