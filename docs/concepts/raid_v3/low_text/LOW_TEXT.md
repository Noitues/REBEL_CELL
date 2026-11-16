# Raid in Deface v3: low-text directions, 2026-11-15

The designer asked: "iterate on UI elements so we have little to no text blocks. Corporate documents are a good example, but
also make sense to have text. I still want to find a happy medium." This folder holds three directions, each shown on the set 6
`r3_plan` state and the `r3_place` held-sticker moment. All of them reuse the same map, routes, beacons, units and pencil. Concept
plates only; nothing in the `r3_*` set changed.

- `lt_A_plan.png`, `lt_A_place.png`: **A, Pictogram**
- `lt_B_plan.png`, `lt_B_place.png`: **B, Diegetic**
- `lt_C_plan.png`, `lt_C_place.png`: **C, Happy medium**
- `lt_sheet.jpg`: 3 rows x 2
- Source: `../src/low_text.py` (imports `raid_v3_city`, `raid_kit`). Run `python low_text.py`.

## Word counts (from the plates)
Every string the script draws is registered, so these numbers come from the plates themselves.
- **Words** are tokens with 2+ letters. Callsigns, item names and SEND IT count as words.
- **Labels** are 1-letter tokens and codes: route letters A/B, keys Z/Q, cell names, L3.
- The corp document is counted separately.
- The set 6 baseline is listed by hand from `r3_plan` / `r3_place`, including the grid's a-g / 1-7 labels.

| Plate | Words on screen | Labels | Numbers | Corp document words |
|---|---|---|---|---|
| set 6 `r3_plan` (baseline) | 57 | 22 | 35 | (memo, ~40, 9-11 px cap) |
| set 6 `r3_place` (baseline) | 62 | 22 | 36 | (same) |
| **A** plan / place | **7 / 7** | 8 / 7 | 37 / 38 | 0 |
| **B** plan / place | **25 / 26** | 6 / 6 | 16 / 18 | 23 / 23 |
| **C** plan / place | **6 / 6** | 6 / 5 | 22 / 23 | 1 folded / 24 unfolded |

- A's 7 words: KAI, VEX, MOTH, RUNE, SOLACE (the stamped header), SEND, IT.
- C's 6 words: the same minus SOLACE.
- B's words are the stickers' own printing (roles, weapon and device names, SAFE HOUSE, BARRICADE, BLACK MARKET) plus the
  pencil ("2 leak", "safe").

**Text size.** Every line drawn on a panel or document is at least 16 px cap height: Anton 19 px and up, Share Tech Mono 23 px
and up on screen. I measured the cap ratios at Anton 0.86 and Mono 0.70. This fixes the work order's 9 px unit rows. B is the
exception: its worded stickers keep text below the aim, about 10-15 px cap (roles, L chips, shop names, cost dots, the
SAFE HOUSE sub-label, the map barricade). A and C have no sticker words below the aim.

## What each direction does
**A, Pictogram.**
- **Left column:** the core tape is a heart, eight cells and "8 → 6". Rounds are four diamonds with the current one lit;
  credits are the cyan coin and 7. The CREW stickers keep only their callsigns, with level shown as pips. The weapons are
  pictograms with stars: SMG burst, rail beam, shotgun spread, jammer waves. UNDO is an undo arrow and the Z key.
- **INCOMING** is a wave strip under a stamped Solace header (wordmark plus an eye in a red stamp ring for "intercepted"),
  with Heat as a flame and 25. Each round is a row: the round number, then each group as its v4 icon and ×count. The current
  row is lit with the schedule edge and later rows dim. The A/B route chips are shown where v39 gives a path.
- **Shop:** stickers with price dots only. The barricade is its hazard stripes, the mine a fused star, the sentry an eye on a
  barrel. Reroll is an icon, a price dot and Q.
- **Forecast strip:** A with a shield, B with a drop and 2, a heart with 8 → 6, a skull with 6/8. The place plate's strip
  starts with a "drop into this cell" icon instead of "IF PLACED e7".
