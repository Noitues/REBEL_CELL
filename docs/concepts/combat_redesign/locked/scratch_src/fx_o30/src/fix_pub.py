p = 'D:/rc_scratch/combat_redesign/locked/fx_o30/src/o30_publish.py'
s = open(p, encoding='utf-8').read()
s = s.replace("('trace_add', 200, 'TRIGGER played: Trace 3 to 4', (1440, 640))", "('trace_add', 200, 'TRIGGER played: Trace 3 to 4', (1440, 700))")
s = s.replace("('wave_enter', 500, 'W4 enters ring +2', (380, 300))", "('wave_enter', 500, 'W4 enters ring +2', (330, 250))")
s = s.replace("'Each effect starts 100 ms after the previous one ends (GODOT_PORT_SPEC 8.2). Effect total %d ms.' % total",
              "'Each effect starts 100 ms after the previous one ends (GODOT_PORT_SPEC 8.2); 400 ms hold before RINGS STEP. Beat total %d ms.' % total")
open(p, 'w', encoding='utf-8').write(s)
