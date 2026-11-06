"""replace_between: replace the lines of a text file from the line that starts with START up to (not including) the line that
starts with END by the content of NEW_FILE.  Each anchor must match exactly one line.  usage:
python replace_between.py FILE START END NEW_FILE"""
import sys

path, start, end, newf = sys.argv[1:5]
lines = open(path, encoding='utf-8').read().split('\n')
si = [i for i, s in enumerate(lines) if s.startswith(start)]
ei = [len(lines)] if end == '__EOF__' else [i for i, s in enumerate(lines) if s.startswith(end)]
assert len(si) == 1, ('start', start, si)
ei = [i for i in ei if i > si[0]]
if end == '__EOF__':
    lines.append('')
assert ei, ('end', end)
new = open(newf, encoding='utf-8').read().rstrip('\n').split('\n')
if lines[ei[0]].strip() and new[-1] != '' and not (lines[ei[0]].startswith('|') and new[-1].startswith('|')):
    new.append('')
out = lines[:si[0]] + new + lines[ei[0]:]
open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print('replaced lines %d-%d (%d) with %d' % (si[0] + 1, ei[0], ei[0] - si[0], len(new)))
