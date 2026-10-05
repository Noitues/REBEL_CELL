# M14 rolling audit: Group 1 (ART-1 Foundations), NAIVE (beginner + non-English reader)

Main sha 12c6ad3 (worktree at the same sha; import clean on the second pass, 0 ERROR).
One capture session, one window at a time, every Godot run through `tools/run_windowed.py`:
- `tools/visual_qa/capture_pack.py --screens title,new_campaign,hq,hq_heat_band,grid,grid_site_selected,grid_raid_pending,raid_setup,route,combat_start,combat_hover,combat_resolving,combat_after,loot,mainframe,event,event_dispatch,options,tutorial --filters none,grey`:
  one launch, 19 of 19 screens ok, 38 pictures (colour + Pillow greyscale), 0 Godot ERROR lines.
- `tools/design_lab/kit_sheet.tscn` pages kit / lifecycle / materials (75 frames each), then
  `tools/design_lab/glyph_sheet.tscn` (30 frames, pages 1-3 at text scale 1.0, 64/32/16 px). 0 ERROR lines.
- Note: the lab runs were asked for at 1600x900 but the frames came out 1280x720 (the sheet scales to fit);
  the materials page cuts off the bottom of the CEL / TOON strip at that size.

Frames were judged only as captured (800x450 pack, plus crops upscaled for reading). The frames were
deleted after reading. The reviewers did not read the design docs.

Many screens are not restyled yet (Groups 2-4). Mixed old/new looks are noted, not counted as P1.

## Understanding table

B = the beginner (reads English, knows nothing about the game). NE = the non-English reader (relies on
icons, colours and shapes). % = how much of the screen's purpose and its actions they could explain.

| Screen (frame) | What they think it is | B % | NE % |
|---|---|---|---|
| title | Main menu: continue, campaigns, tutorial, codex, stats, options, quit; record stickers on the right | 85 | 70 |
| new_campaign | Set up a new game (seed, target, ICE, home server, crew) and start | 50 | 30 |
| hq | Home base: menu left, map preview, crew cards, WANTED poster with Heat, big JACK IN button | 60 | 40 |
| hq_heat_band | Same, Heat has gone up, a stamp says "noticed", a raid warning note | 65 | 40 |
| grid | A city map with sites to attack, a legend and a list of runs on the right | 55 | 40 |
| grid_site_selected | One site picked (T2, "Intel"), but no way to start it shown | 50 | 35 |
| grid_raid_pending | Map with an arrow attack coming in, a RAID SETUP button | 55 | 40 |
| raid_setup | Place defences (turret, ice lock, decoy) to protect home, then START DEFENSE | 55 | 40 |
| route | Pick the next stop on a route (fight / event / shop / rack); key at bottom right | 70 | 55 |
| combat_start | Two spinning wheels (me vs enemy), cards at the bottom, press SEND IT | 35 | 20 |
| combat_hover | Same, pointing at a card changes the preview tags (old one crossed out) | 35 | 20 |
| combat_resolving | The wheels play out; numbers fly | 30 | 20 |
| combat_after | Next turn; a "last turn" line, HP forecast "NEXT 49 (-11)" | 40 | 25 |
| loot | Pick one of three cards or skip | 80 | 60 |
| mainframe | A shop: chips, cards, slices, daemons, remove a card, leave | 55 | 40 |
| event | A story with two choices and their costs | 75 | 55 |
| event_dispatch | A message from your handler with two choices | 65 | 45 |
| options | Settings tabs and switches | 80 | 40 |
| tutorial | First lesson over a fight: explains the wheel | 55 | 25 |
| kit_sheet (kit / lifecycle / materials) | The look kit: stickers, pencil, paper, CRT screens, data bits | 80 | 70 |
| glyph_sheet at 16 px | 114 icons: tell apart | 85 | 85 |
| glyph_sheet at 16 px | 114 icons: guess the meaning without the label | 45 | 40 |

Average over the 19 game screens: B 58 %, NE 39 %. The fight (the core of the game) is the lowest for both.

## Findings by owning area

### 1A palette / faces / theme

- **P2 — danger and gain are told apart by hue only; greyscale loses it.** Evidence: `event` vs grey `event`:
  "+25" (Cycles, green) and "+2" (Heat, red) are the same grey and both carry a "+". The only difference left
  is the small icon. Same in the Mainframe: affordable price tags (yellow "BUY 100") and unaffordable ones
  (pink "BUY 141 / 129 / 218", 120 Cycles held) are the same light grey in grey `mainframe`, and in colour
  nothing but the hue says "you can't afford this" (no lock, no strike, no dimming).
  Expected: danger/gain and can/can't carry a second cue (sign glyph, arrow up/down, dim or strike for
  unaffordable) as the STYLE_GUIDE colour-is-never-alone rule implies. Fix: a cost/loss token (e.g. a
  down-tick or "−" style) for Heat gains, and a disabled style (dim + lock) for unaffordable prices.
