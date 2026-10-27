# Art direction review: everything explored so far (2026-10-01)

Status key: **LOCKED** = the designer has decided. **LEANING** = a front-runner exists but it hasn't been confirmed. **OPEN** = no decision yet. **UNEXPLORED** = no concept work done yet.

## 1. Base world style: LOCKED
- **Choice:** Cv2, gritty triangulated low-poly, with E's cel shading (toon bands and ink lines).
  - Proof: `round2/assets_compare/s1_cv2_cel`, `round2/r2_blend_EC_on_Cv2_day`.
- **Rejected:**
  - round 1 Aâ€“E (neon ink, tilt-shift diorama, riso zine, rain noir, glitch vector);
  - round 2 A, B and D (low-poly 3D, painterly matte, neon painting);
  - Cv3 (regressed the variable polygon sizes);
  - the E-only city.
- **City:** a restyle of the game's own city layout and HQs, with glowing streets (`round6_city_restyle`). The designer said "City looks great!".
  - It now has day, night, day + suspicion and night + suspicion versions (`round6_city_restyle/views/*_full.png`).
  - The zoomed-out overview (`round5_city_overview`) and the helix-HQ wide cities (`round2/r2_city_wide_helix`, `r2e_city_wide_helix`, `r2_helix_blender`) are superseded.
- **OPEN:** sign off on the night and suspicion full shots (the helicopters, drones and red/blue light levels).
- **OPEN:** how the city recedes behind combat (feedback item 3). Round 10 tests this.

## 2. Overlay layer: LOCKED
- **Kept:**
  - vinyl stickers for all words and objects;
  - grease pencil for plans (yellow for routes, red for threats);
  - light spill from glowing base elements.
  - Proof: `round3_overlay/combined_v2`.
- **Rejected:**
  - spray and stencil ("doesn't look good");
  - ransom collage, ink brush, the light pen as an overlay, and the original dripping marker.
- **OPEN:** feedback items 6 and 9 assumed a marker writing **over** washed-out system words ("SEND IT" over EXECUTE, with drips). Now that the marker and spray are gone, what plays that role? Options:
  - (a) a vinyl sticker verb slapped over the washed-out system word;
  - (b) a grease-pencil scrawl over it;
  - (c) drop the idea.
  - My pick is (a): it keeps one material for words.

## 3. MODEM shop sign: LEANING
- `round4_modem_sign`: the original neon MODEM sign on a circuit-board backing, with light spill.
- **OPEN:** confirm it, and pick the shop view (inside or outside: the street view in `round2/r2c_v2_modem` or the current shop).

## 4. Wheel structure (frame, pointer, hub): LEANING
- **Explored:**
  - round 1 `spinner_3d` (depth studies);
  - round 4 W-A salvaged faceted, W-B instrument dial, W-C layered stack, W-D segmented ring with stickers;
  - round 7 V1â€“V3. **V2 "living programs" was picked**, and its telemetry readout border was "great".
- **OPEN, the pointer:** the round 4 notched blade with a value window, or the V2 pointer.
- **OPEN, the hub readout:** "ATK 6" (borrowed from W-B) for accessibility.
- **OPEN, the 3D/layered feel (item 4):** how much depth? The W-C layer parallax is the cheapest way to show it.
- **OPEN, boss "extra something":** V2 bosses got a heavier bezel, a banner and phase pips. Is that enough?

## 5. Slice art: LOCKED on the family, OPEN on the details
- **Locked:** family C, "Screens & Data". Each slice is a live CRT screen with a bold white glyph and number (`round5_slices/s_c_screen_data`, extended in `round6_roster`).
  - Backgrounds may borrow from A (circuit PCB, already used for SANDBOX) and D (corp materials).
- **Rejected:** round 8 identity art (big illustrated icons) and round 9 low-poly identity art. They pushed slices toward the city style, but they didn't land.
- **In progress (round 10):** reworked VIRUS (poison) and PROXY (evade), and how the slices sit on the new city combat screen.
- **OPEN, the glyph set:** do the icon ideas (skull, fire and poison for attacks; wall, steel door, safe, lock and shield for defence; mask, key, bug and so on) become the white **glyphs** inside the C screens? Or do glyphs stay as the simpler round 4/5 shapes?
- **OPEN, new slice types** (PHISHING hook, SHIELD, ENCRYPT `***`, RECON magnifier): these are **game design changes**, not art. They need a GDD/DECISIONS entry before any art.
- **OPEN, value and upgrade variation:** should a slice look different at higher value or upgrade level? For example, a busier screen, a gold bezel, or an extra glyph pip.

## 6. Enemy, corp and boss skins: LEANING
- **What exists:** round 6 corp screen skins:
  - Meridian: container and barcode;
  - Solace: cells and glass;
  - Halcyon: blueprint;
  - Orbital: star map;
  - REBEL_CELL: corrupted board.
- It also has special mechanics on the wheel (second pointer, docked drones), and 5 bosses with phase 2 (`round6_roster`).
- **OPEN:** approve the corp skins one by one, and say which boss phase 2 treatments you like.

## 7. Cards: OPEN
- `round4_wheel_card`, four versions:
  - C-A faceted print;
  - C-B data chip;
  - **C-C sticker card (the front-runner)**;
  - C-D terminal.
- C-C fits the sticker overlay and the "slap on" animation (item 8).
- **Risk:** a lot of white in an 8-card hand. The fallback is C-A.
- **OPEN:** pick one.

## 8. Effects: LEANING / OPEN
- **Binary damage shards** (item 5): a concept exists (`binary_damage`). LEANING; please confirm.
- **Heat glitch shader** (item 11): agreed in principle, switchable in Options. UNEXPLORED visually.
- **City life** (item 7): status of each part:
  - fog patches, tilt-shift, elevated highways, hologram billboards, helicopters and drones: partly shown in the city restyle;
  - the raid grid with nodes and paths on the same plane: UNEXPLORED in the new style.

## 9. Unexplored areas: these need a concept pass before the art bible rewrite
- Raid and grid view in the new style (nodes and paths on the same plane).
- Menus and UI chrome: title, map HUD, panels, buttons, tooltips, and typography.
- Operative portraits and characters, if the asset list wants them beyond wheel hubs.
- Reward, event and dialogue screens.

## Decisions from round 10 (2026-10-01)

**VIRUS slice**
- Screen effect: the round 10 option B ooze (it slides down from the rim and pools).
- Icon: the biohazard (option C).
- The option A effect (violet blotches eating a hex dump) is reserved for future BURN, TORCH or DISSOLVE programs.
- The poison-vial icon is reserved for later.

**EVADE slice**
- Icon: the double chevron.
- Screen: a street-sign hard turn, a detour arrow. The zigzag was dropped because it read as lightning.

**Guy Fawkes-style mask**
- It's no longer an icon.
- It becomes a slice **background** (screen content) for a program to be decided. It isn't EVADE.

**Grease pencil**
- Near-opaque.
- Thicker.
- Saturated yellow and red.
- A dark under-shadow, so it reads on both day and night.

**Combat backdrop**
- Round 11 tests a close-up of the building being attacked, in day and night versions, instead of the whole city dimmed.

## Designer answers on the open items (2026-10-01)
1. **City night and suspicion shots:** approved. The helicopters and drones read, and they will read even better once they move, so they need animation.
2. **Combat fade:** the fade amount is good, but the view is too zoomed out. The next pass focuses on this (round 11 is a target-building close-up).
3. **Verb over a washed-out system word:** **sticker**.
4. **MODEM shop:** an exterior street view, with the circuit-board MODEM sign. It becomes a fixed shop building facade. Options are in progress in round 12:
   - 3 facades;
   - each in rain, day (with building shadow) and night.
5. **Wheel details:** to be handled over the next iterations.
6. **Glyphs:** they're starting to look good. A full glyph pass is needed.
7. **New slice types:** yes. Some art will be a placeholder for game content that doesn't exist yet. Add them to the game to-do list when the art is reintegrated.
8. **Value and upgrade variation:** spec 3 versions of every slice. Also spec temporary slice-state overlays (frozen, locked, burning, empowered, â€¦) that sit on top of a slice.
9. **Enemy and boss designs:** keep iterating.
10. **Cards:** sticker cards are **LOCKED**, with peel and stick animations. Explore an effect where the sticker dissolves into binary or code when it's played.
11. **Binary damage shards:** yes, but iterate on the visual.

## Decisions from round 11 (2026-10-01)

**Combat backdrop**
- **Locked:** a close-up of the building under attack.
- Night is approved.
- Day should be slightly cooler, so the orange target building separates from the orange corp wheels. This is being re-rendered.
- It's fine for the wheels to hide parts of the building.

**Approved**
- EVADE: the double chevron over a road-sign hard turn.
- VIRUS: the biohazard over ooze.
- The opaque grease pencil.

## Decisions from round 12 (2026-10-01)
- MODEM shop exterior: **F1 Tenement** is locked.
- Its sign spill becomes pinker, like F2.
- The dangling cables over the alley stairs are removed.
- The F1b revision is in progress.

## Decisions from round 13 (2026-10-01)

**Wheel frame**
- **D4 "Lens & rail"** is LOCKED for every wheel.
- The phase pips are loved.
- The NEXT arrows are removed as a standing element. They are reused as the card-play preview: where the pointer will land, shown when a card is aimed.
- The grease pencil will follow the cursor, so its clipping doesn't matter.

**Enemies and bosses**
- Slices get more identity through a **corp-level theme** that every enemy and boss of that corp inherits.
- Variations then sit on top: regular, elite, boss, plus boss upgrade and phase effects.
- Round 14 is in progress.

**Glyphs (round 14 in progress)**

| Glyph | Change |
|---|---|
| SANDBOX | A kid's sandbox with a shovel. |
| PATCH and HEAL | Two crossed band-aids of one width. DOSE is kept. |
| SHIELD | Keep trying. |
| RECON | Binoculars. |
| NULL | Try divide-by-zero options. |
| JUDGEMENT (the gavel) | Takes the Meridian RAM-drain effect. |
| CITATION | Takes the receipt. |
| SPOOF | A full fingerprint. |
| CLEANSE | Try CTRL-ALT-DEL. ALT-F4 is a placeholder "kill process". |
| EMPOWERED | New options. |
| SPIN N+ (the Momentum card) | Redraw it as a conditional or combo spin. |
| NUDGE INNER | Concentric rings with the inner ring highlighted. |
| NUDGE | A short Â±1 two-way arc. |
| UNDOCK | A drone with an arrow, or an open ball-and-socket. |
| BREACH | Lightning over a bullseye. |
| EXHAUST | A tearing card. |
| All fire | One shared two-peak flame. |

**Upgrade tiers**
- Tier II â†’ III needs a shape change, not only colour, so it works for colour-blind players. Round 14 is in progress.

**State overlays**

| State | Change |
|---|---|
| CORRUPTED | A pink and green full-slice glitch shader. |
| ENCRYPTED | Asterisks scrolling outward. |
| OVERCLOCKED | More translucent. |
| PARASITE | The symbol latched on, translucent. |
| FROZEN | Approved. |
| BURNING | Approved. |
| LOCKED | Lock symbols scrolling left to right. |
| EMPOWERED | Huge arrows moving outward. |

## Decisions from round 14 (2026-10-01)

**Glyphs approved**

| Glyph | Approved form |
|---|---|
| WEIGHT | The anvil. |
| SANDBOX | The plank box with a shovel. |
| PATCH | Crossed band-aids. |
| SHIELD | Option A, heraldic. |
| JUDGEMENT | The gavel. |
| CITATION | The receipt. |
| EMPOWERED | Option A, a chevron stack. |
| Also approved | UNDOCK, BREACH, EXHAUST, the two-peak burn, FIREWALL. |

**Glyphs being redone (round 15 in progress)**

| Glyph | Redo |
|---|---|
| RECON | Thin-circle binoculars. |
| NULL | 1/0. |
| SPOOF | White ridge lines. |
| CLEANSE | An ESC key. |
| KILL PROCESS | A power symbol. |
| MOMENTUM | A spin arrow with big/small numbers, where the big one is the one that executes. |
| NUDGE | An arc with a needle. |
| NUDGE INNER | Check it doesn't look like SPIN. |

**Tiers**
- All upgrade flair moves inside the slice border.
- Round 15 shows three options:
  - a: an inner line, then a filled gap;
  - b: an outer-arc pattern, plus stronger tick and PERFECT marks;
  - c: a pattern all the way round.

**States**
- PARASITE: only the animated bug.
- EMPOWERED: huge rising chevrons.

