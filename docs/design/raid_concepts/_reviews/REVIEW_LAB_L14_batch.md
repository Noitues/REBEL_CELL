# Review: Raid Lab L14 batch (city raid, L8 board)

**Verdict:** This is a telegraphed-threat defense with excellent forecasting and damage that persists and visibly snowballs. Three things hold it back: the decision layer is gated behind hover and text, forecasts usually collapse to one tier before the playout starts, and losing districts shrinks the response menu to HOLD-or-SACRIFICE. **34/50 (S 6, V 6, Fit 7).** That places it between FTL and Kingdom Rush.

## Scores

| Axis | Score | One-line reason |
|---|---|---|
| **W** what/why/when | 7 | The phase headers, NOW/LATER/DONE beam list, "WHAT THE BEAMS TOUCHED" and per-raid record explain cause and order well. Forecast cells and panel lines truncate ("HOM…", "wou…"). |
| **P** predictability | 8 | A 12-outcome worst/best forecast, an on-board preview of one assumed configuration, and per-response worst/best of 4 all come before commitment. Response results need a hover, and the best-move mark costs +3 Heat (SCAN). |
| **N** no words | 5 | The tier glyphs (heart / broken heart / X / skull), threat color+shape and beam lines carry the raid. Capture meaning, card verbs, response rows and the between-raid trade are text-only. |
| **D** decision depth | 6 | Real leg-scale trades: intensity, ghost Heat, exploit captures, card vs clean, sacrifice. Within a raid, the response is usually irrelevant (uniform forecast) or reduced to HOLD vs SACRIFICE. |
| **C** consequences | 8 | DOWN→TAKEN decay, wounds that become dead cards in hand, HOME pips, Heat carried across the leg, and campaign loss on breach. All are visible and compounding. |
| **Total** | **34/50** | |
| **S** suspense | 6 | The staged reveals (A → response → B → hunter) are well built. Only about 1 in 3 raids still has a spread when the playout starts. Judged from the beat sequence only; stills show no motion. |
| **V** visuals | 6 | A coherent neon slab with strong type coloring. The board is small in frame, the panel text is tiny, and raid 3 is cluttered with overlapping arrows, wrenches and numbers. |
| **Fit** | 7 | Corp Heat, a run deck with wounds, and a netrun stand-in suit a cyberpunk roguelite deckbuilder. Deckbuilding is still thin: add a guard or clean a wound. |

## Placement

Ladder: Into the Breach 45 · Slay the Spire 42 · Invisible, Inc. 39 · FTL 35 · **L14 lab 34** · Kingdom Rush 33 · TFT 31.

The axis comparisons below are my estimates of the anchors, not the earlier critic's breakdown.

- **Versus FTL (35, one above):**
  - The lab wins **P**. FTL hides intent, while the lab enumerates all 12 outcomes.
  - It roughly ties on **C**.
  - It loses **S** (6 vs 8) and **V** (6 vs 7).
  - It loses **D**. FTL's route and resource map gives more distinct leg-scale strategies than HOT/NORMAL/LOW plus 2 placements.
- **Versus Kingdom Rush (33, one below):**
  - The lab wins **P**, **C** and **D**. Persistent wounds and decay beat per-level resets.
  - It loses clearly on **N**. KR is readable with the sound off, and this is not.
  - It also loses **S** (6 vs 8) and **V** (6 vs 8).
- **Versus Into the Breach (its structural cousin, 11 above):**
  - The lab is close on **P** and **C**.
  - Most of the gap is **N** and **W**: ITB puts every consequence on the board as an icon.
  - Some of the gap is **D**: ITB's responses always reshape the outcome.

## What the scrambled run did and did not convey (written before reading the README)

The scrambling is a consistent substitution: GIFUX always stands for the same word, and numbers survive. Repeated tokens therefore became learnable symbols. That makes this a softer test than true wordlessness.

**Conveyed by images alone:**

