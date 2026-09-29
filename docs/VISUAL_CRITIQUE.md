# REBEL_CELL: visual critique (pack aa51ad2)

Scope note: every still (76 at 1.0, 16 at 1.6 with controller, 21 scrambled), all 11 frame strips, and a 20-frame contact sheet of each of the 25 GIFs have been reviewed. GIF timings are read from the frame timestamps, so they're accurate to about ±50 ms.

---

## 1. First impression

The game has a real identity. The isometric neon city (title `01`, grids `19`/`64–68`, the HQ diorama in `05`/`21`) is the strongest asset in the pack and looks trailer-grade. The zine layer (sticky-note top bar, drip graffiti SEND IT / LOOT / VICTORY, marker circles in `55`, the crossed card in `53`) gives the game a voice most deckbuilders don't have.

It does **not yet look finished**, though. The quality is uneven. Combat, the Modem, the Grid and HQ look designed. Campaign select (`02`), New campaign (`03`), Stats (`18`), Codex (`16`), both pause menus (`10`, `40`), FLATLINED (`51`) and the campaign end screens (`62`, `63`) look like debug text dumps sitting in large empty boxes.

The zine-vs-terminal split is the right idea, but it isn't applied by rule. Terminal panels hold cream zine cards, and zine pages hold native dropdowns. Many small readouts sit at roughly 7–9 px, which works against the "readability over spectacle" goal.

---

## 2. Per screen (INDEX order)

**01 Title.** The eye goes to the city first, then the drip logo. That's right. The taped note and NEVER SLEEP graffiti float in the gap between the two panels with nothing anchoring them. The version string and the Continue line's stat glyphs are too small and low-contrast. The panels are semi-transparent over a very busy backdrop, so darken or blur the city behind them by about 30%.

**02 Campaign slots.** This is a plain text list. "Slot 1: Solace Biosystems, Heat 0, ICE 0, 0 runs, active" should be a card with the corp colour, a Heat bar and the run count laid out as fields. **Delete uses the same power icon as Quit and has the same visual weight as Load**, which is dangerous. Make it a small, secondary red-outline button.

**04 Target picker.** The open dropdown lists a single item, "Solace Biosystems", and nothing else. The locked corporations are invisible. That's a missed tease: show all five as corp-colour tiles, with the locked ones greyed, a padlock, and "unlock at the Black Market (140)".

**03 New campaign.** The config row is five native-looking dropdowns and spinners squeezed onto one line, and it reads as a dev tool. Give each picker a labelled tile, and show the corp picker as a row of corp-colour swatches or logos. The Share codes panel and the Profile records panel are mostly empty space.

**05/06/07/21 HQ.** This is a strong composition: menu, diorama monitor, WANTED poster, and the round JACK IN stamp, which is a great primary CTA. Problems:
- The Crew panel shows two dossiers and leaves about 40% of its width empty. Use three columns, or narrow the panel.
- The "MORE BELOW" pill overlaps content.
- Diorama tier labels and pips are about 7 px and unreadable.
- Heat 62 / FLAGGED in `21` is drawn in **green**, and green reads as "good". Heat should run from neutral to amber to red as the band rises.
- "RAID PENDING: Collections: Trespass (6)" wraps onto three lines in the menu.
- Black Market (`06`/`09`): about 20 identical outlined text buttons with no grouping and no icons. Affordable vs not is shown only by brightness. Add a lock or price-red treatment, and group items into Recruit / Boosts / Unlocks with headers.

**08/14/15 Dossiers and roster.** The class portraits have distinct colours, which is good. The silhouettes are near-identical, though, so class reads only through colour. The Polaroid caption repeats the name printed below it.

**10/40 Pause.** A large box that's about 60% empty, with the raw string `RC1-solace-0-1-home_standard-breaker` printed in it. Shrink the box to fit its content, and put the code behind a "Copy campaign code" button.

**11/12/13, 57/58 Loadout (HQ and in-run).** The DECK and SPINNER tabs of the same modal open at **different widths** (`57` is about 680 px, `58` about 520 px), so switching tabs makes the frame jump. The shop shows through on the right of `58`. The deck tab leaves its right third and bottom half empty. Fix the modal at one size and scale the wheel up to fill the spinner tab. In the deck view, card text truncates ("Blocked whil…") and the first row's titles are clipped by the header. The spinner view (`12`) is nice, but the WANTED poster pokes out from behind the modal edge, so the modal needs a full-screen scrim. In rank 3 (`13`) the inner-ring labels ("X2", "PIE") are tiny and cryptic, and the chip label **"Accelera/tor" breaks mid-word**.

