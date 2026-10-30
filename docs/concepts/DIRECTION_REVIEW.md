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
- **Beam heads, round 1 (designer, 2026-10-27, `tide_raid/H3_heads/heads_board.jpg`): none picked.** The designer likes the
  *identity* of B (daemon creatures with character), but the detailed icons don't work, so the next round must be simpler. New
  themes to explore:
  - computer hacking;
  - corporation-themed (Solace: bacteria, virus or medical);
  - military.
  Every family needs simple bold silhouettes that read at 24 px and keep a creature-like or character identity.
- **Beam heads, round 2 (designer, 2026-10-27, `tide_raid/H4_heads/heads_board.jpg`): still not settled.** The designer prefers a
  **mix across families**, but isn't settled on the icons themselves. Keep iterating. Each type needs a distinct icon and its own
  identity, but the three must share a **cohesive theme**.
- **Beam heads picked (designer, 2026-10-27, `tide_raid/H5_heads/heads_board.jpg`):**
  - D = the T2 worm;
  - N = the T5 thorn claw;
  - E = the T4 sea-mine / virion, drawn about 15% smaller than N so N and E separate by size;
  - the 4th unit (bonus) = the T2 beetle.
  The in-game look follows the **family-test row**: heads at about 40–48 px in the raid (scaled at 1280), with the shared rim light,
  core dot and outline. Next: one finalise pass to harmonise the four heads into a single language, then the plates take them.
- **Beam heads locked (designer, 2026-10-27, `tide_raid/H6_heads_final/`):** the harmonised family at **44 px at 1920 (29 at
  1280)**, with SVG sources in `heads/`. In polish, the N claw gets thicker prongs and an asymmetric hook so it never reads as "£" or
  "3" at any heading. Crowd-test finding for build and the plates: draw Site tags and tier pips **above** the beam/head layer,
  because a parked head hides 81–91% of the pip strip at every size.
- **Tide polish iter 1 (designer, 2026-10-27, critic `tide_raid/CRITIC_P1.md`: S8 V8 R8 M8 W8, bar not beaten):**
  - DAMAGED = FF9A00 (accepted from the tritan fix).
  - **SITES LOST** keeps C98410 ochre, drawn as an **ink-black ring with a white rim, ochre hatch and its own tier glyph**, so it reads
    by value and shape. Every tier must stay distinct at 320 px in greyscale.
  - **Iteration 2: go.** It runs the critic's top 10 on one shared base: the P1 plate, the H6 heads and the palette. The plates,
    motion and interactivity must all match, and the next critic views every plate and real MP4 frames.
- **Tide polish iter 2 (designer, 2026-10-27, critic `tide_raid/CRITIC_P2.md`: whole S8 V8 R8 M8 W8, plates S9 W9).** Iteration 3
  runs two tracks:
  1. **Plates:** the critic's top 10, including the tier-tile anchor bug, tiers that survive at 320 px, hero light shafts, declutter,
     the lock glyphs in 03, a quieter cage and hidden ambient ground marks.
  2. **A real-time Godot prototype** of the daemon travel and the HOME hit. It lives only in the art-owned tide_fx.gd / tide_look.tres
     (plus the grid Bloom front API and a lab capture scene), on an art branch, with no rules or flow code. Its captures become the
     true motion reference and prove the plates can be built.
- **Godot must look like the plates (designer, 2026-10-27):** the critic is skipped on the prototype. Art-pass may **build new tools
  and challenge the current Godot city build** on the art branch (art/tide-proto in D:/rc_art/godot_look_tide, separate from main).
  In scope: city materials, lights, post / grade, signage and props, plus the parity tooling. The target is the P2/P3 plates.
  - City layout, gameplay data and generators stay build's. If a look change needs a data or flow change, write it as a spec.
  - The critic returns only for live Godot frames, once parity is close.
- **Overnight parity bar (designer, 2026-10-27):** "be very critical when comparing godot to the plate and do not settle for
  anything. Iterate and fix till it looks extremely close and then pass it to the visual critic for their score."
  - Acceptance: the plate and Godot are indistinguishable at a glance (full size and at 320 px), the per-band metrics are within
    tolerance, the signature elements are present, and perf is measured.
  - Only then does a fresh critic score the live frames.

## 2026-10-28: Waves converged study, designer answers
- **Adjuster / enemy types:** an enemy type can be a unit, a satellite or a ring. The Adjuster is ultimately the boss of the wave fight and may affect other enemies and the battlefield. Art must give the boss a look that works in all three forms (unit cell, rim satellite, whole ring).
- **Wide units:** units may stretch across sectors, up to the full sector span, which makes the unit a ring. One stretched cell is the drawing rule.
- **Nudge:** it may be reconsidered in the new combat approach (a rules question for build). Art does not draw nudge buttons for Waves until it is settled.
- **Converged look adopted (designer, 2026-10-28):** "converged look is the primary front runner, use it". Shifting Waves uses the converged single board drawn in the ART_BIBLE's media. ART_BIBLE §3.22 was added with the ring-wheel rules (from the converged study's amendments, reworded for the PL7 lessons), and the §3.1 "no forecast tags" bullet now carries the ring-wheel exception. All E7 plates use this look.

## 2026-10-28: Tide raid, Godot vs plate review (designer)
1. The live beam must be one blended ribbon, not overlapping segments.
2. The plates' shadows read deeper than Godot's. Godot gets runtime AO and sky visibility from the city height field.
3. **No cage around the HQ** (agrees with Godot). Remove the green cage from the golden plates and the STYLE_CONTRACT.
4. Bug: roads show through buildings in Godot. Fix the occlusion.
5. Smooth the river banks, even where that deviates from the plates.
6. HOME hit chip: the plate's hexagon icon with the "-6" damage number.
7. HOME hit: keep Godot's attacking-enemy head icon over the blast (supersedes the plate's bare flare).
8. The **river** through the city (the jagged light line near the bottom of plan view 01) must read as a real flowing river, deliberately deviating from the plate (designer: "the river look should deviate from the plate look"). Give it smooth banks, a slight blue hue, ripple-distorted reflections and subtle texture, never a mirror. The bay water was fine: keep its round-6 look (the round-7 bay edits were a misread and are reverted).

## 2026-10-28: Shifting Waves E8, hit/HP representation (designer)
- **Option A is adopted** (study: docs in D:/rc_scratch/combat_polish/E7_waves/repr/, REPR_STUDY + REPR_ALT; A scored 18/20 across 10 options).
  - Unit HP = cream lit segments in a dark socket along the unit's arc.
  - Hit = 1-4 red chevrons on the inward edge of each covered sector. A single chevron has no stem; stems appear only on stacks of 2 or more (critic note).
  - Defense: shield = a cyan bracket over the segments, emptied first; armor = a bevelled steel rim cap; sealed = faint whole-ring hatching plus a padlock and a SEALED +2 tag.
