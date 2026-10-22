# Solace THE BLOOM A "Necrosis": Godot port (look only), 2026-10-22

Branch `art/look-bloom` (off art/look-gate 105e9808), godot worktree D:/rc_art/godot_look_bloom. DECISIONS entry "2026-10-22 - LOOK Solace Bloom A (Necrosis)".
- `parity_A.jpg`: target (A3d_*, Cycles) above, Godot frozen (`--reduce-effects=1`, plate cameras) below; `godot_*.jpg` the five Godot frames.
- Street frames: seed 1, decision shot, plate camera (na23_lab `--plate_dir`), fronts -0.5 / 0.75 / 1.4 layers (operative on layer 2: gaps 2.5 / 1.25 / 0.6). HQ frames: hq_run_lab pov / pod, fronts layer 3.0 (floor 9 of 27) and 1.75 + the decision lift (28 BU), at 1280x720 (the lab's window).
- Bloom off vs today: strength 0 (`--bloom-strength=0`) and no Bloom call at all are pixel-identical to the base commit: street decision max diff 0, HQ overview and decision max diff 0.
- Not the same city: the Godot street is the game's seed-1 street, not the plate's (3.7 BU rooms, 6 BU layers), so the composition differs; the skin (plum body, thin pink veins, hatch, ragged hot front, ribbons ahead on the road) is what reads alike. The HQ page looks inland (its own yaw), so the helix is seen from another side.
- Capture scripts in `scripts/` (run_street.sh / run_hq.sh through tools/run_windowed.py under the GPU lock helper gpu_run.py, parity_sheet.py, imgdiff.py).
- Rev 3 (hot hairline 45 / 1.1 BU, spore haze): the haze is a Godot FogVolume layer of its own (bloom_haze.gdshader), never in the strand albedo or emission: "dark body, hot edge".

## Tuning round (rulings 2026-10-22)
Sheet rebuilt: target above / Godot below for street x3 and HQ x2, plus squint rows (320 px and 4 px blur). Street frames now the game's seed 3, operative L4 (seed 1's near column hides the CREEPING front). Strength 0 re-proved: max diff 0 (street seed 3, HQ overview + decision). Tendril / ribbon reach are in layers.
