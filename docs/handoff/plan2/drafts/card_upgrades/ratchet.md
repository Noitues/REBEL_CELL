<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__ratchet; status ok; tokens in 5122 cache-write 0 cache-read 32585 out 1127; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: ratchet

1. **Role**: a neutral reward-pool tool that shifts the inner ring by a large fixed step (8 of 30 ticks, nearly a full 10-tick segment), so you can reach a far modifier without spending nudges.

2. **Upgraded card**: "Ratchet+". One level only, because the card is a single number plus a cost.
- RAM cost: 2 → 1.
- Cycle cost multiplier: ×1.5 (55 → 83, rounded).
- Text: "Move your inner ring 8 ticks clockwise. Then nudge it ±1 for free."
- Effects:
  1. NUDGE-type move, as today: type SPIN-like inner move (existing type 5 = NUDGE), target OWN_WHEEL, ring_scope INNER, amount 8, no status, duration 0.
  2. NUDGE, target OWN_WHEEL, ring_scope INNER, amount 1 (player picks the direction, as with Feather Touch), duration 0.
- Exhaust: false (unchanged). wheel_target: OWN (unchanged).

**Why this rider, and why it isn't strictly dominant:** the card stays a large inner-ring shift and gains fine alignment at the end. This fixes its real weakness: 8 ticks is a coarse step, and inner segments are 10 ticks wide. It does not become a different card. Neither a cost cut alone nor the rider alone was enough: the cost cut keeps it playable on a RAM-tight turn. The rider is a sidegrade in one spot: the 1-RAM cost rewards using it as a cheap setup before a card that depends on the inner ring. Ratchet remains weaker than Inner Snap for a "snap to the nearest centre" result when you are already near a centre.

3. **Interplay**
- Inner segments are fixed at 3 × 10 ticks. N12 changes the outer ring only, so the 8 + 1 move is unaffected by variable slice sizes. Inner modifiers still read by segment, not by sub-tick quality.
- With R9 (corruption doubles RAM where the acting pointer reads a CORRUPTED slice), a 1-RAM card costs 2 on a corrupted slice, so the base card would cost 4. Cheap cards are the good ones to keep playable under corruption.

4. **Data**
- `ram_cost` 2 → 1.
- `cycle_cost` 55 → 83.
- `description` updated.
- `effects` gains a second `EffectData` (type 5, target 1, ring_scope 1, amount 1).
- Dependency: the free ±1 step needs player choice of direction. If NUDGE on a card already supports ±1 choice (as Feather Touch and Ring Tap do), this is data-only. Otherwise NEW: a "choose direction" flag on card nudges. Fallback: set the second nudge to a fixed +1 clockwise, or drop the rider and keep only the cost cut.
- No new rules; the preview shows the final inner position as usual, so preview equals result.

5. **Q:**
- Should the free ±1 be limited to the inner ring (proposed), or let the player pick either ring?
- Is a RAM cost of 1 too cheap next to Gear Shift (5 ticks, 1 RAM)? If so, keep 2 RAM and make the + version a pure rider.
