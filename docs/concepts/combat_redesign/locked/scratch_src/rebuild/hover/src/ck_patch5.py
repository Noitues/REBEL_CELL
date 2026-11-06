"""ck_patch5.py : hv_checks.board_a -> the board's mask set is rb_capture (R__) + the board render's own classes (Z__), without the hover
classes: with it the board check reproduces the board's published rows (p1_nowords r0 s0 3.34 at 282 px)"""
import io
p = 'D:/rc_scratch/combat_redesign/locked/rebuild/hover/src/hv_checks.py'
s = io.open(p, encoding='utf-8').read()
a = """    Mb = {}
    for k, v in M.items():
        pre, _, nm = k.partition('__')
        if pre == 'R':
            Mb[nm] = (Mb[nm] | v) if nm in Mb else v
    rb = RC.check_cells(T.lum(bg), bg, dict(geometry=rep['geometry']), Mb, T.lum(probe) if probe is not None else None)"""
b = """    Mb = {}
    for k, v in M.items():
        pre, _, nm = k.partition('__')
        if pre in ('R', 'Z') and nm not in BOARD_A_SKIP:
            Mb[nm] = (Mb[nm] | v) if nm in Mb else v
    rb = RC.check_cells(T.lum(bg), bg, dict(geometry=rep['geometry']), Mb, T.lum(probe) if probe is not None else None)"""
assert a in s
s = s.replace(a, b)
s = s.replace("def board_a(rep, M, bg, probe, a):", "BOARD_A_SKIP = ('hover', 'ghost', 'inset', 'plan', 'hand', 'send', 'undo')     # hover classes, not the board's\n\n\ndef board_a(rep, M, bg, probe, a):")
s = s.replace("""    tells a hover failure from a board-renderer one.  Reported; the hover gate above is unchanged.\"\"\"""",
              """    tells a hover failure from a board-renderer one.  The masks are rb_capture's (R__) and the board render's own classes (Z__) without the
    hover classes; with them this reproduces the board's published rows (final p1_nowords ring 0 sector 0: 3.34 at 282 px).  Reported; the
    hover gate above is unchanged.\"\"\"""")
s = s.replace("note='rb_checks.check_cells on work/board_<key>.png (the board renderer, this plan state, no hover marks, no dim) with the R__ masks')",
              "note='rb_checks.check_cells on work/board_<key>.png (the board renderer, this plan state, no hover marks, no dim) with the board masks (R__ + Z__ without the hover classes)')")
io.open(p, 'w', encoding='utf-8').write(s)
print('ok', s.count('BOARD_A_SKIP'))
