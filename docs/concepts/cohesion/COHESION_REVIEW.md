# Solace slice: cohesion review (art-pass, 2026-10-30)

Sheet: `slice_sheet.jpg` (18 cells, 3 columns, new city first). Squint (1/16 scale, blurred): `slice_sheet_squint.jpg`.
Reference: approved round-6-look city on r42, `tide_raid/G1_parity/r42/plan_r42.png`.
Checked against ART_BIBLE 1.2 (media jobs), 2.4 (corp colours) and the pink rule (3.22, DIRECTION_REVIEW 2026-10-28 E9: pink for unit screens only, darkened).
Newer DIRECTION_REVIEW rulings win over the bible. All images were looked at side by side; verdicts are not from file names.

## 1. Frame per state (latest found)

| # | State | Frame used | Status |
|---|---|---|---|
| 0 | New city (reference) | `tide_raid/G1_parity/r42/plan_r42.png` | CURRENT, accepted r42 |
| 1 | Campaign City Grid | `round44_undesigned/A_map/hq_idle.png` | OLD CITY (round 38-40 violet unified city, Meridian data); UI target still valid |
| 2 | Site dossier (holo Site file) | `round44_undesigned/A_map/hq_node_selected.png` (Site file also in `hq_idle.png`) | OLD CITY, UI valid |
| 3 | Netrun route, street | `golden_plates/street_decision.png`; page `round44_undesigned/A_map/route_page.png` | AAA-2 plate; the look is the open designer decision |
| 4 | Terminal event card | `solace_vertical/nodes/godot/frames/now_event.png` (Godot, Solace lime); concept `round31_reward_event/event_screen_memo.png` | Current for Solace, but a build frame |
| 5 | Combat, Shifting Waves | `D:/rc_tmp/combat_critic/plates/waves_e10/p1_decide.png` (+p2, p2b, p3) | Latest plates (E10). No DIRECTION_REVIEW verdict on E10 yet. Backdrop is the old violet Meridian city |
| 6 | Rewards | `round32_shop_reward/reward_screen_v2.png` | Round 32, old backdrop |
| 7 | Shop | `round33_shop/shop_v3_layout.png` | Round 33 |
| 8 | Deck screen | `round44_undesigned/B_menus/deck_viewer.png` | Round 44 |
| 9 | Raid setup | `round44_undesigned/A_map/raid_setup.png` (old city, Meridian) | OLD CITY; new-city raid grade not made yet |
| 10 | Raid defense | `tide_raid/G1_parity/final_proposed/` beats 02-07 (right half of the side-by-sides) | CURRENT city (r42), world only, no HUD layer; awaits designer review |
| 11 | Heat strip | `round44_undesigned/A_map/topbar_by_page.png` | Round 44 |
| 12 | HQ boss run | `solace_vertical/hq/H_decision_v5.png` (also `golden_plates/hq_solace_*`) | Approved plate (lime helix, plinth); no HQ-run UI layer on it |
| 13 | Campaign win | `round21_raid_world/campaign_dossier.png` | Halcyon dossier, not Solace |
| 14 | Campaign lose | `round20_raid_world/campaign_lost.png` | Halcyon "PROCESSED", not Solace |
| 15 | DISPATCH briefing / dialogue | `round31_reward_event/dialogue_B.png` | Round 31 concept |
| 16 | DISPATCH view / busts | `corp_themes/stills/rebel_cell/B05_briefing.png`, `round39_portraits/portraits_classes_v2.png` | Current set |

**Count:** 11 requested states; all 11 have a frame; 0 outright MISSING.
Partial: campaign win and lose (both Halcyon, not Solace), HQ boss run (world plate only, no UI), raid defense (world only, no HUD).
Not found anywhere: any game screen drawn on the new city. Every UI screen sits on the older violet city.

## 2. What the squint shows
- The new city is the only bright, saturated, multi-hue frame: navy-blue sea, grey-green ground, lime park, cyan and green avenues, magenta-violet towers.
- The map pages (cells 1, 2, 3b, 9) sit on a near-uniform desaturated violet slab. Beside the new city they read as a different game: no blue sea, no lime park, different ground.
- Combat, rewards and shop share one dim violet-gold backdrop. The steps in brightness are fine; the hue matches neither city.
- The HQ plate (12) is the darkest and greenest frame, and the only one with strong Solace lime.
- Hot-pink stickers (BUY, CONTINUE, UPGRADE, JACK IN, NEW CAMPAIGN) are the loudest marks on every non-combat screen. SEND IT in combat is yellow, as ruled.

## 3. Checks by state
Key: C corp colour, P pink rule, U UI chrome, V value and contrast, M medium.

### 0 New city
Reference. Lime park and helix are Solace; district hues are per-corp tints. No pink in gardens (round 9 ruling) holds. Bay blue, ground grey-green.

