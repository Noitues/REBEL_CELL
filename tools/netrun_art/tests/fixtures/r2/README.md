# street r2 fixtures (P2-P4 step 1)

Regenerate with `python -m netrun_art.tests.gen_r2_fixtures [art-pass checkout]` from `tools/` (needs the art-pass worktree and PIL).
Source: art-pass `street_r2` scripts at ed8675a8 (street_r2 scripts last changed; checkout HEAD 0cce764a), art seed 1 (the plate). Nothing of the art-pass code is committed.

- `inputs/s1_layout.json`  the v3 city cut to 300 BU around the street (lot records), the 10 border links, and the plate's street
  derivation (`derive_v3`). Floats are hex strings (exact doubles). Input of `layout_pass` and `plan_pass`.
- `inputs/s1_kits.json`    the facade-kit cases (`r2_cases.kit_cases` of the plan); `seed` values are decimal strings (u64).
- `inputs/s1_signs.json`   the plan's signs and megastructure, and the glyph boxes the plate's fonts gave (`measure` rows).
- `expected/s1_layout.json` heights after `layout_pass` (lot units) and its log. `s1_plan.json` the plan (signs, props, rhythm, kits, ...).
- `expected/s1_kits.json`  per kit case: face counts and the SHA-256 of the canonical record. `s1_signs.json` the sign draw lists.

Expected files are the canonical text of `netrun_art.r2.canon` (floats to 1e-6); the GDScript twin must reproduce them byte for byte.
