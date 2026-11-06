import re
p='xf_gfx.py'
s=open(p).read()
s=s.replace("out = [(c[0] + r1 * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))), c[1] + r1 * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1)))) for i in range(n)]",
"out = [(c[0] + r1 * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1))), c[1] - r1 * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1)))) for i in range(n)]")
s=s.replace("inn = [(c[0] + r0 * math.cos(math.radians(a1 + (a0 - a1) * i / (n - 1))), c[1] + r0 * math.sin(math.radians(a1 + (a0 - a1) * i / (n - 1)))) for i in range(n)]",
"inn = [(c[0] + r0 * math.sin(math.radians(a1 + (a0 - a1) * i / (n - 1))), c[1] - r0 * math.cos(math.radians(a1 + (a0 - a1) * i / (n - 1)))) for i in range(n)]")
open(p,'w').write(s)
p='xf_tower.py'
s=open(p).read()
s=s.replace("PAGE_V = 0.74","PAGE_V = 0.80")
s=s.replace("def render_tower(f, name='BREAKER', S=3,","def render_tower(f, name='BREAKER', S=int(__import__('os').environ.get('XF_SS', '3')),")
s=s.replace("hf = hatch_cached(cv, (45, 135), 5.4, 1.9, 77)\n        cv.paint(hf * reg, col, 0.96)","hf = hatch_cached(cv, (45, 135), 6.0, 1.7, 77)\n        cv.paint(hf * reg, col, 0.9)")
open(p,'w').write(s)