**16 Codex.** A wall of monospace text about 1,200 px wide, with section headers the same size as body text. Use two columns and real headings, and show slice glyphs at 24 px next to each entry. This screen should look like the zine's reference page, not a log file.

**17 Options.** Toggles sit at the far right edge, about 1,100 px away from their labels, so it's hard to track which toggle belongs to which setting. The off state is a small dot while the on state is a pill, so the toggle style is inconsistent. The text-scale slider has no value label, and "1.6×" should be shown.

**18 Stats.** Achievements use ASCII "[ ]" checkboxes, and "no runs yet" sits in a large empty sheet. This needs a pass: sticker badges for achievements, and a stats grid.

**19/20 City Grid.** This is the best system screen. The iso map, tier hexes, leader-line labels and legend all work. Problems:
- Two magenta primary buttons (RAID SETUP and JACK IN) compete. Pick one primary per state.
- In RUNS OPEN NOW, the "CLAIM / OPENS 1" chips float between rows instead of sitting inside them.
- On Solace, the sites, links and routes are all green on a green city, so there's little separation.
- The left cluster labels overlap in `20`.
- Heat 62 isn't reflected anywhere on the map. Consider a red vignette or patrol lights.

**22/23 Raid setup.** The dashed "IF THE RAID RUNS NOW: HOME HIT" stamp is excellent, and it flips to ALL HOLD in `23`, which is clear cause and effect. The node list is **clipped mid-row** ("HP 30 > 25 HOLDS" is cut off) while the panel below is empty. Placed assets show as roughly 16 px circles on the map, so make them 28 px and add the asset glyph.

**24/25/26 Raid playout.**
- Damage numbers and the collector glow pile up on top of node labels.
- The stamp still says **"IF THE RAID RUNS NOW" during and after the playout** until late. It should switch to "LIVE" and then "RESULT" immediately.
- The disabled Continue is magenta at about 30% opacity and looks like a rendering bug. Use a grey outline with a lock or "wait" label.
- In `26` the camera ends framed on empty road.

**27 Route.** Node-type icons read well. YOU ARE HERE floats in empty space rather than on a node. The route list ("[2] Fight > Fight (same as 1)", "then: 🔒") is harder to parse than the map itself, so shrink it and let the map lead.

**28 Raid interlude.** "RUN ASSETS:" and "ARMORY:" are empty labels. START DEFENSE is outlined here but solid magenta in `22`: same action, two styles. The form uses native dropdowns ("armory: Turret", "Deploy armory asset"), which looks like debug UI.

**29–50 Combat:** see section 3.

**51 FLATLINED.** About 70% black void with no city. The stamp is small in a corner, and the dispatch text is cut off ("Recruit, regr"). This is the emotional low point of a run and it currently has no staging.

**52 Modem.** The best-dressed screen outside combat: vertical MODEM neon sign, colour-coded panels, BUY sticker prices, the LEAVE THE MODEM graffiti. Problems:
- Microchip text is about 7 px.
- Unaffordable prices are distinguished only by being paler pink.
- "Socket into Slot 1: CRIT 12" is a native dropdown.
- The Cycles readout is duplicated (top bar and the Remove panel).
- The BUY / SHRED stickers bottom left look like buttons, so it's unclear whether they are.

**53/54/55 Viewers.** The crossed-out card (`53`) and the drip marker circle around the target slot (`55`) are the best zine moments in the game. Put these on the store page. In `54` the detail popup repeats the card text word for word, and the card art area is **empty**. Every card is text-only, which is the biggest content gap for screenshots. In `55` the price is tiny under UPGRADE and should be on the button.

**56 Daemon tray.** The tooltip repeats its title twice ("TWIN POINTER" / "Daemon Twin Pointer").

**59/60 Events.** The terminal panel for the DISPATCH voice is a good differentiation. But the story panel is about two-thirds empty, the top subtitle band **repeats the same text at about 7 px**, and the speaker name appears three times ("DISPATCH - DISPATCH: Early Reply / DISPATCH: …"). In the choice cards the numbers appear twice, once in the text and again as chips, and good vs bad is shown by green vs red only.

