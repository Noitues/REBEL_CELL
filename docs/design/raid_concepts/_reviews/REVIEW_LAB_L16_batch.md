# Review: Raid Lab L8 city raid (L16 batch: scrambled / planned / breach)

**Verdict: 38/50 (S 5, V 7, Fit 8).** This is a highly predictive and consequential raid loop, close to Into the Breach on foresight. Three things hold it back: the board does not carry the decisions without text, the response layer collapses to "nothing to do" in most raids, and the "LOCKED" banner overstates how locked a raid is. That banner, combined with a HOLD guard that only appears at HOME 1, let the breach line throw away two HOME pips it could have saved.

---

## 1. Scrambled read (images only, written before opening the README)

**What came across with no words:**

- **The arena.** An isometric neon city strip with an amber stacked HQ on the left (ours) and a glowing cobalt tower on the right (theirs). Three lanes run between them, labeled by noise that I could tell were row names, and there are four numbered cross-streets (B/C/G/D = 0–3).
- **The top bar.**
  - A heat bar with two tick marks (50, 75) and a number that climbs from 44 to 96 over the leg.
  - An "x/3" raid counter.
  - Three amber pips that are clearly HQ integrity. They stayed full all run.
  - Bank and score numbers.
- **The loop shape (000→010).**
  1. Glowing yellow rings with "+" and values: pick a district to claim.
  2. A card row fills at the bottom.
  3. Pieces get placed on the board.
  4. A panel of colored heart tables appears.
  5. Beams fire one after another (a pink lane beam, a dashed white route, then a blue beam down a cross-street).
  6. A big colored tier word appears.
  7. A three-column card choice with 1/2/3 flame icons.
  8. Repeat, with two "+" rings after the 3-flame pick (013/014).
- **Typed threats.** Triangle, square and circle glyphs survive scrambling. Each has its own color: cyan, magenta and orange. The bottom legend pairs them, so I could see that a cyan triangle piece sits against cyan triangle threats.
- **Outcome tiers by color.** The five-color legend at bottom right maps green, teal, orange, red and crimson tiers. The forecast in 003 is a wall of green hearts, and the aftermath in 010 shows a big green word. I read that as "this raid is safe and it was."
- **The arc.** The run went green, green, orange (039 shows three badges). Heat rose every raid, the pips never dropped, and the final total was 60.

**What did not come across:**

- **The card differences.** Shield, curved arrow and zigzag look different, but I had no idea how they differ.
- **The forecast axes.** I could not tell what the 2×2 tables in 003, 017 and 031 vary over, or what the small numbers beside the hearts mean.
- **Sealed and hunter mechanics.** "?" markers sit over threats, but nothing visual says "two of three lanes are real, one revealed now."
- **The response rows.** 006, 020 and 034 are 6–9 text rows. Their tier icons tell good from bad, but not what each row *does*.
- **The intensity cards.** The between cards (011) hold numbers in arrow rows that I could not decode. I could not tell why the 3-flame card was picked.
- **The score.** The 039 breakdown is just a column of signed numbers.

**Net:** the *loop* reads wordlessly, but the *decisions* do not. A scrambled player could follow a raid without being able to play one.

---

## 2. Scores

| Axis | Score | Reason |
|---|---|---|
| **W** what/why/when | 8 | Every phase names itself. AFTERMATH lists "what the beams touched" (planned/024), and RECORD gives a per-raid cause line (planned/039, breach/043). The intensity card numbers stay opaque even in English (planned/011). |
| **P** predictability | 8 | An exhaustive 12-outcome forecast with worst/best, plus a skull on HOME and launch friction (breach/002–004), predicted every result exactly. It loses points for micro-glyph density and a misleading "LOCKED" label. |
| **N** no-words | 6 | Shapes, colors and tier colors carry type and outcome. The forecast, response list and between screen are text tables (scrambled/003, 020, 011). |
| **D** decision depth | 7 | The leg has real choices: claim, 2 placements plus a ghost, response, then repair/add/clean and intensity, all feeding into heat. But the cards are identical as sentries, JAM never fired, and 6 of 9 raids had a trivial response. |
| **C** consequences | 9 | DOWN decays to TAKEN, which adds a wound, which becomes a dead draw (breach/014, 029, 031). HOME pips, heat and campaign loss all carry forward, with clear signaling throughout ("Next HOME hit ends the campaign", breach/027). |
| **Total** | **38/50** | |
| **S** suspense | 5 | Judged from the beat order, since stills cannot show motion. The 8-step reveal is well built, but 6 of 9 raids are "LOCKED: fast resolve," so the playout replays a known result. |
| **V** visuals | 7 | Handsome neon isometric board, with beams and typed glyphs reading clearly. The board is a thin diagonal strip with lots of dead space, and the on-board icons are tiny. |
| **Fit** | 8 | Sentries-as-cards, wounds clogging the deck, heat as corp attention, and two HQs on the city map all fit the deckbuilder fantasy. |

