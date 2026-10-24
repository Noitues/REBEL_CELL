# Review: Raid lab L8 (city raid), L17 capture batch

**Verdict:** Among the most forecastable raid modes I have scored, and its consequences carry across the whole leg. The board shows the threats well. But the two decisions that matter most, the response pick and the intensity pick, still live in text tables. The response phase often has nothing to decide. **36/50 (S 6, V 6, Fit 7). It sits between FTL and Invisible, Inc.**

---

## 1. Scrambled run first: what the images alone told me

I read `scrambled/000`–`039` before opening the README. The words were noise. Numerals, colors, shapes and glyphs survived.

### What I understood without words

- **The board.** It is an isometric strip with an amber HQ on the left and a cobalt tower on the right. Three horizontal lanes (the noise labels at the tower end) are crossed by numbered vertical streets. I read it as "they attack along lanes, we hold the left end".
- **Ownership.**
  - Amber or lit tiles are ours.
  - Glowing yellow rings with a `+` and a number (6, 10, 12) are things to claim (`000`, `013`, `027`, `028`).
  - In `028`, two rings get claimed one after the other. So some turns let you take two.
- **Threat types.** Shape and color carry them well: a cyan triangle, a magenta square and an orange circle. Units of the same shape stand on our tiles, so I guessed "sentries match threat types". I could not confirm it without words.
- **Heat.** The top-left bar has ticks at 50 and 75 and a number that climbs 44 → 46 → 64 → 69 → 89 → 94 → 96. The bar turns red past the second tick. The bottom card row grows from 4 to 5 to 6 cards in step. I inferred that Heat gives cards. I did not infer that Heat also adds beams.
- **HOME.** There are three amber pips at the top, and they never dropped in this run. I read them as HOME health.
- **Sequence.** `004` → `009` show one beam firing, then a row highlighting, then a white dashed arrow down a lane (`007`), then a blue beam down a street (`008`). I could tell there is a staged reveal with a moment to act in between (`006`).
- **Outcome icons.**
  - A green heart means good (`010`). Amber and broken hearts mean worse. The legend strip at the bottom right ranks five glyphs from green to red.
  - Broken-heart icons sit at the tower end of each lane (`004`, `018`, `032`). I read them as "this lane hurts if it fires". That was correct, and it was the best wordless device in the set.
- **The leg.**
  - `011`/`025` show three big cards with signed numbers (−4/−2/−10, then −1/+5/−7). One card gets highlighted. Flame pips on the cards rise left to right.
  - `039` is a three-row recap (green, green, amber) with a total of **60**.
  - Leg number 8 comes from the surviving numeral in the record title.

### What I did not understand without words

- **The forecast tables** (`003`, `017`, `031`): what the three colored blocks of heart grids index. I could see a 2-column grid per block. I could not tell that it was "second route × hunter street".
- **"Sealed" versus known.** The `?` markers over streets and the paw glyph read as "unknown", but not as "two of three routes are real".
- **What the response was.**
  - In `006`, `020` and `034`, a magenta or yellow ring appears on a district and a unit shows up or moves.
  - I could not tell that this was a card-paid DEPLOY or SHIFT, what it cost, or what it beat.
- **Why the intensity card was picked.** In `011`/`012`, the highlighted card jumps from −2 to −10. The bot took the *more negative* number, and nothing visual explained why.
- **Decay and TAKEN.** They never occur in this run, so I learned nothing about them.
- **The score.** The 60 breaks down into lines I could not attribute, apart from "big plus, two minuses".

**Net:** with no words I could follow the board, the threat types, Heat, HOME, the reveal order and the outcome color. I could not follow any decision. N is scored on that basis.

---

## 2. Scores

