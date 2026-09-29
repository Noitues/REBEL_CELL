# W8c — Netrun pages and run end (branch `art/w8c-netrun`)

ART_BIBLE §11 Route / Loot / Modem / Events / Raid interlude / Run failed, §6.4–§6.8, §8 T4,
§10, §12. Presentation only: no rule, content value or save format changed.

## Pictures

| File | What it shows |
|---|---|
| `before_after/<screen>_<combo>.jpg` | W10 harness, before (`art-pass/docs/art_review/W10/baseline/full`) and after, for `route`, `loot`, `modem`, `modem_socket`, `event`, `raid_interlude`, `run_end` at 1.0 mouse, 1.6 pad, 2.0 mouse and 1.0 greyscale (28 sheets). |
| `flatlined_t4_strip.jpg` | The FLATLINED T4 (`--demo-w8c-end=died`, 30 fps): the Polaroid flatlines, the city greys, FLATLINED slams at hero size, then the receipt, the fate line and Back to HQ. |
| `shred_no_reflow_strip.jpg` | A shred by drag (`--demo-shop --demo-anim=drag_shred`): the carried card leaves its ghost; nothing reflows under the pointer until the viewer closes. |
| `lint_report_after.md` | W10 runtime lint over the after pack. No finding is in a W8c file (route_legend is W8b's, the SAVED stamp is `fx.gd`'s, the glass title is W8a's). |

At 2.0 every page scrolls inside its window (MORE BELOW): the top bar takes two rows there (W8b, `hud_bar`).

## What changed (files)

- `scripts/ui/netrun_scene.gd` (owned):
  - **Route:** a compact list: the button says only what the node is ("1 Fight"), and one row of icons and short words holds its Heat, where it leads, "(same as N)", and what only it reaches. GRID VIEW and Save & quit are Tertiary. Map mode is on (W7), and reduce motion cuts the route and raid cameras.
  - **Loot:** the modal is 70% of the screen's width, with offers at hover size or more. The LOOT graffiti keeps 140% slack and a gap for its drips. The pick stamps TAKEN, then flies to CARDS. Skip is Secondary. The Firmware slot is picked on slot tiles.
  - **Modem:** laid out by containers, with the baked sign. Two columns at 1.0; one column scrolling at 1.15 and above. Chips are at `body`, the socket list is slot tiles, and there's no wallet. LEAVE THE MODEM sits under the spinner in the REMOVE window.
  - **Events:** paper sized to its words, Plex ≤ 70 columns, DISPATCH mono ≤ 64 columns. The speaker appears once and the subtitle doesn't repeat the story. The numbers show once as ▲/▼ chips, and the CHOSEN stamp carries no picture. The page is a calm zone and keeps the safe margin.
  - **Raid interlude:** one TilePicker for the asset to deploy plus "Deploy here" on each row. No empty labels (a designed empty note instead). START DEFENSE is Primary, and there's map mode.
  - **Run end:** a RunEndStage.
  - **Seed:** a CodeField.
  - **Tips:** input-aware.
  - **W8a APIs:** `open_modal` and `after_modals`.
- New kit pieces:
  - `slot_picker.gd`: a TilePicker of spinner slots.
  - `event_outcome_row.gd`: OutcomeRow with ▲/▼.
  - `run_end_stage.gd`: the T4 run end, the grey grade and the receipt.
  - `verdict_stamp.gd`: a hero rubber stamp.
- `buy_button.gd`: the locked state with NEED n · HAVE m, the pad glyph as its own element, the caption floor, and high contrast.
- `modem_sign.gd`: draws `assets/art/netrun/modem_sign.svg` in six bands, so the warm-up still strikes tube by tube. The notes are gone, and there's a subtitle when translated.
- `daemon_tray.gd`: the title is shown once, with scaled sizes.
- `flight_fx.gd`: a word-only stamp and the caption floor.
- `event_held_mark.gd`: high contrast.
- `assets/art/netrun/modem_sign.svg` (+ force-tracked `.import`, 2x): an original neon design.
- `content/config/ui_motion.tres`, `ui_motion_data.gd` REQUIRED_IDS, `motion_lab.gd` DEMOS: `run_end_flatline` (T4, 2.4 s).
- `tools/visual_qa/review_pack.gd`: `modem_socket` focuses the tiles (it cast to OptionButton).
- `assets/text/strings.csv`: appended keys only. `lint_baseline.json` lowered.
- Tests: `test_art_w8c_netrun.gd` (29 tests), plus updates to 14 older tests that asserted the replaced looks (listed in the commits).

## ART_BIBLE §14 checklist

| Item | Result |
|---|---|
| §3/§4/§5 tokens only | **Pass**: static lint 0 in every W8c file. The literal sizes (LEAVE THE MODEM 32, PLAY IT SAFE 24, the DISPATCH strip colours, the stamp floor 10) moved to steps and tokens. |
| Materials not mixed | **Pass**: no native control on paper or glass. Paper (LEAVE tag, stickers) is taped onto glass. |
| Focal order / one primary | **Pass**: route (map, then list), loot (modal), Modem (sign, windows), raid (START DEFENSE Primary), run end (stamp, then receipt, then Back to HQ Primary). |
| Six states | **Pass** via the kit: SlotPicker/TilePicker, buttons, and BUY stickers (hover, flap, locked, refused via price_refused). |
| 1.0 / 1.6 / 2.0 | **Pass**: no clipping, overlap, text < 12 px or width overflow (tested on 8 pages × 3 scales). 1.6/2.0 scroll vertically with a hint. |
| Contrast §3.7 | **Pass**: locked BUY keeps INK on paper; TEXT_MID captions; lint shows no W8c findings. |
| Greyscale | **Pass**: route icons + words; ▲/▼ on outcomes; lock + NEED/HAVE; verdict by word (see the grey sheets). |
| Pad | **Pass**: prompt bar, the glyph apart from the price, no "click"/"drag" in tips (tested). |
| Motion / tiers / reduce effects | **Pass**: T4 2.4 s, skippable; reduce effects gives the end state; reduce motion cuts cameras. Loot stamp T2; sign flicker T0 is static under reduce effects. |
| No placeholder / leftovers | **Pass**: no bar after a choice (tested); the city shows behind the run end. |
| Review stills | **Pass** (this folder). |

## Decisions (one line each)

1. §11 Route: the list is one button per choice ("1 Fight") plus one icon+word row; the words stay in the tooltips and map labels.
2. §6.4: GRID VIEW and Save & quit are Tertiary, Skip and "Deploy here" are Secondary, START DEFENSE and Back to HQ are Primary.
3. §11 Loot: "hover size" means at least `ZineCard.HOVER_SCALE` × LOOT_CARD, filling the row up to 1.4×; the lettering is max(fill, text size).
4. §4.3 rule 5: the loot graffiti is fitted to the modal's inner width ÷ 1.4, so the English words keep 40% slack.
5. §11 Loot: the celebration is a T2 TAKEN stamp on the picked card before it flies (FlightFx's stamp), and the loot page's hold covers stamp + flight.
6. §4.3 rule 5: the Modem sign's art is English; a GLASS caption subtitle appears only when the locale translates MODEM/CYBER/SHOP.
7. §11 Modem, critique 52: BUY/SHRED stickers are always buttons; the sign's decorative notes were removed rather than made into drop targets.
8. §4.2: microchip and Daemon tiles letter at `chip_text_scale` = text scale × 15/12, so ZineCard's caption step draws at `body`, without editing W4's file.
9. §5.3: the Modem keeps two columns up to text scale 1.15, then one column scrolling in its page with MORE BELOW (a fixed 1280×720 can't hold four windows of body text at 1.6).
10. §6.7/§3.7: out of reach = paper kept (PAPER_ALT) + DISABLED edge + lock badge + "NEED n · HAVE m" on the sticker; SHRED with an empty deck shows only the lock.
11. §6.5: the Modem socket and Firmware loot use SlotPicker (TilePicker tiles: number, slice icon, "CRIT 12", a chip mark); the full slot name is the tile's tip.
12. critique 28: raid assets are picked once (DeployPick) and each active row gets one "Deploy here"; the chips still drag.
13. critique 28: an empty RUN ASSETS / ARMORY row is hidden; the ARMORY row stays (saying "empty: drop a placed asset here") while assets are placed, as the drop target.
14. §6.5: the start page's seed is a CodeField limited to 6 digits (the old SpinBox's 0–999999).
15. §11 Events: a leading "SPEAKER:" is dropped from the event's title and story (the plate says who, once); the band no longer says the story.
16. §3.1: good/bad on choices is ▲/▼ drawn before each amount (EventOutcomeRow), since OutcomeRow is W3's file.
17. critique gifs/24: the chosen stamp is the word CHOSEN over the choice with no snapshot (FlightFx.stamp_on `picture=false`).
18. §11 Events: the story sits beside the choices when both fit (paper ≤ 70 cols + 300 px of choices), else the choices go under it.
19. §11 Run failed: the grey is a desaturate + 35% dim shader over the backdrop inside the run-end page (W7 has no grey context); a clean exit keeps the colour.
20. §8 T4: reduce effects shows the run end's end state at once and the page's own entrance supplies the cross-fade.
21. §6.6: the verdict stamp is a double-framed rectangle at `hero` (64 × text scale, ≤ 96), −5°, with a 140% slack fit and a floor at `display`.
22. §11 Run failed: the stats receipt is W8a's RunReceipt (icon + number fields); the fate words sit beside it in Plex (≤ 44 cols).
23. §12: input-aware tips keep their base and drag kind as metas and are reworded on `Settings.hints_changed`.
24. PageTransition.settle ends the run-end T4 through the Typing meta (the stage keeps its tween there); a dedicated hook is requested from W8a.

## Overlap with ANIM-R5 netrun (commit `1c749d2`, not merged)

| ANIM-R5 item | W8c | On merge |
|---|---|---|
| B1: event paper sized to its text, `EventText`, `VC_CHARS_AFTER_SHAPING` | the same line and name; the paper height via `_fit_paper` (ZinePanel now sizes itself after W8a) | keep one; the identical line merges cleanly |
| B2: subtitle lines per screen | untouched | take theirs |
| B3: run end over the city, verdict stamp (same words), permadeath line, Heat reason | RunEndStage (stage, stamp, receipt, grey) | keep W8c's `_show_end`; put `end_fate()` + `heat_reason()` into `stage.fate_label.text`; drop their ForecastStamp verdict |
| B4: typing cap / settle | untouched; RunEndStage keeps a tween under `Typing.META`, which `Typing.any_typing` may count | check that `words_typing()` ignores the stage |
| B5: slower flights, landing pulse, loot waits for the pick | loot hold also bounded by the pick (+ its TAKEN stamp) | keep their bound and add `sold_stamp` |
| B6: route choices inert mid-move | untouched; `_fill_route_choices` rewritten (row per choice) | keep both: their focus release sits in `_refresh_route_choices` |
| B9: icon + word pairs under a choice | `_ahead_row` rewritten with the same node names (`Ahead_<kind>` → Icon/Word) plus next kinds and twins | keep W8c's `_ahead_row`; their `AHEAD_SHORT` = W8c's `ROUTE_SHORT` |
| B11: Modem socket label | SocketRow/SocketWord with a SlotPicker | keep W8c's (tiles); take their SOCKET_TIP words |

## Couldn't do / known gaps

- The UPGRADE viewer's price on its button and its marker circle (critique 55) live in `spinner_view.gd` (W3). Requested.
- The DeckView (W4) says "Left click / Right click" and ends below the canvas at 2.0. anim4b's layout test stays at 1.6 for that.
- At 2.0 every page scrolls, because the top bar takes about 200 px (W8b).
- The grey grade covers the page area only. The subtitle band strip above it keeps the city's colour.
- One-column Modem at 1.6/2.0: the CARDS window leaves more than 25% empty beside 3 cards.
- The high contrast look of the paper pieces (verdict stamp, receipt) follows W9's open question.

## Bible rules I'd question

- §11 Loot: "cards at hover size" is ambiguous (hand hover 1.12× or the detail size). I read it as ≥ HOVER_SCALE and filling the modal.
- §8 T4 "becomes a cross-fade" under reduce effects, but reduce effects also stops motion. Suggest "shows its end state; the page's own cross-fade brings it in".
- §5.2 "one line" subtitle band vs events: suggest the band stay empty on pages whose words are the page itself.
