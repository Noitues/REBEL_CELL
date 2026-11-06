s = open('asm_units.py').read()
a = "            h = hits(u, 'dia', size, side)\n            BADGE_LOG.append(dict(uid=u['id'], kind=u['kind'], badge='warded'"
b = "            h = hits(u, 'dia', size, side)\n            while (h['tag'] + h['tray'] + h['chev'] + h['glyph']) > 0 and size > 8:      # assembly: layout-aware, shrink 1 px until 0 px on tags / tray / chevrons / glyph\n                size -= 1\n                h = hits(u, 'dia', size, side)\n            BADGE_LOG.append(dict(uid=u['id'], kind=u['kind'], badge='warded'"
assert a in s
s = s.replace(a, b)
a = "            h = hits(u, 'disc', size, side)\n            BADGE_LOG.append(dict(uid=u['id'], kind=u['kind'], badge='dead'"
b = "            h = hits(u, 'disc', size, side)\n            while (h['tag'] + h['tray'] + h['chev'] + h['glyph']) > 0 and size > 6:\n                size -= 1\n                h = hits(u, 'disc', size, side)\n            BADGE_LOG.append(dict(uid=u['id'], kind=u['kind'], badge='dead'"
assert a in s
s = s.replace(a, b)
open('asm_units.py','w').write(s)
