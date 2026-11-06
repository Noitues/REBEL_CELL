from PIL import Image
g = Image.open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/effects/resolve_beat.gif')
print('frames', g.n_frames, g.size, g.info.get('duration'))
ims = []
for k in (20, 60, 100, 140, 180):
    g.seek(k); ims.append(g.convert('RGB').copy())
sh = Image.new('RGB', (g.size[0] * 3, g.size[1] * 2))
for i, im in enumerate(ims):
    sh.paste(im, ((i % 3) * g.size[0], (i // 3) * g.size[1]))
sh.save('D:/rc_scratch/combat_redesign/locked/fx_o30/work/gif_peek.jpg', quality=90)
tot = 0
for k in range(g.n_frames):
    g.seek(k); tot += g.info.get('duration', 0)
print('total ms', tot)
