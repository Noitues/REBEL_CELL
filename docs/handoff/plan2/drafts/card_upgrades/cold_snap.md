<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__cold_snap; status ok; tokens in 5176 cache-write 0 cache-read 32585 out 1082; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: cold_snap

1. **Role:** A neutral tempo-and-defense card. It denies the target's respin so the player can plan against a known tick, and adds a little block. At 3 RAM it is too expensive for what it does, which is why it is a reward-pool card and not a staple.

2. **Upgraded card: Cold Snap+** (one level only; no second level needed)
- **RAM cost:** 2 (was 3).
- **Cycle cost multiplier:** ×1.4 (70 → 98), because the cost reduction is the main gain.
- **Text:** "The target skips its next respin and you gain 6 block."
- **Effects:**
  1. FREEZE: target = TARGET_WHEEL, ring_scope = WHOLE_WHEEL (unchanged).
  2. GAIN_BLOCK: target = SELF, amount 6, amount_mode FLAT (was 3).
- **Exhaust:** false. **wheel_target:** ENEMY (unchanged).
- **Why this and not a rider:** the card is already a Freeze with a bonus. Making it cheaper and doubling the block sharpens it without changing what it is.
- **Not strictly dominant.** Freeze (3 RAM, exhaust) remains the pure-lock option. At 2 RAM, Cold Snap+ is cheaper than Freeze and also repeatable, but its block is small beside Bulwark's 12. It is a tempo card, not a defense card.

3. **Interplay:**
- **Block scaling:** the 6 block is a player amount. It is not scaled by tier (R2 scales enemy amounts only), and it expires at the start of your next turn (R13).
- **Compliance-style resistance:** Freeze ignores resistance today (it is not a nudge or flip), so the freeze still works against Weight and Compliance Lock.
- **N7 respin lock:** if an enemy sets `respin_locked`, that blocks the player's own Respin. It does not affect Freeze, because Freeze skips the target's start-of-turn respin. A boss that auto-respins every turn makes the card a deterministic-planning tool.
- **R9 corruption:** the card is played, not resolved on a slice, so a corrupted slice under the acting pointer would double its RAM cost (2 → 4). Cleanse first.
- **No interaction** with tick quality or the Parasite ring.

4. **Data:**
- `ram_cost` 3 → 2.
- `cycle_cost` 70 → 98.
- `fx1.amount` 3 → 6.
- `description` updated.
- Add `upgraded_from = &"cold_snap"` on the + card. This depends on the card-upgrade pass's linking field, so mark it **NEW: card upgrade link** (a data-only id convention such as `cold_snap_plus` works as a fallback).
- No new effects, and no dependency on N1 (amount modes): the amount is flat.

5. **Q:**
- Should the + version keep a one-turn Freeze, or gain "also skips the target's next nudge"? The nudge skip would need N7 and would make the card too strong.
- Is a 40 % Cycle premium right for a cost-only upgrade? Balance sim to confirm.