- **P2 — pink means too many things.** Pink is the main action (JACK IN, SEND IT, START DEFENSE, New
  campaign, RAID SETUP), damage against you ("HITS YOU 8" chip in `combat_after`), attack slices and their
  values on the wheel, the Heat number, the "1 LEFT" counts in `raid_setup`, and plain top-bar stickers
  (SCHEMATICS, RANK, ICE, CREW). The NE reader could not tell "press this" from "this hurts you". "YOU GET
  CORRUPTED" (`combat_start`) is coral-red while "HITS YOU 8" is pink: two reds for one meaning.
  Fix: keep pink for actions/verbs only, one danger red for harm, and neutral paper for plain counters.
- **P2 — top-bar sticky notes are coloured without meaning.** `hq`, `combat_start`, `grid`: HEAT beige,
  SCHEMATICS pink, HP / HOME yellow, CYCLES white, RANK / ICE pink, CREW yellow. The NE reader assumed the
  colours meant good/bad and guessed wrong (HP yellow = warning?). Their 6-7 px caps labels ("SCHEMATICS",
  "BANKED", "EXPLOITS") are the smallest text on screen and barely readable at 800x450.
  Fix: one neutral paper colour, or colour by kind (resource / threat / count) with a legend.
- **P2 — Heat bands are not visible without reading the word.** Only two bands were captured (0 "cool" in
  `combat_start` / `hq`, 27-30 "noticed" in `hq_heat_band`). In both the Heat number is the same hot pink and
  the bar is the same pink fill; the band is only the word ("cool" lime in combat, grey in HQ; "noticed" black
  brush on the poster). In grey there is nothing else. The kit's "HEAT 62 FLAGGED" poster shows a red band
  colour, so a ramp exists in the kit but not on these screens. Fix: band colour on the number/bar and a
  band glyph or pip count, so a band reads at a glance and in grey. (Five-band colouring on combat came with
  2C; the HQ poster is on the 1A theme.)
- **P2 — switches in Options: the "off" state has no visible track.** `options` crop: off toggles are a lone
  grey dot on the dark panel; on toggles are a white pill. The NE reader thought the dots were bullets, not
  switches. Fix: theme the CheckButton off track with a visible outline/fill token.
- **P3 — the Heat number counts while the band stamp is already held.** `hq_heat_band`: stamp "HEAT 30 ·
  NOTICED (25+)" and top bar 30, but the big number reads 27. Wrong number in a still; expected the held
  state to show the end value. Fix: capture the held state after the count-up, or start the stamp at the end
  of the count.
- **P3 — distressed faces at small size.** ".PIRATE.RADIO" label (`hq`) reads as noise; "noticed" brush
  italic is small; the "SAVED" note at bottom right of `raid_setup` is nearly invisible grey. Body mono face
  and the condensed bold headings read well at 800x450.
- **P3 — faces/portraits.** The crew Polaroids (`hq`) and the tiny grid crew chips (`grid`, about 25 px) read
  as a hooded figure with a pink visor; fine as a silhouette. Two operatives of one class are identical, so
  at small size the only difference is the "Breaker 1 / 2" caption.

### 1B materials

- **P2 — the binary bits read as numbers.** `combat_resolving` crop: "0 1 0 1 0" digits fly through the
  wheel next to the slice values ("5", "6") and the block value, in a similar cyan. Both reviewers read them
  as values ("did I get 10?"). On the kit sheet (`kit_materials` frames 20-65) the bits clump inside the
  left of the circle and then vanish instead of reading as a stream "round the rim into HP".
  Fix: make bits smaller/fainter than any value digit, a distinct colour from the block cyan, and keep them
  moving along the rim.
- **P3 — materials read as different kinds on the kit sheet, not yet in game.** On `kit_sheet` the four
  read clearly apart (stickers = verbs/things, yellow/red pencil = plan/threat, CRT = the Cell's systems,
  paper/holo = stolen intel); both reviewers could sort them. In the game frames paper carries everything
  (top-bar stats, story text, choices, tutorial, crew cards, WANTED); CRT is the menus and the DISPATCH bar;
  no grease pencil appears in any captured screen; the sticker words in game (SEND IT, NEVER SLEEP, LOOT:
  pick a card, LEAVE MAINFRAME, PLAY IT SAFE??) are pink drip graffiti, not the kit's white die-cut / holo
  SEND IT (`kit_lifecycle`). Mixed old/new, for the screen owners (Groups 2-4) as they restyle.
