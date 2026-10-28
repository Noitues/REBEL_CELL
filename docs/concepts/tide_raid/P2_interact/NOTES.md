# P2 interactivity concepts: Solace Infected Tide (art-pass, polish iteration 2, 2026-10-27)

Rebuild of P1_interact on the shared P2 base (`D:/rc_scratch/tide_concepts/p2_base/`, STYLE_CONTRACT). Nothing committed. Stills only.
Every frame exists twice: `frames/NAME.jpg` annotated (designer layer), `frames/clean/NAME.jpg` game UI only. Judgements were made on clean frames.

## What changed against P1 (critic punch list #1)
| Item | P1 | P2 |
|---|---|---|
| City | old darker plate, regrade | `p2_base/city_default.png` (graded city: warm/cool, sodium lamps, signage, wet streets), no rails |
| Heads | pass-2 dart / block / ram | H6 D worm / N claw / E mine, the 16 pre-rendered rotations at 44 px, above ribbons, below tags |
| Palette | DAMAGED FF6A1A, SITES LOST F29A1A | DAMAGED FF9A00, SITES LOST C98410 as an ink-black ring / block / tile with white rim and ochre hatch |
| Tier ring | 7 px band | 13.6 px band, 6.3 px ink under-stroke, 2.2 px white inner rim, per-tier pattern (dots / bars / hatch / chevrons / crosshatch + second ring); world-circle iso ellipse radii 9.5 to 12.5 BU |
| Stop block | 44 x 34 px | 13.5 x 10 BU world rectangle, chamfered, ink border, white rim, tier pattern |
| HOME | grey tick ring | white ring r22 BU (brightest object), 50-tick gauge, warm pool, preview = amber outline, lost = amber filled |
| Towers | 10 equal wireframes | ranked: bright wire + scan + spine only for stop Sites (`ix_lib.BRIGHT`), the rest 35 % quiet glass; heights 100 / 130 / 164 px |
| Cage | cyan-white | mint 55E0A0 at 60 % |
| Beams | | E ribbon x0.8 strength, glow x0.6; ghost pass (0.8 gain where the city occludes, corridor darkened 22 %) |
| Pressure | none | plum creep at 38 % from the cage base, dread shadow ahead of each head, drain ring on the DOWN Site |
| Occlusion | none | ground marks hidden by `occluder_mask.png`, with a 0.55 x-ray ghost (my addition, see weak points) |
| Tally | 12 waxy marks in a tray, hairline diff | **pictogram row**: five fixed tier columns, tier tile x count, no panel (soft ink pool only) |
| Hand | tray + cards | pictogram-only cards (type tab with head silhouette, big ink verb glyph); no tray |
| Discs | glyph + 3 tiny pips | scene pictograms (card drops onto a socket / wall + pause / old hex to new hex / crossed Site to HOME) + 3 tier tiles above; word on hover only |
| Ultrawide / 4:3 | mirrored, blurred mock-up | **real city** (see build item 13) |

## The fixes to the iteration-1 weak points
1. **Uncommitted needs a second channel.** Preview carriers (ring, block, tile) now carry three cues: dashed white outline, a 7 px diagonal **white hatch** over the band or plate, and a **pulse halo** (a soft white glow band 5 px outside the carrier, 0.8 Hz, 60 to 100 %; the stills show the 100 % phase). Committed carriers have none of the three. At 1920 the hatch and dashes read; at 320 px the pulse halo is the only survivor (a bright blob beside a clean mark) and at 1280 hatch plus halo survive, dashes do not.
2. **Tally diff tangle.** Replaced by columns: five fixed tier slots; before count = small ghost token on the top row, after = full token on the bottom row, a chevron joins them, a signed delta (+2 / -1) marks each column that changed. At most five things to read however many of the 12 outcomes move. Identical rows show a single "=" badge. Sealed / hunter inspect shows the lit share as the count plus a 12-pip bar (n of 12).
3. **t1 cluster.** Towers ranked (only t1_c / t1_b / t2_intel bright), tiles fanned at 70 px, old-ring ghosts kept thin. Still the densest spot (see weak points).
4. **Discs at rest.** Pictogram scenes, bigger (r66), outcome tiles in the same hex grammar as the map. Verified at rest in `04a` to `04d`, word on hover only.
5. **Hand / tally trays pictogram-only.** No trays, no text; numerals only on counts, HUD and the HOME chip.

## Sequences (all rebuilt on the P2 base)
| Sequence | Frames | Board |
|---|---|---|
| Flow filmstrip (new) | `frames/flow/` F1 plan, F8 placed, F11 commit, F12 run (clean + annotated); F2 to F7, F9, F10 are the sequence frames below | `boards/00_flow_board.jpg` (12 steps) |
| 1 Hover / focus | 01a Site, 01b beam, 01c card, 01d HOME | `boards/01_focus_board.jpg` |
| 2 Drag and drop (7 reasons: match, wrong type, none, same, occupied, 2-guard limit, cancel) | 02a to 02i | `boards/02_drag_board.jpg`, `boards/02j_reasons_board.jpg` |
| 3 What-if scrub | 03a t3_c, 03b t2_virus, 03c t1_c, 03d t3_b (no change) | `boards/03_whatif_board.jpg` |
| 4 Response discs | 04a DEPLOY, 04b HOLD, 04c MOVE, 04d SACRIFICE | in the focus board |
| 5 Sealed / hunter inspect | 05a lock, 05b hunter eye, 05c Site to locks | `boards/05_sealed_board.jpg` |
| 6 Controller / keyboard | 06a order, 06b snap, 06c prompts, 06d wheel, 06e cycle, 06f map | `boards/06_input_board.jpg` |
| 7 Layouts | 07a 1280 native + board, 07b 4:3, 07c ultrawide, 07d nesting | |
| 8 Onboarding | 08a to 08d, ghost hand 08b_demo_1..4 | `boards/08_onboarding_board.jpg` |

