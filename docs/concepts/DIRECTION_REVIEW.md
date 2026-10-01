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

## What happens after the decisions
1. Rewrite `docs/ART_BIBLE.md` around the locked direction.
2. Write a Godot implementation plan: shaders, atlases, and the order of screens.
3. Implement on `art-pass`, screen by screen, with before/after captures.
