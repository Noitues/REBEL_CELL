<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__bug; status ok; tokens in 5211 cache-write 0 cache-read 32585 out 978; cost $0.013. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: bug

1. **Role**: A dead-code tax card. It is forced into the deck by ICE 11 (STARTING_BUG_CARD), never offered as a reward, and removable at a Mainframe. It costs 0 RAM to play, drains 1 RAM, and exhausts.

2. **Upgraded card**: this is a deliberate exception to "sharpen the card". A Bug is a penalty, so the + version is a **worse** Bug. It is not a reward upgrade. It is the sidegrade of a Bug the player has neglected, and it only exists if the designer wants a pressure mechanic.

   **Recommendation: do not build a + version. Keep Bug as a single-level card.**

   One-line reason: an upgrade that makes a penalty card harder to ignore gives the player no chance to want it, and a strictly better Bug would break the ICE 11 rule. If the designer still wants one, use this draft:

   **Bug+ ("Rotted Bug", placeholder)**
   - RAM cost 0, Cycle cost multiplier ×1.0 (the Mainframe removal price is unchanged; the player is the one choosing to remove it)
   - Text: "Corrupted code. Drains 2 RAM when played. Exhaust."
   - Effects: DRAIN_RAM, target SELF, amount 2, ring_scope OUTER (unused), status NONE, duration 0
   - exhaust true, wheel_target OWN (unchanged)

   It only reaches the deck as a Bug that has been hit by a future "decay" effect, never by player choice. That would be NEW: a Bug-decay hook, for example a Heat MAJOR threshold or the Parasite ring turning a Bug into Bug+.

3. **Interplay**: Corruption now doubles RAM costs on CORRUPTED slices, but Bug costs 0 to play. Double of 0 is 0, so the drain is not multiplied, and Bug+ keeps a flat 2. A deliberate play on a corrupted slice therefore costs nothing extra, which keeps this card from becoming a corruption-stacking trap. No interaction with slice sizes or tick quality.

4. **Data**: against the current .tres, change `amount = 1` to `2`, `id = &"bug_plus"`, `display_name`, and `description`. Keep `offered = false`. No new effect is needed for the card itself. The trigger that turns Bug into Bug+ would be NEW: Bug decay hook (no N# fits). Without it, the card cannot be reached, so the data-only fallback is to skip the + version entirely.

5. **Q:**
   - Do we want a Bug+ at all, or is "Bug has no upgrade" the right ruling for the whole penalty-card family?
   - If we do build Bug+, what escalates Bug to Bug+: a Heat threshold, an enemy listener (N6), or a parasite effect (N10)?
