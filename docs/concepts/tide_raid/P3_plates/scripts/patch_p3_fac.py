s = open('p3_look.py').read()
s = s.replace("hh > 0.74", "hh > 0.80")
s = s.replace("wcol * lit[..., None] * 0.36", "wcol * lit[..., None] * 0.30")
s = s.replace("wcol = np.where(cool[..., None], ICE[None, None], SOD[None, None]) * (0.55 + 0.9 * _h(cu, cf, 9)[..., None])",
              "wcol = np.where(cool[..., None], ICE[None, None], SOD[None, None]) * (0.6 + 0.5 * _h(cu, cf, 9)[..., None])")
s = s.replace("        # lit atrium:", """        # continuous light strip on every 7th floor (a real facade feature, reads as architecture at 320 px)
        strip = ((np.mod(cf, 7) == 3) & (ff > 0.40) & (ff < 0.62)).astype(np.float32)
        e = e + ICE[None, None] * (strip * 0.55)[..., None]
        # lit atrium:""")
open('p3_look.py', 'w').write(s)