- **The board.** It is a long slab between an amber HQ (left) and a cobalt tower (right). Three horizontal routes are labeled at the tower end, and columns of districts are lettered along the top.
- **Ownership.** Owned districts are amber, the corp's are cobalt.
- **Capture** (scrambled/000, 013, 027). Clickable yellow rings with + glyphs and numbers (6/10/12) read as "pick one, bigger is better." 028 shows a second pick after the three-flame card, so I connected "three flames → two picks."
- **Threats and sentries.**
  - Threats are colored figures with "?" above them (unrevealed).
  - Sentries are pillars matching card colors, and the card glyphs pair shape with color: cyan triangle, magenta square, orange circle.
  - A dog glyph marks some kind of chaser.
- **Beams** (004–009, 018–023, 032–037). Colored lines run along routes or streets and end at HQ or stop at a pillar. The panel list steps one row "active" at a time, which reads as an ordered sequence.
- **Outcome tiers.** The full cyan heart, broken yellow heart and red X were immediately clear as good/meh/bad. The big glyph on aftermath (010, 024, 038) and the record rows (039: heart, heart, broken heart) told me how the leg went.
- **Pressure.** The top-left bar fills from 44 to 96, with tick marks at 50 and 75 tagged +1/+2. Three amber pips at the top never changed, so I guessed "home health, untouched."
- **Between** (011, 025). Three cards with 1/2/3 flames and a wrench on the middle one read as a risk ladder with numeric trades.
- **Score.** The final score (039) is a signed ledger. I could tell two big negatives dragged 98 down to 60.

**Not conveyed:**

- What the capture numbers are (value? cost?), or that some carry a key/exploit.
- That two routes are sealed and revealed in a fixed order, or what the 2×2 tables in the forecast (003, 017, 031) index.
- What the response rows do. Response (006, 020, 034) was a wall of noise. I could only see that one row was highlighted and that a pink/green circle appeared on the board.
- What the cards do. Shield, arrow and zigzag were visible but meaningless.
- That the Heat bar's ticks change the hand size, or why the right-hand number ("leg value") jumped around.
- What the hunter is, and why its street was dashed.
- That the run made three different response choices, which only decoding the panel later revealed.

**Net result.** Without words I could follow *the plot* (claim, defend, see damage, escalate) and *the outcome*. I could not follow *the decisions*.

## Findings

### P1

1. **The escape hatch is the quietest row on the screen.**
   - In breach/006, 020 and 035, HOLD shows its tier inline (DAMAGED/DAMAGED, then BREACHED/BREACHED), while every SACRIFICE row says "hover for the result."
   - SACRIFICE shields HOME, and taking it in raid 3 would have saved the campaign.
   - The naive line held three times and lost.
   - The rule is right. The presentation steers the player toward the visible tier and away from the hidden better one. SCAN (+3 Heat) charges for what should be default information.
2. **Forecasts usually collapse to one tier, so the response and playout are often formalities.**
   - Uniform 12/12 outcomes appear in planned/003 (all HOLDS), planned/031 (all BATTERED), breach/003 and 017 (all DAMAGED) and breach/031 (all BREACHED).
   - Planned raid 3 still paid +2 Heat for DEPLOY DRONE > SOU 1 (planned/034), which showed BATTERED/BATTERED. Heat went from 92 to 94 for no change in tier (planned/038).
   - Only planned raid 2 (planned/017 → 020 → 024: DAMAGED/HOLDS → BATTERED/HOLDS → HOLDS) shows the intended "response changes the odds, then reveals resolve it" arc.
   - This caps both S and D.

### P2

3. **The launch confirm appears less often than the README says.** The README asks for a confirm when HOME drops on every outcome.
   - breach/003 (r1) and breach/017 (r2) are 12/12 DAMAGED, yet they go straight to known_beams with no "LAUNCH ANYWAY" frame.
   - Only r3, at HOME 1 (breach/031–032), adds friction.
   - Either the rule or the capture is wrong. As shown, the two avoidable HOME hits that set up the breach passed with a single Enter.
4. **The death spiral strips the response menu to almost nothing.**
   - After decay (breach/013, 027), no free district remains to DEPLOY onto. Response then offers only HOLD and SACRIFICE (breach/020, 035), even with GUARD and SHIFT cards in hand (bottom row).
   - That is a legitimate consequence, but it is a binary choice.
   - Ghosted DEPLOY rows with a "no free district" reason would also explain *why* the options vanished.
