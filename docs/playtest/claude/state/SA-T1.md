# State playtest SA-T1 — intermediate tier, persona strategist, ICE 0, breaker vs solace

Cost: $0.09 (71 LLM calls). Option 0 of every menu = the built-in policy (greedy CombatBot).

| Seed | Outcome | Runs | Completed | Deaths | Raids (won) | Heat peak | Breach Heat | Fights | Decisions off-default |
|---|---|---|---|---|---|---|---|---|---|
| 1000 | NONE | 2 | 2 | 0 | 1 (0) | 23 | -1 | 13 | 24 of 79 |

## Reasons by decision kind (sample)

- seed 1000 [combat] Jolt on your wheel (+); Fine Tune on your wheel (+); nudge enemy wheel -1; Overdrive on your wheel (+). RAM 3. End Turn: you deal 36, take 0 (Triage Unit 45->9) — *Option 1 deals the full 36 damage with zero damage taken, and nudging the enemy wheel to -1 lands its Hotfix on a PERFECT slice instead of GOOD or WEAK, so I get the strongest outcome for the same RAM*
- seed 1000 [combat] nudge enemy wheel +1. RAM 0. End Turn: you deal 9, take 0, 1 kill(s) (Triage Unit 9->0). Pointers: Breaker pointer 0: tick 5 -> Shim 6 (offset +0, PERFECT); Tri — *Option 0 kills the Triage Unit and takes zero damage for only 0 RAM spent, so it clears the fight while preserving RAM and cards; the other kill options cost more RAM for no added value, and ending th*
- seed 1000 [combat] nudge your wheel +1; Fine Tune on enemy wheel (+). RAM 1. End Turn: you deal 20, take 0 (Claims Adjuster 112->92). Pointers: Breaker pointer 0: tick 10 -> Shim  — *Options 0, 2, and 4 all deal 20 with zero damage taken, but option 0 spends only 1 RAM and keeps Brute Spin and Jolt in hand for later turns, preserving resources for the fight ahead. Option 5 wastes *
- seed 1000 [combat] Mirror Flip on your wheel (+); nudge enemy wheel -1; Jolt on your wheel (+); Overdrive on your wheel (+). RAM 5. End Turn: you deal 68, take 0 (Claims Adjuster  — *Option 0 deals 68 damage with zero damage taken, leaving the Claims Adjuster at 24 HP and keeping 4 RAM in reserve, which beats option 2's 72 damage at the cost of 8 HP and option 1's 64 damage for an*
- seed 1000 [node] ROUTER at layer 1 (Heat +0) — *All three routers are identical at layer 1 with Heat +0, so I take the first to keep the run moving without spending Heat, and I'll judge future branches on Heat and objective once they differ.*
- seed 1000 [node] ROUTER at layer 4 (Heat +0) — *Heat is at 1 and a Server Rack elite would push it to 3 for a reward I don't need at full HP; the Router at layer 4 keeps Heat flat and keeps the campaign on a safe, low-raid track while the deck is s*
- seed 1000 [node] ROUTER at layer 1 (Heat +0) — *Both router options are identical at Heat +0, so I take the first without any real difference, keeping Heat at 10 and avoiding any new raid pressure while I look for the Exploit Site ahead.*
- seed 1000 [node] ROUTER at layer 2 (Heat +0) — *Both routers are identical at Heat +0 and keep Heat at 10 with no new raid exposure, so I take the first and avoid spending any Heat-raising route; the choice is effectively a coin flip, so I'd rather*
- seed 1000 [reward] Skip this reward — *The deck is a tight 10 cards with a working core. Overload costs HP and exhausts, and Inner Drift and Flick are marginal utility cards that would dilute draws, so skipping keeps the deck consistent.*
- seed 1000 [reward] Skip this reward — *The 10-card deck is tight and working at full HP. Gear Shift is situational, Patch Up is a one-use heal I don't need yet, and a fifth Jolt adds little. Skipping keeps the deck lean and avoids dilution*
- seed 1000 [reward] Firmware Leech into slot 2 (Shim 6): SHIM slice restores 1 RAM on Good or better. — *Leech gives free RAM on a Shim slice, which helps every fight. Heat is already 1, so Coolant Loop adds little, and putting Leech on a Shim 6 slice keeps the wheel's existing slices intact instead of o*
- seed 1000 [reward] Skip this reward — *The 10-card deck is tight and I'm at full HP. A second Overdrive adds variance, Stim Patch is a one-use heal I don't need yet, and Reroll is random. Skipping keeps the deck consistent and doesn't dilu*
- seed 1000 [event] Copy the index (+2 Schematics banked) (+2 Schematics) — *Heat is already at 0 so Wipe's -2 Heat buys nothing while costing 5 HP, and copying the index banks +2 Schematics for future upgrades at no risk to the roster or home server.*
- seed 1000 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *All sites are tier 1 with no objective and +0 Heat, so there's no real difference yet. I'm starting with Breaker 1 at the first site to learn the run structure at no Heat cost, and Breaker 2 stays saf*
- seed 1000 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *Heat is only 5 with no raids yet, so there's no pressure to scrub. The Pricing Memo Archive is the only Site that yields an Exploit, which is the win condition (0 so far). Breaker 1 has more rank, and*

## Run logs

### seed 1000
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 3 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 6 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 6 turns, HP 60 -> 52
      FIGHT won vs account_manager: 5 turns, HP 52 -> 46
    run 1: Breaker 1 R0 T1 t1_a -> COMPLETED, Heat 5, Exploits 0, home 50/50, Schematics 50, armory 2
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 48
      FIGHT won vs dosage_dispenser: 2 turns, HP 48 -> 48
      FIGHT won vs triage_unit: 2 turns, HP 48 -> 48
      FIGHT won vs billing_daemon: 2 turns, HP 48 -> 48
      FIGHT won vs triage_unit: 3 turns, HP 48 -> 44
      FIGHT won vs triage_unit: 2 turns, HP 44 -> 44
      FIGHT won vs account_manager: 7 turns, HP 44 -> 35
    run 2: Breaker 1 R1 T2 t2_intel -> COMPLETED, Heat 23, Exploits 1, home 45/50, Schematics 62, armory 6
