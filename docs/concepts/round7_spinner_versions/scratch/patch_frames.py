p = "slicelib.py"
s = open(p, encoding="utf-8").read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)
rep("""    gap = 1.6 * ss
    bw = 8.5 * ss
""", """    fr = o.get("frame")
    gap = (3.2 if fr == "v3" else 1.6) * ss
    bw = (13.0 if fr == "v3" else 11.0 if fr == "v1" else 8.5) * ss
""")
rep("""    e_in = rho - Ri - gap
""", """    e_in = rho - Ri - gap
    lat = rho * np.radians(d)
    if fr == "v1":  # round 7 V1: program cartridge silhouettes
        if prog == "FIREWALL":  # brick-toothed outer edge
            tooth = ((lat / (16 * ss)) % 1.0) < 0.5
            e_out = e_out - np.where(tooth, 0.0, 6 * ss)
            e_in = e_in - np.where(((lat / (16 * ss) + 0.5) % 1.0) < 0.5, 0.0, 4 * ss)
        elif prog == "VIRUS":  # organic, cell-like edge
            wob = 2.8 * ss * (np.sin(lat / (8 * ss)) + 0.7 * np.sin(rho / (6 * ss) + 1.3)) - 1.5 * ss
            e_side = e_side + wob
            e_out = e_out + wob
            e_in = e_in + wob
        elif prog == "EXPLOIT":  # cracked, jagged edge
            saw = (lat / (13 * ss)) % 1.0
            e_out = e_out - 7 * ss * np.abs(saw - 0.5) * 2
            e_side = e_side - 4 * ss * np.abs(((rho / (11 * ss)) % 1.0) - 0.5) * 2
""")
rep("""    else:
        base = np.array([0.15, 0.16, 0.18], np.float32)
        hair = c01(MERIDIAN)
    light = 0.85 + 0.3 * np.cos(np.radians(th - 315))  # key light top-left
    bez = base[None, None, :] * light[..., None]
    lip = np.exp(-(e_tile / (1.2 * ss)) ** 2) * 0.22  # outer lip catch-light
    bez = bez + lip[..., None]
    shadow = smooth(-5 * ss, 0, e_scr)  # inner bevel shadow toward the screen
    bez *= (1 - 0.6 * shadow)[..., None]
""", """    else:
        base = np.array([0.15, 0.16, 0.18], np.float32)
        hair = c01(MERIDIAN)
    light = 0.85 + 0.3 * np.cos(np.radians(th - 315))  # key light top-left
    if fr == "v1":  # cartridge shell moulded in the program colour
        base = c01(col) * 0.30 + 0.035
    if fr == "v3":  # anodised metal housing per program, brushed, strong bevel
        rngb = np.random.default_rng(11)
        brush = (rngb.random(2048).astype(np.float32) * 0.06)[(th * 5.6).astype(np.int32) % 2048]
        base = c01(col) * 0.38 + 0.07
        light = 0.65 + 0.6 * np.cos(np.radians(th - 315))
    bez = base[None, None, :] * light[..., None]
    if fr == "v3":
        bez = bez + brush[..., None]
    lip = np.exp(-(e_tile / (1.2 * ss)) ** 2) * (0.45 if fr == "v3" else 0.22)  # outer lip catch-light
    bez = bez + lip[..., None]
    shadow = smooth(-5 * ss, 0, e_scr)  # inner bevel shadow toward the screen
    bez *= (1 - (0.85 if fr == "v3" else 0.6) * shadow)[..., None]
""")
rep("""    rgb = scr * a_scr[..., None] + bez * (1 - a_scr[..., None])
    a = a_tile[..., None]
""", """    if fr == "v1" and prog == "ZERO-DAY":  # glowing seal: the whole shell burns
        halo = np.exp(-(np.maximum(-e_scr, 0) / (6 * ss)) ** 2)
        bez = bez + halo[..., None] * np.array([1.0, 0.55, 0.85], np.float32)[None, None] * 0.9
    rgb = scr * a_scr[..., None] + bez * (1 - a_scr[..., None])
    if fr == "v1" and prog == "NULL":  # broken, unplugged frame: chunks of shell missing
        brk = ((((lat / (34 * ss)) + 0.35) % 1.0) < 0.22) & (e_scr < 0) & ((rho > Ro - bw - gap - 2 * ss) | (rho < Ri + bw + gap))
        a_tile = np.where(brk, 0.0, a_tile)
    a = a_tile[..., None]
""")
open(p, "w", encoding="utf-8").write(s)
print("ok")
