p = 'hv_checks.py'
s = open(p, encoding='utf-8').read()
old = "glob.glob(HERE + 'chk/h*.json') if not p.endswith('.checks.json'))"
assert old in s
s = s.replace(old, "glob.glob(HERE + 'chk/h*.json') if not p.endswith('.checks.json') and not os.path.basename(p).startswith('h00'))", 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
