<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__tailspin; status ok; tokens in 5187 cache-write 0 cache-read 32585 out 1277; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: tailspin

1. **Role:** Neutral cantrip spin. It moves a wheel a little and replaces itself, so it adds a nudge-like adjustment without costing a card slot. It is a mid-cost cycling tool for tick fixes.

2. **Upgraded card: Tailspin+** (one + level is enough; this is a cheap common-tier card)
- **RAM cost:** 1 (was 2).
- **Cycle cost multiplier:** ×1.25 (65 → 81), because the cost cut is real value.
- **Text:** "Spin a wheel 4 ticks clockwise and draw 1 card. If you already spun this turn, draw 2 instead."
- **Rarity, exhaust, wheel_target:** unchanged (rarity 1, exhaust false, wheel_target ANY).
- **Effect list:**
  1. SPIN: target TARGET_WHEEL (2), amount 4, ring_scope WHOLE_WHEEL (2). Unchanged.
  2. DRAW_CARDS: target SELF (0), amount 1. Unchanged.
  3. DRAW_CARDS: target SELF, amount 1, gated on "a spin already resolved this turn" (NEW condition).

**Why this and not just −1 RAM or +1 draw.** A flat cost cut alone would make it strictly better than Twist at the same number. The conditional extra draw pays off only in spin-heavy turns, so it is not a straight upgrade in every hand. It borrows Momentum's "already spun this turn" check but rewards a card, not distance. Without a prior spin the card is simply a 1-RAM Tailspin, which still beats the original on cost alone. Because the draw bonus depends on turn order, the + version is not an automatic include in every deck: it pairs with Twist, Jolt, Whirl and Flick, not with nudge-only decks. Spin distance stays at 4 so the card is not turned into a different spin.

3. **Interplay**
- **Tick quality and slice sizes (R11):** a fixed 4-tick spin lands differently on 4-, 5- and 7-tick slices. The extra draw gives the player more chances to find a fix card when the 4 ticks overshoot.
- **Corrupted slices (R9):** the card is played, not resolved on a slice, so the double-RAM tax does not apply. A cheap 1-RAM cantrip costs less to dig for Cleanse.
- **Enemy resistance:** it is still absorbed by resistance, and it is blocked less than Flip. This is unchanged.

4. **Data (changes against the current .tres)**
- `ram_cost` 2 → 1.
- `cycle_cost` 65 → 81.
- `description` rewritten.
- `effects` gains `fx2` (DRAW_CARDS, amount 1) with the condition below.
- `load_steps` 5 → 6.
- **New system:** a conditional effect, "only if a SPIN has resolved this turn". Nothing in N1–N20 covers it. Momentum already needs this check, so it probably exists as a CUSTOM handler. Tag it **NEW: spun-this-turn condition on EffectData**.
- **Data-only fallback:** reuse Momentum's CUSTOM handler script on `fx2`. If that is not reusable, fall back to cost 1 and unconditional "draw 1", which is a plain cost-cut sidegrade with no new system.

5. **Q:**
- Q: Does a Respin or a Flip count as "already spun" for the condition, or only SPIN effects? Proposed: SPIN only, to match Momentum.
- Q: Should the extra draw also fire if the earlier spin was absorbed fully by resistance? Proposed: yes, because the spin was played, and this keeps the preview simple.
