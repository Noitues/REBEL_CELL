"""element-list omission audit.  Runs the 5 assembled renders under a call profile, then walks every element row of DECISIONS.md section 3 and
checks that at least one of the functions named in the row was really called while drawing (FINAL rows), or exists in the source (LATENT rows).
Writes out/coverage.json."""
import sys, os, re, json, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
called = set()


def prof(frame, event, arg):
    if event == 'call':
        fn = frame.f_code.co_filename
        if fn.startswith(HERE) or HERE.replace('\\', '/') in fn.replace('\\', '/'):
            called.add(frame.f_code.co_name)


import asm_r2 as A
A.setup()
t = time.time()
sys.setprofile(prof)
for b in ['p1', 'p2', 'p2b', 'p3', 'nowords']:
    A.render(b, check=False)
sys.setprofile(None)
print('rendered', round(time.time() - t))

src_names = set()
for fn in os.listdir(HERE):
    if fn.endswith('.py'):
        s = open(os.path.join(HERE, fn), encoding='utf-8', errors='ignore').read()
        src_names.update(re.findall(r'^\s*def\s+(\w+)', s, re.M))

dec = open('D:/rc_art/art-pass/docs/concepts/combat_e10_design/DECISIONS.md', encoding='utf-8').read()
sec = dec[dec.index('## 3. Final per element'):dec.index('## 4. Cohesion check')]
rows = []
for line in sec.splitlines():
    if not line.startswith('|') or line.startswith('|---') or line.startswith('| Element'):
        continue
    cells = [c.strip() for c in line.strip().strip('|').split('|')]
    if len(cells) < 3:
        continue
    el = cells[0]
    if not re.match(r'^[a-z0-9_]+$', el):
        continue
    rows.append((el, cells))

STOP = {'A', 'B', 'C', 'P', 'V', 'R', 'E', 'kglyph2', 'hud2', 'obj2', 'kscene2', 'kcard2', 'wc2', 'wr2_lib', 'e10', 'NOW', 'words', 'asm_tokens'}
res = {}
for el, cells in rows:
    txt = ' '.join(cells[1:])
    status = 'FINAL'
    low = txt.lower()
    if 'retired' in low or 'final removed' in low or 'final none' in low or 'removed' in cells[1].lower() or cells[1].lower().startswith('final none') or ' (none)' in low:
        status = 'REMOVED'
    elif 'latent' in low or cells[1].lower().startswith('latent'):
        status = 'LATENT'
    if 'UNSETTLED' in txt:
        status = 'UNSETTLED'
    names = set()
    for m in re.finditer(r'[A-Za-z_][A-Za-z0-9_]*', cells[2]):
        nm = m.group(0)
        if nm in src_names and nm not in STOP:
            names.add(nm)
    hit = sorted(n for n in names if n in called)
    exists = sorted(n for n in names if n in src_names)
    res[el] = dict(status=status, names=sorted(names), called=hit, in_source=exists)

summary = dict(total=len(res))
for st in ('FINAL', 'LATENT', 'REMOVED', 'UNSETTLED'):
    summary[st] = sum(1 for v in res.values() if v['status'] == st)
untraced_final = [el for el, v in res.items() if v['status'] == 'FINAL' and not v['called']]
latent_missing = [el for el, v in res.items() if v['status'] == 'LATENT' and not v['in_source']]
summary['final_traced'] = summary['FINAL'] - len(untraced_final)
out = dict(summary=summary, untraced_final=untraced_final, latent_without_source=latent_missing, rows=res, called=sorted(called))
json.dump(out, open(os.path.join(os.path.dirname(HERE), 'out', 'coverage.json'), 'w'), indent=1)
print(json.dumps(summary))
print('untraced FINAL:', untraced_final)
print('latent without source fn:', latent_missing)
