# HQ redesign: design pass (M14, HQ-DESIGN)

Status: proposal for the designer. Nothing is built; no game file is changed.
Agent: HQ-DESIGN, 2026-10-05, on main @ 11edde0.

## Designer rulings 2026-10-05 (relayed by the orchestrator)
- **Direction B, "THE HAND", is chosen.**
- **Q1, yes.** The Heat gauge takes the top bar's first slot (upper left) on every screen.
- **Q3, keep the rule.** You may jack in with a raid pending; the raid fires as an interlude, as today.
- **Q4, yes.** At the HQ the wheel may zoom out past `raid_fit_max` into the GRID band (the whole city).
- **Q11, examples first.** The designer wants to see examples before deciding. They are in section 6b below.

Q2, Q5 to Q10, Q12 and Q13 are still open, with the defaults written in section 6.

## The brief (designer, 2026-10-05)
The art pass missed the HQ and it does not match the concepts, so the HQ is reworked entirely:
- fewer panels; big at-a-glance verbs and selections;
- no separate City Grid page: the HQ **is** the live 3D city at the RAID band (the view 6w built);
- Heat sits where the Heat indicator sits for the whole run, with no WANTED poster or Heat panel at the HQ;
- JACK IN starts a netrun the same way every netrun starts.

Parity entries HQ-01..10 are superseded by this pass. The S-GRID-HUD slice (GRID-04, 05, 07..11) waits for it.
GRID-01..03, 06, 12 and 13 (bloom, marker size, label collisions, framing) still apply to the map layer under
every direction.

## How the images were made
- **The city is real.** Every image sits on one windowed capture session of main's `CityView3D`. It was one
  launch of `tools/city/city_lab.tscn` through `run_windowed.py`, at 1920x1080, quality tier 2, **RAID band**
  (log: `band=1`). The capture is the Meridian district with the lab's sample network decal: an 8-node ring
  whose links are the city's real network decal. Meridian's HQ (The Master Manifest) is on the right.
- **The kit is real.** The stickers, CRT terminal panels and chips, decrypted holo, corp paper, rubber stamps
  and grease pencil all come from the v2 kit's own drawing code. That is round 33 `ui31.py` /
  `sticker_lib31.py` on tag `art-concepts-r43`, imported unchanged; only the font paths are re-pointed, as
  `tools/art/bake_menus_r33.py` does. Site markers v4, raid sockets, the Ghost beacon, the v2 busts and
  photo prints are main's own PNGs (`assets/city/grid_markers`, `assets/raid/sockets`, `assets/raid/beacons`,
  `assets/portraits`).
- **Composited, not rendered.** The markers and sockets are placed by hand on the ring's nodes. The lab draws
  no uplink pads. The network is a sample, not a campaign. Read the images as layout and language studies on
  the real city, not as screenshots.
- Script: `tools/art_pipeline/hq_redesign/compose_hq_concepts.py` (usage in its header).

**The moment shown in every image:** Meridian, ICE 5, Heat 58 (FLAGGED), raid ROUTE AUDIT pending (Heat 50
crossed, entry A at LOSE THE TRACKING). Crew: CELL-9 (Breaker R2), NOVA (Ghost R1, posted on the Safehouse),
RIG-4 (Rigger R0), and HEX (Botnet, flatlined). The selected Site is DRONE CHARGING YARD (T1), next to the
Cell's Safehouse. Names, prices and rules come from content and the GDD.

