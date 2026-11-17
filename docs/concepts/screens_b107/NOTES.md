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

## Answers from the vertical slice (v47 rules, 2026-11-16)
- **Heat after a lost raid:** Heat changes. Any fallen stop grades the raid "overrun", and an overrun gets the normal
  Heat vent. The amount is still being tuned. To fix: the lost result shows "Heat drops" with no value.
- **EVACUATE:** exists in v47, at stop 1 only. The player gives up the target in round 0, and every wave moves on to
  the next stop. It is not available at later stops. To fix: add an EVACUATE action to setup at stop 1.
- **Support, then defend:** allowed. An operative may support next door and later defend their own site in the same
  raid. Only supporting twice in one raid is barred: the supporter of a fallen stop does not support again.
- **Rest slots only while holding, and docked reach on hover:** look calls with no rules objection. The designer
  decides with his pick.

## Answers from build (port, 2026-11-16)
- **HQ armory stock:** since v44, every station sells its own city armory. HQ has 3 weapons and 2 devices, with the
  same rolls and prices as the raid Armory but its own stock per station, rerolled after each raid. The weapons
  screen should show it as "HQ stock".
- **MAINFRAME:** only inside Rebel Cell territory, never on a Solace street.
- **The route runs through the underground tiers too.** Rooms sit on the frontage or underground: basement, subway,
  utility, plaza.
- **Heat after a lost raid:** build said "unchanged". The vertical slice, which owns the rule, says the overrun Heat
  vent applies. Art follows the vertical slice: "Heat drops".
- **Recruit cost and the SCHEM currency:** build will answer from the port's data.

---

## Plates added 2026-11-17

Drawn by `scripts/reward_loss.py` (`python scripts/reward_loss.py [a b c d_mid d_final loss stop]`) and, for the mark, `scripts/raid_world.py marks`. Same kit, 1920 x 1080, PIL only. `sheet.jpg` has a new row for them.

### Netrun room reward (vertical slice v49-1): `netrun_reward_a.png` to `netrun_reward_d_final.png`

All five share one frame:

- the netrun street (`transitions/v6/plates/netrun_street_won.png`) dimmed to about 44 % and softened;
- the run HUD: runner, run health, credits (`unbanked` amber / `BANKED` lime), Heat;
- a crumb: site, tier, node, layer;
- the result sticker;
- lime terminal glass panels (T4 W5);
- the DECK pile bottom left, with a pencil arrow from the hovered card ("+1 = n");
- CONTINUE (Space).

Cards are netrun deck cards in this set's vinyl: RAM disc, name, type-colour art field with a glyph, type band (HACK pink, SYSTEM cyan, GUARD green, POWER gold with a gold keyline), effect text, rarity pips. Implants are die-cut chip tiles with the slices they fit.

Shared states:

- **hover / selected:** the card lifts about 22 px, sits straight and gets a lime glow and keyline;
- **picked:** it flies to the deck (T4 W6);
- **SKIP:** keeps the deck as it is;
- the card pick and the implant pick are separate, and each can be skipped.

| Plate | Node | On it |
|---|---|---|
| `netrun_reward_a.png` | ROUTER win | ROUTER CLEARED; card pick 1 of 3 (Static Shock, Tailspin, Sanitize) or SKIP. **Over the asset cap** (amber panel): a 12-segment wheel ring with segments held up to the cap in lime and above it in amber. Here 3 above give "+6 cr, 2 cr each, max 6" and the tag "unbanked until a rack". When nothing is over the cap the panel is hidden. A pencil note says what a ROUTER never pays: no flat credits, no run health, no Heat. |
| `netrun_reward_b.png` | ELITE win | ELITE DOWN plus a HEAT +1 sticker (36 > 37). A richer card pick 1 of 3 (Leech Worm, the POWER card Backdoor, Cold Snap). IMPLANT pick 1 of 2 (Overvolt, Siphon selected), with its own SKIP. |
| `netrun_reward_c.png` | TERMINAL (no fight) | The DISPATCH line, then CHOOSE ONE of three glass panels: (1) the implant shown (Tracer); (2) upgrade the 2 listed cards (Static Shock > Static Shock+ 4 > 6, Firewall > Firewall+ 6 > 9), drawn hovered with lime glass; (3) heal 5 run health (31 > 36, capped at the max). TAKE IT confirms. |
| `netrun_reward_d_mid.png` | SERVER RACK, mid (layer 4) | RACK TAKEN; the ELITE rewards (card pick with a POWER card, Root Kit, and implant pick 1 of 2); a BANKED stamp with the banked amounts, "credits and raid assets safe"; HEAL 6 (24 > 30). The HUD credits read BANKED. |
| `netrun_reward_d_final.png` | SERVER RACK, final (layer 7) | SITE CLAIMED; HEAT +8 ("+3 more on a tier 3 site"); card pick 1 of 3; implant pick 1 of 2; BANKED. A paper variant note: the first tier 3 site's pick is 3 POWER cards (three minis); a tier 3 site may offer a UNIQUE card (a mini with a UNIQUE sticker). |

Not drawn, by rule: MAINFRAME is a shop, not a reward. BLOCK SERVER is HQ-only.

