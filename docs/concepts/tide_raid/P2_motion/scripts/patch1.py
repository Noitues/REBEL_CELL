s = open('m2.py').read()
s = s.replace("""    colg = col * np.clip(g, 0, 1.6)[:, None] ** .6
""", """    colg = col * np.clip(g, 0, 1.6)[:, None] ** .6
    core = np.clip(1 - np.abs(off) / (hw * .30), 0, 1) * np.clip(g - .55, 0, 1) * 0.55 * (a_t > .5)
    colg = colg * (1 - core[:, None]) + (PAL['WHITE'] * .85 + PAL[R.typ] * .15)[None] * core[:, None]
""")
s = s.replace("fr.sparse(iy, ix, colg * 1.0, a_tot, gh_rgb, gha, gk=gk * np.clip(g, 0, 1.6).mean() if False else gk)",
              "fr.sparse(iy, ix, colg * 1.0, a_tot, gh_rgb, gha, gk=gk, gw=np.clip(g, 0, 1.8))")
s = s.replace("def sparse(self, iy, ix, rgb, a, ghost_rgb=None, ghost_a=None, gk=0.5, corridor=None):",
              "def sparse(self, iy, ix, rgb, a, ghost_rgb=None, ghost_a=None, gk=0.5, corridor=None, gw=None):")
s = s.replace("            em = rgb * vis[:, None] * gk\n", "            em = rgb * vis[:, None] * gk * (1.0 if gw is None else (gw ** 1.5)[:, None])\n")
s = s.replace("gk=0.55, gain_fn=None, ghost_gain=0.8", "gk=1.1, gain_fn=None, ghost_gain=0.8")
s = s.replace("    col = PAL['SLATE'] if hero else PAL['QUIET']", "    col = PAL['SLATE'] * .62 if hero else PAL['QUIET']")
s = s.replace("        P.poly(q, col * sh * .9 + .06, gl_a + .12)", "        P.poly(q, col * sh * .8 + np.array([.02, .03, .10]), gl_a + .10)")
s = s.replace("gl_a = (.30 if hero else .17) * k", "gl_a = (.22 if hero else .15) * k")
s = s.replace("wc = np.clip(col * 1.5 + .35, 0, 1)", "wc = np.clip(PAL['SLATE'] * 1.25 + .28, 0, 1)")
s = s.replace("wp = 1.6 * wire_k", "wp = 2.0 * wire_k")
s = s.replace("    fr.glow_add(PAL[typ][None, None] * ((vis + gh) * .35)[..., None], cx0, cy0)",
              "    fr.glow_add(PAL[typ][None, None] * ((vis + gh) * .6)[..., None], cx0, cy0)\n    if alpha > .05 and halo == 0:\n        glow_disc(fr, (pos[0], pos[1] + 6), 5.5 * scale, PAL[typ], .38 * alpha, gk=0.0, power=1.8)")
open('m2.py', 'w').write(s)
