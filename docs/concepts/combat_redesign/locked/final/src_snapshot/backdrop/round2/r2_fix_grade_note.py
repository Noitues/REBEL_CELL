"""r2_fix_grade_note.py -- docs-only fix after the full publish: rewrite grade.json round2.note with r2_publish.grade_note (measured scrim rows
instead of a code constant) in round2/backdrop/out/grade.json, copy it to the published folder and compare the two byte for byte.  No plate
is touched."""
import sys, json, shutil, filecmp, ast
sys.dont_write_bytecode = True
HERE = 'D:/rc_scratch/combat_redesign/locked/round2/backdrop/'
DST = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/backdrop/'
# take grade_note from r2_publish.py without running the publish (parse the source, exec only that function)
src = open(HERE + 'r2_publish.py', encoding='utf-8').read()
mod = ast.parse(src)
fn = [n for n in mod.body if isinstance(n, ast.FunctionDef) and n.name == 'grade_note'][0]
ns = {}
exec(compile(ast.Module(body=[fn], type_ignores=[]), 'grade_note', 'exec'), ns)
g = json.load(open(HERE + 'out/grade.json', encoding='utf-8'))
ck = json.load(open(HERE + 'out/checks.json', encoding='utf-8'))
g['round2']['note'] = ns['grade_note'](g['version'], ck['ui_scrim_rows'])
json.dump(g, open(HERE + 'out/grade.json', 'w'), indent=1)
shutil.copyfile(HERE + 'out/grade.json', DST + 'grade.json')
print(g['round2']['note'])
print('byte identical', filecmp.cmp(HERE + 'out/grade.json', DST + 'grade.json', shallow=False))
