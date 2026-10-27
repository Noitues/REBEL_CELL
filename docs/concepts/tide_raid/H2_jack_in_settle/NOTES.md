# H2 "Jack-in over the Night City", concept pass 2 (settle the grammar)

Goal: settle what each mark means and how each beat reads. This is not polish. Pass 1 (`../H_jack_in_hybrid`) is untouched; this set was built from a copy of its scripts. Frames are 1920x1080: `frames/01..12`, `13_declutter_t1`, new `14_response_preview`, `15_hunter_playout`, `16_sentry_shield`; `grammar.png` is the legend board (every mark in normal | deutan | tritan, at game size, on a patch of the real purple city); `squint/` has `_320` and `_blur4` for every frame and the board, `colorblind/` has deutan and tritan sims (Machado 2009) of 04, 06, 07, 12 and grammar; `sheet.jpg` is the contact sheet.

## The grammar in one line each (what the designer is settling)
- **Beam = type.** One cased ribbon per beam, always its pure type hue, never tinted by outcome. Head + body pattern is the second channel: D blue dart on chain links, N magenta block-in-brackets on a braided strand, E yellow bull-horn ram on a hazard-chevron band.
- **Tier = target.** The outcome lives only on the target: a tier-coloured ground ring under the Site, a short tier-coloured stop block laid across the street where the beam stops, and the intent tile (glyph + number). Pass-through Sites carry no mark at all.
- **Towers = quiet.** ICE towers are steel slate (7C88AE), thin and dim, no cyan, no white glow. They give the Sites a body and then get out of the way.
- **Weight ramp = severity.** UNTOUCHED, HOLDS and SITES LOST are dark plates with a coloured edge; DAMAGED is a solid orange plate with an ink glyph; BREACHED is solid red with a second outer hex. Severity reads as weight even with no hue.
- **Yellow = the E type only.** E ribbon, E head, the small E glyph on E cards and E programs. Never a tier, never the hunter, never focus, never a window (the grade still pulls window yellow to warm white).