Card and implant text is the real `content/cards` and `content/firmware` text. The four POWER cards (Backdoor, Root Kit, Dead Man Switch, Mirror Shard) are art placeholders, because no POWER card exists in content yet.

### Campaign loss: `loss_printout.png`

- **T11 dossier, slot B composition:** the manila folder on the dimmed, teal-tinted raid city.
- **Left page:**
  - the T11 survey photo, every node crossed (cropped from `solace_endscreens/v2/lose_B.png`), taped;
  - FILED stamp;
  - SAMPLE LOG: the crew; lost runners struck through, DECEASED run n;
  - a post-it.
- **Right page:** the Solace memorandum:
  - TO / FROM / RE;
  - **CAMPAIGN SUMMARY:** days active, sites claimed, sites lost, runners lost, raids held, raids lost, final Heat, HQ integrity 0 / 20; losses in red;
  - the Heat line;
  - the **TARGET ACQUIRED** corp ink stamp (the same stamp as `raid_f_result_lost.png`);
  - "no appeal is offered", the signature.
- **Footer:** MAIN MENU and NEW CAMPAIGN.
- **Variant panel, right:** a runner lost on a netrun (the T4 L5 trace printout, not the campaign end).
  - **RUNNER LOST** shows:
    - the runner FLATLINED, gone for good;
    - lost with the runner: the deck (19 cards), unbanked credits, unbanked raid assets;
    - HEAT +12 +2 (tier 2) = +14;
    - "banked credits and assets: safe at HQ";
    - TRACE BURNED;
    - GRID VIEW.
  - **SAFETY NET USED / RUNNER EXTRACTED:**
    - the runner lives (back to HQ);
    - deck kept;
    - unbanked credits and raid assets lost;
    - the same Heat;
    - safety net 1 > 0 left;
    - same GRID VIEW footer.

### Stop banner: `stop_banner.png`

The raid stop banner at 1:1, drawn by `raid_world.stop_banner` where it lives (top centre on the city) and cropped. Each state is labelled with the plates it appears on:

| State | Banner | Seen on |
|---|---|---|
| STOP REACHED | `STOP 1/3 [D4] > A3 > HQ` | raid_a, b, c |
| HELD | `[D4 lime] > A3 > HQ` | raid_f_result_held |
| FELL | `STOP 2/3 [D4 struck] > [A3] > HQ` | raid_d |
| HQ STOP | `STOP 3/3 [D4 struck] > [A3 struck] > [HQ]` | raid_e |

It also shows the chip legend (cur / next / end / fell / held).

### Raid mark: REPLACE SUPPORT (raid rule v50), on `raid/raid_marks.png`

The rule: a defender's full-strength weapon may dock on a slot held by a supporter's weapon, and the supporter's weapon pops back to its owner. The new tile (bottom right) shows two states at 1:1 on slot c3, which is one of NYX's supporter slots and also one of MAKO's slots at D4:

- **HELD + HOVER:**
  - MAKO's RAIL is held (lifted);
  - the slot is lit amber with an ink edge;
  - the slot reads **REPLACE SUPPORT** (amber chip);
  - the hover pencil ring;
  - a dashed amber pop-back preview arrow from NYX's docked SMG to NYX's post.
  - While a defender weapon is held, every supporter-held slot it may take reads REPLACE SUPPORT. The ring and the preview arrow are the hover only.
- **DROPPED:**
  - the RAIL is docked;
  - NYX's SMG flies back along a solid amber arrow to NYX's post ("to NYX");
  - NYX's tether is gone.

The other marks are unchanged. To fit the tile, the two rows of tiles moved up (10 and 26 px) and the bottom band was compacted: the stop banner now sits under the HQ tape, and REFUSALS sits under the devices.

### Calls made for these plates (open questions for the designer)

1. **Implants = the firmware pool.** v49-1 says "implants". The plates use the firmware names and text under the label IMPLANT, with "fits ATK . CRIT" from the firmware's allowed slices.
2. **POWER cards:** no POWER card exists in content. The names and effects drawn are placeholders.
3. **"Held segments above the asset cap"** is read as wheel segments held at the fight's end, against a per-fight cap: 12/12 held, cap 9. What is the cap, and is it per runner or per site?
4. **Mid SERVER RACK Heat:** "ELITE rewards" is read as the rewards only, so no Heat +1 sticker is drawn on the mid rack. Does the rack's elite fight add Heat?
5. **TERMINAL:** no SKIP or leave is drawn. Can the player take nothing?
6. **SAFETY NET:** drawn as a one-time save: the runner and deck survive; unbanked credits and raid assets are still lost; the Heat still applies. Is that the rule, and how many nets are there?
7. **Runner-lost Heat:** drawn as "+12 +2 (tier 2) = +14" (12 + site tier).
8. **Campaign summary numbers** are sample values. "Sites lost" counts sites Solace retook.
9. **Naming:** the new plates have no raid-shop or HQ-stock text, so FIELD SUPPLY and STASH do not appear. The older raid plates (`raid_b_setup_armory.png` and the raid NOTES) still say ARMORY for the round-1 raid shop and were not renamed in this pass.