**Card-play preview**
- Option A, the ghost blade, with:
  - no aim pips;
  - a dashed outline on the landing slice;
  - an outside trace line with direction arrows.
- To be shown with multiple needles and a docked drone.

**Corporations**
- Corp motifs move into the full slice background; no small motif panel.
- Per-slice briefs for Solace, Meridian, Halcyon and Orbital are in round 15.
- Meridian's JUDGEMENT slice: a gavel striking down, replacing the receipt machine.
- REBEL_CELL = the player's own slices in red, with a rebel-fist crest.

## Decisions from round 15 (2026-10-01)

**State overlays: LOCKED ("ship it")**
CORRUPTED, ENCRYPTED, OVERCLOCKED, PARASITE (the bug only), FROZEN, LOCKED, BURNING and EMPOWERED (chevrons).

**Card-play preview**
- Every needle gets a full ghost blade.
- Ghost drones show where docked drones end up.
- The trace line has no arrowheads.
- Gates are deferred to the to-do list.

**Corporations**
- Halcyon and Orbital palettes move further apart.
- Corp tiers:
  - tier 1: corp primary border;
  - tier 2: corp secondary border;
  - tier 3: the player tier-III style in the corp palette.
- Corp animations stay upright.
- Halcyon MISS: the CLOSED sign.
- Defend walls everywhere: attacks come from the outer arc, and the wall sits on the inner arc.
- Per-slice fixes are in round 16.

**Glyphs**
- RECON: cone eyepieces.
- SPOOF: realistic ridges, thinner border.
- NUDGE: the needle points down through the arc.
- JUDGEMENT: a strike block offset from the gavel.
- SANDBOX: a sand pile with a pail and shovel.

**Tiers**
- Option a is agreed.
- It must be more obvious, while keeping the silhouette identical.

## Decisions from round 16 (2026-10-01)

**Locked**
- Slice tiers: **V2 "strong"**.
  - Tier II: a steel bezel plus a bright inset line with a gap.
  - Tier III: a gold strip, heavy cross-hatch and a brighter screen.
- Player FIREWALL: shots fall from the outer arc onto a wall at the hub.
- Glyphs: NUDGE (the needle down through the arc), JUDGEMENT (the raised gavel), SANDBOX option C.
- Corp slices: Orbital and REBEL_CELL are fully approved.
  - Halcyon attack: option B, the drone lock-on.
  - Solace: everything except GROWTH.

**Round 17 in progress**

*Card-play preview*
- It gets an animated version.
- One set of large ghosted chevrons, chasing from the top needle to its landing; no white trace lines.
- The example must be clearer: start, direction, where each needle lands, where each drone ends.

*Corp fixes*
- Solace and Orbital palettes move further apart.
- Solace: GROWTH as true mitosis.
- Meridian:
  - CRIT: a stamped box.
  - DEFEND: running-bond containers.
  - JUDGEMENT: a real gavel striking its block.
  - MISS: the box shreds away.
- Halcyon: SHIELD reverts to the round-15 riot shield.

*Glyph tweaks*
- Binoculars: short, filled cones.
- Fingerprint: the bottom horizontal lines removed.
- Solar flare: the horizon line only.
- The final glyph package is exported.

## Decisions from rounds 17â€“18 (2026-10-02)

**Locked**
- The animated card-play preview.
- The sticker card play: peel, slap, dissolve.
- The hit and crit damage shards.
- The corp slices, except the Solace and Meridian fixes below.
- Raid nodes and links on the street use **C, the circuit inlay**. B (holo tiles) is kept for some other feature.

**Corp fixes (round 18 in progress)**
- Solace GROWTH: no pink arrows.
- Meridian:
  - DEFEND: running-bond containers.
  - CRIT becomes AIRMAIL, a plane flying across.
  - The RAM-drain slice becomes PRIORITY: the stamped box, with a new alarm-light glyph. JUDGEMENT is retired.

**Combat effects (round 19 in progress)**
- The card play gets the hover preview.
- Each dissolve gets its own GIF.
- A full effects list, plus a first batch of animations.
- The heat glitch is kept but the designer isn't sold on it: explore non-intrusive Heat alternatives.

**Raid (round 19 in progress)**
- Stickers only for things that don't change: cards, node types, buttons, titles. A subtler sheen.
- Grease pencil on tactical elements must be true to the game rules:
  - no "THEY WANT THE VAULT", "FLAK HERE?" or "HOLD IT!";
  - drag hover shows the arrow, the circle and the route shift.
- Other mediums for the info panels.
- No node tags; node status shown on the node itself.
- Live info (feed, speed, HP, damage) in a live medium, not stickers.
- More polygons on buildings.
- Major nodes inside buildings.
- No fog by day.
- Helicopter spotlights only with a gameplay effect:
  - they circle and jiggle;
  - drones carry mini spotlights;
  - helicopters come in and out at the edges.
- A threat vehicle matrix: corp Ã— unit type Ã— upgrade.

## Decisions from round 19 (2026-10-02)

**Locked**
- Corporations: all five kits.
- Card play: hover preview, then slap, then **dissolve A** (bit stream).
- Effects:
  - block/shield walls;
  - heal;
  - drone deploy and attack;
  - enemy defeated.
- Heat: **H1, the city reacts**. Police lights, searchlights and helicopters on the backdrop. The screen glitch is an Options extra only.

**Round 20 in progress**
- Corrupt tick: the bars dissolve left to right.
- Evade: the token flies to the top left with the attack chasing it, and both fade at the edge. No wheel shift.
- H1 at NOTICED needs to be more noticeable.
- Batch 2 of the effects.

## Decisions from rounds 19â€“20 (2026-10-02)

### Combat effects

**Locked**
- Corrupt tick.
- Nudge and resistance.
- Respin.
- Drone destroyed, without its labels.

**Rule**
- Every card-caused effect stems from the card's slap and dissolve on the target wheel, not from the hand.

**Round 21 in progress**
- Evade veers off earlier.
- Phase-change bits come from the HP phase pip.
- RAM-gain origin options.
- Heat dialled down:
  - the old FLAGGED becomes HUNTED;
  - the old NOTICED becomes FLAGGED;
  - the new NOTICED is a couple of alarms on non-target buildings.

### Raid

**Locked**
- Lime links.
- The node status key.
- City detail.
- The EXPOSED spotlight.
- The CELL HOLDS stamp.
- The threat vehicle models.

**Round 20 in progress**
- Routes back to red grease pencil.
- "DOWN" marks wipe away.
- The decoy frame redone.
- Node health: lit portion drains north to south, plus floats on hover or an Options toggle.
- GIFs for every changing state.
- No Heat escalation during a raid; Heat changes after it.
- More panel-medium options.
- Speed/Skip matches the chosen panel medium.
- Building nodes get a rooftop outline and an operator drop target.
- Stationed operators.
- Vehicle corp colours plus icon versions.
- A campaign-lost ransomware screen and the campaign summary.

## Decisions from rounds 20â€“21 (2026-10-02)

### Combat

**Locked**
- Evade v3.
- Phase change v2.
- RAM gain comes from the **TURN banner**.

**Round 22 in progress**
- Drone destroyed: its own HP counter goes to 0, with no tag.
- FLAGGED Heat: city searchlights plus one or two alarms on the target.
- SEND IT restyled as a raid-format sticker.
- Word stickers from effects (CORRUPTED, EVADED, CHECKPOINT, PHASE 2, DELETED) are temporary and dissolve into binary.

### Raid

**Locked**
- Red grease-pencil routes.
- The DOWN wipe.
- The CELL HOLDS sticker.
- Panels: option **E, by fiction**.
- Building nodes: **B, uplink pad**.
- Vehicle models and colours.
- Campaign lost: **A, ransomware lock**.
- EXPOSED is kept.

**Path rules**
- Solid line = the active route; dashed = what-if.
- Decoy preview: scribble through the old path, and show the new route dashed.
- On placement: erase the old path and draw a new solid one.
- No re-route during execution, unless the decoy is destroyed, in which case the route reverts.

**Card drag model**
- The peeled sticker parks.
- A grease-pencil arrow follows the cursor.
- Near a node, a yellow circle means valid and a red X means invalid.

**Round 21 in progress: raid screen**
- Panels: a less transparent holo with a decrypted corp seal (and a non-decrypted variant), the work order kept, and Speed/Skip moved.
- Node health: the outline and icon stay lit; only the fill drains.
- Interaction GIF fixes.
- The raid report as a classified corp document.

**Round 21 in progress: raid world**
- R3 class beacons with cone beams, one per class.
- Station-bonus effects.
- Heading circle shown only on hover.
- Vehicle icon shapes by type.
- The campaign summary as a corporate dossier with polaroids and auditor post-its.

## Decisions from round 22 (2026-10-02)

**Locked**
- SEND IT vinyl sticker.
- Drone destroyed v3.
- Heat on the combat screen, all three bands.

**Round 23 in progress**
- Apply CORRUPTED is overlay only: no corner diamond badge and no rule chip.
- The CORRUPTED overlay is the full-slice pink and green glitch.
- The other word stickers are re-rendered with the temporary-label rule.

## Decisions from round 23 (2026-10-02)

**Locked**
- Corrupt apply v4: overlay only, the glitch.
- Corrupt tick v3.
- Evade v4.
- Phase change v3.
- Enemy defeated v2.
- Temporary word stickers dissolve into bits.

**Respin**
- Its label reads **RESPIN**, not CHECKPOINT.
- A checkpoint is the GDD's rewind point, which every random outcome sets. The undo block is shown on the UNDO button instead.

## Decisions from raid round 21 (2026-10-02)

**Locked**
- Raid setup, path rules, node health and the interaction GIFs.
- The raid report.
- YOUR NETWORK keeps its detail chips.
- R3 station beacons.
- The campaign dossier and audit report.

**Round 22 in progress: raid screen**
- The parked sticker sits above its hand slot, with no dashed outline in the game.
- Node "LOST" is renamed **TAKEN**.
- BREACHED: no double stroke, keep the underline.
- Swap = return to hand (park at the bottom), plus the pencil arrow drawing to the cursor.
- Ice: crystals along the inside border with a light-blue fill, for links and for units.

**Round 22 in progress: raid world**
- Rigger: blinking glasses and an occasional angry face.
- Phantom and Botnet violets separated.
- Station bonuses:
  - the slow ring moves inward;
  - freeze grows crystals on the ring;
  - repair rises upward.
- Vehicle icons:
  - a health disc that drains downward;
  - a corp-coloured dashed status ring, bigger than the icon, carrying the heading;
  - the fast chevron nudged up;
  - Lander becomes Orbital's special;
  - flying is a drone diamond with a 2Ã—2 circle glyph;
  - the red ring paled.

## Decisions from raid round 22 (2026-10-02)

**Locked**
- Remove-to-hand.
- Frozen ice on links and units.
- Vehicle icons v4, with the close and far health views and the status pips.
- The Rigger beacon.
- The slow-field proposal.

**Round 23 in progress**
- Drag snap: the arrow parks just outside a node's circle and the circle draws (yellow = valid; red circle + X = invalid). Leaving the node erases the circle and the arrow snaps back to the cursor.
- Swap with a truthful cursor path.
- A brief grease-pencil TAKEN mark.
- A slower BREACHED sequence.
- The slow field drawn under the units: **LOCKED** (round 23).
- Repair raises the node diamond's middle health fill, plus a diegetic count-up on hover: **LOCKED** (round 23).

**Round 24 in progress**
- Target buildings for Solace, Halcyon, Orbital and REBEL_CELL.
- HQ updates: Meridian cranes, an Orbital launch pad, the Halcyon eye.
- City motion.

## Art backlog (to address in coming rounds)
- [x] Combat backdrop: a zoomed-in target building, in day and night versions (round 11; the cooler day is in round 11b).
- [x] MODEM shop facade: F1 picked (round 12; the F1b polish is in progress).
- [ ] Target buildings for the other corps and fights, since every fight needs its own target.
- [ ] HQ updates:
  - Meridian HQ gets cranes, to match its crest.
  - Orbital HQ might become a launch pad.
  - Halcyon's crest is now an eye; check the HQ matches.