**48/61 Loot.** The LOOT drip overlaps card 1's top edge. The modal is small with a lot of empty city around it, so it could be about 1.3× larger.

**62/63 Campaign end.** Won and Lost use **the same template and are indistinguishable at a glance**: 12 px text and full-width bars. This is the payoff screen of a 5–10 hour campaign. Give it a full-bleed stamp (CORP DOWN / CELL BURNED), the corp colour, and a Polaroid wall of the crew.

**64–68 Corp grids.** Tinting the whole district is a strong identity move. Meridian orange works. Halcyon purple is very close to the UI magenta and the afflict purple. **Orbital white** is the same colour as all UI text and icons, so the district looks unthemed. **Rebel Cell red** is the same red as damage and threat, and its red threat route disappears against red sites. See section 7.

**69–76 Class wheels (turn 1).** On screen, the eight classes come in **visually near-identical pairs**:
- Botnet (`72`) and Hivemind (`76`): the same wheel, including the purple drone slices, and the same opening hand.
- Rigger (`71`) and Overclocker (`75`): the same wheel with a hex slice, and the same hand.
- Ghost (`70`) and Phantom (`74`): the same green advance-slice layout.
- Breaker (`69`) and Wrecker (`73`): a very similar wheel and an identical hand.

Portraits reuse three tints: purple for Breaker, Rigger, Ghost and Hivemind, orange for Botnet and Phantom, and cyan for Wrecker and Overclocker. Every class also opens on "DEFEND · PERFECT AIM", so in a screenshot the class differs only in its hub name (about 10 px) and a chip or two. If these pairs are meant as base and advanced versions of one class, show that deliberately with a shared silhouette and a distinct accent. Either way, give each class:
- its own hub colour and pattern
- its own portrait colour, not three shared tints
- a class glyph on the hub

The most distinctive wheels today are Botnet and Hivemind, because their purple drone slices are the one place where class identity shows up in the wheel itself.

---

## 3. Combat

| Question | Answer now | Why |
|---|---|---|
| Whose wheel is whose? | **Mostly, by position and name only** | Both wheels use the same pink/cyan slice palette at similar sizes. The enemy has a green name, a green ring tint and yellow brackets, but the brackets mean "target", not "enemy". |
| What will each wheel do? | **Yes, and this is the best thing in the game** | The cream "IF YOU SEND IT" tags ("DEFEND · PERFECT AIM +10 BLOCK") are excellent. |
| What will a card do? | **Partly** | On hover (`31`) the tags preview the effect, which is great. But the hovered card doesn't lift or grow. With the mouse, **the preview disappears when you pick the card up** (strip 04, +367 ms) and only comes back after the drop, so it's missing exactly while you're aiming. With a controller the preview stays up during aiming (`1.6/12`), so this is a mouse-path bug. |
| What happened after SEND IT? | **Mostly** | The yellow hit line (`36`) and the ticks on forecast chips are clear. The numbers aren't: "-7" with a shield "4" (`38`) reads as 7 damage when the net is 3. The impact number collides with the HP text ("42⁶42", `37`). And "12 → 6 = -3" on the kill (`47`, strip 05) reads as bad arithmetic because the overkill cap isn't shown. |
| Who is winning? | **Weakly** | HP is a green number and a thin dashed arc. HP stays green even at 1/60 (`49`, `50`) and the enemy's 0/42 is still green (`47`). During the lethal turn (`49`) the top-bar HP sticky says 60/60 while the wheel says 1/60 (possibly because the state was set up for the camera, but check it). "NEXT 56" next to HP has no clear meaning. |

What I'd change:
1. **Ownership by frame, not position.** Give the operative's wheel a cyan outer bezel with the portrait inset in the hub, and the enemy a corp-colour bezel with a notched "hostile" edge. Keep the yellow brackets for targeting only.
2. **Split the forecast tags by side.** Each tag currently lists both sides' outcomes: "YOU TAKE 3 HP" sits on your own CRIT tag (`35`). Put *what this wheel does* on its own tag, and *what I receive* under my HP as a single net line ("−3 ♥ (7 − 4 block)").
3. **Keep the preview visible while dragging**, and draw the aim line from the card's centre, not its corner.
4. **Net damage numbers.** Show one number per hit in the colour of the result: amber if partly blocked with a small "7 − 4" subscript, red for full hits. Anchor numbers above the hub, never on the HP text.
5. **A real HP bar**: a thick ring segment, or a bar under each wheel, that goes amber below 50% and red below 25%, with a dimmed ghost segment for forecast damage. That answers "who is winning" at a glance.
6. **Boss framing.** The boss (`43`, `46`) looks exactly like a regular enemy. Use a larger wheel (+20%), a nameplate banner, and phase pips on the HP bar. At phase changes (`44`, `45`) the PHASE stamp stacks on top of "+10 HP" and "NO DAMAGE" in the hub, making three layers of unreadable text, and the second needle sits on top of the HP number. Clear the hub for the stamp, and move HP outside the needle sweep.
7. **At 1.6 the wheels shrink** to make room for text (`1.6_pad/10`). Invert that priority: the wheels are the game, so let side panels scroll or collapse first.

