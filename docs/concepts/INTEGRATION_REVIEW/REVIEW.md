# M14 integration review: art direction (2026-10-06)

Reviewer: art director's reviewer. Build = `D:\Godot\rebel_cell` main @ 175377de (read only). The build was read
from the newest capture of each screen: the `docs/art_review/PARITY/fixes/*.jpg` "after" columns, `HQ_REDESIGN/build/`,
`ART-*/`, and `docs/timeline/` up to `2026-10-05_21_*`. Locks = `docs/concepts/DIRECTION_REVIEW.md` (later rounds
win) and `docs/ART_BIBLE.md` v2. Side-by-sides: `contact_sheet_diff.jpg` (build on the left, lock on the right). Sheet rows map to
review ids: 1→D1, 2→D2, 3→D3, 4→D15, 5→D5, 6→D6, 7→D7, 8→D14, 9→D8, 10→D9, 11→D10, 12→D18, 13→D11.

**What I found.** The build uses the right assets: the faces, glyph atlas, wheel screens, stickers, MAINFRAME sign,
landmarks and paper kit all come from the art pass. It has the right *parts*, but the scenes are not composed like
the concepts. The concepts get their finish from four things, and the build skips all four on almost every screen:
1. **A dimmed, darkened world behind the UI.** The concepts drop the city to about 55 % around the wheels, the hand
   and the panels. The build draws the bright isometric map at full strength behind everything.
2. **Few, large, readable marks.** The concepts show one sticker verb, three to six nodes and one pencil plan. The
   build adds labels, tags, rings, spray halos and influence fills until the screen is busy.
3. **Every material finished.** Pencil is thick opaque wax with an under-shadow. Holo has scanlines and an RGB
   edge. Stickers have extrude and gloss. The build often draws these as a flat vector line, a flat tinted box or a
   flat chip.
4. **A camera chosen for each screen.** Combat, the HQ run and the netrun use low-angle or close framings in the
   concepts. The build reuses the map's ortho isometric camera, so different screens look the same.

Fix those four once, as systems, and most of the "lacks polish" verdict goes. Grading uses A (matches the concept)
to D (reads as a different game).

---

## a. Verdict by area

