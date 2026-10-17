<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01Y2bjt88e8i6ocTDPQPm21s, custom_id slup__null; status ok; tokens in 12865 cache-write 0 cache-read 32585 out 3183; cost $0.032. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# slice_upgrades: NULL

## 1. Role of the type
NULL is the "miss" slice: it does nothing, and it is the wheel's only dead space. Today it is a fixed 5-tick slice with `base_output = 0`. Its only value comes from the rest of the kit: recycler (+2 RAM when it resolves), Fault Tolerance (3 damage), Zero Day (a Perfect on NULL = 3× OVERFLOW), Stolen Intent, Cold Exit (finish without NULL resolving), and the Fortress steer-to-Null trick on the enemy side.

Variants: there is one slice file. Recycler is the only NULL-specific chip, and it is not redundant. The design question is whether a player wants a NULL at all. The answer should be **yes, a small one, as a deliberate utility slice**, not a penalty.

Choice: NULL stays the only slice that is "safe to be hit by" in the sense that nothing was wasted. Its upgrade path trades **size for utility**. A NULL that shrinks is a gift, because it leaves tick budget for real slices. This inverts the usual "bigger is better" rule, which makes it the scarcest-resource slice's most interesting case.

## 2. Level table
Wheel budget is 30 ticks. A 6-slice wheel with a 5-tick NULL spends 17 % of the ticks on nothing.

| Level | Size (ticks) | Quality pattern | Output | Extra effect | Cost / give-up |
|---|---|---|---|---|---|
| I (base) | 5 | W G P G W | 0 | none | The baseline dead slice |
| II "Idle Cycle" | 4 | W G G W (no Perfect) | 1 RAM FLAT, any tier | A landing refunds RAM, so it is a reliable pay-off | Loses Perfect, so Zero Day and NULL-Perfect hooks are dead |
| III "Pressure Valve" | 3 | G P G | Cleanse 1 of your slices (CHOSEN) | A Perfect also gives 3 SHIELD | The cleanse is a modest effect, and the slice is now real and worth hitting |
| IV "Dead Man's Slice" | 2 | G G | 2 RAM + 10 % max HP PERCENT heal on Good or better | The next hit that crosses it is negated once per combat, as an inline SANDBOX | The slice is tiny, so it is almost never hit, and the effect is sparse. Pays off when it lands. |

Two parallel branches at Level III (a choice, not a ladder):
- **III-a Pressure Valve** (above, 3 ticks, utility).
- **III-b "Hot Null"** (4 ticks, W G G W): output 0, but a landing triggers 4 damage to the pointer target and 1 Heat. This is the Fault Tolerance fantasy on the slice itself, and it costs Heat. Level IV from III-b is "Dead Man's Slice" with the damage added.

Why it is a real choice, not a strict upgrade:
- Smaller slices free ticks that can be given to a real slice, but a small slice is a harder landing target. A NULL that is both small and good is rarely hit, so its benefit is mostly the freed ticks.
- II drops Perfect, which kills the Zero Day and NULL-Perfect hooks, so it is an anti-synergy for a Zero Day build.
- Recycler stays best at I or II (cheap landings, frequent).

Level IV is exciting because the player has built a wheel where the dead slice is an ace: a 2-tick slice means 28 ticks of real slices, and the little slice is a panic button.

**Mapping to existing fields:**
- Size: new `size_ticks` on `WheelSlotData` (R11; N12). Level sets the default.
- `base_output`: 0 remains for NULL. The RAM and heal values go in `extra_effects` (GAIN_RAM, HEAL with `amount_mode`, CLEANSE, EVADE).
- Each Level is a separate `SliceData` file (`null_l2.tres`, ...), with a new field `upgrade_level: int` and `upgrades_to: Array[SliceData]` (the branch list).
- The 2-tick Level IV must have an authored `tick_quality` (G G), which the R11 default map already gives.

