p = 'hv_core.py'
s = open(p, encoding='utf-8').read()
a = s.index("RING = {'turns': 1.07, 'drift': 0.03}")
b = s.index("def you_pip_x(i):")
new = open('ring_new.txt', encoding='utf-8').read()
s = s[:a] + new + '\n\n' + s[b:]
s = s.replace("HERO_ROOM_T = 10       #", "HERO_ROOM_T = 17       #", 1)
s = s.replace("HERO_ROOM_B = 14       #", "HERO_ROOM_B = 21       #", 1)
s = s.replace("HERO_GAP = 24          #", "HERO_GAP = 28          #", 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
