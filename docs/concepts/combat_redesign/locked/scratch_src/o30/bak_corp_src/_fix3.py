p='xf_board.py'
s=open(p).read()
s=s.replace("xtext(cv, 'XEROX FLYER', 440, 78,","xtext(cv, 'XEROX FLYER', 330, 78,")
s=s.replace("""sw = [('TONER', (21, 18, 26), 'key plate, ground'), ('SHEET', (242, 238, 228), 'paper, 80% on tower'), ('MAGENTA', (255, 61, 168), 'CELL_PINK: ours'),
      ('CYAN', (18, 169, 230), 'misprint plate only'), ('HARM', (255, 68, 51), 'hatch: enemy'), ('GAIN', (123, 224, 123), 'your HP'), ('SOAK', (58, 126, 243), 'hatch: soak')]""",
"""sw = [('TONER', (21, 18, 26), 'key, ground'), ('SHEET', (242, 238, 228), 'paper'), ('MAGENTA', (255, 61, 168), 'ours'),
      ('CYAN', (18, 169, 230), 'misprint only'), ('HARM', (255, 68, 51), 'enemy hatch'), ('GAIN', (123, 224, 123), 'your HP'), ('SOAK', (58, 126, 243), 'soak hatch')]""")
a=s.index("for nm, xx, yy in (('KEY STROKE")
b=s.index("# ---- big pieces")
s=s[:a]+"""for nm, xx, yy in (('KEY STROKE = OURS', 54, 958), ('TWO RULES = PROTECT', 54, 976), ('HATCH = LOST', 54 + 215, 958), ('AT END TURN', 54 + 215, 976), ('X = SLICE LOST', 54 + 345, 958), ('REG MARK', 54 + 450, 958), ('BURST = OUR HIT', 54 + 545, 958)):
    d.text((xx, yy), nm, font=F('ShareTechMono-Regular.ttf', 13), fill=(160, 170, 190))

"""+s[b:]
a=s.index("d.text((860, 360 + 300)")
b=s.index("im.save(OUT + '../style_board_draft.png')")
s=s[:a]+"""d.text((870, 650), 'CARD A: WHITE SHEET', font=F('ShareTechMono-Regular.ttf', 15), fill=(160, 170, 190))
d.text((1340, 650), 'CARD B: BLACK TONER', font=F('ShareTechMono-Regular.ttf', 15), fill=(160, 170, 190))
sl = bigA.crop((260, 90, 680, 420)).resize((525, 412), Image.LANCZOS)
bg = Image.new('RGBA', sl.size, BGC + (255,))
bg.alpha_composite(sl)
im.paste(bg.convert('RGB'), (850, 672))
d.text((852, 1086 - 20 - 0), '', font=F('ShareTechMono-Regular.ttf', 15), fill=(160, 170, 190))
for k, big in enumerate((bigA, bigB)):
    h = big.crop((330, 330, 610, 610)).resize((250, 250), Image.LANCZOS)
    bg = Image.new('RGBA', h.size, BGC + (255,))
    bg.alpha_composite(h)
    im.paste(bg.convert('RGB'), (1420 + k * 260, 690))
d.text((1420, 950), 'HUB A: RANSOM TILES ON BLACK', font=F('ShareTechMono-Regular.ttf', 14), fill=(160, 170, 190))
d.text((1680, 950), 'HUB B: ON A WHITE DISC', font=F('ShareTechMono-Regular.ttf', 14), fill=(160, 170, 190))
d.text((852, 1090 - 14), '', font=F('ShareTechMono-Regular.ttf', 12), fill=(160, 170, 190))
d.text((1420, 985), 'ONE SLICE (A, LEFT): FLAT MAGENTA, BLACK KEY, HALFTONE SHADE.', font=F('ShareTechMono-Regular.ttf', 14), fill=(160, 170, 190))
d.text((1420, 1008), 'EVERY LETTER OF THE CELL IS CUT FROM A DIFFERENT SCRAP.', font=F('ShareTechMono-Regular.ttf', 14), fill=(160, 170, 190))
"""+s[b:]
open(p,'w').write(s)
