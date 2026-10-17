<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__armor_plate; status ok; tokens in 5185 cache-write 0 cache-read 32585 out 1312; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: armor_plate

1. **Role:** A neutral two-for-one defensive utility. It protects one slice from the next status (ENCRYPTED) and adds a small BLOCK buffer. It suits a deck that is mostly slices and not much hand.

2. **Upgraded card: "Armor Plate+"** (one level only; a second would add nothing here).
- RAM cost: 2 (unchanged).
- Cycle cost multiplier: ×1.5 (60 → 90).
- Text: "ENCRYPT a chosen slice and gain 6 block. If that slice is already ENCRYPTED, gain 4 more block."
- wheel_target: OWN (0). Exhaust: false.
- Effects:
  - fx0: APPLY_STATUS, target OWN_WHEEL, status ENCRYPTED, slice_pick CHOSEN. Unchanged.
  - fx1: GAIN_BLOCK, target SELF, amount 6, amount_mode FLAT (N1; plain `amount` works without it).
  - fx2 (rider): GAIN_BLOCK, target SELF, amount 4, FLAT, conditional "chosen slice was already ENCRYPTED before fx0" (condition field: NEW, see 4).

**Why the sidegrade:** the base block goes up 50%. The rider rewards stacking Plate on an already-encrypted slice, which includes a Hardened Firmware slice that is permanently ENCRYPTED. Plate then pays out 10 block instead of acting as a dead ENCRYPT. It does not dominate at every point: the rider does nothing on a bare slice, so a plain Plate+ is just +2 block for +30 Cycles. Cheaper alternatives such as Firewall (1 RAM, 6 block) still compete on RAM efficiency. Block is temporary and has no cap, so the 10-block case is the ceiling and stays modest next to Bulwark's 12 for 2 RAM.

3. **Interplay:**
- **Statuses as anti-Firmware (R8) and parasite latches:** ENCRYPTED absorbs one status. Plate+ keeps its defensive value against ×N OUTPUT_DOWN, TIER_DOWN and CORRUPTED, and its block is a small buffer against bosses that apply them while hitting. Whether ENCRYPTED also absorbs a Parasite ring latch is undecided; I assume it does not, since parasites are slices and not statuses.
- **Corruption as a RAM debuff (R9):** a CORRUPTED slice cannot be ENCRYPTED if the slot is "full". I assume ENCRYPT can still be applied to a CORRUPTED slice, so it protects against Genome Core Immunization re-corruption only in the sense of absorbing the next status.
- **Variable slice sizes (R11):** no interaction.

4. **Data:**
- Changes to `armor_plate.tres`: `display_name`, `description`, `cycle_cost` 90, `fx1.amount` 6, and a new `fx2`. Ship as a separate `armor_plate_plus.tres` and give the base card an upgrade link (field NEW: `upgrade_id`, part of the card-upgrade pass).
- Needs NEW: `EffectData.condition` (an enum such as SLICE_ALREADY_STATUS) and an evaluation that reads the pre-apply state. This is deterministic and previewable.
- **Fallback with no new system:** drop the rider and make fx1 GAIN_BLOCK 8 (a pure number upgrade). It is weaker, but data-only.
- N1 amount modes are not required.

5. **Q:**
- Q: Should the + version use a conditional rider (needs a new `condition` field), or take the data-only +4 block fallback?
- Q: Does ENCRYPTED absorb Parasite ring latches, or only statuses?
