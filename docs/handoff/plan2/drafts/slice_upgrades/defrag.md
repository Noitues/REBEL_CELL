<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01Y2bjt88e8i6ocTDPQPm21s, custom_id slup__defrag; status ok; tokens in 13732 cache-write 0 cache-read 32585 out 3002; cost $0.032. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# slice_upgrades: DEFRAG (BLOCK)

## 1. Role of the type
DEFRAG is the temporary defense: BLOCK that expires at the start of your next turn (R13). It is the cheap, reliable answer to a telegraphed hit. It is also the type that makes the wheel's quality pattern matter least, because it has no Perfect-only payoff today.

Today's content is a pure number ladder: defrag_2, 3, 4, 5, 6, 8, 12. All are 5-tick slices that differ only in `base_output`. They are redundant as separate "types". Upgrade levels replace the ladder, so each Level is one slice id with its own size and shape. Keep defrag_4 (L1), 6 (L2) and 12 (L4 base) as the anchors. Retire 2, 3, 5 and 8 from the player pool. They stay as enemy/legacy content.

Firmware overlap: `bulkhead` (+50%, DEFRAG and SANDBOX), `static_coat` (+2 SHIELD) and `barbed_wire` (+2 damage) already exist. Level effects must not duplicate them. Levels change shape, size and rules; the chips stay flat add-ons.

## 2. Level table
Output is placeholder BLOCK per landing at Good. Perfect and Good are 1.0x and WEAK is 0.5x (GDD 2.4).

| Level | Size | Tick quality | Output | Extra effect | Cost / trade-off |
|---|---|---|---|---|---|
| **I** (base) | 5 | W G P G W | FLAT 5 | none | the baseline |
| **II-a Wide** | 6 | W W G G W W | FLAT 7 | none | +1 tick, but no Perfect and 4 of 6 ticks are WEAK |
| **II-b Tight** | 4 | W G G W | FLAT 6 | none | -1 tick, no Perfect, steadier |
| **III-a Reactive** | 3 | G P G | FLAT 6 | Perfect: also +2 SHIELD | smallest body, no WEAK ticks, a Perfect is a 1-tick target |
| **III-b Bastion** | 6 | W W G G W W | PERCENT 12% max HP | none | scales with HP; weak on a low-HP class, strong on Breaker (60 HP = 7) |
| **IV Fortress** | 5 | W G P G W | PERCENT 15% (9 at 60 HP) | Perfect: carry 50% of unspent BLOCK into next turn | costs a full 5 ticks; the carry-over breaks the "expires" rule only on Perfect |
| **IV Phalanx (alt)** | 7 | W W G P G W W | PERCENT 10% | Perfect: BLOCK also applied ×1 to the next landing's slice | the largest footprint, built for slow wheels |

Why this is a choice and not a ladder:
- Level II splits into wider or tighter, trading Perfect access and WEAK exposure for output.
- Level III splits into a precision build (III-a) and a scaling build (III-b).
- Level IV is exciting because Fortress turns a Perfect into a banked defense, so a player who can nudge to Perfect gets a sustain engine while one who can't gets a plain 15%.
- Size is the budget: IV at 5 ticks costs the same as Level I but rewards the player's skill, while Phalanx spends 7 of 30 ticks.

**Field mapping:**
- Size: `size_ticks` on `WheelSlotData` (R11), so a Level is a slice id plus its slot size.
- Output: `base_output`, with `amount_mode` (N1) for the PERCENT variants.
- Effects: Reactive's SHIELD and Fortress's carry use `extra_effects` (existing trigger ON_PERFECT, effect GAIN_SHIELD).
- New fields: `level` (int, 1-4), `upgrades_to: Array[SliceData]` (the branches), `tick_quality` override (R11), and a `carry_pct` rider for Fortress (NEW: BLOCK carry-over rider, S, data-only fallback is a flat +4 SHIELD on Perfect).

