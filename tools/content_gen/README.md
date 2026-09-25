# Content generators

Python scripts that write the `.tres` content added in the horizontal milestones. The
`.tres` files in `content/` are the source of truth that Godot loads; these scripts are how
they were produced, kept so a change of numbers or text can be regenerated consistently.

| Script | Writes | Milestone |
|---|---|---|
| `gen_classes.py` | Ghost, Rigger, Botnet, the four alternatives, their cores, rings, cards, barks, unlocks | M6 |
| `gen_pools.py` | shared cards, Firmware, Daemons, defense assets, shop slices, Solace events | M7 |
| `gen_meridian.py` | Meridian Freight Systems | M8 |
| `gen_corp_lib.py` | shared corporation builder (spec dict -> all files) | M9+ |
| `gen_halcyon.py` | Halcyon Civic (spec for `gen_corp_lib.py`) | M9 |

Run from anywhere with Python 3 (`python tools/content_gen/gen_halcyon.py`), then
`godot --headless --path . --import` and the three checks in CLAUDE.md. Scripts overwrite
their own files only. Hand edits to generated `.tres` files are lost on regeneration: change
the script instead.
