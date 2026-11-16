# B-107 screens (DRAFT concept plates, 2026-11-16)

These are art concept plates for build's B-107 rulings (origin/port-campaign-b MAILBOX_TO_ART; DECISIONS 2026-11-16 "transitions v5 rulings").

- They are 2D (PIL) at 1920 x 1080, with no Godot or Blender.
- Every plate was read back at 1:1 and at 50 % and iterated.
- `sheet.jpg` is the contact sheet.
- The scripts are in `scripts/`, run as `python scripts/<file>.py`:
  - `raid_world.py`
  - `hq_screens.py`
  - `advance.py`
  - `blockserver_v2.py`
  - `contact_sheet.py`
- The transitions part of B-107 (T2, T4, the BLOCK SERVER v2 copy) is in `../transitions/v6/` (see its STORYBOARD).

The look is REBEL_CELL's own vocabulary, Solace only:

- die-cut vinyl stickers for the runner's things;
- corp paper and enamel for Solace;
- navy terminal glass for the system;
- wax pencil for the player's marks;
- the round 17 LOCKED glyphs, round 22 v4 unit icons and old-pass busts.

The quality bar is ref_setup, ref_shop and ref_talents; nothing was copied from them.

The crew are the in-game capture's four operatives:

| Operative | Class |
|---|---|
| MAKO | Gunner |
| URSA | Sapper |
| OZZY | Hacker |
| NYX | Fixer |

---

## 1. RAID: five moments, one design with the vertical slice's raid look brief

`raid/`. This is the art lead's re-brief: B-107's five raid screens and the vertical slice's RAID_LOOK_BRIEF (game-v2, v47) are drawn as one design.

- **One city, one camera.** Every frame is the living semi-isometric city at set 8's raid camera: the native city capture (`city_hi`), pushed bolder, on set 8's district grid.
- **Slots are computed, not hand placed.** They come from the port's v42 rule (route slots = the route cells within dockRadius of the post, one piece each; `dock_rules.slots_of`).
- **Reused set 8 pieces, read only:** threat icons v4, class beacons, gear tags, device badges and the set 8 slot tile.

The district's stops:

| Stop | Cell | Post |
|---|---|---|
| TARGET | d4 | MAKO |
| THEN | a3 | NYX, a neighbouring claimed site that helps at the target |
| END | our HQ, a6 | URSA stationed there |

OZZY is not in this raid (OFF). Lanes A (from the east, up avenue e) and B (from the north, down street c) meet at d3.

The first pass of five plates on the raid capture is kept in `raid/superseded_first_pass/` for the record.

### a. `raid_a_review_route.png`: B-107 "review the incoming raid" = brief (a)

- **Purpose:** the raid is announced. Where it hits, by which streets, and where it goes if the target falls.
- **On it:**
  - the city with the route drawn as a bold dotted line from stop to stop:
    - TARGET: corp-red crosshair ring, current;
    - THEN: white dashed ring;
    - END . HQ: the pink heart;
  - red lane tints and pencil for A and B;
  - the wave per street at each lane's entry, exact: unit icons v4 with counts;
  - the three posts (beacons);
  - pencil forecast: "falls R3", "3 walk on", "HQ safe";
  - the stop banner STOP 1/3 [D4] > [A3] > [HQ];
  - the folded intercepted Solace order (the one corp document);
  - the RAID INCOMING sticker;
  - HQ tape, Heat and credits;
  - the crew stickers, one state each: HERE / HELPS / AT HQ / OFF;
  - the forecast strip: per lane icons + counts, then FALLS R3 > A3 x3.
- **Interactions:**
  - hover a stop or a lane to pulse it;
  - click a crew sticker to see its post;
  - TO THE ARMORY (Space).
- **States:** a raid at any Heat line (25 / 50 / 75 / 100, same shape, stronger). A forecast that never reaches HQ shows "HQ safe" (no number). One that does shows "HQ -n" on the END stop.

### b. `raid_b_setup_armory.png`: B-107 "shop" + "place operatives" = brief (b)

- **Purpose:** setup at the target. Buy, dock, merge before round 1.
- **On it:**
  - the ARMORY open: lime glass with 4 weapons and 2 devices (cost dots), reroll and the bank;
  - MAKO's RAIL card held and lifted;
  - only the slots it may take now are lit (solid cyan); the others rest as faint dashed tiles;
  - NYX's SMG docked on c2, tethered to NYX's post, with the supporter share pill (pie + **N%**: the share is still moving);
  - a BARRICADE holding e5 (one piece per slot);
  - the hovered slot e4 in yellow pencil, with the rail's reach hatched on the cells it hits and "+2";
  - the scarcity counter: slot tile 2/10;
  - the forecast strip: R1, A held 0, B leaks 1, HOLDS, "with rail: B 0";
  - SEND IT.