| Area | Grade | What matches the concept | What drifted |
|---|---|---|---|
| Combat wheel stack | **C+** | D4 bezel, blades with value windows, corp rims, telemetry rail, HP arc and result chips, screen atlases, precision landings | The hub writes the boss name, the shield and the passive in big type. The concept's hub is an emblem plus a tiny name. The screens are flatter and lower in contrast than the concept, even after WHEEL_b. A lime focus reticle (two arcs plus a crosshair) sits on the boss wheel, and lime is focus only (bible 2.10). The wheel areas are not darkened (3.1). |
| Combat backdrop | **D+** | It is the real HQ model, and it matches the map | The concept is a low-angle close-up. The build uses the map's iso camera at pitch 22 to 40, so it reads as "the map behind wheels". It is bright and saturated, with no 55 % wheel pools, no dark bands under the hand or the top bar, and no rain or haze. Site fights show unrelated holo squares floating in the frame (CARDFACE_hand_b). |
| Cards / FX | **B-** | The C-C face is the art pass's own export. Gloss, cost dot, peel, slap and dissolve are wired | The hand is a flat, evenly spaced row. The concept fans it with overlap, a slight arc and a lifted hover. Cards at rest are dimmed to about 40 % while aiming, so they look disabled. The aim line is a thin, even vector stroke, not the bible's 8 to 10 px wax with dropouts and an under-shadow. The play-result plate is a terminal box on the hub, an undesigned element that covers the hub emblem. |
| HUD (combat) | **B-** | TURN strip, CELL-n sticker, RAM pips, piles, SEND IT over EXECUTE, RESPIN and UNDO chips | EXECUTE is a large ghost word that competes with SEND IT. The concept washes it out to about 25 % in the terminal font. The top-right Settings chip and the debug "Fight / Seed" dropdowns appear in the review frames. |
| City grid / HQ (dir. B) | **C** | The unified 3D city, v4 markers, red pencil TARGET, the paper work order, crew polaroid cards, JACK IN in the verb slot | The concept direction_B is calm: about 8 markers, one plan and a dimmed map. The build idle frame shows more than 20 orange markers, a stack of node name tags, lime spray glow across the Cell district, overlapping CLAIMED stamps, a corp-news ticker band across the top, and a stamp printed over the Heat gauge. The map is at full brightness with no darkening under the panels. |
| Raid | **C** | Circuit inlay, red pencil routes, paper work order, THREAT INTEL holo, START DEFENSE sticker, defence cards (RAID-01 is now the concept card), IF PLACED terminal | The build adds per-node text tags ("Parcel Sorting Hall 20 → 17 HOLDS"), but round 19 says **no node tags** (status lives on the node). The playout puts an orange influence fill over the map, which no round designed. THREAT INTEL is a flat orange box with no scanlines, bands or RGB edge. The RAID SETUP yellow title sticker is gone (Q6). |
| Netrun / route | **C-** | Cable-run paths, ring states, the corp-paper dossier, the hidden-node rule, district plates, the 4.4 s jack transition | The map mode greys the city to a dark slate (luminance 0.044) where the concept is a saturated violet night. The concept dims the network's *surroundings*, not the city's hue. Nodes are small and the route occupies about 10 % of the frame where the concept fills about 40 % at a closer zoom (round 38 transit v3). The ROUTE window, tiny labels and the FIGHT // L1 holo crowd the corners. |
| HQ runs | **C** | Compounds, node rings, title sticker, HQ MECHANIC terminal, the canyon perspective | The camera is pulled far out and the scene is desaturated, so the compound reads small. The concept fills the frame with the landmark and lights its lanes (pink and cyan street glow). The REBEL_CELL canyon reads as a top-down grid, not round 43's canyon. Grey cut-off discs pile up on Solace and Halcyon. |
| Shop / rewards / events | **C+** | MAINFRAME sign v4, pegboard, kraft tags, the offscreen stock wheel, the recycle bin, loot sheet, outcome chips, the PLAY IT SAFE?? pencil | LOOT: the title is PAYOUT where the concept has FIGHT WON. OURS NOW and CONTINUE are missing, and the FIRMWARE DROP panel is absent. The page sits on a generic map city instead of the dimmed fought Site. EVENT: the CAM feed is an empty dark box, the page sits on the bright city instead of the green-tinted dimmed scene, and the terminal is a cramped strip with choices and chips squeezed. Event DISPATCH is now on corp memo paper (EVT-03), which **contradicts** bible 4.11 ("DISPATCH never gets a face... VOICE ONLY") and the media rules: DISPATCH is the Cell's handler, not a corp. |
| Dialogue / portraits | **B** | The bust on a CRT feed, the DISPATCH red waveform with no face, the class gear | No BRIEFING-style composition: the busts are not framed big over a blurred backdrop, and there are no sticker reply buttons (round 31 dialogue A). The listener is not dimmed enough. |
| Menus / title / settings / codex | **B-** | The title matches round 33 option A, with the blurred lit 3D city. Settings framing follows round 31. The pause menu and abandon dialog use stickers plus terminal. New campaign uses tile plates | **Codex is on corp paper**, which breaks the media rule (paper = intercepted corp documents; the Codex is the Cell's own knowledge). The pause menu has 7 stickers on one panel (RESUME, ABANDON, QUIT×2, OPTIONS, CODEX) plus pencil captions, which breaks "one sticker verb per screen" (bible 2.10). The two QUIT stickers are pink and cyan, so colour carries a role it should not. The campaign-slot folders and the "CAN'T UNDO" pencil arrows repeat on all three slots (pencil is for plans, not static captions). |
| Campaign end / dossier | **B+** | The audit dossier, polaroids, post-its, CASE CLOSED, the ransomware lock with padlocks and curling stickers | CORP DOWN (won) is a build invention layered onto the corp's dossier, which is acceptable. The lock's notice is a flat panel. Round 20's lock frames it as a corp-coloured screen over a darkened city with a large countdown. |
| Skins (ART-12) | **D** | | The cobalt and graphite skins re-tint the whole UI into outlined neon wireframe city plus pastel panels (skins_cobalt.jpg). They are the rejected wireframe / neon-painting look (bible 1.2 "Rejected"), applied globally. |

---

## b. Differences, by priority

Each item gives the build capture and the locked reference (with its round), then what differs and the fix.

### P1: contradicts a lock or reads wrong

**D1. Combat backdrop is a map, not a close-up.**
- Build: `PARITY/fixes/ARENA_b.jpg` (round 2 column).
- Locked: `round41_wheel_stack/combat_typical_v4.png`, `round31_meridian_combat/combat_meridian.jpg` (rounds 11, 25, 26, 31).
- Different: the iso top-down camera, no darkening, saturated yellow containers that compete with the orange boss
  wheel.
- Fix:
  - Camera: a perspective camera about 6 to 10 degrees above the street, looking *at* the facade, 35 to 50 mm
    equivalent. That is the same `fov_deg` path already built for the canyon (HQRUN-08). Use it for every HQ and
    Site.
  - Grade: after the city grade, multiply by 0.55 inside a soft disc of radius 1.25 R around each wheel. Add
    vertical dark bands, about 35 % black, 120 px under the hand and 70 px under the top strip (bible 3.1).
  - Atmosphere: depth haze 15 to 20 % toward the night sky colour, plus the round 11 rain layer at night.
  - Saturation: cap the backdrop at 0.6 inside the wheel pools.

**D2. The hub is a text plate.**
- Build: `WHEEL_b.jpg` right.
- Locked: `round40_hub_inner_ring/hub_cores_v3.png` and `combat_typical_v4` (round 38 to 40).
- Different: the boss name in Anton about 20 px, with SHIELD and the passive in mono inside the hub.
- Fix:
  - The emblem goes in the centre at 0.45 of the hub's radius, with the accent glow.
  - The name sits under it in Plex Condensed caps at 9 to 10 px at 1080p, and the passive at 8 px. Below r = 90
    the hub shows the emblem only.
  - Shield and passive belong in the HP result chips and the tooltip, not the hub.

**D3. The aim pencil is a thin vector line.**
- Build: `COMBAT_HUD.jpg` after column.
- Locked: bible 1.2 and 6.3, `round11_combat_target/combat_boss_night.png`, `round19_combat_fx/card_play_v2_storyboard.png`.
- Fix:
  - The stroke is a `Line2D` 9 px wide at 1080p with round caps and the wax-grain texture: dropouts every 40 to
    70 px, a 1 px sheen line at 35 % white.
  - An under-shadow copy sits at offset (2, 3) in #060308 at 85 %.
  - Colour #FFE200 at alpha 0.96.
  - The loop round the target wheel is one hand-drawn ellipse with a 20 degree overlap tail, not a perfect circle.

**D4. The reticle is lime.**
- Build: `CARDFACE_hand_b.jpg` (the aiming row), `WHEEL_b.jpg`.
- Locked: bible 2.10 (lime = focus) and 3.17.
- Different: two lime arcs plus a crosshair on the target wheel during a hover or aim, on top of the yellow pencil
  loop.
- Fix: delete the arcs during aim, because the pencil loop *is* the target mark. Keep lime brackets only for pad
  focus.

**D5. Raid nodes carry text tags and spray halos.**
- Build: `MAPVIEW.jpg` (after, Solace setup) and `HQ_REDESIGN/build/g_final.jpg`.
- Locked: `round40_city_unified/raid_view_v3.png`; round 19 says "no node tags; node status shown on the node itself".
- Fix:
  - Remove every always-on name and HOLDS tag.
  - Show the forecast as the dashed outer ring in the outcome colour (bible 4.8).
  - The name appears on hover only, as a terminal tooltip.
  - Replace the lime "spray" glow discs under owned nodes with the socket's own 2 px halo at 35 %.
  - Never stack stamps: CLAIMED stamps once, then wipes after 1.5 s, like the TAKEN pencil grammar.

**D6. Raid playout has an orange influence fill.**
- Build: `MAPVIEW.jpg` playout end.
- Locked: no reference. Round 20 to 23 GIFs show the state on nodes, links and units only.
- Different: a blocky orange area wash over the city. It is a medium with no job.
- Fix: remove it.
  - Losses read through node health drain, DOWN wipes and de-powered links.
  - If a "where they reached" summary is wanted, it belongs on the raid report as red pencil hatching on the
    paper's map thumbnail.

**D7. The HQ idle frame is crowded and the city is not dimmed.**
- Build: `HQ_REDESIGN/build/g_final.jpg` idle 1.0.
- Locked: the ruled `HQ_REDESIGN/direction_B.png`, plus bible 4.1.
- Fixes:
  - Draw the map at the 0.68 "map band" darkening (as raid) outside the network fit rect. The 3D city stays fully
    lit only inside a soft vignette round the selected Site.
  - Show at most one name tag (the selected Site). Others get a tag on hover.
  - Pin only the Sites bible 4.5 pins (Exploit and Heat objective, yours, cleared, seized, boss). The ring of more
    than 15 orange "selectable" markers is the hidden-node rule failing at HQ zoom. Apply 4.6's visibility rule
    here too.
  - Move the corp-news ticker off the top. A corp news toast is a holo strip at the foot for 2.4 s (bible 4.13),
    not a standing band.
  - No stamp on the Heat gauge. The Heat change is the gauge's roll.

**D8. Loot screen.**
- Build: `TITLE-01d.jpg` loot after, `CARDFACE_loot.jpg`.
- Locked: `round32_shop_reward/reward_screen_v2.png` (round 31 A).
- Fixes:
  - The title sticker reads FIGHT WON (yellow) for a fight. PAYOUT is a terminal word.
  - The backdrop is the fought Site's close-up in its won state (lime outlines, district at 62 %) with the yellow
    pencil "OURS NOW", not the map.
  - FIRMWARE DROP is a lime-edged terminal with the mini spinner when a drop exists.
  - The CONTINUE sticker sits bottom right. If it "changes the flow", it can be the same press as taking the card.
    The art need is that the page ends on a sticker verb.
  - The sheet is pure white liner #F7F7F2 with kiss-cut slot outlines, and the taken slot stays a shiny empty
    outline.

**D9. Event screen.**
- Build: `TITLE-01d.jpg` event after.
- Locked: `round31_reward_event/event_screen.png`, `event_screen_memo.png`.
- Fixes:
  - The CAM feed must never be an empty box. Until per-event renders exist, use the fought or current Site's
    backdrop close-up through the CAM shader: green-tinted mono, scanlines, a REC dot and a timestamp. One frame
    per corp is enough, and it is the same "event CAM feed in world style" the bible asks for.
  - The page sits on the close-up dimmed to 40 % with a green corp tint, not on the map.
  - Choices are full-height yellow-number stickers, 44 px tall at 1080p, with chips beside them.

**D10. DISPATCH became corp paper.**
- Build: `NETRUN.jpg` EVT-03 after.
- Locked: bible 4.11 and 1.2; round 31 `dialogue.png` (DISPATCH voice only).
- Different: DISPATCH's words are on a DISPATCH letterhead memo with a DO NOT FORWARD stamp.
- Fix: revert to the red voice trace panel ("VOICE ONLY // NO FEED") plus the transcript typed on in the red-accent
  CRT. DISPATCH is the Cell's handler, so it uses the Cell's medium in DISPATCH red. Paper only becomes correct
  after the betrayal *if* the designer wants DISPATCH to read as a corp (question Q-A below).

**D11. Codex on paper.**
- Build: `MENUS.jpg` codex.
- Locked: bible 1.2 (terminal = the Cell's systems), `round33_ui_chrome/ui_kit.png`.
- Fix: the Codex book becomes a terminal. Navy glass, scanlines, `> CODEX // WHAT THE CELL KNOWS`, tab plates as
  now, entries in glyph-tile rows (26 px glyph plus Plex text, like the tooltips). Entries about a corp (its
  crest, its bosses) may show an intercepted **holo** card when selected (hacked intel). Never paper.

**D12. Skins.**
- Build: `ART-12/skins/skins_cobalt.jpg`, `skins_graphite.jpg`.
- Locked: bible 1.2 "Rejected: the wireframe net, neon-painting cities".
- Fix: a skin may only swap terminal accent and edge tokens (cyan to cobalt or graphite) and sticker backing hues.
  It must never re-render the city, paper or pencil. Today it turns the world into neon wireframe.

**D13. The pause menu has many stickers.**
- Build: `PAUSE_b.jpg`.
- Locked: bible 2.10 (one sticker verb per screen), round 33 ui_kit.
- Fixes:
  - RESUME is the only sticker (yellow, safe, default focus).
  - Everything else is a terminal row with a `>` caret: Options, Codex, Quit to main menu, Quit to desktop.
  - The destructive ABANDON is a HARM-edged terminal row. Its confirm dialog then carries the pink BURN IT
    sticker.
  - Remove the pencil captions ("No going back", "Come back soon"). They are jokes in pencil, which round 19 bans.

### P2: loses polish or clarity

**D14. Netrun map mode turns the city grey slate.**
- Build: `ROUTE_b.jpg`, `MAPVIEW.jpg` route.
- Locked: `round37_netrun/city_default.png`, round 41 transit v3 ("lighter city").
- Fixes:
  - Keep the hue: map saturation 0.85, not 0.7, and no violet veil.
  - Darken by 0.86 and use translucency per bible 4.1.
  - Zoom to fit the run map at about 130 to 190 ortho so the route fills 40 % or more of the frame.
  - Node stickers at least 44 px.

**D15. The hand is flat.**
- Build: `CARDFACE_hand_b.jpg`.
- Locked: `round41 combat_typical_v4`.
- Fixes:
  - Fan the hand: ±2.5 degrees per card from the centre, 12 % overlap, a 6 px arc rise at the centre.
  - At rest, cards are full brightness. Unaffordable cards go greyscale with the NEED tag; others never dim to
    40 % while aiming (use 75 %).

**D16. EXECUTE competes with SEND IT.**
- Build: `COMBAT_HUD_b.jpg`.
- Locked: round 22 `send_it_sticker.png`.
- Fix: EXECUTE in Share Tech Mono at 25 % alpha, 0.8× the SEND IT cap height, half covered by the sticker.

**D17. THREAT INTEL holo is flat.**
- Build: `RAID.jpg` RAID-03 after.
- Locked: round 21 to 22 holo, bible 1.2.
- Fix: corp tint at 78 %, 4 px scanlines at 12 %, three slow horizontal bands (6 s period), ±2 px RGB split on the
  edge only, a 0.88 scrim behind, and the cracked seal with a red fracture under the DECRYPTED stamp. Today it is
  an orange box with a stamp.

**D18. HQ-run framing.**
- Build: `HQRUN.jpg` after.
- Locked: `round43_hq_mechanics/hq_*_compound.png`.
- Fixes:
  - The landmark fills 55 to 65 % of the frame height.
  - Restore the street lane glow under the compound at 100 % (the concepts' pink and cyan lanes).
  - Cut-off nodes are small grey discs at 60 % size with no backing.
  - The REBEL_CELL canyon uses round 43's raking view down the street, with the blade signs visible.

**D19. Light spill is missing on panels and stickers over the city.**
- Where: every screen.
- Locked: round 3 combined_v2.
- Fix: neon (signs, the JACK IN sticker's pink, the TARGET pencil) casts an additive spill of 20 to 30 % on the
  city under it, with a radius of 1.5× the element. Panels cast a soft 18 px black drop shadow at 45 % onto the
  city (the concepts' panels sit *on* the world).

**D20. The ON AIR ticker and the top bar repeat on every page.**
- Build: `PAUSE`, `SLOTS_c`, HQ.
- Fix: the ON AIR line lives on the title and the HQ only. Other pages drop it.

**D21. Campaign slots.**
- Build: `SLOTS_c.jpg`.
- Fix: one red pencil "CAN'T UNDO" on the focused slot only, not on all three. Manila folders are fine. They are
  the Cell's own case files, so they get the **Cell's** stamp style, not a corp letterhead.

### P3: finish

- **D22. Sticker gloss sweep.** Bible 1.2 says "one slow sweep on one sticker at a time". The captures show several
  stickers lit at once on the title and pause screens. Add a global sweep scheduler: one sweep every 4 to 6 s on
  the screen's primary verb.
- **D23. Scanlines on terminals.** They are present but the faint scrolling hex-dump at 6 % is missing on most
  panels (only the HQ card has it). The shared `crt_panel` uniform needs `hexdump = 0.06` by default.
- **D24. Paper.** Work orders and dossiers lack the paper clip and the 1 to 2 degree tilt with a contact shadow
  that the concepts have (round 21 raid_report). Add a tilt from a seeded stream and a 6 px shadow.
- **D25. Motion.** Pencil marks appear whole in some captures (HQ TARGET circle). They must write on in about
  0.4 s and wipe with the cloth (never fade).

---

## c. Screens the concepts never designed

Rule for all: borrow the nearest locked screen, and give each medium its job.

| Screen (build) | Fits? | Call |
|---|---|---|
| **HQ page, direction B** (ruled; the HQ room was DROPPED) | Mostly. HQ actions live on the city as the Cell's map, which is the right spirit | Keep B. It is the City Grid with a hand. Its dressing must follow the City Grid lock (round 39 `city_grid.png`): THE GRID-style yellow title sticker is allowed (Q10 below), minimap terminal, key strip, at most one tag. The Site card is a terminal; the selected corp Site's file is a **holo** (it is hacked intel, round 37 DEPOT 15). Today the Site card is a terminal, so change it to holo for corp Sites and keep terminal for the Cell's own nodes. The home node CORE's card gets PATCH / Heat SCRUB as terminal actions with one pink verb. Directions A and C are superseded and must not ship. |
| Heat gauge + Heat terminal | Yes | Terminal (the Cell's system). Bare Anton number. No stamp over it (D7). |
| Codex | **No** (paper) | Terminal (D11). Corp entries as a holo card. |
| Stats & achievements | Partly | Tiles are terminal (good). Achievement badges as die-cut stickers are right (they never change once earned). Run history on **paper receipts is wrong**, because they are the Cell's records: make them terminal log rows, Anton outcome word on a sticker only for FLATLINED or COMPLETED. |
| Options | Yes | Round 31 terminal, as built. |
| Pause | Partly | One sticker (D13). |
| Confirm / abandon / quit | Yes | Round 33 abandon dialog: yellow CANCEL, pink BURN IT. Quit uses yellow KEEP GOING plus a cyan terminal "save & quit", not two stickers of competing hue. |
| Campaign slots | Yes, mostly | Manila case files are the Cell's own, so the label is a terminal tab clip, not a corp letterhead. One pencil note (D21). |
| New campaign | Yes | Terminal tiles. The corp tiles may show each corp's crest on a small **holo** chip (intel on the target), a nice touch that fits. |
| Deck viewer / card detail | Yes | Terminal window with sticker cards. Card detail notes as tooltip glyph rows. Add the liner backing behind the grid (cards are stickers on a sheet, like loot). |
| Loadout (deck / spinner tabs) | Yes | As the deck viewer. The spinner tab should show the D4 wheel at r = 220 on a dimmed backdrop, not a mini wheel. |
| Route map variants (GRID VIEW, show-all, focus stops) | Yes | Follow round 37. The focus stop is lime brackets on the sticker; no extra rings. |
| Raid interlude (mid-run raid) | Yes | Same raid view. Add one binary-bits "INCOMING" transition (bits are transitions), about 0.6 s, from the run page into the raid. |
| Run end (JACKED OUT / FLATLINED / HOME FELL) | Yes | Polaroid with a verdict sticker and the grey city is a good invention. The report is a terminal (the Cell's log). The verdict is a sticker (fixed object). FLATLINED's red pencil X is allowed (true: the operative is dead). |
| Campaign WON (CORP DOWN) | Yes | Corp's own audit dossier with CORP DOWN. Keep. |
| Play-result plate on the hub (aiming) | **Undesigned and covers the hub** | Drop the plate. The result shows in the HP result chips of each affected wheel, highlighted with a yellow pencil underline (true plan), plus the existing ghost landings. |
| Card piles (DECK / DISCARD) | Yes | Plain dark card backs, as the concept. |
| TURN strip key hints, Settings corner chip | Partly | Settings becomes a 32 px terminal icon chip. Key hints, see Q2. |
| Tutorial card between the wheels | OK | Terminal card with a cyan edge, never a sticker. |
| ON AIR ticker | OK on title and HQ | Terminal strip. Elsewhere remove (D20). |
| Corp news ticker band (HQ top) | **No** | Holo toast at the foot, 2.4 s (bible 4.13). |
| Raid playout influence fill | **No** | Remove (D6). |
| Skins | **No** | Token-only (D12). |
| Jack-in transition | Yes | Locked 4.6; bits plus CRT collapse. |

**HQ check against the designer's decision.** Round 42 dropped the HQ room. Direction B folds the HQ into the
city at the RAID band with a hand. That fits the art direction: HQ actions are verbs on the Cell's own nodes, and
the CORE's PATCH, CLAIM, REPAIR and UPGRADE all sit in the verb slot. One mismatch: the Heat SCRUB lives in the Heat
terminal off the top bar. It should also appear as the CORE node card's terminal action, because the home node is
where HQ actions belong.

---

## d. Systemic polish gaps

| Gap | Missing where | Fix (one system) |
|---|---|---|
| World darkening under the UI | Combat, HQ, loot, event, route | One `UiScrimPools` layer: 0.55 pools round wheels and panels, dark bands under bars. Concept numbers are in bible 3.1 and 4.1. |
| Light spill | Stickers, signs, pencil over the city; combat | An additive spill sprite per emissive UI element onto the world layer (D19). |
| Ink and cel shading | The 3D city at map zooms looks clean CG in places. Panels have no ink keyline | Ink edge pass strength 1.0 at combat or close; keep it at map zoom (5b compares show it thinner than Blender). |
| Facet detail | Landmarks in Godot are smoother than the Blender finish (`ART-5/5b/meridian_hq_night_compare.jpg`: flat walls, no tone jitter) | Bake per-triangle tone jitter into vertex colour (±6 %), and normal-split facets. |
| Sticker gloss / peel | Several stickers gloss at once; no peel corner at rest on menu stickers | Sweep scheduler (D22); 4 px corner curl at rest on verb stickers. |
| Pencil opacity / wax | Aim line, HQ plan lines, captions | One wax material everywhere (D3). Audit every pencil: is it a true plan? If not, remove it. |
| CRT look | Hex-dump missing, holo panels flat | Shader defaults (D17, D23). |
| Camera | Iso reused for combat and HQ run | Per-screen cameras (D1, D18). |
| Motion timing | Pencil appears whole; tickers always on | Write-on 0.4 s, wipe 0.4 s; one ambient loop per screen. |
| Clutter | Labels and tags | One rule: a label appears only for the selected, hovered or plan-relevant element. |

---

## e. Questions that need the designer

- **Q-A.** DISPATCH after the betrayal: still voice-only red CRT (my call), or corp paper because it is now an
  enemy? Before the betrayal it must be voice-only.
- **Q-B.** Combat backdrop camera: accept the perspective close-up at 6 to 10 degrees for every fight (a perf cost
  of about 1 to 2 ms over iso, already measured for the canyon)?
- **Q-C.** Skins: may they exist at all beyond accent tokens? My call: tokens only.

---

## Calls on the orchestrator's 15 open questions

1. **Fight top bar: (c), no bar, plus a small Heat gauge in the corner.**
   - Bible 3.15 puts Heat on combat in the backdrop (H1 "the city reacts"), never on the HUD.
   - The Heat-everywhere ruling (Q1) still wants the number reachable, so use a 120 × 32 terminal chip top left:
     number, band word and the strip, no bar.
   - This matches concept `combat_typical_v4`, which has no bar.

2. **Key hints: tooltip only.**
   - Concept HUD v4 (round 43) shows key letters under the nudge buttons (Q / E, A / D) and on RESPIN [R] and
     UNDO [Z]. Those stay, as letters on the controls, not as a sentence.
   - No caption line.

3. **HQ behind Sites: DESIGNER (scope).** The art call is "with the unique per-fight backdrops". A distant HQ in an
   orthographic Site shot is the wrong composition anyway. Bible 3.14 says the HQ is the boss backdrop, and a Site
   backdrop is its own close-up.

4. **Map mode: entries of the shown raid only, yes.** Round 19 says major nodes and no frontier clutter, and bible
   4.8 is true to the rules. "One link per route" is a rules question, so it is **DESIGNER**. The art call is to
   draw what the route really uses.

5. **Honeypot card: no.**
   - The vault glyph is VAULT's. Bible 5.2 (unique silhouettes) and 2.3 (colour = type) say pink is attack.
   - Use a placeholder from the atlas: `placeholder_phishing` (the hook) in the decoy violet #B08CFF, because a
     honeypot lures like the decoy.
   - Log it for the glyph concept slice.

6. **Raid card size 105 × 120: OK in 720p units only.**
   - The concept raid cards are about 150 × 175 at 1080p, which is 100 × 117 at 720p. So 105 × 120 at 720p is OK
     **if** that is 720p units.
   - At 1080p they must scale to about 158 × 180. The INT and count text must stay above the 12 px floor.

7. **RAID-10, result banner in grease pencil: no.** The result is a fixed fact once the raid ends, so it is a
   **sticker** (CELL HOLDS, round 20 to 21 lock) on the after-action **paper**. Pencil may add a tick or "RIP" on the
   report (round 21). The banner over the map goes.

8. **Won and abandoned network photos: yes, queue the export.** The round 21 dossier polaroids are locked, and the
   won and abandoned variants reuse the polaroid context (bible 4.12). Shoot them from the unified city at the
   final state.

9. **Big text on raid setup: YOUR NETWORK under THREAT INTEL at 1.3 and up.** Grease pencil and the map must stay
   uncovered (round 40 standing rule). Stacking the panels in the right column keeps the map.

10. **RAID SETUP title sticker: put it back.** Round 40 `raid_view_v3` has the yellow RAID SETUP sticker. A screen
    title is a fixed object, so it is a sticker. Q6 "no title" was for the HQ idle page. While the DEFENCE hand is
    open the page *is* the raid setup, so show the title then. On the HQ idle page, "THE GRID"-style is optional,
    but I recommend no title there.

11. **HQ-run titles: no, use the concept's words.**
    - Use CLIMB THE HELIX / CRANE + TRAIN / THE LONG WAY / THE LAUNCH LOOP when those mechanics are built.
    - Until then, "<CORP>: <CENTRAL SERVER NAME>" (e.g. "SOLACE: THE GENOME CORE"). It names a real place
      (bible 4.7) and is truer than "HQ RUN".

12. **RESET TO DEFAULTS: DESIGNER (UX scope).** The art call is the open tab only, labelled "RESET THIS TAB", as a
    terminal button, not a sticker.

13. **Codex: terminal glass** (D11; bible 1.2: the Codex is the Cell's own knowledge). Corp entries may open a holo
    card.

14. **Events at text 1.3: shrink and reflow, never hide.** The CAM feed is the event's world medium (bible 4.11).
    Shrink it to a 160 px wide strip above the story, and drop it last.

15. **Hidden route nodes: grey discs are wrong.**
    - Round 35 to 36 node states say white means "not yet available" and grey means "past or used". A grey disc
      for a hidden node says "used".
    - Round 37 locks "hidden by default". So: **fully hidden**, with hover, the legend strip or the Options switch
      to reveal.
    - If a hint of the run's shape is wanted, use hairline white dashes at 25 % for the links only, never a grey
      disc.
