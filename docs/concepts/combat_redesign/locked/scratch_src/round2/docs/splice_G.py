"""splice_G.py: replace VISUAL_PLAN.md section G (from '## G. Effect overlays' up to the '---' line before '## H. Hover')
with work/vp_G.md.  usage: python splice_G.py [--write]   (without --write: prints the old and new line counts only)"""
import sys

VP = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/VISUAL_PLAN.md'
NEW = 'D:/rc_scratch/combat_redesign/locked/round2/docs/work/vp_G.md'
txt = open(VP, encoding='utf-8').read()
a = txt.index('## G. Effect overlays (designer note 7)')
b = txt.index('\n---\n\n## H. Hover', a)
new = open(NEW, encoding='utf-8').read().rstrip('\n') + '\n'
old = txt[a:b + 1]
print('old G lines', old.count('\n'), 'new G lines', new.count('\n'))
assert txt.count('## G. Effect overlays') == 1
out = txt[:a] + new + txt[b + 1:]
if '--write' in sys.argv:
    open(VP, 'w', encoding='utf-8', newline='\n').write(out)
    print('wrote', VP)
