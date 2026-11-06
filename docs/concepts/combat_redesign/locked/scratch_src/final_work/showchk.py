"""showchk.py chk.json: print the occlusion / collision / hand numbers"""
import sys, json
c = json.load(open(sys.argv[1]))
print('asserts', len(c['asserts']), 'fail', sum(1 for a in c['asserts'] if not a['ok']), 'dash', c['dash_calls'], 'dot', c['dot_calls'])
print('occ', c.get('occlusion_px'), c.get('occlusion_pass'))
print('hand', c.get('hand_vs_board'))
print('overlap nonzero', {k: v for k, v in c.get('overlap_px', {}).items() if v})