- [ ] Wheel details: pointer, hub readout, 3D/layered depth, boss "extra something".
- [ ] Full glyph pass, covering every slice type, status and pictogram in one consistent set.
- [ ] 3 value or upgrade tiers for every slice.
- [ ] Temporary slice-state overlays: frozen, locked, burning, empowered, plus CORRUPTED, OVERCLOCKED, ENCRYPTED and PARASITE.
- [ ] Enemy and boss wheel iterations (corp skins, phase 2).
- [ ] Sticker card animation: peel, stick, and a dissolve into binary or code on play.
- [ ] Binary damage shards, visual iteration.
- [ ] Heat glitch shader, visual exploration (switchable in Options).
- [ ] City motion: helicopters, drones, searchlights, traffic and hologram billboards.
- [ ] Raid/grid view in the new style, with nodes and paths on the same plane.
- [ ] Menus and UI chrome: title, map HUD, panels, buttons, tooltips, and typography.
- [ ] Operative portraits and characters.
- [ ] Reward, event and dialogue screens.
- [ ] Rewrite the art bible, then write the Godot implementation plan.

## Game to-do list for reintegration (art placeholders for content that doesn't exist yet)
- New slice types and programs: PHISHING (hook), SHIELD, ENCRYPT (`***`), RECON (magnifier). These need a GDD/DECISIONS entry before they become content.
- Reserved effects: BURN, TORCH and DISSOLVE programs (the round 10 VIRUS-A blotch effect).
- A program for the Guy Fawkes-style mask slice background.
- Renames:
  - INERTIA becomes WEIGHT.
  - TARIFF becomes JUDGEMENT (the Meridian RAM drain).
- SANDBOX's purpose: the GDD defines it as SHIELD, a shield that persists across turns (cap 15). The designer is considering "block one whole attack regardless of size" or "block the next status". This is a design decision.
- Slice upgrade tiers Iâ€“III. SliceData has no tier yet.
- Placeholder states FROZEN, LOCKED, BURNING and EMPOWERED. These are not in the game yet.
- A CLEANSE ability, now with an ESC-key glyph, and a "kill process" ability with a power-symbol glyph.
- Solace's HEAL slice reads as growth: a possible rename to GROWTH.
- A future mechanic, **gates**: rim gates that trigger when the pointer rotates through them. The card-play preview trace shows the direction and the gates passed. The art is deferred until the mechanic is designed. Round 15's `preview_A.png` has a first sketch: crossed gates light gold, uncrossed gates stay grey.
- Meridian content: CRIT becomes AIRMAIL, and the RAM-drain slice becomes PRIORITY (TARIFF, then JUDGEMENT, then PRIORITY).
- The heat glitch needs an Options setting (`heat_glitch`) and an exemption from the VfxTier rules.
- Raid Heat proposals that need a GDD decision:
  - a node in a helicopter spotlight is "exposed" (takes extra damage);
  - higher Heat brings more and stronger waves and more routes.
- **EXPOSED** (raid): a node in a helicopter or drone spotlight takes extra damage. The designer wants it; it needs a GDD rule.
- Station bonuses for the alternate classes (Wrecker, Phantom, Overclocker, Hivemind). The designer's proposals, each with a levelled-up version:
  - damage boost (levelled: adjacent nodes too);
  - slow radius (levelled: freeze);
  - sniper (levelled: player-aimed);
  - drone operator (levelled: counters enemy drones, helicopters and EXPOSED).
- Station levelling: levelled-up stationed operatives. The GDD has no operative station levels yet.
- Raid intel: the corp intel shows "decrypted" normally; at high Heat it may not decrypt.
- Decoy destroyed: a planned future enemy ability for harder AI and difficulty scaling. The route reverts when the decoy is destroyed. The raid code has no defence damage yet.
- MOMENTUM's pictogram is dynamic: the big number switches once a spin has happened. It needs runtime support.

## What happens after the decisions
1. Rewrite `docs/ART_BIBLE.md` around the locked direction.
2. Write a Godot implementation plan: shaders, atlases, and the order of screens.
3. Implement on `art-pass`, screen by screen, with before/after captures.

## Decisions from raid round 23 (2026-10-02)
- **Locked**
  - The drag dock preview.
  - BREACHED speed.
- **Accepted for now:** the swap motion. It's a bit janky; revisit it when the art goes back into the game.
- **In progress:** the TAKEN mark becomes normal weight, placed above the node.

## Decisions from round 24 (2026-10-02)

**Locked**
- The TAKEN mark v2.

**Rule**
- The boss target **is** the corp HQ.
- The close-up combat view must match the city map exactly: the same HQ model and the same roads.
- Regular fights happen at smaller Sites, which also sit on the real road layout.

**Meridian**
- Pivot to a **container castle**: a medieval castle built from shipping containers.
- Follow-up: check which other Meridian assets need to follow.

**Solace**
- A DNA helix only, with no centre tower.
- Thicker strands and thin walkway rungs.
- The green toned down.

**Halcyon**
- Loved. Add more levels.

**Orbital**
- Pivot: the dishes and antenna tower in a crescent around missile silo doors.
- Two states: doors closed, and doors open with a missile nose showing.

**REBEL_CELL**
- The player's home for most of the game, until the betrayal reveal.
- Iterate the design.
- The fist road network must show in the close-up too, consistent with the map.
- Two versions: home and post-betrayal DISPATCH.

**Round 25 in progress.**

## Decisions from round 25 (2026-10-02)

**Locked**
- City motion layers ("amazing").
- The map = close-up rule.
- Solace helix form.
- Halcyon's extra layers and stair ramps.
- The Orbital rocket.
- The Meridian regular site.

**Combat framing**
- Zoom in further. The HQ is the focus of the backdrop, and the wheels may overlap it.

**Round 26 in progress**

*City*
- More highways and complex interchanges.

*Meridian*
- Historical castle silhouettes that read from afar.
- Combat view face-on to the drawbridge.

*Solace*
- Lighting: underside down-lights, a centre up-spot, and LED chasers spiralling up.
- The regular site becomes a hospital.

*Halcyon*
- No radar dish.
- The eye scans like the Eye of Sauron.
- Regular site: a sphinx or a police station.

*Orbital*
- No tower in front.
- The silo is a round in-ground hole with a caution rim and sideways-sliding doors.
- The regular site becomes a TV station with dishes.

*REBEL_CELL*
- Explore several ideas: a Tokyo street, painted roofs that form a fist, hijacked holograms and billboards.
- The regular site becomes the MODEM shop with a red sign.

## Decisions from round 26 (2026-10-02)

**Locked**
- City motion v4: the flying-car sky lanes, the speed, and random lane colours by day and night.
- Solace HQ: the lit helix, plus the hospital site.
- Halcyon HQ, with the scanning eye.
- Orbital HQ: the in-ground silo, plus the TV station site.
- Combat zoom framing.

**Round 27 in progress**
- Meridian: an angular container fortress, with no rounded shapes. For example, a big container wall around a regular building.
- Halcyon regular site: a sphinx that isn't janky, or an alternative landmark.
- The MARKET NEON takeover sign: a flash sequence NO / MRE / MAN.

## Decisions from round 27 (2026-10-02)

**Locked**
- Meridian HQ shape: **A, the container wall** fortress. Its textures are still being iterated in round 28.
- Halcyon regular site: **Halcyon Court + Justice statue**. The new sphinx is liked and kept in the library.

**REBEL_CELL**
- No fist streets: a normal street grid.
- The HQ is a subtle city look, not a standout building.
- City map: painted rooftops forming a subtle fist, in home and DISPATCH versions.
- Combat backdrop: the **Tokyo street canyon**.
- Round 27 is in progress.

## Decisions from rounds 27–28 (2026-10-02)

**Locked**
- The shop sign is **MARKET NEON**.
- On a REBEL_CELL takeover it flashes **NO → MoRE → MAN**. The "o" comes from lighting the top half of the A.
- Source: ound27_modem_sign_flicker/market_neon_more_sequence.gif.

**Meridian castle**
- Not yet.
- Keep texture A (raw corrugated steel, Meridian orange).
- Lower walls, add a moat, and a beefy gantry crane as the central keep.
- Round 29 is in progress.

## Decisions from round 29 and REBEL_CELL round 27 (2026-10-02)

### Meridian

**Locked**
- Texture A.
- Lower walls.
- A moat.
- The gantry crane as the keep, with the boom lowered.

**Round 30 in progress**
- Train tracks along the boom side, with the crane loading a freight train.
- More polygon detail on the castle and on the moat water.
- Combat motion: the crane raises and lowers, and trains pass.

### REBEL_CELL

**Locked**
- The Tokyo canyon direction.

**Round 28 in progress**
- The map fist: bigger paint strokes, or a low hologram fist just above the roofs.
- Darker canyon lighting so the alley detail reads.
- Animated signs and holograms in the combat backdrop.
- A street-level combat test.

## Decisions from Meridian round 30 and REBEL_CELL round 28 (2026-10-02)

### Meridian
- **LOCKED** for now: "good enough to move on".
- Final tweak: shift the HQ and the train left in combat, so more detail shows between the wheels.

### REBEL_CELL

**Dropped**
- Holograms.
- Giant floating fists.
- Painted roofs.
- Street-level combat.

**Map**
- Normal buildings, with the window lights in the fist area coloured red so the fist reads city-wide.

**Canyon (combat)**
- Keep the darker canyon and the flicker.
- Home lays low: no rebel signs.
- DISPATCH: every sign and billboard shows the fist, REBEL_CELL or Cell slogans.

**Round 29 is in progress.**

## Decisions from round 31 (2026-10-03)

### Locked
- Rewards: option **A**, peel from the loot sheet.
- Dialogue: option **A**, a cel bust on a CRT feed.
- Events: as drawn. A full design pass comes once enough events exist.

### Meridian
- Combat camera faces the boom, with the crane centred between the wheels.
- The train runs left to right in front, takes a container, and speeds off.

### REBEL_CELL
**Map**
- The fist must be smaller and subtler. Options include a red-tinted district.

**Canyon**
- Detailed surrounding buildings.
- Fewer business signs.
- Food and chip holograms.
- Multilingual signs.
- DISPATCH shows anti-human slogans.

### UI
- Abandon dialog: both buttons are stickers.
- Title menu: replace EXFIL. The designer suggests BREACH / DISABLE / OVERTHROW.
- Corp paper font: **Courier Prime** (OFL).
- Backdrops: no fist roads, and the new Meridian.

### Shop
- Renamed **MAINFRAME**: a blue neon sign, with no extra words.
- Takeover sequence:
  - NO = N + the top of the R;
  - MoRE = M + the top of the A + R + E;
  - MAN = M + A + N.
- The clerk screen moves down.
- A grease-pencil note replaces the MODEM sticker.
- Slices are sold from a spun wheel showing the top 3, not as stickers.
- SHRED is replaced: removal-concept options.
- A more colourful LEAVE sticker.

### Fight won
- The building lights turn to the Cell's colours.

### Netrun route
- The blueprint is rejected.
- Explore combined designs (on the city map) versus separate ones (a building climb, a transit path), plus a hybrid.

### Missed systems
- **Microchips** and **Daemons** were never designed.
- A GDD art-coverage audit is in progress (GDD_ART_COVERAGE.md) before designing them.

## Decisions from rounds 32–33 (2026-10-03)

### Locked

**Netrun**
- Option **D, the hybrid**: a transit path for site runs, a building climb for the HQ boss, and raids on the city map.
- Runs start from a Cell-owned node and expand toward the target HQ.
- A finite set of options at each step.
- Greyed-out, plannable unreachable nodes.

**Firmware and Daemons**
- Firmware: the **socketed die**. It now plugs in from the slice's hub side.
- Daemons: the icons and the combat rack and animations.

**Shop**
- The offscreen slice wheel (option B).
- The recycle bin for removal.
- The new layout.

**Slice names**
- SHIM (attack), OVERFLOW (crit), DEFRAG (defend), DETOUR (evade), HOTFIX (heal), INFECT (afflict).
- SANDBOX, TROJAN and NULL are unchanged.

**UI**
- Courier Prime for corp paper.
- A yellow CANCEL sticker.
- Main menu option A, with **SIMULATE** as the tutorial verb.

**MAINFRAME sign**
- Filled neon.
- Sequences: NO → MoRE → MAN, I AM → AI, and I AM → NO → MAN.
- The white core is being toned down.

### In progress

- Daemon action and miss colours are being separated.
- The shop label is being corrected from MICROCHIPS to FIRMWARE.
- REBEL_CELL:
  - blacked-out buildings draw the fist's details;
  - a brighter canyon;
  - fuller signs.

### Game to-do (integration)

- Rename the boss breach "Mainframe Gate" to **"Central Server"** (GDD §11.7), because the shop is now MAINFRAME.
- Rename the slice programs as above.
- The player-facing name is **Firmware**, not Microchip.
- A campaign upgrade that adds nudges to the shop wheel.
- Replacing a socketed firmware destroys the old chip, with a confirm (proposal).

## Decisions from round 34 (2026-10-04)

