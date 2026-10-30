# Combat backdrop concepts under Shifting Waves E10 (art-pass, 2026-10-30)

Board, ring wheel, cards and HUD are the E10 plate `D:/rc_tmp/combat_critic/plates/waves_e10/p1_decide.png`, untouched. Only the backdrop changed.
There is no separate board layer, so `scripts/board_extract.py` rebuilds an alpha (rect panels + wheel disc + pixel tests for the thin rings). A faint remnant of the old city shows at the edges of the thin outer rings and under the sticker/card corners. That is a compositing artefact, not part of the proposals. A soft contact shadow is added under the board.
Files: `plate1_interior.png`, `plate2_cutaway.png`, `plate3_xray.png` (+ `_squint.png`), `e10_baseline_squint.png`, `sheet.jpg`, `squint_stats.json`.
The visible backdrop is mostly the right-middle band (x 1060-1900, y 380-830), so each concept puts its focus there.

| # | Concept | Look |
|---|---|---|
| 1 | Interior | One-point-perspective Solace bio-lab hall: tank banks with lime liquid, wet floor reflections, a long window onto the night city with the lime helix, terminals under the window. Cel bands + ink. |
| 2 | Cutaway | The chosen building on the street, opened isometrically (dollhouse): lab floor lit with tanks, server racks and a bench, lobby floor beneath with the helix emblem, neighbours, neon-streaked street. Cel + ink. The fight floor reads as "the room you selected". |
| 3 | X-ray scan (own) | The Cell's own jack-in view: the building as a cyan holo wireframe in the dimmed real r42 city, the fight floor slab highlighted with schematic racks and tanks, ground ranging rings, binary bit rain (the binary-bits medium of ART_BIBLE 1.2). Near-monochrome. |

## Squint verdicts (1/16 scale, heavy blur; stats over the visible backdrop only)
| Backdrop | mean lum | p95 | loud share (lum > 0.38) | Verdict |
|---|---|---|---|---|
| E10 now | 0.28 | 0.44 | 14.5 % | The gold crane and lit buildings are a second warm mass beside the board; the board's orange arc competes with it. |
| 1 Interior | 0.19 | 0.37 | 4.6 % | Board first. The green tank bank at the right edge is the next mass, no gold. The helix window is a small accent. |
| 2 Cutaway | 0.16 | 0.36 | 2.7 % | Board first. Quietest of the lit ones; a soft green block (lab floor) sits right of the HUD but does not compete. |
| 3 X-ray | 0.15 | 0.31 | 0.1 % | Board first by a wide margin; the backdrop is a flat teal haze. Its cyan sits near the HUD's own cyan edges, so the HUD frame reads slightly less crisp. |

**The orange ring:** in the baseline squint the big orange wave arc (board art) is the loudest mass, and the old backdrop adds a gold crane right beside it. All three new backdrops are cool and dark and remove that second warm mass, so the arc becomes the single warm shape. The arc itself is unchanged; if it is still too loud, that is an E10 board decision, not a backdrop one.

## References (cited honestly; web search was thin)
- Isometric cutaway language: Hong Kong tenement isometric drawings (HKU Libraries Luke Him Sau collection, e.g. https://lhsarc.lib.hku.hk/items/show/5989, "Hill Road Tenement" isometric view) and the dollhouse-cutaway convention (parallel projection, one open corner, lit rooms against a dark shell).
- Lab/greenhouse interior mood: glass incubators with plants and cold window light (e.g. https://www.budgetpixel.com/p/17017, sci-fi lab hallway with glass cylinders; Polycount plant-incubator-room thread https://polycount.com/discussion/comment/2763168).
- Own art: `solace_vertical/hq` (lime helix, glass cylinders, lit slices), `golden_plates/street_*`, the r42/r43 city.

## Own pick: 2 Cutaway
It answers the designer's idea literally (the room you chose, shown inside its building on the street), is quiet enough to keep the board first, and shares geometry language with the city (iso blocks, ink, neon). The x-ray (3) is the best for pure board readability and the cheapest to build in Godot (a shader over the existing city), so it is the fallback. The interior (1) is the most atmospheric but the strongest competing mass, and needs a different room per building type.
Open for the designer: how many room variants (one per Site type?), and whether the scene should follow the camera down from the street.