- **Interactions:**
  - drag a weapon from a crew sticker's tag or from the Armory onto a lit slot;
  - drag back to undock;
  - a buy that matches a docked weapon merges onto it.
  - Refusals are badges, not words (set 8): taken / device here / too far.
- **States:**
  - nothing held: the rest slots only;
  - held: lit slots, radius ring only when it limits something;
  - hover: the forecast re-projects.
- **Note:** "place operatives" is the post. Operatives are fixed on their sites (v40+), so placing means docking their weapons. There is no operative drag.

### c. `raid_c_round_running.png`: B-107 "execute" = brief (c)

- **Purpose:** watch the round with the exact forecast.
- **On it:**
  - units on the lanes with HP drain and statuses (J = jammed);
  - shot tracers from the docked RAIL (e4) and SMG (c2);
  - a kill breaking into bits;
  - the barricade holding A;
  - ROUND 2/3 with a tick bar and speed buttons 1x / 2x / END;
  - the forecast strip: R2 HOLDS . kills 4/6 . R3 FALLS > A3 x3.
  - No slot marks in playback (set 8 rule).
- **Interactions:** speed, skip to the end.
- **States:** this round holds or falls. If the next round falls, the strip names the next stop and roughly how many go on.

### d. `raid_d_site_falls.png`: brief (d), the site falls and the raid moves on

- **On it:**
  - D4 struck FELL in the banner and on the map, with a D4 FELL sticker;
  - MAKO's post dimmed, an amber pencil arrow "MAKO falls back" (alive, to HQ), MAKO's sticker grey FELL BACK;
  - the three survivors on the route with "x3 carried";
  - A3's own wave not yet played, from lane C;
  - A3's slots (v42 rule at NYX's post);
  - STOP 2/3;
  - **RESUPPLY**: an amber panel, pick 1 of 2, no reroll (between rounds and stops, clearly not the Armory);
  - the forecast: A3 kills 3+3, HOLDS, HQ safe.
- **Interactions:** take one offer or skip, dock, SEND IT.

### e. `raid_e_hq_stop.png`: brief (e), the HQ stop

- **On it:**
  - both stops struck FELL;
  - URSA (stationed at HQ) the only defender, DEFENDS; the others FELL BACK or OFF, with the label "HQ crew only";
  - units at the HQ door, the HQ glowing red;
  - one **-1** sticker per unit that gets in;
  - the HQ tape 20 > 17 with three segments struck and an HQ -3 sticker;
  - the strip: HQ 3 in . 20 > 17 . kills 1.
- **States:** HQ integrity 0 ends the campaign (T11 dossier).

### Results / reward

**`raid_f_result_held.png` (HOLD):**

- D4 HELD: a big lime sticker plus a lime ring and tick on the stop;
- the rest of the route greyed ("route called off");
- +9 credits to the purse, +XP chips on MAKO and NYX (MAKO LEVEL UP), the salvage weapon kept;
- the strip: kills 8/8, leaks 0, HQ 20/20, Heat 50 > 47;
- CONTINUE.

**`raid_f_result_lost.png` (lost):**

- the result stamped **TARGET ACQUIRED** in Solace's corporate ink (double frame, mottled ink, "SOLACE BIOSYSTEMS . FIELD OPERATIONS . VERIFIED");
- the lost sites glow Solace teal on the map; D4 and A3 stickers stamped SOLACE ("retake: tier easier");
- HQ -4 (20 > 16), +7 credits from kills only, the crew alive (FELL BACK);
- CONTINUE.

### Raid mark sheet: `raid_marks.png` (brief item 2)

Each mark is shown on the street it lives on:

- slots: empty (dashed) / lit / weapon / device, plus the 2/10 counter;
- weapon reach on cells;
- post + supporter link + the share pill N%;
- route: TARGET / FELL, THEN, END;
- units v4: HP, status, wave stack, kill bits;
- HQ damage: -1 per unit in;
- verdicts HOLDS / FALLS / HELD / FELL;
- the HQ tape struck;
- the five v42 street devices as their slot badges (BARRICADE, MINE, TAR, SHOCK, GATE; no-mark = "device here");
- refusals: taken / too far;
- the stop banner.

