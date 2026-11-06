"""try_blocks: render every port_spec block and write them to one preview file (exploration)."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/port/src')
import port_spec as PS

out = []
for n, fn in PS.BLOCKS.items():
    s = fn()
    out.append('#### ' + n + '\n' + s + '\n')
    print(n, len(s.split('\n')), 'lines')
open('D:/rc_scratch/combat_redesign/locked/port_rb/work/blocks_preview.md', 'w', encoding='utf-8').write('\n'.join(out))