5. **The response list is long, and its results are hidden.** Planned/034 shows "rows 1–6 of 23"; scrambled shows 18 and 28. Combined with finding 1, the only practical way to find the best row is SCAN.
6. **Text truncation in the decision tables.** Forecast cells read "HOM… ✕ DAMAGED" (planned/017, breach/031), and panel lines end in "wou…" or "a…" (all plan frames). Truncation sits exactly where P lives.
7. **Raid-3 board clutter.** In planned/032–037 and scrambled/036–037, beams, block markers, numbered hits, wrenches, hearts and dashed hunter streets overlap at the corp end. The beam that matters *now* does not stand out from the ones already DONE.
8. **N gap on cards and the between screen.**
   - Card verbs are a tiny glyph beside a type icon (all bottom rows).
   - The intensity cards (planned/011, scrambled/011) express their trade as text arithmetic ("Heat +18 → 67, bank +3 → 10").
   - The flame count is the only wordless carrier.

### P3

9. **The Heat bar's "+1 / +2" ticks are ambiguous.** The README ties two things to 50 and 75: extra hand cards and extra beams ("off (Heat 50)" in plan). The bar labels only one of them, and does not say which.
10. **Leg value only shows for the selected intensity.** "Leg value after" appears for the highlighted card (planned/011: 30.5; planned/012 with HOT: 20.5). Showing all three side by side would make the HOT gamble legible.
11. **Heat dominates the score, and the leg-scale cost of HOT is opaque.**
    - Heat is −37 of the planned line's 47 (planned/039) and −38 of scrambled's 60 (scrambled/039).
    - Both "careful" lines ran HOT twice with the ghost. The cost is visible in the ledger only after the leg.
12. **Positive, keep:**
    - The dead WOUND card in hand (breach/029–030).
    - Red HOME pips and the "Next HOME hit ends the campaign" banner (breach/025).
    - The BATTERED definition printed on aftermath (planned/038).
    - The per-raid record naming the response taken (planned/039, breach/040).

## The three changes that would raise the score most

1. **Inline tier glyphs on every response row, grouped by outcome, best-vs-HOLD marked for free.** Show worst/best icons without hover, merge rows with identical results, and gold-edge any row that beats HOLD. Keep SCAN only for tie-breaks, if at all. **P +1, N +1, D +1 (≈ +3).**
2. **Keep variance alive past PLAN, and say so when it is gone.**
   - Tune so that B and the hunter street still split the outcome in most raids. One lever is that a placement can cover at most one of the two B routes.
   - When the forecast is uniform, label the raid "LOCKED: BATTERED" and let the response list grey out paid rows that change nothing. This also prevents the planned/034 wasted +2 Heat.
   - **S +2 (S axis), D +1 (≈ +1 on /50, +2 on S).**
3. **A wordless decision layer.**
   - Put verb icons at card size (shield / arrow / zigzag as the dominant glyph).
   - Show iconified intensity trades: flame = Heat, coin = bank, + = capture, wrench = repair, with three-way score deltas.
   - Show a per-route outcome glyph at HOME during forecast.
   - Dim DONE beams in playout.
   - **N +2, W +1, V +1 (≈ +3, plus V).**

Together these land around 38–40, in Invisible, Inc. territory.

## Rules ceiling or presentation ceiling?

It is mostly a **presentation ceiling** for now.

- The rules already produce strong P and C. The breach run shows a legible, fair cascade: DOWN → TAKEN → wounds → dead card → HOLD-or-SACRIFICE → breach.
- The missing N, W and V points (≈ 5) are fixable with icons, layout and inline results.

Past about 39 it becomes a **rules ceiling**:

- Plan placement settles most raids.
- Response menus thin to a binary under pressure.
- The run deck grows only by guards and cleans.
- Heat's leg-scale penalty dominates the score.

Reaching Slay the Spire or Into the Breach depth needs responses that reshape outcomes in most raids, and cards with more than "block my type" as their identity.
