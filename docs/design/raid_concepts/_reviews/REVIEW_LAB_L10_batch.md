# Review: Raid lab (city raid), batch of three runs (scrambled, planned, breach)

**Verdict:** The lab is a strong forecast machine with a weak playout. You can see almost everything before you commit, and damage carries cleanly from raid to raid. That same transparency means most raids are solved at FORECAST, so the reveal and response beats only matter when the player leaves a red route uncovered. **37/50. S 4, V 6, Fit 7.** It sits between FTL and Invisible, Inc.

---

## 1. What I read from the scrambled sheets alone (written before the README)

**What came through without words**

- **The board and its two sides.** The amber building stack on the left, with three amber squares in the HUD, is "my HQ / my integrity." The cobalt tower on the right is the enemy. Three named rows run between them.
- **Claiming a district** (scrambled/000, 010, 020). Dashed yellow circles with a `+` and a number (6/10/12) read as "claim one of these, worth N." The panel lists the same numbers.
- **Typed threats and sentries.** Cyan triangle, magenta square and orange circle are used consistently in the legend, on the sentry pillars, on the dashed routes and on the panel cards. I understood that a color stops its own color before I read a word.
- **Forecast verdicts** (scrambled/002, 012, 022). There are three cards, one per route, each marked green-heart, red-X or yellow-heart. The skull on my HQ in plan/forecast (011, 012) meant "this plan gets me hurt."
- **The gamble.** In scrambled/002 two routes are green and one is red. In 003 one beam fires and one row shows `?`. In 004 the red route's color lights up. In 005 every response row is red-X. In 006–007 a red `-1` and a red ring land on my HQ, and one integrity square turns red. I read "I left a hole, the dice found it, and nothing could fix it" with zero words. This was the best moment in the batch.
- **Persistence.** The HUD integrity squares stay red into raid 2. The record (028) shows red-X / green / green with a final number.

**What did not come through**

- **The hunter.** In 006/016/026 I saw a vertical light column down a street and some extra glow. I could not tell it was a hunter, where it would go, or why.
- **Heat.** The orange bar with 44 and the marks `50 +1 / 75 +2` survived scrambling because they are digits. I guessed "thresholds add something," but not that heat subtracts from score.
- **The between-raids screen** (008/009, 018/019). There are three identical cards with numbers, plus build icons. I could tell one card was picked, but not what was being traded.
- **The response rows** (015, 025). I saw that ringed sentries could do something and that one row was green. I could not read the row as "move sentry X to Y" or "jam."
- **Why the score beat the careful run.** Scrambled ended at 48 with a home hit. I could not explain that from images.

**Caveat on the N test.** Digits, `?`, `1x/2x/4x`, hotkey letters and icons all survive scrambling. The scrambled sheets therefore flatter the no-words reading somewhat.

---

## 2. Scores

| Axis | Score | Reason |
|---|---|---|
| **W** what/why/when | **8** | Phase titles, the LAUNCH timeline with BEAM/SEALED/HUNTER rows marked NOW/DONE/LATER, and the one-line sentry rule make "when" explicit. The hunter rule, ghost cost and heat→score link live only in fine print. |
| **P** predictability | **9** | Every sealed candidate is forecast with exact hit/block/HOME results. Every response row is priced. Between-raid cards preview next heat and beam count. One point off because the HUD leg value ignores the ghost's heat until aftermath (planned/001 vs 007). |
| **N** no words | **6** | Type colors, skull, red `-1` ring, verdict colors and cobalt takeover holograms all carry. Hunter, ghost, intensity cards and response rows need text. Surviving digits inflate this. |
| **D** decision depth | **6** | The capture→place→ghost→response→repair/build/intensity chain is real, and breach proves a wrong chain kills. But FORECAST solves each raid, the response has a dominant row, and intensity is a thin 1–3-point trade. |
| **C** consequences | **8** | Home integrity, DOWN→TAKEN decay (including loss of the sentry standing there), heat ratchet, bank and exploits all carry raid to raid, and the record itemizes them. Nothing is shown carrying across legs. |
| **Total** | **37/50** | |
| **S** suspense | **4** | Judged from the beat sequence; stills cannot show motion. Real beats happen only when a red candidate is left (scrambled r1/r2). Planned r1/r2 are foregone, and breach r3 is foregone and announced as such. |
| **V** visuals | **6** | The neon isometric board is coherent and the palette is disciplined. The board fills under half the frame, routes tangle near HOME (planned/021–022), and the hunter has no silhouette. |
| **Fit** | **7** | Corp raids on your turf, netrunner/drone/enforcer types and heat fit REBEL_CELL. CAPTURE is an explicit stand-in for netruns, and no cards touch the raid, so the deckbuilder link is still a promise. |

