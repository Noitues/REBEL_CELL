<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_018qf9qUPrCq1xu3cv9eEHKg, custom_id cardup__arc_flash; status ok; tokens in 5112 cache-write 32585 cache-read 0 out 1228; cost $0.052. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# card_upgrades: arc_flash

1. **Role.** Neutral reward-pool AoE: a small sweep that chips every enemy at once. It is weak 1v1 and strong against multi-body fights such as satellites, drones and multi-enemy nodes.

2. **Upgraded card: Arc Flash+** (one level only; no further tiers needed).
   - RAM cost: 2 (unchanged).
   - Cycle cost multiplier: ×1.4 (65 → 91).
   - Text: "Deal 4 damage to every enemy. Apply 1 OUTPUT_DOWN to the slice under each enemy's pointer."
   - Effects:
     1. DEAL_DAMAGE, target ALL_ENEMIES, amount 4, FLAT (damage is the player's, so no tier scaling).
     2. APPLY_STATUS, target ALL_ENEMIES, slice_pick UNDER_POINTER, status OUTPUT_DOWN, 1 stack (equivalent to PARASITE until N8/N9 land), duration 0.
   - Exhaust: false. wheel_target: ENEMY (1 → stays 1 as currently set).
   - Justification: +1 damage is a modest bigger-number change. The rider is the sharpening: it turns a chip into "hit all and weaken what each is about to do", which keeps it a sweep card. It is not a sidegrade at the cost point, because RAM is unchanged, but it is not strict dominance either, since it costs 40 % more Cycles. A pure damage +2 would be the alternative, but it would make the card a better Static Shock rather than a better Arc Flash.
   - Preview: the rider hits the slice currently under each pointer, so the preview equals the result. It is applied after the damage and does not depend on the damage.

3. **Interplay.**
   - Statuses are anti-firmware (R8). OUTPUT_DOWN −25 % per stack on an enemy's current slice is a real defence on a single resolve, and it is strongest against a one-needle enemy's big hit.
   - Phase parking (R3): the 4 damage still parks at a threshold. The status survives phase changes (R6), but is remapped by centre tick. Enemies with ENCRYPTED on that slice absorb the rider and still take the damage.
   - Satellites: the sweep hits satellites too, and the status lands on each satellite's slice.

4. **Data.**
   - Change fx0 amount from 3 to 4.
   - Add fx1 (APPLY_STATUS, target 4 = ALL_ENEMIES, slice_pick 0, status 4 = PARASITE as stand-in; OUTPUT_DOWN ×1 once N8/N9 exist).
   - Update description and cycle_cost 65 → 91.
   - Dependency: APPLY_STATUS on ALL_ENEMIES with UNDER_POINTER must iterate over every enemy's pointer (per-pointer on multi-needle enemies). Small change in `effect_interpreter`, no new N#.
   - Fallback: a data-only version with the PARASITE stand-in (half output, strong) is too strong at 2 RAM. Before N9, ship the damage-only upgrade (4 damage, RAM 2, Cycles ×1.2) and add the rider later.

5. **Q:**
   - Q: On multi-needle enemies, should the rider hit every needle's slice or only the primary needle's? (I lean every needle, to match the pointer rule.)
   - Q: Should the rider's stack count be capped on bosses with OUTPUT_DOWN immunity-style buffs, or is Compliance Lock enough?
