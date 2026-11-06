p='xf_slices.py'
s=open(p,encoding='utf8').read()
a=s.index("PAL = {"); b=s.index("TEXKIND")
new='''PAL = {
    'A': {   # riso spot inks on the white sheet: magenta, cobalt, sun yellow, green
        'BURST':  dict(fill='FF3DA8', tex='B3126F', op=0.95, name='BIG DOTS'),
        'SHIELD': dict(fill='2A58F0', tex='142C86', op=0.95, name='SCALES'),
        'TURRET': dict(fill='FFD21F', tex='A97D00', op=0.95, name='CHECKER'),
        'REPAIR': dict(fill='4BD67E', tex='11703A', op=0.95, name='PLUS TILES'),
    },
    'B': {   # fluoro inks re-dealt onto the black toner sheet: orange, violet, aqua, lime
        'BURST':  dict(fill='FF5A14', tex='A12D00', op=0.95, name='BIG DOTS'),
        'SHIELD': dict(fill='7A3CF0', tex='3B1A8A', op=0.95, name='SCALES'),
        'TURRET': dict(fill='3FE0F5', tex='0A7C8C', op=0.95, name='CHECKER'),
        'REPAIR': dict(fill='C5F42E', tex='5C7A00', op=0.95, name='PLUS TILES'),
    },
}
'''
s=s[:a]+new+s[b:]
open(p,'w',encoding='utf8').write(s)
