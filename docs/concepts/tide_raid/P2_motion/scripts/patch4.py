import re
def sub(fn, pairs):
    s = open(fn).read()
    for a, b in pairs:
        if a not in s:
            print('MISSING', fn, a)
        s = s.replace(a, b)
    open(fn, 'w').write(s)

sub('scenes.py', [
    ("gain=.42, flow=f * .06))\n    S.beams.append(dict(rid='K3', s0=R3.ext, s1=R3.L - 4, gain=.42", "gain=.80, flow=f * .06))\n    S.beams.append(dict(rid='K3', s0=R3.ext, s1=R3.L - 4, gain=.80"),
    ("gm = 0.55", "gm = 0.90"),
    ("def rest_beams(self, k=0.42", "def rest_beams(self, k=0.85"),
])
sub('scenes2.py', [
    ("S.beams.append(dict(rid='K1', s0=520, s1=route('K1').L - 4, gain=.30, flow=f * .05))\n    S.beams.append(dict(rid='K3', s0=520, s1=route('K3').L - 4, gain=.30, flow=f * .05))",
     "S.beams.append(dict(rid='K1', s0=520, s1=route('K1').L - 4, gain=.65, flow=f * .05))\n    S.beams.append(dict(rid='K3', s0=520, s1=route('K3').L - 4, gain=.65, flow=f * .05))"),
    ("gm = .5 * kr", "gm = .9 * kr"),
    ("gain=(.5 + .8 * t)", "gain=(.9 + .5 * t)"),
    ("gain=.34, flow=f * .05))\n    S.beams.append(dict(rid='K2', s0=520, s1=route('K2').L - 4, gain=.30", "gain=.70, flow=f * .05))\n    S.beams.append(dict(rid='K2', s0=520, s1=route('K2').L - 4, gain=.65"),
    ("S.rest_beams(.30, flow_t=f)", "S.rest_beams(.65, flow_t=f)"),
    ("(('K1', .5), ('K2', .42), ('K3', .42))", "(('K1', .9), ('K2', .8), ('K3', .8))"),
    ("(('K1', .5), ('K2', .42), ('K3', .42))", "(('K1', .9), ('K2', .8), ('K3', .8))"),
    ("    gm = .55\n    S.beams.append(dict(rid='K1', s0=R.ext, s1=s_stop + 20", "    gm = .90\n    S.beams.append(dict(rid='K1', s0=R.ext, s1=s_stop + 20"),
])
sub('boardscenes.py', [
    ("def std_scene(f=0, beams=.5):", "def std_scene(f=0, beams=.85):"),
    ("std_scene(f, beams=.40)", "std_scene(f, beams=.7)"),
    ("std_scene(f, beams=.25)", "std_scene(f, beams=.4)"),
])
sub('m2.py', [
    ("gk=1.1, gain_fn=None", "gk=1.7, gain_fn=None"),
    ("    img = fr if isinstance", "    img = fr if isinstance") if False else ("def resolve(self, glow_gain=1.0):", "def resolve(self, glow_gain=1.45):"),
    ("        img = self.img + up * glow_gain\n", "        img = (self.img + up * glow_gain) * 1.06\n"),
    ("    fr.pl(P, gk=0.9 * ring_k, occ=0.6, k=ring_k)", "    fr.pl(P, gk=1.7 * ring_k, occ=0.6, k=ring_k)"),
    ("glow_disc(fr, c, 18.0, PAL['WARM'], .55 * pool_k, gk=0.0, power=1.4)", "glow_disc(fr, c, 20.0, PAL['WARM'], .85 * pool_k, gk=0.6 * pool_k, power=1.3)"),
    ("    fr.pl(P4, gk=1.0 * (1 + 0.6) * ring_k, occ=0.0)", "    fr.pl(P4, gk=2.4 * ring_k, occ=0.0)"),
    ("    col = PAL['CAGE'] * .6 + .05", "    col = PAL['CAGE'] * .9 + .03"),
    ("    fr.pl(P, gk=.35, k=k)\n\n\ndef glyph", "    fr.pl(P, gk=.7, k=k)\n\n\ndef glyph"),
])
