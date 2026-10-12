P1 4 / P2 17 / P3 23 (L28–L65 plus Pack B findings L78–L83; every axis of the matrix reviewed)

# M14 ART-12 12q: QA matrix audit (vertical)

Tree: `qa12q` = db29f599 (main + M14 close-out fixes). Harness: `tools/visual_qa/capture_pack.py`, one window, pillow filters.

Coverage
- Pack A (`%TEMP%/qa12q/matrix`, this auditor): text 1.0 / 1.6 × mouse / pad × reduce effects off / on × none / grey / deutan:
  24 combos, 2208 pictures, 0 not captured, manifest `skipped: []`. Sheets: `docs/art_review/ART-12/12q/sheets_a/`
  (`screen_<screen>.jpg` = rows text scale, columns input × RE; `combo_<combo>.jpg` = every screen of one combo).
  Lint: `docs/art_review/ART-12/12q/lint_report_a.md`.
- Pack B (`%TEMP%/qa12q/matrix_b`, helper agent): 2.0 mouse / pad × RE off / on were captured (92/92 each) and read
  from raw frames; my interim sheets are `docs/art_review/ART-12/12q/sheets_auditor/s20_NN.jpg` (2.0 mouse RE off,
  capture order, 6 per sheet) and `pad20_00.jpg` (2.0 pad). Pack B's own sheets / lint, and the high contrast,
  reduce motion and colour-blind (deutan setting) combos at 1.0 and 2.0: see "Pack B findings" at the end.
- Godot logs: 0 ERROR / SCRIPT ERROR / WARNING lines in the 8 pack-A runs. No failed, crashed or skipped screen.
- Compared against the parity sheets (`docs/art_review/PARITY/<screen>.jpg`) for the look; findings below are
  layout / accessibility defects only.

s20 index (2.0 mouse RE off): 00 title…new_campaign · 01 new_campaign_picker…hq_black_market · 02 hq_crew…hq_pause_options ·
03 hq_heat_band, b4_idle…b4_upgrade · 04 b4_heat…grid_site_selected · 05 grid_raid_pending…grid_orbital ·
06 grid_rebel_cell, raid_setup…raid_playout · 07 raid_result…route_hover_all · 08 route_mid…combat_start ·
09 combat_hover…combat_boss_p2 · 10 combat_boss_p3…mainframe · 11 mainframe_socket…codex · 12 codex_corps…run_end_clean ·
13 campaign_won…tutorial · 14 jack_in…pause_fight_abandon_hold.

## Findings

