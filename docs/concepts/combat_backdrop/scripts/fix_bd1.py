p='bd1_interior.py'
s=open(p,encoding='utf-8').read()
s=s.replace("zb = 3.0\n","zb = 2.45\n")
s=s.replace("x0, y0 = P(-1.1, 0.5, zb)\n    x1, y1 = P(1.1, -0.05, zb)","x0, y0 = P(-1.35, 0.58, zb)\n    x1, y1 = P(1.35, -0.04, zb)")
s=s.replace("cx = (x0 + x1) * 0.62","cx = (x0 + x1) * 0.5")
s=s.replace("xv = math.sin(t * 6.283 * 2.4) * 16","xv = math.sin(t * 6.283 * 2.4) * 22")
s=s.replace("P(-1.7, 0.8, 3.0)], (14, 26, 28, 255))","P(-1.7, 0.8, 3.0)], (14, 26, 28, 255))")
s=s.replace("zs = [2.75, 2.3, 1.85, 1.45, 1.1]","zs = [2.3, 1.9, 1.55, 1.25]")
s=s.replace("cx_, cy_ = P(side * 1.15, -0.62, z)\n            r = F * 0.19 / z\n            h = F * 1.05 / z","cx_, cy_ = P(side * 1.25, -0.62, z)\n            r = F * 0.19 / z\n            h = F * 1.05 / z")
# reflections + haze
s=s.replace("    # a floor-level lime light spill from the tanks","""    # reflections of the tanks in the wet floor
    R_ = layer(W, H)
    for z in zs:
        for side in (-1, 1):
            cx_, cy_ = P(side * 1.25, -0.62, z)
            r = F * 0.19 / z
            for k in range(14):
                a_ = int(70 * (1 - k / 14))
                rect(R_, [cx_ - r * (1 - k * 0.012), cy_ + k * r * 0.28, cx_ + r * (1 - k * 0.012), cy_ + (k + 1) * r * 0.28], fill=(90, 220, 70, a_))
    img.alpha_composite(R_)
    # window haze: cold light from the helix window into the room
    Hz = layer(W, H)
    wx, wy = P(0, 0.3, zb)
    ellipse(Hz, [wx - 520, wy - 140, wx + 520, wy + 330], fill=(150, 235, 190, 70))
    img = glow(img, Hz, 90, 1.0)
    # a floor-level lime light spill from the tanks""")
open(p,'w',encoding='utf-8').write(s)
