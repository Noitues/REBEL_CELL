# REBEL_CELL — Gap Analysis and Horizontal Slice Plan

Target set by the designer: **a complete game — all bosses, operatives, story, dialog,
menus — that an average player spends about 100 hours on to reach full content.**

The designer's process (2026-09-24): fix every vertical-slice gap, rerun this analysis,
repeat until the vertical section comes up clean; then run the same loop over the
horizontal slices. Every decision is made by the implementer and logged in
`DECISIONS.md`. This file is rewritten on each pass; the pass log keeps history.

## Pass log

| Pass | Date | Vertical gaps found | Result |
|---|---|---|---|
| 1 | 2026-09-24 | 48 across combat, netrun, campaign, narrative, menus, art | Fixed in vertical batches 1–4 (commits 3295d43 … 102f1e0) |
| 2 | 2026-09-24 | 5 (V1–V5) plus 4 found by the balance simulation (home repair, raid frequency, patrol soft-lock, one-shot tier damage) and 1 display bug | Fixed in vertical batch 5 |
| 3 | 2026-09-24 | **0** | Vertical slice clean. Horizontal loop starts (§4). |
| H1 | 2026-09-24 | 16 after M6-M12 (Solace-only win text, speaker, music, DJ, ICE picker and records; codex spoilers; rescue; untested cores and home servers; built-in ICE Locks ignored in raids; stale docs) | Fixed in horizontal batch H1 |
| H2 | 2026-09-24 | 11 (5 P1: raid names and warning keys per corporation, event speakers, shared text naming Solace, untested H1 rules; 6 P2) | Fixed in horizontal batch H2 |
| H3 | 2026-09-24 | 6 (lost-raid names, REBEL_CELL elite pool leak, pad-only focus, untested config numbers, stale doc, Mirror numbers in code) | Fixed in horizontal batch H3 |
| H4 | 2026-09-24 | 6 (focus lost after a card play, Tab swallowed by focus, modals without focus, ICE unreachable by pad, auto-focus preview, docs/tests) | Fixed in horizontal batch H4 |
| H5 | 2026-09-24 | 4 (keyboard actions replaced the End Turn preview, dialogs dropped focus, Esc in the code field, input-level tests) | Fixed in horizontal batch H5 |
| H6 | 2026-09-24 | 6 (reward, Modem, corporation picker and lower Grid rows unreachable by D-pad; dead reward hotkeys; SEND IT left; assist label numbers) | Fixed in horizontal batch H6 |
| H7 | 2026-09-24 | 3 + tests (title Options sections, reference notes unscrollable by pad, netrun combat linked too early) | Fixed in horizontal batch H7 |
| H8 | 2026-09-24 | 1 + docs/test (reference notes still not pad-scrollable; H7 claim corrected) | Fixed in horizontal batch H8 |
| H9 | 2026-09-24 | 1 + doc (HQ panels ran off the 1280 screen once many unlocks and classes existed; stale test count) | Fixed in horizontal batch H9 |
| H10 | 2026-09-24 | 1 + follow-up (mid-run raid screen ran off the 1280 screen; netrun combat entry left focus on Settings) | Fixed in horizontal batch H10 |
| H11 | 2026-09-24 | 10 (stationed operatives could run and dead ones kept posts, empty-roster stall, text-scale overflow, Heat previews unscaled, home repair ignored ICE 13, boosts skipped special runs, relay shared only the Breaker bonus, magic numbers, stale TECH_SPEC, stale counts) | Fixed in horizontal batch H11 |
| H12 | 2026-09-24 | 7 (profile per slot, final Rack rewards unclaimable, patrol Seized mid-run re-extracted its Exploit, raid setup / end / title overflow, Daemon and raid magic numbers, Twin Pointer Miss and Cold Exit, Racks stat estimated) | Fixed in horizontal batch H12 |
| H13 | 2026-09-24 | 9 + 1 (inner-ring cards moved the outer ring, resolve-time resistance wiped, card kills didn't end fights, hidden and lethal Terminal costs, Daemon choices charged twice, Scrubber Rack labels, tutorial over the wheels, Momentum numbers, GDD header; netrun panels overflowing at text scale 1.6) | Fixed in horizontal batch H13 |
| H14 | 2026-09-24 | 25 (content-vs-behaviour sweep: 4 event texts, 5 enemy/boss mechanics, 5 card/Firmware/hub behaviours, 9 UI fit and pad-focus, 2 save/resume) | Fixed in horizontal batch H14 |
| H15 | 2026-09-25 | 8 (Daemons fired per extra resolution, hotkeys behind the pause menu, pause Options clipped, Intel showed raw phase layouts, a Flip refreshed Firmware limits, Repair hid its price, fixed statuses previewed as random, config and doc leftovers) | Fixed in horizontal batch H15 |
| H16 | 2026-09-25 | 5 (Mirror copies fired Daemons and resolved the Miss, Commons Array kept orbiting, arrow keys unbindable, netrun pause menu clipped at 1.6, Esc in the pause Codex) | Fixed in horizontal batch H16 |
| H17 | 2026-09-25 | 6 (pause menu let clicks through, Shunt landings skipped statuses / Stolen Intent / drones, copies took Burner's Overclock free, rebinds took reserved and duplicate keys) | Fixed in horizontal batch H17 |
| H18 | 2026-09-25 | 5 (Reset dropped pad buttons, combat pause menu unthemed / unscaled, subtitles unscaled, Mirror copies of Overclocked slots, Stolen Intent kept Burner's Overclock) | Fixed in horizontal batch H18 |
| H19 | 2026-09-25 | 3 + doc (refused rebind widened Options off screen, key hints ignored rebinds, Mirror copies ignored Parasite, README autoloads) | Fixed in horizontal batch H19 |
| Merge | 2026-09-26 | Visual/UI branch merged (5afe42d): stickers and SEND IT carry bound keys, stickers moved off the wheel, paged combat subtitles | 540 tests; see DECISIONS "Merge" |
| H24 | 2026-09-27 | 38 from pass 24 (0 P1; 11 P2; 27 P3) incl. the fourth naive-player reviews, plus test isolation (parallel runs shared one settings file) | Fixed in horizontal batch H24 (combat, city maps, screens); DECISIONS "H24 ..." entries. Motion moved to its own Animation pass |
| H23 | 2026-09-27 | 21 from pass 23 (1 P1: an empty subtitle box after a re-dock; 12 P2; 8 P3) incl. the third naive-player reviews | Fixed in horizontal batch H23 (combat, city maps, screens); DECISIONS "H23 ..." entries |
| H22 | 2026-09-27 | 14 from pass 22 (0 P1, 8 P2, 6 P3) incl. the second naive-player reviews | Fixed in horizontal batch H22 (combat, city maps, screens); DECISIONS "H22 ..." entries |
| H21 | 2026-09-26 | 22 from pass 21 (3 P1: pad nudge wheel/ring, pad focus lost, no visible turn result; 12 P2; 7 P3) incl. the first naive-player reviews | Fixed in horizontal batch H21 (combat, city maps, screens); DECISIONS "H21 ..." entries |
| H20 | 2026-09-26 | 25 after the merge (5 P1: hidden resolve outcome, hidden card/respin previews, blind slice choice, silent refusals, no target marker; 10 P2; 10 P3) plus the designer's 7 (tooltips, drag-to-target cards and nudge arrows, a baked backdrop with live lights and territory colour, no text logs, naive-player reviews, directions that read the right way) | Fixed in horizontal batch H20 (combat, city, screens); DECISIONS "H20 ..." entries |

### H24 (fixed 2026-09-27): pass 24 = audits + fourth naive-player reviews

No P1. Preview == result held for 7 enemies (4 bosses) x 2 seeds x 8 turns, LAST TURN
parts summed to the real change for all 59 enemies incl. DISPATCH and a Mirror; satellite
plates stayed clear of tags in 3,510 placements; the Grid held for all corporations at
1.0 / 1.3 / 1.6 early and late.

| # | Sev | Gap | Source |
|---|---|---|---|
| 1 | P2 | Translators never saw the code's words (no tr() keys in strings.csv) | horizontal |
| 2 | P2 | Words translated twice (status line, respin note, HQ buttons, pad prompts, speaker names) or never (tag titles, YOU, statuses, SEND IT, RAM, Heat poster, raid facts, screen titles, Modem, map words) | horizontal, vertical, non-English |
| 3 | P2 | "%+d" keys lost their numbers under pseudolocalisation | vertical, horizontal |
| 4 | P2 | At 1.6 the inner-ring arrow answered as the outer; drones took arrow clicks | vertical |
| 5 | P2 | At 1.6 the aim hint covered the RAM counter; the status line ran under Settings | vertical, beginner |
| 6 | P2 | Satellite tokens and plates sat on NEXT and LAST TURN | vertical |
| 7 | P2 | Bigger text made LAST TURN and hub names smaller | vertical, beginner |
| 8 | P2 | Raid map at 1.6 late in a campaign: nodes outside, legend over nodes | horizontal |
| 9 | P2 | Grid at 1.6 small, labels dropped or touching the top bar (H23 open question) | vertical, beginner |
| 10 | P2 | RUNS OPEN NOW rows alike: no reason to pick one | beginner, non-English |
| 11 | P2 | Icon collisions: snowflake = ICE and Heat reduction; diamond = Exploit and shop | beginner |
| 12 | P3 | LAST TURN missed drone block and RAM refill; counted capped shield | vertical, horizontal, beginner |
| 13 | P3 | "-11 HP" / "HITS YOU 14" needed a sum; hovered cards didn't say which wheel they act on; no win condition; aim dots unexplained | beginner, non-English |
| 14 | P3 | Toasts over the cards; the aim line over HP and NEXT; standalone status line ~100 px | beginner, vertical |
| 15 | P3 | SAVED placed with stale geometry; pager page of only a speaker name | vertical |
| 16 | P3 | Esc left the Modem when Settings was rebound | horizontal |
| 17 | P3 | Event, Modem, HQ dossier, route panel, step-row and label overlaps at 1.0 / 1.6 | vertical, beginner |
| 18 | P3 | Title Continue line read as debug; the storyboard's title showed another slot | beginner |
| 19 | P3 | Raid defences unexplained, RUN THE RAID read as attacking, ARMORY counts differed | beginner, non-English |
| 20 | P3 | Stale DISPATCH lines on later screens; top-bar set changed unexplained | beginner |
| 21 | P3 | Test runs and storyboards shared the player's settings file (flaky failures) | ANIM-1 agent |

### H23 (fixed 2026-09-27): pass 23 = audits + third naive-player reviews

LAST TURN matched the real HP change for 58 enemies x 4 turns; satellite landings matched
the resolver for every satellite-bearing enemy; the raid forecast verdict matched
`raid_verdict` in 720 cases; event outcome rows matched the applied deltas in 7,895.

| # | Sev | Gap | Source |
|---|---|---|---|
| 1 | P1 | A line on screen when the subtitle bar re-docks (fight start, screen change, text scale) turns into an empty framed box | vertical, horizontal, beginner |
| 2 | P2 | Wheels still shrink at big text (60 px in a run at 1.6); hub names cut ("Breake") | vertical, horizontal, beginner |
| 3 | P2 | NEXT disagrees with the HP after SEND IT when a turn-start effect fires (Auto-Renew); LAST TURN nets them into NO CHANGE | vertical |
| 4 | P2 | Drone tokens cover their host's HP; at 1.3+ a drone's HP plate sits under the tag | vertical, horizontal |
| 5 | P2 | Raid map nodes under the top bar, off screen or under the Armory | horizontal |
| 6 | P2 | Spoken lines and drawn words (tags, stamps, stickers, combat chips) never translate | horizontal, non-English |
| 7 | P2 | After SEND IT nothing says what happened (defend + afflict read NO CHANGE); a respin that lands the same looks like RAM for nothing | beginner, non-English |
| 8 | P2 | Two key pairs for nudging ([Q]/[E] arrows vs "YOURS [W] OUTER [R]"); OUTER on one-ring wheels | beginner |
| 9 | P2 | Route legend is the campaign legend; route icons unexplained | beginner, non-English |
| 10 | P2 | Modem items: no descriptions, "100+" prices, BUY/SHRED not buttons, cut card text | beginner |
| 11 | P2 | City Grid: legend below the fold, labels piled or floating from their node, a node under the panel; HQ mini-map labels pile at 1.6 | beginner, vertical |
| 12 | P2 | Raid setup numbers ("50 > 40", "0/2", "x1", 10/8/12) unexplained; no line saying what a raid is | beginner, non-English |
| 13 | P2 | Pad prompts missing on HQ, Grid, raid, route, Modem, loot, event | beginner |
| 14 | P3 | SAVED stamp over Back to HQ; raid speaker named twice; raid line cut with no cue | vertical, beginner |
| 15 | P3 | Aim hint on the RAM row and "Drop" on a pad; tutorial hard-codes A/B/1-9 and says PARTIAL | vertical |
| 16 | P3 | Satellite plates use "5→2"; target ring doesn't scale | vertical |
| 17 | P3 | "-11 HP" under DEFEND reads as a cost; bare "+4" folded chip; RESPIN 4 without its unit | beginner |
| 18 | P3 | Event subtitles pseudolocalised twice; forecast stamp icon over its caption at 1.6 | horizontal |
| 19 | P3 | "+0 Heat" event option; event title under the subtitle band; "Scrub Heat -5 (25)" | beginner |
| 20 | P3 | WANTED poster's COOL hidden; Pirate Radio clipped | vertical, beginner |
| 21 | P3 | Node kinds unexplained until the legend; run list rows without icons | beginner, non-English |

Not changed: the title's Continue summary reads the newest real slot (the storyboard plays
in a private slot); the toast still sits over the hand (H21 moved it off the HP arcs).

### H22 (fixed 2026-09-27): pass 22 = audits + second naive-player reviews

Pass 22 found no P1. Preview == result held for 112 fights, 653 card hovers (100
reshuffling) and every random pick; aiming held for 3,408 card x class x ring cases; the
event outcome icons matched 5,010 choice applications.

| # | Sev | Gap | Source |
|---|---|---|---|
| 1 | P2 | After SEND IT the forecast ("60→49") read as the result; two HP numbers disagreed | beginner, non-English |
| 2 | P2 | LAST TURN missed CORRUPTED bites, heals, evades, guard hits | horizontal |
| 3 | P2 | Satellite markers and labels sit on slice values and HP numbers; a satellite inside a nudge arrow's hit area at 1.3+ can't be aimed at | vertical |
| 4 | P2 | At big text the wheels shrink away and the tag covers the inner arrows; hub and ring names cut | vertical, beginner |
| 5 | P2 | Tutorial never teaches LT/RT (W/R), LAST TURN, the new words | vertical |
| 6 | P2 | A satellite's own wheel (slice, tier) is never shown | vertical |
| 7 | P2 | Subtitle paging breaks on text without spaces and on translated (pseudolocalised) text | horizontal |
| 8 | P2 | Stickers, SEND IT key, aim quality and aiming carry meaning in words only | non-English, beginner |
| 9 | P3 | Raid setup: BREACHED stamp before the raid runs vs HOLDS; legend covers CORE; defence cards cut and costs unreadable at 1.6; legend and mini-map labels don't scale | vertical, both naive |
| 10 | P3 | MORE BELOW covers buttons; second crew Loadout not pad-reachable; HQ shows one dossier at 1.6 | vertical, beginner |
| 11 | P3 | Map labels ignore the screen edge and the Grid column; map labels skip TextDb; route button icons differ from the map's | horizontal |
| 12 | P3 | Event rescue tooltip names the wrong class; heal / Heat shown uncapped | horizontal |
| 13 | P3 | Odds chips abbreviated; satellite chips BLK/SHD; LAST TURN line overflows at 1.6; keyboard aim order not screen order; ring toggle on a wheel without a ring; combat Settings tooltip | vertical, horizontal |
| 14 | P3 | Top-bar tags go icon-only at 1.6 on some screens; route view has no legend; Grid list and HQ JACK IN / crew buttons word-only; no tier difficulty cue | beginner, non-English |

### H21 (fixed 2026-09-27): pass 21 = vertical + horizontal audits and the first naive-player reviews

Reviewers: a vertical and a horizontal auditor, a first-time player and a player who
can't read English (the last two judged `tools/playtest/storyboard.tscn` screenshots;
`--scramble` turns interface text into asterisks). Preview == result held over 112 fights;
card aiming held for 71 cards x 8 classes x 5 corporations.

| # | Sev | Gap | Source |
|---|---|---|---|
| 1 | P1 | Pad can't pick the nudge wheel or ring (the pickers went with H20) | vertical, horizontal |
| 2 | P1 | First pad press after the mouse drops focus (hand rebuilt on hints_changed) | vertical |
| 3 | P1 | Nothing shows what SEND IT did (preview for next turn replaces it at once) | beginner, non-English |
| 4 | P2 | Random resolve picks (DOSE, Citations, Solar Flares) preview the exact slot | vertical, horizontal |
| 5 | P2 | Preview after a reshuffling card uses the wrong RNG (preview != result) | horizontal |
| 6 | P2 | HITS chip counts one hit per attack, not per pointer (multi-pointer targets) | horizontal |
| 7 | P2 | Nudge cards / Undock on a satellite only go one way by mouse | vertical, horizontal |
| 8 | P2 | Tags run over the status line / off the view at 1.3+; toast covers HP arcs | vertical |
| 9 | P2 | Cards say what they do in words only; tags use abbreviations (DEF, AFL, BLK, CRPT) | beginner, non-English |
| 10 | P2 | Top-bar stats have no icons; CELL STATUS icons unlabelled | beginner, non-English |
| 11 | P2 | Subtitles in the top band hide the stats (money in the Modem) | beginner, non-English |
| 12 | P2 | Modem card prices sit in the RAM-cost circle; raw "crit_12" in the socket list; no wallet | beginner, non-English |
| 13 | P2 | Event choices and menus carry meaning in words only (no outcome icons, no menu icons) | non-English |
| 14 | P2 | Route choices identical ("Router"), no "you are here", tiny similar node icons; map nodes have no tooltips | beginner, non-English, vertical |
| 15 | P2 | Big text reaches menus but not crew cards, shop / loot / deck cards, stat tags, map labels; Grid side column and HQ notes overflow | beginner, horizontal |
| 16 | P3 | Modem / Loadout spinners run the slot order the other way round to combat | vertical |
| 17 | P3 | Missing chips: boss phase / new needles, 2x nudge next turn, satellite block / heal / statuses / moves | vertical |
| 18 | P3 | Inner-ring ghost arc not drawn; tag title clipped at 1.6 | vertical |
| 19 | P3 | Content text bypasses TextDb in new HQ code and hub names | horizontal |
| 20 | P3 | Retired keybinds kept from old settings files; Heat chip scaled on the total | horizontal |
| 21 | P3 | HQ / Grid naming: JACK IN vs Launch netrun; raw corporation id on the title | beginner |
| 22 | P3 | Halcyon's Sites lie mostly outside its district, so raid sway barely tints its Grid | horizontal |

### H20 (fixed 2026-09-26): vertical + horizontal re-review after the merge, with the pass-20 items

Pass-20 P1 (netrun fight cut off at 1.3+) is **fixed** by the merged layout (cards and SEND
IT fully visible at 1.0/1.3/1.6, system log on or off); a height test is still to add.
Pass-20 P2 (preview hid results) is **worse** (item 1); pass-20 P2 pad keys (item 8) and
P3 stale hints (item 16) stand.

| # | Sev | Gap | Evidence |
|---|---|---|---|
| 1 | P1 | The resolve outcome is mostly hidden: intent tags show slice, base output, tier, net HP and block only; statuses, RAM, resistance, shield, evade, deploy, heal, bodyguard, retrigger, corrupted, deaths, Burner's Heat (unscaled "MODIFY_HEAT") and enemy satellites' own pointers show nowhere (GDD 2.10 "full outcome") | combat_scene.gd `_set_intents`; preview_note hidden |
| 2 | P1 | Card-hover results and respin odds go only to the hidden preview note (M5 "odds for random effects" fails) | `_show_card_preview`, `_show_respin_odds` |
| 3 | P1 | Cards that need a chosen slice (Spawn Drone in Botnet/Hivemind decks, Cleanse, Encrypt, Armor Plate, Hot Patch, Sanitize) can't be aimed by mouse or pad; F cycles an invisible picker (M12 pad box fails) | `_slot_option` in hidden controls_row; no pad bind for cycle_slot |
| 4 | P1 | Refused actions fail silently ("Not enough RAM...", resistance blocks) | `_on_action_refused` writes to hidden notes |
| 5 | P1 | The current target isn't drawn (Tab can move it to a satellite unseen) (GDD 9.2 explicit targeting) | `WheelView.highlighted` never drawn |
| 6 | P2 | Combat subtitle dock covers the intent tags and the status line (standalone 1.0/1.6; netrun at 1.6 and with the system log on) | SUBTITLE_DOCK fixed at y 58; test checks wheels only |
| 7 | P2 | The bottom subtitle bar hides controls: raid setup asset cards, LEAVE THE MODEM, HQ Loadout buttons, Grid rows, Options Close/Assist at 1.6 | Dialogue.dock_bottom 200-1080 x 578/628-700 |
| 8 | P2 | Pad players see keyboard keys only (stickers, SEND IT, tutorial, HQ; "Right-click a slice") | Settings.key_text |
| 9 | P2 | Pad focus escapes the Modem modals (DeckView, SpinnerView, LoadoutView, DaemonTray): A can buy behind them | netrun_scene.gd `_open_modal` |
| 10 | P2 | Raid setup target node is mouse-only (pad can deploy to the default node only) | hq_scene raid setup |
| 11 | P2 | Text scale doesn't reach card text (11 px), intent tags (15), hub lines (10), SEND IT and stamp hints (GDD 9.6) | zine_card.gd, wheel_view.gd, drip_button.gd, zine_stamp.gd |
| 12 | P2 | Tutorial describes the old UI (preview strip, hover preview, no stickers/tags); its rect runs 12 px past the screen in a netrun | tutorial_overlay.gd steps 0/3/5 |
| 13 | P2 | Modem "UPGRADE A SLICE" shows slot 0's price; the Miss slot costs 150, not 100 | netrun_scene.gd:757, netrun_session.gd:770 |
| 14 | P2 | REBEL_CELL's colour (#FF2A6D) is nearly the Cell pink: claimed vs corporate Sites, legend rows, enemy vs player wheels differ by colour alone (GDD 9.6) | city_layout.gd, map_legend.gd, wheel_view.gd |
| 15 | P2 | New kit behaviour untested (CityLayout, CityMapOverlay site clicks, MapLegend live toggle, SpinnerView/DeckView pick flows, LoadoutView, DaemonTray, CrewCard orders) | no test references |
| 16 | P3 | Rebind hints stale outside combat (HQ Settings/Options, tutorial); hard-coded "[Esc]" (Resume, Close x3); ZineStamp always draws "[SPACE]" (JACK IN does nothing on Space; result stamps take focus with no handler) | hq_scene.gd:468,560; zine_stamp.gd:35 |
| 17 | P3 | Hints use physical key names, the Controls grid the layout's: may disagree on AZERTY (code-verified only) | settings.gd key_text vs settings_panel.gd |
| 18 | P3 | Wide intent tags (4-pointer boss) run under the side column | wheel_view.gd intent tag |
| 19 | P3 | `layout_violations` uses r+22, missing value labels (r+36), satellite labels and the HP arc (r+66) | wheel_view.gd wheel_rect |
| 20 | P3 | Five cards' text is cut at 5 lines in the hand; pad inspect on a card shows nothing | zine_card.gd, combat_scene inspect_at |
| 21 | P3 | Raw ids on screen: raid labels ("home", "m_home"), crew stamps "ON <SITE_ID>", NODE ORDERS rows | hq_scene.gd:607,961,974,1038 |
| 22 | P3 | Raid setup/playout maps have no legend; HQ Grid legend height not live; mid-run raid playout still uses the old GridMapView | hq_scene.gd:760, netrun_scene.gd:451 |
| 23 | P3 | Portraits keyed by class (every Breaker the same face); combat caption is the class name; wanted poster silhouette; VIEW LOADOUT / Daemon tray show the first operative only; loadout spinner omits hub and inner ring | portrait_art, hq_scene.gd:1217-1245 |
| 24 | P3 | Code leftovers: `corp_creep = heat / 100.0` (not heat_max); ModemSign "SELL" note and hard-coded pink; unused kit classes (RaidBoardView, DripLabel, NeonSign, NeonTag, ScreenHeader); HP arc literal colour | combat_scene.gd:882, modem_sign.gd, wheel_view.gd:259 |
| 25 | P3 | Docs drift: STYLE_GUIDE §4 (log strip, circular SEND IT) and §7 (placeholder portraits); `--demo-*` slot shares profile.json | STYLE_GUIDE.md, netrun/hq demo hooks |

Latent, not counted: two main enemies would push the hand 126 px off screen (no shipped
fight has two). Out of scope: Fx.heat_pulse unused (motion handoff 4.6); fx.gd / NeonCity
inline animation values await the motion config (handoff §3).

### Pass 3 (vertical) — clean

Re-checked every GDD section against the code and the simulator after batch 5:
every rule has a code path and a test (355 tests), every screen follows the three-worlds
rule, the Grid and netrun maps are interactive, and a bot completes ICE 0 and ICE 5
campaigns within GDD 11.8 pacing (see DECISIONS.md, batch 5). What remains outside code
is listed under "Out of reach for code" in §2 and needs people (art, music, voice,
translation, a human performance run and playtests).

---

## 1. Where the project stands (horizontal pass 1, after M12)

| Layer | Built |
|---|---|
| Combat | Full effect language, preview, rewind, replay, statuses incl. PARASITE, Firmware, Daemons, ring segments, drones, boss phases, ICE/Heat modifiers, freeze cooldown, assist free nudges |
| Classes | Breaker, Ghost, Rigger, Botnet + Wrecker, Phantom, Overclocker, Hivemind; cores and Mk2 cores, rings, two exclusives each, station bonuses, barks, unlocks |
| Corporations | Solace, Meridian, Halcyon, Orbital (32 Sites, 6 enemies, 2 elites, mini-boss, phased boss, 3 Exploits, 6 story paths, own raids, voice, colour, raid music) and REBEL_CELL built from the profile |
| Campaign | Corporation and class selection, per-corporation ICE ladders and records, 7 node types, 5 home servers, raids with station bonuses and built-in holds, assist mode, share codes, daily run |
| Content | 60 shared cards, 18 Firmware, 24 Daemons, 8 assets, 12 shop slices, events: Solace 40, others 28 rollable each |
| Tooling | Balance simulator per class and corporation drafting by measured value; content generators in `tools/content_gen/` |

Tests: 700 passing at H23 (667 at H22); schema smoke test and content validation green.

---

## 2. Gaps in the vertical slice (pass 2)

| # | Gap | Sev | Notes |
|---|---|---|---|
| V1 | `CampaignRules.launch_error` and `RunManager.launch_error` gate Rank with the default class, not the operative's class | A (latent bug) | Wrong the moment a second class exists. |
| V2 | Clicking a Site on the Grid view does nothing (`site_clicked` has no listener) | B | The text list works; the map should select and act. |
| V3 | Netrun reward, event, shop and end panels are plain button lists | B | STYLE_GUIDE: "anything the Cell touches gets zined"; cards should be stickers everywhere. |
| V4 | No automated check of GDD 11.8 pacing (runs to win, Heat peak) | B | Needed before balance can be discussed; a seeded bot campaign is enough. |
| V5 | `MILESTONES.md` stops at M4; the vertical-fix work has no acceptance record | C | Add M5 "Vertical completion". |

**Out of reach for code (needs people; tracked, not counted as open):** final art
(portraits, holograms, Grid buildings, zine textures), composed music and recorded SFX,
voice recording, translations into other languages, the 1080p mid-range PC performance
run (the fps counter is in place), human playtests.

---

## 3. What "100 hours to full content" implies (decided)

GDD 11.8: average campaign ≈ 6 h 35 m, fast ≈ 2 h 15 m.

| Lever | Decision (DECISIONS.md) |
|---|---|
| Corporations | 4 + REBEL_CELL: Solace Biosystems, Meridian Freight Systems, Halcyon Civic, Orbital Commons |
| ICE progression | A win at ICE *n* unlocks up to *n + 3* on that corporation; any corporation starts at global best − 5; fresh profiles pick 0–3 |
| Classes | Breaker, Ghost, Rigger, Botnet + one alternative each |
| Content per corporation | 30–40 Sites, 6 normal + 2 elite + 1 mini-boss + 1 boss, 3 Exploits, 6 story paths, ~30 rollable events (own + shared; Solace has 40), 8 raid templates, own voice sets |
| Pools | ~60 shared cards + 2 exclusives per class, ~18 Firmware, ~24 Daemons, ~8 assets |

≈ 19 campaigns to full content ≈ 120 h average / 45 h fast.

---

## 4. Horizontal slices, prioritised

P0 = systems the finished game needs; P1 = content volume for 100 hours; P2 = polish.

### P0
1. ~~**Recruitment by class** and the class unlock purchase (80 Schematics); the roster
   chooses among unlocked classes.~~ Done in M6.
2. ~~**Botnet drones persisting between combats** in a run (Hub passive).~~ Done in M6.
3. ~~**Corporation selection** at campaign start (profile-unlocked corporations).~~ Done in M8.
4. ~~**Balance simulation** grows into a tuning tool (per ICE, per class, per corporation).~~
   Done: `class=<id>` (M6), `corp=<id>` (M8), measured drafting (M7).

### P1
5. ~~**Classes**: Ghost, Rigger, Botnet (wheels, Hub Cores + Mk2, rings, exclusive cards,
   station bonuses, barks), then four alternatives.~~ Done in M6.
6. ~~**Pools**: shared cards to ~60, Firmware to ~18, Daemons to ~24, assets to ~8, shop
   slices to ~12.~~ Done in M7.
7. ~~**Solace depth**: events to ~40.~~ Done in M7.
8. ~~**Meridian Freight Systems** (done in M8), **Halcyon Civic** (done in M9), **Orbital Commons**~~ (done in M10): grid, enemy
   family, mini-boss, boss with phases, Exploits, threats, raids, story paths, events,
   voice sets, music context, corporation colour.
9. ~~**REBEL_CELL**: generator from the profile, own ICE ladder, DISPATCH reveal, finale,
   "final final".~~ Done in M11.
10. ~~**More home-server variants**~~ (done in M12) and skins (deferred to art, M13).

### P2
11. ~~Controller support.~~ 12. ~~Daily seed / challenge runs and replay sharing.~~
13. ~~Assist options~~ (done in M12: extra free nudge and HP; previews are always on). 14. Art, audio, voice and translation integration
as assets arrive.

---

## 5. Milestones after M4

| Milestone | Scope |
|---|---|
| M5 Vertical completion | Passes 1–2 (§2) |
| M6 Class roster | P0 1–2, P1 5 |
| M7 Pools and Solace depth | P1 6–7 |
| M8–M10 Corporations 2–4 | P0 3, P1 8 |
| M11 REBEL_CELL | P1 9 |
| M12 Polish and reach | P1 10, P2 |
| M13 Art/audio/voice integration, M14 balance and release | Needs people |