### Locked
- Firmware and Daemons.
- The multiplier tags move under the status badge.
- MAINFRAME letter legibility.
- The normal canyon.

### Shop
- Slice price tags sit closer to their slices.

### MAINFRAME sign
- The circuit board interacts with the letters: traces into the tubes, pads, components, and traces that pulse with the flicker.
- One consistent trace style.

### Netrun rules

**Player choices**
- No planning feature: the route lives in the player's head.
- Runs go from any owned node to any unowned node across a border link. There's no cap on choices.

**Node and link states**
- Unavailable nodes and links are **white**. Past nodes are greyed.

**Info panels**
- Node panel: only tier, rewards and type, and only when decrypted.
- Operative: a corp-paper dossier with stats and the raid placement effect.

**Map display**
- The target circle is labelled TARGET.
- Heat is shown.
- Each node shows its tier; tier 3 nodes, which carry the Central Server keys, are special.
- Parts of the city irrelevant to the run are greyed out.
- A denser network, a higher zoom level, and map panning.
- Three transition ideas for zooming into a link.

**Consistency**
- Buildings are individual, not blocks, so the raid, city grid and netrun views look consistent.

**HQ run**
- Branches merge.
- The top node is the Central Server.
- Each room is detailed.
- Try a raid-style overhead view of the compound. Meridian's crane and train make the map dynamic.

### REBEL_CELL

**Fist shape**
- A tucked thumb: a half-length bottom line on the right, plus a vertical line up to the fingers.
- Toned down.

**Reveal**
- The whole sector starts lit, then the ring and the hand lines black out.

**Label**
- Moved off the fist.

**DISPATCH canyon**
- The closest right-hand hologram becomes the fist.

### Shop wheel (2026-10-04)
- The shop spinner has no needle. The top slice's price tag hangs in its place.
- **Game to-do:** the top slice is cheaper than the sides (80 vs 100 in the concept). The GDD price is a flat 100, so this needs a DECISIONS entry.

### MAINFRAME sign: LOCKED (2026-10-04)
- Version v4: `round33_mainframe_sign/*_v4`.
- Filled neon with varied circuitry wired to the letters.
- Sequences: NO → MoRE → MAN, I AM → AI, and I AM → NO → MAN. An A's legs go dark when only its top is lit.

### REBEL_CELL: LOCKED (2026-10-04)
- Version: `round34_rebel_cell`.

**Map**
- Option A: red windows forming a tucked-thumb fist.
- The washed-out lit state, then a blackout reveal of the ring and the hand's lines.

**Combat backdrop**
- The Tokyo canyon.
- Home lays low.
- DISPATCH shows anti-human signage and the fist hologram.
- Animation is slow and gentle.

## Decisions from netrun round 35 (2026-10-04)

### Locked
- HQ run: the **overhead compound**.
- Heat: option **B**, darker orange. The city reacts with circling lights, and Heat lights centre on the nodes it has made harder.

### Round 36 in progress
- The AT LARGE stamp moves next to the operative's name.
- Node states, two options:
  - outline circles: white = unavailable, orange = selectable, lime = visited;
  - or a softer white wash.
- A per-node Heat marker.
- A patrol affordance on grey city sites.
- A dressed-room close-up per node.
- Four more zoom transitions in the mixed-media style.

### New: unified city, raid and run pass (in progress)
- One shared, detailed real-city model for the City Grid, raid management and run transit, shown side by side.

### Rules: game to-do
- The tier-3 "keys" are the **Exploits**: the Central Server needs 3.
- On the run map, nodes are never revisited.
- On the city map, cleared sites can be patrolled (existing rules).
- HQ moving nodes: links de-power and are then remade. Needs a dedicated pass on unique HQ mechanics: Meridian crane and train, Solace rotating walkways, Halcyon eye blocking, Orbital silo doors.
- Central Server names per corp (to iterate): The Master Manifest, The Genome Core, The Panopticon, Launch Control.

## Decisions from round 36 (2026-10-04)

### Locked

**Unified city concept**
- One real-city model shared by the City Grid, raid and netrun views: "the concept I am looking for".
- The City Grid view must include all city details (highways and sky lanes, holo billboards, etc.).

**Netrun node states**
- Option **A**: normal icons with outline rings (white unavailable, orange selectable, lime visited).

**Node backdrops**
- The detailed room backdrops for HQ nodes.

**Exploits**
- Exploits stay on **tier-2 sites**, per the GDD. The tier-3 wording was a slip.

### Round 37 in progress
- Netrun:
  - nodes that aren't next are hidden by default;
  - an always-show option;
  - legend hover shows all nodes, and node hover shows that one node;
  - calmer, slower Heat lights;
  - the combo transition: terminal connect, then the window despawns, the operative's wheel spins up, and the wheel lens zooms in.
- Unified city:
  - city details on the grid;
  - translucent, darkened buildings in the raid and netrun views, so nodes and links dominate.

### Game to-do
- Raid view zoom fits the player's network size. Needs a dedicated pass.

### HQ backdrops: LOCKED (2026-10-04)
- Regular HQ-run nodes (combat, event, shop) use their **detailed room backdrop**.
- The boss fight at the Central Server uses the locked **HQ close-up**, for example Meridian facing the boom.

### Netrun round 37: LOCKED (2026-10-04)

**Node visibility**
- Hidden-node visibility rules.
- An "Always show all nodes" option.
- Legend hover and node hover reveal hidden nodes.

**Heat**
- Calm Heat lights: two slow searchlights, plus gentle circling on hardened nodes.

**Transition**
- Terminal connect, then the window despawns, the wheel spins up, and the wheel lens zooms in (about 4.4 s, skippable).

**Game to-do**
- Add the "Always show all nodes" setting.

## Decisions from unified city round 37 (2026-10-04)

### Unified city (round 38 in progress)
- Buildings: slightly lighter.
- A real-scope test before locking: the real run-map node count, plus a real raid view fitted to a mid-campaign network.
- Flying cars as low-poly models, not dots.
- The zoom-through GIF is only a scale proof, not a gameplay transition.

### Backlog started (round 38)
- Hub cores, Mk2 versions, enemy hubs and the breached state.
- Inner-ring glyphs, including Anchor.
- Precision landings (Perfect / Good / Partial).
- Exploit items and the Central Server gate.
- Satellites as mini-wheels.
- Operative portraits, their states and contexts, plus contacts (DISPATCH is voice-only).

## Decisions from round 38 (2026-10-04)

### Locked
- Portrait states and contexts.
- Portraits: Wrecker, Overclocker and Botnet.
- Hub cores: Ghost, Swarm and Hive, plus all enemy hubs.
- The Central Server breach look.
- Unified city: the opacity treatment at every zoom.

### Round 39 in progress

**Portraits**
- Breaker: no chin piece.
- Ghost: ninja style, with no eye slits.
- Phantom: a full mask with round robot eyes.
- Rigger: goggles attached to the strap.
- Hivemind: a square lens connected to the circlet.

**Hub cores**
- Breaker: a crowbar hitting a cracked glass square.
- Wrecker: the unexplained lines are removed.
- Phantom: an echo trail.
- Rigger: a socketing chip.
- Overclocker: an RPM gauge in the red.
- Breached stays as an enemy state (the Hub Breach card disables the Hub for one turn).
- New: a player defeat state where the core turns to bits and drains away.

**Inner ring**
- More defined: bezel, outline and polish.
- Full-slice textures that extend into the outer slices.
- Proposal mock-ups (see the game to-do).

**Satellites**
- Centred on their slice.
- A rounded clamp.
- A binary explosion when destroyed.
- Bigger slices spread at an angle.
- Fix the spin centre.
- New: a **parasite partial third ring** concept as a boss mechanic.

**Landings and Exploits**
- The OVERFLOW banner moves off the needle.
- PARTIAL becomes **WEAK**.
- An expanded Exploit set, one for each boss power-up.
- Map badges showing which Exploit each tier-2 site holds.

**Unified city**
- A closer default zoom with panning.
- Meandering links.
- The raid view carries all the locked raid UI.
- Netrun paths are thin double dashes that follow the street grid, with the locked netrun details.
- Car LOD: dot plus line far out, a grey box plus line at mid zoom, and a full model plus speed line up close.

### Game to-do (design proposals from the designer)

**Inner ring**
- ACCELERATOR becomes a mini second needle that triggers whichever outer slice it points at.
- New segments:
  - a drone-focused segment;
  - status-themed segments, or CORRUPT becomes "double status effect";
  - AOE segments, adjacent or global.
- Operatives start with 1–2 blank inner segments.
- Echo and ×2 overlap: consider making ×2 a firmware (Echo plus ×2 firmware gives big multipliers).

**Satellites**
- A new satellite overwrites an occupied slice.
- Satellites can't be nudged, except as a drone-class ability.
- A parasite third-ring boss mechanic.

**Exploits**
- One for each boss buff.
- Make each tier-2 site's Exploit visible on the map.
- Breach against a one-pointer boss: it stays at one pointer.
- Virus picks its slices at random.
- Nice-to-have: replace the reused placeholder icons.

**City**
- Map panning.
- Car LOD tiers.

## Decisions from round 39 (2026-10-04)

### Locked
- **Portraits:** all classes except Phantom (triangle eyes pointing down) and Rigger (goggles in line with the headband), both being fixed.
- **Precision landings:** Perfect / Good / WEAK.
- **Exploit options:** the expanded set, including the ROOTKIT, HIJACK and CIPHER proposals.
- **Satellites:**
  - icon and number size;
  - the destroyed effect;
  - the spin;
  - bodyguard.
- **Parasite ring colours.**
- **Hub cores:** Rigger and Overclocker.
- **Inner ring:**
  - textures that extend into the affected slices;
  - the sub-needle, hangar, double-status and other proposals as directions.

### Round 40 in progress
- **Exploit map:** a badge only, with the full tag on hover, and nothing covering grease pencil.
- **Satellites:**
  - the dock blends into the slice outline;
  - the replace effect: the old satellite returns to the core as green bits, and the new one hovers, then installs.
- **Parasite ring:**
  - thinner, with a bigger icon and number;
  - its icon coloured like its number;
  - shown on the player's wheel;
  - its slices can reuse effects, for example a heal that heals the boss;
  - three layouts for how it interacts with the needle.
- **Hub cores:**
  - Breaker: spiderweb cracks.
  - Phantom: no inner pulse.
- **Enemy lockdown:** an encrypted-bits waterline that drains with the timer.
- **Player defeat:** bits vanish at the bottom, with no pink line.
- **Inner ring:**
  - a sub-needle shaped like the real needle;
  - a hangar with two drones;
  - status stack indicators.
- **Unified city:**
  - medium car LOD matches its line colour and is translucent;
  - all the raid interaction GIFs re-run in the unified concept.
- **Netrun transit:**
  - single dashed lines meandering between the buildings of the adjacent blocks;
  - a closer zoom;
  - about 7 layers, around 15 to 20 nodes.

### Game to-do
- **One-pointer boss:** never offer the Breach Exploit, or change it to "boss starts stunned (misses its first turn)".
- **Parasite ring:** can latch onto either wheel. It's mainly a boss mechanic inflicted on the player.
- **Hangar:** decide how damage works with multiple drones.
- **Status stacking:** show the stack count.

## Decisions from round 40 (2026-10-04)

### Locked
- **Exploit map:** badges, with the tag shown on hover.
- **Operatives:** portraits v2.
- **Hub cores:**
  - Breaker (spiderweb cracks) and Phantom;
  - the hub-breach lockdown waterline;
  - the player defeat drain.
- **Inner ring:**
  - the sub-needle;
  - the two-drone hangar;
  - status stacks as a ×N tab.
- **Satellites:**
  - the blended dock (for now);
  - the replace animation (green bits).
- **Parasite ring:** option A, beyond the needle tip.
- **Raid interactions:** the re-run in the unified city.
- **Cars by zoom:** the three LOD tiers.

### Standing rule
- **No UI may ever cover grease pencil.**

### Round 41 in progress
- **Exploit map:** chip moved off the pencil.
- **Wheel stack:**
  - multiple drones on one slice;
  - the parasite pop-up behaviour: it stays attached while spinning or when not under the needle, and pops up when the needle settles on it;
  - parasite and drones together;
  - a combined layer stack covering every per-slice feature, plus priority rules.
- **Netrun transit v3:** network, cable and power-line runs (straight segments and turns, not a hiking path), with the walked path solid, and a lighter city.
- **Unified city:** lightened.

### Locked (2026-10-04)
- **Exploit map v3:** the chip sits clear of the pencil.
- **Netrun transit v3:** straight cable-run paths, a solid walked path, and the lighter city ("perfect").

