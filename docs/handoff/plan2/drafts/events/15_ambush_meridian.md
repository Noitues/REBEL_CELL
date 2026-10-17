<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__15_ambush_meridian; status ok; tokens in 6418 cache-write 0 cache-read 32007 out 2109; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_mer_exclusive_carrier: Exclusive Carrier Clause

**Mechanic:** AMBUSH, corporation meridian, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Sign a Meridian "exclusivity" contract that stops a hunter from jumping you, or refuse it and fight a tier-tweaked Enforcer. The fight pays more if you take it voluntarily and less if it catches you.

## TerminalEventData fields
- id: `ev_mer_exclusive_carrier`
- title: Exclusive Carrier Clause
- speaker: STREET_MERC (1)
- text: "A contract slides across the Terminal screen: 'Exclusive Carrier Agreement, Cell to move no data except via Meridian.' The signature box is already pulsing. Behind it, a dead-eyed courier in a Last-Mile jacket leans on the doorframe, scanning your face against a bounty list. Fine print says refusal 'triggers enforcement of delivery terms.' The courier doesn't look like he's reading it. He looks like he's counting you."
- corporation_id: `meridian`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

**1. Sign it (-15 Cycles/ +Heat)**
- label: "Sign the clause (-20 Cycles, +4 Heat)"
- result_text: "Ink dries on nothing. The courier tips two fingers and goes back to the street. Meridian now knows exactly which lane you use."
- cycle_cost: 20
- hp_cost: 0
- effects: MODIFY_HEAT / CAMPAIGN / amount 4
- reward: none
- (new) starts_combat: none
- (new) next_combat_overrides: none

**2. Void it and take the hit (voluntary ambush)**
- label: "Void the clause and call him out"
- result_text: "You flag the contract as fraud. He drops the clipboard, and a drone swarm unfolds behind him. 'Enforcement of terms,' he says."
- cycle_cost: 0
- hp_cost: 0
- effects: none
- reward: set by the fight (below)
- (new) starts_combat: enemy `last_mile_enforcer` (elite, meridian)
  - combat_overrides: `tier_delta` -1 (fights one tier below the run tier, minimum 1), `enemy_phase_skip` none, `starting_hp_pct` 100
  - stake: on loss/death, normal operative death rules apply. On a win, no HP is restored. The operative enters the fight with current HP.
  - reward on win: 45 Cycles + Firmware choice (1 of 3, common pool, Router-quality). Heat -2 ("you made the courier file a loss report").
  - Defeat/flee: no flee option.

**3. Sneak out through the freight lift (-HP)**
- label: "Slip out through the freight lift (-8 HP)"
- result_text: "You squeeze past the scanner arc and take a pallet corner to the ribs. Behind you, the courier lowers his scanner and starts typing. He'll find you later."
- cycle_cost: 0
- hp_cost: 8
- effects: none
- reward: none
- (new) next_combat_overrides: the next Elite Router on this netrun gets `replace_enemy` = `last_mile_enforcer`, `tier_delta` +1 (capped at tier 4), duration: next one Elite combat only, expires at netrun end if none occurs. The reward for that fight is unchanged (no bonus).
- (new) map_edits: none

## Design notes
- **The three-way split:** Signing is a safe, costly price: 20 Cycles is about a Mainframe item's worth, and 4 Heat is nearly half a MINOR threshold step. Voiding is a gamble with the best payoff: a tier-minus-one Last-Mile Enforcer is a 6-8 turn fight (R1 elite), winnable but expensive in HP. Sneaking costs a small, certain 8 HP but defers a worse fight (tier+1, no bonus). A strong run that wants Firmware picks the fight; a weak or broke run signs.
- **No dominant option:** Sign is dominated only if you have the HP to fight, and the fight is dominated only if you can't afford the HP. Sneaking looks cheap, but its tier+1 ambush punishes a player who is low on HP later. Heat from signing feeds the raid clock, so the "safe" choice is not free on the campaign layer.
- **Economy check (GDD 11 placeholders):** +45 Cycles +Firmware vs -20 Cycles +4 Heat: the fight has about 65 Cycles of swing plus a Firmware, priced against an expected HP loss of roughly 15-25 at tier 2 for a fed operative.
- **Determinism:** The combat uses the standard fight RNG streams. The deferred ambush is fixed by data (`next_combat_overrides` is stored in run state, checkpointed), so there is no random trigger. If no Elite Router remains, the override is simply dropped, which should be shown in the choice tooltip.
- **Systems:** requires N16 (`starts_combat`, `combat_overrides` including `tier_delta` and `replace_enemy`, `next_combat_overrides`). Data-only fallback for choice 2: none. Fallback for choice 3: replace it with a +Heat 3 effect and hp_cost 8, losing the deferred threat.
- **Text keys:** `ev_mer_exclusive_carrier.title/text`, three labels, three results, a tooltip key for "next Elite Router becomes a Last-Mile Enforcer, +1 tier".
- **Collision avoidance:** this is a contract/legal ambush with a deferred variant, distinct from Convoy, Port Strike or Customs ambushes, which are not framed as a contract with a signature trap.

## Q:
- Q: Should `tier_delta` -1 on a voluntary fight also lower the reward pool, or is a flat reward right?
- Q: Does the deferred Enforcer (choice 3) count toward the guaranteed Elite per layer, or replace one?
