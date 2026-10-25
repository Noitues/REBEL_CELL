# REVIEW: MANHUNT (r8). Fresh critic, scrambled frames read before SPEC.md

Verdict: **30/50.** The sweep is a clean, fully telegraphed puzzle and it reads well. Around it sit a weak "why", a playout whose result you already know, and consequences that do not bite. It is not ready to ship as the raid.

## Scores

| Axis | Score | One-line reason |
|---|---|---|
| W what/why/when | 6 | The "when" is excellent (4 cobalt pips plus a shield, a fixed beat). The "why" is not the player's Heat: contact fires every 4 netruns whatever the Heat, and Heat only sets how fast the front moves. |
| P predictability | 7 | At the sweep the forecast is exact (+1 against -9). At route time (frame 2) there is no forecast of raid exposure, and the route panel's Heat numbers (0 / 40) do not match frame 1 (Heat 16) or the rule that running a node adds Heat. |
| N no-words | 6 | The beams (numbered arrows), the good/bad colors, the stamp and the route line all read with the letters scrambled. Ghost, decoy and go-dark glyphs cannot be told apart by purpose. The "alternative plan" panel is not drawn on the grid. The Cell glyph looks like a bomb. |
| D decision depth | 6 | Three levers against a known three-beam pattern give a real puzzle (best beats median by 22; "ghost the biggest" is best only 13 %). But it is fully known and deterministic, and a live exact preview turns it into trying combos until the number peaks. Decoys sit in 77 % of best plans, close to a default. Every value is Schematics, so it collapses to one sum. |
| C consequences | 5 | Legible (red X equals the repair cost). But a perfect evade nets +1, the record ends at 43 Schematics against a 25-Schematics key (losses never threaten the goal), "Cell holds" every time, and nothing persists beyond a currency tax. |
| **Total** | **30/50** | |
| Fit | 6 | "Hiding assets from a sweep with ghosts, decoys and going dark" fits hackers well. "Front" is a wall, not a manhunt: nothing hunts the crew, and the hunter beam is one line in a 4x3 minigame. "Hack toward the core" is well served by the left-to-right lattice. |
| V vs AAA | 4 | The information layout is clean and value is encoded in node size (good). Half of frames 3, 4 and 5 is dead space. The two map spaces (10x3 campaign, 4x3 network) are not linked visually. There is no motion language beyond rings. Next to Into the Breach (sheet) it is a diagram, not a scene. |

Reference sheet: `D:/rc_tmp/raid_design_lab/critic_r8/sheet_manhunt_vs_refs.png`
- Into the Breach: https://upload.wikimedia.org/wikipedia/en/d/d0/Into_the_Breach_Screenshot.png
- Invisible, Inc. (tactical view): https://upload.wikimedia.org/wikipedia/en/9/98/Tactical_View_Invisible_Inc.png
- FTL: https://upload.wikimedia.org/wikipedia/en/d/d7/FTL_Faster_Than_Light_Screenshot.jpg (a combat screen, not the sector map. It stands as a genre reference for the pursuit clock: FTL's rebel fleet is the obvious ancestor of the front.)

Sheet findings:
- **Into the Breach** shows enemy intent on the real board, with the threatened tiles tinted. Manhunt shows its beams on an abstract grid unrelated to the City map you just crossed.
- **Invisible, Inc.** draws vision as filled areas. Manhunt's "near miss" is a thin ring that disappears at 1280x720.
- **FTL** makes the pursuit a spatial threat you can be caught by. Manhunt's front never says what happens if it reaches you.

## Per axis: what gets it to 9

**W (6 to 9)**
- Frame 1: tie contact to Heat visibly. Either the pip count shortens with the Heat band, or the band adds a beam to the next sweep. Show it as "next sweep: 3 beams" beside the chevrons. Today the chevrons (which look like playback speed) are the only Heat link.
- Frame 1: state what the front does to the Cell. Show a danger tint when the hatched band touches the Cell's column. In frame 1 the Cell sits exactly on the hatch line, and no frame says whether that is fatal.
- Frame 3: add a one-glance header on the grid ("Contact 1 of 3, your 7 assets"), as an icon plus a count.

**P (7 to 9)**
- Frame 2: add a third stat to each route card: expected exposure (asset count and total value at the next contact, or the worst-case loss against the telegraphed sweep pattern for that contact). Today greed shows only its upside (25 against 12) and a Heat number.
- Frame 2: settle the Heat math. Say whether the Heat shown is a delta or the end value, and why the solid route is 0 when running nodes adds Heat.
- Frame 5: show the breakdown as a receipt (+6 evade, -3 decoy, -2 dark income = +1). The spec says evaded is +6, and the frame shows +1 with no reconciliation.