## 3. Tick-quality interplay (R11)
- **Calibrated** (every sub-tick one tier up): a Level II 4-tick W G G W becomes G P P G, so Idle Cycle gains a Perfect, and Zero Day works again. This is a strong chip on a small NULL and is a good, cheap way to un-kill the Perfect.
- A Level IV 2-tick G G becomes P P with Calibrated, so it is guaranteed Perfect: Zero Day (3× OVERFLOW on a Perfect NULL) fires on **every** landing. This is the headline combo, and it is exciting but not mandatory, because the slice is hit only 2/30 of the time.
- Size 1 is not offered: a 1-tick slice would be a lottery rather than a slice, and we avoid size 1-2 being mandatory. Size 2 only exists at Level IV, and its power is conditional.
- Level III-a uses a 3-tick G P G: a tight Perfect, while any landing is Good or better, a safe small slice.
- Perfect-only effects (Zero Day, Perfect hooks): Level I and III keep a Perfect, and II and IV rely on Calibrated or a nudge to reach one. Rule: a Level's text must state "any tier" or "Perfect only". Level IV has no Perfect-only text, so it is never dead.
- Nobody is forced to shrink NULL: Level I at 5 ticks is still the best Zero Day and Fault Tolerance catcher, since it is the largest target.

## 4. Rack flash (G15)
- **Offer:** a Rack flash for NULL gives **2 choices**: (a) upgrade this NULL by one Level (or choose the branch at III), or (b) swap it for another slice from the pool.
- A NULL is flagged in the flash screen as a **"free upgrade"**: upgrading never costs Cycles, because NULL is the slice the player never wants to spend on.
- **Swap pool:** 3 slices shown, one from any type (rare weighting), one common attack, one defense; the swap may change type. Swapping NULL for a real slice keeps its size if it fits, otherwise the pool slice's default size, and the wheel total is re-balanced by the player (a fix-up step if the sum ≠ 30).
- **Rarity:** Level II common, III uncommon, IV rare; III-b "Hot Null" uncommon.
- **How NULL appears:** weight it low in flash offers (the player has one, and a shrink is a quiet reward), but guarantee a NULL option when it is the player's only slice of size ≥ 4, because shrinking it is the cheapest way to free ticks.
- **Reward-table row (N18):** `kind = slice_flash`, `pool = slice_upgrades`, `count = 2`, `conditions: node_type = Rack`, plus a `chance` modifier on Rack layer 7.

## 5. Economy
- **Shop / Workshop:** an upgrade can be bought as a service. Placeholder prices: Level I → II 40 Cycles, II → III 80, III → IV 140. These are cheaper than a real slice's upgrade, because NULL's upgrade is a trade-off rather than a power spike.
- **Workshop node (D4):** a "Resize" service moves ticks between two slices, which pairs with NULL shrinking. The cost is 20 Cycles per tick.
- **Firmware sockets:** NULL has one socket, as every slot does. Recycler is the natural chip; Calibrated is the strong one. An upgrade **keeps** the socketed chip, but chips with an `allowed_types` restriction must still match the type. The upgrade never changes type, so the chip stays valid.
- **Swapping to another type** (flash b) shows a confirm if a chip would be destroyed (the G14 confirm), and the chip is returned to the inventory rather than destroyed when the new type is not allowed.

## 6. Systems & data
- N12 (variable slice sizes, `size_ticks`, `tick_quality`), required. No data-only fallback for sizes other than 5; a Level I/II/III-a pass without N12 is impossible, since only Level I is 5 ticks. A fallback is "upgrades without size change" (all at 5 ticks), which loses the core trade.
- N1 (amount modes) for the PERCENT heal.
- N14 (SANDBOX negate) for the Level IV inline effect.
- N18 (reward table row `slice_flash`), M.
- NEW: `upgrade_level` and `upgrades_to` fields on `SliceData`, plus a per-slice `upgrade_cost` (S). Save version unchanged if the level is derived from the slice id.

Q: Should NULL's Level IV negate be once per combat (proposed) or once per turn, given the tiny landing chance?
Q: Is "free upgrade" for NULL acceptable, or must it cost Cycles to keep the shop economy consistent?
Q: Should a swap that breaks the 30-tick sum auto-resize the neighbours, or force a manual fix-up?
Q: Is Hot Null's Heat cost too punishing at Level IV, given Heat drives raids?