## Files
| File | What it shows |
|---|---|
| `direction_A.png` | A: the concept's Grid HUD becomes the HQ |
| `direction_B.png` | B: the crew is a hand of cards (the raid setup's layout) |
| `direction_B_market.jpg` | B with the hand on MARKET (recruits as HIRE cards, boosts, unlocks) |
| `direction_B_defence.jpg` | B with the hand on DEFENCE: the raid setup in place on the same page |
| `direction_B_text20.jpg` | B at text scale 2.0 |
| `direction_C.png` | C: the verb bar (RUN / CREW / MARKET / DEFEND) with one panel at a time |
| `direction_C_tabs.jpg` | C: all four tabs |
| `heat_indicator.jpg` | Common to every direction: the HEAT tag in a run and at the HQ (same pixels), and the Heat terminal it opens at the HQ (Scrub Heat) |
| `jack_in_flow.jpg` / `.gif` | Common: select, runner, JACK IN, then the 4.6 jack along the link on this same city |
| `ref_parity_hq_today.jpg` | Today, from the parity audit (art-pass build vs main) |

---

## 1. Inventory: everything the HQ does today
Sources: `scripts/ui/hq_scene.gd` (`show_hq`, `show_grid`, `_site_card`, `show_raid`, `cell_badges`,
`_refresh_status`), `scripts/ui/kit/hud_bar.gd`, `pause_menu.gd`, `RunManager`, `CampaignRules`.
**Rule** means the GDD requires it, and every direction keeps it. **Pres.** means presentation, free to move
or merge.

| # | Function | Where it is today | GDD | Kind | Where it goes (A / B / C) |
|---|---|---|---|---|---|
| 1 | **Start a netrun**: a Site plus an operative. Refusals: not reachable, Rank too low for the tier, dead, run already under way | HQ JACK IN stamp opens the Grid page; the Site card holds the operative dropdown and JACK IN; a crew chip can be dragged onto JACK IN | 1.3, 4.1, 5.3; `CampaignRules.launch_error` | Rule | Select a Site on the map, pick the runner, press the one JACK IN sticker; the 4.6 jack plays along the link on this city (`RunManager.jack_link` already reads the map on screen) |
| 2 | Run kinds: netrun, patrol (cleared or claimed Site), reclaim (TAKEN Site), breach (Central Server, at least 3 Exploits) | Site card and run rows | 3.3, 4.2, 11.7 | Rule | The same select-then-JACK IN path. The holo names the kind; a refusal shows the rules' own words |
| 3 | Resume a run that was saved and left | HQ JACK IN goes back into it (`go_to_netrun` with no link: the old CRT push) | ANIM-R1 M1 | Pres. (one run at a time is a rule) | JACK IN again, with the same link jack from that run's Site; the deck-CRT push goes |
| 4 | Site facts and **IF CLEARED** (Exploit, Heat change, raid it brings, Schematics, Sites it opens, claimable) | Site card badges; run rows | 4.1, 7.1; preview equals result (CLAUDE rule 6) | Rule (numbers) / Pres. (form) | The selected Site's holo (corp intel), with the IF CLEARED chips inside it |
| 5 | Step through Sites: PREV / NEXT, RUNS OPEN NOW, map click and hover | Grid side column | 9.5 (full keyboard), pad reach | Pres. | Map cursor (stick / D-pad steps Sites), Q / E; name chips on the selectable Sites only |
| 6 | **Claim** a cleared Site: pick a node type (locked types shown) and pay | Site card | 3.1, 3.2, 3.4 (unlock gating), 11.4 | Rule | Select the Site: the card offers node tiles with prices; the sticker slot reads CLAIM (Q18) |
| 7 | **Repair** a DOWN node (50% of install) | Site card | 3.3 | Rule | Select the node: REPAIR chip with its price (sticker slot, Q18) |
| 8 | **Upgrade** a node (30 then 60) | Site card | 11.4 | Rule | Select the node: UPGRADE chip with its price |
| 9 | **Patch home** (1 Schematic a point) | CYBERDECK menu | 3.3 | Rule | Select CORE: PATCH chip with its price |
| 10 | **Station / recall** an operative on a Safehouse slot | Dossier buttons; drag a dossier onto the mini-map | 5.4 | Rule | A: crew row to Safehouse. B: drag the crew card onto the Safehouse (the raid's pencil drag). C: CREW tab. Recall: a chip on a posted operative |
| 11 | **Recruit** a rookie (15) | Black Market; drag onto the roster | 5.4, 11.4 | Rule | A: MARKET tab. B: MARKET hand (HIRE cards, the bible 4.12 recruit state). C: MARKET tab |
| 12 | **Next-run boosts** (10, 15, 20) and the queued kit | Black Market | 11.4 | Rule | As 11; the queued boosts show on the runner (card / row) |
| 13 | **Profile unlocks** paid from campaign Schematics | Black Market | 3.4 | Rule | As 11 (a PROFILE group) |
| 14 | **Scrub Heat** -5 (25, +10 each) | CYBERDECK menu | 11.4, 11.5 | Rule | The HEAT tag opens the Heat terminal with SCRUB HEAT (`heat_indicator.jpg`) |
| 15 | Heat value, band, rules in force, next threshold | WANTED poster, CELL STATUS badges, top-bar HEAT, `heat_tip` | 4.3, 9.4 | Rule (must be readable) / Pres. | The run-wide HEAT tag (number, band word, five-band strip) and the terminal it opens. The poster and badges go. The world keeps 5e's Heat rig |
| 16 | Cell status: home, Exploits, Sites, Armory n/6 and contents | CELL STATUS badges, top bar | 7.3, 11.7 | Pres. | Top bar (HOME, EXPLOITS); Armory in the DEFENCE hand / tab and the raid setup; Sites are on the map |
| 17 | Crew dossiers: portrait, class, rank, HP, deck, Daemons, flatlined; select an operative; VIEW LOADOUT; DAEMONS | CREW // ROSTER, top bar | 5.1 to 5.3, 6 | Pres. (state shown) | A: crew rows. B: crew cards. C: CREW tab. VIEW LOADOUT and DAEMONS stay in the top bar for the selected runner |
| 18 | **Rank 3 Inner Ring segment swaps** | OptionButtons on the dossier | 6.4 | Rule | Into the Loadout's SPINNER tab (the ring is drawn there) |
| 19 | **Pending raid**: RAID PENDING, then the raid setup (place / move assets, forecast, START DEFENSE, Speed / Skip, report). Undefended, the raid becomes an interlude in the next run | CYBERDECK row, Grid nav, `show_raid` (already on this city, RAID band) | 4.4, 7.1 to 7.3 | Rule | A: the RAID PENDING strip plus RAID SETUP. B: the work-order paper plus the DEFENCE hand. C: the DEFEND tab. In B and C the setup runs **in place**: same page, same camera |
| 20 | Map: markers v4, links, locked links, threat routes, TARGET plus edge arrow, minimap, key, SHOW ALL, pan and zoom | Grid page (GRID band) and HQ mini-map | 4.1, 9.3 | Pres. (on rule data) | One map at the RAID band (Q4, Q5). The key becomes a one-line strip (round 37). The minimap is optional at RAID zoom |
| 21 | Pirate radio (DJ line); share code in its tooltip | HQ right column | 8 (flavour) | Pres. | Q7: an ON AIR ticker line in the prompt row. The share code is already in the pause menu |
| 22 | Story so far (revealed beats) | HQ window | 8.4 | Content must stay reachable | Q8: a STORY section in the Codex, plus a toast when a beat is revealed |
| 23 | Codex, Settings, Save | CYBERDECK menu (all also in the pause menu; the game autosaves after every action) | none | Pres. | The pause menu (Menu / Esc) only |
| 24 | Drag and drop (ANIM-4): crew to post, recruit to crew, boost to kit, crew chip to JACK IN | HQ and Grid | STYLE 5.4 | Pres. (motion entries kept, binding) | Re-pointed onto the new targets; no motion entry dropped |
| 25 | Refusal and news toasts; SAVED stamp | page foot | STYLE 4.13 | Pres. | Unchanged |
| 26 | The Central Server breach and HQ run (8w compound, gate) | launched from its Site | 11.7 | Rule | Unchanged: selected and jacked into like any Site |

Nothing in the table disappears. Items 21 to 23 move; they are not deleted.

---

## 2. Common to every direction

**HEAT, one indicator for the whole game** (`heat_indicator.jpg`).
- The top bar's first slot is always the HEAT gauge at the same pixels: bare-Anton number in the band colour,
  the band word printed (never colour alone), and the five-band strip with the 25 / 50 / 75 ticks and a marker.
- At the HQ the tag carries a caret and is a button (pad: View). It opens the Heat terminal: rules in force,
  next threshold, sinks, and **SCRUB HEAT -5 · pay 25**.
- The WANTED poster, the CELL STATUS badges and the Heat band banner on the poster go. The poster's Heat
  count-up and band-crossing motion move onto the tag; the motion entries stay (binding ruling).
- To keep one spot on every screen, the screen titles leave the bar for yellow title stickers (v2 rule:
  titles are stickers). This touches every screen, so it is Q1.

**The map is the raid map.**
- `WireframeBackground.use_city3d(true, RAID)`; 6w's view cover; 5e's GridCityLife (Heat rig, the Cell's
  fist, landmark).
- The Cell's nodes are their raid sockets on uplink pads, with stationed class beacons.
- Corporate Sites are markers v4 (pad, disc, ring, pips): orange ring = run now, white = not yet,
  lime = yours.
- TARGET is the red pencil circle with the `CENTRAL SERVER // name   EXPLOITS n/3` chip.
- A pending raid's routes are red dashed pencil (what-if) until the setup opens, then solid.
- A selected Site gets a yellow pencil circle, and the link the jack will ride is dashed yellow.
- The camera fit (`RaidZoomFit`) frames the network plus the launchable Sites (Q5).

**JACK IN = every netrun start** (`jack_in_flow.jpg` / `.gif`).
- Select a Site, the runner is preselected, press the pink JACK IN sticker.
- `RunManager.launch` then `go_to_netrun(site)` then `Fx.jack_in_link`: the 4.6 sequence
  (`jack --from RETURNS_PROC --to DRONE_YARD`, rain on the link only, CRT collapse, wheel slap, lens).
- The page JACK IN used to open, and the deck-monitor CRT push, both go: there is no "HQ jack" any more.
  Resuming a saved run plays the same jack from that run's Site.

**One sticker verb.** The pink sticker slot (bottom right, where START DEFENSE sits in the raid setup)
always holds the selected thing's verb:
- JACK IN for a runnable Site;
- CLAIM, REPAIR or UPGRADE for a node (Q18);
- START DEFENSE during the setup.

Everything else is a terminal chip. Corporate Sites read as **holo** (decrypted intel); the Cell's own nodes
read as **CRT terminal**; the raid's work order is **paper**. All three follow bible 1.2.

---

## 3. The directions

### Direction A: "THE GRID", the concept's HUD made the HQ (`direction_A.png`)
**Idea.** Round 32's `city_map_hud.png` is the HQ, nearly as drawn. A persistent left column holds CREW and
MARKET as tabs, with a one-line map key. On the right sit the selected Site's holo (IF CLEARED inside it),
the RUNNER line and JACK IN. A bottom-centre RAID PENDING strip carries RAID SETUP.

**Layout at 1280x720** (the image is 1920x1080, scale 2/3):
- top bar 0..57;
- THE GRID title sticker at the top left;
- left column 13..280 x 125..580 (CREW / MARKET tabs, four crew rows, RECRUIT and LOADOUT chips, the key
  strip, < PREV / NEXT >);
- holo 968..1267 x 467..600, RUNNER line 608..641, JACK IN at 1144, 679;
- RAID PENDING 301..787 x 635..709;
- the map's free part is about 300..960 x 60..630.

**Reach (mouse / pad):**
- Run: click a Site, then JACK IN (2 clicks). Pad: stick or D-pad steps Sites, A selects, LB / RB changes
  the runner, X is JACK IN.
- Station: drag a crew row onto the Safehouse, or select the row and then the node (STATION chip).
- Market: click the MARKET tab (pad LT / RT).
- Raid: click RAID SETUP (R): the panels swap, the city stays.
- Heat and scrub: the HEAT tag (View).
- Claim, repair, upgrade, patch: select the node, then its chip or sticker.
- Loadout and Daemons: top bar.
- Pause, Codex and Options: Menu / Esc.

**At text 2.0:**
- The left column widens (~520 px at 1080) and the crew rows take two lines.
- The market tab scrolls (FitScroll), and the holo puts TYPE and REWARDS in its tooltip.
- The key folds (MapLegend.FOLD_SCALE). PREV / NEXT shrink to `<` `>`. The top-bar tags drop their captions.
- The map's free part shrinks to about 40% of the screen. This is the same squeeze main's HQ has today: A
  has the most panels of the three.

**Reuses:**
- 4C: CrtWindow, MenuChip, CrtTiles tabs, VerbSticker JACK IN, title sticker;
- 5e / 5d: markers, legend strip, CityGridControls, minimap if kept;
- 6w: the RAID band city, RaidZoomFit, raid setup unchanged;
- 7w: RouteNodePanel's holo pattern for the Site card;
- CrewCard and PortraitBust;
- ANIM-4 DropLayer.

**New:** crew rows (a compact CrewCard), the MARKET tab list (grouped, headed, with icons and prices), the
Site holo with the IF CLEARED chips, the RUNNER line, the RAID PENDING strip.

**Panels on screen:** 6 (top bar, title, left column, holo, runner line, raid strip). Today: 15 over two pages.

**Rough cost:** about 7 agent slices. Common work is about 5: fold the Grid page into the HQ on the RAID
band, the HEAT tag and Scrub drop-down, JACK IN unification, cleanup of poster / radio / story / status, and
porting ~32 test files that call `show_hq` / `show_grid`. A's own panels are about 2.

### Direction B: "THE HAND", the crew are cards and the HQ is the raid setup's twin (`direction_B*.{png,jpg}`)
**Idea.** The HQ uses the raid setup's own layout (round 40 `raid_view_v3`, as 6w built it). Along the foot
is a hand of cards. At the bottom right is the one pink sticker. A paper work order sits at the top left while
a raid is pending. A holo / terminal card sits at the right. The **hand has three decks** behind three
terminal tabs:
- **CREW**: your operatives as cards, using the v2 corp photo print, name plate, class, rank, HP and a status
  chip (READY / ON <SITE> / FLATLINED).
- **MARKET**: HIRE cards for recruits, boost stickers with gold price tags, unlock chips.
- **DEFENCE**: the Armory's defence cards. This is the raid setup in place: routes go solid, START DEFENSE
  takes the sticker slot, and Speed / Skip sits under it.

Picking a runner lifts its card (the raid's "parked" card) and draws the yellow pencil arrow to the
selected Site, which is the drag model the raid already uses. The HQ and the raid setup become one screen
with a different hand.

**Layout at 1280x720:**
- top bar 0..57;
- work order (paper) 17..245 x 75..235 with RAID SETUP under it, only while a raid is pending;
- hand tabs 16..143 x 571..693;
- hand 190..900 x 560..720 (cards 113x150, about four visible);
- holo 968..1267 x 467..600;
- JACK IN at 1144, 660 with the `> jack --from .. --to ..` system word under it (bible 1.3: word over a
  system word);
- the map's free part is about 260..960 x 60..560. The fit frames above the hand, as 6w's fit does above the
  card row.

**Reach:**
- Run: click a Site, then JACK IN. The runner is the lifted card; click another card to change it, or drag a
  card onto the Site.
- Pad: D-pad up / down moves between map and hand, left / right inside each; A picks or selects; X is JACK IN;
  LB / RB switches CREW / MARKET / DEFENCE.
- Station: drag a card onto the Safehouse (yellow pencil arrow; red circle and X with the rules' refusal),
  or pick the card and then the node (STATION chip). Recall: a chip on a posted card.
- Market: the MARKET tab; buy by click or drag (ANIM-4's flights land in the hand).
- Raid: RAID SETUP or the DEFENCE tab, in place.
- Heat, node verbs, Loadout and pause: as A.

**At text 2.0** (`direction_B_text20.jpg`):
- Words grow; drawn objects stop at x1.3 (STYLE 5.6), so the cards stay card-sized and the hand shows the
  runner, one more, and "+N more".
- The holo keeps the name and the IF CLEARED chips (two rows).
- The work order keeps its title rows. The top bar shows icons and numbers, and HEAT keeps its full gauge.
- The map keeps more room than A because there is no side column.

**Reuses:**
- 6w / 3A: layout grammar, AssetCard, RaidDragPencil, RaidPaper work order, START DEFENSE, RaidSpeedStrip,
  raid setup logic (`show_raid`, merged in place);
- ANIM-4 DropLayer (crew to post and crew to Site already exist);
- PortraitBust prints;
- 4C stickers and chrome;
- 5e markers;
- the 7w holo pattern.

**New:** the crew card face (photo print on a Cell card), the HIRE card, the hand tabs, the contextual sticker
slot, the boost stickers (baked from the kit's `ui31.sticker`, like 4C's title words), and merging the raid
setup into the HQ page.

**Panels on screen:** 3 (top bar, holo, hand), plus the work order while a raid is pending.

**Rough cost:** about 8.5 slices (common ~5, B's own ~3.5; the raid-setup merge is the big one).

### Direction C: "THE VERB BAR", four verbs, one panel at a time (`direction_C*.{png,jpg}`)
**Idea.** The city fills the screen. A bottom bar of four big terminal verbs (**1 RUN · 2 CREW · 3 MARKET ·
4 DEFEND**, LB / RB) picks what you are doing. Only that verb's panel shows, at the left. The map's
emphasis follows the verb:
- RUN: the selectable Sites are lit and named; the panel is the Site holo plus WHO RUNS IT portraits.
- CREW: your nodes stay lit and the rest dims; the panel is the roster, and stations and recalls go on the
  lit nodes.
- MARKET: the city dims; the panel is the grouped Black Market.
- DEFEND: the raid setup in place (paper, defence cards, START DEFENSE).

The sticker slot follows the verb (JACK IN / START DEFENSE).

**Layout at 1280x720:**
- top bar 0..57;
- one panel 13..312 x 75..450;
- verb bar 313..920 x 660..704 with LB / RB;
- JACK IN at 1144, 657;
- the map's free part is about 320..1267 x 60..650, the largest of the three.

**Reach:**
- Run: RUN tab (the default), click a Site, then JACK IN.
- Pad: LB / RB moves through the verbs; the D-pad moves in the panel and on the map; A selects; X is the verb.
- Station: CREW tab, select a row, then the lit Safehouse.
- Market: MARKET tab.
- Raid: DEFEND tab.
- Heat, node verbs, Loadout and pause: as A.

**At text 2.0:** one panel at a time, so the panel can widen to about 600 px at 1080 with no other panel to
squeeze. The verb bar keeps the numbers and words (subtitles in the tooltip). This is the strongest of the
three at big text and on a pad.

**Reuses:** 4C CrtTiles / MenuChip for the bar, CrtWindow, the market and crew panels from A, raid setup
in place as in B, and the 5e markers with a per-mode dim (CityMapOverlay `Look` already has ISOLATE).

**New:** the verb bar and mode state, the per-mode map emphasis, and the four panels.

**Panels on screen:** 3 (top bar, one panel, verb bar).

**Rough cost:** about 8 slices (common ~5, C's own ~3).

---

## 4. Comparison
| | A: THE GRID | B: THE HAND | C: VERB BAR |
|---|---|---|---|
| Panels always on screen | 6 | 3 (+ raid paper) | 3 |
| Jack in, mouse | 2 clicks | 2 clicks (or one drag + 1) | 2 clicks (RUN is default) |
| Jack in, pad | stick to Site, A, X | stick to Site, A, X | stick to Site, A, X |
| Station / recall | drag row / chip | drag card (raid pencil) / chip | CREW tab, then node |
| Black Market | tab in the left column | MARKET hand | MARKET tab |
| Raid setup | separate mode (button) on the same city | **same page**, DEFENCE hand | **same page**, DEFEND tab |
| Selection reads at a glance | crew row highlight plus pencil circle | **lifted card plus pencil arrow plus circle** | portrait frame plus pencil circle |
| Map room at 1.0 | smallest | medium (above the hand) | largest |
| Text 2.0 | weakest (3 panels squeeze) | good (objects cap at x1.3) | **best** (one panel) |
| Closest to a locked concept | **round 32 Grid HUD** | **round 40 raid view** | none (new) |
| Shares with the raid setup | the city | **city, layout, cards, drag, sticker slot** | city, setup in place |
| Learning curve | lowest (everything visible) | low (raid-like) | a mode to learn |
| Rough cost (slices) | ~7 | ~8.5 | ~8 |

## 5. Recommendation: B, "THE HAND"
B answers each point of the brief:
- **Fewest panels.** Only the hand and the selected Site's card stay up, plus the paper while a raid waits.
- **Biggest selections.** The picked runner is a lifted card with a yellow pencil arrow to a pencil-circled
  Site, and the one sticker says what will happen. The CITY carries the rest (orange ring = run now).
- **The Grid page and the raid view stop being separate places.** The HQ and the raid setup become the same
  screen: the same camera, card row, drag model and sticker slot. Only the deck in the hand changes.
  That is the most literal reading of "the city raid view is the HQ".
- It gives the crew the big v2 portraits the art pass made (busts / prints), instead of 64 px chips.

C is the best fallback, and the right call if the pad and text 2.0 matter most. Its verb bar can be added to
B later (B's hand tabs already are the CREW / MARKET / DEFENCE verbs). A is the safest and closest to the
round 32 concept, but it keeps the most panels, which the brief asks to cut.

**If B is chosen, the build order** (one slice each, each with its tests):
1. HQ on the city at the RAID band, with the Grid page folded in (markers, fit, selection, pencil, holo).
2. The HEAT tag plus the Heat terminal (Scrub Heat); titles off the top bar (Q1).
3. JACK IN unification (launch and resume on the link jack).
4. The crew hand (cards, pick / lift / arrow, station drag).
5. The MARKET hand.
6. The raid setup merged in place (the DEFENCE hand).
7. Cleanup (poster, radio, story into the Codex, CELL STATUS) and test porting. About 32 test files call
   `show_hq` / `show_grid`: behaviour tests are ported and look tests are adapted, each one listed.

---

## 6. Questions for the designer
Anything that would change a rule, or that touches every screen, is listed here instead of being designed in.
- **Q1. HEAT on every screen.** Should the HEAT gauge take the top bar's first slot on every screen (route,
  fight, shop, HQ), with the screen titles moving out of the bar to yellow title stickers? Default: yes.
- **Q2. HEAT tag as a button.** At the HQ the tag opens the Heat terminal with Scrub Heat. In a run, should it
  open the same terminal read-only, or do nothing? Default: read-only.
- **Q3. Pending raid and JACK IN** (rule). Today you may jack in with a raid pending; the raid then fires as
  an interlude in the run (`NetrunSession`). Keep that, or require the defence first? Default: keep (no rule
  change); JACK IN's system word says `raid incoming mid-run` while one waits.
- **Q4. Zooming out to the GRID band.** The HQ holds the RAID band. Should the wheel be able to zoom out past
  `raid_fit_max` (640) into the GRID band (solid buildings, the whole city), or is the route's GRID VIEW the
  only whole-city view? Default: clamp at the raid range; the minimap shows the rest.
- **Q5. What the camera fits.** The raid fit frames owned nodes plus entry Sites. The HQ must also fit the
  launchable Sites, and late in a campaign that may pass 640. Default: fit network plus launchable Sites up to
  the clamp; the Central Server is shown by its edge arrow when it is outside.
- **Q6. Name of the page.** A shows THE GRID; B and C show no title. Internal names follow display names (the
  binding ruling). If the HQ's player-facing name changes, `hq` / `hq_scene` would be renamed too, which is
  a large churn. Default: no title sticker and the internal name kept.
- **Q7. Pirate radio.** Default: one ON AIR ticker line in the prompt row (4C's `on_air_ticker`), not a panel.
- **Q8. Story so far.** Default: a STORY section in the Codex, plus a corp-news toast when a beat is revealed.
- **Q9. The Save button.** Default: drop it. The game autosaves after every action, and the pause menu keeps
  Save & quit.
- **Q10. Bible 4.3 vs the brief.** Bible 4.3 puts the Grid's / netrun's Heat number on the operative
  dossier stamp (`HEAT 52: FLAGGED`). The brief puts it in the run-wide indicator. Should the route dossier
  keep its Heat stamp (parity ROUTE-02 overlaps it)? Default: drop the stamp; the tag is the one place.
- **Q11. Context stickers.** One sticker at a time: when a node is selected, the slot reads CLAIM / REPAIR /
  UPGRADE / PATCH (baked with the kit's sticker code, as 4C did for words the concept never drew) instead of
  a terminal chip. OK? Default: yes for CLAIM and REPAIR, chips for UPGRADE and PATCH.
- **Q12. Hand order.** Crew cards in roster order, the flatlined ones last, and an ineligible card greyed
  with the rules' reason (`RANK 1 NEEDED for T2`). OK?
- **Q13. Segment swaps.** Rank 3 Inner Ring swaps move into the Loadout's SPINNER tab. OK?

## 6b. Q11 examples: node verbs as stickers or as chips
The designer asked to see these before ruling. Every image is direction B's page over the same real
RAID-band capture, with a fresh `city_lab` launch for the same frame.

How the stickers were made:
- Each word (CLAIM, REPAIR, UPGRADE, PATCH) is baked by the kit's own sticker code: round 33
  `ui31.sticker` plus `focus_sticker`, with JACK IN's size and fill. That is how 4C baked the title words the
  concept never drew; nothing is hand-drawn.
- The price is never on the sticker, because bible 1.2 says values that change are not stickers. It sits in a
  gold terminal tag under the sticker.
- The node card is the Cell's own CRT terminal (cyan), not holo, because these are the Cell's systems. Cards
  sit clear of the TARGET pencil.

| File | Shows |
|---|---|
| `q11_a_claim.png` | A cleared Site, PARCEL SORTING HALL, is selected; the card sits at the left. The card lists the node tiles with their prices (FIREWALL RELAY picked, COMPILER RACK locked behind its unlock) and a PATROL IT INSTEAD chip. The verb slot reads **CLAIM**, with **30 SCHEMATICS** under it. |
| `q11_b_repair.png` | CUSTOMS PRE-CLEARANCE is a DOWN Firewall Relay: the white bolt over a greyed socket. It sits on the raid's route A. The verb slot reads **REPAIR**, with **15 SCHEMATICS** under it (50% of the 30 install). |
| `q11_c_upgrade_patch_chips_vs_stickers.png` | Side by side. Top: the Safehouse's **UPGRADE** (30 Schematics) as a terminal chip on its node card (the verb slot is empty), then the same as the sticker. Bottom: CORE's **PATCH** (+6 to 50/50, 6 Schematics) as a chip, then as the sticker. |

What I see in them:
- CLAIM and REPAIR read best as stickers. They are the one thing to do with that node, and REPAIR before a
  raid is urgent.
- As chips, UPGRADE and PATCH leave the verb slot empty, so the page has no "do this" at all.
- As stickers they turn a small top-up (PATCH +6) into the screen's loudest object.

My default is unchanged: stickers for CLAIM and REPAIR, chips for UPGRADE and PATCH. "Always a sticker" is
the other consistent choice, so the slot is never empty.

## 7. Not in this pass
No game code, scenes, content or shaders changed. This pass also does not cover the bible 4.14 "HQ actions"
row or Appendix B #10 ("HQ actions without an HQ room"); this proposal answers them, but the bible and GDD
text change only after the designer rules. When a direction is picked, its DECISIONS entry records the ruling
and the GDD 1.3 line "HQ: recruit, station, spend Schematics, pick a Site and an operative", which stays true
under all three.