## 3. Tick-quality interplay (R11)
- The shape is part of the Level. Upgrading to a branch changes the map, so the loadout screen shows the before/after maps in the preview.
- **Calibrated** raises each sub-tick one tier. It is strongest on the 4-tick Tight (W G G W becomes G P P G, which gives two Perfect ticks) and on Wide (W W G G W W becomes G G P P G G). It adds little on Reactive, which is already G P G (it becomes P P P).
- That makes Tight + Calibrated the premium pairing, but Tight has no Perfect effect to trigger at Level II. This is intended: the chip is what unlocks the value of the shape.
- PERFECT-only effects (Reactive, Fortress) pair with Calibrated naturally.
- To avoid pointless or mandatory sizes, no Level has size 1-2. The minimum is 3 (G P G). Size 3 pays with a Perfect bonus, so it is never a trap, and no single size is required for any content because enemies' BLOCK-ignoring pierce (R13) punishes mono-defense builds.

## 4. Rack flash (G15)
A Server Rack offers a **flash** with 3 choices drawn from the slices on the player's wheel:
- **Upgrade:** one slice goes up one Level (II-a or II-b, and so on). The player picks a branch where there are two.
- **Swap:** replace the slice with another pool slice of the *same type family* (BLOCK / SHIELD / SANDBOX), a different type only on a rare roll. Offer 3 candidates, Common 60% / Uncommon 30% / Rare 10%.
- **DEFRAG in offers:** Level I DEFRAG appears as a swap target on any wheel. Level II-III appear as upgrades of an owned DEFRAG. Level IV is offered only from a Level III DEFRAG, and only at layer-7 Racks.
- **Cost:** free at the Rack (the reward is the flash). The player sees both maps (size, tick pattern, output) before choosing, and the swap keeps the Firmware socket.
- **Reward table (N18):** row kind `slice_flash` with fields {choices: 3, rarity weights, allow_cross_type: chance, conditions: Rack layer 4 or 7}. Layer-4 Racks cap at Level III.

## 5. Economy
- **Shop (Mainframe) / Workshop:** upgrade a slice for Cycles: I→II 60, II→III 100, III→IV 160 (placeholders, ×0.8 at the Workshop, which specialises in this). Branch choice is made at purchase. The Workshop node is already ruled in (D4).
- **Events:** some give a free Level, which fits the N16/N17 event outcomes.
- **Firmware sockets:** the socket stays on the slot, not the slice, so Firmware survives an upgrade. Size changes can strand a chip that doesn't suit the new shape, so the preview warns when Calibrated or `bulkhead` would be mismatched. `bulkhead` (+50%) stacks multiplicatively with PERCENT output, which is the main balance risk at Level IV (15% × 1.5 = 22%), so cap total BLOCK per landing at 25% of max HP.
- A Level-down on swap is not allowed; swapping to a different slice resets that slot to Level I of the new slice.

## 6. Systems & data
| Need | N# | Size | Fallback |
|---|---|---|---|
| `size_ticks`, `tick_quality` | N12 | L | none; the Level shapes need it (data-only: all 5-tick, with only output and effects varying) |
| PERCENT BLOCK | N1 | S-M | use FLAT numbers scaled per class |
| `level`, `upgrades_to`, branch UI | NEW: slice upgrade | M | the shop swap-only |
| `slice_flash` row | N18 | M | none until the data-driven table exists |
| BLOCK carry-over rider | NEW: carry rider | S | a flat SHIELD on Perfect |
| Perfect riders | N20 | S-M | existing ON_PERFECT trigger |

- Q: Should a Level-IV carry-over be allowed to break the "BLOCK expires" rule, or be converted to SHIELD to keep the trio distinct?
- Q: Do Level II branches both exist at every Rack, or is only one offered at a time to keep the choice small?
- Q: Does the 25% BLOCK cap per landing apply to enemy BLOCK as well?
- Q: Should the retired defrag_2/3/5/8 stay in the shop pool as Level I swap targets with cheaper prices?