### In progress
- **Worst-case combat clutter test:** double drones, a parasite and a status on every slice of both wheels, with the inner ring populated. Compared against a typical case, with mitigations.

## Decisions from the clutter test and city v2 (2026-10-04)

### Locked
- **Parasite slices.**

### Wheel stack (clutter v2 in progress)
- **Drones:**
  - smaller and shorter;
  - no stem when a parasite is present, a small stem otherwise.
- **Drone collapse:** drones collapse into a thin slice layer showing only their current effect; on hover they bloom to full size with their needle state.
- **Inner-ring textures:** must render, including the extension into the outer slices.
- **Re-runs:** the worst case and the typical case again, plus a spin GIF if the worst case fits.

### Unified city
- **City Grid brightness:** revert the global brightening; the grid returns to its earlier brightness.
- **Raid and netrun views:** keep their current state, but make the translucent buildings less see-through and less grey.

### New work started (round 42)
- Site markers: every kind, tier and state.
- The Cell's HQ room, plus its DISPATCH variant.
- Unique HQ mechanics for each corp, with de-power and re-form animations.

### Next, after these land
- Rewrite the ART_BIBLE from this review.
- Write the Godot implementation plan.

## Decisions from round 42 (2026-10-04)

### Locked
- **Unified city:** v3 ("ready to lock").
- **Wheel stack:** the collapsed drones.

### Dropped
- **The Cell HQ room.** The game to-do list must find other ways to represent the HQ actions: Heat, patching, repairs, recruiting, and the Black Market.

### Round 43 in progress

**Site markers**
- Customs: a tipping scale.
- Yours: a rebel fist.
- T2 keys: a keyring with three keys.
- Disabled: a circled lightning bolt, in the player colour.
- Seized: a caution triangle.

**Combat HUD**
- Nudge buttons sit above the wheels: CCW on the left, CW on the right.
- The CELL-9 sticker sits above the RAM readout.
- The forecast and NEXT readouts are removed. A this-turn result number sits next to each HP value, with a tooltip breakdown on hover.

**HQ mechanics**
- **Meridian:**
  - the next container is telegraphed;
  - the train stays one full turn;
  - the crane moves containers both ways;
  - links are recreated after each move;
  - paths run along the walls.
- **Solace:**
  - two helix strands, each with its own nodes;
  - crossovers between the strands;
  - the camera keeps the player centred;
  - the goal is to reach the top.
- **Halcyon:**
  - a switchback pyramid with rows of 6, 5, 4, 3, 2 and 1 nodes;
  - shortcuts 4→9, 9→13, 13→17 and 17→20, with at most 2 used;
  - integrated with the eye-sweep idea.
- **Orbital:**
  - a repeating loop where every node must be cleared each lap;
  - sabotage 3 missiles;
  - on the 4th lap the path bypasses the platform, and the 4th launch destroys the base.
- **DISPATCH:** 3–5 out-of-the-box ideas, such as several operatives running at once to hit 3 nodes simultaneously.

### Site markers and HUD (2026-10-05)

**Site markers**
- The previous icon changes are reverted.
- Disabled: a white lightning bolt over the whole site circle, with the full icon greyed out.
- The duplicate key icon becomes a new icon.
- Seized and disabled nodes de-power their links.
- A plain-language legend explains what each icon means.

**HUD**
- Nudge buttons are aligned across both wheels, and the boss has key labels.

**Forecast format**
- [final damage] (shield-absorbed) [+shield gained] [−other] [status].
- Example: −6 (4 shield) +4 shield −1 RAM.

## Decisions from round 43 (2026-10-05)

### Locked
- **Combat HUD v4:**
  - aligned nudges;
  - boss keys A/D;
  - the forecast format.
- **HQ mechanics, good for now** (revisit in playtest):
  - **Meridian:** the crane/train cycle.
  - **Halcyon:** the switchback, shortcuts and eye.
  - **Orbital:** the missile loop, cutting encounters to keep within the time rule.
- **Solace:** the strands are semi-random node sets, not "all elites" or "all shops".
- **DISPATCH:**
  - the finale is **Sync Strike** (3 runners hit 3 locks together);
  - **mirror combats** (fighting your own slices and firmware) appear throughout that chapter.

### Site markers v4 (in progress)
- **Seized:** matches the raid map's memo-pad icon, replacing the node circle like disabled does.
- **Second key icon:** a bolder icon that reads from afar.
- **Yours:** a rebel fist with the thumb tucked.

## Decisions from the M14 integration review and round 44 (2026-10-06)

Review: `INTEGRATION_REVIEW/REVIEW.md`. Renders: `round44_undesigned/` (A_map, B_menus).

### Locked
- **DISPATCH:** voice only, before and after the betrayal, with captioned words; never paper.
- **Combat camera:** a perspective close-up for every fight (not the map iso).
- **Skins:** accent tokens only; never re-render city, paper or pencil.
- **HQ behind Sites:** wait for the unique per-fight backdrops.
- **Map links:** draw only the links the route uses; hover shows all. The main-line map must lose clutter.
- **RESET TO DEFAULTS:** every tab ("RESET ALL TABS", terminal button).
- **Pause:** all-sticker menu (kept from the M14 ruling).
- **Campaign slots:** LOAD and DELETE stickers on every folder, each with a pencil CAN'T UNDO.
- **Sticker focus:** focus and hover show only the peel-back corner curl; the rainbow gloss sweep runs on a scheduler, one sticker at a time.
- **Aiming result:** no hub plate; HP result chips underlined in yellow pencil, plus ghost landings.
- **Loot:** CONTINUE added.
- **HQ page:** round 44 `hq_idle.png` / `hq_node_selected.png` are the target (direction B, cleaned). The page frames the Cell's network; an off-screen corp HQ gets a red pencil edge arrow. About 16 pinned markers is acceptable.
- **Route page:** round 44 `route_page*.png` zoom and declutter are the target.
- **Heat number:** lives in the terminal top strip, not on the dossier stamp (bible 4.3 updated).
- **Per-fight backdrops (2026-10-06):** unique buildings for non-HQ Site fights stay deferred. Gameplay polish passes come first, then another content and visual pass. Site fight subjects (Solace, Orbital) are interim through M14.
- **Inner ring (round 45, 2026-10-13):** ghost wedge over the affected outer slice, the modifier's mark tiled inside it (stronger: 38 %, 1.3x), the active inner segment raised and lit with a tick on the needle line, the word plate and tooltip on hover or aim only. One modifier per slice. Supersedes the bible 3.10 standing ring plates.

## Decisions from the route map rounds (2026-10-14)
- **Route map direction:** the V3 side view (dollhouse) with the dynamic camera: parallax along the run, a DECISION zoom by default, OVERVIEW on Z. It is also the base for the HQ netruns.
- **Look:** AAA-2 "Realistic night" is the designer's favourite (revision r2 in progress). This deliberately extends the locked cel world for this view: a designer call.
- **Kept media:** grease pencil is the route connection medium; node icons are vinyl stickers; the hover power cut stays.
- **Traffic:** no car geometry; light streaks only (head and tail, long exposure).
- **Buildings:** add circular, fat, stepped and adjoining shapes.
- **Rejected:** X1/X2/X3 cyberspace (no wireframe city). X2's scrolling binary facades are parked for reuse.
- **Next:** after r2 is approved, a full netrun storyboard (HQ view, select the netrun, AAA-2 overview, zoom to start, first option) as video or GIF; then the Blender and Python pipeline tools for building every netrun; then a Halcyon HQ render in this style.
- **Standing rule (2026-10-14): the look must be procedural.** Every look element of the netrun views (fog, beams, plumes, sky and street streaks, flicker, billboards, silhouettes) is a seeded rule driven by the layout data and one shared look preset. It must rebuild on any city formation or location with no hand edits. Concepts must prove it with a second layout.
- **Netrun entry flow (2026-10-15):**
  - one press skips the whole entry;
  - no wheel lens: the jack-in terminal goes straight into the dive;
  - the plan pencil is orange;
  - route rooms are hidden until street level, then the walls dissolve to bits from left to right while the links write on, then the markers draw, then the zoom to the start room.
- **Standing rule: the city is always alive.** Traffic streaks, beams, flicker, holos, fog drift and rain run in every beat and screen. Only the level of detail changes with zoom.
- **Orbital HQ (2026-10-15):**
  - The route is several circuits round the launch complex, and the camera orbits to keep the active room front and centre.
  - The antenna tower is a real structure with elite rooms on every circuit.
  - Each circuit sabotages the rocket, which then strikes Orbital facilities in the city or in space. The last circuit is a shortcut that fires the rocket early into the closed bay doors and destroys the HQ.
  - Future cutscenes: (1) after each circuit, a city-wide zoom out to launch, strike and explode, then back in; (2) the HQ explosion. Both are planned as future tasks.
- **Boss wheels v3 (2026-10-15):** the identities are approved: Roman "The Pantheon" (fresco gods, Ascendant plus Omens) and Atlantis "The Tank" (migrating predators, 2 to 8 arm pointers, kraken reveal).
  - Approved rule exceptions:
    1. the Tank uses 8 slots and 40 ticks;
    2. RESIST is allowed as a boss slice effect;
    3. wrath can change a slice's type mid-fight (the preview recomputes, and rewind never crosses a crack);
    4. Pluto stays NULL for card effects until it turns wrathful.
  - Visual polish is still far from target. Each wheel gets a dedicated polish session; the prompt is in `boss_wheel_v2/POLISH_SESSION_PROMPT.md`.
- **One continuous city (2026-10-15):** the netrun street is derived from the real map lots along the selected Site's border link. One camera path, a look blend on shared geometry, and a section cut by zoom. The designer approved three map-side layout rules for mainline:
  - (a) buildings fronting border-link streets are at least 6 floors (about 11.5 BU);
  - (b) border-link street tiles are 8 BU wide instead of 6;
  - (c) hero signage on route columns, placed by rule.
- **Halcyon (2026-10-15):**
  - The concept is accepted as is, with no re-render.
  - Eye: white-teal with an amber rim; the overview camera stays fixed.
  - The status word is SPOTTED; its game effect is defined elsewhere.
  - THE PANOPTICON is suggested to the GDD as the Central Server name.
  - Shortcut strength is not decided here.
  - Perimeter belt: prefer flattening foreground buildings with zoom (the section approach). Use an empty belt only where it makes sense.
- **New corps (2026-10-15):** the identities, crests and icons are accepted.
  - The district "street" renders were unnecessary (no game view uses them).
  - The Aurelian Concord and Tethys Deep HQs each need a separate concept and design pass, then a visual pass. For Tethys, explore dams or water locks.
  - Side-street views rely on the global one-city approach plus each corp's building types.
  - Tethys underwater look: clearer water with a deeper distance fade.
  - New UI/HUD items are allowed. The colours are fine.
- **Process rule:** no game design in art-pass. Rules questions go to other sessions.
- **Next:** a full city render showing every corp district, including Tethys as a flooded district.
- **HQ review (2026-10-15):**
  - Fix the lighting misses on Solace, Rebel Cell and Meridian.
  - Bring dense city close to every HQ: no open perimeter. Use the section cut to keep rooms visible.
  - Rebel Cell: identity from the mainline Tokyo-alley HQ, with the red MAINFRAME sign.
  - Orbital: clean up the platform centre (the rocket and silo must read).
  - Meridian: the netrun runs 360° round the fortress, with containers moved wall-to-train every other turn enabling and disabling links.
  - Meridian (designer, 2026-10-15 evening): the train needs a track leading away, so the wall-to-train shuttles are physically possible. Direction: a freight line through a gate in the fort wall, across the yard, out as an elevated viaduct through the city to the coast. It is set dressing only, with the route unchanged, and the same line appears in the all-corps city render.
  - Occlusion (designer, 2026-10-15 evening): foreground buildings that block the camera's view of an HQ get flattened or made transparent. The rule: any building inside the camera-to-HQ (and route) sight cone is section-cut to a 1–2 floor lit stub. If it still blocks, it ghosts to about 15–20 % opacity with its edges kept. It eases in and out with the orbit camera and is never fully hidden. It is a camera-rig rule for every HQ, and goes into the pipeline spec and Godot mapping as a per-instance height clip plus a dithered alpha fade.