### 1 City Grid
- C: Solace hue is absent. The page is Meridian (orange Site file and markers); lime fists are the Cell. The lime district and park never appear.
- P: the JACK IN sticker is hot pink. The 2026-10-28 ruling covers combat unit screens only; this is a conflict to rule on (question 3).
- U: HUD strip, corp-paper dossier, polaroids and orange holo follow 1.2. Good.
- V: the map is darkened to x0.68-0.86 as intended, but the underlying city is clearly less saturated than r42. Saturation drops from the city reference to this page.
- M: old city has solid shaded prisms; r42 has flat toon bands and thin ink. Different building look.

### 2 Site dossier
- U: holo Site file (corp tint, DECRYPTED stamp) follows 1.2; frame and type match the HUD. Good.
- C: orange is Meridian. A Solace version (lime #96FF46 holo, about 78 %) is not shown. Check that it does not collide with the Cell's own lime on the map (fists, firmware).
- V: same background issue as 1.

### 3 Netrun route (street) and route page
- M: the street plate is AAA-2 (PBR, volumetric fog, wet ground). A realistic render beside the cel-and-ink city. This is the open designer decision; not decided here.
- C: magenta and violet facades dominate; nothing reads as Solace (no lime, no cell/helix kit).
- P: heavy magenta/pink in the plate; the Bloom variant (`solace_vertical/bloom/A3d_street_close.png`) adds pink veins. Bloom pink is Solace's secondary (bible 2.4) but breaks the strict pink rule; needs a ruling.
- V: the street is darker and more contrasty than the city, the largest medium and value jump between map and run.
- Route page (3b): old city behind; chrome (Terminal, corp paper, red pencil TARGET) is consistent with the HUD.

### 4 Terminal event card
- C: lime frame, "Solace Biosystems" and a CAM feed of the helix district. Good Solace read.
- U: Terminal glass, Anton choice stickers and a yellow pencil note are the right media. The concept memo (paper next to the terminal) is consistent.
- P: the concept memo CONTINUE is hot pink; the Godot frame has none.
- V: dark green on dark green, the lowest-contrast screen on the sheet. Works, but flatter than its neighbours.
- M: the CAM feed is cel and ink world; correct.

### 5 Combat, Shifting Waves (E10)
- C: Cell cyan and yellow, wave orange. Solace hue appears nowhere; the backdrop is the violet Meridian city.
- P: unit screens graded to mauve with red chevrons; CELL-9 sticker and frame cyan, SEND IT yellow, lane pale blue. Passes the E9 ruling.
- U: ring board, strips, stickers and cards match the other screens. The board is busy (E10 caveat 3); the squint still holds the main ring and the orange ring.
- V: the orange ring and strip are the most saturated mass of any screen, brighter than the map pages.
- M: backdrop is the old low-poly night. Beside r42 it looks older and less saturated.

### 6 Rewards, 7 Shop, 8 Deck
- C: Rewards use Cell cyan and lime; card bodies are pink for HACK (unit or card identity, acceptable). Shop is a violet pegboard with pink tags (neutral).
- P: pink is everywhere (BUY, CONTINUE, card bodies). The rule covers unit screens only, so these are open (question 3).
- U: stickers, terminal panels, kraft tags and paper are the correct media. The deck viewer frame is pink-edged; bible 1.2 says a CRT terminal has a cyan edge.
- V: the deck sheet is a large white rectangle, one of the brightest areas on the sheet.
- M: backdrops are the old low-poly night.

### 9 Raid setup, 10 Raid defense
- C: tide beats show the Solace helix and park well; setup is Meridian orange.
- P: forecast and impact beams in beats 04-05 are magenta/pink. r42 notes that in beats 02-03 the cyan forecast competes with the cyan and green avenues, which is the reason for the dimmed raid grade.
- U: setup has the right parts (work order, THREAT INTEL holo, START DEFENSE sticker). The tide beats carry no HUD, so chrome cannot be judged.
- V: the new city in raid mode is at full brightness; the old raid page dims the city. The raid grade (roadmap section 2) is still to do.
- M: both cel and ink; consistent once graded.

### 11 Heat strip
- U: all-terminal resource bar, Anton numbers, same from page to page. Consistent.
- C: the amber and orange Heat gradient is near Halcyon amber #FFAA28; low risk.

### 12 HQ boss run
- C: lime helix, green lit rings, dark navy night. The clearest Solace identity on the sheet; the lime is stronger than the park in r42.
- U: no HQ-run UI on the plate (node rings, MECHANIC terminal, title sticker), so it cannot be checked.
- V: darker and greener than the map; the step down is acceptable for a run.
- M: AAA-2 render (designer exception 2026-10-14), a realistic render beside the cel map. Part of the open netrun and HQ look question.

### 13 Win, 14 Lose
- C: both Halcyon (violet, amber), not Solace.
- P: the dossier's pink post-it is corp paper (not under the pink rule). NEW CAMPAIGN and MAIN MENU stickers are pink and yellow.
- U: cork, paper and polaroids (corp paper medium) and a CRT lock (terminal) are correct.
- V: the dossier is the brightest frame on the sheet (cream page); it jumps from the dark map with no step.
- M: the polaroids show the old violet city.

### 15 DISPATCH briefing, 16 busts
- C: DISPATCH red and Cell cyan frames are right.
- P: pink appears only as a visor hue; fine.
- U: terminal feed and sticker replies; the violet JACK IN reply is off the yellow family (small).
- V: heavily blurred dark city behind; consistent with other pages.
- M: low-poly toon busts, correct for the World medium.

## 4. Cross-state findings
1. One city is missing: the new r42 city has not been put behind any UI page.
2. Solace hue lives only in the park and helix, and in the HQ plate. UI pages and the street never show it on purpose.
3. Pink is used outside unit screens on most non-combat screens (stickers, deck frame, street plates).
4. Medium split: AAA-2 (street, HQ) against cel and ink (city, raid, busts). The designer decision is open; this review does not pick.
5. Brightness steps: city (bright, saturated), map pages (dim, desaturated), dossier (bright cream), street (dark, magenta), HQ (dark green). The eye jumps most at city to map and at map to dossier.

## 5. REDO LIST (prioritised)

| # | State | What is off | What to change | Effort |
|---|---|---|---|---|
| 1 | City Grid, Site dossier, route page (1, 2, 3b) | On the old violet city, low saturation, Solace hue absent | Re-lay on the r42 city with the dim grade (x0.68 outside the fit rectangle, x0.86 inside, hue kept); show the Solace lime Site file; keep the UI | M |
| 2 | Raid setup and defense (9, 10) | Setup on the old city; beats 02-03 forecast competes with avenues | Make the raid-mode dimmed grade (as round 40 did for round 6); re-render setup with HUD; recheck beam colours | M |
| 3 | Netrun street and HQ run (3, 12) | Realistic render beside a cel city; magenta dominant, no Solace identity; HQ-run UI layer absent | After the designer decides the look: re-grade or restyle the street; draw HQ-run UI over `H_decision_v5` | L |
| 4 | Combat backdrop (5) | Old violet Meridian city behind E10; orange ring is the loudest mass | New Solace canyon backdrop in the r42 look; keep the E10 board; drop the outer ring saturation a step | M |
| 5 | Pink on non-unit screens (1, 4 memo, 6, 7, 8, 13) | Pink verb stickers and deck frame | Rule first (question 3), then recolour; deck frame to cyan edge | S after ruling |
| 6 | Win and lose (13, 14) | Halcyon content, brightest frame, no Solace version | Draw Solace win and lose on new-city polaroids; darken the dossier a step | M |
| 7 | Rewards, shop, deck (6, 7, 8) | Old backdrops | Swap in the new city, dimmed | S |
| 8 | Terminal event (4) | Flat dark green, low contrast | Lift the CAM feed and frame glow; check the lime against Cell lime | S |
| 9 | DISPATCH briefing (15) | Violet reply sticker off the yellow family | One sticker family for replies | S |
| 10 | Heat strip (11) | Amber close to Halcyon amber | Check against the Halcyon HUD | S |

## 6. Questions only the designer can answer
1. **Netrun and HQ-run look (first).** Keep AAA-2 realistic for street and HQ beside the cel-and-ink city, bring the street to cel and ink like the new city, or a hybrid? This decides redo item 3 and what the HQ-run UI sits on.
2. **Solace hue in the street and HQ.** Should the netrun street carry Solace lime (and the Bloom pink veins), or stay the neutral magenta and violet street of every corp?
3. **Pink scope.** The pink rule is written for unit screens. Do hot-pink verb stickers (BUY, CONTINUE, JACK IN, UPGRADE, NEW CAMPAIGN) and pink card frames stay on shop, rewards, deck and map pages, or all change? Does the Solace Bloom pink count as a corp colour or as a violation?
4. **Combat backdrop.** The r42 city seen from a canyon, or a Solace-specific park and helix backdrop?
5. **Win and lose.** Does the slice need Solace-specific screens, or does the generic dossier and lock with a Solace crest do?
6. **E10 plates.** Accept E10 as the combat target for the slice? It has no DIRECTION_REVIEW verdict yet.

## Added after redo 1 (map pages on r42)
7. Site names, work orders and THREAT INTEL still read as Meridian (for example PRIORITY LANE EXCHANGE and MANIFEST AUDIT) on the Solace slice. Should the slice data be Solace-flavoured? This is game data, not art.
