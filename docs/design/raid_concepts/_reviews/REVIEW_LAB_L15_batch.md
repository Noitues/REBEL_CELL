# Review: Raid lab L8 (city raid), batch L15

**Verdict:** The rules engine and forecast are close to Into the Breach. The persistence chain (HOME pips, DOWN→TAKEN decay, wounds as dead draws) is the best part of the mode. Two things hold it back. Most raids are already LOCKED at plan time, so the staged reveal plays out a foregone result. And the response layer only works in words.

## Scores

| Axis | Score | Reason |
|---|---|---|
| **W** what/why/when | 8 | Each phase has a header and a one-line instruction. Beams are tagged NOW/LATER/DONE, and the "known beams touched" log and aftermath cause lines (`planned/038_r3_aftermath`: "2+ districts went DOWN, or one was TAKEN") give the why. The tier ladder itself is never shown as a whole. |
| **P** predictability | 9 | Every plan lists its 12 outcomes, worst/best, before launch, plus a per-route 2×2 table (`planned/003_r1_forecast`). The launch confirm also fires when every outcome costs HOME (`breach/004_r1_launch_friction`). Almost nothing is hidden that matters. |
| **N** no words | 6 | Board grammar survives scrambling: colored typed threats, beams with arrows to the amber HQ, a dashed hunter path, and a big aftermath stamp. Forecast axes, response rows and tier distinctions (heart / broken heart / X / skull) do not. |
| **D** decision depth | 7 | The leg-level levers are real: capture choice and exploits, two sentries plus the ghost, response, repair vs card vs clean, and intensity versus Heat bands. Within a raid, though, the response is usually moot because the outcome is locked. |
| **C** consequences | 9 | Damage carries across raids. HOME pips drop, unrepaired districts decay and add wounds, and a wound shows up as a dead draw (`breach/031_r3_draw`). A red banner warns "Next HOME hit ends the campaign" (`breach/027`), and a breach wipes the score. |
| **Total** | **39/50** | |
| **S** suspense | 5 | The beat order is good: known beams → reveal A → response → reveal B → hunter → stamp. But in 5 of the 6 worded raids the panel already says LOCKED, so the reveals change nothing. Judged from the still beat sequence only; motion, timing and audio are not visible. |
| **V** visuals | 6 | The neon isometric board is coherent and the threat colors are clear. The board takes under half the screen and is tilted thin, and at Heat 90+ the pieces pile up (`planned/032`). The panel text is tiny. |
| **Fit** | 8 | Sentries as cards, wounds clogging the deck and Heat-driven hand size are native deckbuilder-roguelite ideas. The territory between two HQs suits REBEL_CELL. |

## Placement

At **39 it ties Invisible, Inc. (39)**. It sits below Slay the Spire (42) and above FTL (35).