- **P3 — the kit sheet itself.** Materials page cuts off the bottom of the CEL / TOON strip at 1280x720;
  the binary-bits box shows an unexplained green rectangle (the HP target?) with no label.

### 1C glyphs

- **P2 — three icon sets for one slice.** `combat_start`: the intent tag lists "✦ OVERFLOW · ▲ SHIM ·
  ■ DEFRAG" (text symbols), the wheel draws a starburst / white spike / shield, and the glyph atlas has a
  starburst / sword / burning brick wall for the same three. The NE reader, who learns by icon, cannot link
  them. Fix: one glyph per slice from the atlas everywhere (owner of the wheel/tags: Group 2, once it wires
  the atlas).
- **P2 — confusable at 16 px** (`glyph_sheet` 16 px column, upscaled):
  - 24 picto_spin and 26 picto_momentum: the same clockwise arrow.
  - 9 special_priority and 58 hub_emergency_powers: the same siren.
  - 0 slice_shim, 47 hub_breaker_core, 59 hub_station_keeping, 12 special_dose: all a diagonal stick.
  - 40 picto_block and 2 slice_defrag: both brick walls; at 16 px block becomes a grey mush square. BLOCK is
    a core word on every fight tag.
  Fix: give each pair a different silhouette (momentum with motion lines, emergency vs priority with a
  shield/badge, block as a solid shield).
- **P3 — confusable or unclear at 16 px:** 50/51 phantom core vs echo; 45 no_damage vs 68 seg_blank (both a
  minus); 55 hive_core vs 70 fw_hardened (both hexagons); 18 status_encrypted vs 79 barbed_wire (both a
  dotted bar); 34 picto_ring_lock (mush). Meaning guessed wrong without the label: 57 customs_seal
  (read "fast forward"), 61 root_access (read "terminal / console", fine), 89 zero_day "Ø" (read "nothing"),
  98 shield_cache (read "jar"), 102 tuning_fork (read "Y"), 104 salvager "J" (read the letter J).
- **P3 — the Heat icon is a droplet.** Top bar, legend "heat reduction", event "+2": the NE reader read it as
  water or blood. A flame would read as heat.

### Later screen owners (not Group 1; recorded for the fix batches)

- **P2 (tutorial, Group 4)** `tutorial`: the lesson text stops mid-sentence ("Hover or right-click anything to
  read") with no scroll cue; "Next" is greyed with no reason given; the top resource bar is missing on this
  frame. It is a wall of English: NE 25 %.
- **P2 (City Grid, Group 3)** `grid_site_selected`: the selected T2 "Pricing Memo Archive" shows no crew,
  no JACK IN and no reason (locked? needs a cleared neighbour?). The beginner did not know what to do.
- **P2 (route, Group 3)** `route` key: five states are colour-only rings (you are here pink, next yellow,
  further cyan, visited dark teal, elite/Rack lime); in grey, next / further / elite are the same white ring,
  and yellow vs lime are close even in colour. On the map the [1]/[2] numbers and "YOU ARE HERE" save it.
- **P2 (City Grid legend, Group 3)** `grid` legend: "corporate" (lime square) and "cleared" (cyan square) are
  the same square, identical in grey.
- **P2 (combat, Group 2)** card text is about 6 px and cut ("Flip a wheel. Blocked whil..."); the enemy HP
  ring has unexplained yellow ticks; the fight overall: B 35 %, NE 20 %.
- **P3 (events, Group 4)** `event_dispatch`: "DISPATCH - DISPATCH: Early Reply" then "DISPATCH:" again.
  "PLAY IT SAFE??" floats mid-map on both events with no link to a choice.
- **P3 (Mainframe, Group 4)** the vertical neon "MAINFRAME" is hard to read for the NE reader; "SPINNER"
  wheel under REMOVE A CARD is unexplained.
- **P3 (new campaign, Group 4)** "Campaign seed", "ICE (0-13)", "+1" next to the seed spinner: jargon with
  no icon; NE 30 %.

## Verdict

NOT CLEAN — 0 P1, 8 P2 in Group 1 areas (1A: 5, 1B: 1, 1C: 2), plus 5 P2 for later screen owners.