| Axis | Score | Reason |
|---|---|---|
| **W**: what/why/when | 8 | Every phase states its rule in one line ("Districts left DOWN fall to the corp"). Every aftermath says what touched what (`planned/024`: "BEAM 1: SOU 1 block … SEALED B: SOU 1 block"). The record recaps each raid's between-choice. Vocabulary drifts ("street 3 down" vs "route to HOME"), and EVADED is never shown. |
| **P**: predictability | 8 | There are 12-outcome tables, a worst/best per response row, route-end tier markers and a two-step launch confirm when HOME is doomed. Two things hurt it. The intensity card's headline number leaves out its own perk. "Best" means two different things. |
| **N**: no-words readability | 5 | Board state reads well (shapes, ownership, route-end hearts). The forecast grid, the response list and the intensity tradeoff do not; they are tables of words. |
| **D**: decision depth across the leg | 6 | There are real levers: the capture pick (value, exploit), 2 sentries from the hand, the ghost (+5 Heat, placed at 44 → 49 to stay under 50), repair versus card versus clean, and LOW/NORMAL/HOT against Heat bands. But the response is often moot ("no response changes this") or pre-solved ("best:" printed on the plan screen). |
| **C**: lasting consequences | 9 | Effects persist across the leg: DOWN → TAKEN at DECAY → a wound card → a dead draw (`breach/033`). HOME pips persist into a campaign loss. Heat ratchets up and changes hand size and beam count. The score shows each cost. |
| **Total** | **36/50** | |
| **S**: suspense in the playout | 6 | Judged from the beat order only; stills cannot show motion. The structure is good: known beams, reveal A, response, reveal B, hunter, with a NOW/LATER/DONE ladder. But two of three raids per run are foregone at launch (`planned/002` "HOLDS – no response changes this"; `breach/035` "Every outcome breaks HOME"). |
| **V**: visuals | 6 | The neon isometric look is coherent, and the route-end markers are a strong idea. Late raids clutter badly (`planned/036`, `breach/037`), with skulls, wrenches, ⓘ, ×, ?, paws and hearts all at once. Cobalt does triple duty. The panel text is tiny. |
| **Fit** | 7 | A raid between two HQs on the city map, with sentries as deck cards and wounds as curse cards, fits a cyberpunk roguelite deckbuilder. Two things fit less well: the forecast is a spreadsheet, and the "hunter" is just another beam. |

---

## 3. Placement

| Game | /50 | S | V |
|---|---|---|---|
| Into the Breach | 45 | 5 | 8 |
| Slay the Spire | 42 | 6 | 7 |
| Invisible, Inc. | 39 | 9 | 7 |
| **Lab L8 (this batch)** | **36** | **6** | **6** |
| FTL | 35 | 8 | 7 |
| Kingdom Rush | 33 | 8 | 8 |
| Teamfight Tactics | 31 | 8 | 7 |

- **Against FTL (35, just below).**
  - The lab wins P and W clearly: FTL never shows you 12 outcomes before you jump.
  - It is about even on C: wounds and TAKEN districts work like hull damage and lost crew.
  - It loses S badly (6 vs 8) and loses V.
  - The lab is the more honest system and the less exciting one.
- **Against Invisible, Inc. (39, just above).** This is the closest relative: Heat is the alarm level, and the sealed routes are the unseen guards.
  - The lab matches or beats it on P.
  - It loses on S (6 vs 9), because Invisible's dread comes from *partial* information. The lab often resolves it in the forecast.
  - It loses on N: Invisible draws vision cones and alarm ticks on the board.
  - It loses on D: Invisible's every action point is a choice, while the lab's response is often a single obvious row.
- **Against Slay the Spire (42).** StS wins D through card synergy. The lab's four cards (GUARD/SHIFT/JAM/WOUND) differ only by type and verb. StS also wins N, because intent icons alone are enough to play.
- **Against Into the Breach (45, the target).** ITB puts its whole forecast *on the board* as telegraphs. The lab puts the same depth of forecast in a side panel. Most of the gap is that difference (N), plus a response phase with fewer live options (D).
- **Against Kingdom Rush (33).** The lab wins P, D and C. It loses V and S.

---

## 4. What the scrambled run did and did not convey

