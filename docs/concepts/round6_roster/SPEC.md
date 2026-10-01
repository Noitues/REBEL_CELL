# Round 6: roster wheels, in the chosen slice style

## Decision (designer)
- **Base style:** family **C, "Screens & Data"**. Each slice is a tiny live CRT screen running its program, inside a per-slice bezel, with a big white glyph and number on a darkened patch. It resonates best, and its icons read very well.
  Reference: `docs/concepts/round5_slices/s_c_screen_data/` (`programs_sheet.png`, `wheel_player.png`, `shader_fx.gif`, scripts).
- **Not every C slice is approved.** For slice backgrounds you may pull examples from:
  - **A, circuit board** (`docs/concepts/round5_slices/s_a_circuit/`): its PCB looks can sit *inside* the C screen bezel as the screen's content.
  - **D, the corporate themes** (`docs/concepts/round5_slices/s_d_corp_themes/`).
- **Keep the frame, icon and number treatment of C.** Vary only the screen content per program.

## Which C slices to keep or replace
| Program | Verdict |
|---|---|
| EXPLOIT | Keep (hex dump with an injected line) |
| ZERO-DAY | Keep (noise resolving into a skull, RGB split) |
| FIREWALL | Keep (`[#]` brick wall) |
| SANDBOX | Replace. Too subtle at small size; use A's guard-ring PCB, boxed in, inside the screen. |
| PROXY | Keep, but make the reroute path bolder |
| PATCH | Keep |
| VIRUS | Tone it down; it was too bright next to its neighbours |
| TROJAN | Keep |
| NULL | Keep (dead CRT) |

## Rules for every wheel
- **Core layout:** same geometry, pointer, hub, bezel and HP arc as C's player wheel.
- **Hub:** shows the name and core. Use a simple emblem or portrait glyph; it doesn't need to be a painted face.
- **Small size:** below about r=120, use C's small variant (bigger glyph, calmer screen, darker patch).
- **Accessibility:** type reads in greyscale by glyph.
- **Slice values:** real slice values for each class and enemy are in `content/classes/*.tres`, `content/enemies/*.tres` and `content/hub_cores/*.tres`. Read them to build each wheel's slice list (type + value + tick span) where possible. If a value is unclear, make a plausible one and say so.

## Deliverables (`docs/concepts/round6_roster/`)
1. **Operatives**: all 8 classes: Breaker, Wrecker, Ghost, Phantom, Rigger, Overclocker, Botnet, Hivemind.
   - Each class gets its **own player wheel** in C style.
   - Each also gets a **class identity**: a bezel ornament and a hub-ring look per class (e.g. Breaker riveted plates, Wrecker welded and dented, Ghost a flickering translucent rim, Phantom an afterimage double rim, Rigger cable-wrapped, Overclocker vented fins, Botnet an orbiting dot ring, Hivemind a hex lattice).
   - Draw the class's **inner hub ring** of segments where the class has one (Accelerator, Anchor, Corrupt, Echo, Pierce, x2: see `content/` or `docs/art_asset.md`).
   - Alternatives must read as related to their base class.
   - Files: `operatives_sheet.png` (all 8 at about r=220 in a 4×2 grid, labelled), plus one 1920×1080 file per class, `op_<class>.png`.
2. **Enemies**: one wheel per corp theme, using D's corporate materials *inside* C's screen frames. That means a cohesive enemy screen skin per corporation: Meridian container/barcode, Solace cells/glass, Halcyon blueprint, Orbital star map (make it brighter than D's), REBEL_CELL corrupted Cell board.
   - Render **2 regulars + 1 elite per corporation** (15 wheels), picked from the enemy list in `C:\Users\noitu\Documents\Godot\rebel_cell\docs\art_asset.md` (Appendix, Enemies), with real names. Prefer enemies with special mechanics: two pointers (Route Optimizer, Tracking Station), an orbiting pointer, drones docked on the wheel.
   - Show those mechanics on the wheel: a second pointer, drone tokens docked around the rim with HP, a resistance badge.
   - Files: `enemies_<corp>.png` (5 files, 3 wheels each) and `enemies_sheet.jpg` (all 15).
3. **Bosses**: all 5: The Manifest (Meridian), Renewal Engine (Solace), The Civic Core (Halcyon), The Commons Array (Orbital), DISPATCH (REBEL_CELL).
   - Each is 120% size with a heavier bezel, a nameplate banner, and phase pips on the HP arc.
   - Give each a signature boss screen effect, plus a PHASE 2 variant: the wheel re-skins or corrupts, adds a second pointer, or reconfigures slices.
   - Files: `boss_<name>.png` (phase 1 and phase 2 side by side) and `bosses_sheet.jpg`.
4. `contact_sheet.jpg`, `NOTES.md`, `scripts/`.

## Tools
- Extend the C scripts (Pillow + numpy). Write `.py` files; **never run `python -`**.
- Use seeded randomness.
- Keep scratch files in your own subfolder.
- Keep the folder under about 40 MB, JPG for the big sheets.
- Don't touch other folders.