**N (6 to 9)**
- Frame 3: draw each lever's effect on the grid, not only in the legend. Beams should pass visibly through ghosts (a beam line under a translucent asset) and stop with a hit spark at the decoy. The black disc should show its lost income as a dimmed coin.
- Frame 3: draw the hunter as specified (dashed), with its full turn path down column 1. Today it is a 10 px stub that reads as a third straight beam.
- Frame 3: replace the "ghost the biggest" text panel with a ghost overlay on the same grid (a toggle or a mini-grid), so you can see the alternative beams hitting three assets.
- Frame 1: swap the Cell glyph. A yellow disc with a fuse reads as a bomb or hazard, not as "you".
- Frame 1: pick a different metaphor for the Heat chevrons. Scrambled, they read as speed buttons (1x to 4x), and they collide with the real playback buttons in frame 4.
- Frame 6: "+51" carries no meaning without words. Show it as a bar against par or against the greedy line.

**D (6 to 9)**
- Hide one element: for example, the hunter's turn rule is known but its entry side is revealed only at playout, or one beam is listed as "row OR column". Then the plan becomes hedging rather than solving, and the playout regains suspense. This makes P 8 rather than 9, a trade worth making (designer decision).
- Make the levers cost different currencies. Ghosting could cost Heat, go-dark income, and decoys Schematics. Then the choice is between resources, not a single sum.
- Frame 3: let network layout come from route choice (assets placed by the column and row they were run in). Then the route decision in frame 2 already shapes the puzzle in frame 3. Today the 4x3 placement looks arbitrary.

**C (5 to 9)**
- Make DOWN matter beyond a fee. A downed asset could stop yielding until repaired, leave a hole in the network that the next sweep's hunter can enter, or (at the core contact) take one key fragment. A loss should change the next decision.
- Make the key bind. A run that ends at 43 against a 25 key means raid losses never threaten the win. Either the key scales or losses come out of the key.
- Frame 5: give a perfect evade a payoff worth chasing (an item or tag, or front pushed back one column), not +1.

## The 3 biggest problems, ranked

1. **The playout is a replay of a known answer.** The forecast is exact, so frames 4 and 5 show nothing new. In a hands-off format the watch phase is the payoff, and Manhunt's has no drama: no near-miss you didn't foresee, no reveal. The "rings = near misses" are cosmetic.
2. **Raids are not caused by the player.** Contact runs on a fixed 4-netrun clock, and Heat only moves the front, which doesn't directly harm you. The causal chain the brief asks for (my Heat leads to this raid) is missing. The real cause is "you have assets", which barely changes from greedy to cautious play, and frame 2 doesn't show how much it changes.
3. **Consequences are a small currency tax with no failure state.** The Cell always holds. Losses come out of a surplus (43 against 25) and do not persist. The best plan pays +1. Nothing a raid does follows you into the next netrun except a number.

Also noted (not ranked):
- The front-vs-Cell rule is undefined.
- At speed 1.0 or more, with the Cell able to move at most one column per netrun, the front can never fall behind. Laying low costs a column of slack every time it is used. The record (frame 6) never lays low and never moves vertically, which suggests the route layer collapses to "advance every netrun, pick the row".

## Rules or rulings I would change (each is a designer decision)

- **Designer decision:** contact cadence or sweep strength scales with the Heat band (for example, +1 beam at Heat 50 or more, contact every 3 netruns at 75 or more). This lifts W.
- **Designer decision:** one sweep element is concealed until playout (the hunter's entry side, or one beam's axis). This trades a little P for D, and it gives the playout real suspense.
- **Designer decision:** define the front catching the Cell (forced contact now, or a raid at full strength). Make laying low push the front back, or slow it, rather than only Heat -8.
- **Designer decision:** losses touch the key (downed assets at the core contact cost key fragments), or the key scales to the haul, so raids can threaten the win.
- **Designer decision:** DOWN persists (no income until repaired, and repair costs one netrun's action).
- **Designer decision:** lever costs in different currencies (ghost: Heat; decoy: Schematics; dark: income).
- **Designer decision:** network positions come from the route (the column and row each asset was run in), so frame 2 and frame 3 are one decision.

## What the scrambled frames failed to communicate

- That the yellow fused disc is the Cell (it reads as a bomb or objective).
- That the chevrons under the Heat bar are front speed. They read as playback speed buttons.
- What happens when the hatched front reaches the Cell's column (frame 1 places it exactly there).
- What a ghost, a decoy and go-dark each do. The legend shows shapes and a cost of 3, not effects. "x1" next to the black disc means nothing.
- That beam 3 is a hunter that turns. It looks like a short third beam pointing at the decoy.
- That the bottom-right panel in frame 3 is an alternative plan rather than a second outcome or a warning. There is no grid for it.
- Why "+1" is a win (it is a net figure; the +6 evade reward is invisible).
- The rings in frame 4 as "near misses". Without words they read as selection or "scanned".
- What "+51" in frame 6 measures, and whether 43 is good (the 25 key is never shown on screen).
- The two Heat numbers on the frame 2 cards: change or end value?
- What the shield-numbered pins in frame 6 are: contacts and their outcomes. They show where contacts happened but not what each cost.