| Conveyed | Not conveyed |
|---|---|
| Who owns what (amber vs cobalt), what is claimable (yellow rings and values) | That a claim stands in for a netrun, and the adjacency rule |
| Three threat types by shape and color, plus matching sentries | That a sentry blocks *only* its own type (guessed, not shown) |
| Heat rising with thresholds at 50/75; the hand growing at them | That Heat also adds beams (`planned/032`: 3 known beams at 92), and the score penalty |
| HOME as three pips | That HOME loss ends the *campaign* (seen only in the breach run's red banner, and that is words) |
| Reveal order: beam → row → dashed lane → street beam | Which reveals are sealed, and that the response window sits between A and B |
| Outcome severity by heart and skull color; route-end lane markers | What the 2 × 2 forecast grid indexes; which response was chosen or what it cost |
| A three-raid leg with a recap and a total | Why HOT was picked over a "better" number; how the 60 was built |

---

## 5. Findings

### P1: blocks the target score

**P1-1. The decisions are made in tables of words.**
- The forecast (`scrambled/003`, `017`, `031`; `planned/003`, `017`, `031`) is three blocks of 2 × 2 heart grids keyed by text ("B MID / B SOUTH × hunter A: st 2 / B: st 3").
- The response list (`planned/020`, `breach/007`) is up to 14 rows of verb–target–cost–tier, and `planned/020` shows "MORE rows 1-7 of 14".
- The board shows only the *selected* cell, as a big arrow and ring onto the HQ (`planned/003`). The other 11 outcomes and every response row are absent from the city.
- The route-end hearts (`planned/018`, `breach/037`) show the device works. It just isn't extended to responses or the B×hunter split.
- Effect: N is capped near 5. Into the Breach is the counterexample: it resolves the same information on the grid.

**P1-2. The intensity card's headline number misreports its own value.**
- In `planned/011`, the panel offers LOW −6, NORMAL −5 and HOT −12 under the header "net leg value".
- In `planned/012`, the greedy bot takes HOT at **−15** (that card's number after it bought the guard card).
- In the next raid, the second capture lifts leg value from 20.5 → 32.5 → 48.5 (`planned/013` → `015`).
- The same pattern repeats in `planned/025`/`026` (NORMAL **+2** vs HOT **−8**; HOT picked; leg value then goes 39.5 → 61.5 at `planned/027` → `029`).
- In `scrambled/011`/`012` the bot also takes the more negative card.
- So the number most players will compare leaves out HOT's own perk (the extra capture). This is the leg-level decision, and its readout points the wrong way.
- Effect: P loses about 1 point. D also suffers, because a player who trusts the number never learns the real tradeoff between HOT and Heat.

**P1-3. The response phase is frequently moot or pre-solved.**
- In `planned/002`/`006`, the panel reads "HOLD → HOLDS, no response changes this", and the bot then sits through the whole response beat.
- In `planned/030`/`034`, both HOLD and DEPLOY DRONE > SOU 1 yield **BATTERED**. The deploy row is gold ("beats HOLD") and costs +2 Heat, but nothing on screen says what it beats *on*.
- The plan screen itself prints "best: SACRIFICE SOU 0 → BATTERED" (`breach/002`, `018`, `034`) before launch, so the answer is known before the reveal it is meant to answer.
- In the breach line the "decision" each raid was HOLD against a sacrifice that the game labels better three separate times.
- Effect: the phase built around two sealed reveals carries little choice. D and S both pay.

### P2: costs points, does not block

- **P2-1. "Best" means two things.**
  - On the plan and forecast screens, "HOLD → DAMAGED · best: DEPLOY DRONE → BATTERED" uses worst-case tiers (`planned/016`/`017`).
  - Then "12 outcomes with HOLD, worst/best: DAMAGED / HOLDS" uses best to mean the best *outcome*.
  - Raid 2 then came out HOLDS (`planned/024`), better than the "best" printed earlier.
  - Pick one word for the best response by worst case and another for the outcome range.
- **P2-2. The tier ladder has no stable order.**
  - The legend strip in every frame runs EVADED · HOLDS · BATTERED · DAMAGED · BREACHED.
  - The README lists BREACHED, DAMAGED, EVADED, BATTERED, HOLDS.
  - EVADED never appears in 9 raids across three runs.
  - Without words, I cannot tell whether EVADED is the best tier or between DAMAGED and BATTERED.
- **P2-3. Cobalt is overloaded.**
  - It marks the corp HQ, TAKEN districts (`breach/015`, `031`), the hunter's street beam (`planned/008`, `022`) and the drone threat's blue-cyan tones.
  - On `breach/037` a TAKEN tile, a drone sentry and a blue beam sit in the same street.
- **P2-4. Late-raid clutter.**
  - Frames `planned/030`–`037` and `breach/037`–`043` stack, in a small area: skulls and broken hearts at the tower, wrench and ⓘ glyphs, pink × marks, `?` markers, paws, numbered streets, colored sentries, dashed rings, gold card edges and a red HQ ring.
  - The wordless read degrades exactly when the stakes peak.
- **P2-5. The spiral is legible but steep.**
  - One DAMAGED raid (`breach/012`) left three districts DOWN against one repair (`breach/013`).
  - DECAY then took two (`breach/015`), wounds reached 2, then 3, and the third raid drew a dead card (`breach/033`).
  - The rule is clear and the record shows it. It is unclear whether a *competent* player can recover from one bad raid. The naive bot is not evidence of that either way. Show a recovery line in the capture set.
- **P2-6. Friction is layered but does not teach.**
  - The breach line gets a red plan line, a forecast banner, LAUNCH ANYWAY and a HOLD-confirm in every raid (`breach/003`, `004`, `008`, `019`, `020`, `024`, `035`, `036`, `040`).
  - Each one says *that* HOLD is worse. None shows, on the board, *what* the sacrifice gives up (district value, +1 wound) against what HOLD costs (−15 for the HOME pip).

### P3: polish

- **P3-1.** "FAST: every row, one tier" (`planned/032`–`037`) is unexplained. It reads like a rules modifier, but the footer suggests it is a playback speed.
- **P3-2.** The README conflicts with the frames:
  - The README says response results show only on hover and that SCAN (+3 Heat) adds the gold edge.
  - In the frames, every row shows its tier, gold means "beats HOLD", and SCAN never appears (`planned/020`, `breach/007`).
- **P3-3.** The "hunter hound" is drawn as one more beam with a small paw (`planned/008`, `036`). It has no silhouette, so the last reveal has the least presence.
- **P3-4.** Location vocabulary mixes "street 3 down", "street 0 up", "NORTH route to HOME" and "MID 1" in one panel (`planned/030`). Use one convention.
- **P3-5.** Panel text is about 9 px on the contact sheets. The score breakdown in the record (`planned/039`) is the clearest screen in the lab; use it as the model.

---

## 6. The three changes that would raise the score most

1. **Put the forecast and the responses on the city** (N +2, P +0.5, V +0.5).
   - Extend the route-end markers: put a tier glyph on each B-candidate lane and each hunter street, so the 2 × 2 becomes "these two lanes × these two streets".
   - On hovering a response row, ghost its sentry or sacrifice onto the target district, and show the resulting tier at HOME.
   - The panel becomes a confirmation, not the main source of information.
2. **Make the response phase earn its beat** (D +1, S +1).
   - When no response changes the tier, say so with a single board flash and auto-advance. Do not run a full response screen (`planned/006`).
   - Stop printing "best:" on the plan screen.
   - Let responses trade on axes the tier hides: district value at risk, wound count and Heat band crossings. Show those as a three-icon delta per row, so "beats HOLD" means something visible.
3. **Make the intensity card's number honest** (P +1, D +0.5).
   - Fold the extra capture's expected value and the Heat-band crossings into the headline (or show them as separate signed chips).
   - Then HOT −15 vs NORMAL −5 becomes the real comparison the greedy bot is making (`planned/012`, `026`).
   - Add the band crossing, for example "crosses 75: +1 beam, +1 card, −6", as a glyph on the card.

Together these are worth about +5 on /50 (to about 41) and +1 on S. That would put the lab beside Invisible, Inc., with better P.

---

## 7. Is the remaining gap a rules ceiling or a presentation ceiling?

**Mostly presentation, partly rules.**

- **Presentation (about 2/3 of the gap to Into the Breach):**
  - N (5) and V (6) are presentation problems. The information exists and is correct; it is in the wrong place.
  - The route-end markers prove the board can carry it.
- **Rules (the other third):**
  - D (6) and S (6) have a real rules part. Once the forecast is this complete, a three-tier response often collapses to one row, and with only four card verbs, placement is mostly type matching.
  - Fixing the display alone will not create choices.
  - The responses need costs that differ along axes the tier does not summarize, and the hand needs more than type and verb to make placement interesting.
- **C (9) is already at its ceiling.** Do not add more persistence; it is the strongest part of the lab.