---

## 4. Motion

| GIF | Timing and easing | Clarity | Noise | Notes |
|---|---|---|---|---|
| 01 resolve | About 3.8 s per turn. Sequential (me, then enemy) reads well. | Good: hit line, ticks, number into HP | At +2.9 s, respin, redeal and forecast clear all fire at once | Needs a speed setting or tap-to-skip. The turn repeats hundreds of times. |
| 02 perfect | Snappy | The Perfect registers | **Full-screen magenta flash** that tints every pixel | Flash-limiter and photosensitivity risk. Localise it to the wheel. |
| 03 respin (strip) | Lands in about 250 ms and feels weightless for a 4-RAM action | Forecast updates immediately (good) | – | Add about 150 ms of overshoot and settle, plus tick marks passing the needle. |
| 04 card play | Good. Drop, stamp and spin in about 400 ms | Good aim state | The dragged card covers the target hub | The preview vanishes while dragging (see section 3). |
| 05 kill → loot | Good beats: bleach, shatter, VICTORY, DEFEATED stamp | Clear | VICTORY fades out *before* the cut | Hard cut to loot on the flat placeholder city. Hold the VICTORY frame and wipe to loot. |
| 06 boss P2 | Stamp lasts about 600 ms | **Weak**: the new needle just appears | Stacked hub labels | The wheel reconfigures during the respin, so the change is hidden. |
| 25 boss P3 | – | Drones are about 12 px hex outlines and easy to miss | **Full-screen green flash** | Same flash problem as 02. The enemy tag overflows. |
| 07 raid drag | Fine | The forecast verdict swaps without animating | **Map legend jumps to mid-map for a frame** | Layout bug; also visible in 20. |
| 08 refused | Card glides home in about 200 ms (good) | The no-entry ring is tiny, and the shake is invisible at this size | – | This toast is a terminal line, but combat (`41`) uses a yellow sticky. Unify them. |
| 09 crew → JACK IN | Fine | **Weak**: the result is only dropdown text. The "stamp ring" is barely visible. | – | Stamp the Polaroid onto the button. |
| 10 ring swap | Fine | **Weak**: only a 6 px label changes ("PIE" → "COR") | – | Recolour and fill the segment, and pulse it. |
| 11 modem warm-up | Charming tube flicker, about 1 s, doesn't block input | Good | – | Good example of ambient motion. |
| 12 buy by drag | Good. Cycles roll down in about 400 ms. | Good: the SOLD stamp stays in the slot | – | The CARDS sticky is a small, non-obvious drop target. |
| 13 buy refused | The card glides home in about 300 ms (good) | **Good**: the CARDS and Cycles stickers flash red, "NEED 53 · HAVE 5" appears, and unaffordable stock greys out | – | The best refusal in the game. Its bottom-bar toast is the terminal style, though, not the combat sticky. |
| 14 shred | Squash reads well | The grid **reflows the instant you pick up a card** | Modal closes abruptly | Keep a ghost placeholder until the drop. |
| 15 raid playout | Speed buttons are good | Mixed: numbers pile on labels | – | The stamp's text lags behind the game state. |
| 16 claim spread | About 500 ms spread, good pacing | Clear radius | Yellow over green gives a muddy khaki | Use a hatch in the player colour and don't dim the labels. |
| 17 Heat threshold | Roll plus hazard-tape banner | Clear | – | Banner text is about 7 px. |
| 18 jack in | About 900 ms, pixel-glitch button, good | – | – | "CONNECTING TO…" is the smallest type in the most dramatic beat. |
| 19 route move | About 400 ms trail, clean | Good | – | Good. |
| 20 site select | Subtle ring and camera lean | – | Legend pop, panel height jump | Keep the site card at a fixed height. |
| 21 menus | About 300 ms slides | Focus highlight is weak | Options slides in from the left, Codex from the right | Pick one direction. Contents reflow during the slide. |
| 22 page transitions | – | – | Backdrop swaps behind a modal that's still open | Close the modal first, then change page. |
| 23 loot pick | Cards fall away (fun) | **Weak**: the pick isn't celebrated, and the page cuts to the route *under* the falling cards | Placeholder city | Let the chosen card fly to CARDS on the loot page first. |
| 24 event | Typing at about 15 chars/s is slow | – | The chosen card leaves a white bar stuck over the route page | Artifact bug. Go to 40–60 chars/s and make typing skippable. |

