import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
p = "sb_ocjobs.py"
s = open(p, encoding="utf-8").read()
a = s[s.index("LOOK = dict("):s.index("# calibrated on the one-city tests")]
b = '''LOOK = dict(unit_scale=3.0, neon=1.0, win=0.9, panel=4.0, cityglow=900.0, room=60.0, beams=6, beam_rise=1.35, lane_dim=0.5, lane_k=2.5,
            # v3-r3 (art director): beams = an emissive shaft (radial core + soft skirt, gone by 60 % of its length) and
            # one wide soft haze spot; fog 1.3x the v3a field plus coloured mid and ground banks; street-level glows
            beam=6.0e5, beam_cone=30.0, beam_emit=3.0, beam_half=6.0, beam_len=3.5, beam_fade=0.6, beam_efold=0.22,
            beam_core_s=0.13, beam_soft_s=0.42, beam_core_w=1.0, beam_soft_w=0.3, beam_hot=0.5,
            fog_peak=0.0507, wisp_k=1.2, fog_front=7.0, underlight_k=0.07, haze=0.0008, haze_efold=40.0,
            mid_bank=0.035, mid_glow=0.1, gb_top=2.2, ground_bank=0.04, ground_glow=0.06,
            ground_lamp=40.0, ground_glow_step=9.0, ground_glow_depth=60.0, ground_glow_p=0.55,
            step_rate=4.0, lamp=80.0, wash=1500.0)   '''
s = s.replace(a, b)
s = s.replace('''"fm_dive", "fc_test_end")''', '''"fm_dive", "fc_test_end", "fc_t3")''')
s = s.replace('''    elif w == "fc_test_end":''', '''    elif w == "fc_t3":
        # v3-r3 calibration: the street OVERVIEW (walls closed) and the dive frame of the review (f 300), 960 px
        for x in sys.argv[2:]:
            k_, v_ = x.split("=")
            LOOK[k_] = float(v_)
        ov = D["overview"]
        ov["persp"].setdefault("tgt", ov["target"])
        s3, c3, ex3 = full_at(300, D)
        fr = [_fr("T3_ov", ov, SB.T["b4"], [960, 540]), dict(name="T3_0300", persp=dict(c3["persp"]), t=300 / FPS, res=[960, 540],
                                                             zcut=zcut(zoom_of(c3, D)))]
        run(OUTC, [], oc_block("cycles", D, frames=fr, spp=24), "fc_t3")
    elif w == "fc_test_end":''')
open(p, "w", encoding="utf-8").write(s)