## Designer review of round 1 (2026-10-16 morning)
- **Canonical landmarks:** the full-city landmark designs are preferred. HQ netrun views must match the full-map landmark of the same corp, so the city version is the source of truth for silhouette and identity.
- **Rebel Cell HQ:**
  - It is still the weakest design.
  - Tone down the jarring red background.
  - Move MAINFRAME to the target location.
  - The underground gets character: sewers with a slight green light, running water, and pipe tunnels leading to and away from the route.
  - Buildings all touch with no gaps, so the top lane becomes a rooftop approach.
  - NYC-style rooftops: water towers, satellite dishes, roof access doors.
  - Rooftop paths run along the roofs and snake down a level or two.
  - Keep the Tokyo canyon signage but vary the sign styles. Add holograms and billboards at both rooftop and street level.
- **Meridian HQ:**
  - The layout still doesn't make sense, and the structure is hard to read.
  - A fresh architect/designer agent designs a shipping company: a giant crane that resembles a medieval castle, trucks picking up and dropping containers on three sides, and a high-speed train along the fourth side. The crane moves containers between train, wall and trucks.
- **Solace HQ:**
  - The double-helix silhouette is great.
  - Use 2 windows per floor: one facing inward to the walkway, one facing outward. Each is a sideways oval, larger, spanning about 140° of its half. The windows are the nodes, so the grease-pencil outline is oval too.
  - The bottom platform is too blurry and hazy.
  - Make it taller, so each helix makes a full 360° (like the full-city version).
- **Tethys / Atlantis:**
  - On a good track.
  - More city clutter under the water.
  - Clearer distinction between the waterline dams and the city.
  - The HQ becomes a floating pier city (Kamino-inspired), with piers and small copies of itself branching off and the main HQ obvious.
  - Clearer water, with the light rippling through it standing out.
- **Full city:**
  - Show a daytime version; the night version feels too dark.
  - Orbital: the rocket pad is too bright. Use direct spotlights from the platform edge onto the rocket.
  - Aurelian: columns as the external wall; stair-stepped internal tiers.
  - Add highways and train lines.
  - Building colours intermix, with each territory's colour denser closer to its HQ (colour by proximity to the nearest HQ).
  - Push the HQs further apart.
  - The city/sprawl edge must be organic, with traffic trails continuing and light fading slowly.
  - Rebel Cell is the city centre and mostly sprawl-coloured; red appears only later in the game.
- **Procedural street:** the concept is captured, but it's still far from the hand-built polish. Show stills of procedural street round 2; no new video.
- **Spec answers:**
  - Q1: an HQ fills its map lot.
  - Q2: the city and the route are procedurally generated per game seed and differ every game. Each corp territory has the HQ, non-HQ landmarks (the central-server access-key locations), unique building types, then the generated route map, then the flavour details. The landmark and route mechanics are game design for the build and design sessions; art provides the landmark building types.
  - Q3: detail appears with camera distance. Details always exist, are hidden when zoomed out and revealed when zooming in (neon shape first, then the full sign at street view).
  - Q4: render tolerance options to choose from.
  - Q5: keep the 2× landmark rule; HQs are bright and distinct.
  - Q6: render one alternative power-cut level.
  - Q7: the entry sequence timing is approved as in the video.
  - Q8: an edge arrow when the target is off screen. When the target is more than 50 % visible, drop the arrow and show only a partial grease circle.
  - Q9: show examples of the art-randomness settings.
  - Q10: same as the video's zoom timing (1.0 s).
