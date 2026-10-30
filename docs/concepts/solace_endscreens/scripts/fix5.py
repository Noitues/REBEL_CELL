p='d2_city.py'
s=open(p,encoding='utf-8').read()
s=s.replace("shift=0.40, sat=1.0, val=1.12","shift=0.215, sat=1.0, val=1.12")
s=s.replace("""    d = np.sqrt((xx - BASE[0]) ** 2 + ((yy - BASE[1]) * 1.5) ** 2)
    n = noise(5, 14)
    rad = 330 + (1 - p) * 900   # infection stops at this radius (the lime island)
    infected = (d + (n - 0.5) * 220) > rad""","""    d = np.sqrt((xx - 1400) ** 2 + ((yy - 870) * 1.5) ** 2)
    ax, ay, bx, by = 1450, 170, 1420, 860
    t_ = np.clip(((xx - ax) * (bx - ax) + (yy - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2), 0, 1)
    dseg = np.sqrt((xx - (ax + t_ * (bx - ax))) ** 2 + (yy - (ay + t_ * (by - ay))) ** 2)
    n = noise(5, 14)
    rad = 380 + (1 - p) * 900
    dd_ = np.minimum(d / rad * 300, dseg * 1.0 * 300 / 215)   # island radius ~ 300 in this metric
    infected = (dd_ + (n - 0.5) * 120) > 300
    d = np.minimum(d, dseg * 1.9)""")
s=s.replace("rng.uniform(0, 1920, 1500), rng.uniform(0, 1080, 1500)","rng.uniform(0, 1920, 5200), rng.uniform(0, 1080, 5200)")
s=s.replace("< 3.2).reshape","< 2.4).reshape").replace("< 1.4).reshape","< 1.1).reshape")
s=s.replace("base = a * (1 - inf_soft[..., None] * 0.55)","base = a * (1 - inf_soft[..., None] * 0.35)")
s=s.replace("base = base + inf_soft[..., None] * tint * 0.55","base = base + inf_soft[..., None] * tint * 0.45")
s=s.replace("isl = np.exp(-(np.maximum(d - rad * 0.55, 0) / 160) ** 2) * (1 - inf_soft)","isl = (1 - inf_soft)")
s=s.replace("(1620, 1032))\n    return img\n\n\nif","(1620, 1032))\n    return img\n\n\nif")
open(p,'w',encoding='utf-8').write(s)