---

## 3. Placement

**37 places the lab between Invisible, Inc. (39) and FTL (35).** The anchors' per-axis scores are not given to me, so the comparisons below are my reading of where each game is strong.

- **Against Invisible, Inc. (39; S 9, V 7):** the closest analog. Heat behaves like the alarm ratchet. The lab **wins P**, because Invisible hides guard paths and the lab forecasts every candidate. It **loses S badly** (4 vs 9) and loses some **D**, because Invisible's partial information keeps every turn a judgment call.
- **Against FTL (35; S 8, V 7):** the lab **wins P and W**. FTL's event outcomes and fights are far less forecastable. It **loses S** (4 vs 8) and likely **D**, since FTL's ship build and routing across a sector is wider than one build and one intensity per break.
- **Against Into the Breach (45; S 5):** this is the real design target. ITB proves a full-forecast game can score 45 with low suspense. The gap to ITB is **not S**. It is **D**: ITB's forecasts open many good answers, while this lab's forecast usually points at one. The gap is also **N**: ITB's board pictograms carry intent, while here the panel does.

---

## 4. Findings

### P1 (would block a ship)

- **The forecast solves the raid, so the reveal and response are empty most of the time.**
  - Planned r1 and r2 forecast all three candidates HOLDS (planned/002, planned/012). The reveals (004, 014) and the sealed and hunter beats (006, 016) are therefore foregone, and every response row in planned/005 reads HOLDS.
  - The only live beats in 85+ frames come when the player cannot or does not cover a candidate:
    - scrambled/002 → 004 → 005 → 007, where the gamble is lost;
    - scrambled/012 → 014 → 017, where it is won.
  - The sealed 1-of-3 is the lab's suspense engine, and the rules let the player switch it off.

- **Breach raid 3 is ten frames with no agency, and the spiral that causes it is double-counted.**
  - breach/020: decay takes MID 0 and SOU 0, and the sentries standing on them are lost too.
  - breach/022: the plan therefore opens with 0/0/0 sentries and a BREACHED verdict.
  - breach/023 says "no response changes this," and breach/026 says "Nothing you can do changes this."
  - The decisive moment was breach/018–019. The banner reads "Next HOME hit ends the campaign" and the hint reads "PROTECTS HOME: build ENFORCER." Bank was 15, yet the naive line built NONE.
  - That screen never says "this is your last decision," and it does not show what the raid-3 forecast would be with or without the build.
  - Telegraphing the loss is fair. Playing out a decided raid is not suspense; it is waiting.

### P2 (costs points now)

- **The response has a dominant row, and the menu reads as "find the green one."**
  - planned/025 and scrambled/025: every r3 forecast is BATTERED, and JAM is the only row that HOLDS. Redeploy rows are worse (DAMAGED).
  - planned/015: MOVE rows are worse than plain HOLD.
  - Outcome-labeled rows are excellent for P, but with one green row and no price difference, the decision is gone.

- **Intensity is a thin, near-flat trade.**
  - planned/008: LOW +3 bank / +6 heat; NORMAL +7 / +12; HOT +10 / +18.
  - planned/018: LOW +5 / +6; NORMAL +10 / +12; HOT +15 / +18.
  - Heat above 44 costs 1 leg value per point, so every card loses 1–3 points on the step it is picked. HOT only pays if the bank buys a sentry or repair you would otherwise miss.
  - The real lever, "next Heat 73–78, 2–3 known beams," sits in small red text at the bottom of each card.