**Best 3:** 04 card play (clear aim state and a snappy payoff), 11 Modem warm-up (atmosphere without blocking input), 05 kill → VICTORY (good beat structure).

**Weakest 3:** 02/25 full-screen flashes (they break the readability rule and are an accessibility risk), 10 ring swap and 09 crew assign (the result is invisible), 23 loot pick and 22/24 transitions (stacked cuts and leftover elements).

Consistency: there are two toast styles, two slide directions, three full-screen flash colours, and modal open/close is sometimes animated and sometimes a cut. Write one motion spec: page slide 250 ms ease-out-cubic from the right; modal scale 0.96 → 1 plus 180 ms fade; stamp 120 ms overshoot; numbers rise 400 ms.

---

## 5. Large text (1.6) and controller

What breaks:
- **Not everything scales.** Panel header labels (e.g. "REBEL_CELL // MAIN MENU", "SYSTEM ONLINE") and the Modem's microchip text stay at 1.0 (`1.6/01`, `1.6/14`). Any fixed-size label is a bug at this setting.
- **Combat wheels shrink** (`1.6/10`), and the forecast tags cover the [LB]/[RB] nudge prompts (`1.6/10`, `1.6/11`).
- **Clipping:** the Grid run list ("T1 Implant Re…"), the raid node list, dossier Loadout buttons (`1.6/04`), and the subtitle band, which starts mid-sentence (`1.6/08`, `1.6/15`).
- **Grid nav collapses to icons** (`1.6/07`). RAID SETUP becomes a bare shield. MAP KEY folding is a good pattern; use the same for the run list.
- The **Route key** doesn't scale even though the route list next to it does (`1.6/09`).
- Unaffordable **Black Market** items are grey on navy at about 2:1 contrast, which is unreadable at any size (`1.6/05`).
- The **loot tooltip** is a narrow column wrapping about one word per line, and it spills past the modal's left edge (`1.6/16`).

What holds up: slots (`1.6/02`), Options (`1.6/06`) and the event and loot cards reflow cleanly. The combat LAST TURN row scales and stays readable (`1.6/13`).

Controller prompts:
- The prompt bar uses plain yellow letters ("A Select X Pick up Menu Settings") rather than button glyphs. Use the standard coloured A/B/X/Y face glyphs, and icons for the Menu/View buttons ("Menu" and "[VIEW]" as words are ambiguous).
- The title-family pages (`1.6/01`, `02`, `06`) have no prompt bar at all. Options writes "Close [B]" inline instead.
- Tooltips still use mouse wording under a controller: "Or drag it onto the CARDS tag" (`1.6/16`) and "Or drag it onto a slot" (`1.6/14`).
- In combat, the [LB]/[RB] nudge prompts sit underneath the forecast tags (`1.6/10`, `1.6/12`).
- The aiming hint is good: "D-pad left / D-pad right: choose a glowing target · A: play · B: cancel" (`1.6/12`).
- Only the focused card shows its button glyph.
- In the Modem, the focus glyph sits inside the price sticker ("BUY 76 A") and reads as part of the price. The tooltip still says "Or drag it onto a slot".
- Focus highlights are thin yellow outlines. On a TV at 3 m they need a thick bracket plus a scale-up of about 4%.

---

## 6. Scrambled stills

**Still work without text:** Combat (slice icons, numbers, cost pips, Q/E arrows, aim pips), City Grid (legend icons, tier hexes, boss star, CORE house, plug-icon JACK IN), Route (node-type icons are excellent), Raid setup (map, cards, numbers), and HQ (menu icons, plus JACK IN recognised by its size and position).

