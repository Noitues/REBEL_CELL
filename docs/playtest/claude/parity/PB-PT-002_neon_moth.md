# Decision parity — PB-PT-002/neon_moth

87 paired turns; 79 clearly worse than the best plan; 20 probed (better plan visible from the screen: yes 0, partly 17, no 3). Cost $0.21.

# Visual changes ranked by turns fixed

Nearly every finding comes down to one missing feature, a **landing preview**. I split it into three distinct changes by what the player needs to see. Some shots appear in two entries because they had two findings.

## 1. Ghost pointer and landing slice on the wheel rim (hover/queue preview)
**Screen element:** wheel rim and pointer, on both the player and enemy wheels.
**Change:** When a card or nudge is hovered or queued, draw a ghost pointer at the post-play tick. Highlight the landing slice with its value and its PERFECT/GOOD/WEAK label. Show a dashed arrow from the old to the new position, and chain the preview across queued cards. Also show the end-of-turn resolve position by default, since the current pointer is not where the turn resolves.
**Turns (20 findings, 15 shots):** 0032, 0048, 0052, 0053, 0059, 0061, 0064, 0065, 0066, 0067, 0069, 0072, 0041
**Why:** The player had to simulate tick counts, flips, multipliers and nudges by hand. Examples are Jolt, Mirror Flip, Overdrive and Fine Tune combining into a PERFECT on Overflow 12. Others are nudging the enemy onto Null or Dose, or flipping it onto Dose. The preview shows each of these results directly. It also covers the cases where the best plan was off the enemy wheel.

## 2. Projected-outcome readout (deal / take / kill) next to the HP bars and End Turn
**Screen element:** HP preview chips, enemy HP bar, and the area near SEND IT / End Turn.
**Change:** Show a live "if you end now / after this plan" line, for example "Deal 36 / Take 0, Daemon dies" or "Agent 31→19". Update it as cards are hovered or queued, and show the do-nothing outcome alongside for comparison. Sum the RAM cost of the queued sequence.
**Turns (15 findings, 14 shots):** 0032, 0048, 0052, 0053, 0059, 0061, 0064, 0065, 0066, 0067, 0069, 0072
**Why:** Even when the wheel is understood, the payoff (a kill, or 0 damage taken) is not visible. The existing chips only describe the do-nothing state. "LETHAL" in 0053 even reads as already won.

## 3. Make the PERFECT/GOOD/WEAK offset and its payoff legible
**Screen element:** pointer tag, slice numbers, and slice-center marks.
**Change:** Add slice-center ticks and a numeric offset on the pointer, such as "-1 GOOD". Show the PERFECT bonus on the slice with a gold glow and a boosted number, such as 6→12. Label nudge costs (0 RAM).
**Turns (7):** 0041, 0053, 0059, 0064 (two findings), 0061, 0069
**Why:** A 1-tick offset is invisible on the rim. "GOOD" reads as positive even when it is hiding a doubling. The slice number does not change between GOOD and PERFECT.

## 4. Untruncated, concrete card text
**Screen element:** card faces (Mirror Flip, Overdrive, Fine Tune, Jolt, Brute Spin).
**Change:** Stop truncating ("Blocked while th…", "OVERCLOCK your slic…"). Say which ring or wheel is affected and what the effect does to the damage number. A hover tooltip is enough.
**Turns (7):** 0032, 0052, 0053, 0059, 0061, 0066, 0072
**Why:** This is secondary to the preview, but it removed the last clue to what a card does.

## Minor
- **Enemy intent clarity (0052, 0065, 0069, 0072):** show the incoming damage and the RAM drain tied to the specific slice about to hit.
- **Name mismatch (0065):** "Dosage Dispenser" in the target name does not match the "Collections Agent" label on the wheel.
- **Dim Overflow tile (0052):** the pale Overflow tile does not read as the big payoff.

## What the screen showed well
- Current pointer position and slice values for both wheels.
- GOOD/WEAK tags, which are accurate for the current state, though they are easy to misread as an outcome.
- HP preview chips (e.g. 40→34, 57→54), which are correct for the do-nothing outcome. They are a good base for the projected readout in change 2.
- Enemy and player HP, and incoming damage numbers.
- The existence of the big Overflow 12/14 slices, so players could spot the target. Only the way to reach it was hidden.
