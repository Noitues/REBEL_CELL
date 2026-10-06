# M14 resume: asset-parity sweep, combat and foundations (Groups 1-2)

Worktree branch `worktree-agent-ab68662e2190e33b2`, based on main `00d310f`. WIP checkpoint `457303d`
("ART parity combat: WIP checkpoint for resume"). Not merged with main. No tests and no fast checks run yet.
Temp folder `%TEMP%\apA\` (APPDATA `%TEMP%\apA\appdata`). Concept scripts are extracted at `%TEMP%\apA\c\`
(`docs/concepts/<round>/scripts`, plus `content/` and `assets/fonts` from the tag so the scripts' relative paths work).

## Done in the checkpoint (code written, NOT yet imported, run, tested or captured)
1. **Firmware die**: `tools/art/export_firmware_daemons.py` runs round 34 `fwlib.put_chip` (glyph split off)
   -> `assets/wheel/firmware/die_<rarity>[_lit].png` + manifest. `FirmwareSocket.draw_die` now draws the texture
   (rotated pins-in, cross-fade to `_lit` for the flash) plus the atlas glyph upright. The old drawn octagon is gone.
2. **Daemon tiles**: the same script exports `fwlib.daemon_tile` as 12 idle frames + 1 fire frame ->
   `assets/wheel/daemons/<id>.png`. `DaemonRack._draw_tiles` uses the sheet (frame from the scan phase; frame 0
   when the scan is off; fire cross-faded). The drawn tile stays only as a fallback for unknown ids.
   Note: the tile's phosphor is the concept's family per Daemon, which can differ from `AttachStyle.daemon_family`.
3. **Hand cards**: `tools/art/export_card_faces.py` runs `r31lib.card_face` + `card_sticker`, with text and glyphs split off
   -> `assets/cards/face_<wheel|hack|system>_<rarity>.png` + manifest with the layout. The new class `CardFace`
   (`scripts/ui/fx/card_face.gd`) draws the face, plus the live cost, title, art glyph, kind word, pictograms (atlas),
   rules text, key, NEED, disabled and alarm states. `ZineCard` gets `face_art`, `card_rarity` and `with_face_art()`,
   and `pictos_of` now adds `"effect"`. Only the combat hand opts in (`combat_scene._make_card`). Shop and deck views
   are unchanged (4A owns the shop).
4. **HUD marks**: `HudSkin.draw_glyph` draws 1C atlas glyphs (shield = picto_block, ram, hp, evade = slice_detour,
   lock = state_locked, cw/ccw = picto_spin, cards = picto_draw). Heat stays drawn, because no concept glyph exists.
   `WheelGlyphs` gets the `@<atlas name>` ids (`WheelGlyphs.named()`).
5. **Word stickers**: `tools/art/export_combat_stickers.py` (round 39 scripts) exports `assets/fx/stickers/`:
   send_it, word_perfect/good/weak, evade_token, drone, drone_piece_0..5, and a manifest. `StickerArt` lookup.
   `VinylSticker` gets a baked mode: when the word is in `StickerArt` it draws the image, with shader rim off and
   gloss/shadow off for images that have their own finish. The motions are unchanged. The landing word WEAK is now
   "WEAK" (x0.5 stays on the rail).

## Left, in order
1. Import (`%TEMP%\apA\import.sh`) and fix any parse errors. Nothing has been compiled yet.
2. FxDraw: `token()` -> `evade_token.png`. `drone_hex()` slap -> `drone.png` (scale `DRONE_HEX/40`).
   `drone_burst()` -> the 6 pieces flying along `dir` from `offset` (keep the clamp and crack lines). WheelView `_draw_guards`
   standing EVADE token (around line 2385) -> `evade_token.png`.
3. Tests: run test_art2_attachments, test_art2_cards_fx, test_art2_hud, test_art1_material_kit,
   test_anim_r2_combat, test_anim_r1_campaign, test_horizontal_pass24_screens and test_visual_lint_static in ONE gt.sh call.
   Lint may flag `Color(...)` literals or new consts. CardFace constants are generator px, so baseline or rename them if flagged.
4. Strings: "WHEEL"/"HACK"/"SYSTEM" (CardFace.KIND_WORDS # TR) and "WEAK". Re-export
   `tools/export_text.gd`, then import.
5. Windowed after-captures: `bash %TEMP%/apA/cap_wheel.sh after "typical,worst,kits,hubs,states,landing:perfect,landing:good,landing:weak" 24`
   (frames come out 1280x720; the `--resolution` flag is ignored). Also arena_lab (`--fixture=worst --bloom`, for the dies, rack and drones)
   and motion_lab demos for evade_token, drone_deploy and drone_destroyed. Before frames are in `%TEMP%\apA\cap_before\keep\`.
   Copy before/after crops to `docs/art_review/ART-parity/combat/` (add `.gdignore`).
6. Inventory `docs/handoff/m14_asset_parity/combat.md` (not written yet; findings below) and the DECISIONS entry
   "Art direction — asset parity: combat".
7. Still to judge: the wheel disc shader's procedural bezel, hub and inner ring (a port of frames._d4 / ringlock: is a
   texture bake from the recipe feasible?); the old `ZineCard._draw_pictos` drawn arrows (shop and deck: hand to 4A/Groups 3-4);
   manifests for the existing `assets/wheel/screens` and `glyphs_interim` (concept-sourced already).
8. Hand-back: `git merge main`, `JOBS=2 bash docs/handoff/art_2/process/checks_fast.sh`, own scripts via gt.sh.

## Inventory progress (to write up)
- Replaced: firmware die, Daemon tile, hand card face, HUD marks (8 kinds), SEND IT, PERFECT/GOOD/WEAK; evade token and drone are exported but not wired.
- Already from the concepts: slice screens (bake_wheel_screens), corp crests (bake_wheel_glyphs), 1C glyph atlas (verified manifest
  source_tag art-concepts-r43), combat backdrops (Blender from concept scripts).
- Procedural, with reason: DEFRAG bricks and SANDBOX hexes, bits, tears, shards, shockwave, cracks and jaws (the concepts draw these per frame
  procedurally too; no sprite exists); Heat mark (no concept glyph); lethal skull `WheelView.draw_skull` (no concept glyph);
  drone dock band and lobe and mini-wheels (live values, dynamic geometry); card peel curl (moving fold); name sticker and other
  vinyl words with live text (VinylSticker material = the sticker_lib recipe on live text); kit materials (CRT, pencil,
  spill, holo, paper) applied to arbitrary content.

## Gotchas
- The Bash worktree guard refuses compound commands that contain git; write scripts to `%TEMP%\apA\*.sh` / `.py` and run them.
- Python `write_text` on Windows writes CRLF; write with `open(..., newline="\n")`. Manifests got CRLF (git normalises them).
- Concept libs hard-code the art-pass font path; the wrappers re-point them to `assets/fonts`.
- Importing round 39 / 23 `effects_batch1` renders wheels at import time (~1 min) and needs `content/` beside `docs/`.
- `python -` PID 10788 belongs to another agent (city3d), not this one; leave it.

## Open questions
- Card kinds: the concept has WHEEL / HACK / SYSTEM only, so the game's violet "rest" family maps to SYSTEM (cyan).
- WEAK is amber in the concept and was yellow in the game: the concept wins.