`squint/` = normal | 320 px | blur 4 | deutan | tritan for 11 key frames; `sims/` = full-size deutan and tritan of the same. The interaction grammar, states table and input map of P1_interact/NOTES.md are unchanged (lime = focus as brackets, one refusal mark, one dim ladder); read that file for them.
Numbers (outcome tiers, stops) remain illustrative (`ix_lib.BASE12`).

## Build spec (12 items of P1 stand; additions and changes)
P1 items 1 to 12 unchanged (drop_class reason enum, whatif, stable outcome identity, focus model, hover = focus, carried-card state, response_preview, sealed inspect queries, layout services, onboarding flags, input actions, tests). Changes and new items:
- **6b. Tally is five counts.** `whatif` / `response_preview` only need per-tier counts for the tally; the stable per-outcome list is still needed for the lock / hunter lit share.
- **13. Extended world for non-16:9.** Camera at the same zoom, centred so the 4:3 box holds HQ and HOME; ultrawide just widens the viewport (world continues, no UI). Frames here use an approximation outside the P2 capture (fitted colour map on the raw plate); the Godot render replaces it. HUD / hand pin to the 16:9 or 4:3 box.
- **14. Preview channel (art-owned shader).** `tide_fx` preview flag on ring / block / tile materials: diagonal white hatch 7 px at 28 to 55 %, dashed outline, pulse `0.8 Hz, 60 to 100 %` on the halo; reduce-motion = pulse frozen at 100 % (hatch + dashes carry it). Committed = flag off.
- **15. Ground-mark occlusion with x-ray ghost.** Ground marks use the depth holdout (hag > 1.5 BU, class 2) at 0.55 gain instead of fully hidden. Confirm against P2_plates.
- **16. Pressure layer** (plum creep 38 %, dread shadow 220 px at 38 %, drain ring) is the P2 plate layer reused unchanged in the interactive scene.
- **17. Tally token = the Site tile** (same hex, glyph, solid / hatched variants) at r25 plus a count numeral; zero counts at 22 %.

## Self-score against the REF_BASELINE bar (honest)
- **Readability 8** (bar 9, not beaten). Gains: ranked towers and the 13.6 px rings give the Sites a presence at 320 px (the SITES LOST ink ring is the darkest mark and reads as a hole); HOME ring reads first; the tally is five items. Holds it back: at the 320 strip the preview carriers survive only as a halo blob, the hatch and dashes vanish, the tally tokens are too small to read, and the pad / MATCH marks in 02a, 01c are small; under tritan the DAMAGED amber, SITES LOST ochre and E yellow still sit close and rely on the ink / pattern.
- **Wordlessness 9** (bar 9, matched, provisional). No words in clean frames besides numerals (counts, deltas, HUD) and the disc word on hover. The disc word is the one exception; the pictograms carry the discs at rest. No naive viewer has tested it.
- **Visual quality** is now one look with the plates (same city, heads, palette, mark specs), so the critic's consistency finding is closed on paper; the P2 plates were not yet readable when this was built, so the match is to the contract, not to rendered plates.

## Weak points
1. The 320 px squint still loses the uncommitted channel except the halo; the pulse is untested in motion.
2. The t1 cluster is better but still the busiest 300 px (ring, block, tile, old-ring ghost, brackets, tower, readout).
3. Tally tokens are readable at 1920 only; at 1280 the five-column row needs the grouped form at r >= 25 px and about 590 px of width.
4. Ground-mark x-ray ghost (0.55) deviates from the plate rule (hidden); needs a ruling.
5. Extended city is an approximation (fitted colour map, no warmth field / signage / wet gloss); the seam is hidden by a smooth correction but a Godot render must replace it. The left of the ultrawide is the river bank, so the extra width is asymmetric.
6. SITES LOST under deutan / tritan: hatch, ink fill and glyph carry it, hue does not.
7. Delta numerals (+2 / -1) are small; sign is the only channel (no hue), fine for colour blindness, weak at squint.
8. Hand cards keep the bone paper of the pass-2 kit; the 18 px soft shadow is lighter than the contract in some frames.
9. P1 weak points still open: snap radius, deadzone, ghost-hand timing, pad glyph legibility on a real device, lifting sealed corridors on narrow streets.
10. Illustrative outcome model (12 outcomes, MOVE12 etc.) is not the rules.
11. The what-if scenario story is not fully consistent between frames (03 starts with the K1 stop at t1_c as SITES LOST, flow F8 shows it HOLDS after the drop).

## Process notes
- Slip against the hard rules: one bare `python -` with an empty heredoc was started once by mistake (interactive banner, exited at EOF, no code run). No python process of mine remains.
- Another slip: a patch script truncated my own copy of `scripts/ix_lib.py` (write failed on a non-cp1252 character); I restored it from the P1 original and re-applied the edits. Nothing outside P2_interact was touched.
- Wrote only to `P2_interact/` and my cache `D:/rc_scratch/tide_concepts/p2i_work/`; read-only use of `p2_base`, `plates`, P1_interact scripts, P2_plates (not even read) and D:/Godot/rebel_cell (not touched). Deleted only my own temp scripts by name.
- Rebuild: `python ix_a.py; ix_b.py; ix_c.py; ix_d.py; ix_f.py; ix_e.py; ix_h.py; ix_g.py` from `scripts/` (`p2kit.py` = the contract marks, `extcity.py` = the real-city extension).
