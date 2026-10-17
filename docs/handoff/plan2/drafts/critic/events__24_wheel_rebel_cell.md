<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__24_wheel_rebel_cell; status ok; tokens in 3791 cache-write 0 cache-read 32585 out 1810; cost $0.016. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/24_wheel_rebel_cell

**Verdict:** FIX

## Issues

1. **BLOCKER, template / ids:** `echo_process` and `loyalty_test` are real enemy ids, but the draft was told to use only ids from the supplied list. The list isn't shown here, so confirm both are on it. `rc_witness` and `ew_rc_witness` are new content ids, which is fine as the event's own ids.
2. **MAJOR, determinism ("previews must equal results"):** Slice 1 gives a "random Daemon (`events` stream)". Its random roll happens after the player has committed, which hides the outcome from the preview. Rolling at wheel-open (checkpointed) and showing the Daemon on the slice would fix this.
3. **MAJOR, design quality (dominance):** The wheel's value is far below Choice 3, and Choice 3 has no wheel risk.
   - Choice 3 gives 6 Schematics plus a 0.8× HP `echo_process` for 8 HP. This is a guaranteed gain.
   - The wheel averages about 15 Cycles-equivalent. Fixing the pointer start (below) doesn't change that.
   - Choice 2 pays 10 Cycles for only −2 Heat. Slice 6 gives −6 Heat for 6 HP. Choice 2 is dominated at nearly any pointer position.
4. **MAJOR, arithmetic / economy claims:** The draft says 6 Schematics is "about a quarter of a typical Rack's worth", which is unsupported. The wheel's slice sizes sum to 30, which is correct. The EV shares are wrong: Slice 2 is 6/30 = 20 %, Slice 3 is 20 %, Slice 4 is 7/30 ≈ 23 %, Slice 5 is 5/30 ≈ 17 % and Slices 1 and 6 are 10 % each. That is consistent, but the "15 Cycles-equivalent" figure shows no arithmetic.
5. **MAJOR, sub-tick rules (R11):** The draft says "nudge ±1 tick, OUTER ring" on a wheel with no inner ring, and gives no `tick_quality` for the event wheel. If quality maps to nothing, a "Perfect" at a 3-tick slice centre is meaningless unless the outcome scales with it. State that the quality tier is cosmetic, or give each outcome a Perfect/Good/Weak scale.
6. **NIT, nudge currency:** The "player chooses the currency each time" payment adds three-way UI. It is cheap to specify, but it also makes −1 Heat or −2 HP strictly better than Cycles in most states. Heat isn't a campaign-neutral currency, so −1 Heat should be reconsidered.
7. **NIT, template:** `dispatch_clue` is "false" and `foreshadows` is empty. This is fine, but the template expects clue or foreshadow "if apt". A REBEL_CELL event about the Handler arguably fits.
8. **NIT, fields:** Slice 5's combat should state the combat stake (rewards), but Q2 leaves it open. Choice 1 has no "(new)" combat entry.

## Concrete fixes

- **Issue 2:** Replace Slice 1 with "Reward: Daemon, rolled from the `events` stream when the wheel opens (checkpoint) and shown on the slice; +3 Heat." Preview then equals result.
- **Issue 3:**
  - Choice 2: change to "−5 Heat, 15 Cycles".
  - Choice 3: change to "−8 HP, +4 Schematics; next combat `echo_process` hp_by_tier ×0.9".
  - Slice 4 Blank: change to "+10 Cycles (she remembers a small thing)", so the default outcome is not a loss.
- **Issue 4:** Add the sum: EV = 0.10×(Daemon≈40) + 0.20×(Firmware≈25) + 0.20×35 + 0.23×10 + 0.17×(fight ≈ +10 net of risk) + 0.10×(+6 Heat value −6 HP ≈ 0) ≈ 4 + 5 + 7 + 2.3 + 1.7 ≈ 20 Cycles. State that Cycles-equivalent values are placeholders.
- **Issue 5:** Add "Quality tiers on event slices are cosmetic. The outcome is fixed per slice, and the sub-tick map is not read." Also drop "OUTER ring".
- **Issue 6:** Fix extra-nudge payment to Cycles (8) only, with 2 HP as the alternative. Drop the Heat option.

## Keep

- The uneven slice sizes (3/6/6/7/5/3 = 30) make the pointer's position decide what you pay to reach each outcome.
- The Cell-as-judge premise and the "a steered memory is a corrupted memory" tone fit REBEL_CELL.
- The 4-nudge cap and the N17 dependency with its fallback are stated clearly.

## Q:

- Q: Should the Handler foreshadow (a `dispatch_clue`) live in the wheel's Slice 1 reward instead of the event header?
- Q: Does the 8 HP cost in Choice 3 count against the next fight's start HP, and should it be gated on HP threshold?
