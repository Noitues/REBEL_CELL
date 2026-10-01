# Art direction review: everything explored so far (2026-10-01)

Status key: **LOCKED** = the designer has decided. **LEANING** = a front-runner exists but it hasn't been confirmed. **OPEN** = no decision yet. **UNEXPLORED** = no concept work done yet.

## 1. Base world style: LOCKED
- **Choice:** Cv2, gritty triangulated low-poly, with E's cel shading (toon bands and ink lines).
  - Proof: `round2/assets_compare/s1_cv2_cel`, `round2/r2_blend_EC_on_Cv2_day`.
- **Rejected:**
  - round 1 A–E (neon ink, tilt-shift diorama, riso zine, rain noir, glitch vector);
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
  - round 7 V1–V3. **V2 "living programs" was picked**, and its telemetry readout border was "great".
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
8. **Value and upgrade variation:** spec 3 versions of every slice. Also spec temporary slice-state overlays (frozen, locked, burning, empowered, …) that sit on top of a slice.
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
| NUDGE | A short ±1 two-way arc. |
| UNDOCK | A drone with an arrow, or an open ball-and-socket. |
| BREACH | Lightning over a bullseye. |
| EXHAUST | A tearing card. |
| All fire | One shared two-peak flame. |

**Upgrade tiers**
- Tier II → III needs a shape change, not only colour, so it works for colour-blind players. Round 14 is in progress.

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
- Slice upgrade tiers I–III. SliceData has no tier yet.
- Placeholder states FROZEN, LOCKED, BURNING and EMPOWERED. These are not in the game yet.
- A CLEANSE ability, now with an ESC-key glyph, and a "kill process" ability with a power-symbol glyph.
- Solace's HEAL slice reads as growth: a possible rename to GROWTH.
- A future mechanic, **gates**: rim gates that trigger when the pointer rotates through them. The card-play preview trace shows the direction and the gates passed. The art is deferred until the mechanic is designed. Round 15's `preview_A.png` has a first sketch: crossed gates light gold, uncrossed gates stay grey.
- MOMENTUM's pictogram is dynamic: the big number switches once a spin has happened. It needs runtime support.

## What happens after the decisions
1. Rewrite `docs/ART_BIBLE.md` around the locked direction.
2. Write a Godot implementation plan: shaders, atlases, and the order of screens.
3. Implement on `art-pass`, screen by screen, with before/after captures.