- **On the map:** the Safehouse is a house with the core's heart. The leak pencil is a drop and 2, and "safe" becomes a tick.
  Grid labels are off.

**B, Diegetic.**
- **No HUD panels.** Round, credits and Heat are the Cell's pencil on the glass corner: four boxes with the current one
  circled, a pencil coin and 7, a red pencil flame and 25.
- **Forecast:** pencil only, on the map ("6 → 3" at the wall, "2 leak", "8 → 6", and ✗ 6/8 under the core note).
- **INCOMING** is the intercepted work order as a real document. It is enlarged, every line is 16 px cap or more, and the unit
  rows are printed v4 icons with counts.
- **Shop:** the sticker sheet, with only a printed BLACK MARKET header. Stickers keep their printed words. SEND IT has no key
  hint.

**C, Happy medium.**
- **Live and numeric:** A's left column, shop, reroll and forecast strip.
- **The one document:** the work order, folded at rest to a paper corner under the glass. Visible are the Solace seal,
  "ROUND 1 · 8", a dog-ear, the edge of the red stamp and a cyan unfold chevron, with Heat beside it.
- **Place plate:** shows the order unfolded, with fold creases, over the shop as the brief asked.

## Pros and cons
**A, Pictogram**
- Pro: the fewest words while keeping all the information. Every live number is next to its icon. The wave strip carries
  all four rounds, so the shop can be planned against what is coming.
- Pro: the screen reads in one consistent icon language: heart = core everywhere, drop = leak, skull = kills.
- Con: the screen loses its corp voice. The work order was the best piece of fiction on screen; a wordmark strip is a weak
  stand-in.
- Con: there are a lot of icons to learn on day one, and some are guesses: the diamonds as rounds, the drop as leak, the
  "drop into cell" icon as IF PLACED. They need onboarding or hover tooltips.

**B, Diegetic**
- Pro: the most characterful. The corp document is a real document and everything else is the player's pencil and stickers.
  Nothing looks like a game HUD.
- Con: the most words of the three (about half of set 6). Small sticker text stays below the aim.
- Con: rounds, credits and Heat as pencil are slow to read and look like scribble at a glance. With no forecast line, the
  forecast is scattered across the map.
- Con: there is nowhere for UNDO or reroll key hints.

**C, Happy medium**
- Pro: almost as few words as A (6). It keeps the one document that earns its text. Folding gives the designer's balance:
  paper when you want the fiction, pictograms for everything you check every second.
- Pro: "ROUND 1 · 8" on the corner plus the ×5 / ×3 stacks at the entries cover the current wave without opening anything.
- Con: later waves are hidden until the order is unfolded, which matters when buying in the shop.
- Con: the unfold-on-hover does not work while dragging a sticker. The place plate shows it per the brief; in play it would
  be hover or a key at rest.

## Recommendation
**C**, with one change I'd test next: print the next round as a strip of icons (no words) on the folded corner, under
"ROUND 1 · 8". That gives the shop its look-ahead without unfolding, and keeps the document as the only text block.

A is the fallback if the corp voice can live elsewhere (aftermath report, site raids). B is the strongest mood piece but
does not meet the low-text goal or the size aim.

## Weak points
- **Weapon and device pictograms are mine**, not from the bible. At CREW size the weapon tag is about 34 px tall, so the
  pictograms are small.
- **Grid labels are off in all three**, which removes the cell names. The pencil "on c2" becomes a tick, and the beacon
  colour shows where. Anything in v39 that refers to cells by name in UI text would need a different cue.
- **"A holds" has no cell.** The shield is beside the route chip and the barricade on the map shows where.
- **B does not stack later waves at the entries.** v39 gives paths only for round 1, so only round 1 can stand at its
  entries; I didn't invent paths for the other rounds. The later waves are on the work order.
- **SEND IT stays a worded verb sticker (2 words) in all three.** It is the bible's verb.
- **Not tested:** the wave strip's unit icons (12 px radius) are only checked by eye, and no readability test was run with
  players.
