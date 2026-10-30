"""Assembles v2/scripts/nr_city.py from nr_scene_v2.py (look kit: materials, icons, street detail) plus nr_city_part.py (real-city layout)."""
base = 'D:/rc_art/art-pass/docs/concepts/netrun_cel/v2/scripts/'
L = open(base + 'nr_scene_v2.py', encoding='utf-8').read().split('\n')
def seg(a, b): return '\n'.join(L[a - 1:b])   # 1-based inclusive
head = seg(1, 152)
kit = seg(233, 420)          # icons, big_sign, sign_board, street_detail
scene = seg(664, 827)         # clear .. mist (world kept)
render = seg(838, 862)        # render_setup
s = head + '\n' + kit + '\n' + scene + '\n' + render + '\n'

def rep(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, 1)

rep("CAMLOC = {'f2': (-75.0, -8.0, 66.0), 'f3': (-6.0, -68.0, 22.0), 'f4': (-8.0, -9.5, 11.0)}[FRAME]", "CAMLOC = [0.0, 0.0, 0.0]\nINK_FIXED = [None]\nXF = [None]  # local->world frame of a facade: (cos, sin, tx, ty, tz)")
rep("def ink_t(cx, cy, cz, k=1.0):\n", "def ink_t(cx, cy, cz, k=1.0):\n    if XF[0]:\n        c_, s_, tx_, ty_, tz_ = XF[0]\n        cx, cy, cz = cx * c_ - cy * s_ + tx_, cx * s_ + cy * c_ + ty_, cz + tz_\n    if INK_FIXED[0] is not None:\n        return max(0.03, INK_FIXED[0] * INK_PX * k)\n")
s = s.replace("INK_JIT = random.Random(99)", "INK_JIT = random.Random(99)\nWS = 1.0", 1)
rep("e.inputs['Strength'].default_value = 0.5", "e.inputs['Strength'].default_value = float(os.environ.get('NR_BODYK', '0.5'))")
rep("u = mn('DIVIDE', u, 0.95); v = mn('DIVIDE', sep.outputs['Z'], 1.25)", "u = mn('DIVIDE', u, 0.95 * WS); v = mn('DIVIDE', sep.outputs['Z'], 1.25 * WS)")
rep("        o = len(self.v)\n        self.v += pts;", "        if XF[0]:\n            c_, s_, tx_, ty_, tz_ = XF[0]\n            pts = [(p_[0] * c_ - p_[1] * s_ + tx_, p_[0] * s_ + p_[1] * c_ + ty_, p_[2] + tz_) for p_ in pts]\n        o = len(self.v)\n        self.v += pts;")
rep("    rz = {'N': 0, 'S': math.pi, 'E': math.pi / 2, 'W': -math.pi / 2}[facing]\n", "    rz = {'N': 0, 'S': math.pi, 'E': math.pi / 2, 'W': -math.pi / 2}[facing]\n    if XF[0]:\n        c_, s_, tx_, ty_, tz_ = XF[0]\n        pos = (pos[0] * c_ - pos[1] * s_ + tx_, pos[0] * s_ + pos[1] * c_ + ty_, pos[2] + tz_); rz += math.atan2(s_, c_)\n")
rep("float(os.environ.get('NR_FOG', '0.0018'))", "float(os.environ.get('NR_FOG', '0.0'))")
rep("    b.inputs['Metallic'].default_value = 0.0", "    b.inputs['Metallic'].default_value = 0.0\n    L.new(at.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = float(os.environ.get('NR_GEMIT', '0.0'))")
# mist placement from globals
rep("ob.scale = (460, 150, 9.0); ob.location = (50, -20, 4.5);", "ob.scale = MIST_BOX[0]; ob.location = MIST_BOX[1];")
s = s.replace("def mist():", "MIST_BOX = [(400, 300, 9.0), (0, 0, 4.5)]\ndef mist():", 1)
s += '\n' + open(base + 'nr_city_part.py', encoding='utf-8').read()
open(base + 'nr_city.py', 'w', encoding='utf-8').write(s)
print('built nr_city.py', len(s))
