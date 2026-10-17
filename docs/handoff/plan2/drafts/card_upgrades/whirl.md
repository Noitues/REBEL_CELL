<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__whirl; status ok; tokens in 5119 cache-write 0 cache-read 32585 out 1196; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: whirl

1. **Role**: A mid-size neutral spin (7 ticks, 2 RAM) that lands a wheel one slice-and-a-bit away. It fills the gap between Twist (4) and Heavy Spin (9), and it is the "reposition the target's needle" tool when nudges are too expensive.

2. **Upgraded card**: **Whirl+** (a single + level)
- RAM cost: 1 (was 2)
- Cycle cost multiplier: 1.5× (55 → 83)
- Text: "Spin a wheel 7 ticks clockwise. If you already spun this turn, spin 3 more."
- Effects (EffectData):
  1. SPIN, target TARGET_WHEEL (the current `target = 2`; `wheel_target` stays ANY), amount 7, ring_scope WHOLE_WHEEL.
  2. SPIN, same target and wheel, amount 3, ring_scope WHOLE_WHEEL, gated by the existing "already spun this turn" condition that Momentum uses.
- Exhaust: false. wheel_target: ANY (unchanged).
- Why this shape: the cost cut is the main upgrade. The rider gives Whirl+ a combo identity without making it a different card. It is not a strict dominator: the 3 extra ticks are a bonus only when you chain, and 7 → 10 can overshoot a nudge-tuned landing. A player who wants exactly 7 pays only 1 RAM and ignores the rider, so Whirl+ is never worse than Whirl, but it isn't the best pick in every hand. The higher Cycle price offsets the RAM saving.

3. **Interplay**
- Variable slice sizes (R11): 7 ticks lands differently on each size, so the 3-tick rider matters more when slices are 3–4 ticks wide. It is a reach tool, not a precision tool.
- Corruption (R9): a cost-1 card on a CORRUPTED slice costs 2, the same as an uncorrupted base Whirl, so the discount survives one corruption tax.
- Satellites (R12): the spin still carries docked satellites with the host, as before.
- Resistance: a spin on an enemy wheel is still absorbed by its first R ticks, so the rider's 3 ticks are the first absorbed under Resistance 3.

4. **Data**: against `whirl.tres`:
- `ram_cost` 2 → 1.
- `cycle_cost` 55 → 83.
- `description` replaced.
- A second SubResource `fx1` (type 6, target 2, amount 3, ring_scope 2) is added to `effects`, with a conditional "if you already spun this turn" flag.
- The condition has no field on EffectData today. Momentum implements it, so the likely route is to reuse the Momentum handler as a CUSTOM effect with `custom_handler`. That is a data-only fallback using the existing handler, with no N# required. Otherwise it needs NEW: `condition_spun_this_turn` on EffectData (S).
- The two SPIN effects must resolve as one preview, so the preview shows the combined 7 or 10 ticks and equals the result.

5. **Q:**
- Should the rider be a flat +3, or a percent-style "the same again at half" to scale better against resistance?
- Is a 1 RAM spin at 7 ticks too close to Jolt (3 ticks, 1 RAM) and Counter-Spin (5 ticks, 1 RAM)? Should the + version stay at 2 RAM and take a stronger rider instead?
