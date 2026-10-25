# Raid concepts r9: critic review (fresh, no prior reviews read)

**Verdict: build M9c (sealed + reactive spoof).** It is the only concept where the one input carries information
the plan could not have had. Fix its readability first, because it currently has the worst no-words score of the four.
S9 fits the core verb best, but its measured stakes are too small. It also breaks GDD pillar 4 ("Wheel mechanics exist
only in combat"), and that is a designer decision, not something to settle quietly.

Read order: scrambled frames first, then SPEC.md and the mockups. GDD 1.2 and 4.3 were checked for pillars and Heat.
Reference sheet: `D:/rc_tmp/raid_design_lab/critic_r9/refs_vs_concepts.png` (script in `scripts/sheet.py`).

References (images only, from Steam store pages):
- Into the Breach: https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/590380/ss_4b985c7747c1ff0b7fbbf3eaf8ca5a1272f0dadb.1920x1080.jpg?t=1755610784
- Invisible Inc.: https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/243970/ss_5bc3599a1531d384933c93e2cc8f5df464ce9bec.1920x1080.jpg?t=1790784841
- Inscryption: https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1092790/ss_3b714682e9e0a214df1630a234e9f6764528eece.1920x1080.jpg?t=1777572925

## Score table

| Concept | W | P | N | D | C | /50 | Fit | V | S |
|---|---|---|---|---|---|---|---|---|---|
| M9a sealed, zero input | 6 | 8 | 5 | 5 | 6 | **30** | 6 | 5 | 5 |
| M9b timed spoof | 6 | 7 | 6 | 4 | 6 | **29** | 6 | 5 | 6 |
| M9c sealed + reactive spoof | 6 | 7 | 4 | 7 | 6 | **30** | 6 | 5 | 7 |
| S9 ring-siege spinner | 7 | 6 | 6 | 6 | 5 | **30** | 7 | 6 | 6 |

One-line reasons:
- **M9a**
  - **W6.** Heat bar, notch and number say "you crossed 50". Nothing says what raised Heat or when the next raid comes. Invisible Inc.'s alarm dial is on screen every turn; here the warning only appears at contact.
  - **P8.** The exact per-candidate table (-26 / -2 / -2) is the strongest forecast of the four.
  - **N5.** Two "1, 2, 3" number sets collide: filled badges are beam-2 candidates, hollow badges are beam origins.
  - **D5.** Three tokens on six assets against three candidates. A small minimax that the forecast solves for you.
  - **C6.** The key bar crash (19 to 1) hits the run goal hard. But the ledger does not add up (see below), and "CELL HOLDS" stamped on a near wipe sounds wrong.
  - **Fit6.** "Evading a sweep" fits the premise well but does not use the wheel.
  - **V5.** Clean, but half the screen is empty and the lever legend has no labels.
  - **S5.** A single 1-in-3 reveal, then deterministic beams. Watchable twice; skipped by the fifth raid.
- **M9b**
  - **P7.** The landed vs missed outcomes are exact, but the result now depends on execution.
  - **N6.** The least cluttered: teal ring, teal window, check vs cross. A wordless reader gets "press here, save 14".
  - **D4.** The press holds no decision. Its target is fixed in the plan. It is a reflex tax on a solved plan; only the plan-around effect (50%) is depth.
  - **C6.** A 14-point swing on a reflex is harsh. "DOWN until repaired" stays on screen with 0 down.
  - **S6.** Real tension, but you know the moment in advance.
- **M9c**
  - **D7.** A real read-and-react: hedge the plan, see the reveal, choose the target live. Reacting beats committing on 60% of networks.
  - **P7.** The panel shows only the best-reaction values. The missed values (-23 / +1 / -9) appear only in the caption.
  - **N4.** The most layers: three candidates, two number systems, a teal ring that moves after the reveal, and the bar. The scrambled frames rely on the footer.
  - **S7.** The best playout: a reveal, then a decision, then execution, in about two seconds.
- **S9**
  - **W7.** The best "what and when": a roster with wave numbers, threats visibly queued on spokes, and frame 6 shows the next threshold (75) and a fourth spoke. Still no "why".
  - **P6.** The forecast is exact but unverifiable by a human: 3 rings, 3 speeds, 3 spokes, 30 ticks. Two of six rows are blank and the table is not tied to the spokes. Players will tune against a black box.
  - **N6.** Threat silhouettes, the X, the U-turn and the house read without words. Ring speed (chevrons) is not drawn in any frame.
  - **D6.** A large stocking space (9 slices into 18 positions, plus speeds and the snap), but the outcome band is flat: 1 kill of 6, -7 vs -12, snap worth +2 on average.
  - **C5.** Broken slices and returning survivors persist well, but a teal "CLEAN" stamp over 5 of 6 threats surviving tells the player they won when they mostly did not.
  - **Fit7.** Wheels, slices under pointers and WEAK off-center map directly to the core verb and pillar 1. Taken off for the pillar 4 conflict.
  - **V6.** The strongest composition, but the playout's top spoke stacks icons and HP pips into mush.
  - **S6.** Rings turn and contacts tick, but 4 of 6 threats never get touched. The one live moment is on beat 29 of 30.

## Ledger and consistency errors (all concepts)
- **M9a, frame 5.** Net shows -26 in the coin icon, but the key bar drops 18 (19 to 1). The caption calls 18 "repair". The other 8 are not shown anywhere, and coins and Schematics share one icon.
- **M9a and M9c, frame 3.**
  - The evaded candidates show -2 (M9a) and +1 (M9c). Decoy (-3) plus go-dark income does not produce either number. There seems to be a hidden evade bonus that is never displayed.
  - Candidate-2 line runs off the grid at x≈690 to nothing.
- **M9b, frame 5.** EVADED and 0 down, yet the red "DOWN until repaired" label stays under an untouched bar.
- **S9, frame 5.** "CLEAN" with 5 survivors and 1 broken slice. If CLEAN means "home untouched", say so; otherwise rename it.
- **S9, frames 2 to 4.** The spec says ring speed is set with chevrons. No chevron or speed control is drawn in any frame.

## Which to build: M9c
- It is the only concept whose input is a decision made with new information. M9b's press is a fixed QTE, and S9's snap target comes from the forecast.
- Its depth figure (60% of networks reward reacting) is the best measured number in the spec. S9's +2 average stakes is the worst.
- Its weaknesses are presentation (N, P), which mockup work can fix. S9's weakness (flat stakes, opaque tick math) is structural.
- It stays inside pillar 4 (a graph auto-battle with a planning phase). Its timed press is on pillar 1 (precision is the currency of skill).

Runner-up: S9, if the designer is willing to amend pillar 4. Its ceiling for fit and spectacle is higher than any Manhunt variant.

## Top 3 changes per concept

**M9a**
1. **Frames 2 to 4: one numbering system.**
   - Candidates get letters or ghosted line styles (A/B/C), not 1/2/3.
   - Beam order goes on the beam origin as in Into the Breach: the number sits on the attacker.
   - Draw the hunter in a distinct color with a "turns here" elbow at the first find. *(N +2)*
2. **Frames 3 and 5: an itemized ledger.**
   - Show repair (key), decoy (coins) and lost income (coins) on separate rows, each with its own currency icon.
   - Show the evade bonus, if there is one, as its own row. *(P +1, C +1)*
3. **Frame 1 and campaign HUD: a persistent "next raid" countdown on the Heat meter.**
   - Shown during netruns, with per-node Heat deltas ("this node +4 Heat") so the cause is visible before contact. *(W +2)*

**M9b**
1. **Designer decision: make the spoof target choosable during the playout (any node, any beam)**, instead of planned at a teal ring. Without this the press stays a reflex test. *(D +2)*
2. **Frame 4: widen the window and show it on the board**, as a shrinking ring on the node, not a bar in the side panel. The eye cannot watch both. *(N +1, S +1)*
3. **Frame 5: fix the leftover "DOWN" label.** Show the 14 you saved as a struck-through -18 next to -4. *(C +1)*

**M9c**
1. **Frame 3: show missed values beside best-reaction values in the panel** (for example -13 / -23), not only in the caption. A forecast that hides the downside is not an honest forecast. *(P +1)*
2. **Frames 2 to 4: de-clutter for the no-words test.**
   - Candidates as letters.
   - The unselected candidates collapse at the reveal (they already fade; make them vanish).
   - The spoof window as a ring on the node, not a side-panel bar.
   - A one-beat freeze at the reveal so the player can choose. *(N +2, S +1)*
3. **Designer decision: decide whether the reaction needs to be timed at all.**
   - Option one: a click on a node during a short reveal pause, which still breaks zero input but needs no dexterity.
   - Option two: keep the timing (on pillar 1) with a window of at least 300 ms.
   - Either way, show "best reaction" only after the reveal, so the decision is not pre-solved. *(D +1)*

**S9**
1. **Designer decision: raise the stakes or cut the duration.**
   - 4 of 6 threats untouched in 30 beats is a dead playout.
   - Either make survivors cost more and kills pay more, or cap at 15 beats with denser contacts.
   - Then re-measure snap value (it is currently +2). *(D +1, S +2)*
2. **Frame 3: put the forecast on the wheel.**
   - Draw contact ticks per spoke as pips on the rim (as Into the Breach draws damage on the tile).
   - Draw each threat's fate glyph at the head of its spoke instead of in a detached table.
   - Draw ring-speed chevrons. *(P +2, N +1)*
3. **Frame 5: rename or recolor the verdict.**
   - Use teal only when no threat survives.
   - Otherwise use amber with "HOLDS, 5 RETURN".
   - Show survivors queued on the rim in frame 6, so the deferred consequence is visible. *(C +2)*

## Do the one-press inputs earn breaking zero-input?
- **M9b: no.**
  - The press is pre-planned and carries no information. It turns a solved plan into a reflex check worth 14 points.
  - Planning around it changing the allocation on 50% of networks is real, but you could get that with a non-timed token.
- **M9c: yes.**
  - The press is spent after a reveal the plan could not see, and that is where its value comes from.
  - Timing it is defensible under pillar 1 but optional. The value is in the choice, not the reflex.
- **S9: not at current stakes.**
  - "Usually exactly one right moment", shown by the forecast, worth about +2, and "without scarcity the press adds nothing": that is a QTE with a precomputed answer.
  - It would earn its place only if the right moment depended on something the player learns during the playout.

## What the scrambled frames failed to communicate
- **M9a**
  - Which badge set is order and which is candidates.
  - That dashed means "hunter" (ghost and candidate lines are also dashed: three dashed meanings).
  - What the black disc does (go dark) versus the grey node (already dark).
  - Why the right-hand bar fell 18 when the number says 26.
  - That the orange stamp means you survived and not that you lost.
- **M9b**
  - That the teal ring is planned by you and not a corp target.
  - That the bar in the side panel is synced to the beam on the board.
  - Why a red "down" label shows after a clean evade.
- **M9c**
  - Everything M9a fails on, plus:
  - That the teal ring moved because of the reveal.
  - That the forecast numbers assume you land the press (the missed values exist only in the scrambled caption).
- **S9**
  - Ring speeds and direction (no chevrons drawn).
  - Which inbound-roster row belongs to which spoke.
  - Why two forecast rows are empty.
  - That the pause glyph "29" is a plan marker and not a hazard.
  - That the U-turn means "comes back next raid" and is a cost.
  - That the red X on a slice is a permanent loss. The same glyph means "kill" in teal and "broken" in red, so color alone carries a reversed meaning.
