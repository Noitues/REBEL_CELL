def grade_pre(bare, P):
    """steps 1-5 of the grade (hull, blur ramp, corp light, chroma, contrast, value) plus the local-mean luma the tone step needs.
    Independent of tone_lo / tone_hi / knee / ceil / haze, so a solver can cache it.  Returns (a 0-1, m, d, lb or None)."""
    P = dict(BASE, **P)
    m, d = hull(P)
    m3 = m[..., None]
    if P.get('mid_blur') is not None:
        # 2026-11-03 (rb2) seam: one blur ramp instead of a sharp / blurred cross-fade (no double-image band where the city meets the room):
        # hull_blur inside, mid_blur at the middle of the edge band, city_blur beyond it; smoothsteps on the hull sdf (or the ellipse d)
        if P.get('hull_poly'):
            q, e0, e1 = poly_sdf(P['hull_poly']), -P['pf0'], P['pf1'] + P.get('blur_reach', 0.0)
        else:
            q, e0, e1 = d, P['f0'], P['f1']
        fm = 0.5 * (e0 + e1)
        s1 = smooth(e0, fm, q)[..., None]
        s2 = smooth(fm, e1, q)[..., None]
        a = (blur(bare, P['hull_blur']) * (1 - s1) + blur(bare, P['mid_blur']) * s1) * (1 - s2) + blur(bare, P['city_blur']) * s2
    else:
        a = blur(bare, P['hull_blur']) * m3 + blur(bare, P['city_blur']) * (1 - m3)
    a = a / 255.0
    a = corp_light(a, P)
    # chroma
    mx, mn = a.max(-1), a.min(-1)
    S = (mx - mn) / np.maximum(mx, 1e-4)
    neon = (smooth(0.35, 0.60, S) * smooth(0.35, 0.65, mx))[..., None]
    k = P['chroma'] * (1 - (1 - P['neon_chroma']) * neon) * (1 - (1 - P['pink_chroma']) * pinkw(a)[..., None])
    if P.get('city_chroma') is not None:
        # 2026-11-03 (rb2) seam: the city outside the hull keeps city_chroma of its chroma, so the violet / mauve facades next to the room do not
        # read as a second picture; the room's light (spill haze, step 7) then tints that calmer street
        k = k * (m3 + P['city_chroma'] * (1 - m3))
    l = luma(a)[..., None]
    a = l + (a - l) * k
    # contrast
    a = P['pivot'] + (a - P['pivot']) * P['contrast']
    a = np.clip(a, 0, None)
    # value
    a = a * (P['hull_value'] * m3 + P['city_value'] * (1 - m3))
    lb = None
    if P.get('tone_hi'):
        from scipy.ndimage import gaussian_filter
        lb = gaussian_filter(luma(a).astype(np.float32), P['tone_blur'])
    return a, m, d, lb


def grade_post(pre, P):
    """steps 5b-8 of the grade on grade_pre's output"""
    P = dict(BASE, **P)
    a, m, d, lb = pre
    # 2026-11-03 (rb2): local tone (a dodge).  The gain comes from the LOCAL mean luma (gaussian tone_blur px), not the pixel's own luma, so
    # dark areas of the room come up by multiplication and keep their ink lines and their relative detail; bright areas come down the same
    # way.  target(x) = tone_lo + (tone_hi - tone_lo) * (1 - exp(-x / tone_s)); gain = target / x, capped at tone_gmax; full in the hull,
    # tone_out of it in the city out to hull distance tone_d0..tone_d1.  One extra blurred-luma pass in a shader.
    if lb is not None:
        tgt = P['tone_lo'] + (P['tone_hi'] - P['tone_lo']) * (1 - np.exp(-lb / P['tone_s']))
        g = np.clip(tgt / np.maximum(lb, 1e-4), 0.0, P['tone_gmax'])
        reach = 1 - smooth(P.get('tone_d0', 9.0), P.get('tone_d1', 10.0), d)
        g = 1 + (g - 1) * (m + P.get('tone_out', 0.0) * (1 - m) * reach)
        a = a * g[..., None]
    # highlight shoulder on luma
    kn, ce = P['knee'], P['ceil']
    if kn < ce:
        l = luma(a)
        span = ce - kn
        l2 = np.where(l > kn, kn + span * (1 - np.exp(-(l - kn) / span)), l)
        a = a * (l2 / np.maximum(l, 1e-4))[..., None]
    # haze
    hz = np.array(P['haze_rgb'], np.float32) / 255.0
    if P.get('haze_out') is not None:
        # 2026-11-03 (rb2) seam: the haze amount ramps from haze (room) to haze_out (city) with the hull weight, and its colour is the room's
        # own light (spill_rgb) at the hull and the night haze (haze_rgb) from d = sp0 to sp1, so the room's light carries into the street
        # round it and the city meets the room through one atmosphere
        hk = (P['haze'] * m + P['haze_out'] * (1 - m))[..., None]
        sp = np.array(P['spill_rgb'], np.float32) / 255.0
        ws = smooth(P['sp0'], P['sp1'], d)[..., None]
        hz = sp * (1 - ws) + hz * ws
        a = a * (1 - hk) + hz * hk
    else:
        a = a * (1 - P['haze']) + hz * P['haze']
    # vignette + board falloff
    v = (1 - P['vignette'] * smooth(P['v0'], P['v1'], d)) * (1 - P['board_falloff'] * (1 - smooth(P['bx0'], P['bx1'], XX)))
    a = a * v[..., None]
    return np.clip(a * 255.0, 0, 255)


def grade(bare, P):
    return grade_post(grade_pre(bare, P), P)
