import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
p = "sb_ocfull.py"
s = open(p, encoding="utf-8").read()


def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b)


rep('''STREET_POST = dict(exposure=float(os.environ.get("OC_EXPOSURE", "0.83")))     # v3-r3: 1.1 -> 0.83 for the denser, lit fog; value-checked on the holds''',
    '''STREET_POST = dict(exposure=float(os.environ.get("OC_EXPOSURE", "0.84")))     # v3-r3: 1.1 -> 0.84 for the denser, lit fog (the near shots)
# v3-r3: the street grade by zoom. The OVERVIEW (and the dive that lands on it) sees the most fog and the lit ground bank,
# so it is graded down to EXP_OV; the near shots (decision, hovers) keep STREET_POST; the zoom move eases between them.
# Value-checked on the held shots (median 0.12-0.13, 35-39 % under 0.10)
EXP_OV = float(os.environ.get("OC_EXP_OV", "0.77"))


def exp_for(f):
    s_, c_, ex_ = seg(f)
    if s_ in ("ov", "dive"):
        return EXP_OV
    if s_ == "zoom":
        return EXP_OV + (STREET_POST["exposure"] - EXP_OV) * ex_.get("u", 0.0)
    return STREET_POST["exposure"]''')
rep('''    o = dict(STREET_POST)
    return PA.finish(C, "real", shot=base, t=t, inp=inp, over=o)''', '''    o = dict(STREET_POST, exposure=exp_for(f))
    return PA.finish(C, "real", shot=base, t=t, inp=inp, over=o)''')
rep('''        pl = finish_name(nm, t).resize((1920, 1080), Image.LANCZOS)''', '''        pl = finish_name(nm, t, dict(exposure=exp_for(f))).resize((1920, 1080), Image.LANCZOS)''')
rep('''        o["exposure"] = o.get("exposure", 2.0) + (STREET_POST["exposure"] - 2.4) * OJ.look_w(z)''',
    '''        o["exposure"] = o.get("exposure", 2.0) + (EXP_OV - 2.4) * OJ.look_w(z)''')
open(p, "w", encoding="utf-8").write(s)
