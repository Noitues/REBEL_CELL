"""stale_banner.py: insert a dated status line under the title of the hover, effects and transitions NOTES (gate 1 did not re-render them)"""
import sys
sys.dont_write_bytecode = True
LOCK = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/'
ITEMS = {'hover/NOTES.md': '2.4, 2.5, 2.6, 3.9 and 3.13',
         'effects/NOTES_CDHL.md': '1.6, 2.10, 2.11 and 3.10',
         'effects/NOTES_MPST.md': '1.6, 2.10, 2.11 and 3.10',
         'transitions/NOTES.md': '1.7 and 3.12'}
for f, items in ITEMS.items():
    p = LOCK + f
    t = open(p, encoding='utf-8').read()
    tag = '**Status 2026-11-04 (gate 1): not re-rendered.**'
    if tag in t:
        print('already', f)
        continue
    lines = t.split('\n')
    line = ('%s These plates still show the older board (before the 2026-11-03 rebuild and gate 1), so their HUD, hand, room, cells and '
            'colours do not match `../final/`. AD review items %s are open here. See `../final/NOTES.md`, "2026-11-04 gate 1", Not done.' % (tag, items))
    lines.insert(1, '\n' + line)
    open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
    print('banner', f)
