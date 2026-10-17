<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__tap_tap; status ok; tokens in 5121 cache-write 0 cache-read 32585 out 1187; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: tap_tap

1. **Role.** Neutral fine-tuning: spends 2 RAM for three ±1 nudges on one ring, so you can reposition a landing by up to 3 ticks (e.g. WEAK → Perfect on a 5-tick slice) without paying 1 RAM per nudge.

2. **Upgraded card: Tap Tap+** (one level only; no further levels needed)
- RAM cost: 1 (was 2). Cycle cost multiplier: ×1.5 (60 → 90).
- Text: "Four ±1 nudges on one ring."
- Effects (single EffectData):
  - type NUDGE, target TARGET_WHEEL, amount 4 (was 3), ring_scope OUTER (unchanged), status NONE, duration_turns 0, multiplier 1.0.
- exhaust: false. wheel_target: ANY (unchanged; the scope is still one chosen wheel and one ring).

Why this shape: the card stays "tap-tap", just bigger and cheaper. The 4th tick covers the 4-tick distance between Perfect and a slice edge on 7-tick slices under R11, and it reaches an adjacent slice's centre from a slice edge on a 5-tick wheel. Cost 1 puts it level with Fine Tune (2 nudges for 1 RAM) but with double the reach, so it is not a strict upgrade at every point:
- Fine Tune still wins on cheap fixes of 2 ticks or fewer, because it costs the same RAM and the Cycle price is lower (+ costs 90).
- The +'s real price is the shop and reward slot, since the base card remains in the pool.
- A cost of 1 is a clear sidegrade against Feather Touch (0 RAM, 1 nudge), which stays better for a single tick.

3. **Interplay.**
- Uneven slice sizes (R11): 4-tick slices have no Perfect, so extra nudges are mostly spent reaching a Good on a neighbouring 5- or 7-tick slice. 4 ticks usually clears that gap.
- Corruption (R9): played where the acting pointer reads a CORRUPTED slice, it costs 2 RAM, the same as the old base card. The cost-1 discount thus halves the corruption tax's bite on nudge cards, an intentional soft counter to the RAM debuff.
- Resistance: nudges on an enemy wheel are still absorbed per tick, so 4 nudges against Weight 3 move it only 1 tick. Jam and Ghost Step remain the answers there.
- Compliance Lock and Parasite-ring effects are unaffected.

4. **Data.** Changes against the current .tres:
- `id` &"tap_tap_plus"
- `display_name` "Tap Tap+"
- `description` "Four ±1 nudges on one ring."
- `ram_cost` 1
- `cycle_cost` 90
- `fx0.amount` 4
- `effects` unchanged otherwise.
- New systems: none; fully data-only. The + id needs a link from the upgrade pass (a mapping or `upgrade_of` field on CardData; NEW: card upgrade link, but not required for the card to work).

5. **Q:**
- Q: Should a card's + version replace the base in the deck in place, or be a separate reward-pool entry (as drafted here)? This affects the Cycle cost multiplier.
- Q: Does Ghost's "first nudge each turn ignores resistance" apply to every nudge in this card, or only the first?
