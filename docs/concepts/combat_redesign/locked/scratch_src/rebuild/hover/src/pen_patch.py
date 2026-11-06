p = 'hv_checks.py'
s = open(p, encoding='utf-8').read()
a = s.index("def check_pencil(M):")
b = s.index("def check_grain(M, rgb, bg):")
s = s[:a] + open('pen_new.txt', encoding='utf-8').read() + s[b:]
s = s.replace("    out['pencil'] = check_pencil(M)\n", "    out['pencil'] = check_pencil(M, rgb)\n", 1)
# grain: exclude every board mark restored on top, and the 1 px resampling edge
s = s.replace("""    top = dil(hand | stick | inset | g(M, 'Z__digits') | g(M, 'Z__labels') | g(M, 'Z__tags') | g(M, 'Z__badges') | g(M, 'Z__hud_labels'), 2)
    core = ndi.binary_erosion(g(M, 'P__L6_wax'), iterations=1) & ~top""", """    top = dil(hand | stick | inset | g(M, 'Z__digits') | g(M, 'Z__labels') | g(M, 'Z__tags') | g(M, 'Z__badges') | g(M, 'Z__tickets') | g(M, 'Z__tape')
              | g(M, 'Z__plates') | g(M, 'Z__leader') | g(M, 'Z__hud_labels') | g(M, 'Y__you') | focus, 2)
    core = ndi.binary_erosion(g(M, 'P__L6_wax'), iterations=1) & ~top""", 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