- **The HUD leg value lags the ghost's heat cost.**
  - planned/001: heat is 49 ("ghost +5"), but the formula reads "– Heat 0" and LEG VALUE is 38.
  - planned/007: the same value drops to 33.
  - The price of the ghost is invisible at the moment you commit it.

- **The hunter does not read as a hunter.**
  - In planned/006/016/026, scrambled/006/016 and breach/006/027 it shows as a light column down a street.
  - Its street ("the street of the first touch") is never drawn on the board at PLAN. Players learn of it in text.
  - The README promises a hound; the stills show a beam.

- **Home damage looks cheap until the last point.**
  - scrambled/028 prices one HOME hit at –8, and that leg-8 line finished at 48 with a hit. The careful leg-5 line finished at 43 with none (planned/028).
  - The legs differ, so this is not proof. Still, it signals that one hit costs about one district, while the third hit costs everything.
  - That cliff is what makes breach feel sudden even though it was announced.

### P3 (polish)

- **Board size.** The board fills well under half the frame. The top-left starfield and the huge row labels (NORTH/MID/SOUTH) take space the routes need. This shows on every frame and is worst in planned/021–022, where the dashed routes cross near HOME.
- **Forecast row text.** Rows like "hit NOR 1, MID 1, SOU 1; blocked at MID 1, NOR 1, NOR 0" (planned/022) are unreadable at speed. The board preview conveys the same thing better.
- **Unexplained negative leg value.** It goes to –2 in breach/018 with no explanation, and the record then says "a breach leaves no score" (breach/029). The meaning of the negative number is never stated.
- **Things that work well:**
  - the capture value numbers floating over districts (planned/000);
  - the cobalt holograms on TAKEN districts (breach/020);
  - the HOME-integrity squares turning red in the HUD (breach/017).

---

## 5. The three changes that would raise the score most

1. **Make full coverage of the three sealed candidates impossible or expensive by rule** (for example, the sentry budget covers at most two routes, or the ghost/spoof are the only way to cover a third).
   - The reveal then always resolves a live 1-of-3 gamble, which is the scrambled-r1/r2 beat on every raid.
   - **S +3, D +1.** P is unchanged, because the risk is still forecast exactly.
2. **Put "last chance" on the between-raids screen and stop playing decided raids.**
   - Preview the next raid's worst-case HOME result for each build and repair option.
   - Return a lost district's sentry to the pool, so one decay does not cost both district and defense.
   - If no option avoids a breach, cut to the record.
   - **D +1, W +1, S +1**, and breach r3 stops being dead air.
3. **Do a no-words pass on the board.**
   - Give the hunter a creature silhouette and draw its street at PLAN.
   - Show intensity as 1/2/3 flame pictograms on the board edge, with the beam count as icons.
   - Draw response rows as from→to arrows on the sentries.
   - Show ghost heat in the leg value at commit time.
   - **N +2, P +0.5, V +1.**

These would bring the total to about 41–42/50, with S around 7–8.

---

## 6. Rules ceiling or presentation ceiling?

**Mostly a rules ceiling.**

- **Presentation work can still buy real points.** Changes like #3 above would raise N, V and a little W, worth about +2–3 on the /50.
- **The rest of the gap to Into the Breach is D.** The forecast is so complete and the option sets so narrow that there is usually one right answer:
  - one green response row;
  - a near-flat intensity trade;
  - a sealed candidate you can simply cover.
- **The suspense deficit is also rules-made.** Information is complete and coverable. The scrambled run shows the engine works as soon as the rules force a gamble.
- **On the presentation side**, the visual language (type colors, skull, red ring, cobalt takeover) is already good enough to carry a deeper ruleset. It is not what is holding the lab back.
