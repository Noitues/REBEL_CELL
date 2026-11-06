p = 'hv_core.py'
s = open(p, encoding='utf-8').read()
anchor = "HL.pencil = pencil\n"
assert anchor in s
s = s.replace(anchor, '''def done_box(L):
    """the hover marks layer to 1x with a BOX filter (2 x 2 supersampling): LANCZOS rings at the wax / ink edge and lifts the wax above its
    pigment (PLAN G 226 read up to 239); BOX keeps every wax pixel at or under PLAN, so the grain only darkens"""
    return L.im.resize((W, H), Image.BOX)


''' + anchor, 1)
open(p, 'w', encoding='utf-8').write(s)
p = 'hv_plates.py'
s = open(p, encoding='utf-8').read()
n0 = s.count('Lm.done()') + s.count('Lx.done()')
s = s.replace("top.append(Lx.done())", "top.append(V.done_box(Lx))")
s = s.replace("img = K.compose(bg, mask, ghosts, [Lm.done()], hand_lay, stick, insets=ins_layers, top=top)", "img = K.compose(bg, mask, ghosts, [V.done_box(Lm)], hand_lay, stick, insets=ins_layers, top=top)")
s = s.replace("    img.alpha_composite(Lm.done())\n    cr = img.convert('RGB').crop(crop)", "    img.alpha_composite(V.done_box(Lm))\n    cr = img.convert('RGB').crop(crop)")
open(p, 'w', encoding='utf-8').write(s)
print('ok', n0, s.count('done_box'), s.count('Lm.done()'))
