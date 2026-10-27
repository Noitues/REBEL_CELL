A: 38/50 (W8 P8 N7 D7 C8) · S7 V7 Fit6 · Vision 8 · PASS (with fixes)
B: 31/50 (W6 P6 N6 D6 C7) · S7 V7 Fit8 · Vision 5 · MARGINAL PASS (forecast and sealed/hunter beats fail wordless)
C: 38/50 (W7 P8 N8 D8 C7) · S8 V7 Fit6 · Vision 4 · PASS (with fixes)

Ranking: 1) A, 2) C, 3) B. A and C tie on the rubric. A wins because the designer's stated vision (a living city street map seen through a 3D camera) is what it delivers, and it is the cheapest to build over the real 3D city. C is the better puzzle board and should donate its forecast and verdict language.

Shipped baseline for reference (earlier critic, REVIEW.md): 31/50, S6 V6 Fit7. A and C beat it by 7 points. B only equals it, and its gains in look are given back in information.

Coverage: I inspected every beat frame of A, B and C (decay, draw (A, B, C), plan, forecast, response, both playouts, aftermath, hq_step, city_lost, panels-removed), the NOTES, and the deutan/tritan sims of forecast and playout for B, and forecast for A and C. I looked at the squint strips only for A forecast, A plan blur, B forecast blur and C forecast. The shipped plates (D:/rc_scratch/tide_concepts/plates/shipped/default) came back "media removed", so shipped-screen comparison rests on the earlier REVIEW.md, not fresh eyes. Squint judgments on the others are inferred from those strips and the frames themselves.

