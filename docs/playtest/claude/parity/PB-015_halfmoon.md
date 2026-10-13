# Decision parity — PB-015/halfmoon

33 paired turns; 30 clearly worse than the best plan; 20 probed (better plan visible from the screen: yes 0, partly 16, no 4). Cost $0.21.

# Visual changes ranked by turns fixed

Nearly every finding comes down to one missing thing: the screen shows where each pointer is now, not where it will land. The changes below split that into distinct visual changes. They are ordered by turn count.

## 1. Live ghost pointers on the wheel rims (predicted landing tick, tinted by quality)
**Element:** wheel rim and pointer on both wheels. A faded second needle appears on hover or queue, with the landing slice highlighted and a PERFECT/GOOD/WEAK tint. A small chip names the slice, e.g. "Overflow 12 PERFECT" or "Null".
**Turns (20):** 0009, 0030, 0032, 0034, 0041, 0044, 0055, 0056, 0060, 0061, 0064, 0075, 0080, 0089, 0090, 0099, 0101, 0106, 0108, 0109
**Why:**
- Players had to count ticks by hand on irregular wheels with unequal slice widths.
- They could not see that Jolt, Brute Spin or a nudge would move the enemy pointer onto a harmless Null or Defrag slice.
- They could not see that a ±1 nudge or a spin would reach a Perfect on their own wheel.
- Several plans (0034, 0075, 0109) ended with the player's pointer on a WEAK slice or dealing 0 damage, which a preview would have shown beforehand.
- Multi-step plans (0041, 0075, 0080, 0089) needed chained previews that update as each card is queued.

## 2. Projected-outcome chips on the HP bars and near End Turn
**Element:** the HP and damage chips under each wheel, the enemy HP bar, and the area by the End Turn / SEND IT button. These chips currently show only the "do nothing" result (e.g. the red -6 and -24). They should show the result of the queued plan: "Daemon 30→0 KILL / you take 0".
**Turns (13):** 0030, 0032, 0041, 0044, 0055, 0056, 0060, 0061, 0064, 0080, 0090, 0106, 0108, 0109 (0109 and 0108 also benefit from the lethal match)
**Why:**
- Players never saw that a plan was lethal, because damage numbers were not linked to enemy HP.
- The "take 7" or "take 6" cost of the enemy's attack was easy to miss (0055 costs 2 HP for doing nothing).
- Comparing plans by outcome was impossible, e.g. the 5-action plan that dealt 9 versus the 3-action plan that dealt 43 (0090).

## 3. Mirror Flip hover preview of the flipped wheel
**Element:** the card hover state. It should show the flipped wheel layout and the new landing slice.
**Turns (4):** 0009, 0034, 0041, 0080 (0108 also names Mirror Flip)
**Why:** "Flip a wheel" gives no sign of what the flipped wheel looks like. The player cannot tell that it puts the Overflow slice under the pointer or moves the enemy onto Null.

## 4. Persistent offset or tick scale on each pointer
**Element:** the pointer on the wheel. It should carry a small tag such as "GOOD +1" or "WEAK +2", and the slices should show tick marks.
**Turns (6):** 0032, 0055, 0061, 0064, 0089, 0108
**Why:** A one-tick offset from the slice centre is invisible, so GOOD looks like PERFECT. The "Dead centre" dialogue in 0061 was also misleading.

## 5. Full, untruncated card text with movement and effect
**Element:** the card faces. Text such as "Blocked while th…" and "OVERCLOCK your slice under th…" is cut off. Cards should state direction and tick distance, and show an arc on the rim on hover.
**Turns (6):** 0030, 0032, 0034, 0075, 0108, 0109
**Why:** Players could not tell what Overdrive, Fine Tune, Jam or Mirror Flip actually did.

## 6. Clearer enemy intent
**Element:** the enemy slice label and intent icon. It should show who gets hit and for how much (e.g. "Shim 7: you lose 1 RAM", or a damage number in place of the sword glyph). It should also show that a Null slice cancels the action.
**Turns (4):** 0009, 0030, 0060, 0075
**Why:** The yellow "LANDS HERE" lines and the sword glyph pointed attention at the wrong thing. The true cost of leaving the enemy pointer where it was stayed hidden.

## 7. Free nudge affordance
**Element:** the "FREE NUDGE 1" banner and the nudge control. They should be tied to the wheel with a hover ghost showing the +1 and -1 results.
**Turns (3):** 0055, 0064, 0099
**Why:** The banner was easy to miss and showed nothing about what the nudge would do. In 0099 the player also did not realize the enemy wheel could be nudged.

## What the screen showed well
- Slice values and special slices were readable. The 12-damage Overflow slice was clearly marked as the big hit (0009, 0080).
- The current pointer positions were always visible on both wheels.
- Current-state damage chips (-7/-12, -6/-24) were clear for the "do nothing" case.
- The Null slice (1/0) was identifiable as a slice type.
- Card names and short descriptions ("spin 3 / 6 ticks") gave the basic action, even though they did not give the landing point.
- Result tags (PERFECT/GOOD/WEAK, offsets) appeared after the action (0109, 0099), so the system exists and only needs to be shown earlier.