- **Into the Breach (45):** this is its closest relative, a deterministic forecast and S 5 for the same reason. It loses on N (ItB's tile previews are wordless; these response rows are not), on D and on V. P is about level.
- **Slay the Spire (42):** it plausibly wins on P (all 12 outcomes vs intent icons) and C (campaign-level HOME and decay). It loses on N, because StS intents read without text. It also loses on D, because StS's deck grows and changes far more than this run deck's +1 guard or clean.
- **Invisible, Inc. (39):** it wins on P and roughly matches on C. It loses badly on S (5 vs 9): Invisible's playout is tense because outcomes are not locked. It also loses on V (6 vs 7).
- **FTL (35):** it wins on P and W. It loses on S (5 vs 8).
- **Kingdom Rush (33) and TFT (31):** it beats both on P, D and C. It loses on S and V.

## Scrambled run: what came through with no words

### Read from images alone, before the README

- The amber stepped block on the left is ours, and the cobalt tower on the right is theirs. Three rows of districts run between them.
- The phases have distinct panels and a fixed order.
- **Capture** (`scrambled/000`, `013`): yellow plus-rings with numbers 6/10/12 read as "claimable districts and their value". The key icon on one row read as "special".
- **Draw** (`scrambled/001`, `015`): cards appear in the bottom row. Shield vs curved-arrow glyphs mean two card kinds.
- **Plan** (`scrambled/002`):
  - colored pawns stand on our districts, matching the cyan triangle / magenta square / orange circle legend;
  - glowing lines with arrowheads run toward our HQ, so they are attacks;
  - "?" over some enemy pieces means unknown.
- **Forecast** (`scrambled/003`): a grid of hearts and broken hearts with small digits, read as a table of possible outcomes.
- **Response** (`scrambled/006`): yellow-green halos on districts, and a magenta ring with a long line reaching out from it. I guessed "move or retarget a piece".
- **Hunter** (`scrambled/008`, `009`): a dashed blue column sweep, a second, separate threat.
- **Aftermath:** a big green heart means good (`scrambled/010`, `024`). An orange broken heart means worse but survived (`scrambled/038`).
- **Between** (`scrambled/011`, `025`): three cards with 1/2/3 flames, a risk-level pick. The big top-left number (44→58→71→89→96) on a bar marked at 50 and 75 is a rising pressure meter that grants cards.
- **HUD:** three yellow pips are clearly HQ health.
- **Record** (`scrambled/039`): three rows (two green, one orange), a breakdown column and a final 60.

### Not conveyed without words

- That a sentry blocks only its own type. Color matching hints at it, but I could not confirm it.
- That two of the three routes are real, sealed beams revealed in sequence.
- What the hunter's street choice depends on.
- What the ghost is. Its circle on HOME just looked decorative.
- The forecast table's axes (B route × hunter street).
- What any response row does or costs. The rows are word walls with tiny glyphs (`scrambled/020`).
- That Heat is a score penalty, not only a card source.
- The full tier ladder (HOLDS/EVADED/BATTERED/DAMAGED/BREACHED).
- Wounds, decay and TAKEN. None occurred in this line.
- The column numbers. They are text, so they scrambled to B/C/G/D.

### This line versus the worded runs

The scrambled line was also the most suspenseful of the three. Its plans showed real ranges in every raid:
- raid 1: worst DAMAGED, best HOLDS;
- raid 2: BATTERED / HOLDS;
- raid 3: DAMAGED / BATTERED.

The playout did matter here, as the 60 shows.

## Findings

### P1

1. **LOCKED raids turn the playout and the response into ceremony.**
   - **Planned line:**
     - `planned/002_r1_plan` and the launch panels: "LOCKED: HOLDS on all 12 outcomes".
     - `planned/006_r1_response`: every non-sacrifice row reads HOLDS.
     - `planned/030_r3_plan`: "LOCKED: BATTERED on all 12 outcomes".
     - `planned/034_r3_response`: every row reads BATTERED, including the +2 Heat DEPLOY the bot paid for.
   - **Breach line:** `breach/002`, `017` and `032` are all locked, ending in "LOCKED: BREACHED" (`breach/036`).
   - **Effect:** in 5 of 6 worded raids, the beats from reveal A through the hunter sweep (`planned/005`–`009`, `033`–`037`; `breach/006`–`010`, `036`–`040`) show results the HUD already printed. A pinned "LOCKED" tag during launch even announces it.
   - Determinism is fine; Into the Breach is deterministic too. Spending eight beats on a known result is not.
   - **Hurts:** S and D.

2. **The response decision exists only in text.**
   - On the board, `scrambled/006`, `020` and `034` show halos and a target ring. Nothing links a row to its effect: no shield on HOME for SACRIFICE, no ghost path for REDEPLOY.
   - The rows themselves are 8–14 lines of tiny text (`planned/020`: "MORE rows 1-8 of 14").
   - The only cue that survives scrambling is the gold edge for "beats HOLD".
   - **Hurts:** N most of all.

### P2

3. **HOLD into a breach is not challenged at the response step.**
   - `breach/007` and `breach/022` show SACRIFICE → BATTERED (HOME shielded) against HOLD → DAMAGED.
   - In `breach/037`, at HOME 1/3, SACRIFICE MID 1 / SOU 1 → BATTERED sits above HOLD → BREACHED.
   - Launch friction exists (`breach/004`, `019`, `034`: "LAUNCH ANYWAY"). The response step has none, though the campaign-losing click happens there.
   - A human might not miss this. It is still the one place where a cheap confirm would save a run.

4. **The Heat cost is opaque at the moment you pay it.**
   - The between cards all carry the same green "HOLDABLE" tag (`planned/011`, `025`; `breach/012`, `027`), so the tag never tells the options apart.
   - The real price surfaces only in `planned/039`:

     | Score line | Points |
     |---|---|
     | Heat above 44 | −25 |
     | Heat bands | −12 |
     | Exploits kept | +12 |

   - Greedy took HOT twice and reached Heat 94. The "Leg value after" line on the between panel is tiny and below the cards.
   - **Hurts:** D readability.

5. **The board crowds out at high Heat.**
   - At Heat 90+, three beams plus five sentries plus threat icons overlap in columns 0–1 (`planned/030`, `032`; `breach/035`).
   - The board is about 40% of the frame, and the right half of the city is mostly empty.
   - **Hurts:** V and N.

### P3

6. **README and captures disagree on SCAN and hover.**
   - The README says row results show only on hover, and that SCAN (+3 Heat) marks the best row.
   - The captures show results on every row, with free gold "beats HOLD" edges (`planned/020` header).
   - Heat goes 67→69 (card +2 only), so no SCAN was bought.

7. **Stale footer warnings.**
   - "Every outcome costs HOME with this plan: change it?" persists through the aftermath, between and decay screens (`breach/012`, `014`, `027`, `042`).

8. **Tier glyphs are a weak ladder.**
   - HOLDS (heart) and BATTERED (broken heart) differ mostly by color. EVADED never appears.
   - The bottom legend (`planned/000`) lists units and states but no tiers.
   - Column indices are text-only, so they scrambled to B/C/G/D (`scrambled/002`).

## The three changes that would raise the score most

1. **Make locks pay off rather than drag.** *(S +2, D +1)*
   - When the plan is LOCKED, collapse launch into one fast resolve with the stamp.
   - When it is not, keep the full reveal ladder.
   - As a rules option, keep the hunter street live more often (e.g. a hunter that can't be fully pre-covered by 2 sentries plus the ghost), so the response matters in more raids.
2. **Glyph-first responses and a tier ladder.** *(N +2, W +1)*
   - Hovering a row previews its effect on the board: a shield dome on HOME for SACRIFICE, a ghost arrow for REDEPLOY, a struck-out hound for JAM.
   - Give the five tiers distinct shapes, not heart variants.
   - Pin the ladder in the legend.
   - Add a confirm when HOLD is worse than a visible row and HOME ≤ 1.
3. **Price Heat where it is chosen, and give the board more room.** *(D +1, V +1)*
   - Replace "HOLDABLE" on the intensity cards with the projected end-of-leg Heat penalty and leg-value delta.
   - Widen or zoom the board when the panel is in a playout phase.
   - Fan out stacked sentries at Heat ≥ 75.

Together these come to about 42–44/50, S 7, V 7.

## Ceiling: rules or presentation?

**Mostly presentation on N, V and W; mostly rules on S and D.**

- **P and C:** near ceiling now. The forecast and the persistence chain need no rework.
- **N and V:** limited by the response panel and the board's screen share. That is fixable without touching the oracle.
- **S and D:** limited by the rules.
  - The outcome space is small: 3 A routes × 2 B routes × 2 hunter streets.
  - With deterministic resolution, a careful plan collapses it to one tier most of the time.
  - That is the Into the Breach trade, which caps S near 5 unless something stays genuinely open after commit.

If the team accepts that trade, the honest move is to shorten the locked playout rather than dress it up. The more ambitious move is a rules change that keeps one live variable through the response.
