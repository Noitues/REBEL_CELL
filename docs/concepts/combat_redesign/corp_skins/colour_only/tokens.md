# Corp skin tokens (colour only)

Source: `src_snapshot/corp_skin.py`, `TOKENS[corp]`. Swapping corp = swapping this table. The tokens feed a luminance ramp for the enemy enamel family (so HOT/COLD/FAR grades keep their order) and a hue move for the schedule-orange family. Reds, pinks, cyans, violets and boss gold are never remapped.

| Role | What it colours | Solace Biosystems | Meridian Freight |
|---|---|---|---|
| primary (kit) | corp identity, ART_BIBLE 2.4 | #96FF46 | #FF8C1A |
| secondary (kit) | tier II, ART_BIBLE 2.4 | #FF4696 (not used on the board, see NOTES) | #FF2E28 (not used on the board, see NOTES) |
| ink | deepest line, keylines, shadow | #050C08 | #08090A |
| glass_lo | empty cell wells, ring floor | #0B1E14 | #15181B |
| glass | cell body, gutters | #1E4A30 (leaf-green glass) | #2F353A (container steel) |
| mid | enamel body, dim (FAR/COLD) hairlines | #5E9A62 | #7C858C |
| hot | HOT enamel lines, frames, token rim | #A8F070 | #E8E2D2 |
| disc | token disc, ticket paper, white text plates | #F0FFE2 | #F4F0E6 |
| rim_lo | outer rim shadow | #0E2A1A | #3A1E12 |
| rim | outer rim body | #2C7046 | #9A5A1E |
| rim_hi | rim highlight hairline | #B8FF8A | #FFA03A |
| tape | THIS TURN / HOLD tape and the other schedule-orange marks (hue move, value kept) | #96FF46 | #FF8C1A (unchanged) |
| accent2 (secondary, softened) | reserved, unused in this test | #F4B6CE blush | #B8402A oxide |

Unchanged on both: HARM red and the red cross-hatch, CELL_PINK (ours), RAM cyan, Trace violet, boss/plan gold, HP green, white game digits.