- **Tower slice HP:** option H's thin floating bar with 2 segments. Build confirmed slices keep 2 HP in E8 (3 only if the census needs it): intact / cracked / broken. Breaking a slice loses its ability and drives the scrap star.
- Raw numbers stay off the board (designer's E8 ruling).

## 2026-10-28: Tide raid city, Godot round 7 review (designer)
1. Keep the amber lamp ambiance, but place lamps logically: along streets, at intersections, on plaza edges and bridges. No random scatter. No streetlights along highways. If the lamps become too much, shrink them (glow and pool) rather than thinning them: keep the density. Hide the bright square lamp source (a housing would block it); show only the cast light (soft round pools, faint wall spill), and keep shrinking the pools toward a realistic look. Avoid light grids: no lamps inside open areas (edges only), keep dark gaps, jitter the spacing and drop some lamps, so lamps read as strings along streets.
2. Highways must join with logical interchanges (ramps, flyovers), never overlap.
3. Add a few mini city-block parks in the Solace sector.
4. Car lights must ride on the roads.
5. Many more windows and window lights, at lower intensity so the building colour still comes through. No clutter.
6. More building shape variety: setbacks, L and T footprints, rounded or chamfered corners, podium towers, roof features. Varied by district.
7. The beam still looks bad. Mimic the plate's clean transitions at the beam's corners and intersections.

## 2026-10-28: Shifting Waves E9 (designer)
- The big "lands → through" pair stays as digits: the one exception to "no raw numbers". The option chips' lands > through pair counts as the same quantity. Every other count stays as marks and tallies, with digits only on hover.
- Pink is reserved for unit screens only (designer): the CELL-9 sticker and code-base frame are cyan, SEND IT is yellow and the lane is pale blue. Recorded in ART_BIBLE §3.22.
- PL10 conflict resolved: keep pink for unit screens, but darken or desaturate the unit bodies so the red chevrons pop.

## 2026-10-28: Tide raid city, round 9 review (designer)
1. Still too many lights in open areas: cut the lamps around open ground, so open ground reads dark.
2. Give each streetlight a seeded random intensity for variation.
3. No lights along the river (quay lamp row removed).
4. No pink in the gardens: remove the bloom domes and the plum park-edge glow; parks are green only. This supersedes the earlier "magenta blooms" direction, which came from the plate.

## 2026-10-28: Tide raid city, night-light guide from the designer's real-city refs
The refs are NYC aerials and Tokyo river and highway shots; local copies are in D:/rc_scratch/g1/refs_night. They guide the light only. The designer wants MORE building colour than these photos show.
1. **Light lives on the street network.** From altitude, streetlights merge into continuous amber lines along the streets, not separate dots or pools. Main avenues are brighter and wider than side streets, and the street grid is the brightest pattern in the city.
2. **Highways glow from traffic, not lamps.** They read as warm orange or red ribbons, from sodium deck light and tail-light streams, with white headlight streams in the other direction. Interchanges are bright tangles of these ribbons.
3. **Open areas are dark voids.** Parks are near-black, like Central Park, with at most a faint path line. Plazas and vacant ground stay dark.
4. **Water is black.** It shows only smeared reflections of the lit shore and bridges. Bridges read as strings of lights along the span. There are no lamp rows along the banks.
5. **Buildings:**
   - windows are tiny, dense points;
   - light concentrates at street level (storefront glow at the base);
   - upper floors are sparser;
   - tall towers carry accent lighting (lit crowns, cyan or white LED edges).
6. **Colour mix:**
   - warm sodium amber is the base;
   - cool white or cyan LED is the second voice;
   - magenta, pink, violet and blue signage clusters at commercial hotspots (Times Square / Shinjuku style), not spread evenly.
7. **Contrast:** deep near-black darks between bright lines. Optionally, low haze glows over the densest districts.
- **Cyberpunk colour refs (designer, second set):** Shibuya aerial, Shinjuku street trails, two wet neon streets; local copies `cp_*` in D:/rc_scratch/g1/refs_night.
  - **The Shibuya aerial is the closest match to our camera.** Its colour comes from the facades: giant screens and billboards are saturated rectangles (cyan, magenta, green, orange) on the building faces and roofs. Sign spill tints the bodies (pink, cream, teal).
  - Crossings and plazas in the hotspot are bright white or amber. Trees are dark green, lit from below.
  - **Palette:** deep blue-black sky and shadow; cyan/teal plus magenta/pink as the neon pair; amber sodium and orange/red tail-light trails; white headlights; green accents.
  - **Wet streets in the hotspots** reflect the neon as long vertical colour streaks. That fits our rain, but only in the neon districts. Elsewhere the streets stay amber and dark.
  - Apply the signage colour as facade screens and spill in 1-2 hotspots per district. The rest of the city follows the night-light guide above.
- **Street-lamp falloff (designer):** street light lights the street and the bottom of buildings, then fades dark going up, by about 3-4 floors. Today it projects upward and misses the building bases, which is a bug. Upper floors are lit only by windows, crowns and signage.

## 2026-10-28: Tide raid city, round 10 review (designer)
- Agrees with the art-pass issue list for round 11: the neon hotspots, the street grid as the brightest pattern, the mid-tone veil, building shapes that read from above, and the low-district light grid.
- Lower the streetlight intensity overall, and further in low-building areas, while keeping the line read and the density.
- **Tone up the neons (designer):** "this is a futuristic cyberpunk city in a video game". Neon goes past photo realism:
  - more and stronger hotspots, and neon avenues;
  - background signage everywhere: blade signs, edge strips, rooftop logos;
  - saturated cyan and magenta plus accents;
  - floating holo ads above the tallest towers;
  - stronger spill and wet reflections.
  The streetlights stay dim amber, there is still no pink in parks, and the darks stay deep.

## 2026-10-28: Tide raid city, round 13 (designer)
- "I actually really like where it is." Round 13 (art/tide-proto de4c3896) is the baseline.
- A visual critic scores round 13 as is.
- A neon-pushed variant is being built on the separate branch art/tide-neon-push, exposed as a config preset, for comparison.
- **Critic review (30/50) and neon verdict (designer):**
  - "r12 was better." The round-12 neon look is preferred over round 13 and over the neon-push. Neon-push stays an off preset.
  - Take critic fixes 3-8. Fix 1 is NOT taken: the street grid stays dim as ruled.
  - Fix 2 is replaced by: increase the traffic head- and tail-lights.

## 2026-10-28 night: autonomy for the city iteration (designer)
"Progress through the iteration by making your own calls and logging them. Keep in mind the real city references, and this is a cyberpunk game, and to follow logical placements of all things in the scene."
- Art-pass makes the city look calls overnight and logs each one below as "ART CALL".
- Guardrails:
  - the real-city refs in D:/rc_scratch/g1/refs_night;
  - a cyberpunk game look;
  - logical placement of everything in the scene: lamps on streets, traffic on roads, signs on facades facing streets, holos above tall towers, nothing floating or detached;
  - every earlier ruling still holds.
- Nothing merges or replaces final/ without the designer's review. Work stays on art/tide-r14 and its successors.

### Overnight art calls
- ART CALL 1 (round 14c): the hotspot tree underglow is off entirely (it made pale mint wedges). The crossing glow is at 0.05.
- ART CALL 2 (round 15): neon signs go only on street-facing walls. When a building has a street on more than one side, prefer the camera-facing one. No signs on walls facing an alley or a neighbouring wall.
- ART CALL 3 (round 15): an automated placement audit runs every round. Every neon quad is checked against its building's footprint, height and steps, and nothing may float, clip or face a neighbouring wall.
- ART CALL 4 (round 15): bridges get light strings along the span: lamps on both rails at a regular spacing, warm amber, as in the Tokyo river ref.
- ART CALL 5 (round 15): spread hotspots to the north-east and far south-west. Every district has at least 1 cluster, with dark gaps between clusters.
- ART CALL 6 (round 15): the brown arc gets traced by dumping the node tree, then removed or fixed.
- ART CALL 7 (round 16): round 15 made the neon too calm for a cyberpunk game, because the street-facing-only rule cut the screens.
  - Screens may face streets OR plazas (still never alleys or neighbouring walls).
  - Hotspot screen counts and gain go back to r14 loudness.
  - Holos go up from 5 to about 10-12 in the plan, over tall towers only.
- ART CALL 8 (round 16): the corporate district wall (A2Features/Walls, the "brown arc") is a real feature of the plan, so it is redrawn instead of hidden. It becomes a dark security wall with a thin red/cyan light strip on top and gate lights at the checkpoints, never lamp-lit amber.
- ART CALL 9 (round 16): the river stays thin until build's A-104 lands. Bridge strings stay.
- ART CALL 10 (round 17): the redrawn district wall reads as a thin grey pole slicing through buildings, and its light strip doesn't show.
  - The wall may never clip a building. Building lots touching the wall route are skipped or set back.
  - If the plan's wall route crosses building lots, that's a build spec.
  - The wall goes to about 2x thickness, with a visible red or cyan top strip at the plan camera.
- Critic on r16: 29/50 (r13 was 30). Review: D:/rc_tmp/visual_critic/city_r16/REVIEW.md. The main regressions are a darker, flatter frame (p50 0.265 / p75 0.369 vs plate 0.325 / 0.481) and the wall artefact.
- ART CALL 11 (round 17): lift the plan value back to about p50 0.31 / p75 0.43. Do it by brightening lit windows, crowns and street-facing lower walls. NOT by brightening the street grid (ruled dim) or lifting the blacks.
- ART CALL 12 (round 17): round 14's traffic ribbons, district tints and roof-tile thinning are too subtle to register. Push each until it reads at the plan camera: traffic as continuous red/white ribbons, district tints at a distinct hue, roof tiles on ≤20 % of roofs.
- ART CALL 13: the critic's "saturate the neon" conflicts with the designer's "r12 was better", so the r12 character is kept. Only the cream and white FILL blocks get cut, not the white-hot glow.
- ART CALL 14: the dark cubes in the seed-3 HQ park are real Solace site buildings, so they stay. They get campus styling (lit glass pavilions, roof gardens) instead of being removed.
- ART CALL 15 (round 18): the elevated rail and stations are real plan features, so they are drawn, not hidden (r17 had hidden them).
  - Like the wall, building lots under the rail route are skipped in the view so no building is pierced.
  - The plan reroute goes to build as A-106.
- ART CALL 16 (round 18): the Solace campus roof gardens in r17 read as flat, bright green squares (placeholder look). Use darker, varied greens with tree tufts and a lit path, at a glance the same family as the HQ park.
- Round 18 accepted:
  - rails and stations are back, with no building pierced (the view skips building lots on the route);
  - campus gardens are dark and varied;
  - lamp pools are softer;
  - p50/p75 are still on target.
  The A-106 ask now carries the counts: the rail crosses 869/940/773 building lots on seeds 1/3/7. A fresh visual critic is scoring r18.
- Critic on r18: 29/50 (review: D:/rc_tmp/visual_critic/city_r18/REVIEW.md). The score has plateaued at 29-30 since r13, so the approach changes.
- ART CALL 17 (round 19, reverses ART CALL 15): until build reroutes the rail (A-106), the rail and stations are hidden and the city keeps its buildings. The rail read as a hairline with a dangling pod, and the cleared lanes left diagonal scars. Logic wins over completeness: no rail through towers and no scars.
- ART CALL 18 (round 19): the core of the plateau is the 320 px squint, which reads as one purple mass. Since the grid stays dim (ruled), structure has to come from three things:
  1. the highways as bright warm ribbons: dense red tail-light and white headlight streams plus a lit deck edge, the brightest LINES in the frame (as in the Tokyo highway ref);
  2. districts with distinct value and hue, separated by dark gaps;
  3. a few white-hot vertical tower accents, like the plate's pale glass towers.
  Each is judged on the squint itself, not on close-ups.
- Round 19 accepted: the clearest step since r12. Districts now read, highways are warm lines, white towers act as landmarks, and squint structure is up 12-14 % (83-89 % of the plate).
- ART CALL 19 (round 20):
  - Highway glow becomes crisp light lines: drop the flat additive slab that reads as a peach haze band over the roofs, and keep the red and white streams plus a thin edge.
  - Dark-gap buildings drop from 23 % to about 10 % of the frame. They read as black slabs.
  - The teal district reads blue-white, so its value comes down.
  - White towers go down to 8 in the plan frame.
  - The magenta low-rise district is toned down 20 %, so it doesn't fight the neon.
- Critic on r20: 30/50 (review: D:/rc_tmp/visual_critic/city_r20/REVIEW.md). The rail pole is gone, but removing the glow plane lost r19's warm highway read.
- ART CALL 20 (round 21):
  - **Highways:** restore r19's warm highway ribbons from vehicle light only. Wide warm tail-light and headlight streams with bloom, no flat glow plane, no lamps.
  - **Core zones:** 3-4 value and temperature zones that survive the squint. Enlarge the amber district toward the lower left as on the plate, keep dark seams at 6-8 %, and lower the base window gain rather than the exposure to raise structure.
  - **White towers:** clearly brighter than their neighbours.
  - **Roof outlines:** on under 15 % of roofs.
  - **Magenta and violet low-rise blocks:** more varied footprints.
  - **Hotspots:** narrow wet streaks under them.
  - **Seed-3 campus towers:** lit pavilion roofs.
- Round 21 accepted with one fix. The squint now has real zones: a warm lower left, a dark cool centre and a violet/glass right. Highways read warm again, structure is 0.144 full frame and 0.164 in the core, and perf is fine.
- ART CALL 21 (round 22): the amber district's building bodies have drifted to salmon/orange, which is the round-6 defect. Its warmth has to come from LIGHT (amber windows, storefront glow, warm crowns) on violet-indigo bodies, as on the plate. Fix the bodies and keep the zone's value. Also identify and fix the pale pink translucent columns beside the hotspot tower.
- Round 22 accepted in part. The bodies are violet-indigo again and the tail lights are redder. p50/p75 are on target (0.306/0.431) and perf is 12.35 ms. However, the district now reads PINK-LILAC rather than amber, both on the squint and in the close-up. The plate's lower left is dark bodies with dense warm-amber window dots, and it has no pink. Coarse structure fell to 0.139 (r21: 0.144). The pale columns are still there. They are opaque towers in the shared pale-concrete family (`concrete_fam`), washed out by lilac spill and bloom.
- ART CALL 22 (round 23):
  - **Amber district:** the lilac spill, bloom and neon tint on bodies are cut or tinted amber inside the district, so the light that reaches the bodies is warm. The window dots are pushed toward deep amber/orange (plate), not peach.
  - **Pale columns:** pale-concrete towers are overridden per building in the CITY path only, through a city-side instance parameter. The shared family values stay as they are, so the netrun is unchanged. In dense districts they become the dark glass/indigo family. Only the ruled white-tower accents (up to 8) stay pale, and they must read as lit glass, not translucent.
  - **Structure:** coarse structure has to come back to at least 0.144.
- Round 23 accepted with one fix. The pink is gone from the amber district, the 320 px squint now has a clear warm lower-left zone, coarse structure is 0.147 (above r21) and perf is 11.57 ms. The pale-concrete override is city-only.
  - **Leak found:** the art districts had leaked into the street netrun since r19, through the shared CityView3D. It is now gated by `CityView3D.art_look` (false in route_rig.gd). This is a logical fix and it is kept; it must be named in the build hand-off.
- ART CALL 23 (round 24):
  - **Amber district overshoot:** the district now overshoots. At gain 20 the faces read as solid orange terracotta, the round-6 "brick" problem coming back through light. The plate's lower left is dark bodies with crisp amber window POINTS and dark mullions between them, so it sparkles. Window gain drops so the face between windows stays dark, the windows become smaller and crisper points, the lit share varies per floor (a few fully lit floors, many dark ones), and the warm glow at the base stays. Its warmth has to survive the squint at a lower face fill.
  - **Pink-lilac towers beside the hotspot:** they survive every mesh and post toggle, so the suspect is a LIGHT. Dump and toggle the light sources near the hotspot: omni/spot lights, lamp-plan lights, the env/reflection probe and the hotspot's own light.
  - **Critic:** a visual critic runs on r23 in parallel.
- Critic on r23: 29/50 (review: D:/rc_tmp/visual_critic/city_r23/REVIEW.md). Readability rose a point because the 320 px zones now read, but craft and cohesion lost a point each: the amber faces read as solid orange and the pink-lilac towers stand out. Both are already in ART CALL 23.
- ART CALL 24 (added to round 24):
  - feather the amber edge into the violet core (1-2 lots of grading, with a few violet and cyan windows);
  - about 15 % of faces in the dark right core show dim windows, so it reads as an unlit city and not a void;
  - the highway light streams stay brighter than the amber facades at 320 px.
- Round 24 accepted in part. The pink-lilac towers are fixed: they came from the grade's world-fixed hero glow (g1_hero), not from a light, and they read clean in the hotspot close-up. Perf is 11.70 ms.
  - **Amber district:** the plate lower-left crop pair shows the amber is still off. r24's windows are big orange dots with bloom halos (polka dots), on near-black bodies. The plate's lower left has MEDIUM blue-violet bodies with lit roof outlines, tiny and dim window points, and warmth that sits mostly at STREET level, pooling between the blocks.
  - **Structure:** coarse structure fell to 0.135.
- ART CALL 25 (round 25). The amber district is the third round on this one zone, so if r25 does not land it goes to the designer as a pick rather than a fourth guess.
  - **Bodies:** lift the district's bodies to the plate's medium blue-violet.
  - **Windows:** windows become tiny dim points with no bloom halo, either kept below the bloom threshold or with lower gain and a higher count.
  - **Warmth at street level:** warmth comes from street-level light pooling between the blocks and the warm base glow on the lowest floors. Placement logic: lit streets light the bottoms of the buildings.
  - **Structure:** comes back through the contrast between bodies and street gaps, not through window brightness.
  - **Highway streams:** about 1.4x, so they are the brightest lines at 320 px.
- Round 25 reviewed side by side with the plate's lower-left crop. Option C (committed) is the closest so far at plan scale: medium violet blocks, dim window points and warm light between the blocks. It is accepted as the working base. Two problems remain:
  1. The warm pools are round discs in the zoom-3 close-up, while the plate's warmth runs as LINES along the streets.
  2. The warm zone disappears at 320 px, and coarse structure stays at 0.135.
  The plate's own 320 px lower left is subtler than r23's solid orange, so C may be the more faithful of the two. The numbers alone don't settle it (A-020).
- **DESIGNER PICK PENDING (amber district):** r25/amber_options.jpg, A (white points) / B (amber points) / C (lifted bodies with street warmth, the working base), or back to r23's solid-orange zone, which squints stronger but drifts from the plate. Work goes on with C until the designer picks.
- ART CALL 26: stop iterating the amber zone until the pick. In round 26 the warm pools become strips along the streets, not discs. A fresh critic runs on r25 first, so its top fixes fold into r26 instead of costing a round.
- Critic on r25: 30/50 (review: D:/rc_tmp/visual_critic/city_r25/REVIEW.md). Craft and cohesion each gained a point and readability lost one: the core is a flat, speckled violet mass, and its roofs are brighter than its faces, the reverse of the plate.
- ART CALL 27 (round 26). Critic fixes taken:
  1. **Warm strips:** warm pools become continuous dim-amber strips along the streets. Full strength in the amber district. City-wide they run at no more than 20 %, with random intensity per segment, never in open areas, on highways or on the river. This is capped low because the designer has twice rejected visible grids of street light.
  2. **Roofs:** darken the core roofs one stop and halve the white roof tiles, so faces read brighter than roofs, as on the plate.
  3. **Low-rise breaks:** 3-4 breaks at about 35 % height along the diagonal highway and beside the hotspot tower, ONLY if the heights are art-side (shape kit). If they come from plan data, it goes to build through the mailbox.
  4. **Lit share:** the lit window share varies per building (25-60 %), with dark facets.
  The bay haze and far-shore lights (critic #5) are declined: the bay was reverted to r6 at the designer's request and gets no new content without them.
- Round 26 accepted. The warm strips read as lit streets, not a grid, and the audit is clean. The core faces are now brighter than the roofs, and the lit share varies. Coarse structure is 0.137 and perf 12.31 ms, with a thin margin.
  - The low-rise breaks need layout heights, so they went to build as a general rule for every seed in A-107.
  - Against the plate crop, the plate's lower-left streets are brighter warm lines than ours. That gap stays, because the designer ruled the grid dim and rejected light grids twice.
- ART CALL 28: the overnight loop stops at r26. The remaining gap to the plate is bounded by designer rulings and pending items:
  - the dim street grid;
  - the amber district pick;
  - layout heights (A-107);
  - the rail route (A-106).
  More rounds would only oscillate, as r21-r25 did on the amber zone, and the perf margin is thin. Next comes the designer's review: the amber pick, then whether the street grid may brighten toward the plate in the amber district only.

## 2026-10-29 · Designer review of r26 (red-box screenshots) · DESIGNER RULINGS
1. **Highway interchange by the bay:** its deck overhangs. The highway stops where the interchange arcs start.
2. **Traffic:** traffic is individual thin red and white streaks, like very fast cars moving along the roadways, and gets animated later in the "living city" pass. Road and highway surfaces are plain road colour. No blotchy red/white rectangles: only the light lines carry the traffic colour.
3. **Signs:** no fully white buildings. A sign is never full building height, it has real colour, and its light spreads onto the neighbouring buildings.
4. **Breaks:** no random breaks in roads or highways (the city highway curve, the low areas near the river).
5. **Open areas by the river:** the empty no-building areas near the river are filled with buildings or parks.
6. **Parks split by streets:** where park lies on both sides of a road, the road is removed so the park reads as one, and the strip is filled with foliage.
7. **Park ground:** the ground under parks is green, or tinted green.
8. **Bay roads:** roads that run into the bay or along its coast are removed.
9. **City colour (the original idea, restored):**
   - Each building's lights take a CORPORATION colour.
   - The choice is uniformly random, except that near a corp's HQ that corp's colour becomes denser.
   - Each building's concrete takes a slight tint toward its light colour.
   - The neon outlines come back: vertical neon on some building edges and along the roof tops.
   - The overall city is too dark and uniform, and the look has strayed far from the original idea.
10. **Amber rule abandoned:** the "amber district" (ART CALL 20 onward) is dropped, along with the art-district profiles that stood in for corp colour. The city is coloured per corporation and is generally random. In this Solace case study more buildings are Solace-coloured, but not all: the weight rises with proximity to a corp's HQ and never reaches 100 %.
- Art-pass note: the overnight loop chased the plate's warm lower-left and the critic's squint metric, and drifted from the corp-colour concept. The corp rule above now outranks the plate's local colour and the structure metric. The pending amber pick (A/B/C) is void.

## 2026-10-29 · Designer: the city returns to the round-6 look · DESIGNER RULING
- Sheet: `tide_raid/G1_parity/r26/city_soul_then_vs_now.jpg`. The designer: "round 6 and 40 are roughly the same, only round 40 view is darkened to accent the raid placement lines … city should look like round 6." Remake the current city (the A2 planner layout, tide raid Godot view) with round 6's building look (`round6_city_restyle/views/restyle_night_crop.png`).
- Round 6's traits:
  - **Buildings:** Cv2 faceted low-poly buildings with tone jitter per facet.
  - **Toon and ink:** 3 hard toon bands, wobbly ink outlines from id, normal and depth edges.
  - **Shapes:** varied forms (hex, octagon, wedge, stepped, tapered).
  - **Colour:** muted, corp-tinted concrete in mauve, teal and slate, with small square windows in the corp colour.
  - **Neon:** neon roof-top outlines and vertical edge strips in the corp colour, plus antenna beacons with diamond tips.
  - **Streets:** coloured glowing avenues.
  - **Spill:** light spills onto walls and streets.
- **Traffic and highways:** they follow round 26 city motion (`round26_city_motion/storyboard_ambient_v2.png`, `interchanges_v2.png`):
  - elevated decks, each with a highway colour rail;
  - dense head and tail streak traffic, two-way on highways and one-way on ramps and loops;
  - upper decks hide the traffic beneath;
  - glow only on the top deck.
- This matches the standing rule that the city map keeps cel + ink at raid zoom (2026-10-20, ART_BIBLE 1.2); the realism (AAA-2) look applies only where 1.2 names it. Round 27's corp colour system (HQ proximity, 0.65 cap) and its geometry fixes carry over. The round-6 look supersedes the dim-street-grid and lamp work where they conflict. A/B check: the round-6 coloured avenues versus a dimmer street level.
- Round 28 (round-6 look, first pass) reviewed against `restyle_night_crop.png`.
  - **Matches round 6:** toon bands, wobbly ink, corp neon rims, mast diamonds and tone jitter. They came from the old raid post, which the realism grade had been hiding.
  - **Fails:**
    - **Colour:** grey-green and murky.
    - **Ground:** grey ground, grey-black parks and a grey bay.
    - **Avenues:** pale pastel blocks with gaps instead of glowing rivers of light.
    - **Ink:** too heavy, and rough on tall towers.
- ART CALL 29 (round 29), so the designer isn't shown a known miss:
  - navy-black ground, a dark green lawn and a navy bay;
  - continuous saturated glowing avenues joined through intersections;
  - a saturating grade with mid-value saturated building families;
  - stronger toon contrast and thinner ink;
  - crisp small windows;
  - mast tips that keep their hue;
  - hex and octagon prisms;
  - top-deck traffic occlusion;
  - no lilac haze on open ground.
- Round 29 reviewed: the clear step toward round 6. It has navy-black ground, saturated mid-value families tinted per corp, separate toon bands, thinner ink, hex and octagon prisms and a dark green lawn. It is shown to the designer as the checkpoint.
  - **Known gaps against round 6:**
    - **Avenues:** they read as dashed flat yellow and cyan slabs, not continuous glowing neon lines with a halo.
    - **Massing:** the core is a forest of thin, even-height towers, where round 6 has chunkier mixed low and mid massing. Heights are layout (A-107).
    - **Bay:** it reads as a flat royal-blue plane on seed 3.
    - **Traffic:** no top-deck occlusion yet.
    - **Haze:** a pink fringe remains on the west edge of seed 3.
- **Designer on r29 (2026-10-29):** "Buildings are looking good (colors and all)." The navy ground shifts to a dark brown. Otherwise keep going.
- ART CALL 30 (round 30):
  - streets, lots and land go dark brown; the lawn stays dark green and the bay stays water;
  - avenues become continuous glowing neon lines with a halo, not dashed slabs;
  - the bay stops reading as a flat royal-blue plane;
  - upper decks hide the traffic below them, with glow only on the top deck;
  - remove the pink fringe on seed 3.
  The buildings are locked as they are.
- Round 30 accepted. The dark umber ground reads well under the locked buildings, the sea plane's royal blue and the seed-3 pink fringe are gone (both were the outer land plane), and upper decks now hide the traffic beneath. Perf is 9.43 ms.
- ART CALL 31 (round 31, avenues only): the avenues are still the gap to round 6, for three reasons:
  - **Too pale:** the cores tone-map to near white, so they read pastel white-yellow and white-cyan. Round 6's are wide saturated bands of green, cyan, violet, amber and magenta-free hues.
  - **Too thin:** at plan zoom they almost vanish.
  - **Broken:** they break wherever a lot has fewer than two buildings beside it.
  - **Fix:** wider bands in saturated hues, with the core gain capped so the hue survives the tone map. Each avenue stays continuous along its whole street line and stops only at a real open-ground run of 2 or more lots, the river or a highway zone.
  The buildings and the ground stay locked.
- **Designer on r30 ground (2026-10-29):** "the brown is maybe a bit too brown, maybe push toward gray/green." The bay water stays blue: under the bay, the ground colour transitions to blue so the transparent water shows blue, the way the river does. Both are added to round 31.
- Round 31: the avenues are accepted. They are wide, saturated and continuous, in green, cyan, violet and amber, and at last read as round 6. Perf is 8.94 ms.
  - **Not met, ground:** the multiplier is grey-green, but in the avenue close-up the ground between the avenues still reads mauve-maroon, so some other ground layer (lot ground, a grade cast or the haze) keeps the old hue.
  - **Not met, bay:** the bay and seed 3's open sea still read as a flat dark grey-violet plane, not blue like the river.
- ART CALL 32 (round 32): find and fix the two ground and water layers by bisection, as a pixel probe per layer:
  - the ground reads dark grey-green everywhere;
  - the whole bay and the open sea read blue like the river.
  Everything else stays locked.
- Round 32: the ground is accepted. The root cause was that wet_street never took ground_mul, and the ground now reads dark grey-green, apart from the additive avenue halos, which are fine. The bay is not met, and it got worse: the top-left of the plan and seed 3's open sea now read as an olive grey-green expanse. The agent called it OuterLand terrain, but it is where r22 and earlier showed navy sea, and the bay close-up shows shore islands of buildings in it. I read it as the translucent sea showing the newly grey-green land beneath.
- ART CALL 33 (round 33): stop tinting the land under the water. The bay and sea water carry their own colour: the river's blue family, at enough opacity that whatever lies beneath can't recolour it. If that expanse really is land, it gets the treatment of real land: dark grey-green with sparse features, or a coast. Either way, settle it from the plan's water mask, not from heights, and show a mask overlay.
- Round 33: the plan's water mask shows only river cells inside the city rect. The top-left expanse is the OuterLand terrain outside the city rect. That mesh is tagged with the water class, and the realism grade used to paint it as deep sea, so the designer has always seen it as the bay.
- ART CALL 34 (round 34): the designer's words decide it ("make sure the bay water stays blue … transition the ground color there to a blue so the transparency shows water as blue"). The OuterLand expanse beyond the city's shore renders as BAY WATER in the river's blue family, a little deeper, with the shoreline highlight where it meets city land. That matches the water-class tag and the A2 city map, where the city sits on a peninsula in the bay. A note goes to build so the plan can mark it as water if gameplay ever needs it. City ground stays grey-green.
- Round 34 accepted. The OuterLand expanse renders as opaque deep-blue bay water in the river's family, the city ground stays grey-green, and perf is 9.23 ms.
  - **Open, small:** the bay meets the city rect's grey apron band with a hard edge, with no shoreline highlight yet; that needs the coast contour. A few structures sit in the bay: shore building clusters, three cubes and road stubs. The roads are with build (A-108).
  - **Next:** a checkpoint with the designer.
- **Designer on r34 (2026-10-29):** the r33 and r34 changes are agreed.
  1. The area under the highway near the bay shows as water, but it is still land, so it renders as land.
  2. The pink-topped walls (A2Features/Walls) are changed:
     - the one cutting north-south through the city gets the same highway treatment as the other highways (deck, colour rails, streak traffic);
     - the one around the HQ is removed.
- ART CALL 35 (round 35): these changes are view-side only. Build gets a note that the wall routes now draw as a highway or not at all, in case gameplay reads them.
- Round 35 accepted.
  - **Land and water:** the strip under the bay highway is land. Blue now appears only on the plan river and its banks, the south sea and the bay.
  - **North-south route:** the core's wall route draws as an elevated highway with rails, streaks and pylons, at its own lift. It has no interchange where it meets the other highways.
  - **HQ ring:** gone. The park edge reads as tree line and lawn.
  - **Perf:** 10.52 ms.
  - **Generalised beyond the frame:** every non-Solace wall route (Halcyon, Orbital, Meridian, Aurelian, Tethys) now draws as a highway, and Solace's draws nothing. Flagged for the designer, because Meridian's HQ is a walled container yard by its landmark rule (ART_BIBLE §2.4). If that yard wall is one of these routes, it should probably stay a wall.
- **Designer on r35 (2026-10-29):** "the colored streets show cuts in them, likely from clipping into some terrain. need to fix so it is cohesive."
- ART CALL 36 (round 36):
  - every avenue-strip cut is mapped by cause;
  - the strips follow the terrain height with a constant offset, and a depth bias keeps the ground from clipping them;
  - single-lot stops in the middle of an avenue are bridged;
  - the shoreline highlight goes in if there is time.
- **City generation evaluation (designer ask, 2026-10-29):** `tide_raid/city_gen_eval/CITY_GEN_EVAL.md`. Verdict: the A2 macro plan is sound, but below it the layout layers are never cross-checked, and the view hides the collisions.
  - **Recommendation:** option (b), a headless CityLint over 25 seeds, plus targeted layout rules. No rewrite.
  - **Build:** the layout asks went as A-110.
  - **Art, after r36:** derive decks from one road source, assert that the view hides nothing once the corridors land, and end avenues and traffic at real intersections and roads.
- **Designer, 2026-10-29: "do your recommended action for the procedural generation finds."** Build hasn't answered since B-081, so art acts within its own lane and leaves the layout untouched:
  1. **CityLint prototype:** pure, read-only, on art/city-lint in worktree D:/rc_art/godot_lint, swept over 25 seeds. It measures the defects and produces coordinates for build, and goes to build as a proposal for A-110 item 1.
  2. **View-side fixes, round 37 (queued after r36):**
     - one road-geometry source, with ramps built from the plan's own interchanges;
     - a no-hide assertion that reports the skip lists;
     - avenue and traffic end rules.
  The layout rules themselves stay with build (A-110).
- **DESIGNER RULING (2026-10-29): art-pass may change the city layout code.** "There is no build session active … I think you are free to make changes as needed." Art-pass now owns the layout-realism work (A-104 to A-110): the builder, raster, plan, terrain, features and plan data.
  - **Where:** in art clones and branches only, never in D:/Godot/rebel_cell main. Merging to main waits for the designer.
  - **Rules for every change:**
    - deterministic core;
    - a test for every rule;
    - the CityLint sweep before and after;
    - the full test suite before any branch is called done.
  - **Order:**
    1. Lint (in progress).
    2. P0 layout rules: corridors, streets kept off water and parks, dead ends and connectivity.
    3. P1: the height field, waterfront band, river infill, street hierarchy and a single road source.
    4. Retire the view skip lists.
- Rounds 36 and 37 accepted.
  - **r36:** the avenue cuts are fixed. Each strip piece now sits at the highest ground under it plus a small lift, and gaps shorter than 3 lots are bridged, so the bands read continuous.
  - **r37:** the strips start and end at intersections with buildings on both sides, ground cars run only on connected streets, and ramps land only on road lots: plan interchange ramps (17 of 84 accepted) plus filtered invented ramps.
  - **No-hide test:** a test now reports the view skip lists (wall skip 9 and 7, pockets 5), and they can only shrink once the layout corridors land.
  - **Perf:** 10.38 ms.
  - **Open:**
    - at some crossings two hues overlap where they meet;
    - sky lanes still follow the avenues;
    - no shoreline highlight;
    - the decks are not yet snapped to the raster centre line.
  - **Next:** the city view waits for the layout branch (art/city-layout-p0), then renders it.
- **City layout P0 landed:** CityLint is on art/city-lint (78fbe945, 19 rules), and the P0 layout rules are on art/city-layout-p0 (6ea2d710). Totals over 25 seeds:
  - **Down to 0:** streets touching sea, streets in parks, dead ends and disconnected street components. Buildings in rail, highway, ramp and wall corridors also went to 0, from 13,011.
  - **Small side effects:**
    - bare lots in the dense zone +2 %, as deck and shore lots become park strips;
    - buildings without street frontage +7 %;
    - lots with a park street on both sides rose from 760 to 1,037.
  - **Sites:** the site-on-road check was mis-specified, so it was re-specified. 773 Sites remain, and none were moved.
  - **Full suite:** 4,050 tests, 5 failing. They fail in vfx_tiers, s_mapview, art5_city_integration, visual_lint_static (tide_fx) and no_bare_id_sort (tide_fx, look_parity). The P0 diff touches none of those files. Pre-existing, but still to fix before any merge.
- ART CALL 37: round 38 merges city-layout-p0 into the r37 view, renders the fixed layout and checks the no-hide baselines drop. P1 runs in parallel on art/city-layout-p1:
  - street hierarchy and block merge;
  - the height field and step-downs;
  - the waterfront band;
  - ramp ends;
  - retiring the skip lists.
- Round 38 accepted. The P0 layout merged into the view cleanly: streets stay out of parks, and the north park now reads as one park.
  - **Wall-clash skip rose** to 11 and 12 lots, all in the west corner, where the wall corridor doesn't seem to cover the route. Sent to P1.
  - **Floating holo cubes** over the core: they must anchor to a host building.
  - **North park:** a featureless tree mass, which needs paths, clearings and lawn under the deck.
  - **Bay apron:** bare, with lone buildings. This is P1's waterfront band.
- ART CALL 38 (round 39, view only):
  - anchor the holos;
  - dress the north park like the Solace district;
  - one rule for avenue crossings;
  - the shoreline highlight;
  - sky lanes avoid the bay and bare lots.
- Round 39 accepted.
  - **Park:** the north park now has clearings, winding paths, ponds and lawn under the deck.
  - **Avenues:** where two avenues cross, the brighter one wins, so the colours no longer overlap.
  - **Shore and sky:** a bank highlight runs along the bay apron, and sky lanes split at street gaps.
  - **Perf:** 10.04 ms.
  - **Holo ads:** they now sit on the roof (gap 0.6 BU), but by design they still read as floating pale cubes at plan zoom.
  - **Bare lots:** the big grey bare lots (bay apron, north of the core, beside the Solace park) are layout, and P1 handles them.
- ART CALL 39: the holo cubes are off in the city view (`neon_holo_share` 0) until a proper holo design exists. They read as floating boxes, and the designer's sign rule (coloured, partial height, spilling light) is already met by the screens and blades. This goes into the round that merges P1.
- **Designer, 2026-10-29 evening: "progress without my input."** Overnight plan:
  1. Finish P1.
  2. Round 40 merges P1 into the view, turns the holos off, and renders.
  3. A fresh visual critic runs on r40 against the round-6 target, and only clear fixes follow.
  4. Stage a PROPOSED final in `G1_parity/final_proposed/`, with the golden-plate updates staged beside it and the hand-off notes drafted.
  Nothing replaces final/, the golden plates or main without the designer's review (standing rule). Every call gets logged as an ART CALL.
- **Designer, 2026-10-29:** "if you reach the end of this current phase and its before 8am tomorrow, please proceed to the Cohesion phase without asking for any input from me."
  - **What this allows:** once the city phase is staged (final_proposed, staged plates and the hand-off draft), art-pass starts roadmap step 2, the cohesion pass, before 08:00 on 2026-10-30.
  - **Scope:** the slice sheet of every Solace state against the new city, the redo list, and a dimmed raid-mode grade.
  - **Out of scope:** the netrun-look decision stays with the designer, and nothing replaces final/ or the golden plates.
- **City layout P1 landed** (8a817aad on art/city-layout-p1). Totals over 25 seeds, P0 → P1:
  - no_frontage 28,628 → 2,651
  - height_cliff 1,498 → 92
  - bare_in_dense 7,502 → 0
  - singleton 136 → 13
  - park_street_both_sides 1,037 → 396
  - ramp ends off land 182 → 0
  - low_rise_share in its band on every seed
  - the wall skip is empty on seeds 1 and 3
- **Checks:**
  - Full suite: 4,064 tests, with the same 5 failing that already failed before this work (s_mapview, vfx_tiers, art5_city_integration, visual_lint_static, no_bare_id_sort).
  - Schema smoke passes. The two hung runs came from a parse error in the agent's own edit, which is fixed.
  - Building counts fell about 15 %, so three "enough buildings" test thresholds were lowered. Sites were not moved.
- ART CALL 40: the 5 failing tests are art-owned (tide_fx colours, bare sorts in tide_fx and look_parity), so art-pass fixes them now on art/city-test-fixes, before any merge.
- **Next for layout (P2):**
  - a surface-use lot kind under the decks;
  - avenues along the arterials;
  - retiring the skip lists and the Solace pockets.
- Round 40 accepted. P1 merged into the view cleanly. The holo ads are off, and the wall skip is at 0 on seeds 1 and 3. The height field reads as a dense core with lower fringes. Perf is 9.36 ms.
  - **Weakened test:** test_city_motion was weakened to "road count ≥ 0" because its model rect is now park. The test-fix agent is restoring it, since a weakened test cannot merge.
- ART CALL 41 (round 41, view plus layout under the 2026-10-29 clearance):
  - **Bay apron:** remove the lone apron towers and turn the bare grey apron into a waterfront (quay promenade with a tree line, port blocks or a linear park).
  - **Odd buildings:** bring the odd slab and the glass cluster into the height field.
  - **North park:** brighter path cores, with lamps on the park paths only.
  - **Bare lots:** fill the dark and bare lots beside the Solace park.
  - **South-west low-rise:** vary it so it matches the core's style.
  - **Plan zoom:** drop the stray guide dots.
- Round 41 accepted.
  - **Bay apron:** dressed as a quay with a tree line and warehouses.
  - **Paths and lots:** the park paths are lit, and the bare lots are now lawn.
  - **South-west:** low-rise shapes vary.
  - **Plan zoom:** the far-tier sky cars no longer show.
  - **Perf:** 9.40 ms.
  - **Left alone:** the apron tower, the slab and the glass cluster sit on Site or landmark lots, so they stay. Some grey slab remains beyond the apron band.
- ART CALL 42: the city phase closes on r41.
  1. A fresh visual critic reviews r41 against the round-6 target.
  2. All 7 beats of the tide raid sequence are re-rendered on r41 into `G1_parity/final_proposed/`, using the same side-by-side and squint format as final/.
  3. The hand-off notes are drafted.
  final/ stays untouched until the designer reviews it.
- Critic on r41: 26/50, "not ready, yes-with-fixes in about two rounds" (review: D:/rc_tmp/visual_critic/city_r41/REVIEW.md). It read only part of its inputs.
- ART CALL 43, my rulings on its list:
  - **Declined:**
    - #1, more corp colour on the core walls: the designer approved the r29 buildings "colors and all", so corp colour stays in windows, rims and neon.
    - Its call for an orange or amber core: already ruled out.
  - **Taken into round 42:**
    1. **Towers piercing the highway loop:** verify with a 3D deck-vs-building clearance audit and fix the cause, whether layout corridor or deck path.
    2. **Park artefacts:** remove the grey diamond holes, haze rectangles and stray pink patches.
    3. **Apron:** the grey slab behind the quay gets warehouse or lawn lots out to the highway zone, and the pylons stand on dressed ground.
    4. **Avenues:** they run along the arterials (P1's street hierarchy) so they read as continuous lines, not stubs.
    5. **Low-rise breaks:** biased to lots beside highways and around the hotspot tower (A-107's intent).
  - **Final render:** final_proposed is re-rendered on r42.
- **Full suite green:** art/city-test-fixes (a76b09b6, based on art/tide-r40) runs 4,069 tests with 0 failing, and schema smoke and validate_content pass.
  - **Code fixes:** rc_common includes in 7 shaders, Palette tokens in tide_fx, and explicit sort comparators.
  - **Two stale tests updated,** each citing its ruling.
  - **Weakened test restored:** test_city_motion is back, now on a densest-window helper.
  - **P1 thresholds:** the agent's own P1 threshold cuts were reverted.
  - **Merge note:** r42 must merge art/city-test-fixes before the final render.

## Round 42 review (art-pass, 2026-10-30 01:50)
- **Accepted:** art/tide-r42 bbdc20ae, which is r41 plus art/city-test-fixes.
  - Full suite: 4,070 tests, 0 failing. Schema smoke and validate_content pass.
  - Perf: GPU p95 10.15 ms, against a 12.57 ms limit.
- **Checked side by side** with r41 and with final/ (old_vs_new.jpg).
  - **Highway decks:** no towers pierce them; the deck-clearance audit finds 0 on seeds 1, 3 and the camera seed.
  - **Arterial avenues** read as continuous corridors.
  - **The pink ramp stubs** are gone.
  - **Low-rise breaks** sit along the highways.
  - **Squint:** buildings, avenues and highway loops hold. The bay is blue and the ground is grey-green.
- **Still open, carried to round 43:**
  1. A row of grey diamonds on the north park lawn. These are chunk-ground lot quads, so the fix needs a per-lot probe.
  2. A grey slab behind the quay at the top of the plan.
- **final_proposed (7 beats on r42):** the tide path reads clearly in beats 04 and 05.
  - In beats 02 and 03, the cyan forecast path competes with the cyan and green avenues.
  - This is the case for the raid-mode dimmed grade in the cohesion phase: during a raid the city must step back so the raid marks lead.
  - final_proposed waits for the designer's review. final/ is untouched.
- **ART CALL 44:** the city phase is closed apart from the two items above, which round 43 takes.
  - It is before 08:00, so the cohesion phase starts now, as the designer ruled.
  - The netrun-look decision stays with the designer.

## Cohesion review (art-pass, 2026-10-30)
- **Accepted:** `cohesion/slice_sheet.jpg`, its squint version, and COHESION_REVIEW.md. All 11 states have a frame. Four are only partial: win, lose, HQ run and the raid HUD.
- **Art-pass squint verdict:**
  - The r42 city is the outlier: the only bright, multi-hue, high-frequency frame. Every UI page still sits on the older flat violet city.
  - The bridge is a dimmed under-UI grade of r42, the same one as the raid grade in round 43. It keeps the corp colour but steps it back so the chrome leads.
  - **Loudest jumps:** the cream dossier page and E10's orange ring.
- **ART CALL 45:**
  - Redo item 1: lay the City Grid, Site dossier, route page and raid setup again over the r42 city, using the dim grade.
  - This starts now as composite concept plates, not Godot work, under the concept-vs-polish rule.
  - Items 3, 4 and 5 and both win/lose screens wait for the designer's answers in COHESION_REVIEW.md, netrun look first.

## Cohesion redo 1 review: map pages on r42 (art-pass, 2026-10-30)
- **Accepted as concept plates** (`cohesion/map_pages_r42/`, b78b7dec). Checked side by side with the old pages in contact_old_vs_new.jpg and by squint.
- **The strong under-UI grade works:**
  - values: x0.58 outside the focus area, x0.78 inside it;
  - saturation pull: 0.18 on buildings, 0.55 on neon.
  - The r42 city keeps its corp hues and its cel/ink identity, and the chrome, network, TARGET and raid routes lead.
  - The flat violet field is gone, and the pages now belong to the same world as the raid beats.
  - The grade is the reference for the Godot under-UI grade. Round 43's raid grade should land close to it.
- **Notes for the port, not blocking:**
  1. The node network is an affine diamond lattice. In Godot it must follow the real r42 road graph.
  2. The route page is a soft 2x upscale. In Godot it needs a real transit-zoom camera.
  3. Solace lime (#96FF46) and Cell lime (#D4FF00) sit close together. The colour-blind check in the polish step must cover them.
- **Designer questions** (added to COHESION_REVIEW): should the Site names and work orders still read as Meridian on a Solace slice? This is game data, so not art's call.

## Round 43 review: visuals (art-pass, 2026-10-30)
- **Visuals accepted.** Final acceptance waits on perf and the full suite.
  - Checked side by side in compare_r42_r43.jpg and raid_grade_beats.jpg, plus a squint.
- **Grey diamonds gone:** the north park lawn is continuous.
- **Deck-lot slab:** dressed as lawn. The apron and seed 3 show no regressions.
- **Raid grade:** buildings 0.62/0.72, neon 0.48/0.38, ground and water 0.86.
  - The city steps back but keeps its corp hues and its cel/ink.
  - The avenue strips stop competing.
  - **Beat 03:** the cyan reveal path reads first.
  - **Beat 04:** the pink tide path and the HOME ring lead.
  - **Beat 02:** passes, but the forecast stub is short and faint. More ribbon gain goes to the motion pass, which is the right place for it.
  - The grade sits close to the strong under-UI grade on the cohesion map pages, so the raid and map pages now match.
