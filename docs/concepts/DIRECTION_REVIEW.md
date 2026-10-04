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