---

## 3. Placement

The order is: Into the Breach 45 > Slay the Spire 42 > Invisible, Inc. 39 > **Lab 38** > FTL 35 > Kingdom Rush 33 > TFT 31.

I do not have the anchors' per-axis scores, so the comparisons below are qualitative.

- **Against Invisible, Inc. (39, S 9), directly above:**
  - The lab matches or beats it on **P** (it enumerates the full outcome space before you commit) and on **C**.
  - It loses badly on **S**. Invisible's partial information pays off in the playout; the lab's mostly resolves at plan time.
  - It also loses on **N**. Invisible's board-first danger overlays read with no words.
- **Against FTL (35, S 8), directly below:**
  - The lab wins clearly on **P** and **W**.
  - It roughly ties on **C**, and loses on **S**.
- **Against Into the Breach and Slay the Spire, above:**
  - ITB beats it on **N** and **D**: board-projected intent, and units that each do something different.
  - Spire beats it on **D**: card variety with real trade-offs.
  - The lab's S of 5 matches ITB's deterministic flatness without ITB's turn-by-turn puzzle density.

---

## 4. What the three runs showed (README now in hand)

- **Scrambled (leg 8, auto greedy):** HOLDS, HOLDS, BATTERED, for a score of 60.
  - Raids 2 and 3 had a real spread at plan time: BATTERED/HOLDS (scrambled/016), then DAMAGED/BATTERED (scrambled/030).
  - The response mattered in both. A SHIFT move of an enforcer gave HOLDS (scrambled/020). A DEPLOY netrunner limited raid 3 to BATTERED (scrambled/034).
  - This is the best case for the system.
- **Planned (leg 5, auto greedy):** HOLDS, HOLDS, BATTERED, for a score of 47.
  - Raid 1 was "LOCKED: HOLDS on all 12" (planned/003). Every response row read HOLDS or worse (planned/006).
  - Raid 3 was "LOCKED: BATTERED on all 12" (planned/030). Every response row read BATTERED (planned/034).
  - Only raid 2 had a live decision: DAMAGED/HOLDS → DEPLOY DRONE > NOR 1 → HOLDS (planned/017, 020).
  - Two HOT picks pushed heat to 94 and cost 37 points (planned/039). That is more than double the bank.
- **Breach (leg 3, auto naive):** DAMAGED, DAMAGED, BREACHED.
  - Every plan was flagged red ("Every outcome costs HOME", breach/003; "breaks HOME", breach/033), and launch friction fired each time (breach/004, 019, 034).
  - In all three raids, SACRIFICE would have held the result to BATTERED: breach/007, breach/022, and breach/037. The bot held each time.
  - Between raids, one free repair could not keep up with 3 DOWN districts. Decay turned MID 0 and SOU 0, then SOU 2, into wounds (breach/014, 029), and a dead card showed up in hand (breach/031).
  - The consequence chain is exemplary and fully legible.

---

## 5. Findings

### P1

1. **"LOCKED" is locked under HOLD, not locked.**
   - breach/035–036 show "LOCKED: fast resolve" with the HOLD tier BREACHED, yet breach/037 offers SACRIFICE MID 1/SOU 1 → BATTERED.
   - The same holds in breach/006–007 (locked DAMAGED, sacrifice BATTERED) and breach/020–022.
   - The banner plus the forced 2× speed tell the player the outcome is fixed exactly when a better row exists.
   - The "HOLD is worse than SACRIFICE: launch anyway?" guard only appears at HOME 1 (breach/038). In raids 1 and 2, HOLD silently cost a HOME pip each time (breach/011, 026).
   - That is how the breach happened. It is a P/W failure in the one place where it matters most.
2. **Most raids resolve at plan time, so the reveal beats carry no information.**
   - 6 of 9 raids across the batch were locked under HOLD: scrambled r1, planned r1 and r3, and breach r1–r3.
   - In the planned locked raids, every response produced the same tier (planned/006, 034).
   - The launch sequence of Reveal A, sealed A, Reveal B and hunter (planned/004–009, 032–037) is then a replay.
   - The sealed and hunter structure is the suspense engine, and it is idling. This is the main reason S sits at 5.

### P2