Also work: the Loadout deck (`scr/06`), where cards stay identifiable by their bottom glyph (spin 3/6, nudge ×2, flip, overclock) and cost pip. The refused-respin state (`scr/18`) reads from the no-entry toast icon plus the RAM bar turning red. Event choices (`scr/20`) partly work through the ⊘ / +25 Cycles / +2 Heat chips.

**Depend on text:**
- **Black Market** (`scr/05`) is pure text with prices in brackets, and becomes a wall of noise. It's the worst screen here.
- **Campaign slots** and **New campaign** (`scr/02`, `scr/03`) can't be used without reading.
- **Options** (`scr/07`): toggles have no icons, which is acceptable for a settings list.
- The **raid result** (`scr/10`) is carried only by stamp colour (yellow = hold, pink = hit), which also fails colour-blind players.
- Combat chips (`scr/16`) keep their harm/block colour, but the numbers are part of the scrambled string rather than standing alone. Pull numbers out as separate glyph + number tokens.
- Forecast outcome *words* (DEFEND / PERFECT AIM): only the three-pip aim meter survives, so add a slice glyph to the tag.
- The raid verdict stamp (only a house icon survives).
- Dossier stats, which are sentences ("HP 60/60 DECK 10") rather than icon + number fields.
- Events and Codex, which are acceptable as text screens.

**Localisation risk:** the **REBEL_CELL logo itself is live text** and scrambles (`scr/01`, `02`, `07`), so it should be baked art. The LOOT: PICK A CARD graffiti grows past the modal's right edge when the string lengthens (`scr/21`). The MODEM / CYBER SHOP neon sign, SEND IT, LEAVE THE MODEM, NEVER SLEEP and the HEAT letter tiles are all live text in display fonts, so their width changes with the language (`scr/19`, `scr/13`). Either bake the signature ones as art with a translated subtitle, or design them with 40% width slack and a fallback font that has the glyphs.

---

## 7. Colour and typography

**Palette.** Magenta (primary UI and player slices), cyan (player and system), neon green (city, HP, "good"), yellow (focus, targets, next, claimed), cream (zine paper), red (damage). It's coherent, but **each colour carries too many meanings**:
- Green means the city, HP, Solace, heal slices, *and* Heat 62.
- Yellow means focus, targeting, claimed territory, loot and warnings.
- Magenta means primary buttons, player slices, Halcyon-adjacent purple and the Perfect flash.

Reserve green for HP and good outcomes, red for harm, and yellow for focus and targeting only. Then give corps colours that no UI role uses.

**Corporation colours.** Solace green clashes with the city and HP. **Orbital white** is the same as the text colour. **Rebel Cell red** is the same as damage. Halcyon purple is the same as afflict. Suggested: Solace teal-mint with a hatch, Meridian orange (keep), Halcyon violet (shift away from magenta toward blue-violet), Orbital ice-blue or silver with a hex pattern, Rebel Cell pale acid-yellow-green or a reserved glitch pattern. **Give every corp a pattern or glyph as well as a colour**, so the grid reads without colour.

**Colour-blind risks.** Green/red/orange corps plus green HP and red damage is the classic deuteranopia and protanopia problem. Affordable vs unaffordable (brightness only), good vs bad event chips (green vs red), and HP at 1/60 (colour unchanged) all rely on colour or brightness alone. Add icons (lock, ▲/▼, skull) and simulate each screen in a deutan filter.

**Type.** The drip display font is great used sparingly for verbs (SEND IT, LOOT). The condensed marker font for headings and the monospace for body are a sensible trio. The issues:
- There are too many sizes below 10 px (LAST TURN rows, legend, microchips, tier pips, subtitle band, banner rule text). **Set a hard floor of 12 px at 720p (about 16 px at 1080p) for anything the player needs to read.**
- Monospace at full width in the Codex and events is tiring. Cap line length at about 70 characters.
- Heading hierarchy inside terminal panels is flat (header labels are the same size as body text).

---

## 8. Top 15 recommendations (ranked by impact vs effort)

