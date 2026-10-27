D: 39/50 (W8 P8 N7 D8 C8) · S8 V7 Fit7 · Vision 7 · Hack 9 · PASS (hunter lock weak)
E: 37/50 (W7 P7 N9 D7 C7) · S9 V8 Fit7 · Vision 7 · Hack 10 · PASS (best sealed/hunter reveal; forecast tiers off-route)
F: 38/50 (W8 P8 N7 D8 C7) · S8 V7 Fit8 · Vision 8 · Hack 6 · PASS (best forecast; beam types never co-visible)
A: 38/50 (W8 P8 N7 D7 C8) · S7 V7 Fit6 · Vision 8 · Hack 3 · PASS with fixes (round-1 score kept; sealed/hunter reveal still a letter bubble)
B: 31/50 (W6 P6 N6 D6 C7) · S7 V7 Fit8 · Vision 5 · Hack 7 · MARGINAL (round-1 score kept; sealed/hunter fail)
C: 38/50 (W7 P8 N8 D8 C7) · S8 V7 Fit6 · Vision 4 · Hack 2 · PASS with fixes (round-1 score kept)
Shipped baseline: 31/50. Scores are honest, not generous: D, E and F are close, and none is a finished answer. The designer's hybrid beats all of them.

Coverage and method. I viewed every beat frame, panels-removed frame and reveal frame (D 12/13, E 12, F 12) for D, E and F, looking at pixels. For A, B and C I looked at the compare sheet plus A's forecast, HOME hit and all-panels-removed frames, and carried the round-1 CRITIC.md scores and notes forward (A/B/C were judged in round 1; I re-checked A visually, and B/C only on the compare sheet). Squint and colour-blind: I viewed the D, E and F deutan forecast sims and judged the squint behaviour from the frames, not every strip (the squint strips themselves were not opened). The shipped plate folder was listed but its images were not opened; the 31/50 baseline is the earlier REVIEW score.

