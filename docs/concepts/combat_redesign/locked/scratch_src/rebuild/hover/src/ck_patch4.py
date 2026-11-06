"""ck_patch4.py : hv_checks.py -> the L5 chevrons (L5c) and arrowheads (L5h) in the pencil sets; L5 edge widths on the edges only, chevron
widths reported"""
import sys, io
sys.dont_write_bytecode = True
p = 'D:/rc_scratch/combat_redesign/locked/rebuild/hover/src/hv_checks.py'
s = io.open(p, encoding='utf-8').read()
a = "    pen_all = g(M, 'P__L6_all') | g(M, 'P__L5_all')\n    pen_wax = g(M, 'P__L6_wax') | g(M, 'P__L5_wax')\n"
b = ("    pen_all = g(M, 'P__L6_all') | g(M, 'P__L5_all') | g(M, 'P__L5c_all') | g(M, 'P__L5h_all')      # L5c chevrons, L5h arrowheads\n"
     "    pen_wax = g(M, 'P__L6_wax') | g(M, 'P__L5_wax') | g(M, 'P__L5c_wax') | g(M, 'P__L5h_wax')\n")
assert a in s
s = s.replace(a, b)
a = "    r = dict(mask=dict(L6_wax=sw('L6_wax'), L6_all=sw('L6_all'), L5_wax=sw('L5_wax'), L5_all=sw('L5_all')), reference=dict(REF_W),\n"
b = ("    r = dict(mask=dict(L6_wax=sw('L6_wax'), L6_all=sw('L6_all'), L5_wax=sw('L5_wax'), L5_all=sw('L5_all')), reference=dict(REF_W),\n"
     "             L5_chevrons_reported=dict(wax=sw('L5c_wax'), all=sw('L5c_all'), spec='3.4 px wax, 1.5 px ink a side'),\n")
assert a in s
s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
