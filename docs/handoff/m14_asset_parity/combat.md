# M14 asset parity: combat and foundations (Groups 1-2)

Rule (designer, 2026-10-05): any icon, sprite, texture or sheet the art pass made is exported by running its own
generator on tag `art-concepts-r43` (drawing code unchanged; a wrapper may split a sheet and drop live text) or
sliced from the approved image. Never redrawn. Procedural only where no concept asset exists.

## Replaced by the art pass's own export

| Item | Source (tag art-concepts-r43) | Export script | Asset | Used by |
|---|---|---|---|---|
| Firmware die (4 rarities, plus lit frame) | round 34 `fwlib.put_chip` (glyph split off) | `tools/art/export_firmware_daemons.py` | `assets/wheel/firmware/die_<rarity>[_lit].png` + manifest | `FirmwareSocket.draw_die` (pins-in rotation, cross-fade to lit, atlas glyph upright) |
| Daemon tile (all Daemons; 12 idle frames + 1 fire frame) | round 34 `fwlib.daemon_tile` | same | `assets/wheel/daemons/<id>.png` + manifest | `DaemonRack._draw_tiles` (frame from the scan phase, fire cross-faded) |
| Hand card face (wheel / hack / system x 4 rarities) | round 31 `r31lib.card_face`, `card_sticker` (text and glyphs split off) | `tools/art/export_card_faces.py` | `assets/cards/face_<kind>_<rarity>.png` + manifest | new `CardFace` (`scripts/ui/fx/card_face.gd`), via `ZineCard.with_face_art()`; combat hand only |
| HUD marks (shield, RAM, HP, evade, lock, spin cw/ccw, draw) | round 17/1C glyph atlas (manifest source_tag art-concepts-r43) | existing atlas | `assets/glyphs/...` | `HudSkin.draw_glyph`, `WheelGlyphs.named()` |
| SEND IT sticker | round 22 `fx_r22.send_sticker` | `tools/art/export_combat_stickers.py` | `assets/fx/stickers/send_it.png` | `VinylSticker` via `StickerArt` (slap, hover, grey states run on it) |
| PERFECT / GOOD / WEAK landing words | round 39 `landing.word` -> `effects_batch1.vinyl_word` | same | `word_perfect/good/weak.png` | `VinylSticker` via `StickerArt` |
| EVADE `>>` token (flight and standing) | round 19 `effects_batch1.token_sticker` | same | `assets/fx/stickers/evade_token.png` | `FxDraw.token` (flight) and `WheelView._draw_guards` (standing, one per charge) |
| Drone sticker and its six pieces | round 22 `fx_r22.drone_sticker`, `_pieces_from` (HP number split off: live HP) | same | `drone.png`, `drone_piece_0..5.png` | `FxDraw.drone_hex` (slap), `FxDraw.drone_burst` (pieces fly along the manifest's directions) |

## Already from the concepts (unchanged)
Slice screens (`bake_wheel_screens.py`), corp crests (`bake_wheel_glyphs.py`), the 1C glyph atlas, combat backdrops
(Blender from the concept scripts).

## Procedural, with the reason (no concept asset exists)
- DEFRAG bricks, SANDBOX hexes, bits, glitch tears, shards, shockwave ring, crack lines, jaws: the concepts draw them
  per frame procedurally too; there is no sprite.
- The drone's outline-packing hex and the clamp arms and crack zigzag in the burst: concept draws them procedurally.
- Heat mark: no concept glyph exists.
- Lethal skull `WheelView.draw_skull`: no concept glyph.
- Drone dock band, lobe, mini-wheels: live values and dynamic geometry.
- Card peel curl: a moving fold.
- Name sticker and other vinyl words with live (translated) text: `VinylSticker` material is the `sticker_lib` recipe on
  live text.
- Kit materials (CRT, pencil, spill, holo, paper): shaders applied to arbitrary content.
- The wheel disc shader's bezel, hub and inner ring: a port of the concept's `frames._d4` / ringlock recipe, not a
  bake. A texture bake would freeze live geometry (spin, slice count); proposed slice: bake the static bezel ring
  from the recipe once and let the shader tint it.
- Shop and deck card pictograms (`ZineCard._draw_pictos` arrows): shop and deck views belong to 4A and Groups 3-4;
  the combat hand uses the atlas pictograms.

## Not done / proposed slice
- Windowed after-captures of the wheel, rack, dies, drones and landing words were not taken in this pass (tests and
  fast checks only); the orchestrator's windowed QA run should read them.