- P1 codex, codex_corps, hq_pause_codex 1.6 / 2.0 mouse+pad: the tab strip shows SLICES…CARDS (5 of 13 tabs) at 1.6 and 4 at 2.0; FIRMWARE, DAEMONS, RING SEGMENTS, ENEMIES, NODES, HOME SERVERS, DEFENSE ASSETS, THREATS, LEXICON run off the panel edge with no wrap, scroll or MORE cue, so a mouse player cannot reach them — tabs wrap to a second row (as at 1.0) or page with a visible cue — sheets_a/screen_codex.jpg, screen_codex_corps.jpg, screen_hq_pause_codex.jpg; sheets_auditor/s20_11.jpg, s20_12.jpg, s20_02.jpg
- P1 raid_report, raid_report_meridian 1.6 / 2.0: the BACK TO THE GRID sticker is half below the bottom edge (only its top shows) and the paper's letterhead sits under the two-row HUD; at 2.0 the OPERATION line is also under the HUD — the exit is fully on screen and the paper starts below the HUD — sheets_a/screen_raid_report.jpg, screen_raid_report_meridian.jpg; sheets_auditor/s20_07.jpg
- P1 hq_black_market, b4_market 1.6 / 2.0: the MARKET hand's boosts row is cut at the right (OVERCLOCK → "OVERCLO", "15 SCHEM" → "15 SC") and the further offers (field kit, profile unlocks) are gone; at 1.0 the PROFILE UNLOCKS block is already masked at x≈395 ("CORPORA", "80 SCHEMATI") — every offer reachable (row scrolls or pages) — sheets_a/screen_hq_black_market.jpg, screen_b4_market.jpg; sheets_auditor/s20_01.jpg, s20_04.jpg
- P1 b4_claim 2.0 (and 1.6 partly): the CLAIM terminal's "PICK THE NODE TO BUILD" choices (COMPILER RACK / FIREWALL RELAY) are cut to their top half and the RUNNER line is drawn over by the map's red raid arrows; the player cannot read what they build — the build choices whole and above the map marks — sheets_a/screen_b4_claim.jpg; sheets_auditor/s20_03.jpg
- P2 b4_core, b4_repair, b4_upgrade, grid_influence 1.6 / 2.0: the node terminal is cut after LINKS (STATIONED, HQ ACTIONS, HEAT SCRUB, PATROL IT INSTEAD gone); at 2.0 it is cut after INTEGRITY — every row and action of the node card reachable — sheets_a/screen_b4_core.jpg, screen_b4_repair.jpg, screen_b4_upgrade.jpg, screen_grid_influence.jpg; sheets_auditor/s20_03.jpg, s20_05.jpg
- P2 hq, hq_crew, hq_heat_band, grid, grid_* (all corps), b4_idle/heat/market/crew 2.0: the site card shows only its title (cut: "CONTINUUM BILLING FAR", "ADHERENCE MONITORING") and the TYPE row; LINK, IF CLEARED and CAN BE YOUR NODE are gone — the card grows or pages so its rows stay — sheets_auditor/s20_01.jpg … s20_06.jpg
- P2 grid_site_selected 1.6 / 2.0: the Exploit card's explanation is cut mid-sentence ("…JACK IN shows here." loses "here." at 1.6; at 2.0 it ends at "a Site linked to it") — whole text — sheets_a/screen_grid_site_selected.jpg; sheets_auditor/s20_04.jpg
- P2 hq_loadout_spinner 1.0 / 1.6 / 2.0: the attach column truncates its labels ("Accelera" at 1.0; "Class defau / Corru / Ancho / Accel" at 1.6; "Clas defa / Corr / Anch / Acce" at 2.0) and at 1.6 / 2.0 the modal's bottom (the HP gauge, Close [Esc]) is below the screen edge — labels whole, Close on screen — sheets_a/screen_hq_loadout_spinner.jpg; sheets_auditor/s20_02.jpg, pad20_00.jpg
- P2 raid_playout 1.0 / 1.6 / 2.0: a START DEFENSE sticker is drawn during the playout, over the LIVE RAID FEED lines at 1.6 / 2.0 ("Step / CORE:" hidden) — no setup control during the playout, feed readable — sheets_a/screen_raid_playout.jpg; sheets_auditor/s20_06.jpg
- P2 mainframe, mainframe_socket 1.6 / 2.0: the slice wheel (the c100 slots) is pushed below the bottom edge, only its top arc shows; the clerk panel is cut to "MIRROR FLIP Flip a wheel. Blocked while…" — the wheel's slots on screen — sheets_a/screen_mainframe.jpg, screen_mainframe_socket.jpg; sheets_auditor/s20_10.jpg, s20_11.jpg
- P2 raid_setup, raid_setup_meridian, raid_setup_page2, raid_drag_asset, b4_defence 2.0: the dossier paper and the THREAT INTEL holo do not follow text scale (lint: raid_paper.gd font 228, raid_holo.gd font 60), so their text is the smallest on screen at 2.0 and THREAT INTEL drops the routes ("COLLECTOR" only, rest behind MORE) — text scale reaches the paper and the holo — sheets_auditor/s20_06.jpg, s20_04.jpg, pad20_00.jpg
- P2 tutorial 1.0 / 1.6 / 2.0: the tutorial note's text is clipped with no scroll (lint: "11 of 12 lines visible" at 1.0, "6 of 7" at 1.6); at 2.0 the page reads "More on the next" — every line of every page visible — sheets_a/screen_tutorial.jpg; sheets_auditor/s20_13.jpg
- P2 combat_victory, combat_defeat 1.0 / 1.6 / 2.0: the operative's line ends in an ellipsis ("Perfect. Tell the board the …", "Bricked. Tell the Cell it …"; lint dialogue.gd clipped) — the whole line — sheets_a/screen_combat_victory.jpg, screen_combat_defeat.jpg; sheets_auditor/s20_10.jpg
- P2 campaign_won, campaign_lost 1.0 / 1.6 / 2.0: the DISPATCH line ends in "…" at every scale (lint terminal_note.gd clipped) — the dispatch wraps or ticks through — sheets_a/screen_campaign_won.jpg, screen_campaign_lost.jpg; sheets_auditor/s20_13.jpg
- P2 slots, slots_2, slots_3 2.0 (1.6 for slots_3): the panel shows one slot; at 2.0 the folder's slot tab and corporation name are gone and LOAD reads "LOA"; slots_3 shows only slot 3 with no MORE ABOVE cue — slot name and LOAD whole, a cue for hidden slots — sheets_a/screen_slots_3.jpg; sheets_auditor/s20_00.jpg
- P2 b4_heat 1.0 / 1.6 / 2.0: the Heat terminal covers the crew polaroids and the MARKET tab, and the map's red raid arrows are drawn over its "60 complication // 70" line — terminal above the map marks, crew tabs clear — sheets_a/screen_b4_heat.jpg; sheets_auditor/s20_04.jpg, pad20_00.jpg
- P2 daemon_tray 1.0 / 1.6 / 2.0: the BREAKER 1 chip and the CASCADE daemon card sit over the ROUTE panel (GRID VIEW / Save & quit hidden) — the tray beside the route panel — sheets_a/screen_daemon_tray.jpg; sheets_auditor/s20_13.jpg
- P2 grid_raid_pending, raid_setup, b4_idle, b4_defence deutan (pillow, 1.0 / 1.6): the raid route (red) and the Cell's network (lime) both read yellow, and the THREAT INTEL card's A/B markers lose their red; the threat path keeps its arrow head but "hostile vs ours" is carried by colour — a pattern / shape cue for the hostile path (dashes, hazard ticks) — sheets_auditor/filt2_00.jpg, filt_00.jpg; sheets_a/combo_1.0_mouse_re-off_deutan.jpg
- P2 grid_drag_crew 1.0 / 1.6 / 2.0: no carried operative is visible in the capture (the state's subject) — the polaroid under the pointer on its way to JACK IN, as in PARITY/grid_drag_crew.jpg — sheets_a/screen_grid_drag_crew.jpg
- P3 title, title_confirm, slots*, codex, codex_corps, options, loot, loot_firmware, tutorial all scales: the SAVED toast sits on the bottom-right hint ("back", the ON AIR ticker, CONTINUE on loot, VIEW LOADOUT on loot_firmware 2.0) — the toast clear of hints and actions — sheets_a/screen_title.jpg, screen_codex.jpg, screen_loot.jpg; sheets_auditor/s20_00.jpg, s20_10.jpg
- P3 event_dispatch 1.6 / 2.0: the "VOICE ONLY // NO FEE" chip is cut — whole chip — sheets_a/screen_event_dispatch.jpg; sheets_auditor/s20_11.jpg
- P3 b4_idle 1.6 / 2.0: the INTERCEPTED corp toast covers the polaroid names and the dossier sits under RAID SETUP — toast clear of the crew — sheets_a/screen_b4_idle.jpg; sheets_auditor/s20_03.jpg
- P3 combat_hover 1.6 / 2.0: the hovered card's zoom covers the player's HP readout — HP readable while hovering — sheets_a/screen_combat_hover.jpg; sheets_auditor/s20_09.jpg
- P3 raid_playout, raid_result, raid_report, raid_interlude, campaign_won 1.6 / 2.0: the HUD's stat chips wrap to two rows and push the page down (the cause of the raid_report P1) — one row, as BIG-TEXT b did for YOUR NETWORK — sheets_a/screen_raid_result.jpg; sheets_auditor/s20_07.jpg
- P3 campaign_lost RE off, all scales: at the harness's settle the screen is the full-frame glitch with only the DISPATCH line and CELL DEFENSE stamp; the lost-campaign content is unreadable (RE on shows the end state) — confirm the glitch resolves to the page within a few seconds — sheets_a/screen_campaign_lost.jpg; sheets_auditor/s20_13.jpg
- P3 hq, hq_crew, grid* 1.6 / 2.0: the site card overlaps the third and fourth polaroids (hq_crew "W…" cut) — the crew row clear of the card — sheets_a/screen_hq_crew.jpg; sheets_auditor/s20_02.jpg
- P3 route, route_*, daemon_tray, run_end, run_end_clean 1.6 / 2.0: the route key strip and the run-end title chips stay at 1.0 size (lint route_legend.gd font 160) — key strip follows text scale — sheets_a/screen_route.jpg; sheets_auditor/s20_08.jpg
- P3 hq_pause, pause_netrun, pause_fight 1.6 / 2.0: the pencil taglines truncate ("No Going Bac", "Come Back So") at 1.6 and are dropped at 2.0; the PAUSED header wraps — taglines whole or knowingly dropped at every large scale — sheets_a/screen_pause_fight.jpg; sheets_auditor/s20_14.jpg
- P3 options, options_glitch, hq_pause_options all scales: the focus bracket's top-left corner is drawn over the "EFFECTS & MOTION" section label — bracket inside the row — sheets_a/screen_options.jpg
- P3 title, slots, slots_2, slots_3, title_confirm pad 1.0 / 1.6 / 2.0: the pad capture is pixel-identical to the mouse capture (mean diff 0.0); the only focus cue is the BREACH / LOAD sticker sheen, which also shows with the mouse, so pad focus is not distinguishable — a focus ring / bracket on the focused control — sheets_auditor/padfocus_00.jpg; sheets_a/screen_title.jpg
- P3 raid_incoming RE on 1.0 / 1.6: the "A raid is queued" Heat note covers the raid panel's title — note clear of the panel — sheets_a/screen_raid_incoming.jpg
- P3 raid_interlude, raid_incoming, run_end, run_end_clean, campaign_won all scales: panel header text is flush against the left border ("RAID // COLLECTIONS" loses the R; "NETRUN FAILED" touches the frame) — the kit's header inset — sheets_a/screen_raid_interlude.jpg; sheets_auditor/s20_07.jpg
- P3 b4_claim, raid_setup_meridian 1.0: dossier letterhead ends in an ellipsis ("SOLACE BIOSYSTE…", "MERIDIAN FREIGHT SYS…") — whole name — sheets_a/screen_b4_claim.jpg, screen_raid_setup_meridian.jpg
- P3 combat_victory 1.0: the operative speech box covers the "OURS NOW" scrawl — scrawl clear of the box — sheets_a/screen_combat_victory.jpg
- P3 new_campaign_codes 2.0: the share-code field shows "RC1-corporation-ice-s" (placeholder cut) — whole placeholder or a shorter one — sheets_auditor/s20_01.jpg
- P3 mainframe_remove 2.0: the card row is cut at the cards' middle (bottom half hidden) — whole cards with a scroll — sheets_auditor/s20_11.jpg
- P3 hq, grid*, b4_*, raid_*, route*, jack_in, pause_netrun (44 screens) all combos: harness warning "waited 20 s for the city bake; not ready (old look)" — these frames show the city's pre-bake look; the bake should land inside the harness wait or the wait should be longer — pack manifest `warnings`
- P3 lint (horizontal leads, not separately ranked): contrast below 4.5:1 in raid_paper.gd 137, fx.gd 133, case_file_card.gd 106, value_stepper.gd 32; font-size overrides off the §4.2 scale in fx.gd 320, combat_scene.gd 180, terminal_window.gd 88 — see lint_report_a.md "Findings per owning script" — docs/art_review/ART-12/12q/lint_report_a.md

## Reduce effects
RE on is an end state on every pack-A screen compared (largest RE off/on differences: raid_result / raid_playout jump to the
report, campaign_lost shows its end page, title / hq / jack_in drop scanlines and glitch). No RE-on frame showed a
half-finished animation. sheets_a/screen_raid_result.jpg, sheets_auditor/re16_00.jpg.

## Pack B findings
Pack B root a: 2.0 × mouse / pad × RE off / on × none / grey / deutan, 1104 entries; root b: hc / rm / cb-deutan at 1.0 and 2.0
(mouse, RE off), 552 entries. Both manifests: 0 not ok, skipped []. Sheets: `docs/art_review/ART-12/12q/sheets_b/` (root b);
lint: `lint_report_b.md` (root a, 2.0), `lint_report_b2.md` (root b, settings). Reduce motion: an end state everywhere (hq,
title, raid_playout, jack_in drop the camera and parallax moves; nothing else changes). Root a's 2.0 lint clipped / overlap
lines are all dup of L39 (tutorial), L40 (combat line), L41 (dispatch), L47 (SAVED toast), L29 (raid_report_meridian paper).
- P2 combat_*, hq*, grid*, b4_*, raid_*, route* hc 1.0 / 2.0: high contrast leaves these screens almost unchanged (mean pixel difference vs off 0.2–2 of 255; combat identical): card rules text, LAST TURN captions and slice labels stay thin on the busy city, panels stay translucent; only the pause / confirm scrims and modals go opaque — the setting's own promise ("Opaque panels, 7:1 text and thick edges") on every screen — sheets_auditor/hccmp_00.jpg, hc10_00.jpg; sheets_b/screen_combat_after.jpg, screen_grid_site_selected.jpg
- P2 grid_raid_pending, raid_setup, b4_idle, b4_defence cb-deutan 1.0 / 2.0: the colour-blind mode (deutan) does not change the map; the raid route stays red against the lime network, and through a deutan simulation of the mode's own frames both still read yellow, so turning the mode on does not fix L45 — with the mode on, the hostile path gets a pattern or glyph cue ("Patterns and glyphs stay the main cue") — sheets_auditor/cb_00.jpg (columns: off, mode on, mode on seen as deutan); sheets_b/screen_grid_raid_pending.jpg, screen_raid_setup.jpg
- P3 run_end, run_end_clean hc 1.0 / 2.0: the SAVED toast is 1.08–1.11:1 on the dark page (invisible) — readable or not shown — lint_report_b2.md (fx.gd contrast)
- P3 tutorial hc 1.0 / 2.0: the tutorial's "Next" measures 4.42:1, under the 7:1 high contrast promises — 7:1 — lint_report_b2.md (tutorial_overlay.gd contrast)
- P3 raid_result, raid_result_meridian 2.0: two "-5" Heat flight labels are stacked on the same spot (65×121 px overlap) — one number — lint_report_b.md (flight_fx.gd overlap)
- P3 new_campaign*, options*, hq_pause_options, route*, raid_result*, raid_report* hc (lint lead): the filled cyan selected buttons (Daily run, RESET ALL TABS, GRID VIEW, VIEW LOADOUT, MAP KEY) declare white on cyan at 2.1–2.6:1 (measured 7.5–9.3:1, low confidence); hc doubles the contrast findings vs off (168 vs 74 at 1.0) — confirm the drawn colours; if the fill is that cyan the label fails 7:1 — lint_report_b2.md (crt_window.gd, terminal_window.gd, hud_bar.gd, map_legend.gd contrast)
