<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__undock; status ok; tokens in 5121 cache-write 0 cache-read 32585 out 1131; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: undock

1. **Role:** Neutral utility that repositions a satellite (docked mini-wheel) so it covers or uncovers a slice. Under R12 it becomes one of the few ways to move a fixed satellite, so it is a niche tech card, not a staple.

2. **Upgraded card: Undock+** (one level only; the card is too narrow to need more)
- RAM cost: 1 (unchanged).
- Cycle cost multiplier: ×1.25 (55 → 69). The wider reach is worth a little more.
- Text: "Move a satellite up to 2 slices, either direction. If the destination holds a satellite, swap them instead of replacing."
- Effects (one CUSTOM effect, same handler):
  - type CUSTOM (24), target CHOSEN (the satellite is picked by the player), custom_handler `undock_handler.gd`.
  - Handler parameters: `max_steps` 2 (was 1) and `on_occupied` SWAP (was REPLACE under R12, which would destroy a satellite).
  - Direction: either way, as today.
- Exhaust: false. wheel_target: SATELLITE (3), unchanged.
- Sidegrade, not a strict upgrade: the card still moves one satellite once, and its cost stays 1 RAM. Swap is the safe answer to R12 replacement, and it also lets the player shift an enemy satellite onto a slice the pointer will read. Reach 2 is only slightly more useful than 1 on a 6-slice wheel, so the card gains flexibility and not raw power.

3. **Interplay:**
- R12 makes satellites fixed, so this card is a rule exception. The + version is deliberately still a one-use, 1-RAM move, which keeps it from competing with the operative class that can move satellites for free.
- Variable slice sizes (R11): "slice" steps count slots, not ticks. The satellite keeps its slot index and lands on the destination slot whatever its size_ticks. A satellite on a 2-tick slice is easy to dodge, and moving it to a 7-tick slice makes it a wide bodyguard. The preview must show the new guard coverage.
- Replacement (R12) in a Meridian or Orbital fight can destroy an enemy satellite via REPLACE. The + version's swap never destroys one, so it is a repositioning tool only.

4. **Data:**
- `undock.tres`: `cycle_cost` 55 → 69; description string.
- The handler gains exported or passed fields `max_steps` (int) and `on_occupied` (enum REPLACE/SWAP), read from the effect (reuse `EffectData.amount` = steps and `multiplier` unused, to stay data-only). With no new fields on EffectData, the pairing is `amount` = 2 and a SWAP flag in the handler variant.
- New system: N13 (fixed satellites + `on_occupied`). Fallback: a second handler script `undock_plus_handler.gd` with the values hardcoded, which needs no schema change.
- Needs a distinct id `undock_plus` if upgrades are stored as separate resources.

5. **Q:**
- Q: Does a swapped satellite count as moved for Daemon and Firmware triggers (`can_move_satellites`)?
- Q: Should SWAP be the base card's behavior too, once REPLACE can destroy a player's own drone?
