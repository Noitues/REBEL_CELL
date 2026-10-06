# M14 parity audit: art pass vs main (GAPS)

Status: **INTERIM** (2026-10-05). Screens compared so far: title, title confirm, campaign slots,
new campaign (+ picker open), HQ, plus the two findings the orchestrator passed on (shop, boss
phase 2). Every other screen is captured on both sides; the comparison continues in the same
format below.

Designer rulings this file follows (DECISIONS 2026-10-05 "the M14 audit is a side-by-side art-pass
parity audit", and the orchestrator's relay of the later ruling): every difference is described
neutrally, both sides; where it helps, an honest view of which reads better and why; **nothing is
fixed until the designer has ruled** on each id (`Decision:` left empty).

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
Decision:

**TITLE-02 (P2) MORE panel crowds the verb stickers.** Concept: a clear gap (~40 px at 1080p,
~25 px at 720) between OVERTHROW and the MORE panel, MORE sits lower. Main: MORE's top edge almost
touches the OVERTHROW sticker. View: concept reads better (the three verbs are the hero group).
Likely cause: `title_scene.gd` `_place_bottom` / `FOOT_GAP` / `_align_verbs`. Fix: place MORE from
the foot up with the concept's gap, or nudge the verb column up.
Decision:

**TITLE-03 (P3) CONTINUE summary line.** Concept: `slot 1 // Halcyon Civic // run 9 // Heat 58`
(slot named first). Main: `Solace Biosystems // run 1 // Heat 0` and a `>` caret on the focused
chip (the caret is the UI kit's focus rule). Fix if wanted: prefix the slot in
`title_scene.gd` `slot_words`. Decision:

**TITLE-04 (P3) Version line.** Concept: `REBEL_CELL v0.33.0 // build <date> // godot 4.7`. Main:
`REBEL_CELL v0.9.0 // cell uplink`. Content only. Decision:

### Title: delete-slot confirm (`title_confirm.jpg`)
Ref: concept `round33_ui_chrome/abandon_dialog.png` (the build has no such dialog; it is the same
kit dialog as main's pause-quit confirm).

**CONFIRM-01 (P2) Scrim.** Concept: the page behind is dimmed, still sharp. Main: blurred
(`GlassScrim`, `Palette.SCRIM_BLUR_PX`) and dimmed. View: both read; the blur hides the title sign
entirely, the concept keeps the context visible. Likely cause: `scripts/ui/kit/glass_scrim.gd`
(shared by every modal: changing it changes all modals). Decision:

**CONFIRM-02 (P3) Dialog body.** Same kit, same layout. Differences: main adds a divider rule above
the buttons (concept has one too, fainter and full width); main's question is set slightly larger;
main's stickers are centred as a pair, the concept's sit under the two cost columns. The verb is
DELETE (main) where the concept's run-abandon says BURN IT: different action, both fine.
Likely file: `scripts/ui/kit/confirm_dialog.gd`. Decision:

### Campaign slots (`slots.jpg`)
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
Decision:

**SLOTS-02 (P2) Load / Delete.** Build: pink filled `Load` (primary) and a red-edged `Delete`.
Main: two equal terminal buttons, `Load` with the lime focus brackets. View: main follows the v2
rule (one sticker verb per screen, the rest terminal chips); the build's colour split marks the
destructive action more clearly. Same file as SLOTS-01. Decision:

**SLOTS-03 (P3) Page title.** Build: the REBEL_CELL logo top left. Main: a `CAMPAIGN SLOTS` title
sticker (the v2 sticker-title rule, as THE GRID / RAID SETUP). View: main is consistent with v2.
Decision:

**SLOTS-04 (P2) Panel height.** Main's panel runs from y 160 to the ticker with the lower half
empty (hex-dump texture only); the build's panel wraps its content and shows the city below.
Likely cause: `title_scene.gd` `_page` / `SLOTS_W` (the page fills the height). Fix: size the
panel to its content. Decision:

### New campaign (`new_campaign.jpg`, `new_campaign_picker.jpg`)
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
emblems from the art pass's own assets). Decision:

**NEWC-02 (P2) Page header.** Build: the REBEL_CELL logo, a pink `TRUST NO ONE` pencil scrawl and
a pink START sticker top right with `SHARE CODES` beside it. Main: a `NEW CAMPAIGN` title sticker,
a yellow `TRUST NO ONE` pencil, the pink `New campaign` sticker under the form. View: main's title
sticker matches the v2 page-title rule; the build puts the one verb where the eye ends (top right).
Decision:

**NEWC-03 (P2) Seed, daily run, share codes.** Build: seed lives in a collapsible SHARE CODES box
at the bottom (seed stepper, code field, copy); no daily run panel. Main: `City seed` field +
`Next seed` in the form, plus two lime-edged panels `TODAY'S RUN` and `SHARE CODES` side by side
under it. Main has more here (daily run is a main feature). View: main's lime panel edges are as
loud as the focus colour (lime = focus in the v2 kit), which competes with real focus.
Likely file: `hq_scene.gd show_start`. Decision:

**NEWC-04 (P1) Picker opened.** Build: "picker" is the tile row (no popup). Main: the target
OptionButton's popup list (Godot default popup restyled). Follows NEWC-01. Decision:

### HQ (`hq.jpg`)
Ref: art pass build `hq` (no concept image for the HQ page; chrome per `round33_ui_chrome/ui_kit.png`).

**HQ-01 (P1) Top resource strip.** Build: each resource is a coloured paper tag (cream, pink,
yellow) with a stencil number. Main: dark navy terminal chips with cyan edges (the v2 kit's
"terminal resource strip", as in `round32_ui_chrome/city_map_hud.png`). View: main follows the
v2 kit; the build's tags are louder and more "zine". Likely file: `scripts/ui/kit/hud_bar.gd`,
`hud_stats.gd`, `hud_skin.gd`. Decision:

**HQ-02 (P1) WANTED poster overlaps JACK IN.** Build: JACK IN disc top right, WANTED poster below
it, clear of each other. Main: the poster sits top right against the top bar and its right edge
runs into the JACK IN disc. View: main's overlap is a defect whichever look is chosen. Likely
file: `scripts/ui/hq_scene.gd` (HQ layout), `scripts/ui/kit/heat_poster.gd`. Decision:

**HQ-03 (P2) PIRATE RADIO.** Build: a taped paper note, pencil-script header, typewriter body.
Main: a terminal panel `> PIRATE RADIO`, Plex sans body. View: the v2 kit gives paper to
intercepted corp documents and terminal to the Cell's systems; pirate radio is neither, so this is
a designer call. Likely file: `hq_scene.gd` (radio block), `terminal_note.gd` / `zine_note.gd`.
Decision:

**HQ-04 (P2) Crew cards.** Build: polaroid with a flat illustrated hooded silhouette, a pencil
`RANK 0`, stencil name, class line, HP bar, deck/daemon icons. Main: polaroid with the v2 portrait
bust (`round39_portraits/portraits_classes_v2.png`, LOCKED), caption `Breaker 1 R0` in tiny type,
name, class/rank line, HP bar, `HP 60/60 · DECK 10 · DAEMONS 0` text. Main's portraits follow the
locked v2 set. Main's roster panel is wider than its cards (empty right third). Likely file:
`scripts/ui/kit/crew_card.gd`, `polaroid.gd`, `operative_dossier.gd`. Decision:

**HQ-05 (P2) Menu panel rows.** Main's CYBERDECK panel wraps `Scrub Heat -5 · pay 25` onto two
lines (`25` alone on the second); the build fits it on one. Main's headers carry the v2 `> ` caret
and square (kit rule). Likely cause: main's panel is narrower than its row at 1.0
(`hq_scene.gd`, menu column width). Decision:

### MAINFRAME shop (`mainframe.jpg`; only the orchestrator's finding so far)
Refs: build `modem`; concept `round34_firmware_daemons/shop_v5.png`.

**SHOP-01 (P1) Pencil note over the clerk's line.** Concept: the yellow pencil
`ASK ABOUT THE BACK ROOM` sits below and right of `CYCLES ONLY.`, clear of it. Main: at 1.0 the
note's first line runs over the end of `CYCLES ONLY.` (the full stop and the Y are covered).
Build: no clerk. Likely cause: `scripts/ui/netrun_scene.gd` `CLERK_NOTE` placement (~l.3558), the
note anchored to the line's right instead of under it. Fix: anchor the note under the last clerk
line, offset right, as in the concept. Decision:

### Combat, boss phase 2 (`combat_boss_p2.jpg`; only the orchestrator's finding so far)
Refs: build `combat_boss_p2`; concept `round41_wheel_stack/combat_worst_case_v4.png`.

**BOSS-01 (P1) Guard-arc marker over the HP plate.** Main: the green guard-arc end marker (the
triangle) sits on the first digits of the boss HP `1395/1475`. Build and concept: nothing over the
HP value. **In progress: FIX-REDS** (a separate agent is fixing it). Decision:

## Mechanics the rules lack (listed, not built)
(Filled as the remaining screens are compared; first candidates seen while capturing: the HQ run
pages' per-corp mechanics (round 43 "climb the helix", "crane + train"; GDD has the HQ run but
not the per-corp mechanic), the boss phase-2 satellites / inner ring / status-stack tabs of
`combat_worst_case_v4.png`.)

## Fix slices (provisional; nothing starts until the designer has ruled)
Grouped by file ownership so parallel agents never share a file:
- **S-TITLE** (`scripts/ui/title_scene.gd`, `scripts/ui/kit/slot_picker.gd` new): TITLE-02/03/04,
  SLOTS-01..04. Opus (visual; SlotPicker port).
- **S-BACKDROP** (`scripts/ui/kit/cyberdeck_background.gd`, the title's city): TITLE-01. Opus.
- **S-NEWC** (`scripts/ui/hq_scene.gd` `show_start` only, `tile_picker.gd` / `planning_picker.gd`
  new): NEWC-01..04. Opus.
- **S-HQ** (`scripts/ui/hq_scene.gd` HQ layout, `heat_poster.gd`, `crew_card.gd`, `hud_bar.gd`):
  HQ-01..05. Must not run beside S-NEWC (same file): sequence them, or split hq_scene first.
  Sonnet for HQ-02/05 (mechanical layout), Opus for HQ-01/03/04 if the designer picks a change.
- **S-MODAL** (`glass_scrim.gd`, `confirm_dialog.gd`): CONFIRM-01/02. Sonnet.
- **S-SHOP** (`scripts/ui/netrun_scene.gd` shop block): SHOP-01. Sonnet.
- BOSS-01: FIX-REDS (in progress).

## Harness
- `tools/visual_qa/parity_sheet.py` (new): builds `<screen>.jpg` and `<ID>.jpg` from the two packs
  and the concepts; `tools/visual_qa/parity_pairs.json`: the screen list, references and the
  difference rectangles.
- Capture, main: `python tools/visual_qa/capture_pack.py --out <dir> -j 1 --no-lint --save-size 1280x720`
  (60 screens). The HQ run pages and the Central Server gate (not in the review pack):
  `python tools/run_windowed.py --log <f> -- --resolution 1280x720 res://tools/art_pipeline/hq_run/hq_run_lab.tscn -- --out=<dir> --states=run_solace,...,gate_solace`.
- Capture, art pass: from a scratch copy (`git archive art-pass | tar -x`, here
  `%TEMP%\parity\artpass`, imported headless): `python tools/visual_qa/capture_pack.py --out <dir> -j 1 --no-lint`
  run inside the copy (53 screens; screen names as main's except modem* = mainframe*).
- Sheets: `python tools/visual_qa/parity_sheet.py --art <art pack>/1.0_mouse_re-off_none --main <main pack>/1.0_mouse_re-off_none --concepts <copy>/docs/concepts --pairs tools/visual_qa/parity_pairs.json --out docs/art_review/PARITY`.
- Motion: the motion lab (`--demo-anim=<id>`, one launch per demo, Movie Maker 30 fps) captured on
  both for jack_in, card_hover, send_it_press, wheel_spin, loot_fan, panel_in, enemy_break,
  victory_flash, card_stamp, saved_stamp; strips not yet compared.
