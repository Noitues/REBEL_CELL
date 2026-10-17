<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01Y2bjt88e8i6ocTDPQPm21s, custom_id slup__detour; status ok; tokens in 13108 cache-write 0 cache-read 32585 out 2930; cost $0.031. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# slice_upgrades: DETOUR

## 1. Role of the type
DETOUR (R13 display name SANDBOX, "negates one whole attack: every hit of one resolution") is the panic button and the anti-multihit answer. It is the only defense that beats an enemy's many-hit slices (Genome Core IV, multi-pointer bosses). Pierce does not bypass it.

Today's content:
- `detour_1`, `detour_2`: identical except base_output (1 vs 2). Output is meaningless under the new rule, since it negates a whole attack, so this is **redundant**. Merge into one `detour` family; output becomes a different axis (see below).
- `counterstrike` chip (+4 damage to pointer target) is the only variant. It stays as a chip, not a level.

Design question for the type: what does a slice that either works or doesn't scale with? It scales with **coverage** (how many attacks and what else it does), not magnitude. Because it is binary, size matters more than for any other type: a 5-tick slice with a Perfect cannot be "better" at negating, so quality pays out in riders.

## 2. Level table
Quality tick strings per R11. Output column: DETOUR's base_output becomes the **negation count** (attacks negated per resolution) at Level III+. Below that it stays "1 whole attack" and base_output is the rider amount.

| Level | Size | Pattern | Negates | Extra effect | Cost / trade-off |
|---|---|---|---|---|---|
| I (base) | 4 | W G G W (no Perfect) | 1 attack (the first resolving at you) | none | Compact; no Perfect hooks (Breaker's Perfect hook can't fire here). Cheap on ticks. |
| II **Wide** | 6 | W W G G W W | 1 attack | WEAK landing still negates but only *hits of ≤ 50% max HP* (a WEAK DETOUR fails vs big hits) | Bigger, easier to land, but 2 of 6 ticks are unreliable and it eats 20% of the wheel. |
| II **Sharp** (branch) | 3 | G P G | 1 attack | On Perfect: restore 1 RAM per attack negated | Tiny and precise; needs a nudge to land, wins economy. |
| III | 5 | W G P G W | 1 attack; **Perfect negates 2** (the two largest attacks) | Reflect: 15% of the negated damage dealt back (PERCENT) | Standard 5-tick; benefit gated behind precision. |
| IV **Event Horizon** | 4 | G P P G (a 4-tick slice with Calibrated-style ticks built in) | **2 attacks always; 3 on Perfect** | Negated attacks' damage is dealt back at 40% to the attackers; the slice is **ENCRYPTED** | Costs: Level IV fixed at 4 ticks (can't be grown); the player gives up the Wide/Sharp branch and Firmware socket is locked to DETOUR-compatible chips only; after resolving, the slice becomes inert next turn (cooldown 1 turn) so it is a timing bet, not a permanent wall. |

Choice structure: I → II is a fork (Wide for reliability, Sharp for economy), both converge to III, and IV is a commitment (4 ticks, cooldown). Level II branches are lateral, not strict upgrades: Wide trades quality for size, Sharp trades size for precision.

**Field mapping** (existing): `base_output` = rider amount (RAM refund, reflect %); size via `WheelSlotData.size_ticks` (N12). `extra_effects` carry RAM refund, reflect and ENCRYPTED. **New fields on SliceData:** `level` (int 1-4), `branch` (StringName), `negate_count` (int), `negate_count_perfect` (int), `min_tier_to_negate` (enum), `cooldown_turns` (int), `upgrades_to` (Array[SliceData]), `tick_quality` override (R11). Amount mode PERCENT for the reflect rider.

## 3. Tick-quality interplay (R11)
- Level I's pattern has no Perfect on purpose: DETOUR is the least precision-gated slice, so a PERFECT-free base is a feature. A size 1-2 slice is not offered: 3 is the floor (Sharp) so it remains a real choice rather than a trap, and no level requires a size <3 or >6.
- **Calibrated chip** on Level I (W G G W → G P P G) gives it Perfect ticks, making its Level IV pattern reachable as a chip instead of an upgrade. It is intentionally weaker than IV: it grants the pattern but not the negate count. On Sharp (3 ticks G P G → P P P) it makes every landing Perfect, an exciting combo that makes RAM refund reliable.
- Perfect-only effects (Perfect negate 2 / reflect) are only meaningful on sizes ≥3 with a P tick. Wide II's mid-quality pattern is a deliberate dead zone for Perfect hooks, trading it for low risk.
- Under TIER_DOWN (R8) a Perfect landing reads Good: Sharp suffers most, so Encrypt/Cleanse become relevant to it.

## 4. Rack flash (G15)
Offer **3 choices** (rarity-weighted via the `slice_flash` row, N18), always including at least one lateral option for the slice picked:
1. **Upgrade** one chosen DETOUR by one Level (II shows both branches; the player picks).
2. **Swap** to another type from the pool. The swap can change type (DETOUR → DEFRAG, SANDBOX…), always producing a Level I of the new type, size preserved or chosen between the old size and the new type's default.
3. **Rarity flash** (rare, only at Level III→IV): "Event Horizon" offered at a discount of its Cycles price.

Flash offers DETOUR when the operative's wheel has ≥1 DETOUR and the corporation's boss has multi-hit slices (conditions in the N18 row: `has_slice_type = DETOUR`, `layer >= 4`, `is_rack`). If no DETOUR is on the wheel, a "swap in a Level I DETOUR" option still appears at low weight (10%) so the type stays discoverable. Cost: free at a Rack, replacing one Rack reward pick.

## 5. Economy
- **Workshop node (D4):** upgrade a slice one Level for Cycles (placeholders: I→II 60, II→III 100, III→IV 160; Wide/Sharp same price). Reroll the branch for 40.
- **Shop wheel (G14):** the shop wheel sells Level I and II slices at 100 / 80 / 100; Level III/IV appear only via Workshop or Rack.
- **Firmware sockets:** one per slice; upgrading keeps Firmware if its allowed-types still match, otherwise it pops out into inventory (confirm dialog, extending the G14 confirm). `counterstrike` stays valid on every DETOUR level. At Level IV, reflect stacks additively with `counterstrike` (4 flat + 40%); that is the intended build payoff. Sizes that shrink (III→IV) are shown on the loadout screen with the new sub-tick map.

## 6. Systems & data
- **N12** variable slice sizes + `tick_quality` (L): required; **no fallback** for 3/4/6-tick levels; with 5-tick only, Wide and Sharp collapse.
- **N14** defense trio: negate whole resolution (S–M): required for the base rule. 
- **N18** reward table row `slice_flash` (M); **NEW: slice_upgrade_data** (level graph `upgrades_to`, price, branch; M, data-only fallback: separate `.tres` per level linked by `upgrades_to`).
- **NEW: slice cooldown** (`cooldown_turns`, S) with a data-only fallback of an ENCRYPTED-then-CORRUPTED rider (approximation).
- N20 `negate_count` rider (S–M, extends N14). N1 for the PERCENT reflect (S).
- Content: retire `detour_2`, rewrite `detour_1` as Level I; add 5 `.tres`.

Q: Should negate_count be ordered (the first N attacks) or "the N largest"? The latter needs a preview ordering rule.
Q: Is the Level IV cooldown too punishing against the enrage timer, or does Event Horizon need a different cost?
Q: Does a swap in a flash reset the Firmware socket, or only warn?
Q: Should reflect damage count as Perfect-based for Kernel Sync-type Daemons?