3. **The decision screens do not survive scrambling.**
   - The forecast cells (scrambled/003, 017, 031), the response rows (scrambled/006, 020, 034) and the intensity cards (scrambled/011, 025) all depend on text.
   - The board shows *where* threats run but not *what a response would change*.
   - Hovering a forecast cell or response row does not project that outcome onto the board in any frame.
4. **The forecast is too dense.**
   - Each of the 12 cells packs a tier heart plus kept/lost/hit/block micro-numbers (planned/017, breach/018).
   - The hunter axis is labeled only by small text ("hunter A: st 3 / B: st 0").
   - The tier glyph, the one thing that matters, is the size of a digit.
5. **The intensity choice is the leg's biggest lever, and the least explained.**
   - Heat cost 37 of 47 points in the planned line and 38 points in the scrambled line (planned/039, scrambled/039).
   - The intensity cards show "-14.5 ▼-5"-style figures and H55/H60 marks (planned/011, 025) with no clear statement of *net leg value per option*. The only such figure is the single "Leg value after" line for the highlighted card.
   - The greedy bot took HOT twice, and the "careful" line ended up 13 points below the scrambled run.
6. **Card types are shallow.**
   - GUARD, SHIFT and JAM are identical as sentries. They differ only at response, and only if left unplaced.
   - JAM never fired in 9 raids; the row reads "JAM: no JAM card in hand" in every response frame I saw.
   - SHIFT was used once (scrambled/020).
   - The hunter was never decisive in a visible way.
   - The result is D at 7, not 8+.
7. **"beats HOLD" sometimes has no visible reason.**
   - planned/034 shows DEPLOY DRONE > SOU 1 at BATTERED marked "beats HOLD", next to HOLD at BATTERED.
   - The tiebreak (districts? exploits?) is not shown.
8. **The response list is long.**
   - planned/020 shows "MORE rows 1-8 of 14," and planned/034 shows "DEPLOY ×14 variants."
   - Sorting puts the best row first, which helps, but scanning 14 rows to confirm that is busywork.

### P3

9. **The board is a thin tilted strip.** Roughly 40% of the viewport is empty starfield above and below it (all frames). The board icons (broken hearts, "?", skulls, column digits) are tiny as a result.
10. **The lane labels are in the wrong place.** NORTH/MID/SOUTH sit next to the corp tower, far from the home side where sentries are placed (planned/002, breach/017).
11. **The bottom ticker overflows.** It truncates or wraps mid-word (scrambled/006, planned/005). The leg-value formula line under the header is unreadably small.
12. **The README and the captures disagree.**
    - The README says response results show on hover only. The captures show tiers on every row, which may be a capture mode.
    - SCAN (+3 Heat, gold edge) appears in no frame, so I could not judge it.

---

## 6. Three changes that would raise the score most

1. **Make the response guard honest everywhere.** *(P +1, W +1, and it would have prevented the breach.)*
   - Replace "LOCKED" with "HOLD → DAMAGED · best: SACRIFICE SOU 1 → BATTERED."
   - Fire the "worse than best row" confirm whenever HOLD loses a HOME pip that some row saves, not only at HOME 1.
   - Keep fast resolve only when *every* row produces the same tier.
2. **Keep more raids open past the plan.** *(S +2, D +1. This is a rules change.)*
   - Tune the sealed and hunter variance, or the sentry cap, so that HOLD-locked plans are the exception. Target: no more than a third of raids.
   - Give JAM and SHIFT a reason to stay in hand. For example, let JAM also cancel sealed B, or let SHIFT act after Reveal B.
   - The goal is for the hunter reveal to be a decision point, not a replay.
3. **Put the forecast on the board.** *(N +2, V +1.)*
   - Hovering a forecast cell or response row should draw that outcome's beams on the city, along with falling districts and HOME pip loss, with large tier glyphs.
   - The intensity cards should show net leg value as one large signed number, plus icons for captures and income.
   - With that in place, the scrambled run would be playable, not just followable.

Together these lift the total to about **42–43/50** with S at about 7. That would place the lab between Slay the Spire and Into the Breach.

---

## 7. Ceiling note

**P and C are already near their ceiling.** The forecast is exhaustive, and the decay → wound → dead-draw chain is as clear as anything in the anchors.

**W and N are a presentation ceiling.** Change 3, plus the guard rewording in change 1, closes most of that gap without touching rules.

**D and S are a rules ceiling.** No presentation fix creates suspense in a raid whose every response yields the same tier, or depth from three card types that play identically on the board. Without rules work there, polish tops out around 41–42.
