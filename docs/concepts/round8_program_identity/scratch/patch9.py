def edit(p, pairs):
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a)
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8").write(s)
edit("slicelib.py", [
    ("        plate = 1 - o[\"plate\"] * np.exp(-q * 1.6)\n",
     "        plate = 1 - o[\"plate\"] * np.exp(-q * 1.6)\n"
     "        if o.get(\"art\"):  # round 8: a tight, strong plate just under the glyph block, art stays visible around it\n"
     "            q2 = (lat / (ax * 0.8)) ** 2 + ((rho - rho_c) / (ay * 0.74)) ** 2\n"
     "            plate = 1 - 0.84 * np.exp(-(q2 ** 1.6) * 1.3)\n"),
])
edit("icons8.py", [
    ("    gc = np.array(CAT_GLOW[cat], np.float32) / 255\n",
     "    gc = np.array(CAT_GLOW[cat] if ctx.prog != \"NULL\" else (150, 150, 160), np.float32) / 255\n"),
])
edit("make_round8.py", [
    ("    H = 1640\n", "    H = 2280\n"),
    ("                if k == 0:\n                    fp = f_ui(13, b\"Bold Condensed\")",
     "                raw = I.art(n, 130, 0.3)\n"
     "                d.rounded_rectangle([tx + tl.width / 2 - 70, y + tl.height + 26, tx + tl.width / 2 + 70, y + tl.height + 166], radius=10, fill=(16, 14, 22), outline=(60, 60, 72))\n"
     "                paste(im, raw, tx + tl.width / 2 - 65, y + tl.height + 31)\n"
     "                if k == 0:\n                    fp = f_ui(13, b\"Bold Condensed\")"),
    ("            y += 280\n", "            y += 410\n"),
    ('"bold splash art fills each CRT screen behind the white glyph + value (dark plate kept). "',
     '"top: the slice tile as it plays (art behind glyph + value, dark plate kept); below: the raw image. "'),
])
print("ok")
