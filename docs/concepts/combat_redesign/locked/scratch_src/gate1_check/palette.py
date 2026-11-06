import numpy as np
from lab import hex2rgb, dE76, lab
T = {'CELL_PINK': 'FF3DA8', 'HARM': 'FF4433', 'GAIN': '7BE07B', 'SOAK': '3A7EF3', 'PLAN': 'FFE200', 'SCHEDULE': 'FF8C1A', 'BOSS_GOLD': 'D69A1A',
     'NET_CYAN': '5CE1FF', 'TRACE_VIOLET': 'A03CFF', 'CRT_AMBER': 'FFB000', 'RESIST_GOLD': 'FFD24D', 'FOCUS/CELL_LIME': 'D4FF00',
     'COLD': 'D9877C', 'FAR': '96767A', 'BURST': 'F06EAE', 'SHIELD': '5E9BE0', 'TURRET': 'D6A33A', 'REPAIR': '3FB59A',
     'Packet': '3D5466', 'Worm': '4B4A6E', 'Jammer': '2D5D69', 'Payload': '5B5560', 'Ring': '55617A', 'ENAMEL': 'D9E1EA', 'PAPER': 'F2EEE4'}
def row(name, h, keys=None):
    ds = sorted(((dE76(hex2rgb(h), hex2rgb(v)), k) for k, v in T.items() if (keys is None or k in keys)))
    print('%-18s #%s  L* %.1f  nearest: %s' % (name, h, lab(hex2rgb(h))[0], ', '.join('%s %.1f' % (k, d) for d, k in ds[:5])))
print('-- card type plates / band (2.2)')
row('TOWER plate', '006E66'); row('WAVE plate', 'B4AAFF'); row('Spin3 band', 'FF00F0')
row('old TOWER cobalt', '2F5BFF'); row('old WAVE orange', 'FF8A1F'); row('old Spin3 sun', 'FFD21F')
print('-- corp skin hue inks vs the 2.4 four (Cell lime/FOCUS, GAIN, HARM) and the rest (1.3)')
for k, h in [('Solace leaf', '96FF46'), ('Solace leaf_deep', '4FA83A'), ('Solace porcelain', 'E6EFE4'), ('Meridian rust', 'B0602C'), ('Meridian rust_hi', 'D88A4E'), ('corp_solace', '3DFF8B')]:
    row(k, h)
print('-- token x token minimum')
ks = [k for k in T if k not in ('Packet', 'Worm', 'Jammer', 'Payload', 'Ring', 'ENAMEL', 'PAPER')]
pairs = sorted((dE76(hex2rgb(T[a]), hex2rgb(T[b])), a, b) for i, a in enumerate(ks) for b in ks[i + 1:])
for d, a, b in pairs[:8]: print('  %-16s %-16s %.1f' % (a, b, d))