### Readability pass / fail (the brief's 10 points, on frames a-e)

| # | Check | Result |
|---|---|---|
| 1 | Building under attack, streets in | **PASS**: TARGET ring, red lane tints + pencil, A / B entries. |
| 2 | Every socket empty / weapon / device, and only this many | **PASS on (b)**: rest, lit, docked tag, barricade tile, 2/10. **WEAK at rest**: dashed rest slots are faint at 1:1 over the street (set 8's known weak point). Hidden in playback (c) by rule. |
| 3 | Weapon reach without a panel | **PARTIAL**: the held weapon's reach is hatched on cells (b); docked weapons show reach only as shots in (c). Proposal: hovering a docked tag hatches its cells. |
| 4 | Stationed vs supporters vs not helping | **PASS**: beacons, HERE / HELPS / AT HQ / OFF / FELL BACK chips, tether + share pill. |
| 5 | Incoming wave per street, kinds and counts | **PASS**: wave stacks at each entry + the strip. |
| 6 | Forecast: hold or not, where next, roughly how many | **PASS**: HOLDS / FALLS R3 > A3 x3 on the strip, the pencil on the map. |
| 7 | Route on the city, which stop is fought, which fell | **PASS**: dotted route, TARGET / THEN / END marks, FELL strikes, STOP n/3 banner. |
| 8 | HQ at risk only when real; HQ loss impossible to miss | **PASS**: "HQ safe" until the forecast reaches HQ; in (e) -1 per unit, struck tape, HQ -3, red glow. |
| 9 | Armory vs Resupply clearly different | **PASS**: big lime ARMORY (6 offers, reroll, bank) vs small amber RESUPPLY (2 offers, no reroll). |
| 10 | No text panels, labels of 2-3 words | **PASS** after one fix: two pencil labels were 5-6 words and are now 3. One exception by design: the folded corp order (3 short lines). Captions in the bottom strip are review captions, not game UI. |

### Raid open questions for the designer

1. **Slots: v42 route slots vs the brief's "intersections".** The vertical slice confirmed v42 route slots, so this is answered and kept here only as a note. Nothing in the plates depends on a cross shape: the lanes follow the district's real streets.
2. **"Wall" device:** the brief listed it and v42 lacks it. The vertical slice says it meant the barricade family, so the plates use the v42 list exactly (barricade, mine, tar, shock fence, gate). TAR, SHOCK and GATE still have no sticker glyph (glyph review item 4), so the Armory shows BARRICADE and MINE.
3. **Supporter share value** is still moving (25 % since v45). The pill shows N%. Is a pie without a number enough in game?
4. **Heat after a lost raid:** drawn unchanged (50).
5. **Does EVACUATE exist in v47?** It is not drawn.
6. **The supporter at the target is also the THEN stop's post** (NYX). Is a site's operative allowed to help next door and then defend its own stop in the same raid? Drawn: yes.
7. **Rest-slot visibility** (set 8 question 6): show rest slots only while a card is held?
8. **Docked reach on hover** (pass/fail point 3): proposed, not drawn.

---

## 2. HQ workshop: three separate screens over the hq_idle map page

`hq_recruit.png`, `hq_weapons.png`, `hq_talents.png`.

All three share the same frame:

- the r42 hq_idle page, dimmed and blurred;
- the page's left button column kept crisp (CREW / MARKET / DEFENCE), the active door ringed lime;
- the HUD tape (HQ, credits, Heat);
- HQ / WORKSHOP with sibling tabs RECRUIT / WEAPONS / TALENTS;
- ESC.

### Recruit (`hq_recruit.png`)

- **Purpose:** hire someone who saw a raid held.
- **On it:**
  - three recruit cards (portrait bust, class badge, LV1, two rolled traits with one-line effects, starter weapon): KESTREL Gunner, VOSS Sapper (selected), LUMEN Hacker;
  - paper price tags 12 / 12 / 15 cr;
  - a manila CELL FILE for the selected recruit: traits, starter weapon stats, CAN LEARN, crew after hire 5/4 ("over the crew places: recruit cost applies");
  - HIRE 12 cr;
  - the crew strip 4/4 with a dashed slot for the new one;
  - a pencil note.
- **Interactions:** click a card to select; HIRE; ESC back to the map.
- **States:**
  - free while short of crew places, else the recruit cost;
  - can't afford: the HIRE sticker greys and the price tag gets a red pencil strike;
  - no offer: the page shows the empty board.

### Weapons (`hq_weapons.png`)

- **Purpose:** a shop plus a roster.
- **On it:**
  - family filter chips;
  - the ARMORY: 8 weapon cards (cost, stars, damage / shots / reach, keyword chips);
  - one RARE card locked ("needs 14 cr");
  - the roster glass with a row per operative: weapon slots, a locked +SLOT 30 cr, a LOCKER;
  - MAKO selected, with a pencil arrow from the Rail card to MAKO's slot and the merge line Rail ** + Rail * > *** (MAKO);
  - BUY 9 cr.
- **Interactions:** buy, drag a card to an operative's slot, drag between slots and the locker, merge on match.
- **States:** sold / locked / can't afford / slot locked / merge preview.

### Talents (`hq_talents.png`)

- **Purpose:** what the operative has, and the dossier of everything each operative could get.
- **On it:**
  - MAKO's big card;
  - MAKO HAS: HEADHUNTER and VETERAN HANDS, both OWNED;
  - LEVEL UP: PICK 1: LONG SHOT / RANGE FINDER (circled) / EXTRA MAG, with the note "with the Rail: no LONG penalty", and TAKE RANGE FINDER;
  - a manila DOSSIER with tabs MAKO / URSA / OZZY / NYX:
    - GUNNER ONLY: 2;
    - ANY CLASS: the 23 general talents with one-line effects, owned ticked, today's offers circled;
  - a post-it plan.
- **Interactions:** pick one of the three on level up; the dossier tabs switch operative (planning only).
- **States:** no pick waiting (the LEVEL UP row hidden); a pick waiting (the left card says "1 pick waiting").

### HQ open questions

1. Is the HQ armory stock the same pool as the raid Armory?
2. Recruit cost vs crew places: is it free under the cap and the recruit cost over it, as drawn?
3. The r42 map button says CREW 3/4 and SCHEM. Are schematics the currency, or credits as drawn (from the in-game captures)?

---

## 3. Advance choice (T5): `advance_choice.png`

- **Purpose:** after a netrun claims a site, move the crew up to it or hold the original.
- **On it:**
  - the hq_idle map;
  - the new site SEED VAULT EXCHANGE ringed lime with a tick, its GO sticker hovered (lime glow, "move up");
  - a STAY sticker on the original site CULTURE INTAKE ("hold the intake");
  - a pencil arrow from one to the other;
  - the site-file slot showing the taken site (TAKEN stamp, CREW HERE RIG-4, +12 SCHEM, the two choices as keys);
  - the DISPATCH line;
  - the G / S key chip.
  - JACK IN is gone after the jack-out.
- **Interactions:** click a sticker, or G / S.
- **States:** GO hovered (drawn), STAY hovered (the STAY sticker lifts instead), no choice possible (a single sticker).
- **Open question:** what does GO mean mechanically: the operative's post moves to the new site, or the run's start point?

---

## 4. BLOCK SERVER v2

`block_server_v2.png`, `block_server_v2_beaten.png`, `block_server_kit.png`; copies in `../transitions/v6/plates/`.

- **Fits its 3D building:** drawn in the v3.1 bio cutaway box at the kit's proportions (9 x 7 cells, wall 3.3, slab 0.6).
- **Scale (art's call):** 1 cell = 1 kit m = 0.5 BU, so a storey is 3.9 cells = 1.95 BU, close to floor_bu 1.9.
- **Tank:** the cap top is at 3.2, under the 3.3 wall top.
- **The v5 riser pipes are removed.** The cap pipes run sideways into a wall header.
- **More specimen detail:** spine plates, ribs, veins, gill fronds, tendrils, umbilicals into the cap, nodules, a lit core, one lit eye.
- **The kit sheet:** a plan, an elevation with the wall-top line, the specimen large, and a 12-part list in cells and BU.

**Open question:** the kit room at 0.5 BU per cell is 4.5 x 3.5 BU, but the street placeholder room is 2.6-3.2 BU wide. Which scale does the room lot use?

---

## Process

- PIL only.
- One heavy process at a time on the art side, gated by `D:/rc_scratch/b107/wait_art.sh`.
- Scratch in `D:/rc_scratch/b107`.
- Nothing written under D:/Godot/rebel_cell.
- No commits.