References used (web search was thin; the rest is my own knowledge and is flagged):
- Cyberpunk 2077 Breach Protocol: a design write-up praises the side-by-side matrix and buffer, but a new player is confused by the yellow "next row/column" outline. Lesson: one highlighted next step beats a grid of options. [Prima Games](https://primagames.com/gaming/cyberpunk-2077-hacking-breach-protocol-guide), [Superjump](https://www.superjumpmagazine.com/how-games-can-give-insights-and-solutions-to-ux-problems/). Avoid its code-matrix puzzle; E and D both avoid it.
- Watch Dogs ctOS profiler: tags on targets over a living city; the search found no readability critique, so the clutter claim is my own play knowledge. [NoobFeed](https://www.noobfeed.com/news/watch-dogs-2-will-feature-an-updated-profiler-system)
- From knowledge, not searched: Tron (emissive line on dark ground; D and E), Into the Breach (intent tile with number on the target; F forecast), Google Maps 3D (route ribbon; A), Mini Metro (a few clean lines; C), Jet Set Radio (heavy outline round every paint mark; F), Ghost in the Shell and Gibson (the data layer sits on the city and does not replace it; E), TIS-100 and Shenzhen I/O (parts as pictograms plus waveform; D).

---

## 1. The pass/fail check (every panel removed)

Test: could a player run a whole raid with every panel removed? I checked the sealed route and HUNTER reveal specifically.

- **D: PASS, with a weak hunter.** Frame 11 differs from 04 only by dropping the hand, the analyzer strip and the go button. The map keeps the waveforms, the probe tiles (1, 2, -4) and the HOME ring ticks. Sealed reveal (12): lock A opens, a yellow sawtooth runs the real route home, and the lock plate shows the E glyph. This reads wordlessly. Hunter (13): a small cluster of yellow sparks at the fork, with no obvious "one of two streets" lock. It is the weakest hunter solve of the three.
- **E: PASS, the strongest reveal.** Frame 12 is the best answer in either round. A fog corridor with a letter lock opens into a yellow E ram daemon with its hazard blocks. B and C stay fogged. The hunter eye drops a reticle on one street while the other fades. Frame 11 drops only the hand. Weak spots: the forecast (04) shows its outcome tiers on a bar group at the far left plus small chips on towers, not on the route. The INFECTED tally in the top-right HUD is nine empty cells with a "0", so the 2-vs-8 balance is hard to see at a glance.
- **F: PASS.** Frame 11 drops the launch/back chips and the outcome strip, and the tile-per-target forecast still works. Sealed (12): lock A opens with a bit burst and lights the E route as a chevron band. B and C remain locked, and the hunter eye's brackets snap on one street while the other is crossed out. The grease tally at HOME, a 12-glyph row of tier shapes, is itself a good odds bar. But 11 only removes a strip, so it proves less than D's or E's.
- **A: PASS with fixes.** Frame 10 is a real removal, but the sealed A/B/C bubbles and the hunter "Y" are letters. A first-time player needs a tutorial for the 4-pip tier bars.
- **B: MARGINAL.** The all-panels-removed frame is byte-identical to the forecast, and the hunter and sealed routes never appear.
- **C: PASS with fixes.** The sealed B is a hollow circle and the hunter two dotted threads. The three outcome dots under each response disc have no legend. The best forecast of round 1.

## 2. Direction by direction (the pixels)

**D Circuit Board (39).** The copper PCB layer under the network is the most distinctive "this is a cyberpunk hack" image of all six. HOME as a hand-soldered green rebel board with a dashed ring, Sites as IC chips with legs, and beams as oscilloscope pulses (D sine, N square, E sawtooth) give a shape code that holds under deutan: in the sim the blue sine, the pink square and the gold sawtooth stay distinct as shapes, and the waveform survives where the hue does not. Frame 04 is a very good forecast: each beam runs to the fuse, hits a stop bar, then goes to a dashed flatline. The logic-analyzer strip (a lane per beam: waveform then outcome badges, sealed lane = static forking to three badges) is a real wordless forecast, but it is a panel. Playout: the white-teal shield burst on the fuse (06) and the magenta square pulse into a white-orange burst at HOME with "-4" and bits (07) are both strong. The plum Voronoi body with a hot hairline front on the board (01) is the best infection read of the three: it sits on the board and eats the traces, and the two DOWN chips take pink X marks.
Weaknesses, honestly:
(a) The copper layer is everywhere, not only under the network. It covers the whole screen at about 40% strength, so the streets that carry the beams are not distinguishable from the decorative traces. This is the most cluttered of the three at HOME and at the t1 cluster. At 320 px the screen is brown-orange noise with a bright blue braid.
(b) The 3D city is dimmed and pushed back. It reads as a texture under a diagram, so the "living city" part of the vision is weaker. There is no traffic or life besides the pulses.
(c) Copper (#C8723C) sits close to the ruled DAMAGED orange (#FF6A1A). A -4 in orange next to copper traces is an own-goal. Any hybrid must move the base network off orange (tin, cyan or gold) or the tier colours lose meaning.
(d) The card hand is bottom-left in a fan and the component pictures (fuse, jumper, capacitor) are tiny at game scale.

**E Jack-in (37).** The most cinematic and the strongest "hacking a corp in cyberpunk" image. The translucent ICE towers rising from rooftops, the cylinder-caged helix HQ with ring cages, the data pillars and the red-orange hazard blocks are volumetric and sit in the 3D camera, so this is the one direction that uses depth rather than flat overlays. This matters to the vision (a 3D camera and a living city). The daemon silhouettes are the best shape code of the round: D is a thin diamond-link chain with a swept-wing arrowhead, N is a braided strand with a square cursor head, and E is fat hazard-striped blocks with a blunt horned ram. They remain distinct in the deutan sim (shapes, not hue). The shield program is a hex wall that shatters with bits on impact; the HOME hit is a magenta DNA braid hitting the deck with orange shock rings and a glitch tear; the aftermath is a corp paper stamp. The CITY LOST frame (plum flood, towers X'd, skull with a haloed ring) is strong.
Weaknesses:
(a) The forecast (04) is the weakest of the three. The tier bars on the left are iso bars with glyphs, but the sites on the route carry only small chips and the "ghost heads" are hard to find. Where a beam ends is not obvious from the map, so W and P are only 7.
(b) The grade is about 25% darker and bluer, so the city loses life. The windows are there but the whole thing reads as a blue blueprint. Hue separation outside the daemons is low: nearly everything is cyan or blue.
(c) The wireframe towers sit on top of the real buildings and occlude them. Clutter at the t1 cluster is moderate: three towers with ring caps plus a firewall plus a flag chip. At HOME it is clean.
(d) The infection tally is tiny.
(e) Build is the hardest: per-Site tower meshes with a shader, a daemon renderer, a post pass (scanlines, fringe).

**F Rebel Tag (38).** The most readable, and the most faithful to the game's own look. The city is regraded saturated and the night is kept, so this is the "living, vibrant" city of the six. The key is the forecast: a clean hex pin on every Site, an intent tile on each target (tier glyph plus colour plus a number) in the Into the Breach manner, "50%" and "100%" marks, a percentage computing look on threatened sites, and the Cell's grease tally at HOME. The tally is a row of 12 tier glyphs (ring, shield, slashed square, broken heart), which is a very good compact odds device and a second channel for colour-blind players. The deutan sim keeps the whole forecast. The wheatpaste verdict poster (orange halftone, broken heart, DAMAGED) is a memorable aftermath. The stencil skull and plum bloom for CITY LOST work. Defence cards as paint (stencil slab = guard in the beam's colour, spray arrow = shift, glitched sticker = ghost) are the most original and the most "rebel cell".
Weaknesses:
(a) The beam types are never seen together. D appears as blue beads in the forecast, E as yellow chevrons only in the reveal, and N as a magenta zig-zag only in the HOME hit. A player cannot learn the type code from one frame.
(b) The sealed band (black bar with static) reads as noise at 320 px, and the paint letters A B C are small and shaky. The hunter eye is a yellow ring with an eye glyph, clear, but the fork is a dashed yellow route.
(c) The paint look is a lot of marks on a busy city. The forecast frame at the t1 cluster is crowded: a magenta stencil, a blue stencil, a teal chip, three hex pins, a ghost sticker, a grease arrow and "50%" labels in about 400 px.
(d) "Hack feel" is lower. It reads as street-art defacement, not as netrunning. The graffiti idea is charming but it is the least "hacking" of the three.
(e) A left legend stack in the plan beat is a panel.

**A Live Nav (38, carried).** The route ribbon with a casing, the ETA traffic colouring along each segment, and the HOME pin with a 12-pip odds bar are the best "what happens where" device. The playout fill, the road-closed mark and the "-4" pulse on HOME (06b) are excellent. Hack-feel is nil: it is a daytime map app, and the near-day grade costs Fit. It is the cheapest to build over the real city.

**B ctOS (31).** Fit 8 for the night-noir city and the building-anchored tags, but the forecast tags carry no meaning without a legend, and the sealed/hunter beats fail. Donor value: the HQ building opening action sockets.

**C War Table (38).** The best puzzle board and forecast language: intent arrows, stacked HOME preview, stamps. But a tabletop diorama discards the 3D city (Vision 4).

## 3. Colour-blind separation

- **Beam types.** D, E and F all separate the three types by shape, so this passes in each. Best: E (silhouettes plus the body), then D (waveforms; the strongest distinction is in the oscilloscope idiom, sine against square against sawtooth), then F (beads, zig-zag, chevron, but never co-visible). A (dashed, double rail, chevron) is good.
- **Tiers.** D adds distinct badge silhouettes (circle+ring, shield, diamond+broken link, hexagon+cracked heart, spiked star). Under deutan the amber and the orange collapse to gold but the badge shapes keep them apart. F has the same shape badges (ring, shield, slashed square, broken heart, octagon X) and the tally order; F survives deutan best. E uses glyphs on iso bars that survive. A's 4-pip bars rely on hue and need a second channel.
- **Tritan.** Teal-blue against the plum is the risk: D's blue beams over the navy city lose contrast. E's blue daemons lose contrast the most (the whole screen is blue). F's blue beads and yellow hunter route stay readable because of the black casing.
- Verdict: F best, D second, E good for beams and weak for the site tiers, A weakest for tiers.

## 4. Infection (plum body with a hot edge)

- D: best. Plum Voronoi on the board, a hot hairline front, dying chips. It reads in the squint test as a pink blob against orange.
- F: very good. Plum-black body with pink veins, drips and a biohazard stencil; on the busy city the shape stays readable because of the hot front.
- E: good in 01 (plum body round the two X'd towers with a ring), but the tally is small.
- A: good (plum body on the daytime grade). B and C: weak.

## 5. Clutter

- **t1 cluster.** E (3 towers, 1 firewall, a flag chip) is moderate. F is the most crowded (stencils, hex pins, labels). D is cluttered because chips, traces and pulses all stack, and the copper makes it worse. A has pins, bubbles and an overlapping ribbon; it is tolerable.
- **HOME.** E and F are the cleanest. D has the HOME chip but the dense traces behind it. A's HOME pin with the odds bar is fine.
- Squint: E and A hold up best (one dominant braid or ribbon). D at 320 px collapses to copper noise, which is the main reason Fit is 7.

## 6. Buildability in Godot over the real 3D city

Lowest risk first:
1. **A** (ribbons and pins on the existing streets): low.
2. **F** (screen-space hex pins, tile sprites, decals, a paint shader on cards): low to medium. The paint and poster are screen-space overlays, not world-attached; the brief's note applies.
3. **D**: medium. A trace layer needs a mesh or decal on the street polylines (not the whole city), chip meshes on the Sites, a waveform shader on the beams. The all-city copper layer is purely decorative and should be dropped.
4. **E**: high. Translucent tower volumes per Site (a shader with edge lines), a daemon renderer with three head meshes, scanline/fringe post. It is the biggest win for the 3D camera and the biggest cost.

---

## 7. Per-element table (best direction's solution, with evidence)

| Raid element | Best solution | Why (frame) |
|---|---|---|
| City grade / base layer | F: saturated night regrade, windows blooming, real city on top (`F_rebel_tag/04_forecast.png`). Runner-up E's colder grade for the jack-in moment only. | The city stays vivid, so the "living" part of the vision holds. D's dim city and E's darkened blueprint both lose it. |
| Network layer | D, but only along the real streets, not city-wide (`D_circuit_board/frames/03_plan.png`). Alternative: A's cased route ribbon. | Traces under the beams make the network feel like hardware, and vias at junctions are a good anchor. Strip the decorative copper off the rest of the screen. |
| Beam rendering and type shapes | E's daemon silhouettes for the head (`E_jack_in/frames/04_forecast.png`, `12`); D's waveform body as the secondary cue (`D_circuit_board/frames/04_forecast.png`). | E gives the clearest head silhouettes, D's waveform body is a second shape channel, and both survive deutan. Pick one body style, not both (see conflicts). |
| Sealed-route reveal | E: fog corridor + letter lock opens into the type silhouette (`E_jack_in/frames/12_reveal_sealed_hunter.png`); D's lock plate with the E glyph as the compact HUD echo (`D_circuit_board/frames/12_sealed_reveal.png`). | Wordless, shows the type, and B/C stay fogged. |
| HUNTER reveal | E: eye drops a reticle on one street while the other fades (`E 12`); F's crossed-out second street is the cheaper variant (`F 12`). | D's hunter frame (13) is the weakest; do not use it. |
| Defense cards / placed defenses | E for placed programs (hex firewall wall in the beam's type colour, on the Site tower; `E 03`, `E 06`); F for the card hand (vinyl in the beam's colour; `F 03`). | The wall shatters on impact, the card is colour-coded to the beam it stops. D's component pictures are too small. |
| Forecast / odds | F: intent tile per target (tier glyph + number) plus the grease tally at HOME (`F 04_forecast.png`); A's traffic-coloured route as the route-side channel (`A 04_forecast.png`); D's flatline-at-the-fuse idea for a stopped beam (`D 04`). | Odds live on the target and on the route; both stay readable under deutan. D's analyzer strip is accurate but a panel. |
| HOME damage preview | D: orange ticks on the HOME ring with a "-4" chip (`D 04_forecast.png`); A's 12-pip bar on the pin as the compact alternative. | The ring is a Frostpunk-style gauge, diegetic, and the ticks are the same ticks that leave in the HOME hit. |
| Response choice | F: four stencil discs with a glyph and one word, three tier glyphs above each, lime on the pick (`F 05`); E's keycaps are equivalent (`E 05`). | The three outcome glyphs above each choice are the wordless part; the lime halo follows D25. |
| Playout impact | D/E: white-teal flash with a shield on the guard and bits (`D 06`, `E 06`); F's glass-shatter with paint is the louder alternative (`F 06`). | A hex shield flash with bits, ruled and reusable. |
| HOME hit | D: pulse hits the rebel chip and bursts in white-orange with "-4" and bits (`D 07_playout_home.png`); E's glitch tear is the add-on (`E 07`). | The strongest single signal in round 2, and A's `06b` is still the cleanest "-4" read. |
| Aftermath / DOWN / TAKEN | F: wheatpaste verdict poster plus D28 marks plus the dashed red clock ring on DOWN sites (`F 08_aftermath.png`); E's paper tag is the cheaper stamp (`E 08`). | A verdict word on a tier-coloured stamp, and the clock ring shows "next raid = TAKEN". |
| Infection | D: plum Voronoi body, hot hairline front (`D 01_decay.png`, `D 10`); E adds the tower stump (`E 01`). | Reads as a body, not a disk. |
| HQ step | E: action coins around HOME and a cable to the DOWN Site that ghosts it rebooted (`E 09_hq_step.png`); F's spray menu with the mint ghost is equivalent (`F 09`). | The consequence is previewed on the target. |
| CITY LOST | F/D: plum flood with veins, big skull, balance tipped (`F 10`, `D 10`); E's haloed skull with a glitch tear (`E 10`). | Pick the plum flood from D (cleanest) and the skull from E. |
| The HUD | F: HOME/HEAT chips top-left, the INFECTED-vs-healthy counter top-right with the biohazard glyph (`F 04`); A's panel for the longer bar is a fallback. | E's top-right counter is unreadable; D's is clean but lacks the balance glyph. |

## 8. Hybrid recipes (ranked)

### Recipe 1 (recommended): "Jack-in over the Night City"
- **Thesis:** the real vivid night city, with the Cell's jacked-in data layer on top. Volumetric daemons run the streets, and the forecast sits on the targets.
- **Base:** E (3D data volumes, daemons, reveals) on F's city grade.
- **Take:**
  - from E: ICE towers on Sites only, daemons, the sealed/hunter reveal, the HQ cage, the programs;
  - from F: the saturated regrade, intent tiles with numbers, the grease tally at HOME, the verdict poster;
  - from A: the route's traffic colouring and chevrons as the line under each daemon;
  - from D: the HOME ring with ticks, the plum Voronoi infection, the HOME hit.
- **Drop:** E's global darker blue grade, the left iso bars, all D copper decoration, F's paint-on-everything and the left legend stack, A's daytime grade.
- **Predicted score:** 43/50, S9 V8 Fit8, Vision 9, Hack 9.
- **Build risk:** medium-high. The tower volumes and the daemon renderer are the cost; fall back to flat pins plus daemon heads if the volumes slip.

### Recipe 2: "Street Hack Circuit"
- **Thesis:** F's clean readable night city with a copper trace layer on the raid streets only, and waveform beams.
- **Base:** F.
- **Take:**
  - from D: PCB traces on the streets under the beams only, IC-chip Sites for the t1 cluster, waveform beams, HOME as a soldered rebel chip, the ring ticks, the plum corrosion;
  - from F: tiles, the tally, the stencil cards, the poster;
  - from E: the sealed/hunter reveal.
- **Drop:** D's city-wide copper, the analyzer strip (the tally replaces it), F's hand-lettered sealed band (E's lock plus D's lock plate replace it), copper in orange.
- **Predicted score:** 42/50, S8 V8 Fit8, Vision 8, Hack 8.
- **Build risk:** medium. The waveform shader and a trace decal are modest; the cost is moving D's chip art onto the real Site markers.

### Recipe 3: "Safe Nav" (the low-risk version)
- **Thesis:** A's route ribbons and pins on a night grade, with F's tiles and E's reveal, so it can ship even if the 3D volumes slip.
- **Base:** A, regraded to night.
- **Take:**
  - from F: intent tiles, the tally, the poster;
  - from E: the sealed/hunter reveal, daemon heads on the ribbon;
  - from D: the HOME hit, the plum infection;
  - from C: the stamps.
- **Drop:** A's day grade, the left route legend, the bubble letters.
- **Predicted score:** 41/50, S7 V7 Fit7, Vision 8, Hack 6.
- **Build risk:** low.

**Ranking:** 1) Recipe 1, 2) Recipe 2, 3) Recipe 3. I recommend Recipe 1 and prototyping Recipe 3's route-layer first, so the 3D data layer can be added on top without rework; if the daemon renderer proves too costly, Recipe 2 is the fallback with the least regret.

## 9. Conflicts (elements that do not combine)

1. **Two base layers.** D's city-wide copper, E's blue wireframe towers and A's daytime grade all try to own the base image. Choose one grade (F's saturated night) and let the others be accents on Sites and streets only.
2. **Beam body.** E's daemon, D's waveform and A's ribbon are three different line-and-body systems. Use one body (the ribbon or the waveform) with the daemon as a head silhouette only. Do not draw an E body and a D waveform on the same street.
3. **Orange collision.** D's copper is nearly the DAMAGED orange. If D's traces survive, they must be tin, cyan or gold.
4. **Yellow overload.** E beam is ruled signal yellow, and E's and F's hunter eye and D's lock highlight are also yellow. Keep the hunter eye white or cyan-white so it does not read as an E beam.
5. **Hand-made against corp-clean.** F's paint marks and D's pristine chips do not share a language. If both appear, the Cell's marks are paint and the corp's marks are vector, and the Sites must stay vector.
6. **Three sealed-route grammars.** D's lock plates, E's fog corridor with a letter lock, and F's censor band. Use E's.
7. **Two HUDs.** E's counter and F's are not interchangeable; keep F's.
8. **Panels.** D's analyzer strip and F's outcome strip and left legend are both panels. Keep only one (F's tally replaces the strip), and delete the legend; the brief's hard fail applies.
9. **Depth against paint.** E's volumetric towers occlude the buildings and F's paint overlays are screen-space; they will fight over the same pixels at the t1 cluster. Limit towers to Sites and keep stencils on the ground ring.
