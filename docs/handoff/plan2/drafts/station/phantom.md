<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01KoA2oC9t6Dcg9He9GEZh6r, custom_id station__phantom; status ok; tokens in 4029 cache-write 0 cache-read 32585 out 2299; cost $0.019. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# station: phantom

## 1. Current
Phantom's station bonus is a copy of Ghost's: at ON_RAID_START (trigger 12), `type = 9` (FREEZE) holds threats 1 step. Rank scales it only through `station_bonus_multiplier`. It is meaningful for Ghost, but for Phantom it is **not unique**, because it is the identical effect. The Phantom identity is dodging (Detour, SANDBOX under R13), which the bonus never touches.

## 2. Proposed station bonus: "Decoy Echo" (SANDBOX on the node)
**Concept:** Ghost delays threats before they arrive. Phantom makes the node *untouchable once*: the first hit it takes is negated whole.

**Raid terms:**
- **Trigger:** ON_RAID_START, then re-armed on a cooldown.
- **Effect:** the node gains a SANDBOX charge (R13 semantics). It negates one whole damage event, meaning every hit of one threat's attack in one step. It ignores threat damage amount.
- **Pierce rule:** threat pierce does not bypass SANDBOX.
- **Re-arm:** after the charge is spent, it re-arms after N steps. The raid runs 30 steps, so this stays bounded.
- **Deterministic:** the charge goes to the first damage event in step order (threat index order), and the preview shows it.

| Rank | Charges at raid start | Re-arm after spend | Multiplier shown |
|---|---|---|---|
| 0 | 1 | none | 1.0 |
| 1 | 1 | 12 steps | 1.25 |
| 2 | 1 | 9 steps | 1.5 |
| 3 | 2 (max stored 2) | 8 steps | 2.0 |

At Rank 3 that is up to 2 at start plus about 3 re-arms across 30 steps, so at most ~5 negated hits per raid. This is far less than a wall of integrity, because it absorbs one event whether the hit is 3 or 30. Its value therefore rises with threat strength, which suits Heat-scaled raids.

**Non-raid terms:** while stationed, the operative gives the next netrun that departs from the node's Site a starting SANDBOX charge in the first combat. This is a small echo of the same theme. It is optional, and the raid half ships without it.

**Reads on the grid view:** a small ghost-outline ring around the node icon (one ring per charge). Spending a charge plays the ring shattering in the raid playout. The setup-phase projection shows "SANDBOX ×n" and the projected outcome with the charge consumed on the first hit.

## 3. Family
Ghost's identity is time, slipping and stripping. Phantom keeps the "avoid" fantasy but swaps delay for negation.

| Class | Relation | Bonus |
|---|---|---|
| **ghost** (base) | Delay: threats entering the node are held 1 / 1 / 2 / 2 steps (current FREEZE) | Time |
| **phantom** (alt) | Same stationed-guardian feel, but negation instead of delay: SANDBOX charges on the node | Negation |

Phantom is Ghost's bonus converted from "later" to "not at all". Ghost wins vs many weak threats (long delay pushes them past the 30-step limit). Phantom wins vs one big hit.

## 4. Fit with the defense trio and the other classes
- **Trio:** Ghost's delay is not defense in the trio. Phantom takes SANDBOX. The existing bonuses already map as follows:
  - Rigger: node integrity regen, which is the BLOCK/HP-like role.
  - Botnet: free turret.
  - Breaker: asset damage +50 %.
  - Phantom is the only SANDBOX bonus. A node SHIELD (lingering, capped, 15) is left open for a future class or alternate, such as Hivemind or Wrecker, if the designer wants one.
- **No duplicates:** FREEZE (Ghost), integrity regen (Rigger), turret (Botnet), asset damage (Breaker), SANDBOX charge (Phantom). Alternates for the other three must stay distinct from these.
- **Dominant stacking:** if every class is stationed, Phantom's charges stack with Rigger regen and Ghost delay. The stacking is mild because:
  - The charge is per-node, and a node has one Safehouse slot, so one operative per node. Adjacency sharing (Firewall Relay next to a Safehouse) shares at most 1 charge, not Rank 3's 2. Cap shared charges at **1** for adjacent nodes.
  - Re-arm is slow.
  - The charge is the first hit only, so a second wave needs the re-arm.
  - Against the R4 Heat-scaled second wave, the charge re-arm outpaces the cooldown only at Rank 3. That is the intended reward for investing.

## 5. Data
- **Current:** `te_station` = TriggeredEffectData (trigger 12 ON_RAID_START) with EffectData `type = 9`, `amount = 1`.
- **Needed, raid half:**
  - A new `EffectType`, e.g. GRANT_NODE_EVADE (CUSTOM can carry it as a fallback), with `amount` = charges.
  - A re-arm field, e.g. `EffectData.cooldown_steps`.
  - Raid-resolution support: a per-node `sandbox_charges` counter in the raid sim, consumed on the first damage event, with the preview matching. NEW: node sandbox charge in the raid sim. Size S–M. It is part of the raid design pass, since N14 covers only the combat SANDBOX.
- **Rank scaling:** the existing `station_bonus_multiplier` cannot scale counts and cooldowns cleanly. Use a per-rank table on `RankRewardData`: `station_charges`, `station_rearm_steps` (NEW fields, S, data-only once the handler exists).
- **Non-raid half:** `next_combat_overrides` (N16) is the hook. Defer.
- **Fallback with no code:** keep the FREEZE effect and change only the number (Phantom 0.5 steps is not possible). So a pure data fallback does not exist, and the bonus stays a duplicate until the raid handler lands.

## 6. Q:
- Q: Should a SANDBOX charge on a node negate *one threat's whole step* or *one damage event per threat per step*? (Draft assumes the whole step's damage from one threat.)
- Q: Should Phantom's non-raid half (a starting SANDBOX in the next netrun) ship together with the raid half, or wait for N16?
- Q: Is a node SHIELD-type bonus wanted for another alternate (Hivemind or Wrecker) to complete the trio mapping?
