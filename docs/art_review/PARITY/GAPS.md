# M14 parity audit: art pass vs main (GAPS)

Status: **COMPLETE** (2026-10-05): every screen and state of both review packs, the HQ run pages, the Central Server gate, the combat backdrops, the campaign end lock and dossier, and 10 motion strips are compared. 134 entries covering 136 difference ids (entries by rank: P1 44, P2 59, P3 31); 23 ruled by the designer so far (their `Decision:` filled), the rest wait for a ruling.

Designer rulings this file follows (DECISIONS 2026-10-05 "the M14 audit is a side-by-side art-pass
parity audit", and the orchestrator's relay of the later ruling): every difference is described
neutrally, both sides; where it helps, an honest view of which reads better and why; **nothing is
fixed until the designer has ruled** on each id (`Decision:` empty until then).

## The designer's general principle (2026-10-05)
Where the M13 art-pass build is **richer than main** (more layout, content or information) but
**predates the v2 concepts**, take the build's layout and content and **rework it in the v2 concept
language** (the v2 kit: terminal panels, vinyl stickers, paper for intercepted documents, the locked
palette and type). Neither "copy the build" nor "keep main's plainer version": the build's structure,
the concept's look. First applied to the campaign slots (SLOTS-01/02); the same pattern is the
natural default for the build-richer pages flagged below (new campaign pickers NEWC-01 (ruled), codex CODEX-01, stats STATS-01, pause rows PAUSE-02, loot / shop / deck card faces), each
still awaiting its own ruling.

## How to read this

- Per screen: `<screen>.jpg` = the full pictures side by side, references on the left, main on the
  right, every difference's rectangle marked with its id. Per difference: `<ID>.jpg` = the same
  rectangle cut from every picture, side by side, so each id can be shown on its own.
- **Three kinds of reference**, labelled on every sheet:
  - **ART PASS BUILD**: the `art-pass` branch (head 9a62cec) run from a scratch copy. Its game code
    is the M13 art pass (`art-m13-final`); everything committed on the branch after that is concept
    rounds 31-43, images only (no code changed in scripts/, scenes/, shaders/, content/).
  - **CONCEPT**: the locked image from ART_BIBLE v2 Appendix A (tag `art-concepts-r43`,
    `docs/concepts/`), where one exists for the screen.
  - **MAIN**: main @ c1197dd (4A shop/loot/event/deck viewer included).
  Where the build and the concept disagree (often: main's ART-3 work already follows the concept
  and the build shows the older M13 look), both are shown and the entry says so.
- Capture conditions, both sides: 1280x720 layout, text scale 1.0, mouse, reduce effects off, no
  filter, 60 fps fixed step, each project's own `tools/visual_qa/review_pack.gd` (same screen
  driver, seed 7 campaigns against Solace unless the screen says otherwise), settled frames.
  Art pass: 53 of 53 screens, 167 s; main: 60 of 60, 633 s; 0 errors either side.
- Rank: **P1** anyone would notice (layout, missing/wrong asset, wrong colour/material, wrong type,
  overlap); **P2** noticeable on a look (spacing, size, weight, line, glow, motion timing);
  **P3** pixel-level.

## Differences

### Title (`title.jpg`)
**Designer ruling (2026-10-05):** the title follows concept round 33 `title_screen.png`, except main's SIMULATE sticker stays (not the concept's DISABLE).
Refs: art pass build `title`; concept `round33_ui_chrome/title_screen.png` (LOCKED option A).
The build's title is the M13 menu (logo, pink CONTINUE bar, menu list, yellow note, UPLINK box);
main already follows the locked concept's layout (neon sign, BREACH / SIMULATE / OVERTHROW
stickers, terminal chips, MORE and PROFILE panels, ON AIR ticker). The build look is superseded by
the concept, so it is not listed as a gap item by item.

**TITLE-01 (P1) City backdrop.** Concept: the city behind the sign is the dense, lit, purple-toned
volumetric night city with a tilt-shift blur and the Halcyon ziggurat lit on the right; UI reads
over a dark, soft field. Build: a dark navy, filled isometric block city (no blur). Main: the 2D
`NeonCity` line-art city, unblurred, dimmed 0.58, saturated lime/green and cyan outlines.
View: main's backdrop competes with the stickers and the sign (lime outlines next to the lime focus
halo); the concept's blurred dark city keeps the UI legible and matches the 3D city used on the
Grid / raid / netrun. Likely cause: `scripts/ui/title_scene.gd` builds `CyberdeckBackground`
(`scripts/ui/kit/cyberdeck_background.gd`, 2D `NeonCity`) and `CITY_DIM`; the concept's city is
the unified `CityView3D` look. Fix options: (a) CityView3D at a fixed title camera + the
`glass_blur` shader as a depth-of-field band; (b) keep NeonCity but drop its saturation and add the
blur. Art-pass source: concept `round33_ui_chrome/title_screen.png` / `.gif`.
Decision: **concept 33** (the blurred, lit 3D city). (designer, 2026-10-05)

**TITLE-02 (P2) MORE panel crowds the verb stickers.** Concept: a clear gap (~40 px at 1080p,
~25 px at 720) between OVERTHROW and the MORE panel, MORE sits lower. Main: MORE's top edge almost
touches the OVERTHROW sticker. View: concept reads better (the three verbs are the hero group).
Likely cause: `title_scene.gd` `_place_bottom` / `FOOT_GAP` / `_align_verbs`. Fix: place MORE from
the foot up with the concept's gap, or nudge the verb column up.
Decision: **concept 33** (a clear gap from OVERTHROW to MORE). (designer, 2026-10-05)

