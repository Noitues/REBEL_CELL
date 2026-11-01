p = 'D:/rc_scratch/combat_polish/E7_waves/E10/src/dump10.py'
t = open(p).read()
old = "L_TRIG = find_line(lambda pl: any(a[0] == 'Trigger' for a in pl) and not any(a[0] == 'Brace' for a in pl))"
new = '''def refund_trigger(pl):
    s_ = cl(st0)
    for a in pl:
        if a[0] == 'Trigger' and any(e[0] == 'refund' for e in S.trigger_preview(s_, a[1])):
            return True
        S.apply(s_, a)
    return False


L_TRIG = find_line(lambda pl: refund_trigger(pl) and not any(a[0] == 'Brace' for a in pl))'''
assert old in t
open(p, 'w').write(t.replace(old, new))
