<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01KoA2oC9t6Dcg9He9GEZh6r, custom_id station__hivemind; status ok; tokens in 3988 cache-write 0 cache-read 32585 out 2085; cost $0.018. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# station: hivemind

## 1. Current
The Hivemind file is a copy of Botnet's station bonus: a `ON_RAID_START` trigger firing `DEPLOY_DRONE` amount 1 (type 18), which spawns one free turret per raid. It is meaningful for Botnet. For the Hivemind it is neither unique nor distinct: the same bonus appears on two classes, which breaks G8. Rank only scales `station_bonus_multiplier`, which the effect doesn't read.

## 2. Proposed station bonus: "Swarm Garrison"
**Concept:** The Botnet's drones fight and then are gone. The Hivemind's swarm never leaves, so a stationed Hivemind leaves a *standing swarm* on the node: a permanent mesh of drones that wears down every threat passing through, and that persists between raids.

**Raid terms:** A node with a stationed Hivemind gets **Swarm Mesh** (the node's built-in defense; it doesn't occupy asset slots). On every raid step, the Mesh deals damage to **each** threat that is on the node or one hop away (a chip, not a focused shot). It cannot be redirected, and it can't kill a threat alone at low Rank; it shaves a wide group.

| Rank | Multiplier | Mesh damage per threat per step | Reach |
|---|---|---|---|
| 0 | 1.0 | 1 | on the node |
| 1 | 1.25 | 1 | on the node, +1 hop |
| 2 | 1.5 | 2 | on the node, +1 hop |
| 3 | 2.0 | 2 | on the node, +2 hops |

Damage is flat: 1 × the Rank-0 base, rounded down, with the table above authoritative (the multiplier is read for reach and damage thresholds). Mesh damage is spread-based: Rank 3 can hit up to ~6 threats per step, so it is strongest against wide, multi-vehicle raids and weakest against a single heavy threat.

**Persistence (the "never leaves" part):** the Mesh isn't consumed. If the node goes DOWN, the Mesh goes silent until the node is repaired (no extra cost). If the node is TAKEN, the operative returns to the reserves (existing rule).

**Non-raid terms:** none; a Hivemind that is stationed doesn't run. Optionally a drone-count carry bonus: the next netrun the operative starts with +1 drone docked (see Q).

**Grid view:** the node gets a faint hex-mesh halo whose radius equals the reach (1 or 2 hops, drawn as a dotted ring), and a small drone-swarm glyph on the node badge with the per-step damage as a number. During a raid playout, each Mesh tick draws thin pulses to each threat in reach, so the player sees "wide chip" at a glance. The setup phase's projection counts the Mesh damage per step (deterministic, preview equals result).

## 3. Family
Botnet is the base; Hivemind is its alternate: both leave drones on the node, but Botnet gives a **single placed turret each raid** (a focused, repositionable asset), whereas Hivemind gives a **permanent, area, unfocused chip**.

| Class | Bonus | Feel |
|---|---|---|
| Botnet (base) | One free turret asset per raid (redeployed by `ON_RAID_START`), turret damage scaled by Rank | focused, placed |
| Hivemind | Swarm Mesh: permanent area chip, 1-2 damage, 0-2 hops | wide, persistent |

The other families keep their own differentiated pairs (Breaker asset damage, Ghost freeze, Rigger node heal), and I propose nothing for them here.

## 4. Fit with the defense trio and the other classes
- **Trio:** Raids don't use BLOCK, SHIELD or SANDBOX, so the Mesh is a pure damage source. It does not give any node a shield or evasion. Conceptually it works on the offense side of the trio, leaving defenses to Rigger (heal) and Ghost (delay).
- **Uniqueness:** Breaker boosts asset damage (Breaker +50 %). The Mesh stacks with the Breaker only by damaging separately: asset damage is not touched. Ghost delays threats, which makes more steps in range for the Mesh: this is a good synergy, but bounded, because both need different nodes (one station slot per Safehouse).
- **Dominant stacking:** Mesh damage is capped at 2 per threat per step per node. Two overlapping Mesh nodes would add; I propose a rule that overlapping Meshes **do not stack: the highest applies** to a given threat per step. With 30 steps the Mesh's maximum is 60 damage per threat, which is useful against T1-T2 threats but doesn't remove heavy threats alone.

## 5. Data
- `TriggeredEffectData` on a new trigger: `ON_RAID_STEP` (a new trigger, raid-side; **NEW: raid-step trigger**) or, as a data-only fallback, a built-in node defense field.
- `EffectData`: a new effect type `AREA_CHIP` with fields `amount`, `reach_hops`, `per_threat` (**NEW: area chip node defense, size M**). Rank values come from a per-Rank table in `RankRewardData` (`station_bonus_multiplier` alone is not enough).
- Fallback (data-only, size S): reuse the turret asset with a low-damage, range-2 `AssetData` `swarm_mesh.tres` deployed free at `ON_RAID_START` and made permanent through `station_deploy_asset` (no area hit, a single target). It loses the "wide" identity, so it is only a stopgap.
- Grid view: halo and badge are UI work (**S**).

## 6. Q:
- Should the Mesh's persistence also apply when the operative is *not* stationed, as a node upgrade the player buys later?
- Is a flat 1-2 damage per threat per step significant enough compared with the raid threat HP scale, pending the raid sim?
- Should Rank 3 add a netrun-side benefit (a starting drone), or does stationing stay raid-only?