**TITLE-03 (P3) CONTINUE summary line.** Concept: `slot 1 // Halcyon Civic // run 9 // Heat 58`
(slot named first). Main: `Solace Biosystems // run 1 // Heat 0` and a `>` caret on the focused
chip (the caret is the UI kit's focus rule). Fix if wanted: prefix the slot in
`title_scene.gd` `slot_words`. Decision: **keep main** (content only). (designer, 2026-10-05)

**TITLE-04 (P3) Version line.** Concept: `REBEL_CELL v0.33.0 // build <date> // godot 4.7`. Main:
`REBEL_CELL v0.9.0 // cell uplink`. Content only. Decision: **keep main** (content only). (designer, 2026-10-05)

### Title: delete-slot confirm (`title_confirm.jpg`)
Ref: concept `round33_ui_chrome/abandon_dialog.png` (the build has no such dialog; it is the same
kit dialog as main's pause-quit confirm).

**CONFIRM-01 (P2) Scrim.** Concept: the page behind is dimmed, still sharp. Main: blurred
(`GlassScrim`, `Palette.SCRIM_BLUR_PX`) and dimmed. View: both read; the blur hides the title sign
entirely, the concept keeps the context visible. Likely cause: `scripts/ui/kit/glass_scrim.gd`
(shared by every modal: changing it changes all modals). Decision: **keep main** (designer
2026-10-05): no PAUSED notification on the confirm (the concept's PAUSED sticker in this crop is
dropped); a PAUSED notification is wanted at most during a running raid (applies to PAUSE-01..04).
Main's blurred scrim stays.

**CONFIRM-02 (P3) Dialog body.** Same kit, same layout. Differences: main adds a divider rule above
the buttons (concept has one too, fainter and full width); main's question is set slightly larger;
main's stickers are centred as a pair, the concept's sit under the two cost columns. The verb is
DELETE (main) where the concept's run-abandon says BURN IT: different action, both fine.
Likely file: `scripts/ui/kit/confirm_dialog.gd`. Decision: **keep main** (designer 2026-10-05:
main is slightly better).

### Campaign slots (`slots.jpg`)
**Designer ruling (2026-10-05):** use the art-pass build's layout, reworked to the locked v2 concepts (the art pass never applied the latest concept to this page).
Ref: art pass build `slots` (no concept image for this page).

**SLOTS-01 (P1) Slot layout.** Build: three slot cards in a row inside one terminal panel; a used
slot is a paper dossier card (SLOT 1 tab, corp name in stencil, corp emblem disc, Heat bar, ICE,
runs, save date, two operative portrait chips); empty slots are dashed outlines with `EMPTY SLOT /
No campaign filed here yet.` Main: a vertical list in a tall terminal panel: `SLOT 1` heading, one
text line (`Solace Biosystems, Heat 33, ICE 0, 0 runs, active`), flat terminal buttons.
View: the build is clearly richer and reads at a glance (which corp, how hot, who is alive);
main's list is legible but plain. Likely cause: the build's `scripts/ui/kit/slot_picker.gd`
(`SlotPicker`) was never ported; main's `scripts/ui/title_scene.gd` `show_slots` builds rows.
Art-pass source: `art-m13-final:scripts/ui/kit/slot_picker.gd`, `title_scene.gd show_slots`.
Fix: port SlotPicker onto main's v2 kit (paper card = `PaperInk`/`ZinePanel`, terminal chips).
Decision: **build layout, reworked in the v2 kit**: the build's slot cards brought to main, restyled with the concept philosophy. (designer, 2026-10-05)
Fixed (S-TITLE, `CaseFileCard`; sheet `fixes/SLOTS.jpg`). Follow-up ruling (designer, 2026-10-05): used slots stay manila
folders, each with a sliver of paper poking out (the art pass's print stock); built, sheet `fixes/SLOTS_b.jpg`.

**SLOTS-02 (P2) Load / Delete.** Build: pink filled `Load` (primary) and a red-edged `Delete`.
Main: two equal terminal buttons, `Load` with the lime focus brackets. View: main follows the v2
rule (one sticker verb per screen, the rest terminal chips); the build's colour split marks the
destructive action more clearly. Same file as SLOTS-01. Decision: **build's Load / Delete, reworked with the concept** (v2 kit). (designer, 2026-10-05)
Fixed (S-TITLE): LOAD the pink sticker on the newest campaign, DELETE a HARM chip. Follow-up ruling (designer,
2026-10-05, overriding v2's one sticker verb per screen on this page): LOAD and DELETE are both stickers (DELETE = 4C's
baked `dialog_delete` art at LOAD's size), with a red grease-pencil "Can't Undo" and arrow pointing at DELETE (up to
text scale 1.6; at 2.0 the words move into DELETE's tooltip). Built, sheet `fixes/SLOTS_b.jpg`.

**SLOTS-03 (P3) Page title.** Build: the REBEL_CELL logo top left. Main: a `CAMPAIGN SLOTS` title
sticker (the v2 sticker-title rule, as THE GRID / RAID SETUP). View: main is consistent with v2.
Decision: **keep main** (the v2 page-title rule). (designer, 2026-10-05)

**SLOTS-04 (P2) Panel height.** Main's panel runs from y 160 to the ticker with the lower half
empty (hex-dump texture only); the build's panel wraps its content and shows the city below.
Likely cause: `title_scene.gd` `_page` / `SLOTS_W` (the page fills the height). Fix: size the
panel to its content. Decision: **size the panel to its content up to a maximum allocated size, then a scroll bar.** (designer, 2026-10-05)

### New campaign (`new_campaign.jpg`, `new_campaign_picker.jpg`)
**Designer ruling (2026-10-05):** the same principle as the slots: the build's layout reworked with the latest concept (v2 kit) into main.
Ref: art pass build `new_campaign`, `new_campaign_picker` (no concept image).

**NEWC-01 (P1) Pickers: tiles vs dropdowns.** Build: Target as five corp tiles (corp colour
stripe, corp emblem art, `Best ICE: n`, pink selected frame); ICE as a big `- 0 +` stepper; Home
server as tiles (house icon, lock badge, `UNLOCKS · cost`); Crew as portrait tiles (class portrait,
lock, unlock cost), all visible at once. Main: a form: `Target`, `Home server` and `Crew` are
`OptionButton` dropdowns, ICE a SpinBox with -/+; locked choices are not shown with their costs.
View: the build's tiles show what is locked and what it costs, and give each corp its colour; the
dropdowns hide all of that. Likely cause: the build's `scripts/ui/kit/tile_picker.gd` and
`planning_picker.gd` (`TilePicker`, `PlanningPicker`) were never ported; main's
`scripts/ui/hq_scene.gd` `show_start` (lines ~1239-1400) builds `OptionButton`s.
Art-pass source: `art-m13-final:scripts/ui/kit/tile_picker.gd`, `planning_picker.gd`,
`scripts/ui/hq_scene.gd` (corp tiles ~l.1233). Fix: port both pickers onto the v2 kit (corp
emblems from the art pass's own assets). Decision: **agree with the audit**: the build's tiles (corp / home server / crew, with locks and costs), reworked in the v2 kit. (designer, 2026-10-05)

**NEWC-02 (P2) Page header.** Build: the REBEL_CELL logo, a pink `TRUST NO ONE` pencil scrawl and
a pink START sticker top right with `SHARE CODES` beside it. Main: a `NEW CAMPAIGN` title sticker,
a yellow `TRUST NO ONE` pencil, the pink `New campaign` sticker under the form. View: main's title
sticker matches the v2 page-title rule; the build puts the one verb where the eye ends (top right).
Decision: **agree with the audit**: keep main's v2 title sticker; the start verb sticker goes top right as in the build. (designer, 2026-10-05)

**NEWC-03 (P2) Seed, daily run, share codes.** Build: seed lives in a collapsible SHARE CODES box
at the bottom (seed stepper, code field, copy); no daily run panel. Main: `City seed` field +
`Next seed` in the form, plus two lime-edged panels `TODAY'S RUN` and `SHARE CODES` side by side
under it. Main has more here (daily run is a main feature). View: main's lime panel edges are as
loud as the focus colour (lime = focus in the v2 kit), which competes with real focus.
Likely file: `hq_scene.gd show_start`. Decision: **main-only function, kept; restyle it with the concept approach** so it matches the rest of the final page (not lime panel edges). (designer, 2026-10-05)

**NEWC-04 (P1) Picker opened.** Build: "picker" is the tile row (no popup). Main: the target
OptionButton's popup list (Godot default popup restyled). Follows NEWC-01. Decision: **agree with the audit**: the tiles are the picker; no popup. (designer, 2026-10-05)

### HQ (`hq.jpg`)
**Designer ruling (2026-10-05):** HQ-01..10 are superseded by a dedicated HQ design pass. The art pass missed the HQ; it is reworked entirely: fewer panels, obvious at-a-glance verbs and selections, the separate Grid view folds into the actual city raid view, Heat lives in the run-wide Heat indicator position, JACK IN uses the same netrun-start flow as every other netrun. An HQ-DESIGN agent is producing concept options; there is no S-HQ fix slice.
Ref: art pass build `hq` (no concept image for the HQ page; chrome per `round33_ui_chrome/ui_kit.png`).

**HQ-01 (P1) Top resource strip.** Build: each resource is a coloured paper tag (cream, pink,
yellow) with a stencil number. Main: dark navy terminal chips with cyan edges (the v2 kit's
"terminal resource strip", as in `round32_ui_chrome/city_map_hud.png`). View: main follows the
v2 kit; the build's tags are louder and more "zine". Likely file: `scripts/ui/kit/hud_bar.gd`,
`hud_stats.gd`, `hud_skin.gd`. Decision: Superseded: HQ design pass (designer 2026-10-05)

**HQ-02 (P1) WANTED poster overlaps JACK IN.** Build: JACK IN disc top right, WANTED poster below
it, clear of each other. Main: the poster sits top right against the top bar and its right edge
runs into the JACK IN disc. View: main's overlap is a defect whichever look is chosen. Likely
file: `scripts/ui/hq_scene.gd` (HQ layout), `scripts/ui/kit/heat_poster.gd`. Decision: Superseded: HQ design pass (designer 2026-10-05)

**HQ-03 (P2) PIRATE RADIO.** Build: a taped paper note, pencil-script header, typewriter body.
Main: a terminal panel `> PIRATE RADIO`, Plex sans body. View: the v2 kit gives paper to
intercepted corp documents and terminal to the Cell's systems; pirate radio is neither, so this is
a designer call. Likely file: `hq_scene.gd` (radio block), `terminal_note.gd` / `zine_note.gd`.
Decision: Superseded: HQ design pass (designer 2026-10-05)

**HQ-04 (P2) Crew cards.** Build: polaroid with a flat illustrated hooded silhouette, a pencil
`RANK 0`, stencil name, class line, HP bar, deck/daemon icons. Main: polaroid with the v2 portrait
bust (`round39_portraits/portraits_classes_v2.png`, LOCKED), caption `Breaker 1 R0` in tiny type,
name, class/rank line, HP bar, `HP 60/60 · DECK 10 · DAEMONS 0` text. Main's portraits follow the
locked v2 set. Main's roster panel is wider than its cards (empty right third). Likely file:
`scripts/ui/kit/crew_card.gd`, `polaroid.gd`, `operative_dossier.gd`. Decision: Superseded: HQ design pass (designer 2026-10-05)

**HQ-05 (P2) Menu panel rows.** Main's CYBERDECK panel wraps `Scrub Heat -5 · pay 25` onto two
lines (`25` alone on the second); the build fits it on one. Main's headers carry the v2 `> ` caret
and square (kit rule). Likely cause: main's panel is narrower than its row at 1.0
(`hq_scene.gd`, menu column width). Decision: Superseded: HQ design pass (designer 2026-10-05)

### Netrun route (`route.jpg`)
Refs: art pass build `route` (M13: wireframe city, hex/diamond node icons on a dashed board, route
panel top right, DISPATCH strip, ROUTE KEY); concept `round37_netrun/city_default.png` (LOCKED hybrid
D: the unified lit city, cable-run paths, dossier paper, node holo panel, JACK IN sticker, minimap,
state key, `Always show all nodes` option). Main follows the concept's pieces.

**ROUTE-01 (P1) Route on the city.** Concept: the whole route is drawn: yellow walked cable-runs,
orange selectable, grey hidden nodes as small discs, patrols and corp landmarks labelled with
stickers (THE SPRAWL, MERIDIAN, HALCYON), the target circled. Main: only the two next nodes and a
dashed orange start bracket are drawn; the rest of the run is blank city; `[1] Fight` / `[2] Fight`
chips sit on top of their own markers. Build: the whole board with every node icon. View: main shows
too little to plan a route (the concept shows hidden nodes as grey "not yet" discs). Likely file:
`scripts/ui/kit/netrun_map_view.gd`, `route_overlay.gd`, `route_ink.gd`, `route_legend.gd`.
Decision:

**ROUTE-02 (P1) Dossier overlaps.** Main: the `AT LARGE` stamp covers the HP value (`60 /` cut) and
the `HEAT 0: COOL` stamp touches the IF STATIONED box. Concept: stamps in the paper's margins. Likely
file: `scripts/ui/kit/operative_dossier.gd` (stamp anchors). Decision: **drop the Heat stamp** (designer Q10, 2026-10-05): the Heat gauge in the
top bar is the one place for Heat. Fixed by HEAT-ALL: the stamp is removed from the dossier (the file, its height and
`AT LARGE` keep their places); sheet `docs/art_review/PARITY/fixes/HEAT_ALL.jpg`.

**ROUTE-03 (P1) Node panel.** Main: `DECRYPTED` stamp over the panel header, `Fight: win it for
Cycles and loo` cut at the right edge, the crossed-out dial `5` on the rewards text. Concept: the
node holo (`DEPOT 15`) with tier / type / rewards, the stamp small in the corner, nothing over text;
plus a JACK IN sticker and the map option under it. Likely file: `scripts/ui/kit/route_node_panel.gd`,
`raid_holo.gd` (shared holo), `zine_stamp.gd`. Decision:

**ROUTE-04 (P2) Route choice panel.** Build and main: `ROUTE // PICK THE NEXT NODE` terminal, rows
`[1] Fight > Fight · Event`, GRID VIEW, Save & quit. Main's rows have lime focus brackets and
`then: Shop` lines. Concept: no list (you pick on the map; the holo shows the hovered node). View:
the list is the pad / keyboard path; keep it, but it duplicates the map. Decision:

**ROUTE-05 (P3) Node key strip.** Main: `COMBAT ELITE EVENT SHOP RACK | walked next not yet cut off
| HOVER HERE: SHOW ALL NODES` along the foot. Concept: the same idea, states only. Matches.
Decision:

**ROUTE-06 (P2) Page title.** Concept: `THE GRID` title sticker top left (the run's map). Build:
DISPATCH line under the top bar. Main: top-bar words `NETRUN // ROUTE` only; no DISPATCH line on
this frame. Decision:

### Jack-in (`jack_in.jpg`)
Ref: build `jack_in`; concept `round37_netrun/transition_storyboard.png`.

**JACK-01 (P3) CONNECTING TO.** Build: one small cyan line `CONNECTING TO SOLACE BIOSYSTEMS`. Main:
small `CONNECTING TO` over a large cream stencil corp name. Same grid and scan band. View: main's is
stronger. Likely file: `scripts/ui/kit/jack_sequence.gd`. Decision:

### Loot (`loot.jpg`)
Refs: build `loot`; concept `round32_shop_reward/reward_screen_v2.png` (LOCKED reward).

**LOOT-01 (P1) Loot sheet cards.** Concept: three big sticker cards on a white loot sheet, the
middle one lifted with a peel corner, each card with art (glyph on a coloured field), type band,
rule, and a holo border for rare; a FIRMWARE DROP terminal beside it with a socket wheel. Build:
cream paper cards with halftone art in a terminal panel. Main: the white sheet is there; the cards
are flat gold / purple rectangles with only the name, cost and a two-line rule in small type, no
glyph art, no type band; the sheet is small (cards ~110 px wide). View: the concept is much richer;
main's cards read like placeholders. Likely file: `scripts/ui/kit/loot_sheet.gd`, `zine_card.gd`
(the same card face as CMB-04 / SHOP-02 / DECK-01). Decision:

**LOOT-02 (P2) Page title.** Concept: `FIGHT WON` title sticker + a `LOOT // NETRUN ...` chip.
Main: `PAYOUT` sticker + `> PAYOUT // LOOT: PICK A CARD` chip. Build: pink pencil `LOOT: PICK A
CARD`. Content choice. Decision:

**LOOT-03 (P2) Payout, deck counter, SKIP.** Concept: PAYOUT terminal top right (CYCLES +18, HP,
HEAT), a DECK 17 counter bottom left with a yellow pencil arrow `+1 = 18` from the picked card,
SKIP and CONTINUE stickers. Main: PAYOUT terminal (CYCLES 0, HP 60/60) beside the sheet, a small
`DECK 10` chip with a yellow `+1 = 11` scribble, SKIP sticker, no CONTINUE. View: main's pieces are
crammed into the right of the sheet. Likely file: `loot_sheet.gd`, `netrun_scene.gd` (loot page).
Decision:

**LOOT-04 (P1) Backdrop.** Concept: the dark, blurred lit city. Main: the bright 2D wireframe
city (lime / cyan / magenta outlines) at full strength behind the sheet, also behind the event,
shop overlays and pauses; it competes with every page. Build: the same wireframe city (M13).
Likely file: `cyberdeck_background.gd` (as TITLE-01). Decision: use the title's blurred city (designer 2026-10-05)
Fixed (S-BACKDROP): the netrun's loot and event pages show BlurredCityBackdrop (own look
`content/config/overlay_city_backdrop.tres`, the title's grade); the Mainframe keeps its facade
(it covers the city); review `fixes/TITLE-01b_LOOT-04.jpg`.

### HQ sub-pages (`hq_black_market.jpg`, `hq_crew.jpg`, `hq_loadout_deck.jpg`, `hq_loadout_spinner.jpg`, `hq_heat_band.jpg`)
Ref: art pass build (no concept beyond portraits `round39_portraits/portraits_classes_v2.png`).

**HQ-06 (P1) Black Market layout.** Build: `BLACK MARKET // SCHEMATICS 500` with three headed groups
(`RECRUIT`, `BOOSTS`, `UNLOCKS`, each a big stencil header with an icon), chips with an icon, name,
price and a buy glyph, locked recruits with a lock badge and `Needs Class: ...` under them. Main:
three run-on rows labelled `Recruit:`, `Next-run boosts:`, `Profile unlocks:` with plain text chips
`Class: Botnet (80)`; no icons, no locks, no unlock reasons; the lime panel edge again. View: the
build's grouping is much easier to scan. Likely file: `scripts/ui/hq_scene.gd` (market, ~l.1639);
art-pass source `art-m13-final:scripts/ui/hq_scene.gd` `_market_section` (~l.1768). Decision: Superseded: HQ design pass (designer 2026-10-05, by extension of HQ-01..05)

**HQ-07 (P2) Crew dossier cards.** Build: polaroid with a flat illustrated portrait, `RANK 0` in
pencil, stencil `GHOST 3`, class line, HP bar, icon stats, Loadout. Main: the v2 portrait in the
polaroid with a tiny `Ghost 3 R0` caption, stencil name, `// GHOST // RANK 0`, HP bar, stats as
text `HP 50/50 · DECK 10 · DAEMONS 0`, Loadout; the roster panel shows three cards in a row with
empty space right, and the CELL STATUS panel peeks out behind the top bar. Main's portraits follow
the locked v2 set. Likely file: `crew_card.gd`, `polaroid.gd`, `hq_scene.gd` (roster scroll).
Decision: Superseded: HQ design pass (designer 2026-10-05, by extension of HQ-01..05)

**HQ-08 (P1) Loadout DECK tab.** Same card-face difference as DECK-01 (build: paper cards with
art; main: flat gold faces with text only). Decision: Superseded: HQ design pass (designer 2026-10-05, by extension of HQ-01..05; the card face itself stays with S-CARDFACE / DECK-01)

**HQ-09 (P3) Loadout SPINNER tab.** Same wheel and side list; main's centre reads `BREAKER CORE
MK2` in red (build: pink), the side tiles are cut (`Accelera`). Likely file:
`scripts/ui/kit/spinner_view.gd`, `loadout_view.gd`. Decision: Superseded: HQ design pass (designer 2026-10-05, by extension of HQ-01..05)

**HQ-10 (P2) WANTED poster crossing a band (main only).** Main: the yellow hazard banner
`HEAT 30 · NOTICED (25+)` is taped across the poster over the operative's mugshot, the number rolls
(27 on the frame), `noticed` replaces `cool`; a raid note `A raid is queued. While Heat stays at
25 or more, elites are more frequent.` sits under PIRATE RADIO; CELL STATUS gains `Elite Frequency
+25%`. The banner hides the portrait. Likely file: `heat_poster.gd`. Decision: Superseded: HQ design pass (designer 2026-10-05, by extension of HQ-01..05)

### Title pages: options, codex, stats (`options.jpg`, `codex.jpg`, `stats.jpg`)
Refs: build `options`, `codex`, `stats`; concept `round31_ui_chrome/settings_menu.png`.

**OPT-01 (P2) Options framing.** Concept: a centred terminal ~700 px wide with an `OPTIONS` sticker
on its corner, the dimmed page behind. Main: a full-width terminal (y 60-720) with the sticker,
over the undimmed wireframe city (LOOT-04). Build: a left terminal and the logo. Likely file:
`scripts/ui/kit/settings_panel.gd`, `title_scene.gd show_options`. Decision:

**OPT-02 (P3) Switch rows.** Concept and main: the same rows in caps with a sans hint line,
`ON`/`OFF` switches, `>` caret and lime brackets on focus. Main: the Heat glitch row lacks the
concept's `LIMITED: flash limiter on, slow layer only` chip. Matches otherwise. Decision:

**OPT-03 (P3) Right column.** Concept and main: text scale slider with the live sample, colour-blind
tiles, resolve speed tiles, heat glitch previews; main matches. Decision:

**CODEX-01 (P1) Codex layout.** Build: two rows of tabs (Slices, Statuses & precision, Classes,
Corporations, Cards, Firmware, Daemons, Ring segments, Enemies, Nodes, Home servers, Defense assets,
Threats, Lexicon) and a cream paper page per tab in two columns, every entry with its glyph in
colour and a stencil name. Main: a `CODEX` sticker and one long terminal scroll of every section,
`SHIM SHIM: deals damage...` lines (the code then the name again), no glyphs except a few statuses,
Plex sans. View: the build's is a reference you can find things in; main's is a wall of text.
Likely file: `scripts/ui/kit/codex.gd`; art-pass source `art-m13-final:scripts/ui/kit/codex.gd`.
Decision:

**STATS-01 (P1) Stats layout.** Build: stat tiles with icons (Campaigns started / won / lost,
Runs, Operatives lost, Raids, Best ICE, Perfects, Racks, Cycles, Assisted wins, Achievements), an
ACHIEVEMENTS row of round badges (earned in pink, locked with a lock), RUN HISTORY as paper run
cards. Main: a PROFILE strip of six numbers, then `STATS // RECORDS` as one paragraph of text
(`Campaigns: 3 started, 1 won, 0 lost. ...`), achievements as `[x] First Blood` text lines, run
history as text lines. View: the build is far more readable. Likely file: `title_scene.gd
show_stats` (~l.514); art-pass source `art-m13-final:scripts/ui/title_scene.gd`. Decision:

### Pause menus (`hq_pause.jpg`, `pause_netrun.jpg`, `pause_fight.jpg`, `pause_fight_quit.jpg`)
Refs: build `hq_pause`, `pause_netrun`, `pause_fight` (a compact terminal with a pink `Resume
[Esc]` bar, icon rows, campaign code field + copy button); concept
`round33_ui_chrome/abandon_dialog.png` (a `PAUSED` sticker top left, the page dimmed behind).

**PAUSE-01 (P1) No dim behind the pause menu.** Build: the page behind is darkened under the menu.
Concept: the whole page dimmed and blurred, PAUSED sticker. Main: the menu is a wide terminal over
the page at full brightness (HQ, route and fight all readable behind it), so it reads as one more
panel; the PAUSED sticker is pinned to its top right. View: a defect against both references
(every other modal in main uses `GlassScrim`). Likely file: `scripts/ui/kit/pause_menu.gd` (no
scrim), `glass_scrim.gd`. Decision: **blur and darken** the page behind (designer 2026-10-05); no
PAUSED sticker except, at most, during a running raid.

**PAUSE-02 (P2) Pause rows.** Build: `Resume [Esc]` as a full-width pink primary bar, the rest
icon rows, the campaign code in a field with a copy button. Main: five `>` rows of equal weight, the
code as a plain line (no copy button). View: the build's primary Resume and copy button are better.
Same file. Decision: **the build's rows, reworked in v2** (designer 2026-10-05: the build looks a
little better): primary Resume, icon rows, the code in a field with a copy button.

**PAUSE-03 (P3) Pause over a fight.** As PAUSE-01; the turn banner shows through above the panel.
Decision: **fixed by PAUSE-01** (designer 2026-10-05); verify the banner no longer shows through.

**PAUSE-04 (P2) Quit confirm.** Concept dialog: `CONFIRM // ABANDON RUN` red-edged with a CANNOT
UNDO chip, a cost table, CANCEL (yellow, focus) and BURN IT (pink) with key hints under them, the
page dimmed. Main: `CONFIRM // QUIT` with `Quit REBEL_CELL? Progress is autosaved.`, CANCEL and QUIT
stickers, no key hints, blurred page. Quitting is not destructive, so the red edge is not needed; the
key hints are. Likely file: `confirm_dialog.gd`. Decision: **not the same screen; keep both as
shown** (designer 2026-10-05): the concept's dialog is "abandon the run/campaign", main's is "quit
the game". Both actions should be possible (see the open question on abandon in DECISIONS).

### MAINFRAME shop (`mainframe*.jpg`)
Refs: build `modem`, `modem_socket`, `modem_remove`, `modem_overwrite` (M13 MODEM CYBER SHOP: a
pink neon sign column, terminal panels MICROCHIPS / CARDS / SLICES / DAEMONS / REMOVE A CARD);
concepts `round34_firmware_daemons/shop_v5.png` (LOCKED shop), `firmware_socket.png`,
`round32_shop_reward/removal_options.png`. Main follows shop_v5 (MAINFRAME sign, pegboard, clerk,
slice wheel, recycle bin, LEAVE).

**SHOP-01 (P1) Pencil note over the clerk's line.** Concept: the yellow pencil
`ASK ABOUT THE BACK ROOM` sits below and right of `CYCLES ONLY.`, clear of it. Main: at 1.0 the
note's first line runs over the end of `CYCLES ONLY.` (the full stop and the Y are covered).
Build: no clerk. Likely cause: `scripts/ui/netrun_scene.gd` `CLERK_NOTE` placement (~l.3558), the
note anchored to the line's right instead of under it. Fix: anchor the note under the last clerk
line, offset right, as in the concept. Decision:

**SHOP-02 (P1) Card stock faces.** Concept: pinned sticker cards with type colour (SYSTEM teal,
WHEEL grey), a big glyph on a patterned field, type band, value and rule. Main: pinned cards with
price tags on strings (matches), but the faces are flat gold / magenta with a small rule in tiny
type and no glyph art (same card face as LOOT-01). Decision:

**SHOP-03 (P2) Slice wheel.** Concept and main: the half wheel at the foot with prices on tabs,
`TOP 3 ONLY` pencil; main's slices are darker and the tab prices smaller. Matches in layout.
Likely file: `scripts/ui/kit/slice_stock_wheel.gd`. Decision:

**SHOP-04 (P2) Firmware pegs.** Concept: three chips with glowing coloured gems, white bold glyphs,
names, rarity in colour (COMMON / UNCOMMON blue / RARE gold), allowed slice, kraft price tags, and a
cyan terminal hint row (`> SKIMMER ATK: ...`). Main: two chips, dark with grey glyphs, rarity and
slice in grey, price tags struck out in red (not affordable: the concept's rule is a greyed dot +
NEED tag). View: main's red strike reads as "sold" rather than "can't afford yet". Likely file:
`scripts/ui/kit/shop_item.gd`, `shop_pegboard.gd`. Decision:

**SHOP-05 (P3) LEAVE and the bin.** Concept: `LEAVE THE MAINFRAME` sticker + chevrons bottom
right, recycle bin top right of the wheel. Main: matches; LEAVE is green-white (concept's is the
same), the bin sits higher. Decision:

**SHOP-06 (P1) Socket choice.** Concept: drag the chip onto a slice of the wheel; valid slices get
lime brackets, invalid ones grey out, occupied ones show an amber REPLACE?. Build: a row of numbered
slot tiles `1 CRIT 12 ... 6 MISS`. Main: a `Chips go into: Slot 1: OVFL 12` OptionButton whose list
covers the card's description panel. View: the dropdown is the weakest of the three and hides the
info it needs. Likely file: `netrun_scene.gd` shop socket UI, `shop_item.gd`. Decision:

**SHOP-07 (P2) Remove a card.** Concept (two options): PURGE `rm -rf` keycap you drop the card on,
or DEGAUSS coil. Build: card grid + a SHRED sticker. Main: a `RECYCLE BIN // REMOVE A CARD` lime
terminal with the card grid and the recycle bin icon under it (the bin is the concept's 4th, sketch
option). Designer call between the concept's PURGE (marked "recommended") and main's bin.
Decision:

**SHOP-08 (P3) Upgrade a slice.** Build: `UPGRADE · 100 CYCLES` as one pink graffiti line. Main:
`UPGRADE` graffiti + `100 CYCLES` in small cyan beside it. Same wheel. Decision:

### Events (`event.jpg`, `event_dispatch.jpg`)
Refs: build `event`, `event_dispatch` (M13: paper note top left, choice cards right, pink pencil
`PLAY IT SAFE??`); concepts `round31_reward_event/event_screen.png`, `event_screen_memo.png`.

**EVT-01 (P2) Event terminal.** Concept: one wide terminal centred with a CAM feed still, title,
body, CHOOSE list, RUN side terminal (HP / CYCLES / CREW), TERMINAL sticker and the pencil to the
safe choice. Main: the same pieces, placed top right over the city; no RUN side panel; the CAM
feed is the wireframe city (concept: a photo-like cam still with a red pencil circle). View: main
follows the concept; centring it as the concept does would stop it fighting the top bar.
Likely file: `scripts/ui/kit/cam_feed.gd`, `netrun_scene.gd` (event page). Decision:

**EVT-02 (P2) Choice rows.** Concept: yellow numbered tabs, stencil choice names, outcome chips
(`-12 HP`, `+1 BREAKER`, `NO CHANGE`) in a column to the right of the row. Main: yellow tabs and
stencil names, outcome chips tucked under the name in tiny type, the row has a lime focus edge.
View: the concept's chips are readable at a glance. Likely file: `choice_sticker.gd`,
`outcome_row.gd`. Decision:

**EVT-03 (P1) DISPATCH event.** Concept memo: a paper memo (corp letterhead, highlighted lines,
red pencil circle, DO NOT FORWARD stamp) on the left of the terminal; INTERCEPTED header; result
lines and CONTINUE. Main: a red-edged terminal `> TERMINAL // DISPATCH` with a red heartbeat
`VOICE ONLY // NO FEED` instead of the memo. View: DISPATCH is voice (no document), so main's
waveform is a reasonable stand-in; the memo concept is for corp intercepts. Designer call.
Likely file: `corp_memo.gd`, `netrun_scene.gd`. Decision:

### Deck viewer and card detail (`deck_view.jpg`, `card_detail.jpg`)
Ref: build `deck_view`, `card_detail` (no concept image; the cards should match the hand,
`round41_wheel_stack/combat_typical_v4.png`).

**DECK-01 (P1) Card faces in the viewer.** Build: the cream paper cards with halftone art. Main:
flat gold / magenta cards with name, cost, a two-line rule and a tiny value line; no art, the grid
leaves the right third empty. Same card face issue as LOOT-01 / SHOP-02. Likely file:
`scripts/ui/kit/deck_view.gd`, `zine_card.gd`. Decision:

**DECK-02 (P2) Card detail.** Build: the card at ~2x with its art, and a CARD NOTES panel
(type, what it does, rarity and stock, the SPIN rule). Main: a `CARD DETAIL` terminal over the grid
with a ~1.3x card and three plain lines (`JOLT // 1 RAM`, `Common`, `Jolt (RAM 1) Spin a wheel 3
ticks.`) repeating the card. View: the build's notes explain more. Likely file: `scripts/ui/kit/inspect_popup.gd`.
Decision:

### Daemon tray (`daemon_tray.jpg`)
Refs: build `daemon_tray`; concept `round34_firmware_daemons/daemon_row.png` (the rack in combat,
CLEAN SIGNAL card).

**DAEMON-01 (P3) Daemon tray popup.** Build and main: the same small `DAEMON / CASCADE` terminal
under the top-right Daemon badge; main's reads `Daemon Cascade` (doubled word). Concept: in combat,
a CRT rack on the left with a hover card (name, rarity, trigger, family colour, TILE STATES). The
tray outside combat has no concept. Likely file: `scripts/ui/kit/daemon_tray.gd`. Decision:

### Combat (`combat_*.jpg`, `tutorial.jpg`)
Refs: art pass build `combat_*` (M13: bright teal wireframe city, pink/teal sticker-ring wheels,
cream paper cards, forecast tags above each wheel, NEXT TURN plates, SEND IT as dripping pink
graffiti); concepts `round41_wheel_stack/combat_typical_v4.png` and `combat_worst_case_v4.png`
(LOCKED HUD v4: no forecast tags, no NEXT plates, result chips beside HP, D4 wheels, gold sticker
cards). Main follows HUD v4 in layout (name sticker + RAM bottom left, chips beside HP, SEND IT over
EXECUTE, RESPIN / UNDO chips); the differences are mostly in colour and material.

**CMB-01 (P1) Combat backdrop.** Concept: the corp's lit 3D city (Meridian's yellow crane yard in
the worst case), warm and readable, softened ~55 % under each wheel. Build: the saturated
teal / magenta wireframe city filling the screen. Main: a very dark navy 3D block city, a few lit
windows, most of the frame near black; the scene reads much darker than both references. View: the
concept's lit city gives each corp its place; main's dark field makes the wheels the only colour,
but it loses the sense of where the fight is. Likely file: `scripts/ui/arena/combat_backdrop.gd`,
`backdrop_catalog.gd`, `content/config/city_config.tres` (exposure / light at the combat band).
Decision:

**CMB-02 (P1) Player wheel colour and material.** Concept D4: slices with distinct illustrated
screen fills (attack red grid, defend teal waves, special skull, debuff purple), a bright pink outer
frame with telemetry text, a bold gold active slice, high saturation. Build: flat pink/teal fills,
white glyph badges, a sticker ring. Main: the D4 shape and glyph/number set match, but the fills are
dark and desaturated (maroon / slate), the frame thin and dim; the slice types are hard to tell
apart at a glance. View: the concept is clearly more legible (slice type by colour + glyph); main
reads muddy. Likely file: `scripts/ui/wheel/wheel_face.gd`, `wheel_disc.gd`, `wheel_kit.gd`, the
slice materials / palette tokens (`palette.gd`, `palette_skins.gd`). Decision:

**CMB-03 (P1) Enemy wheel corp kit.** Concept: the enemy wheel wears the corp kit (Meridian orange
hazard frame). Main: the enemy wheel (Solace) is olive-green and very dark; the corp frame is thin.
Build: green sticker ring. Same files as CMB-02 plus the corp kits. Decision:

**CMB-04 (P1) Hand: sticker cards.** Concept: gold-yellow die-cut sticker cards with a white border,
type band (WHEEL yellow / HACK pink / SYSTEM teal), big glyph and value, fanned and overlapping, a
DECK / DISCARD pile pair on the left. Build: cream paper cards with a halftone wheel illustration,
flat row. Main: the gold cards with type band, but in a dim olive tone with a camo/triangle pattern
behind the glyph, a straight row with gaps, no deck/discard piles, card text cut (`Spin a whee...`,
`OVERCLOC...`). View: main is close in structure; the dull gold and cut text read worse than the
concept; the missing piles drop info (deck counts are in the top bar). Likely file:
`scripts/ui/kit/zine_card.gd`, `sticker_button.gd`, `combat_scene.gd` (hand layout). Decision:

**CMB-05 (P2) Turn banner.** Concept: a slim terminal strip top centre `TURN 3 | FREE NUDGE 1` with
the fight's address line under it. Build: one text line top left. Main: a large boxed banner with
stencil `TURN 1 | FREE NUDGE 1` and the key hint under it. View: main's banner is bigger than needed
and pushes into the wheel area. Likely file: `scripts/ui/kit/hud_dialog_panel.gd` / `combat_scene.gd`.
Decision:

**CMB-06 (P2) SEND IT block.** Concept: SEND IT white die-cut sticker overlapping a dark EXECUTE
plate; RESPIN / UNDO terminal chips beside it. Main: matches, but EXECUTE is drawn as a pale ghost
outline that reads like a rendering fault, and `> turn_resolve.exe [Space]` runs under it in tiny
type. Build: graffiti SEND IT with drips. Likely file: `scripts/ui/kit/send_it_sticker.gd`.
Decision:

**CMB-07 (P2) Top bar in combat.** Concept: no global top bar in combat (the turn strip and corner
chips only). Build and main: the full campaign resource bar. View: the concept gives the wheels the
height. Likely file: `combat_scene.gd`, `hud_bar.gd`. Decision:

**CMB-08 (P3) Name sticker and RAM.** Concept: `CELL-9 // BREAKER` pink sticker, RAM pips in a
terminal plate. Main: matches; the name reads `BREAKER 1 // BREAKER` (doubled class word), SAVED
stamp sits inside the RAM plate. Likely file: `scripts/ui/kit/hud_name_sticker.gd`, `ram_bar.gd`.
Decision:

**CMB-09 (P2) Card-play preview.** Build: `LANDS HERE` tag, dashed slice outline and white chevrons
on the target wheel. Main: same pieces (dashed pink slice, LANDS HERE tag, chevrons) dimmer; the
preview tag is cut at the left by the wheel's frame. Concept: `round17_corp_wheels/preview.gif`.
Likely file: `scripts/ui/kit/hud_wheel_layer.gd`, `forecast_*`. Decision:

**CMB-10 (P3) Aim line.** Both: yellow dashed pencil line from the card to the target; main's ends
on the slice, the build's on the wheel. Equivalent. Decision:

**CMB-11 (P2) Mid-replay.** Build: forecast tags flip to `THIS TURN` with tick boxes. Main: a WEAK
landing tag, the bit stream into the hub, a blue shield bar beside the wheel, chips `?`. Main follows
the concept (precision landings, bit stream); fine. Decision:

**CMB-12 (P2) Result chips and LAST TURN.** Concept: `-14` red boxed, `(4 shield)`, `+4` green, at
HP height. Main: the chips are there; `+3` uses a tiny boxed icon, an empty octagon outline chip
follows HP (an empty status slot?) and the HP plate has a cyan chevron bracket the concept lacks.
Likely file: `scripts/ui/kit/hud_result_chips.gd`, `result_chip_model.gd`. Decision:

**CMB-13 (P2) Refusal toast.** Build: yellow paper note with a no-entry mark, pencil type. Main: a
red-edged terminal toast centre-right, small. The bible says "refusal: HARM edge + no-entry mark":
main follows the bible. Decision:

**CMB-14 (P2) Victory.** Build: the enemy wheel greyed with a green `DEFEATED` stamp and skull, a
small LOOT graffiti. Main: `VICTORY` in big lime stencil, `OURS NOW` in yellow over the backdrop,
the enemy wheel removed (dashed circle + DEFEATED stamp), the operative line in a terminal box.
View: main is louder; `OURS NOW` floats with no anchor. Likely file: `combat_scene.gd`
(`combat_end_hold`), `scripts/ui/kit/zine_stamp.gd`. Decision:

**CMB-15 (P3) LOOT sticker.** Main: white die-cut LOOT with lime focus brackets; build: graffiti.
Main follows the sticker rule. Decision:

**CMB-16 (P2) Defeat.** Build: player wheel drained grey with a red DEFEAT stamp and skull. Main:
FLATLINED stamp, wheel dimmed, the top bar shrinks to HEAT + SCHEMATICS only, both on main and the
build. Concept `round40_hub_inner_ring/player_defeat_v2.gif` (drain). Decision:

**CMB-17 (P3) JACK OUT sticker.** As CMB-15. Decision:

**CMB-18 (P1) Tutorial card covers the play area.** Build: the tutorial note sits bottom right,
paper, clear of both wheels. Main: a terminal card sits in the middle between the wheels, over the
enemy wheel's left edge and the backdrop; its body is Plex sans at a small size. View: the build's
placement keeps the wheels readable while you read. Likely file: `scripts/ui/kit/tutorial_overlay.gd`.
Decision:

**BOSS-01 (P1) Guard-arc marker over the HP plate.** Main: the green guard-arc end marker (the
triangle) sits on the first digits of the boss HP `1395/1475`. Build and concept: nothing over the
HP value. (Was in progress at FIX-REDS.) Decision: **fixed** (FIX-REDS merged, designer approved). (designer, 2026-10-05)

**BOSS-02 (P1) Boss wheel phase dressing.** Concept worst case: an outer parasite ring, satellites
docked on the rim, status-stack tabs above, a wide orange hazard frame, two needles. Main: the boss
wheel is the regular D4 wheel in olive with a name plate `RENEWAL ENGINE`, two side hex pips and
guard arcs; no satellites, inner ring tabs or drones. Build: sticker wheel with a bead ring. Part of
this needs mechanics the rules lack (see below); the corp frame and colour (CMB-03) do not.
Decision:

**BOSS-03 (P2) White bead chain on the backdrop.** Main: a chain of white blobs arcs across the
boss backdrop between the wheels (the Solace helix's lights?) and reads as a UI element. Build:
none. Likely file: `combat_backdrop.gd` (boss place). Decision:

**BOSS-04 (P2) Phase 3 arcs.** Main phase 3: lime guard arcs, double chevrons and a `13` marker
crowd the boss wheel's right side; build: an orange dashed arc. View: main's lime again collides
with the focus colour. Likely file: `hud_wheel_layer.gd`. Decision:

### City Grid (`grid*.jpg`: grid, grid_site_selected, grid_raid_pending, grid_influence, grid_drag_crew, grid_meridian, grid_halcyon, grid_orbital, grid_rebel_cell)
Refs: art pass build `grid*` (M13: a flat dark-navy isometric board, hex tier badges, a 2D wireframe
city); concepts `round40_city_unified/city_grid_v3.png` (LOCKED unified city),
`round42_site_markers/site_markers_on_map_v4.png` (LOCKED markers), `round32_ui_chrome/city_map_hud.png`
(Grid HUD, "in progress" in the bible), `round34_rebel_cell/map_A_home.jpg`.
The build's board look is superseded by the unified-city concept, which main follows (3D city,
round marker discs, minimap); the entries compare main with the concept unless they say otherwise.

**GRID-01 (P1) Network area bloom.** Concept: links are thin yellow (yours) / orange (selectable)
cable lines over an unchanged city; the city stays readable between them. Main: the whole linked
area sits under a white/cyan glow veil with bright cyan double-line links and lit pad rings on
every link; at 1.0 it washes out the buildings under it and is the brightest thing on screen.
View: the concept reads better (the markers are the information, the links support them); main's
glow also makes the lime "yours" focus colour hard to pick out. Likely cause:
`scripts/ui/kit/city_map_overlay.gd` (the veil / keyline / glow under-layer, `_draw` ~l.1071) and
the 3D city's bloom (`content/config/city_config.tres` `bloom`, `lane_glow_management`). Fix: drop
the veil, draw links as the concept's single cable strokes in the state colours, lower the bloom
at the Grid band. Decision:

**GRID-02 (P2) Marker size and ring.** Concept v4: small discs (~24 px at 1080p, ~16 at 720)
with a thin state ring and the corp glyph, labels only on hover / landmarks. Main: discs ~36 px at
720 with a thick orange ring and a dark face, a name label on most Sites. View: main is more
legible at 1.0 but crowds the map (labels and discs cover the city); the concept relies on hover.
Likely file: `scripts/ui/kit/site_marker.gd`, `site_marker_view.gd`, `site_marker_layout.gd`.
Decision:

**GRID-03 (P1) Central Server chip collides.** Main: the `CENTRAL SERVER // EXPLOITS 0/3` chip is
cut by the Site label `The Genome Core` placed over it, and the red TARGET pencil runs over the
next marker. Concept: the chip sits clear under the circled HQ (bible rule: no UI over grease
pencil). Same family on REBEL_CELL (GRID-13). View: a defect either way. Likely file:
`scripts/ui/kit/city_map_overlay.gd` label placement (the free-space test ~l.1065) does not
register the chip / pencil; `target_edge_marker.gd`. Decision:

**GRID-04 (P2) Right column.** Build: plain terminal panels, a magenta header rule, CLAIM chips.
Main: both panels have lime 2 px edges with the v2 `>` header and square; the site card holds
portrait chips + an operative dropdown + the JACK IN button; RUNS OPEN NOW rows with IF CLEARED
lines. Concept (HUD in progress): crew panel on the left, holo Site card and IF CLEARED terminal
on the right. View: lime is the kit's focus colour (ui_kit: "lime brackets = focus, everywhere");
using it as a panel edge competes with real focus. Likely file: `scripts/ui/hq_scene.gd` (Grid side
column), `scripts/ui/kit/city_grid_controls.gd`. Decision:

**GRID-05 (P2) Page title and HUD.** Concept: `THE GRID` title sticker, campaign line
`CAMPAIGN 03 // HALCYON CIVIC // ICE 5`, a resource strip and a big HEAT suspect-file bar
(COOL / NOTICED / FLAGGED / HUNTED with the next threshold). Main and build: the shared top bar
(`02 CITY GRID` + resource chips). View: the concept's Heat bar explains Heat on the page where it
matters; whether the Grid gets its own HUD is a designer call (the bible marks it "in progress").
Likely file: `scripts/ui/kit/hud_bar.gd`, `hq_scene.gd`. Decision:

**GRID-06 (P2) Minimap and legend.** Main: minimap (corp territories in colour, lime view box) and a
MAP LEGEND panel with icons (next, cleared, yours, DOWN, TAKEN, exploit, heat obj., locked link).
Concept: minimap only, plus a one-line state key along the bottom (`owned / visited`, `selectable`,
`not yet (hidden)`, `HOVER HERE: SHOW ALL`). Build: a text legend. View: the concept's strip costs
less screen; main's legend is clearer for a first look. Likely file: `scripts/ui/kit/city_minimap.gd`,
`map_legend.gd`. Decision:

**GRID-07 (P2) JACK IN placement.** Concept: one big JACK IN vinyl sticker bottom right (the one
sticker verb on the page). Main: a pink button-sized JACK IN inside the Site card; the bottom right
is the runs list. View: concept matches the v2 "one sticker verb per screen, where the eye ends"
rule; main's keeps the verb next to the operative it launches. Likely file: `hq_scene.gd`.
Decision:

**GRID-08 (P3) Selected Site panel text.** Main adds a plain-language line (`Not reachable yet.
Clear a Site linked to it first: ... Then it opens (orange ring) and JACK IN shows here.`) in Plex
sans; the build shows only the tags. View: main's line helps; it is the only sans paragraph in the
column. Decision:

**GRID-09 (P3) RAID SETUP sticker.** Build and main: a pink RAID SETUP sticker above the Site card;
main's is larger with the v2 white die-cut. Concept: a RAID PENDING terminal at the bottom centre
with a RAID SETUP terminal button. View: equivalent; designer call on the concept's bottom bar.
Decision:

**GRID-10 (P3) Claimed tint.** Main: a lime spray scribble on the claimed Site's ground plus the
claimed marker; build legend says "claimed: spray ring". Matches the intent. Decision:

**GRID-11 (P2) Carried operative (main only).** Main: dragging a crew chip shows a black/lime
`DOWN` sticker on the Site, a green ground glow and the chip ghost (the build has no drag). View:
`DOWN` reads as "this Site is down", not "drop here"; the word may confuse. Likely file:
`scripts/ui/kit/drop_layer.gd`, `drag_ghost.gd`, `hq_scene.gd` (grid drop). Decision:

**GRID-12 (P1) Camera framing on Meridian.** Main: the network sits on the city's edge; the right
half of the map area is empty purple fog past the last block, the TARGET pencil is half under the
minimap, and Meridian's HQ is not in view. Halcyon and Orbital frame well; Solace and REBEL_CELL
are fine. Build: the board fills the area. View: a defect. Likely file: `scripts/ui/kit/grid_map_view.gd`
/ the Grid camera fit (`RaidZoomFit`-style fit for the Grid band), `scripts/core/` city layout for
Meridian's seed. Decision:

**GRID-13 (P1) Label collisions on REBEL_CELL.** Main: `Erase the Ledger` and `Lose the Handler`
labels touch; `The Cell's Own Patch` sits on a marker; the TARGET pencil runs under `CENTRAL
SERVER // EXPLOITS 0/3`. Same cause as GRID-03. Decision:

### Raid (`raid_setup.jpg`, `raid_drag_asset.jpg`, `raid_playout.jpg`, `raid_result.jpg`, `raid_report.jpg`, `raid_interlude.jpg`)
Refs: art pass build `raid_*` (M13: a 2D wireframe city, a terminal column on the right, paper
defence cards in a DEFENSE LOADOUT strip); concepts `round40_city_unified/raid_view_v3.png`
(LOCKED raid view), `round21_raid_ui/raid_report.png`. Main follows the unified-city concept for
the map and the paper work order, and the build for the loadout strip.

**RAID-01 (P1) Defence cards.** Concept: a row of dark cards along the bottom edge over the map,
each with a coloured top band, a big glyph, `INT n`, a count `x1`, a two-line rule; a picked card
is "parked" in a dashed slot with a yellow pencil arc to its target. Build and main: cream paper
cards (`TURRET` / `ICE LOCK` / `DECOY`, `HP 10 1 LEFT`) inside a `DEFENSE LOADOUT // ARMORY 3/6`
terminal panel with `1 Pick a node / 2 Press a card` steps. View: the concept's row frees the map
and reads as "hand of cards"; main's panel is clearer about the steps. Likely file:
`scripts/ui/kit/asset_card.gd`, `hq_scene.gd` (raid setup layout). Decision:

**RAID-02 (P1) Work order paper overlaps.** Main: the instruction line (`The corp is raiding your
CORE. Place defences...`) is set straight over the city above the paper, unboxed and hard to read;
the pink `IF THE RAID RUNS NOW: HOME -10` disc sits on the paper's value column (`2 IN 1 WAVE`,
`STRENGTH 0%`); the `INTERCEPTED` stamp covers `HOME 50 > 40` and `STOPPED 0/2`; the title line
`COMPLIA...` is cut at the right edge. Concept: stamp over the redaction bars only, no disc on the
paper, values clear. Build: no paper (terminal panel). View: main's paper is the right look
(concept), its placement is a defect. Likely file: `scripts/ui/kit/raid_paper.gd`,
`corp_memo.gd`, `hq_scene.gd` (where the result disc is placed). Decision:

**RAID-03 (P2) Threat intel panel.** Concept: corp-tinted holo (orange for Meridian), threat lines
A/B/C, unit sprites along the bottom. Main: corp-tinted (Solace green) holo, `DECRYPTED` stamp over
the panel's own header (`THREAT INTEL //` and `KEY 4C-E7` partly covered), a single small unit icon
and a pencil-crossed dial `5`. Build: none. View: main follows the concept; the stamp should not
cover the header. Likely file: `scripts/ui/kit/raid_intel_strip.gd`, `raid_holo.gd`. Decision:

**RAID-04 (P2) Links and threat pencil.** Main: the same glow veil as GRID-01 under the network,
hex `T1` badges on each node, red pencil arrows A/B. Concept: dashed yellow cable lines, small
diamond pads, red pencil routes with lettered entry marks. Build: green wireframe. Same cause as
GRID-01 (`city_map_overlay.gd`), plus the raid's node badges (`raid_socket.gd`). Decision:

**RAID-05 (P2) Page title.** Concept: `RAID SETUP` title sticker top left. Main and build: the top
bar's words `03 CELL DEFENSE RAID SETUP`. Likely file: `hq_scene.gd`, `hud_bar.gd`. Decision:

**RAID-06 (P2) Right column bottom.** Main: `YOUR NETWORK_` terminal (concept: top left, every node
listed with HOLDS / DISABLED chips), a floating `MORE BELOW` chip inside it, `Back to HQ`, the
START DEFENSE sticker, the speed strip `1x 2x 4x SKIP STEP --/30`. Concept: START DEFENSE sticker
and the speed strip bottom right, `IF PLACED` forecast terminal on the right. View: main lacks the
IF PLACED forecast (it exists as text elsewhere?) and the network list sits where the forecast
goes. Decision:

**RAID-07 (P2) Carried defence card (main only).** Main: the card ghost lifted with a long yellow
pencil line from it to the bottom-right corner (the pointer, off the map), not to a node. Concept:
the arc runs from the parked card to the hovered node with a target loop. The harness parks the
pointer at the corner, so part of this may be the capture; the line should still end on the
nearest valid node when the pointer is off the map. Likely file: `raid_drag_pencil.gd`. Decision:

**RAID-08 (P1) START DEFENSE sticker during the playout.** Main, mid-playout: the START DEFENSE
sticker is drawn over the MAP LEGEND (tilted, mid-exit) while the units move. Build: the button is
gone once pressed. View: a defect (either its exit motion is not over at the capture frame, 2 frames
per step, or it is left behind). Likely file: `hq_scene.gd` raid playout start / `raid_beats.gd`.
Decision:

**RAID-09 (P2) Live feed and Continue.** Build: a paper `PLAYOUT` note with the steps, pink
Continue. Main: `> LIVE RAID FEED_` terminal with a red edge, first line clipped at the top, speed
chips inside; `Continue` as a big grey (disabled) sticker until the end. View: the grey sticker
reads as broken rather than "wait"; the build's paper note is warmer. Likely file:
`scripts/ui/kit/raid_feed.gd`, `raid_playout_panel.gd`. Decision:

**RAID-10 (P2) Result call-out.** Build: a red label sticker `HOME -10 · HOLDS` with a pointer over
the CORE and a big pink `-10`. Main: small red/yellow pencil words `HOME -10 HOLDS` on the map, a
pink `-5` floating near the legend, the CORE pad. View: the build's call-out is far easier to read
at a glance. Likely file: `scripts/ui/kit/raid_verdict.gd`, `raid_report_pencil.gd`. Decision:

**RAID-11 (P1) After-action report.** Main follows the concept (paper report, CELL HOLDS sticker,
BACK TO THE GRID sticker) but the `CLASSIFIED` stamp covers the CORE row's value
(`50 > 40 HOLDS`) and `HOSTILE HOME SERVER 40/50` is red where the concept uses red only for
losses. Concept: the stamp sits on the redaction bars. Build: a terminal list. Likely file:
`raid_paper.gd` (stamp placement). Decision:

**RAID-12 (P3) CELL HOLDS and result disc.** Main: result disc top left plus CELL HOLDS sticker;
concept: the sticker centre-left, no disc (the paper carries the numbers). Decision:

**RAID-13 (P1) Map behind the raid interlude.** Build: the network board (nodes, links, threat
arrows) behind the interlude panel. Main: the old 2D wireframe city (green / cyan, no network, no
threat route), not the unified 3D city used by every other raid view. View: main's backdrop is
inconsistent with its own raid screens. Likely file: `scripts/ui/netrun_scene.gd` (raid interlude
page). Decision:

**RAID-14 (P2) START DEFENSE in the interlude.** Build: the pink START DEFENSE sticker. Main: a
full-width terminal button with a shield icon. View: every other raid page uses the sticker; this
one should too (one sticker verb per screen). Also main shows `RUN ASSETS: none / ARMORY: none` as
two bare lines where the build says why (`No assets to deploy: ...`). Likely file: `netrun_scene.gd`.
Decision:

### HQ run, Central Server gate, combat backdrops (`hq_run_*.jpg`, `central_server_gate.jpg`, `combat_backdrop_*.jpg`)
No art-pass build screen exists for these (the HQ run and the gate are v2 work on main). References:
concepts `round43_hq_mechanics/hq_{solace,meridian,halcyon,orbital}_compound.png`,
`dispatch_idea_1_sync_strike.png`, `round38_landing_exploits/central_server_gate.png`,
`round26_hq_targets/combat_solace.jpg`, `site_solace_night.jpg`. Main: `hq_run_lab.tscn` at
1280x720 (`run_<corp>` = today's run page, `full_solace` = a full run map half walked, `gate_<corp>`,
`hq_solace` / `site_solace` = the combat backdrop's city close-up).

**HQRUN-01 (P1) No page title or mechanic chrome.** Concept: a title sticker per corp (`SOLACE:
CLIMB THE HELIX`, `MERIDIAN: CRANE + TRAIN`, `HALCYON: THE LONG WAY`, `ORBITAL: THE LAUNCH LOOP`),
an `> HQ MECHANIC` terminal at the foot explaining the compound's rule with a progress chip
(`HEIGHT 31%`, `STEP 3`, `LAP 1`), and a state key strip (walked / selectable / not yet / cut off /
danger). Main: none of these; only the TARGET pencil and the `CENTRAL SERVER // <name>` chip.
The mechanic text needs the per-corp mechanics (see "Mechanics the rules lack"); the title sticker
and the key strip do not. Likely file: `scripts/ui/hq_run/hq_run_view.gd`. Decision:

**HQRUN-02 (P1) Today's run shows one dashed line.** Concept: the whole compound route drawn
(nodes on the structure, walked path in lime, selectable in orange, labels like `STRAND A`,
`CROSSOVER`, `ON THE TRAIN`). Main `run_<corp>`: only an orange dashed line from the start to the
server and the operative marker; no nodes (main's run is GDD 4.2's breach run, a straight line).
`full_solace` shows main can draw a full map (rings on the helix, walked lime path, gears for
locked nodes). View: the full-map look is close to the concept; which one the real run shows is
a rules question. Decision:

**HQRUN-03 (P2) Node markers on the compound.** Concept: route vinyl stickers with state rings and
small name tabs. Main `run_solace` (crop HQRUN-03): no nodes at all on today's run. Decision:

**HQRUN-04 (P2) Full run map markers (`full_solace`).** Main: white-dashed rings for not-yet nodes,
grey gear discs for cut nodes, orange selectable rings, a lime walked path; no name tabs, and the
gears are hard to read on the dark helix. Close to the concept's language. Likely file:
`hq_run_view.gd`, `route_overlay.gd`. Decision:

**HQRUN-05 (P2) Meridian compound.** Concept: the crane yard at night with lit warm windows, nodes on
the crane arms and the train, a `NEXT: OFF THE TRAIN` pencil call-out, the master manifest circled.
Main: the same compound model (crane, cars, warm lit faces) — a good match in modelling; camera a
little closer; no nodes / call-outs (HQRUN-02). Decision:

**HQRUN-06 (P2) Halcyon framing.** Concept: the ziggurat seen from further out with the switchback
route on its face, the eye's watched half tinted. Main: a much closer camera on the ziggurat; the
compound fills the frame, the city around it is hidden. Likely file: `scripts/city3d/hq_compound_stage.gd`
(per-corp framing). Decision:

**HQRUN-07 (P2) Orbital launch loop.** Concept: the platform with the hazard ring, dishes, antenna,
the loop route, a `> MISSILE BAY` terminal with a NEXT MISSILE PREP bar. Main: the same platform,
hazard ring and dishes (a close match), no loop route, no missile bay panel (needs the mechanic).
Decision:

**HQRUN-08 (P1) REBEL_CELL HQ camera.** Concept (DISPATCH sync strike): an angled view down three
lanes towards the DISPATCH core tower with red signage. Main: a near top-down view of a street grid
with a red lane, a white X, and a yellow wedge (a searchlight) cut off at the bottom-right corner;
it reads like the Grid, not an HQ. Likely file: `hq_compound_stage.gd` (REBEL_CELL camera pitch /
framing), `city_iso_camera.gd`. Decision:

**GATE-01 (P2) Gate panel.** Concept: a corp-orange bordered panel with `CENTRAL SERVER // THE
MANIFEST`, `EXPLOITS 3/3 minimum to breach`, three keycards (corp name header, icon, type, one-line
effect, a footer tag), EXTRA slots, `3/3 - BREACH READY`, and a BREACH sticker under the panel.
Main: the same pieces (keycards in Solace lime, EXTRA slots, BREACH READY, BREACH sticker with a
lime focus box, `Back to the compound`), larger and without the panel border: the keycards and text
float on the dimmed compound. View: main's content matches; the concept's bordered panel holds it
together. Likely file: `scripts/ui/hq_run/central_server_gate.gd`. Decision:

**GATE-02 (P1) Duplicated server label / boss preview.** Main: `CENTRAL SERVER // THE GENOME CORE`
appears twice (the gate's header and the run page's chip, left visible behind the gate at a
different place); the boss wheel preview sits right with `1475/1475` HP but no exploit effect card.
Concept: one label; the wheel shows the exploit effects (cut slices, a crossed phase) with an
`INTEL // SHIPPING MANIFESTS` card listing what each Exploit did (`PHASE 2 @ 66% ... BREACHED`).
Likely file: `central_server_gate.gd`, `hq_run_view.gd` (hide its chip under the gate). Decision:

**GATE-03 (P3) Gate backdrop.** Concept: the compound blurred and darkened. Main: dimmed, not
blurred. Decision:

**BACKDROP-01 (P1) Boss fight backdrop (Solace).** Concept `combat_solace.jpg`: the double helix lit
pale against a rainy blue-grey city, green beams, readable; the wheels sit in front. Main: the helix
in near-black navy, a chain of white bead lights (BOSS-03), a few lit windows; the frame is
mostly black. Same cause as CMB-01 (`combat_backdrop.gd`, the city's light at the combat band).
Decision:

**BACKDROP-02 (P1) Site fight backdrop (Solace).** Concept `site_solace_night.jpg`: the Site
building (a clinic with the cross sign and helipad) lit and framed at the centre, a lit blue-grey
city around it. Main: generic dark blocks with neon roof outlines, no Site building in view.
Likely file: `backdrop_catalog.gd` (`place(...)` for a Site: which building and camera),
`combat_backdrop.gd`. Decision:

### Endings: run end, campaign won / lost (`run_end*.jpg`, `campaign_*.jpg`)
Refs: build `run_end`, `campaign_won`, `campaign_lost` (M13: a CELL BURNED / CORP DOWN stamp
poster, polaroids, story-uncovered paper notes, a small corp summary paper, New campaign / Back to
title); concepts `round20_raid_world/campaign_lost.png` (LOCKED A, ransomware lock in the corp's
house style), `round21_raid_world/campaign_dossier.png` (the audit dossier). Main's campaign end
lock and dossier come from the `campaign_end_lab` (Solace, 1.0), because the review pack's
`campaign_lost` frame catches the lock mid-tear.

**END-01 (P2) Run end, FLATLINED.** Build: the city drops to greyscale, the operative's polaroid
with a flatline, a big red FLATLINED stamp, a NETRUN paper slip with the tallies, a pink Back to HQ.
Main: a terminal `NETRUN FAILED - OPERATIVE LOST` panel over the full-colour city, a FLATLINED
sticker and a BACK TO HQ sticker inside it, tally chips, a heat line, plus a red DISPATCH voice strip
across the top. No concept image. View: the build's greyscale city and polaroid make the loss land;
main's panel explains more (permadeath, what is kept). Per the designer's principle a candidate for
"build layout in v2 language". Likely file: `netrun_scene.gd` (run end), `campaign_end/`.
Decision:

**END-02 (P3) Run end, clean exit (main only).** Main: `NETRUN COMPLETE`, a JACKED OUT sticker,
the same panel; the build has no clean-exit screen (it reuses the jack out). Consistent with END-01.
Decision:

**END-03 (P1) Campaign won.** Build: a `CORP DOWN` poster with the corp emblem crossed out in
pink spray, the crew's polaroids, a scrolling STORY UNCOVERED paper (the story beats' text), a
corp summary slip, New campaign. Main: the audit dossier (the won variant: polaroids
`Renewal Engine - OFFLINE`, `NODES AT THE END`, the crew; personnel list; annexes; AT LARGE stamp;
`MOST TROUBLESOME` sticky note), MAIN MENU and NEW CAMPAIGN stickers. View: main follows the
dossier concept (which was drawn for the loss); the won screen lacks a celebratory beat (the
build's CORP DOWN) and the story text is reduced to the intercept titles in ANNEX A. Likely file:
`scripts/ui/campaign_end/`. Decision:

**END-04 (P3) Campaign lost capture timing.** The review pack's frame (`hq.show_end()` + 12 frames)
lands inside the tear; the harness should wait for the lock's end state (MotionSkip) or the
dossier. Harness fix only (`tools/visual_qa/review_pack.gd _campaign_end`), not a game gap.
Decision:

**END-05 (P2) Ransomware lock.** Concept A: the losing corp's notice (`YOUR CELL HAS BEEN
PROCESSED`, the corp seal, HOME SERVER / NODES ENCRYPTED bar, `WIPE IN 00:02.80` countdown,
`PROCESSED` stamp) over the city in the corp colour, padlocks on the nodes, the defence stickers
curling off along the bottom. Main (Solace): a very close match in the Solace style (`TREATED`,
green notice, pink countdown and bar, padlocks on the top bar). Differences: the city behind is
a hex pattern rather than the map with padlocked nodes; no defence-sticker row. Likely file:
`scripts/ui/campaign_end/` (lock). Decision:

**END-06 (P2) Audit dossier.** Concept: a kraft folder on a dark desk, a CELL-03 / CLOSED tab, three
3D city polaroids (home server, a beacon, nodes at the end), personnel with class icons, deceased
crossed out in red, colour sticky notes (blue, pink, yellow, green), a heat chart, the CASE CLOSED
stamp, signature. Main: the same structure and copy, very close; differences: white paper on a
grey-white folder (concept: kraft), the polaroids are a flat grid, a 2D map shot and a portrait
(concept: city renders), sticky notes are plain white with blue ink (concept: coloured), the CASE
CLOSED stamp covers `(cell 01)` and part of the STATUS line, `HEAT ... at closure 82:` cut at the
left by the note. Build: the CELL BURNED poster. Likely file: `scripts/ui/campaign_end/` (dossier),
`polaroid.gd`. Decision:

### Motion (`MOTION-01.jpg` … `MOTION-10.jpg`)
Each strip: the motion lab's `--demo-anim=<id>` on both builds (Movie Maker 30 fps, one launch per
demo), 8 frames every 133 ms from the demo's start frame, the art pass on top, main below. The
lab's stage is small for the HUD-piece demos, so those strips show placement and timing, not
detail; an in-context capture (`hq_scene` / `netrun_scene` / `combat_scene` `--demo-anim`) is the
follow-up where a ruling needs it.

**MOTION-01 (P3) jack_in.** Same timing on both: the page cuts to the grid at ~267 ms, the cover
holds to ~800 ms, the page returns by ~933 ms. Main's cover carries the big corp line
(`SOLACE // THE RACK`, JACK-01); the build only a small `CONNECTING`. Decision:

**MOTION-02 / 03 / 04 (P3) card_hover, send_it_press, wheel_spin.** No visible timing difference
at the lab's scale; both lift / press / spin over the same frames. The look differences are the
static ones (CMB-02/04/06). In-context strips needed only if the designer wants them. Decision:

**MOTION-05 (P3) loot_fan.** Same: the three cards fan out from a stack at ~133 ms and settle by
~400 ms on both. Card faces differ (LOOT-01). Decision:

**MOTION-06 (P3) panel_in.** Build: the panel arrives with a bright scan band across it at ~133 ms.
Main: the panel appears at ~133 ms with no band (its kit's panel-in is a plain fade/scale). Likely
file: `scripts/ui/kit/terminal_window.gd` / `menu_motion.gd` (`panel_in` entry in
`content/config/ui_motion.tres`). Decision:

**MOTION-07 (P2) enemy_break.** Same beat timing (break at ~533 ms, the red hit line flies by
~667 ms). Main's in-context demo shows the combat backdrop **lit** (a coloured, readable 3D city)
for its first ~400 ms and then dropping to the near-black look of CMB-01 when the fight settles:
the lit city exists in main and is being darkened afterwards. Useful for CMB-01 / BACKDROP-01.
Likely file: `scripts/ui/arena/combat_backdrop.gd` (the settle / dim step). Decision:

**MOTION-08 (P3) victory_flash.** Build: VICTORY appears at ~267 ms over the unchanged scene.
Main: a white flash disc on the enemy wheel at ~133 ms, VICTORY at ~267 ms, OURS NOW from ~533 ms.
Same start; main adds beats. Decision:

**MOTION-09 (P3) card_stamp.** Both: the card lands on the wheel at ~267 ms and dissolves by
~533-667 ms; main's dissolve is the bible's bit stream into the hub (Dissolve A), the build's a
plain fade. Main follows the bible. Decision:

**MOTION-10 (P3) saved_stamp.** The lab's SAVED stamp sits outside the cropped stage on the build
and as a tiny corner stamp on main; no comparison possible at this crop. Low value; skip unless
asked. Decision:

## Mechanics the rules lack (listed, not built)
Differences whose reference needs a rule the game does not have (ART_REINTEGRATION_PLAN §3.2,
G1-G16). They stay listed until the designer approves a G-pass; any fix agent must leave them out.

| Id | What the reference shows | Needs |
|---|---|---|
| BOSS-02 | boss wheel with a parasite ring, docked satellites, status-stack tabs, two needles | G1 inner ring, G2 satellites, G3 parasite ring |
| CMB-02 / CMB-04 (part) | slice tier pips, slice states FROZEN / LOCKED / BURNING on the wheel; card type band WHEEL / HACK / SYSTEM | G4, G5 (tiers), G16 (card type band; main already draws a band, its words are not in the rules) |
| HQRUN-01 (mechanic text), HQRUN-05/06/07/08 (routes) | per-corp HQ mechanics: Meridian crane / train, Solace two strands, Halcyon switchback + eye, Orbital missile loop, DISPATCH sync strike | G12 |
| HQRUN-02 | a full compound route on today's HQ run (GDD 4.2 has the breach run) | G11 / G12 |
| GATE-02 (part) | the exploit-effect card (`PHASE 2 @ 66% ... BREACHED`) and cut slices on the boss preview for one Exploit per boss buff | G6 |
| SHOP-03 / SHOP-07 (part) | slice wheel sells only the top 3, top slice cheaper; removal by the bin replacing SHRED | G14 (main already shows TOP 3 ONLY and the bin: check against the rules) |
| SHOP-06 (part) | REPLACE? on an occupied socket destroys the old chip | G14 |
| RAID-01 / RAID-06 (part) | defence cards with INT, counts, EXPOSED nodes, IF PLACED forecast by wave | G8, G9 |
| GRID-05 (part) | the Grid's own Heat bar with COOL / NOTICED / FLAGGED / HUNTED and the next threshold | none (presentation), listed because the Grid HUD is "in progress" in the bible |
| END-05 (part) | the defence stickers curling off along the bottom of the lock | none (presentation) |

## Fix slices (provisional; nothing starts until the designer has ruled)
Grouped by file ownership so parallel agents never share a file. A slice takes only the ids the
designer has ruled on, in the ruled direction. "Opus" = visual judgement / porting a build layout
into the v2 language; "Sonnet" = mechanical placement / anchors / sizes.

| Slice | Files (owned) | Ids | Model |
|---|---|---|---|
| S-TITLE | `scripts/ui/title_scene.gd`, new `scripts/ui/kit/slot_picker.gd` | TITLE-02, SLOTS-01..04, STATS-01, END-04 harness note excluded | Opus |
| S-BACKDROP | `scripts/ui/kit/cyberdeck_background.gd` (title + overlay pages' city) | TITLE-01, LOOT-04, OPT-01 (backdrop part) | Opus |
| S-CODEX | `scripts/ui/kit/codex.gd` | CODEX-01 | Opus |
| S-NEWC | `scripts/ui/hq_scene.gd` `show_start` only, new `tile_picker.gd`, `planning_picker.gd` | NEWC-01..04 | Opus |
| ~~S-HQ~~ | none: HQ-01..10 superseded by the HQ design pass (designer 2026-10-05); the HQ-DESIGN agent owns the HQ | — | — |
| S-GRID | `scripts/ui/kit/city_map_overlay.gd`, `site_marker*.gd`, `grid_map_view.gd`, `city_minimap.gd`, `map_legend.gd`, `target_edge_marker.gd`, `content/config/city_config.tres` (Grid band) | GRID-01..03, GRID-06, GRID-12, GRID-13, RAID-04 | Opus (GRID-01/02), Sonnet (03/12/13) |
| S-GRID-HUD | `scripts/ui/hq_scene.gd` Grid side column, `city_grid_controls.gd`, `drop_layer.gd` | GRID-04, GRID-05, GRID-07..11 | Opus — after S-NEWC (same file); hold until the HQ design pass says how the Grid folds into the city raid view |
| S-RAID | `raid_paper.gd`, `corp_memo.gd`, `raid_intel_strip.gd`, `raid_holo.gd`, `asset_card.gd`, `raid_feed.gd`, `raid_playout_panel.gd`, `raid_verdict.gd`, `raid_report_pencil.gd`, `raid_drag_pencil.gd`, `raid_beats.gd` | RAID-01..03, RAID-05..12 | Opus (RAID-01/10), Sonnet (stamps / anchors) |
| S-NETRUN | `scripts/ui/netrun_scene.gd` (raid interlude, shop, event, loot, run end pages), `route_node_panel.gd`, `operative_dossier.gd`, `zine_stamp.gd` | RAID-13, RAID-14, ROUTE-02, ROUTE-03, ROUTE-06, SHOP-01, SHOP-06, EVT-01..03, LOOT-02, LOOT-03, END-01, END-02 | Sonnet (stamps / anchors / SHOP-01), Opus (END-01, EVT) |
| S-ROUTE | `netrun_map_view.gd`, `route_overlay.gd`, `route_ink.gd`, `route_legend.gd` | ROUTE-01, ROUTE-04, ROUTE-05 | Opus |
| S-CARDFACE | `scripts/ui/kit/zine_card.gd`, `loot_sheet.gd`, `deck_view.gd`, `shop_item.gd`, `shop_pegboard.gd`, `slice_stock_wheel.gd`, `inspect_popup.gd` | LOOT-01, SHOP-02..05, SHOP-07, SHOP-08, DECK-01, DECK-02, CMB-04 (card part) | Opus (one card face for hand, loot, shop, viewer) |
| S-WHEEL | `scripts/ui/wheel/*`, `palette.gd`, `palette_skins.gd` (slice tokens), `hud_wheel_layer.gd`, `spinner_view.gd` | CMB-02, CMB-03, CMB-09, BOSS-04 | Opus |
| S-ARENA | `scripts/ui/arena/combat_backdrop.gd`, `backdrop_catalog.gd` | CMB-01, BOSS-03, BACKDROP-01, BACKDROP-02, MOTION-07 | Opus |
| S-COMBAT-HUD | `scripts/ui/combat_scene.gd`, `send_it_sticker.gd`, `hud_name_sticker.gd`, `ram_bar.gd`, `hud_result_chips.gd`, `hud_dialog_panel.gd`, `tutorial_overlay.gd` | CMB-05..08, CMB-10..18 | Sonnet (placement), Opus (CMB-14/16) |
| S-MODAL | `glass_scrim.gd`, `confirm_dialog.gd`, `pause_menu.gd`, `settings_panel.gd` | CONFIRM-01/02, PAUSE-01..04, OPT-01 (framing), OPT-02/03 | Sonnet |
| S-HQRUN | `scripts/ui/hq_run/hq_run_view.gd`, `central_server_gate.gd`, `scripts/city3d/hq_compound_stage.gd`, `city_iso_camera.gd` | HQRUN-01 (title + key only), HQRUN-03, HQRUN-04, HQRUN-06, HQRUN-08, GATE-01..03 | Opus |
| S-END | `scripts/ui/campaign_end/*` | END-03, END-05, END-06 | Opus |
| S-MOTION | `content/config/ui_motion.tres` entries, `terminal_window.gd` / `menu_motion.gd` | MOTION-06 (and any motion ruling) | Sonnet |
| S-JACK | `scripts/ui/kit/jack_sequence.gd`, `daemon_tray.gd` | JACK-01, DAEMON-01 | Sonnet |
| Harness | `tools/visual_qa/review_pack.gd` | END-04 (wait for the lock's end state) | Sonnet |
| done | — | BOSS-01 (FIX-REDS) | — |

Collisions to watch: `hq_scene.gd` is shared by S-NEWC, S-GRID-HUD and the HQ design pass (run S-NEWC
first, or split the file first); `netrun_scene.gd` is one slice on purpose.

## Harness
- `tools/visual_qa/parity_sheet.py` (new): builds `<screen>.jpg` (full pictures side by side, ids
  marked) and `<ID>.jpg` (one crop sheet per difference) from the two packs, lab frames and the
  concepts; `--motion id=demo,...` builds the motion strip pairs. `tools/visual_qa/parity_pairs.json`:
  the screen list, references and difference rectangles (re-run after a fix to refresh the sheets).
- Capture, main: `python tools/visual_qa/capture_pack.py --out <dir> -j 1 --no-lint --save-size 1280x720`
  (60 screens, about 10 min). HQ run pages, gate and combat backdrops (not in the review pack):
  `python tools/run_windowed.py --log <f> -- --resolution 1280x720 res://tools/art_pipeline/hq_run/hq_run_lab.tscn -- --out=<dir> --states=run_solace,run_meridian,run_halcyon,run_orbital,run_rebel_cell,full_solace,gate_solace,hq_solace,site_solace`.
  Campaign end lock and dossier: `python tools/run_windowed.py --log <f> -- --resolution 1280x720 res://tools/design_lab/campaign_end_lab.tscn -- --out=<dir> --corps=solace --what=lost --scales=1.0`.
- Capture, art pass: from a scratch copy (`git archive art-pass | tar -x`, here
  `%TEMP%\parity\artpass`, imported headless twice): inside the copy,
  `python tools/visual_qa/capture_pack.py --out <dir> -j 1 --no-lint` (53 screens, about 3 min;
  screen names as main's except modem* = mainframe*).
- Motion: per demo, `python tools/run_windowed.py --log <f> -- --resolution 1280x720 res://tools/design_lab/motion_lab.tscn --write-movie <dir>/<demo>/f.png --fixed-fps 30 --quit-after 75 -- --demo-anim=<demo>`
  on each build (the lab takes one demo per launch), then `parity_sheet.py --art <art root> --main <main root> --motion MOTION-01=jack_in,...`.
- Sheets: `python tools/visual_qa/parity_sheet.py --art <art pack>/1.0_mouse_re-off_none --main <main pack>/1.0_mouse_re-off_none --concepts <copy>/docs/concepts --pairs tools/visual_qa/parity_pairs.json --out docs/art_review/PARITY --art-rename mainframe=modem,mainframe_socket=modem_socket,mainframe_remove=modem_remove,mainframe_overwrite=modem_overwrite`
  (the pairs file uses main's screen names; `--art-rename` maps the four shop screens to the art pass pack's old names,
  which tests/unit/test_names_pass.gd keeps out of tools/).
  The `file:` references in the pairs file point at this run's lab frames under `%TEMP%\parity\lab_main`;
  re-capture there (or edit the paths) before rebuilding those sheets.