## Fixes against the pass-1 problems
1. **Cold braid.** Removed the tier-coloured rails and the mint tint from the ribbon (the cause of the cyan merge). Towers moved off cyan to quiet slate and lost their glow (edge glow 0.7/0.5 to 0.3/0.1, white-hot core 0.35 to 0.06, alpha 0.66 to 0.60, HQ cage and conduit rails also slate). Three layers now separate by carrier and value: beam (thick saturated ribbon on the street), tier (ring + block + tile on the target), tower (dim slate wire). At the 320 px strip and the 4 px blur of 04 the three beams stay three distinct hues and the towers drop out.
2. **D blue at the squint.** The cause was the thin dashed links, which dissolved under blur. D is now a continuous band (width 11) with dark cross-cuts, a lighter azure (4690FF, was 3D86FF) and a lower glow, so the body survives the blur; verified in `squint/04_forecast_blur4.png`, `06_..._blur4.png` and in the tritan sims (D reads as a cyan-teal band against the teal-green city, still clearly a body).
3. **Amber vs E yellow.** Both moved: E to FFEE3A (paler, higher value), amber to F29A1A (deeper). Structurally they no longer meet: amber is only in tiles, rings, blocks, tally and poster; yellow is only on E things. dE76 amber vs E: 24 to 44 normal, 12 to 21 deutan (pass 1 was 24 / 12 against the old pair at the closest). Tier glyph (tower-down) stays the second channel, and the weight ramp is a third.
4. **Busy ram.** Heads are now one family of solid silhouettes with an ink outline and a white hot-spot, about 30 px at the frame scale: D dart (swallow-tail), N block cursor in four selection brackets (less plain), E a thick forward-opening "C" bull horn. The same polygons are the type glyph on cards, locks and programs (`glyphs.type_polys`). See the HEADS cell of the board.
5. **D, N, E together.** Plan (03) and forecast (04) now show all three. Known beams: K1 D (the plate's street), K2 N (the plate's second street, re-typed from D), K3 E authored on real streets (core, t3_core, t2_intel, t1_a, home) from the plate link polylines. Outcomes: D stopped by the D guard at t1_c (HOLDS), N lands on t1_b (SITES LOST 1), E handed off to the SHIFT decoy at t2_intel (UNTOUCHED). The HOME -6 chip and the tally still come from the sealed routes.
6. **Kept:** wordless beats, the sealed fog corridor with locks, the white HUNTER eye, F's tiles / tally / stencil discs / poster, D's HOME ring, chip and burst, the plum infection, the declutter rules.
7. **New frames:** 14 (consequence of each disc on the map, 2x2: HOLD baseline, DEPLOY places an N guard so t1_b goes amber to teal, MOVE slides the D guard so K1's stop block and ring move, SACRIFICE puts a grease DOWN on t1_d, clears the HOME ticks and turns the HOME chip mint), 15 (hunter playout: street 0 locked by reticle, other street struck out, the ram is white dashes ahead and yellow behind, ghost trail, impact on the Site), 16 (sentry dome: charged, hit, spent in one raid).

## Other decisions made on the way (each is a candidate for the designer to overrule)
- Cards: the face is neutral bone paper; the type rides on a top tab (type hue + big type silhouette) and the verb glyph is ink. So yellow never fills a card.
- SHIFT decoy: the hologram and the hand-off arrow are neutral white-slate; only the small type glyph carries the hue.
- Heads' ghost-at-the-stop from pass 1 is dropped (the stop block is the end marker).
- Sentry: a Site-local hex dome with a charge pip, white-slate (neutral), not on the street; one beam spends it.

## Decisions the designer must settle
1. **Tier carrier.** Ring + block + tile on the target (this set) vs. also keeping a thin tier rail on the ribbon. This set says no rail; it makes the tier info smaller at the squint (see weak points).
2. **Yellow cards / yellow type tab and the yellow E wall.** Is "yellow = E type everywhere it answers E" acceptable (this set), or must yellow be the E beam only, with card tabs and program edges for E in a different treatment (for example white with the E glyph)?
3. **E hue / amber.** E FFEE3A and amber F29A1A as chosen, or move E toward a colder lemon, or amber toward a redder amber? Deutan amber vs orange still collapses to gold; the weight ramp and glyph carry it.
4. **Head family.** Approve dart / bracketed block / bull-horn C, or ask for another N or E shape.
5. **Weight ramp.** Solid plate for DAMAGED and BREACHED: yes or no. If no, amber and orange rely on the glyph alone.
6. **SENTRY look.** A neutral dome vs. a type-coloured dome; and whether a beam that hits a spent dome passes through (this set does not draw that).
7. **SACRIFICE preview.** Mint HOME chip and a grease DOWN on the sacrificed Site, with an amber dashed arc: acceptable grammar for "HOME takes nothing, this Site goes down"?
8. **MOVE preview.** Ghosted old wall + curved arrow to the new Site; the stop block and ring move with it.
9. **Sealed fog under known ribbons.** The sealed corridors still share streets with the known routes (the lavender speckle halo around the ribbons). Keep centre-lane-under, or draw sealed routes as a brighter strip beside them?
10. **Authoring K3.** The default scenario has no known E beam; K3 is authored by me on real streets. Build must expose an equivalent beam in the lab for the golden plates.

## Self-check (squint and sims, with my honest reading)
- 04 at 320 px and at 4 px blur: D, N, E read as three distinct bodies; the towers drop out; the tier rings are visible as coloured ovals; the amber/teal tiles shrink to specks. Tier info at the squint is the weak layer.
- Deutan: D and N both go blue-lavender, so type there rests on pattern and head shape (dashed-link band vs braid, dart vs block); E stays yellow. Amber and orange both go gold; the solid-vs-outline plate and the glyph separate them.
- Tritan (reviewed, not just generated): D becomes cyan-teal, N becomes red-pink, E becomes cream-white. All three still read as distinct bodies. Risks seen: DAMAGED orange becomes the same pink-red as the N beam and as BREACHED red (07 tritan: the HOME burst and the N ribbon are the same colour; the solid plate and glyph are the separators); HOLDS teal is close to the D band in hue under tritan, but they never share a carrier (tile/ring vs ribbon).
- `grammar.png` normal | deutan | tritan: every mark keeps a unique shape; no two marks rely on hue alone except HOLDS vs UNTOUCHED ring colour, which are different glyphs.

## Weak points (honest)
- At the squint the tier outcome is small: the ring is a thin oval and the tile a small hex. The beam grammar is now strong and the tier grammar is weaker than pass 1's rails (a deliberate trade). Bigger rings, or a ring that fills with the tier colour at the target Site, is the obvious next step if the designer wants it louder.
- The towers are now so quiet that at the squint the Sites vanish and the map reads as ribbons on a city. The Site presence at squint comes from the ring, the programs and the tiles only; healthy idle Sites have no mark except the faint wire. This may be too quiet.
- Sealed fog sits under the known ribbons on shared streets and still produces a lavender speckle halo.
- The N head is smaller and fussier than D and E at the frame scale (bracket corners); the board shows it clearly at 31 px but it can disappear on top of the braid.
- Stills only; ribbon flow, head slither, the E-yellow reveal and the dome ripple are unproven in motion.
- SITE INFECTED in the grammar board is dark plum with a faint front and does not read at the 98 px tile; it reads in 01 and 10 at scale.
- Frames 01 and 10 still use the other plate scenarios (decay, lost) so they have no D / N / E story (as in pass 1).
- The 14 board is a composite of four map crops with a disc badge each, not one frame of a live UI.
- Process slip: I accidentally started a bare `python -` (empty stdin, never fed a script) three times against the rule; two hung and were stopped via TaskStop and one PID (17244) with Stop-Process; I confirmed no `python -` process remains. No work was affected.

## Palette (hex, changes from pass 1 marked)
Night ink 070515 / 0A0C24. **Towers TOW 7C88AE / 55608A (was cyan-white 7FEFFF / 2FB8E8).** Fog 9C8CFF. Beams: **D 4690FF (was 3D86FF)**, N FF40D6, **E FFEE3A (was FFD800)**. Tiers: UNTOUCHED B8FFF2, HOLDS 19C9B4, **SITES LOST F29A1A (was FFB21E)**, DAMAGED FF6A1A (solid plate), BREACHED FF3347 (solid plate, double hex), CITY LOST = HOT FFD6F0 skull on plum. Focus lime C6FF2E only. Infection plum 1A0B1F / 4A1440, vein FF3FA8, front FFD6F0. Paper F6F1E4, bone F6F0DE. DOWN mark F6F1E4, TAKEN mark FF2A3A. Hunter white. Sentry dome white-slate (white .8 + TOW .2).

## Build / Godot look deltas from pass 1
Ribbon renderer no longer needs a per-segment tier rail; it needs a target ring decal, a stop-block quad on the street, a head mesh per type (three polygons are in `glyphs.type_polys`), a dome mesh with a hex clip and a pip, and a tile shader with the weight ramp. Cards: neutral face plus a type tab. Add to the build spec: the sentry state (charged / hit / spent), the SHIFT hand-off event, and the three-option preview per response disc.

## Scripts (`scripts/`)
`hb.py` builds frames 01-13 (`python hb.py [name ...]`); `hb3.py` builds 14, 15, 16; `grammar.py` builds `grammar.png`; `post.py` makes the squint strips, sims and the sheet (needs the frames and the board first); `hy.py` (ribbon, heads, stop block, target ring, tiles, cards), `hz.py` (sentry dome), `glyphs.py` (type family), `cb.py` (colour-blind sims), `colcheck.py` (dE76 pair table under normal / deutan / tritan), `common.py` (world, authored K3), `lib.py` (palette), `scene.py`, `ui.py`, `daemon.py`, `eb.py` are libraries; `cr.py`, `mini.py`, `sqrow.py`, `crop.py`, `sq.py`, `probe.py` are review helpers. Needs numpy, Pillow, scipy; plates from `D:/rc_scratch/tide_concepts/plates`; the static cache is `D:/rc_scratch/tide_concepts/h2_work`.
