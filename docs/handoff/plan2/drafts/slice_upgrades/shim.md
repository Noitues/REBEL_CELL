<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01Y2bjt88e8i6ocTDPQPm21s, custom_id slup__shim; status ok; tokens in 15053 cache-write 32585 cache-read 0 out 2726; cost $0.069. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# slice_upgrades: SHIM

## 1. Role of the type
SHIM is the reliable single-target hit and the class staple (Breaker has 3, Ghost 2). It is the slice that rewards precision on a Perfect or Good landing and the one that funds Perfect hooks. Today's 10 plain values (3–20) are an enemy-tuning ladder, not a player progression.

- **Redundant as player upgrades:** shim_3/4/6/7/8/9/10/12/14/16/20 are all one slice at different numbers. These become **Level data**, not 11 separate pool entries.
- **Keep as distinct variants:** shim_7_drain (RAM-drain rider) and shim_8_weight (resistance rider) stay as enemy slices. They are not on the player upgrade path.
- **Player SHIM line:** the base `shim_8` ladders through Levels I–IV. Level IV branches into two forms, so the end point is a choice.

## 2. Level table (output is FLAT; a PERCENT mode does not suit damage)

| Level | Size | Tick pattern | Output | Extra | Price |
|---|---|---|---|---|---|
| I | 5 | W G P G W | 8 | none | base |
| II-a **Broad** | 6 | W W G G W W | 9 | none | no Perfect, wide landing zone |
| II-b **Keen** | 4 | W G G W | 8 | none | no Perfect, tight, frees 1 tick |
| III-a **Heavy** | 5 | W G P G W | 12 | Perfect: ×1.5 | the same size as Level I; needs precision |
| III-b **Fine** | 3 | G P G | 10 | none | all ticks Good or better, but only 3 ticks of wheel |
| IV-a **Sniper** | 3 | G P G | 14 | Perfect: ×2 plus pierce | the smallest, almost never mandatory |
| IV-b **Volley** | 6 | W G P P G W | 10 | `hits` = 2 (each hit separately) | Perfect-wide, but WEAK halves both hits |

Reading the table:
- **No strict upgrade path.** Level II gives a choice between size and the hit window. Level III chooses between consistency (Fine) and a Perfect-based payoff (Heavy).
- Size is the budget. Fine and Sniper free 2 ticks for other slices, but the wheel spins and a small slice is hit rarely. Broad costs 1 tick of the budget in exchange for more WEAK landings.
- **Level IV is exciting**: Sniper is a precision win condition for the player who nudges well. Volley is a different shape, with `hits` and a wide Perfect zone, and works with Kernel Sync and Perfect-based hooks. The hit count is also what the pointer rule multiplies against multi-pointer bosses.
- **Mapping:** Level is a new `SliceData.level` plus an `upgrade_to: Array[SliceData]` list. Each Level is one `.tres` (`shim_l2a`, etc.). Existing fields cover `base_output` and `extra_effects`. The new fields are `size_ticks` (N12), `tick_quality` (N12), `level`, `upgrade_to`, and the rider fields `hits`, `perfect_multiplier`, `pierce` (N20).

## 3. Tick-quality interplay (R11)
- **The pattern is data, not computed.** A Level authors its own `tick_quality` where the default map for its size would not match (Volley's W G P P G W, Fine's G P G, which is the default 3-tick map).
- **Calibrated firmware** raises each sub-tick one tier. Effects: Keen reads G G G G (a 4-tick slice with no Perfect becomes G P P G), Broad's WWGGWW becomes WGPPGW. The chip is strongest on even sizes, which have no Perfect by default. Sniper and Fine gain nothing (already G P G, which becomes P P P, a mild gain). Chip value therefore varies by Level and creates a real socket decision.
- **PERFECT-only effects** (Heavy ×1.5, Sniper ×2, Kernel Sync, class hooks) favour 5-tick and 3-tick slices. Keen and Broad cannot reach Perfect without Calibrated. That is deliberate: they trade the hook for reliability.
- **Small slices are not mandatory.** Sniper and Fine give a high payoff for a small window, and a bigger slice such as Broad is always a viable fallback. A 1–2 tick SHIM is not offered at all; the minimum size for this type is 3, so no mandatory 2-tick GG slice appears.
- **Firmware interplay:** Overvolt (+25 %), Patch+ and Leech/Siphon keep working. Tracer needs a Perfect, so it fits Heavy and Sniper.

## 4. Rack flash (G15)
- **Offer:** 3 choices. Each choice is either UPGRADE (one of the player's slices to a next Level, chosen from its `upgrade_to` list) or SWAP (replace a slice with one from the pool). The player picks one choice or skips.
- **Shape of the 3:** 1 upgrade for a random owned slice, 1 upgrade for another, 1 swap. SHIM upgrades appear when the player owns a SHIM (weight proportional to the number owned), so Breaker sees it often.
- **Swap across types:** allowed. The offered slice is drawn from the class's pool at the same Level or lower. Swapping to a different type keeps its Level at I.
- **Rarity:** Level II offers are common, Level III uncommon and Level IV rare, and appear only on layer 7 Racks or at T3+. Layer 4 Racks offer Levels II and III.
- **Cost:** free as a reward. The Heat cost is the same as the Rack's.
- **Data:** a `slice_flash` row kind in the reward table (N18) with fields `choices`, `max_level_by_rack`, `allow_swap`. The roll uses the `rewards` RNG stream, so a reload cannot reroll it.

## 5. Economy
- **Shop (Mainframe):** the slice wheel sells slices at 100 / 80 / 100 Cycles (G14), and upgrades are a different row: Level II 60, Level III 120, Level IV not sold. Level IV comes only from a Rack flash or a Level III Workshop upgrade at a premium (200).
- **Workshop node (D4):** upgrades one slice by one Level for Cycles, with the choice of branch visible beforehand.
- **Firmware sockets:** the socket stays on the slot when a slice is upgraded. If the chip's allowed types or size make it invalid (Leech is SHIM-only; every Level stays SHIM, so it is fine), a confirm is shown. A swap to another type warns first and sends the chip to the recycle bin (G14 confirm).
- A downgrade is never offered. A respec exists only through a swap.

## 6. Systems & data
- **N12** (size_ticks, tick_quality): required for everything past Level I. **Fallback:** a data-only version with every Level at size 5, which keeps Heavy and Sniper (as 5-tick) and loses Broad, Keen, Fine and the whole size choice.
- **N20** (hits, perfect_multiplier, pierce): needed for Heavy, Sniper and Volley. Fallback: output-only levels.
- **N18** (the `slice_flash` row), **NEW: slice level fields** (`level`, `upgrade_to`, S), and a Workshop node (D4, M).
- Previews must show the level, the tick map and the expected output, and be deterministic.

Q: Should Level IV be reachable only through Racks, or also a Workshop at a high price?
Q: Is a minimum SHIM size of 3 right, or do you want a 2-tick GG SHIM as a Level IV gamble?
Q: Does a swap to another type keep any Level progress?
Q: Should flash offers be guaranteed to include at least one upgrade for the slice type the class is built around?
