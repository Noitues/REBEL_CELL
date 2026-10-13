# V1: what the live combat preview shows today (A2 gap list)

Build: main fc21b1a4, seed 7 (Breaker vs Collections Agent), text scale 1.0 and 2.0, mouse, reduce effects off.
Method: `tools/visual_qa/review_pack.gd` gained eleven `v1_*` screens (tools only). Each one reads the preview as drawn
(chips, tag title, forecast HP, pointer, RAM bar), takes the picture, then really plays the previewed card or nudge
and SEND IT through the engine, and dumps the real state. Raw dumps: `<out>/<combo>/<case>.v1.json`.
Capture: `python tools/visual_qa/capture_pack.py --screens v1_hover,v1_aim,... --scales 1.0,2.0 --save-size 1280x720`.
Sheets: `docs/art_review/PLAN1/V1_PREVIEW.jpg` (1.0) and `V1_PREVIEW_2.0.jpg` (2.0). Order, left to right, top to bottom:
hover, aim, chain2, chain3, nudge, nudge_hover, kill, kill_you, enemy, enemy_fx, null. Layout at 2.0 holds (no overlap seen).

Headline: the numbers are right. Every forecast HP matched the resolver after SEND IT in all 11 cases (including both
kills). What is missing is presentation: no before-to-after reading, no RAM after the turn, no queue view, no "-> 0".

| Case | Shown | Missing or wrong | Screenshot |
|---|---|---|---|
| One card aimed (Jolt, 3 targets; hover is the same) | Chips beside Breaker HP `-11`, `(3` absorbed, `+3` block; Breaker tag "DEFRAG . half power"; Agent tag moves to "OVERFLOW . perfect aim" (pointer 16 -> 14 after the +4 spin); RAM 6 with pending -1 blinking; yellow aim line. Real: Breaker 60 -> 49, Agent 40, matches. | HP is a chip only: no "60 -> 49" and the arc/number never says it. Enemy-side effect of the card (spin +4) shows only as a changed tag and a ghost needle, no chip. The tag title names the landing slice but the chips never say which hit caused the -11. | sheet 1.0 cell 2 |
| Two actions chained (Jolt played, second Jolt hovered) | After the played Jolt the chips fall back to `+3`; the Agent tag reads "NULL . good aim" (pointer OVERFLOW/PERFECT now, tag says NULL for the preview after the second spin). RAM 5, pending -1. | No list of what is already queued/played this turn, no running total across the chain ("-11 saved, now +4 more"). The -11 from the first Jolt is not visible any more, so the chain's net effect is not readable. The tag title (NULL) is for the hovered second play; the pointer shown at that moment (OVERFLOW) is the current one: the two disagree. | cell 3 |
| Three actions chained (2 Jolts, Fine Tune hovered) | Chips `+3` only; Agent tag "NULL . good aim", ghost on the enemy wheel; note log says "outer ring nudged +1" twice. RAM 4 pending -1. | Same as above; additionally the note log (hidden) is the only place the nudges appear. No per-step cost list; RAM bar shows only the next pending cost, not the chain total. | cell 4 |
| Nudge queued (made, then forecast) | Breaker chips `+5` block, `☠?` (random status odds); tag "DEFRAG . good aim"; header FREE NUDGE 0; real: block 5, CORRUPTED lands on a slice. | The nudge itself is not in the preview (no step marker, no "free" tag on the RAM bar); `☠?` shows no odds, so the real CORRUPTED is a surprise. | cell 5 |
| Nudge arrow hovered | Same chips as the queued nudge (`+5`, `☠?`), "1 LANDS HERE" marker on the Breaker wheel, ghost needle, RAM pending 0. | No before/after of the landing slice (WEAK -> GOOD) except the tag; the pointer's tier change is not on the pointer. | cell 6 |
| Kill, enemy at 1 HP (Breaker pointer on perfect OVERFLOW 12 x2, SEND IT) | Agent chip `-1`, tag "INFECT . good aim", forecast HP 0 and alive_after false; HP number stays "1/40". Real: Agent dead, HP 0. | CP-002 ruling 5 not built: no "-> 0" wording, only `-1` (the damage is clamped to the HP, so the chip reads like a 1-point hit). The skull is drawn only on the lethal chip, and the HP number stays 1/40 with no "-> 0". The Agent's own tag still advertises its INFECT as if it will act. | cell 7 |
| Kill, the player (5 HP, Jolt hovered) | Breaker chip `-5` (clamped), forecast HP 0, alive false, skull glyph on the chip, HP "5/60". Real: Breaker dead, HP 0. | Same: no "-> 0"; `-5` hides that 11 would land. The preview does not warn that the card hovered makes a lethal turn before SEND IT. | cell 8 |
| Enemy-side effect (nothing hovered; Agent INFECT) | Breaker chips `+3`, `☠?`; Agent tag "INFECT . good aim"; no chip on the Agent. Real: Breaker 60, block gone, CORRUPTED on slice 3. | `☠?` gives no odds or who-hits-whom text on the chip (odds are in the hidden breakdown). Satellite (Collections Drone) block +3 and its pointer have no row of their own. | cell 9 |
| Enemy-side effect of a card (Jolt spinning the Agent's wheel; no status card in the hand, so a spin stands in) | Agent pointer slice changes in the tag (INFECT -> OVERFLOW), ghost needle. | Enemy chips stay empty: nothing says "your Jolt changes what the Agent does". The 'was' row under the tag is small. No status-on-enemy case was reachable with this hand. | cell 10 |
| The Null (Breaker pointer on NULL, WEAK) | Breaker chip `☠?` only (the status odds), tag "NULL . half power"; note log "Breaker lands on NULL". Real: no damage, CORRUPTED lands. | Nothing on the chips says "NULL: nothing happens / Cold Exit and Fault Tolerance relevant". An empty result reads like a missing preview. Dock/Firmware that trigger on NULL are not shown. | cell 11 |
| RAM, every case | Bar shows current RAM with a blinking pending cost (-1) for a hovered card, 0 for end-of-turn and nudges. | The RAM after SEND IT is never forecast: real RAM after the turn was 9 (hover/aim), 8, 7, 10 (refill each turn), against the bar's "5 left". The chain total is not shown, only the next card's cost. | all |

What A2 still has to build (from the rows):
1. A before -> after HP reading on every row (and "-> 0" for a kill, CP-002 ruling 5); today a chip only, and clamped damage reads as a small hit.
2. A queue/chain readout: what is already played this turn, a running net effect, and a chain RAM total.
3. Enemy-side effect chips (spin, status, block on the enemy) and a row for satellites.
4. An explicit NULL result chip and odds text on the `☠?` chip.
5. RAM after SEND IT (and the refill) next to the pending cost.
6. Pointer: show the tier/slice change on the pointer itself for nudges and spins; the tag title and the pointer disagree while a second play is hovered.

Caveats: a status-card hand and a multi-enemy fight were not reachable with seed 7 turn 1; the Drone satellite has no chips of its own (existing behaviour).
Files changed: `tools/visual_qa/review_pack.gd` only (new `v1_*` screens and a `_v1_*` helper block). No file under scripts/, scenes/ or content/ was touched.