- **Designer, 2026-10-16 (second round of notes):**
  - **Q4:** median 0.14 ±0.03 passes, the warn band is out to ±0.05, and R-VAL-2/3 stay separate.
  - **Q6:** the blackout alternative (outside ×0.20, 70 % desaturation, branch ×1.35, glow 1.0) is one value for street and HQ, as tunable presets.
  - **Q9:** all three variance levels have uses. The variance level varies with proximity to each HQ, and each corp has its own preferred level.
  - **Meridian:**
    - The Gatehouse Gantry is approved.
    - The target is the small tower building (the keep) at the top of the gantry.
    - The train must read more clearly.
    - Wider truck roads ring the building and lead to the highways.
  - **Solace:**
    - Much better.
    - The window outline must be truly horizontal and vertical, not warped along the helix.
    - Non-node windows get translucency, so interior character shows even at full zoom-out.
  - **Rebel Cell:** tone down the MAINFRAME brightness; it is hard to read.
  - **City:**
    - Highways and railways curve smoothly, with no 90° turns.
    - The railway ends at a large port at the water, outside Tethys territory.
    - The highways hub near Meridian.
    - Day is far too bright; match the old art-pass and mainline references.
    - Night is a little too dark.
    - Sprawl suburbs favour a lower profile at the same density.
    - The rocket and the Solace landmark are a little brighter.
  - **Street round 2 (designer, 2026-10-16):** the r2 height passes are approved (frontage silhouette and horizon break change about 465 frontage heights across the one city, never below 6 floors). Unique building ids are required (the layout key has 3,175 duplicates; use (ci, key) until mainline emits unique ids). Both are recorded in PIPELINE_SPEC §3.2.
  - **Tethys (designer, 2026-10-16):** add schools of fish and a migrating pod of whales to the Tethys water. Fish shoals swirl around the drowned streets and pier stilts. A whale pod (3–5, a calf among them) passes through the open water beyond the breakwater, visible through the clear water and lit by the caustics. It also goes in tethys_landmark.py / tethys_quarter.py so the full city gets it.
  - **City r3b (designer, 2026-10-16):** daylight and the new port are approved. Make the circle highway a perimeter ring around the city core, separating it from the sprawl. Add on/off ramps and interchanges. Roads and rail run alongside the Meridian HQ, never ending at it. The city-wide render reads as AI-generated and cartoony: a realism diagnostic (full-res, higher spp, guided denoise, lighter post, longer lens) is running.
  - **Solace v4 (designer, 2026-10-16):** build the windows as real cutaways in the tube with interior dioramas behind them, not surface textures (the textures show roughness). Interiors are full office floors at real scale (elevator core, conference rooms, cubicles, tiny people), seen through the windows. Walkways meld flush into the floors they connect to. At close zoom, add railings and tiny people walking.
  - **City realism A/B (designer, 2026-10-16):** version (b) is approved for the finals: 80+ spp, albedo+normal OIDN, bloom x0.5, no vignette, district fog tint -40 %. The cloverleaf interchange must move off the Meridian HQ. A side exercise has started: a city-planner agent designs a fresh, logically evolved city layout (3-5 options, docs/concepts/city_planner/) without seeing the current layout.
  - **Solace interiors (designer, 2026-10-16):** ship the hybrid: built office floors on route-node and decision-framed floors, interior mapping (a parallax fake-room shader) on every other window. No people anywhere (the block figures look bad); don't iterate on figures.
  - **City plan (designer, 2026-10-16):** Horseshoe Bay (planner design A) is chosen as the city layout direction. The planner iterates A2 with the game constraints and exports a machine-readable layout (city_A2.json) for the Blender city build.
  - **City A2 approved (designer, 2026-10-16):** rebuild the 3D city from city_planner/city_A2.json, with the new Meridian (Gatehouse Gantry) and Tethys (pier city) landmark modules and the (b) render settings. 1080 night and day tests come first.
  - **City A2 pass 2 (designer, 2026-10-16):** add a terrain heightfield, with foothills and mountains around the inland edges so the city doesn't end on a slab, and natural coastlines. Give the bay more character (marinas, ships, lighthouse, waterfront, barrier lights, islands). Add more city density and suburbs on the flat land. Highways read as decks with lane lights. Day gets brighter with a blue sea. Keep the night beam size.
  - **Build replan rulings (designer via the build orchestrator, 2026-10-16):**
    - D1: Aurelian Concord and Tethys Deep become fully playable. Art-pass owes the Tethys decision/hover finals and the Aurelian HQ design pass.
    - D3: the procedural planner city (city_A2-style) replaces the fixed layout.
    - D9: the Heat chip and the RAID AT n tick go on the map.
    - D10: HQ runs may exceed 7 layers, each unique.
    - D8, ownership (agreed): art-pass owns Blender (reference build, golden plates, look-dev, landmark .glb exports). The build session owns tools/netrun_art, the checks, the GDScript twins and Godot, and runs the §12 checks on Godot captures against the golden plates.
    - No building until the weekly token reset.
  - **Art question defaults (designer, 2026-10-18):** all recommended defaults of the plan-2 decision sheet's art and naming block (A1-A7) are accepted. A2: LAUNCH CONTROL (Orbital). A3: THE CONCORDAT VAULT (Aurelian). A4: THE MASTER MANIFEST (Meridian). A5: the Halcyon pyramid is cyan-white. A6: Tethys uses the frames' teal, not the spec 3.4 blue. A7: the TARGET edge arrow is a Godot overlay. The open questions in handoff §6 (Tethys peak 3.7×, the metro loop, the Q9 presets, the provisional spec numbers) keep their defaults: the Tethys peak is accepted, the metro loop stays dropped, Q9 is as provisional, and the spec numbers stand.
  - **NA-02 data contract (AD, 2026-10-18):** the art-pass position is in `HANDOFF_PACKAGE/NA02_CONTRACT_PROPOSAL.md`, sent to the build session for agreement before NA-02. It covers one exported `city.json`, `bid = "i:j"`, art seeds rooted in `layout_seed` with u64 values as strings, and the §12 split between Godot and Blender with an ID capture.
  - **Aurelian HQ (designer, 2026-10-18):** concept B, LOGGIA AND CAVEA (`route_map_graph/hq_aurelian/`), is approved. The route goes up the outer colonnade, round the rim walk, then down the four seating rings to THE CONCORDAT VAULT (the Rostrum's ring temple). Defaults: the gilt neon stays, gilt is dimmed next to the orange option links, colonnade room bays may drop 1–2 columns (HQ only), and runs over 16 layers spill onto the near half.
  - **Tethys mechanic (designer, 2026-10-18):** "Adopt THE WATER LEVEL (Head) as the Tethys mechanic and carry it into Tethys street netruns and raids. Route it to the design session." The base is `MAIN/docs/handoff/plan2/drafts/hq/tethys.md` §1–3. The rules go to the build/design session; art-pass draws the Head states (water plane, drowned LOWER rooms, the tide gauge) in the HQ, a flooded Tethys street netrun and a Tethys raid view.
  - **Designer feedback (2026-10-18), Aurelian:** flatten the tall buildings in front of the netrun views; the route goes outer ring → gates → inward → centre boss; a true arcade of arches on the outer wall; unique non-HQ netruns (e.g. scaling a leaning campanile). **General:** every corp's exploit buildings get a unique netrun view that ends at the exploit target inside the building, with several node layers inside.
  - **Corporation-wide themes (designer, via the build session, 2026-10-18; main DECISIONS "corporation-wide themes"):** every corp gets one campaign-wide theme: a light form in street netruns, the full form at the HQ, and one raid hook.
    - **Solace:** a virus spreads behind the operative and kills them if it catches up. In raids, a rising population-infection % (Solace wins if it fills).
    - **Halcyon:** the Eye scans the city. Spotted territory gets harder. After an Exploit, the Eye fixes on that area for 2 netruns.
    - **Aurelian:** the raid view is a colosseum of rings, with keys and gates leading inward to the HQ.
    - **REBEL_CELL:** a simultaneous rooftop, street and sewer infiltration that converges on the mainframe.
    - **Tethys:** WATER LEVEL.
    - **Meridian, Orbital:** still open. Orbital leans toward comms blackouts.
    - Art starts only the settled ones: Solace, Halcyon, Aurelian, REBEL_CELL DISPATCH, Tethys. Occlusion on every netrun is confirmed as the designer's own ruling.
  - **Exploit-building netruns (designer, 2026-10-18):** "These all work as directions. Rule exploit-building netruns in, and develop each with the corp's other two buildings later." Every corp's three exploit buildings (Intel, Breach, Virus) get a unique netrun that ends at the exploit target inside the building, with several node layers inside it. The 7 picks in `exploit_buildings/stills/sheet.jpg` are approved as directions. The other two buildings per corp come later, from the drafts in `exploit_buildings/<corp>.md`.
  - **Nudge lock (designer, 2026-10-19):** "The nudge lock should be just a grease pen circle slash (🚫) over the nudge buttons." That means a red (`#FF1C2C`) solid grease-pencil circle with a slash over each locked nudge button. It writes on and wipes off. There are no NUDGE LOCKED words and no refusal toast; a refused click re-scribbles the slash. Art-pass extends the same mark to a locked RESPIN (the designer can veto that). UNDO keeps its grey lock tick (ART_BIBLE 3.1).
  - **Review standard (designer, 2026-10-19):** every art-pass review of a build sheet checks the agreed visual standard and the ART_BIBLE 1.2 media rules: which medium carries which kind of information, and its look and its "never" list. A sheet can pass its numbers and still fail on medium.

## Designer ruling: art-pass owns the Godot look (2026-10-19)

The designer said the Blender-to-Godot transition "has been very rough going. We are not seeing results that are coming close to your
vision." Art-pass named the causes:
- The plates are path-traced (Cycles), but Godot rasterizes, and a spec of Cycles numbers does not port.
- The city geometry lives twice (Python rules and a GDScript twin), so it drifts.
- The look was ported in slices against fix lists, not against the whole frame.
- The look is ported by the build side, across a slow mailbox.

The designer's ruling: "yes take over. Do whatever you think makes sense process wise to ensure godot results match our renders."

### Locked
- **Lanes.** Art-pass owns the 3D look inside Godot: materials and shaders, the light rigs, fog and environment, post, and the view
  cameras' look settings for the netrun street, route, HQ netrun and city views. Build owns systems, data, loaders and game code, and keeps
  game UI. Art-pass writes no game rules.
- **Workspace.** Art-pass works in its own clone of the build repo, `D:/rc_art/godot_look`, branch `art/look`, cut from `w1-close`. Build
  merges `art/look` by fetching from that clone. Art-pass never writes in `D:/Godot/rebel_cell`.
- **One geometry source.** Godot generates the city and street. Blender plates are rendered from Godot's scene export (`plate_inputs`), so
  any Godot vs plate difference is look only. The art layout rules get one home (the build port), checked against `r2_rules`.
- **Reachable target.** Each golden plate gets a Godot-reachable twin: a Blender render limited to features Godot has. The designer
  rules on the gap between the Cycles plate and the twin, and the twin becomes the parity target.
- **Parity harness first.** One command renders the same camera in Godot and in Blender and writes the side-by-side sheet plus the value
  numbers. No look change is approved without it.
- **Whole frame first.** One owner per view brings in every element at rough quality, then refines it against the plate.
- **Pilot.** The street overview on seed 1, on the A2 city, once build's CITY-A2 step 1 lands. HQ and city follow the same recipe.

## Solace district and landmark (designer, 2026-10-20)
Concept rounds 1-5 in `solace_vertical/district/` (sheets `sheet.jpg`, `sheet_r2..r5.jpg`).
- **Kit:** direction D "mixed bundles": A capsule towers, B cell clusters (lime, pink nuclei) and C clinic towers in neighbourhood
  bundles of about 3-8 lots, one kit per bundle, neighbours differ (seeded). The hospital Site is C's porcelain cross-plan building.
- **Helix:** no beam or column under it (ART_BIBLE 2.4 "no centre tower"). It stands on a raised three-tier circular plinth with stairs
  at the four cardinal directions, landing on park paths.
- **Ground:** the district is one continuous park with no street grid inside: lawn, ponds, tree clumps, winding lit paths and a few
  curved service lanes, organic clearings, and a soft tree-line edge where it meets the gridded city. The layout change goes to build
  (A-069); street netruns in Solace are build's call.
- **Looks:** the city map keeps cel + ink at the raid zoom (ART_BIBLE 1.2). The AAA-2 night was re-lit so forms read (emission about
  1/3, moon key; median 0.14-0.16, under 1 % clipped). The AAA-2 day uses the approved city-day level (median about 0.46).
- **Solace HQ scene (designer, 2026-10-21):** "The HQ scene follows the new lime district helix (canonical landmark rule). Re-render
  the HQ plates with it, park and plinth setting, then port." The v4 HQ plates (white tubes, lime edges) are superseded once v5 is
  approved. v5 keeps the v4 structure and rulings (two sideways-oval windows per floor, cutaway windows with the hybrid interiors,
  flush walkways, full 360° per strand, no people), re-skinned to the district helix and set in the Solace park on the three-tier
  plinth with cardinal stairs.
- **Combat backdrop camera (designer, 2026-10-21):** the combat close-up rises to a backdrop-only pitch of about 30–40°, looking
  down into the lit street canyon as in r11 `combat_regular_night` / r26 `combat_solace`. This supersedes the D1 street-level pitch
  (6–10°, 2026-10-06) for the combat backdrop only; the city map camera is unchanged. ART_BIBLE 3.14 framing stands. The look-toolbox
  session picks the value from a 30 / 35 / 40° sheet against r11.
- **Combat backdrop r3 and the Solace-only focus (designer, 2026-10-21):** the look-toolbox combat backdrop round 3 (art/look-toolbox
  9674262b) is approved for now, including the REBEL_CELL canyon at 32°. The other corps' HQs will be reworked later. Until then, the
  art work is Solace only: no further tuning on the non-Solace HQ backdrops or landmarks.
- **Light reach and neon cores (designer, 2026-10-21, look-toolbox module 6 questions):** 2D UI spill and 3D city spill keep separate
  reach values; UI spill reaches shorter (about half the city reach), so panels stay crisp. Neon tubes get a white-hot core (signage,
  module 11), "but not so intense we are blinded by it": a thin core under the soft ceiling, with the hue carrying the edges and the
  bloom. Check the core on the squint test against the hue, not just the numbers.
- **Night sky and air (designer, 2026-10-22, look-toolbox module 7 question):** every view shares one night sky and one night air
  (haze) colour. District colour comes in as a separate tint layer on top. A view that differs is a named exception, logged here first.
- **Grease pencil module (designer, 2026-10-22, relayed by the look-toolbox session):** "Grease pen looks good. Approved". The sheet is
  `D:/rc_scratch/look_parity/pencil_8d1cf095/pencil_sheet_all.jpg`, branch claude/gifted-yonath-0c2f42 @ 8d1cf095. The merge follows
  the pencil session's hand-off.
- **Decrypted holo, module 15 (designer, 2026-10-22):** approved; the designer signed it off in the holo session. It covers
  THREAT INTEL: translucent glass, scan bands, edge-only RGB split and a cracked seal (art/look-holo @ 585be87f). Fold it into
  art/look-toolbox for build.
- **Solace fix pass 3 (designer, 2026-10-22):** approved for build now (art/look 36abb390, sheet
  `D:/rc_scratch/solace_v1/hq_port/p4/sheet.jpg`), with the remaining gaps to fix next. The gaps are:
  - the decision view's kit towers are pale striped boxes, where the plate has dark capsule bodies;
  - the decision view is brighter than the plate;
  - the highways still read as white bands;
  - a little sea shows top-right.
- **Neon core, look-toolbox module 11 (designer, 2026-10-22):** the "hot" version. The tube runs 0.9 toward NEON_CORE on a core 35% of
  the tube's width, with the hue on the edges and in the glow (`D:/rc_scratch/rc_look/sign/sign_night_t2.png`). This settles the
  "not blinding" white-hot core ruling.
- **Wet F0, look-toolbox module 8 (designer, 2026-10-22):** street and plinth keep separate wet F0 values: street 0.112, plinth 0.056.
  The water stays on IOR 1.33 (`D:/rc_scratch/rc_look/wet/wet_night_t2.png`).
- **Solace HQ pass 4 (designer, 2026-10-22):** "Good enough. Post pass 4 and move on to the TIDE / Bloom / infection looks." art/look
  2f505f6d. Accepted as is: the decision view's nearest towers are clinic kits (the plate shows capsules), and the highways read faintly.
- **Neon core tint (designer, 2026-10-22, look-toolbox module 11):** each tube's white-hot core is near-white tinted with about 15% of
  its own hue (mix(white, tube, ~0.15)), not the single pink NEON_CORE for every tube. The neon palettes stay as they are for now
  (`D:/rc_scratch/rc_look/sign/neon_palettes.png`). Any unifying of palettes needs its own sheet.
- **Solace THE BLOOM v2 (designer, 2026-10-22):** direction **A "Necrosis"** (`solace_vertical/bloom/sheet.jpg`): plum-black skin, pink
  veins, a hairline hot pink front edge, windows dying behind the front. Media: the Bloom is World; the TIDE gauge is CRT (bands also by
  chevron glyphs); the front forecast is red dashed grease pencil; CAUGHT is pink binary bits; the raid % is bare Anton. Next: a proper 3D
  render of A, then the Godot port.
- **Per-hue hot core applied (designer, 2026-10-22, look-toolbox module 11):** "Approve + 1px min core" on
  `D:/rc_scratch/rc_look/hotcore/hotcore_sheet.png`. Each tube runs 0.9 toward mix(white, tube, 0.15) on its centre 35%, with a floor of
  1 px so far trims and bands keep a core line. This covers city_building (sign strips, trims, bands), hq_solace_pbr (neon role) and
  dress_sign. The fence on city_building and hq_solace_pbr lifts for this change only.
- **Hot core on thin tubes (designer, 2026-10-22):** the proof (`D:/rc_scratch/rc_look/hotcore/hotcore_proof.png`, art/look-toolbox-2
  c806d617) showed the 1 px floor turning 1-2 px far trims near-white. Ruling: "Fade core on thin tubes". Keep the 1 px line, but on
  tubes under ~3 px wide fade the core strength toward ~0.45 (from 0.9), so far tubes keep their hue. Close tubes stay as approved. The
  numbers live in look_sign.tres "hot".
- **Binary bits, look-toolbox module 16 (designer, 2026-10-22)** (`D:/rc_scratch/rc_look/m16/m16_rulings_sheet.png`):
  1. The hot flash (first 0.08 s) is PAPER #F2EEE4 on every bit system. The designer picked this over WHITE_HOT.
  2. The outline is a NIGHT_SKY rim at 95 %.
  3. Motion goes by job: bursts (CAUGHT, hits) flip 0/1 and tumble; data streams keep steady 1/0 glyphs with a trail copy.
  4. Every bit starts its tumble at its own spin phase, and the CPU fallback is matched to the GPU.
  5. Art-pass call: a turn stays 6.28, not TAU, so the move to the module stays bit-exact.
  Lab-only until the raid redesign lands.
- **Solace night air (designer, 2026-10-22)** (`D:/rc_scratch/rc_look/spillair/spillair_sheet_b.png`): air-B, with no helix spill. Night
  air starts at 150 BU, colour sRGB (0.12, 0.10, 0.18), density 0.004, as a Solace night preset in look_air.tres. The pov sky comes to
  54 (plate 55). Spill is dropped: it lifts every city mass, towers included, and the Solace emissive fallback covers the ground.
- **Vinyl stickers, module 13 (designer, 2026-10-22)** (`D:/rc_scratch/rc_look/m13/vinyl_sheet.png`):
  - Designer: the holo band is one "\" shape (top-left to bottom-right) for kit and chrome. It runs parallel to the peel, which starts at
    the top-right corner. The kit already has it, so the chrome changes.
  - Designer: the played-card seam switches from card_sticker_fx to the kit sticker.
  - Art-pass calls, following existing docs:
    - Chrome drops its second white sweep (its header and DECISIONS say one band, not white).
    - Disabled is Palette.STICKER_DISABLED_GREY 80 % grey with alpha 0.8, on both.
    - Extrude and shadow use VINYL_EXTRUDE #09080C on both.
    - The pink verb fill stays STICKER_FILL_PINK; STICKER_COMMIT keeps its own HUD role.
    - Chrome sweep_width comes from a single source (run_sweep).
    - Missing-art verbs keep the PINK fallback.
- **CRT reduce effects, module 14 (designer, 2026-10-22)** (`D:/rc_scratch/rc_look/m14/shots/crt_reduce_night_t2.png`): KEEP_STATIC
  everywhere. Reduce effects stops flicker, roll and scroll; the still scanlines (and the fx vignette) stay. Only high contrast removes
  the static texture. The ZERO_SCAN (ui_theme, neon_city) and HIDE (fx.gd) paths move onto this rule when migrated.
- **Solace THE BLOOM v2, A "Necrosis" in 3D (designer, 2026-10-22)** (`solace_vertical/bloom/sheet_A3d.jpg`, b0edc525):
  - Port A to Godot, look only, with no raid-outcome wiring while the raid redesign is paused. The decision shot's front lift (about 2
    floors above the gap-1.25 rule, to keep it in frame) is OK'd.
  - Push the HQ overview front: a brighter hot hairline plus a faint spore haze just above it, with the body still plum-black, so the
    front separates from clean at thumbnail size.
  - The raid body goes darker plum: plum-black skin with hot pink veins and front edge, as on street and HQ. The TIDE gauge and % stay
    the loudest elements. The raid view itself waits for the redesign.
- **Solace backdrop stills (designer, 2026-10-22)** (`solace_vertical/hq/godot/stills_then_now.jpg`): the re-baked stills match the
  live close-up, so the hand-over has no pop. Day stills = night stills until a live day look exists, because CombatBackdrop's city path
  ignores place.day. A real day backdrop would be its own task. Art-pass call: the live Site close-up framing gets fixed (fit to the S2
  hospital, cut the towers in front of it). Today the hospital is buried and the subject doesn't read.
