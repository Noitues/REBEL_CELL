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

`gen_orbital.py` writes Orbital Commons (M10).
`gen_rebel_cell.py` writes the REBEL_CELL template (M11); `scripts/core/rebel_cell_builder.gd` fills it from the profile at runtime.
`gen_home.py` writes the M12 home-server variants and their unlocks.
`gen_h1.py` writes the horizontal pass 1 content (DJ sets, rescue events, Shatter).

`check_regen.py` regenerates every generator above into a temp copy of the repo and diffs it against `content/` (exit 1 on any difference); run it after editing a generator or hand-editing generated content. Solace has no generator (hand-written `.tres`). N21 resistance (`n21_passive`) and N22 pools (`NORMAL_POOLS`) live in `gen_corp_lib.py`; `gen_meridian.py` shares them. Spec key `letterhead` and enemy key `enrage` are written when present.