References used (web search was thin; most points are from my own knowledge, flagged):
- Into the Breach: critics credit fully telegraphed enemy actions on the board with a crystal-clear UI (GameSpot, Game Developer, Critics at Large). Telegraphing only works because enemies pre-commit; our sealed A/B/C and hunter are the opposite, so the sealed beat is where this game cannot copy ITB. [GameSpot](https://gamespot.com/reviews/into-the-breach-review-a-mechanized-masterpiece/1900-6416865/), [Game Developer](https://gamedeveloper.com/game-platforms/road-to-the-igf-subset-games-i-into-the-breach-i-)
- Watch Dogs ctOS profiler: tags on targets with info bars (NoobFeed). Web search found no readability critique, so the claim that profiler tags clutter in dense scenes is my judgment from play knowledge. [NoobFeed](https://www.noobfeed.com/news/watch-dogs-2-will-feature-an-updated-profiler-system)
- Google Maps / Apple Maps / Waze / Cities: Skylines / Frostpunk / Mini Metro: knowledge, not re-searched. Maps: one cased route, one destination pin, one colour per segment. Mini Metro: a handful of flat lines, never more than the player can count. Frostpunk: one big gauge, not a ledger. Skylines traffic view: colour carries state per road segment.

---

## Pass/fail: could a player run a whole raid with every panel removed?

Honest answer for all three: they can run the known part. None fully survives the sealed-route and hunter beats without text, and none shows how the DEPLOY choice differs from HOLD beyond an icon.

A: PASS. The "ALL_PANELS_REMOVED" frame (10) really has no route list or hand, only the HUD, ribbons, ETA bubbles, pins, and a go button. Where a player gets lost without text: (1) the sealed A/B/C ETA bubbles ("A 4 pips") need a first-time explanation; (2) the hunter "Y" fork bubble is a letter, not a reading; (3) tier pips are four tiny coloured bars, a legend-dependent code; (4) at HQ step the five coins are icons plus prices and the wrench vs "card with red X" vs snowflake needs one tutorial. Otherwise decay, draw, plan (drag arrow, drop rings, lime), forecast (traffic colour), playout (fill progress, road-closed, orange pulse), aftermath (stamped tag) all read.

B: MARGINAL. The all_panels_removed file is byte-identical to forecast.png. That is honest (the frame had no panels to begin with) but proves less than A's and C's explicit before/after. Lost without text: (1) the forecast shows amber tags with 33 / 50 / 100 and nothing about which beam, which type, or what the number is the chance of; (2) only one blue conduit is visible in plan, forecast, response, so D/N/E shape heads and the sealed routes never appear in the frames I saw; (3) the hunter is invisible; (4) HQ step sockets with "10/20/25" costs read only if you know the wrench glyph. The "HOLDS" verdict is the one big word on screen.

C: PASS. Frame 11 is the plan beat with hand and tray removed, and the hand is the only thing that carries which card is which, so a player does lose card identity; the map alone carries rings, stickers on tokens, lines. Where a player gets lost: (1) the card verbs GUARD / SHIFT / JAM labels plus four response verbs are words (allowed), but the stickers on tokens are small; (2) the sealed B is a hollow circle with a letter, the hunter two dotted threads and a crosshair, the weakest mark in the set; (3) the three-dot outcome preview under each response disc is a tier-colour code with no legend; (4) "-6" and "1" arrows read instantly. Best wordless forecast of the three.

---

## Direction A: Live Nav (38/50)

W8 / P8 / N7 / D7 / C8. S7, V7, Fit6, Vision 8.

What works in the pixels: the ribbons are the loudest thing in every frame and they read like a route. Type is shown by pattern, not hue alone: D is a chunky dashed blue ribbon, E is a white chevron ribbon, N a double rail. In the forecast the ribbon is recoloured by outcome tier along its length, so mint changes to amber and then orange as it nears HOME, and a teal stretch marks where a guard stops it, then a grey dotted dead segment. This is traffic colouring, it is the one place in all three directions where "what happens and where" lives on the route itself, and it holds at 320 px and under 4 px blur (the orange run into HOME is the dominant blob). The HOME pin carries a 12-pip odds bar, which is a fine compact P device. The playout is strong: ribbon fill with a puck head, hex shield flash and bit burst on the barrier, "road closed" sign, then an orange pulse ring and "-4" on HOME in 06b, the strongest single signal across all frames of all directions. The aftermath stamped tag, the quarter-ring decay clocks on DOWN pins and the Bloom reads right.

Infection: plum-black body, pink Voronoi veins, white-pink rim front, clearly a bounded necrosis, not a disk. City lost floods it with a black plum field, white skull and red vignette; the skull on 09 is huge and fills the screen, which is dramatic and obeys "skull glyph". The N beam never has to read against plum, because the forecast is tier coloured and N is a rail pattern.

Problems:
1. Fit6, and the biggest: the plate is regraded to a lavender, almost-daytime grade (steel blue towers, lit windows washed out). The brief says "the Grid stays night" and the shipped game is deep violet noir; this looks like a different, lower-contrast game, with the neon netwire barely distinct from the towers. Vibrant, yes, but it loses the night mood that sells the cyberpunk. The notes call this a deliberate departure; I would take the vibrancy from saturation and window bloom, not from raising the whole exposure.
2. The "route ribbons laid on the actual streets" claim is only partly true. The ribbons follow the net lattice over the building tops (diamond lattice), not the street grid visible in the plate, so the Google Maps trick of a route hugging a real road is not delivered; it is a netwire route.
3. Density at the t1 cluster near HOME in plan and forecast: pins, barriers, a Y bubble, B and C bubbles, the plum patch and two ribbons overlap on one junction. A pin and a hex barrier stack at about 60 px spacing.
4. E is chalk white. On a pale ribbon casing over a pale base it is the weakest contrast; "untouched" mint (B8FFF2) is also near-white, so on the forecast the E route and an untouched segment are close in value (the shape, chevrons vs square dashes, saves it).
5. Colour-blind: in deutan, amber and orange collapse to one yellow and mint collapses to white (the forecast reads yellow vs white: still "bad vs fine", but SITES LOST vs DAMAGED gone). In tritan, orange and amber go salmon-red and read as BREACHED red; a held raid could look red there. Shape cues (dash, rail, chevron) hold.
6. Frame defects: the aftermath tag text "DAMAGED" is clipped by its own stamp border ("DAMAGE" + a sliver of D); the junction lens in 06a is a soft blur and covers the Bloom; the route-list chip stack bottom-left in plan and forecast is a (icon-only) panel, which should become chips at the origin pin before this is called "no panel".
7. HQ step (08) is the weakest beat: five coins with prices and a lime ring; the wrench route drawn to the DOWN site is good, but the choice among five has no consequence preview.
8. D (decision depth 7): the guard on the ribbon, the 12-pip bar and the HOLD/MOVE/DEPLOY/SACRIFICE chips show that choices exist, but the response frame shows no per-option outcome change; the lime ring on HOLD is only a selection.

Squint: forecast and plan read as two ribbons; the hand and chips merge to one dark band; the big orange run at HOME in forecast, the orange burst in 06b and the skull in 09 are first reads. 08 is the weakest.

Buildability in Godot: cheapest of the three. Cased ribbon with arclength and lateral coordinates is a standard shader on the existing link polylines (the plate coordinates already exist); pins, bubbles and the HUD are Control or Sprite3D with billboards; Bloom is the existing Bloom A necrosis shader driven from TAKEN sites. Risks: lane offsets when five routes share a street, ETA bubble declutter, and the colour grade, which is a global post change that touches every other screen if not scoped to the raid camera. Traffic dots with trails are optional polish. The lens needs a second camera render target; cut it or fake it.

---

## Direction B: ctOS Profiler (31/50)

W6 / P6 / N6 / D6 / C7. S7, V7, Fit8, Vision 5.

What works: it looks the most like the existing game. The night grade is faithful, the CRT chips, vinyl cards and D28 pencil all fit, and the plan beat is beautiful: a bright cyan conduit loop, yellow pencil drag from the card, lime focus ring. The shield flash in playout_impact is a convincing hex burst with bits (strongest single effect of the B set), and the HOME hit with orange ring, -6 and lilac-white conduit is dramatic. The infection in playout_home (plum clouds with red X's) is the best "plum body, red X" in the set; the city lost frame is a very strong Voronoi flood, skull with plum halo. The squint strip of forecast reads: amber tags, the blue line, yellow HOME ring.

Problems (this is where it loses points):
1. Forecast: ten or so identical amber tags with "33 / 50 / 100". Nothing in the tag says which beam threatens it (no type head colour), nothing says tier (all amber), and "100%" on five tags reads as alarm everywhere. It is the ITB lesson in reverse: a number on the thing, but not the consequence. The brief says forecast = tag with glyph + number + tier colour; the tier colour is absent, and HOME wears a yellow-amber dashed ring that carries no odds. The 12-pip threat dial promised in the notes is not legible in frame.
2. Only one beam type is drawn in the frames I saw (blue conduit). N and E packet heads, the sealed ciphered lines and the hunter reticle, the things the brief requires to differ by shape, are not visible at 1920 and not at all at squint. The notes admit the hunter "is barely visible". So the central rule (types by shape) is asserted, not shown.
3. Decay: the Bloom patch has a thick hot-pink rim all round with a large flat dark body; it reads as a glowing pink-edged disc with some veins, the "flat pink disk" the designer rejected, only less flat. Better in the playout frame, worse here. The notes flag it.
4. Colour-blind: in deutan, tag amber turns yellow, teal and the blue line turn white-blue; D/N/E heads can't be told apart because they are not visible. In tritan the whole map turns cyan, the HOME ring turns salmon red and the "-6" loses its orange. The shield burst separates only by hex cells.
5. The aftermath "HOLDS" slab is a corp-paper-less teal CRT plate, fine, but it covers the very sites that were DOWN; the map near it has two small slashed hexes and a dashed red decay ring that are tiny. At squint, aftermath tells you "teal word", nothing about what was lost.
6. The cyan "edge wire" over buildings, the documented risky departure, is not visible in the frames; the city is just the dim night plate.
7. Vision: it is a dim night plate with glowing icons, not a living vibrant street map. The designer asked for Google Maps; this is closer to the shipped game with better marks.

Buildability: the most expensive/risky per unit of payoff. Per-site profiler tags need per-Site hit odds from the forecast model (new data), tags collide and need a placement solver (crowded on t1_b/t1_c, as the notes say), the scan sweep and edge pass is a screen-space mask effect, packet trains with type-shaped heads on instanced paths, plus a radial dial. The conduit and shield flash are cheap.

---

## Direction C: War Table (38/50)

W7 / P8 / N8 / D8 / C7. S8, V7, Fit6, Vision 4.

What works: the best information design. Forecast is a true ITB board. Thick Mini Metro lines (D blue circles, E yellow squares, N ivory triangles) carry type by shape and by hue, and D blue vs E yellow is the safest colour-blind pair of the three. Arrows land on highlighted targets with numbers: an orange "-6" on HOME with the stacked health preview on the ring, an amber "1" for one Site down, a teal flat-ended arrow with a shield for a stop, the row of tier tiles under the table as the odds. It reads at 320 px (orange blob at HOME, teal and amber arrows). The response frame is the best D device: four round discs with three outcome dots each, lime on the chosen one, so choices visibly differ. The playout impact (hex flash, the pawn toppled with a grease X) and HOME hit (red burst, "-6" luggage tag, HUD number turning orange) are lively; the DAMAGED rubber-stamp tag on corp paper and the CITY LOST stamp with the plum ink spill running off the board onto the felt are the best verdict beats, and the best use of the game's existing paper-and-stamp vocabulary. The HOME ring as a 50-tick gauge is the Frostpunk lesson applied well, and the balance scale for INFECTED vs healthy is a real wordless improvement over the "9 outnumber 8" text.

Problems:
1. Vision 4: this is not the designer's map. A tilt-shift diorama on a table, with beams floating on a Mini Metro grid, no longer reads as "the city". The city is blurred under the marks (up to 8 px), the traffic and searchlights the brief wants alive would be blurred or hidden, and the beams are not routed on streets at all (the notes admit it). It is a board game about the city, not the city.
2. About 40 percent of the screen is table: a dark felt, a stamp prop, a red pencil, a slab edge, and the map slab is a letterboxed strip. The pencil and stamp are decoration that waste space and compete with the HUD. The raid map is smaller on screen than in A or B (the other two crop in at 1.55 to 1.7x).
3. Fit6: it recolours the city to a dusk-purple miniature, and it adds a brand-new prop vocabulary (felt, foam board, ziggurat tokens, round vinyl discs) not in the bible; the sticker, CRT chip, stamp, grease pencil parts do fit.
4. The hunter is the weakest mark in any direction (two thin dotted strings and a crosshair pawn) and the sealed lines are grey dashed paths the rules say should stay hidden.
5. Colour-blind: in tritan the D cobalt turns teal and collides with HOLDS teal; in deutan amber and orange become the same yellow and HOLDS goes grey. The stack-of-squares odds row in forecast loses its tier meaning in deutan (teal vs grey, then four yellows). Shapes, flat-end and numbers still carry.
6. At the t1 cluster, two stickers stacked, a ring, an arrow and a badge sit within about 65 px; the notes say it would not read at 1280.
7. Words are the most numerous: GUARD, SHIFT, JAM on every card plus the four verbs plus DAMAGED. All allowed, but the card labels are the exact kind of explanation text the designer is against; use the glyph colour code only.

Squint: forecast reads best of the three: yellow loop, orange pin, teal arrows; everything else is one dark band (which is also what it needs). HQ step with three action discs and dashed white arrows is clean.

Buildability: medium to high risk. The tilt-shift on the world layer and a separate unblurred marks layer is a significant rendering change (two layers, depth-of-field per band), the table, slab edge and felt are a new scene, and routing lines in 0/90/iso corners that ignore the 3D net means a second path layout from the one build owns (site_path), plus the Site anchor mismatch the notes report (up to 90 px on t1_b). District tokens replace hexes. The stamps, stickers and grease pencil are existing shaders (cheap).

---

## Recommendation

Winner: A "Live Nav", carried with a night grade and C's forecast language.

Why not C: it is the better game board but fails the vision brief and shrinks the city; why not B: it is the most faithful to today but is the least informative in the forecast and never shows beam types.

### Top 5 fixes for A before implementation
1. Put the night back. Keep the vibrancy, drop the lavender daytime grade: dusk/night base with window bloom and saturation, the netwire neon, and ribbons that win by casing and glow, not by washing the city out. Test the ribbon contrast on the shipped night plate. This restores Fit and "the Grid stays night".
2. Fix tier and beam separation for colour-blind players. Give each tier a second channel: pip height or hatch density on the ETA bubble and a ribbon pattern change (solid, chevron density, dotted). Move E off chalk white to a hue that is not mint or white (C's signal yellow, which pairs with D blue and survives deutan), and make sure tritan orange vs red is separated by glyph (heart vs skull) not hue alone.
3. Declutter rules at the HOME and t1 cluster. A budget of at most N bubbles per junction, collapse barriers to a single stack with a count, and show the full ETA bubble only for the focused or known route; remove the bottom-left route list and put the chips at the corp origin pin.
4. Do the sealed and hunter beats properly, as the one thing no direction solved. Show sealed A/B/C as a single fogged band leaving the HQ with letter locks; at reveal, flash the chosen route; show the hunter as a fork with two street ghosts that lock on one. Show that the hunter route is last, and keep the hidden paths hidden.
5. Strengthen consequence and decision beats: give each RESPONSE chip a three-dot (or ribbon-preview) outcome like C's discs, make HQ step show the effect of each coin, fix the clipped DAMAGED tag, and render the playout lens properly (or drop it, since the pulse ring on HOME already works). Also make the ribbons hug the real streets where the plate shows them, or say plainly that they follow the netwire.

### Worth stealing from the losers
From C: the ITB flat-end teal arrow, number on the target and HOME stacked damage preview; the round response discs with three tier dots; the INFECTED vs healthy balance scale as a wordless replacement for the counter text; the 50-tick HOME ring; the DAMAGED and CITY LOST corp-paper stamps and plum ink spill; D blue plus E yellow as the colour-blind pair; the toppled pawn and grease X on a stopped beam.
From B: the hex shield flash with binary bits (the best stop effect); the small per-Site percent tag for the hovered or focused Site only; the infection with plum body and red X in playout_home; HQ step as sockets on the HQ and DOWN Sites; the INFECTED cards flying up to the deck strip in decay.

## Self-check on my own scoring
A and C are within noise on the raid rubric; I placed A first on vision fit, "Grid stays night" being the one fixable A defect, and buildability. If the designer cares more about decision depth and wordless prediction than the Google Maps feel, C would rank first and A's ETA bubbles should be replaced with C's arrows. I have not seen motion; every score is of stills.