- **Netrun street, look-toolbox module 10 (2026-10-22)** (`D:/rc_scratch/rc_look/sheet10/sheet10.png`):
  - Designer: drop the megastructure from the street plan (plan_pass, the dressing.signs mega clause, and the r2 Python twin). It was
    an AD critique item, never a designer ask, and it was never drawn.
  - Designer: open a slice for the near-black frontage slab, the left ~45 % of every na23 overview, which fails the squint test.
    Look only (light, glow or framing options on a sheet); no layout rule changes without the designer.
  - Art-pass calls: keep both facade washes (each lights different facades, so neither doubles), and keep decision fog constant at
    0.12 by deleting the no-op lerp.
- **Bloom reach in Godot (designer, 2026-10-22):** the tendril reach scales with the street's layer spacing, not a fixed 24 BU, so
  CREEPING sits about one layer ahead of the front on any street, and each TIDE band reads the same everywhere.
- **Street slab (designer, 2026-10-22):** the black slab in the street view is the A2 elevated deck and its pillars
  (Ground/A2Features), drawn with the wet_street ground material. Two fixes:
  - The deck's non-flat faces get a concrete lift by world normal (option A: albedo lift, matte roughness, spill on their own
    normal, violet rim).
  - The deck is hidden from the street camera only. It stays on the city map and the HQ, and no layout rule changes.
  - Goal: an open skyline like the plate. The remaining gap in overall brightness to the plate (L ~30 vs 53) is a separate item.
  - Sheet: `docs/concepts/look_parity/slab/slab_sheet.png`.
- **Street car lights (designer, 2026-10-22):** the street kit's headlight_emit and taillight_emit slots glow (headlights warm white,
  taillights red, emissive) instead of falling to solid. The toolbox sends a before | after sheet with squint rows before it ships.
- **Street brightness gap (art-pass, 2026-10-22, from the per-band sheet `docs/concepts/look_parity/gap/`):** the gap to the plate is
  in small bright points, not in the median. The plate has 10-40x the bright blobs per MP and about 1 % of pixels over 0.85; ours has
  about 0. Decision facades already match on value.
  - The fix is detail density, with no exposure lift: lit window, sign and neon trim points on the overview facades, and wet streak
    reflections of those lights on the floor.
  - Overview framing moves toward the plate (facades fill most of the frame, sky about 10 %).
  - Targets per band: R-DET-2 and over_085 toward the plate, R-HUE-1 >= 3.8.
  - This goes before module 18, so perf measures the final load.
- **Car lights, clarified (designer, 2026-10-22):** ground_car.glb is placed in no view. The cars on screen are the city's procedural
  cars, which already have glowing lights.
  - Keep the slot fix (headlight_emit / taillight_emit emissive, max 0 today) so the model glows if it is ever placed.
  - The moving cars' light brightness is judged inside module 19 (detail density) against the plate's light trails.
  - No parked cars are added.
- **REST / WORKSHOP / CACHE nodes (designer, 2026-10-22, sheet `docs/concepts/solace_vertical/nodes/sheet.jpg`):**
  - Icons use C "Slap-tag": a saturated house / wrench / brick-stack glyph with a white contour die-cut and no disc.
  - Pages use A's event layout: the window plus the RUN column, with the icon stamped beside the title.
  - CACHE gets a header-only loot variant: the kind stamp and CACHE in the strip. The title stays LOOT and there is no new text.
  - The CACHE colour moves off FIGHT's cyan, checked for distance under deutan.
  - Art-pass ruling (bible §forecast pencil): no orange pencil plan arrows on the node pages. Forecasts are red dashed what-ifs only.
- **Street skyline fill (designer, 2026-10-22):** keep the sky. No infill blocks behind the far frontage and no raised real buildings.
  - The overview camera already matches the plate.
  - Module 19 closes the gap with lighting only: (a) face washes plus clustered hot windows plus signs and edges, and (b) floor
    streaks.
  - The sky share (39 % vs the plate's 10 %) is accepted. Judge facade numbers per band, not by frame totals.
- **Module 19 (a) review + (b) fence (art-pass, 2026-10-22):**
  - (a) is approved, with one fix: no face wash on a block next to a route column. On decision seed 2, VOLTA's neighbour became a
    flat, full-height pink column that competes with nodes 1-2 (readability first).
  - city_post hold, lifted narrowly: street-only `look.post` wet_refl overrides, applied by route_rig, with no city_post code
    change. The city map and every non-street frame stay max 0. Any city_post code change still needs a sheet to art-pass.
  - Live stomp: CityViewMotion.set_night_share rewrites whole_building, so it drops the street's look overrides in live play. The
    street look must survive it. Route_rig re-applies its overrides after every night_share and look change. This is proved with
    an unfrozen live test, not with frozen captures only.
  - Denser frontage signs and edges through the r2 rules (both twins plus the oracle fixtures) are approved as step (e), after
    (b).
- **Nodes implementation review (2026-10-22, sheet `solace_vertical/nodes/godot/impl_sheet.jpg`):**
  - CACHE icon (designer): a brighter, hotter brick red, so it reads on the dark map at the squint. It may give up some tritan
    margin, but must stay ΔE >= 30 normal / protan / deutan from every kind, room and state colour, and the ELITE fill is still
    separated by the outline. The CACHE room glow follows the new hue.
  - RUN column (art-pass): dropped from the REST and WORKSHOP pages. It repeats the top bar's HP and Cycles, and the shipped event
    page dropped its RUN terminal for the same reason.
  - Page backdrop (art-pass): the new colourful isometric city behind the page competes with the terminal. Dim and scrim it to the
    event page's backdrop level (readability first).
- **Module 19 (e) skipped (art-pass, 2026-10-22):** denser r2 frontage signs and trims barely move R-DET-2. Even at maximum they
  close about 2-8 % of the gap, and the change would churn the twins and the oracle. It is recorded as a measured finding. The
  rest of the plate's point density lives in a denser near city, which the designer declined ("keep the sky").
  - Module 19 closes after the (b) floor fix: no milky mirror slabs on the overview floor, and decision seed 2's floor eased to the
    plate median.
- **Culture garden EX-11 (designer, 2026-10-22, sheet `solace_vertical/garden/sheet.jpg`):** direction **B "Culture stack"**,
  without the thin spires / masts standing around it. The lot is **48 x 42 BU** (the spec's 48 x 36 plus the plaza apron), with
  clearance kept at 8 (posted to build as A-100).
  - The implementation must fix three things:
    - the Bloom reads as a hot pink fill; it should be A Necrosis's dark plum body with a hot edge;
    - the AAA-2 highlight clipping (3-8 % above 0.85);
    - the mint agar stays at hue ~147, clear of the HQ lime.
  - Owed with it: the SOLACE GENERAL game-path frame.
- **Tide raid look (designer, 2026-10-26, PLAN_2026-10-26 §5 Q1–Q4):**
  - **Q1:** art-pass owns the raid look (cards, raid view, colours, lines, indicators, alerts). Build and the raid lab keep rules,
    flow and layout. A raid visual design pass (2–3 concept directions on the real Solace territory plus a fresh critic) comes
    before tide groups A–D.
    - Vision: a living, vibrant, detailed city street map, like Google Maps seen through a semi-isometric 3D camera.
    - **Hard fail:** no wall of text. No PLAN / HQ STEP / AFTERMATH / RESPONSE panels carry the raid.
  - **Q2 tier colours:** a severity ramp.
    - BREACHED = HARM red with a stamp; DAMAGED = orange; SITES LOST = amber; HOLDS = teal; CITY LOST = the skull glyph.
    - A held raid is never red (A-085).
  - **Q2b:** EVADED moves off lime to a cool mint / cyan-white. The focus halo keeps lime game-wide (D25).
  - **Q3 infection:** the Bloom A necrosis look, a plum body with a hot edge, replaces the #FF3DA8 pink. The N beam (#FF40D6) gets
    a shape cue and a hue that reads against plum.
  - **Q4 marks:** one shared D28 grease-pencil helper draws DOWN and TAKEN in both raid models.
- **Tide raid concept round 1 (designer, 2026-10-27, sheet `tide_raid/compare_sheet.jpg`, critic `tide_raid/CRITIC.md`):**
  - Not picked. Scores: A Live Nav 38/50 (Vision 8); B ctOS 31/50 (Vision 5); C War Table 38/50 (Vision 4). None fully passed the
    no-panel test: the sealed and hunter reveals failed in all three.
  - The designer asked for a second round, one direction with a **circuitry look**, remembering that "this is a cyberpunk world we
    are hacking". After it, the designer combines the best of all six.
  - **E beam = signal yellow** (it was orange, which is now DAMAGED). D stays blue, N magenta with a shape cue.
- **Tide raid direction (designer, 2026-10-27, sheets `tide_raid/compare_sheet.jpg` and `compare_sheet_r2.jpg`, critic
  `tide_raid/CRITIC_R2.md`): the hybrid "Jack-in over the Night City".**
  - Base E Jack-in:
    - ICE data towers on the Sites only;
    - black-ICE daemons, used as type-silhouette heads on a single beam body;
    - E's wordless sealed reveal (a fog corridor and a letter lock that opens into the type silhouette);
    - E's HUNTER reveal (an eye and a reticle locking one street).
  - Over F's saturated night grade.
  - Takes:
    - from F: the intent tiles, the grease-pencil odds tally at HOME and the wheatpaste verdict poster;
    - from A: the traffic-coloured route chevrons;
    - from D: the HOME tick ring with a damage chip, the plum infection with a hot hairline, and the HOME-hit burst;
    - shield flash with bits.
  - Drops:
    - E's blue grade and side bars;
    - D's decorative copper and analyzer panel;
    - F's paint-everywhere, outcome strip and legend stack;
    - A's day grade.
  - Keep the hunter eye white; yellow is the E beam alone.
  - Next: render one hybrid concept set for the designer's sign-off before any Godot work. Then tide groups A–D build toward it.
- **Tide hybrid concept set (designer, 2026-10-27, sheet `tide_raid/H_jack_in_hybrid/sheet.jpg`): not signed off.** The designer:
  it "is not even close to a polish visual look… at the proof of concept basic stage". Two stages follow, both in art-pass:
  1. **Settle the concept.** One more concept pass fixes the grammar:
     - the cold braid: split the tier rails from the tower cyan;
     - D blue lost at squint;
     - amber against E yellow;
     - the busy ram head;
     - D, N and E shown together.
  2. **Iterate the visual polish** to true golden plates (AAA finish, critic-scored against real refs) that the Godot run can match
     for parity. No tide group starts in Godot before the designer approves the plates.
  - **Polish scope (designer, 2026-10-27):** the polish passes add **animation concepts, storyboards and interactivity concepts**
    (motion tests, hover / drag / focus states, the what-if preview). The target is to **beat the critic's visual scores of the
    reference games**. A fresh critic first sets the baseline in `tide_raid/REF_BASELINE.md`. The brief is
    `D:/rc_scratch/tide_concepts/BRIEF_POLISH.md`.
- **Toolbox on hold (designer, 2026-10-27):** module 18 (perf) and the module 19 README wait until the tide raid design work wraps
  up, because design changes may overtake them. The toolbox commits where it stopped on art/look-toolbox-9 and stops; it posts no
  READY.
- **Solace roadmap paused (designer, 2026-10-27):** garden B (in progress on art/solace-garden) and the rest of the Solace queue
  (OURS NOW, the cohesion audit, the key-lot buildings) pause until the tide raid concept passes wrap. The designer then reassesses,
  because the two lines touch many of the same areas. Solace commits where it stopped and stops; it posts no READY.
- **Tide hybrid concept pass 2 (designer, 2026-10-27, `tide_raid/H2_jack_in_settle/`, grammar.png):**
  - **Tier carrier:** on the target only (a tier ring under the Site, a stop block where the beam dies, the intent tile). Beams stay
    pure type hue. Polish makes the ring and block bolder so the tiers read at a squint.
  - **Yellow** marks the E type everywhere it answers E (a card tab, the guard wall against E, glyphs), never as a full card fill.
    Blue for D and magenta for N follow the same rule.
  - **Heads:** not settled. Run a head-shape exploration (options per type) before polish.
  - **Tritan:** DAMAGED orange, BREACHED red and the N magenta collide under tritan. Fix this in polish: a yellower DAMAGED and a
    non-hue cue on the HOME-hit burst.