1. **Enforce a minimum text size and full text-scale coverage** — *quick fix, wide reach.* Audit every Label for fixed font sizes: panel headers, microchips, LAST TURN rows, legends, subtitle band. Floor at 12 px at 1.0, and make every label use the scaled theme font.
2. **Replace the full-screen Perfect and Phase flashes with local effects** — *quick fix.* Use a 250 ms radial glow and ring pulse on the wheel only, capped at 40% opacity, and have the flash limiter govern it.
3. **Net damage numbers anchored clear of HP** — *quick.* One number per hit, placed above the hub and never over the HP text, with a "7 − 4" subscript when blocked. Show overkill as "−3 (12 capped)".
4. **Proper HP bars with state colour and forecast ghosts** — *medium.* A thick ring or bar per wheel, green → amber (<50%) → red (<25%), with a hatched segment for forecast damage. Fix the 60/60 vs 1/60 mismatch between top bar and wheel.
5. **Keep the card preview live during drag, and lift the hovered card** — *quick.* Scale 1.15 and move up 24 px. The aim line starts from the card centre. The dragged card shrinks to 60% so it doesn't cover the target hub.
6. **One forecast tag per wheel, about that wheel only** — *medium.* Move "YOU TAKE X" to a single net line under the player's HP, and cap tags at one line of chips (overflow goes to "+2").
7. **Fix clipping and layout pops** — *quick.* Raid node lists, the Grid run list, the "Accelera/tor" break, the loadout first row, the legend jumping on panel rebuild (GIFs 07, 20), the leftover white bar after event choices (GIF 24), and the shred grid reflow (GIF 14).
8. **Controller glyphs and focus** — *medium.* Use real face-button glyphs, a prompt bar on every page including the title, a thick focus bracket plus 4% scale, and controller-specific tooltip wording.
9. **Wheel ownership and class framing** — *medium.* A player bezel with the portrait inset versus a hostile, corp-coloured, notched bezel, with target brackets used only for targeting. Give each of the eight classes its own hub colour or pattern, portrait tint and glyph, so the pairs in `69–76` stop looking identical.
10. **Boss presentation** — *medium.* A larger wheel, nameplate banner and phase pips. At a phase change, clear the hub and hold the stamp for 1 s, animate the needle drawing on, and move HP out of the needle's path.
11. **Re-assign corp colours plus patterns** — *medium.* Orbital and Rebel Cell especially. Add a pattern or glyph per corp for colour-blind players, and take Heat out of green.
12. **Stage the end screens** — *larger.* FLATLINED, Campaign Won and Campaign Lost get full-bleed stamps, the city behind, crew Polaroids, corp colour, and a different template for won vs lost.
13. **Replace native dropdowns and debug forms with zine/terminal widgets** — *medium.* New campaign, the raid interlude, "Socket into Slot", and the crew assignment dropdown.
14. **Unify the motion spec** — *medium.* One toast style (the yellow sticky), one page-slide direction, animated modal open/close, a "fast resolve" option, and skippable typing at 40–60 chars/s.
15. **Card art, or at least a card-type glyph field** — *larger.* Every card is text on a coloured blank (`54`), which is the biggest gap in screenshots. Even a shared set of 10–15 duotone spot illustrations per effect type (spin, nudge, flip, RAM) would change how the game reads.

Honourable mentions (quick): lock the loadout modal to one width across tabs, show locked corps in the target picker, bake the logo as art, replace the Delete icon on campaign slots, show a value on the text-scale slider, make the disabled Continue a grey outline instead of faded magenta, switch the raid stamp to LIVE/RESULT immediately, put three columns in the crew panel, and use two columns with headings in the Codex.

---

## 9. What would embarrass the game in a trailer or store screenshot

- The **full-screen magenta and green flashes** (GIFs 02 and 25) look like a rendering glitch in video and will trip photosensitivity warnings.
- The **empty black FLATLINED screen** (`51`) and the **text-only Campaign Won screen** (`62`). Players will clip these moments.
- The **flat block placeholder city** flashing in after loot and jack-in (GIFs 18 and 23). Pre-bake the next district during the transition.
- **"42⁶42"** collision and **"12 → 6 = −3"** arithmetic in a combat close-up.
- **Faded magenta Continue buttons** in the raid screens, which look broken.
- **Debug-looking forms**: slot list, new campaign row, raid interlude dropdowns, pause menu with a raw campaign code.
- **Text-only cards** in any hand close-up.
- **Class-select or roster shots side by side**: Botnet/Hivemind and Rigger/Overclocker look like the same character twice.
- The **Orbital and Rebel Cell grids** look unthemed next to Meridian.

What to lead with: the title city, the Meridian or Halcyon grid, a combat turn at the moment of a forecast, the marker-circled slice upgrade (`55`), the crossed-out card shred (`53`), the MODEM sign warming up, and SEND IT.
