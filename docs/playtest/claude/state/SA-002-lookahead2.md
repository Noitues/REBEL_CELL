# State playtest SA-002-lookahead2 — heuristic strategist, 2-turn lookahead, ICE 0, breaker vs solace

Cost: $0.00 (0 LLM calls). Option 0 of every menu = the built-in policy (greedy CombatBot).

**Totals over 20 seeds:** wins 16 (80%); run of the win 13, 17, 25, 29, 32, 32, 34, 37, 38, 45, 53, 54, 55, 55, 56, 57; deaths 6 (mean 0.3, max 2); Heat peak max 100 (mean 56); Schematics at the end mean 170; boss attempts 22, boss wins 16.

| Seed | Outcome | Runs | Win run | Completed | Deaths | Raids (won) | Heat peak | Breach Heat | Schematics end | Boss attempts | Fights | Decisions off-default |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1000 | NONE | 60 | - | 60 | 0 | 6 (2) | 100 | -1 | 155 | 0 | 368 | 281 of 1925 |
| 1001 | NONE | 60 | - | 58 | 2 | 6 (2) | 100 | 9 | 143 | 2 | 361 | 379 of 2062 |
| 1002 | WON | 25 | 25 | 25 | 0 | 3 (2) | 35 | 0 | 172 | 1 | 154 | 162 of 855 |
| 1003 | WON | 57 | 57 | 57 | 0 | 3 (1) | 67 | 0 | 215 | 1 | 353 | 314 of 1953 |
| 1004 | WON | 53 | 53 | 53 | 0 | 7 (3) | 100 | 0 | 167 | 1 | 315 | 513 of 2369 |
| 1005 | WON | 37 | 37 | 37 | 0 | 3 (2) | 42 | 0 | 270 | 1 | 229 | 205 of 1276 |
| 1006 | NONE | 60 | - | 60 | 0 | 4 (1) | 67 | -1 | 61 | 0 | 376 | 291 of 1966 |
| 1007 | WON | 55 | 55 | 55 | 0 | 3 (2) | 39 | 0 | 137 | 1 | 345 | 260 of 1792 |
| 1008 | WON | 34 | 34 | 34 | 0 | 3 (2) | 43 | 0 | 325 | 1 | 212 | 215 of 1187 |
| 1009 | WON | 17 | 17 | 17 | 0 | 3 (0) | 37 | 0 | 139 | 1 | 100 | 135 of 632 |
| 1010 | WON | 45 | 45 | 45 | 0 | 4 (2) | 57 | 0 | 212 | 1 | 283 | 229 of 1522 |
| 1011 | NONE | 60 | - | 58 | 2 | 3 (2) | 63 | 9 | 188 | 2 | 364 | 364 of 2028 |
| 1012 | WON | 13 | 13 | 13 | 0 | 4 (0) | 41 | 10 | 85 | 1 | 74 | 143 of 560 |
| 1013 | WON | 32 | 32 | 32 | 0 | 3 (2) | 34 | 0 | 190 | 1 | 190 | 183 of 1073 |
| 1014 | WON | 29 | 29 | 29 | 0 | 3 (2) | 34 | 2 | 118 | 1 | 173 | 179 of 972 |
| 1015 | WON | 56 | 56 | 56 | 0 | 5 (1) | 79 | 1 | 216 | 1 | 341 | 288 of 1838 |
| 1016 | WON | 55 | 55 | 53 | 2 | 3 (1) | 45 | 10 | 122 | 3 | 333 | 334 of 1946 |
| 1017 | WON | 32 | 32 | 32 | 0 | 4 (2) | 30 | 4 | 147 | 1 | 196 | 191 of 1091 |
| 1018 | WON | 38 | 38 | 38 | 0 | 3 (0) | 48 | 2 | 185 | 1 | 236 | 229 of 1345 |
| 1019 | WON | 54 | 54 | 54 | 0 | 5 (2) | 59 | 0 | 157 | 1 | 343 | 279 of 1762 |

## Reasons by decision kind (sample)

- seed 1000 [combat] Jolt on your wheel (+); Fine Tune on your wheel (+); Overdrive on your wheel (+). RAM 3. End Turn: you deal 36, take 0 (Triage Unit 45->9). Pointers: Breaker po — *combat: value 70.0 (deal 36, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1000 [combat] Play nothing, end the turn. RAM 0. End Turn: you deal 9, take 0, 1 kill(s) (Triage Unit 9->0). Pointers: Breaker pointer 0: tick 5 -> Shim 6 (offset +0, PERFECT — *combat: value 1034.0 (deal 9, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1000 [combat] Jolt on enemy wheel (+). RAM 1. End Turn: you deal 20, take 0 (Claims Adjuster 112->92). Pointers: Breaker pointer 0: tick 5 -> Shim 6 (offset +0, PERFECT); Cla — *combat: value 80.8 (deal 20, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1000 [combat] Jolt on your wheel (+); Jolt on your wheel (+); nudge your wheel +1; Overdrive on your wheel (+). RAM 3. End Turn: you deal 72, take 8 (Claims Adjuster 92->20). — *combat: value 105.8 (deal 72, take 8, 0 kill(s)) with 2-turn lookahead*
- seed 1000 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1000 [node] ELITE SERVER_RACK at layer 4 (Heat +2) — *node: value 43.8 at 87% HP*
- seed 1000 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1000 [node] ROUTER at layer 2 (Heat +0) — *node: value 40.0 at 78% HP*
- seed 1000 [reward] Card Flick: Spin a wheel 1 tick. — *reward: card flick value 3.00*
- seed 1000 [reward] Card Jolt: Spin a wheel 3 ticks. — *reward: card jolt value 3.00*
- seed 1000 [reward] Firmware Leech into slot 2 (Shim 6): SHIM slice restores 1 RAM on Good or better. — *reward: firmware leech value 0.50*
- seed 1000 [reward] Card Overdrive: OVERCLOCK your slice under the pointer: 1.5x on its next trigger, then it becomes CORRUPTED. — *reward: card overdrive value 4.25*
- seed 1000 [event] Walk on — *event: the safest allowed choice*
- seed 1000 [event] Walk on — *event: the safest allowed choice*
- seed 1000 [event] Scrub your traces (-2 Heat) (-2 Heat) — *event: the safest allowed choice*
- seed 1000 [event] Leave it — *event: the safest allowed choice*
- seed 1000 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1000 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 5*
- seed 1000 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 18*
- seed 1000 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 24, take the -5 Heat Site*
- seed 1000 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *raid: best exact projection (home 50 after)*
- seed 1000 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 2, reached home 0, DOWN t1_a, TAKEN none — *raid: best exact projection (home 50 after)*
- seed 1000 [raid] spread from home outward (default): projected lost, home 50 -> 42, threats destroyed 1, reached home 2, DOWN none, TAKEN none — *raid: best exact projection (home 42 after)*
- seed 1000 [raid] spread from home outward (default): projected lost, home 50 -> 31, threats destroyed 2, reached home 2, DOWN none, TAKEN none — *raid: best exact projection (home 31 after)*
- seed 1000 [shop] Card Sanitize for 60 Cycles: Remove CORRUPTED from a chosen slice and gain 3 block. — *shop: buy card sanitize (value 4.00)*
- seed 1000 [shop] Firmware Leech for 121 Cycles: SHIM slice restores 1 RAM on Good or better. (into slot 5, Defrag 5) — *shop: buy firmware leech (value 0.50)*
- seed 1000 [shop] Firmware Patch+ for 84 Cycles: Slice output +50%. (into slot 5, Defrag 5) — *shop: buy firmware patch_plus (value 5.00)*
- seed 1000 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1000 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1000 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *hq: claim for 30 Schematics (46 held)*
- seed 1000 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1000 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *hq: repair_home for 5 Schematics (58 held)*
- seed 1001 [combat] Jolt on your wheel (+); nudge your wheel +1; Brute Spin on enemy wheel (+). RAM 3. End Turn: you deal 22, take 6 (Care Swarm 25->3). Pointers: Breaker pointer 0 — *combat: value 33.2 (deal 22, take 6, 0 kill(s)) with 2-turn lookahead*
- seed 1001 [combat] nudge enemy wheel +1. RAM 0. End Turn: you deal 3, take 6, 1 kill(s) (Care Swarm 3->0). Pointers: Breaker pointer 0: tick 15 -> Shim 6 (offset +0, PERFECT); Car — *combat: value 1019.6 (deal 3, take 6, 1 kill(s)) with 2-turn lookahead*
- seed 1001 [combat] nudge your wheel +1; Mirror Flip on your wheel (+); Overdrive on your wheel (+). RAM 4. End Turn: you deal 18, take 3 (Care Swarm 25->7). Pointers: Breaker poin — *combat: value 37.4 (deal 18, take 3, 0 kill(s)) with 2-turn lookahead*
- seed 1001 [combat] nudge your wheel +1. RAM 0. End Turn: you deal 7, take 6, 1 kill(s) (Care Swarm 7->0). Pointers: Breaker pointer 0: tick 15 -> Shim 6 (offset +0, PERFECT); Care — *combat: value 1023.6 (deal 7, take 6, 1 kill(s)) with 2-turn lookahead*
- seed 1001 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1001 [node] ROUTER at layer 2 (Heat +0) — *node: value 40.0 at 80% HP*
- seed 1001 [node] ROUTER at layer 3 (Heat +0) — *node: value 40.0 at 65% HP*
- seed 1001 [node] ROUTER at layer 5 (Heat +0) — *node: value 40.0 at 63% HP*
- seed 1001 [reward] Skip this reward — *reward: nothing above the thresholds, skip*
- seed 1001 [reward] Card Sanitize: Remove CORRUPTED from a chosen slice and gain 3 block. — *reward: card sanitize value 4.00*
- seed 1001 [reward] Firmware Patch+ into slot 2 (Shim 6): Slice output +50%. — *reward: firmware patch_plus value 5.00*
- seed 1001 [reward] Card Brute Spin: Spin a wheel 6 ticks. — *reward: card brute_spin value 4.00*
- seed 1001 [event] Scrub your traces (-2 Heat) (-2 Heat) — *event: the safest allowed choice*
- seed 1001 [event] Walk on — *event: the safest allowed choice*
- seed 1001 [event] Take the left route (+15 Cycles) (+15 Cycles) — *event: the safest allowed choice*
- seed 1001 [event] Walk on — *event: the safest allowed choice*
- seed 1001 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1001 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 3*
- seed 1001 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 14*
- seed 1001 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 21, take the -5 Heat Site*
- seed 1001 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *raid: best exact projection (home 50 after)*
- seed 1001 [raid] spread from home outward (default): projected lost, home 50 -> 45, threats destroyed 2, reached home 1, DOWN none, TAKEN none — *raid: best exact projection (home 45 after)*
- seed 1001 [raid] spread from home outward (default): projected lost, home 50 -> 21, threats destroyed 0, reached home 4, DOWN none, TAKEN none — *raid: best exact projection (home 21 after)*
- seed 1001 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1001 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1001 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1001 [shop] Firmware Barbed Wire for 81 Cycles: DEFRAG slice also deals 2 damage to the pointer target. (into slot 4, Shim 6) — *shop: buy firmware barbed_wire (value 0.50)*
- seed 1001 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1001 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *hq: claim for 30 Schematics (48 held)*
- seed 1001 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1001 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *hq: repair_home for 5 Schematics (56 held)*
- seed 1002 [combat] Jolt on your wheel (+); Overdrive on your wheel (+); Brute Spin on enemy wheel (+). RAM 4. End Turn: you deal 18, take 6 (Care Swarm 25->7). Pointers: Breaker p — *combat: value 29.0 (deal 18, take 6, 0 kill(s)) with 2-turn lookahead*
- seed 1002 [combat] nudge your wheel +1; Mirror Flip on your wheel (+). RAM 3. End Turn: you deal 7, take 9, 1 kill(s) (Care Swarm 7->0). Pointers: Breaker pointer 0: tick 0 -> Ove — *combat: value 1019.4 (deal 7, take 9, 1 kill(s)) with 2-turn lookahead*
- seed 1002 [combat] Brute Spin on your wheel (+); nudge your wheel -1; nudge enemy wheel +1. RAM 3. End Turn: you deal 20, take 0 (Claims Adjuster 112->92). Pointers: Breaker point — *combat: value 80.8 (deal 20, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1002 [combat] Jolt on your wheel (+); Mirror Flip on your wheel (+); Jolt on enemy wheel (+); Overdrive on your wheel (+). RAM 6. End Turn: you deal 72, take 10 (Claims Adjus — *combat: value 103.0 (deal 72, take 10, 0 kill(s)) with 2-turn lookahead*
- seed 1002 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1002 [node] TERMINAL at layer 5 (Heat +0) — *node: value 20.0 at 58% HP*
- seed 1002 [node] ROUTER at layer 6 (Heat +0) — *node: value 40.0 at 58% HP*
- seed 1002 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1002 [reward] Card Brute Spin: Spin a wheel 6 ticks. — *reward: card brute_spin value 4.00*
- seed 1002 [reward] Firmware Barbed Wire into slot 2 (Shim 6): DEFRAG slice also deals 2 damage to the pointer target. — *reward: firmware barbed_wire value 0.50*
- seed 1002 [reward] Skip this reward — *reward: nothing above the thresholds, skip*
- seed 1002 [reward] Daemon Zero Day: A Perfect on the NULL slice resolves as a 3x OVERFLOW. — *reward: daemon zero_day value 3.80*
- seed 1002 [event] Decline the terms — *event: the safest allowed choice*
- seed 1002 [event] Walk on — *event: the safest allowed choice*
- seed 1002 [event] Walk on — *event: the safest allowed choice*
- seed 1002 [event] Clean your own logs instead (-3 Heat) (-3 Heat) — *event: the safest allowed choice*
- seed 1002 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1002 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 4*
- seed 1002 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 16*
- seed 1002 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 30, take the -5 Heat Site*
- seed 1002 [raid] spread from home outward (default): projected CELL HOLDS, home 45 -> 45, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *raid: best exact projection (home 45 after)*
- seed 1002 [shop] Firmware Patch+ for 102 Cycles: Slice output +50%. (into slot 2, Shim 6) — *shop: buy firmware patch_plus (value 5.00)*
- seed 1002 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1002 [shop] Firmware Static Coat for 92 Cycles: DEFRAG slice also grants 2 shield. (into slot 3, Shim 6) — *shop: buy firmware static_coat (value 0.50)*
- seed 1002 [shop] Firmware Recycler for 87 Cycles: The NULL slice restores 2 RAM when it resolves. (into slot 6, Null) — *shop: buy firmware recycler (value 0.50)*
- seed 1002 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1002 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *hq: claim for 30 Schematics (51 held)*
- seed 1002 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1002 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *hq: repair_home for 5 Schematics (81 held)*
- seed 1003 [combat] Mirror Flip on your wheel (+); nudge your wheel -1; Overdrive on your wheel (+). RAM 4. End Turn: you deal 36, take 0 (Compliance Officer 50->14). Pointers: Bre — *combat: value 45.0 (deal 36, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1003 [combat] Brute Spin on enemy wheel (+); nudge your wheel -1; Fine Tune on enemy wheel (-). RAM 3. End Turn: you deal 9, take 0 (Compliance Officer 14->5). Pointers: Brea — *combat: value 39.0 (deal 9, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1003 [combat] Mirror Flip on your wheel (+); Brute Spin on enemy wheel (+). RAM 5. End Turn: you deal 5, take 0, 1 kill(s) (Compliance Officer 5->0). Pointers: Breaker pointe — *combat: value 1030.0 (deal 5, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1003 [combat] Fine Tune on enemy wheel (+); Overdrive on your wheel (+); Mirror Flip on enemy wheel (+). RAM 5. End Turn: you deal 18, take 9 (Care Swarm 25->7). Pointers: Br — *combat: value 5.4 (deal 18, take 9, 0 kill(s)) with 2-turn lookahead*
- seed 1003 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1003 [node] ROUTER at layer 2 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1003 [node] ELITE SERVER_RACK at layer 4 (Heat +2) — *node: value 43.8 at 75% HP*
- seed 1003 [node] ELITE ROUTER at layer 5 (Heat +1) — *node: value 26.6 at 65% HP*
- seed 1003 [reward] Card Flick: Spin a wheel 1 tick. — *reward: card flick value 3.00*
- seed 1003 [reward] Card Snap: Move your outer ring to the nearest slice centre (Perfect). — *reward: card snap value 2.00*
- seed 1003 [reward] Card Brute Spin: Spin a wheel 6 ticks. — *reward: card brute_spin value 4.00*
- seed 1003 [reward] Firmware Static Coat into slot 2 (Shim 6): DEFRAG slice also grants 2 shield. — *reward: firmware static_coat value 0.50*
- seed 1003 [event] Walk on — *event: the safest allowed choice*
- seed 1003 [event] Walk on — *event: the safest allowed choice*
- seed 1003 [event] Walk on — *event: the safest allowed choice*
- seed 1003 [event] Walk on — *event: the safest allowed choice*
- seed 1003 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1003 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 3*
- seed 1003 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 13*
- seed 1003 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 18, take the -5 Heat Site*
- seed 1003 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 3, reached home 0, DOWN none, TAKEN none — *raid: best exact projection (home 50 after)*
- seed 1003 [shop] Firmware Overvolt for 101 Cycles: SHIM and OVERFLOW slices: output +25%. (into slot 2, Shim 6) — *shop: buy firmware overvolt (value 2.50)*
- seed 1003 [shop] Firmware Bulkhead for 111 Cycles: DEFRAG and SANDBOX slices: output +50%. (into slot 3, Shim 6) — *shop: buy firmware bulkhead (value 1.50)*
- seed 1003 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1003 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1003 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1003 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *hq: claim for 30 Schematics (59 held)*
- seed 1003 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1003 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *hq: repair_home for 5 Schematics (56 held)*
- seed 1004 [combat] Jolt on enemy wheel (+); Overdrive on your wheel (+); nudge your wheel -1; nudge your wheel -1. RAM 3. End Turn: you deal 33, take 3 (Collections Agent 40->7).  — *combat: value 56.6 (deal 33, take 3, 0 kill(s)) with 2-turn lookahead*
- seed 1004 [combat] Brute Spin on enemy wheel (+); nudge your wheel +1; Jolt on enemy wheel (+). RAM 3. End Turn: you deal 7, take 3, 1 kill(s) (Collections Agent 7->0). Pointers:  — *combat: value 1027.8 (deal 7, take 3, 1 kill(s)) with 2-turn lookahead*
- seed 1004 [combat] Jolt on enemy wheel (+); Mirror Flip on enemy wheel (+). RAM 4. End Turn: you deal 24, take 0 (Billing Daemon 42->18). Pointers: Breaker pointer 0: tick 0 -> Ov — *combat: value 67.0 (deal 24, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1004 [combat] Jolt on your wheel (+); Overdrive on your wheel (+); Fine Tune on enemy wheel (+). RAM 3. End Turn: you deal 18, take 0, 1 kill(s) (Billing Daemon 18->0). Point — *combat: value 1043.0 (deal 18, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1004 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1004 [node] ROUTER at layer 3 (Heat +0) — *node: value 40.0 at 90% HP*
- seed 1004 [node] ELITE SERVER_RACK at layer 4 (Heat +2) — *node: value 44.0 at 90% HP*
- seed 1004 [node] ELITE ROUTER at layer 6 (Heat +1) — *node: value 26.8 at 85% HP*
- seed 1004 [reward] Card Flip Switch: Flip your own wheel. — *reward: card flip_switch value 2.25*
- seed 1004 [reward] Skip this reward — *reward: nothing above the thresholds, skip*
- seed 1004 [reward] Card Brute Spin: Spin a wheel 6 ticks. — *reward: card brute_spin value 4.00*
- seed 1004 [reward] Card Cleanse: Remove CORRUPTED from a chosen slice. — *reward: card cleanse value 4.00*
- seed 1004 [event] Walk on — *event: the safest allowed choice*
- seed 1004 [event] Decline the terms — *event: the safest allowed choice*
- seed 1004 [event] Delete it (-1 Heat) (-1 Heat) — *event: the safest allowed choice*
- seed 1004 [event] Walk on — *event: the safest allowed choice*
- seed 1004 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1004 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 4*
- seed 1004 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 17*
- seed 1004 [launch] Send Breaker 1 (R3) to Implant Provisioning Hub: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1004 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *raid: best exact projection (home 50 after)*
- seed 1004 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 2, reached home 0, DOWN t1_a, TAKEN t1_a — *raid: best exact projection (home 50 after)*
- seed 1004 [raid] spread from home outward (default): projected lost, home 50 -> 41, threats destroyed 2, reached home 2, DOWN none, TAKEN none — *raid: best exact projection (home 41 after)*
- seed 1004 [raid] spread from home outward (default): projected lost, home 50 -> 44, threats destroyed 5, reached home 1, DOWN none, TAKEN none — *raid: best exact projection (home 44 after)*
- seed 1004 [shop] Firmware Overvolt for 77 Cycles: SHIM and OVERFLOW slices: output +25%. (into slot 5, Defrag 5) — *shop: buy firmware overvolt (value 2.50)*
- seed 1004 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1004 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1004 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1004 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1004 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *hq: claim for 30 Schematics (58 held)*
- seed 1004 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1004 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *hq: repair_home for 5 Schematics (73 held)*
- seed 1005 [combat] Brute Spin on your wheel (+). RAM 2. End Turn: you deal 24, take 0 (Billing Daemon 42->18). Pointers: Breaker pointer 0: tick 0 -> Overflow 12 (offset +0, PERFE — *combat: value 67.0 (deal 24, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1005 [combat] Fine Tune on your wheel (-); nudge your wheel -1; nudge enemy wheel +1. RAM 2. End Turn: you deal 18, take 0, 1 kill(s) (Billing Daemon 18->0). Pointers: Breake — *combat: value 1043.0 (deal 18, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1005 [combat] Jolt on your wheel (+); Brute Spin on enemy wheel (+); Mirror Flip on enemy wheel (+); nudge enemy wheel -1. RAM 6. End Turn: you deal 24, take 0 (Compliance Of — *combat: value 75.0 (deal 24, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1005 [combat] Brute Spin on your wheel (+); Jolt on your wheel (+); Overdrive on your wheel (+). RAM 4. End Turn: you deal 26, take 0, 1 kill(s) (Compliance Officer 26->0). P — *combat: value 1051.0 (deal 26, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1005 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1005 [node] ROUTER at layer 2 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1005 [node] ROUTER at layer 5 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1005 [node] ROUTER at layer 6 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1005 [reward] Skip this reward — *reward: nothing above the thresholds, skip*
- seed 1005 [reward] Card Spin Cycle: Spin a wheel 12 ticks. — *reward: card spin_cycle value 4.25*
- seed 1005 [reward] Card Spin Cycle: Spin a wheel 12 ticks. — *reward: card spin_cycle value 4.25*
- seed 1005 [reward] Firmware Patch+ into slot 2 (Shim 6): Slice output +50%. — *reward: firmware patch_plus value 5.00*
- seed 1005 [event] Walk on — *event: the safest allowed choice*
- seed 1005 [event] Walk past — *event: the safest allowed choice*
- seed 1005 [event] Not today — *event: the safest allowed choice*
- seed 1005 [event] Walk on — *event: the safest allowed choice*
- seed 1005 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1005 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 2*
- seed 1005 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 14*
- seed 1005 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 22, take the -5 Heat Site*
- seed 1005 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *raid: best exact projection (home 50 after)*
- seed 1005 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1005 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1005 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1005 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1005 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1005 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *hq: claim for 30 Schematics (45 held)*
- seed 1005 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1005 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *hq: repair_home for 5 Schematics (81 held)*
- seed 1006 [combat] Mirror Flip on your wheel (+); nudge enemy wheel -1; nudge your wheel -1; Overdrive on your wheel (+). RAM 5. End Turn: you deal 36, take 0 (Dosage Dispenser 38 — *combat: value 63.0 (deal 36, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1006 [combat] Brute Spin on your wheel (+); Brute Spin on your wheel (+). RAM 4. End Turn: you deal 2, take 0, 1 kill(s) (Dosage Dispenser 2->0). Pointers: Breaker pointer 0: — *combat: value 1027.0 (deal 2, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1006 [combat] nudge your wheel +1; Jolt on enemy wheel (+). RAM 1. End Turn: you deal 12, take 0 (Compliance Officer 50->38). Pointers: Breaker pointer 0: tick 15 -> Shim 6 ( — *combat: value 45.0 (deal 12, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1006 [combat] Brute Spin on your wheel (+); Fine Tune on your wheel (-); nudge your wheel -1; Overdrive on your wheel (+). RAM 4. End Turn: you deal 33, take 0 (Compliance Of — *combat: value 63.0 (deal 33, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1006 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1006 [node] ROUTER at layer 3 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1006 [node] ROUTER at layer 5 (Heat +0) — *node: value 40.0 at 95% HP*
- seed 1006 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1006 [reward] Card Counter-Spin: Spin a wheel 5 ticks counter-clockwise. — *reward: card counter_spin value 3.00*
- seed 1006 [reward] Card Ring Tap: Two +-1 nudges on your inner ring. — *reward: card ring_tap value 2.50*
- seed 1006 [reward] Firmware Static Coat into slot 2 (Shim 6): DEFRAG slice also grants 2 shield. — *reward: firmware static_coat value 0.50*
- seed 1006 [reward] Card Spin Cycle: Spin a wheel 12 ticks. — *reward: card spin_cycle value 4.25*
- seed 1006 [event] Walk on — *event: the safest allowed choice*
- seed 1006 [event] Strip it for parts (+25 Cycles, +2 Heat) (+25 Cycles, +2 Heat) — *event: the safest allowed choice*
- seed 1006 [event] Scrub your traces (-2 Heat) (-2 Heat) — *event: the safest allowed choice*
- seed 1006 [event] Walk on — *event: the safest allowed choice*
- seed 1006 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1006 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 4*
- seed 1006 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 19*
- seed 1006 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 36, take the -5 Heat Site*
- seed 1006 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *raid: best exact projection (home 50 after)*
- seed 1006 [raid] spread from home outward (default): projected lost, home 50 -> 35, threats destroyed 0, reached home 2, DOWN t1_a, TAKEN none — *raid: best exact projection (home 35 after)*
- seed 1006 [raid] spread from home outward (default): projected lost, home 50 -> 42, threats destroyed 1, reached home 2, DOWN none, TAKEN none — *raid: best exact projection (home 42 after)*
- seed 1006 [shop] Firmware Static Coat for 107 Cycles: DEFRAG slice also grants 2 shield. (into slot 3, Shim 6) — *shop: buy firmware static_coat (value 0.50)*
- seed 1006 [shop] Card Flip Switch for 51 Cycles: Flip your own wheel. — *shop: buy card flip_switch (value 2.25)*
- seed 1006 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1006 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1006 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1006 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *hq: claim for 30 Schematics (54 held)*
- seed 1006 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1006 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *hq: repair_home for 5 Schematics (69 held)*
- seed 1007 [combat] nudge your wheel -1; Overdrive on your wheel (+). RAM 1. End Turn: you deal 18, take 3 (Care Swarm 25->7). Pointers: Breaker pointer 0: tick 5 -> Shim 6 (offset — *combat: value 33.2 (deal 18, take 3, 0 kill(s)) with 2-turn lookahead*
- seed 1007 [combat] Jolt on your wheel (+); Jolt on your wheel (+). RAM 2. End Turn: you deal 7, take 9, 1 kill(s) (Care Swarm 7->0). Pointers: Breaker pointer 0: tick 15 -> Shim 6 — *combat: value 1019.4 (deal 7, take 9, 1 kill(s)) with 2-turn lookahead*
- seed 1007 [combat] Jolt on enemy wheel (+); nudge your wheel +1; Jolt on enemy wheel (+). RAM 2. End Turn: you deal 24, take 0 (Billing Daemon 42->18). Pointers: Breaker pointer 0 — *combat: value 61.4 (deal 24, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1007 [combat] Fine Tune on your wheel (-); Overdrive on your wheel (+). RAM 2. End Turn: you deal 18, take 4, 1 kill(s) (Billing Daemon 18->0). Pointers: Breaker pointer 0: t — *combat: value 1037.4 (deal 18, take 4, 1 kill(s)) with 2-turn lookahead*
- seed 1007 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1007 [node] ROUTER at layer 2 (Heat +0) — *node: value 40.0 at 80% HP*
- seed 1007 [node] ROUTER at layer 3 (Heat +0) — *node: value 40.0 at 73% HP*
- seed 1007 [node] ELITE ROUTER at layer 5 (Heat +1) — *node: value 26.8 at 60% HP*
- seed 1007 [reward] Skip this reward — *reward: nothing above the thresholds, skip*
- seed 1007 [reward] Card Shatter: Breach the target Hub for 1 turn and strip 1 resistance. — *reward: card shatter value 2.25*
- seed 1007 [reward] Card Corrupt Packet: CORRUPT the enemy slice under your pointer. — *reward: card corrupt_packet value 1.75*
- seed 1007 [reward] Firmware Recycler into slot 2 (Shim 6): The NULL slice restores 2 RAM when it resolves. — *reward: firmware recycler value 0.50*
- seed 1007 [event] Walk on — *event: the safest allowed choice*
- seed 1007 [event] Walk on — *event: the safest allowed choice*
- seed 1007 [event] Walk on — *event: the safest allowed choice*
- seed 1007 [event] Ghost past — *event: the safest allowed choice*
- seed 1007 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1007 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 6*
- seed 1007 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 18*
- seed 1007 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 27, take the -5 Heat Site*
- seed 1007 [raid] outer nodes first, home last: projected CELL HOLDS, home 45 -> 45, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *raid: best exact projection (home 45 after)*
- seed 1007 [shop] Firmware Power Cell for 139 Cycles: SANDBOX slice also restores 1 RAM. (into slot 2, Shim 6) — *shop: buy firmware power_cell (value 0.50)*
- seed 1007 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1007 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1007 [shop] Firmware Static Coat for 98 Cycles: DEFRAG slice also grants 2 shield. (into slot 3, Shim 6) — *shop: buy firmware static_coat (value 0.50)*
- seed 1007 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1007 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *hq: claim for 30 Schematics (59 held)*
- seed 1007 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1007 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *hq: repair_home for 5 Schematics (100 held)*
- seed 1008 [combat] Play nothing, end the turn. RAM 0. End Turn: you deal 6, take 6 (Care Swarm 25->19). Pointers: Breaker pointer 0: tick 5 -> Shim 6 (offset +0, PERFECT); Care Sw — *combat: value 33.2 (deal 6, take 6, 0 kill(s)) with 2-turn lookahead*
- seed 1008 [combat] Brute Spin on your wheel (+); nudge your wheel +1. RAM 2. End Turn: you deal 19, take 6, 1 kill(s) (Care Swarm 19->0). Pointers: Breaker pointer 0: tick 0 -> Ov — *combat: value 1035.6 (deal 19, take 6, 1 kill(s)) with 2-turn lookahead*
- seed 1008 [combat] nudge your wheel +1; Jolt on enemy wheel (+); Jolt on enemy wheel (+); Mirror Flip on enemy wheel (+). RAM 5. End Turn: you deal 12, take 0 (Billing Daemon 42-> — *combat: value 36.0 (deal 12, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1008 [combat] Fine Tune on enemy wheel (-); nudge your wheel +1; Counter-Spin on enemy wheel (+). RAM 2. End Turn: you deal 24, take 0 (Billing Daemon 30->6). Pointers: Break — *combat: value 55.0 (deal 24, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1008 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1008 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1008 [node] ROUTER at layer 2 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1008 [node] ELITE SERVER_RACK at layer 4 (Heat +3) — *node: value 37.4 at 93% HP*
- seed 1008 [reward] Card Counter-Spin: Spin a wheel 5 ticks counter-clockwise. — *reward: card counter_spin value 3.00*
- seed 1008 [reward] Card Spin Cycle: Spin a wheel 12 ticks. — *reward: card spin_cycle value 4.25*
- seed 1008 [reward] Firmware Bulkhead into slot 2 (Shim 6): DEFRAG and SANDBOX slices: output +50%. — *reward: firmware bulkhead value 1.50*
- seed 1008 [reward] Card Gear Shift: Move your inner ring 5 ticks. — *reward: card gear_shift value 2.50*
- seed 1008 [event] Trade gear (Asset: Flak Array) (-10 Cycles, Asset: Flak Array) — *event: the safest allowed choice*
- seed 1008 [event] Walk on — *event: the safest allowed choice*
- seed 1008 [event] Ghost past — *event: the safest allowed choice*
- seed 1008 [event] Walk on — *event: the safest allowed choice*
- seed 1008 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1008 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 5*
- seed 1008 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 17*
- seed 1008 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 29, take the -5 Heat Site*
- seed 1008 [raid] spread from home outward (default): projected CELL HOLDS, home 45 -> 45, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *raid: best exact projection (home 45 after)*
- seed 1008 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1008 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1008 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1008 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1008 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1008 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *hq: claim for 30 Schematics (48 held)*
- seed 1008 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1008 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *hq: repair_home for 5 Schematics (91 held)*
- seed 1009 [combat] Overdrive on your wheel (+); Fine Tune on your wheel (-). RAM 2. End Turn: you deal 18, take 0 (Collections Agent 40->22). Pointers: Breaker pointer 0: tick 10  — *combat: value 25.8 (deal 18, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1009 [combat] Play nothing, end the turn. RAM 0. End Turn: you deal 12, take 3 (Collections Agent 22->10). Pointers: Breaker pointer 0: tick 5 -> Shim 6 (offset +0, PERFECT); — *combat: value 42.8 (deal 12, take 3, 0 kill(s)) with 2-turn lookahead*
- seed 1009 [combat] Fine Tune on your wheel (-). RAM 1. End Turn: you deal 10, take 0, 1 kill(s) (Collections Agent 10->0). Pointers: Breaker pointer 0: tick 1 -> Overflow 12 (offs — *combat: value 1035.0 (deal 10, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1009 [combat] Mirror Flip on your wheel (+); nudge your wheel +1; Overdrive on your wheel (+); nudge your wheel +1. RAM 5. End Turn: you deal 36, take 4 (Billing Daemon 42->6 — *combat: value 61.4 (deal 36, take 4, 0 kill(s)) with 2-turn lookahead*
- seed 1009 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1009 [node] ROUTER at layer 2 (Heat +0) — *node: value 40.0 at 95% HP*
- seed 1009 [node] ELITE SERVER_RACK at layer 4 (Heat +2) — *node: value 44.0 at 83% HP*
- seed 1009 [node] ROUTER at layer 5 (Heat +0) — *node: value 40.0 at 83% HP*
- seed 1009 [reward] Card Armor Plate: ENCRYPT a chosen slice and gain 4 block. — *reward: card armor_plate value 4.50*
- seed 1009 [reward] Card Micro-Adjust: Two +-1 nudges. Exhaust. — *reward: card micro_adjust value 2.50*
- seed 1009 [reward] Firmware Bulkhead into slot 2 (Shim 6): DEFRAG and SANDBOX slices: output +50%. — *reward: firmware bulkhead value 1.50*
- seed 1009 [reward] Card Counter-Spin: Spin a wheel 5 ticks counter-clockwise. — *reward: card counter_spin value 3.00*
- seed 1009 [event] Walk on — *event: the safest allowed choice*
- seed 1009 [event] Walk past — *event: the safest allowed choice*
- seed 1009 [event] Walk on — *event: the safest allowed choice*
- seed 1009 [event] Walk on — *event: the safest allowed choice*
- seed 1009 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1009 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 4*
- seed 1009 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 19*
- seed 1009 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 27, take the -5 Heat Site*
- seed 1009 [raid] spread from home outward (default): projected lost, home 50 -> 45, threats destroyed 1, reached home 1, DOWN none, TAKEN none — *raid: best exact projection (home 45 after)*
- seed 1009 [shop] Firmware Nanite Mesh for 106 Cycles: HOTFIX slice: output +50%, and it cleanses itself after resolving. (into slot 4, Shim 6) — *shop: buy firmware nanite_mesh (value 2.00)*
- seed 1009 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1009 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1009 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1009 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1009 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *hq: claim for 30 Schematics (56 held)*
- seed 1009 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1009 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *hq: repair_home for 5 Schematics (75 held)*
- seed 1010 [combat] nudge your wheel +1; Overdrive on your wheel (+); Fine Tune on enemy wheel (+); Brute Spin on enemy wheel (+). RAM 4. End Turn: you deal 18, take 0 (Compliance  — *combat: value 42.0 (deal 18, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1010 [combat] Jolt on enemy wheel (+); Mirror Flip on your wheel (+); Fine Tune on enemy wheel (-). RAM 5. End Turn: you deal 24, take 0 (Compliance Officer 32->8). Pointers: — *combat: value 57.0 (deal 24, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1010 [combat] Fine Tune on your wheel (+). RAM 1. End Turn: you deal 8, take 0, 1 kill(s) (Compliance Officer 8->0). Pointers: Breaker pointer 0: tick 20 -> Shim 6 (offset +0 — *combat: value 1033.0 (deal 8, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1010 [combat] Overdrive on your wheel (+); Fine Tune on your wheel (-). RAM 2. End Turn: you deal 36, take 0 (Collections Agent 40->4). Pointers: Breaker pointer 0: tick 0 -> — *combat: value 60.8 (deal 36, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1010 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1010 [node] ROUTER at layer 2 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1010 [node] ELITE SERVER_RACK at layer 4 (Heat +2) — *node: value 44.0 at 95% HP*
- seed 1010 [node] ROUTER at layer 6 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1010 [reward] Card Ratchet: Move your inner ring 8 ticks. — *reward: card ratchet value 2.50*
- seed 1010 [reward] Card Heavy Spin: Spin a wheel 9 ticks. — *reward: card heavy_spin value 4.00*
- seed 1010 [reward] Card Inner Drift: Move your inner ring 3 ticks. — *reward: card inner_drift value 2.75*
- seed 1010 [reward] Daemon Adrenal Loop: Each Perfect heals 2. — *reward: daemon adrenal_loop value 4.00*
- seed 1010 [event] Clean your own logs instead (-3 Heat) (-3 Heat) — *event: the safest allowed choice*
- seed 1010 [event] Walk on — *event: the safest allowed choice*
- seed 1010 [event] Walk on — *event: the safest allowed choice*
- seed 1010 [event] Walk on — *event: the safest allowed choice*
- seed 1010 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1010 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 4*
- seed 1010 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 15*
- seed 1010 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 25, take the -5 Heat Site*
- seed 1010 [raid] spread from home outward (default): projected CELL HOLDS, home 45 -> 45, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *raid: best exact projection (home 45 after)*
- seed 1010 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1010 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1010 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1010 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1010 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1010 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *hq: claim for 30 Schematics (53 held)*
- seed 1010 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1010 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *hq: repair_home for 5 Schematics (82 held)*
- seed 1011 [combat] Brute Spin on your wheel (+); Jolt on your wheel (+); Mirror Flip on your wheel (+). RAM 6. End Turn: you deal 24, take 0 (Compliance Officer 50->26). Pointers: — *combat: value 75.0 (deal 24, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1011 [combat] Jolt on your wheel (+); Jolt on your wheel (+); Jolt on enemy wheel (+); Overdrive on your wheel (+). RAM 4. End Turn: you deal 26, take 0, 1 kill(s) (Complianc — *combat: value 1051.0 (deal 26, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1011 [combat] nudge enemy wheel +1; Fine Tune on your wheel (-); Overdrive on your wheel (+). RAM 2. End Turn: you deal 32, take 0 (Claims Adjuster 112->80). Pointers: Breake — *combat: value 76.0 (deal 32, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1011 [combat] Fine Tune on enemy wheel (+); Fine Tune on your wheel (-); nudge your wheel -1. RAM 2. End Turn: you deal 44, take 0 (Claims Adjuster 80->36). Pointers: Breaker — *combat: value 105.0 (deal 44, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1011 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1011 [node] TERMINAL at layer 2 (Heat +0) — *node: value 20.0 at 100% HP*
- seed 1011 [node] ELITE SERVER_RACK at layer 4 (Heat +2) — *node: value 43.8 at 100% HP*
- seed 1011 [node] MAINFRAME at layer 5 (Heat +0) — *node: value 60.0 at 95% HP*
- seed 1011 [reward] Card Fine Tune: Two +-1 nudges on one ring. — *reward: card fine_tune value 2.50*
- seed 1011 [reward] Firmware Leech into slot 2 (Shim 6): SHIM slice restores 1 RAM on Good or better. — *reward: firmware leech value 0.50*
- seed 1011 [reward] Card Fine Tune: Two +-1 nudges on one ring. — *reward: card fine_tune value 2.75*
- seed 1011 [reward] Firmware Counterstrike into slot 3 (Shim 6): DETOUR slice also deals 4 damage to the pointer target. — *reward: firmware counterstrike value 0.50*
- seed 1011 [event] Decline the terms — *event: the safest allowed choice*
- seed 1011 [event] Walk on — *event: the safest allowed choice*
- seed 1011 [event] Walk on — *event: the safest allowed choice*
- seed 1011 [event] Walk on — *event: the safest allowed choice*
- seed 1011 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1011 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 6*
- seed 1011 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 22*
- seed 1011 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 31, take the -5 Heat Site*
- seed 1011 [raid] spread from home outward (default): projected CELL HOLDS, home 45 -> 45, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *raid: best exact projection (home 45 after)*
- seed 1011 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 3, reached home 0, DOWN none, TAKEN none — *raid: best exact projection (home 50 after)*
- seed 1011 [shop] Card Spin Cycle for 71 Cycles: Spin a wheel 12 ticks. — *shop: buy card spin_cycle (value 4.25)*
- seed 1011 [shop] Firmware Static Coat for 84 Cycles: DEFRAG slice also grants 2 shield. (into slot 4, Shim 6) — *shop: buy firmware static_coat (value 0.50)*
- seed 1011 [shop] Firmware Bulkhead for 101 Cycles: DEFRAG and SANDBOX slices: output +50%. (into slot 5, Defrag 5) — *shop: buy firmware bulkhead (value 1.50)*
- seed 1011 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1011 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1011 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *hq: claim for 30 Schematics (47 held)*
- seed 1011 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1011 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *hq: repair_home for 5 Schematics (74 held)*
- seed 1012 [combat] Mirror Flip on enemy wheel (+); nudge your wheel +1. RAM 3. End Turn: you deal 12, take 0 (Collections Agent 40->28). Pointers: Breaker pointer 0: tick 5 -> Shi — *combat: value 65.0 (deal 12, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1012 [combat] Fine Tune on enemy wheel (+); Jolt on your wheel (+); Overdrive on your wheel (+). RAM 3. End Turn: you deal 28, take 0, 1 kill(s) (Collections Agent 28->0). Po — *combat: value 1053.0 (deal 28, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1012 [combat] Brute Spin on your wheel (+); Jolt on your wheel (+); Mirror Flip on enemy wheel (+). RAM 6. End Turn: you deal 24, take 0 (Billing Daemon 42->18). Pointers: Br — *combat: value 67.0 (deal 24, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1012 [combat] Jolt on your wheel (+); Fine Tune on enemy wheel (-). RAM 2. End Turn: you deal 18, take 0, 1 kill(s) (Billing Daemon 18->0). Pointers: Breaker pointer 0: tick  — *combat: value 1043.0 (deal 18, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1012 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1012 [node] ROUTER at layer 2 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1012 [node] ELITE SERVER_RACK at layer 4 (Heat +2) — *node: value 44.0 at 100% HP*
- seed 1012 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1012 [reward] Card Cleanse: Remove CORRUPTED from a chosen slice. — *reward: card cleanse value 4.00*
- seed 1012 [reward] Card Brute Spin: Spin a wheel 6 ticks. — *reward: card brute_spin value 4.00*
- seed 1012 [reward] Card Hot Patch: OVERCLOCK a chosen slice of your wheel: 1.5x on its next trigger, then it becomes CORRUPTED. — *reward: card hot_patch value 4.50*
- seed 1012 [reward] Card Spin Cycle: Spin a wheel 12 ticks. — *reward: card spin_cycle value 4.25*
- seed 1012 [event] Let it run (+1 Heat) (+1 Heat) — *event: the safest allowed choice*
- seed 1012 [event] Ghost past — *event: the safest allowed choice*
- seed 1012 [event] Purge it — *event: the safest allowed choice*
- seed 1012 [event] Walk on — *event: the safest allowed choice*
- seed 1012 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1012 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 6*
- seed 1012 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 14*
- seed 1012 [launch] Send Breaker 1 (R3) to Implant Provisioning Hub: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1012 [raid] everything on the home server: projected lost, home 50 -> 35, threats destroyed 0, reached home 2, DOWN t1_a, TAKEN none — *raid: best exact projection (home 35 after)*
- seed 1012 [raid] spread from home outward (default): projected lost, home 35 -> 25, threats destroyed 0, reached home 2, DOWN none, TAKEN t1_a — *raid: best exact projection (home 25 after)*
- seed 1012 [shop] Card Leech Worm for 50 Cycles: The enemy slice under your pointer gets a PARASITE (half output). Exhaust. — *shop: buy card leech_worm (value 2.50)*
- seed 1012 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1012 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1012 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1012 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1012 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *hq: claim for 30 Schematics (57 held)*
- seed 1012 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1012 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *hq: repair_home for 5 Schematics (91 held)*
- seed 1013 [combat] Brute Spin on your wheel (+); Fine Tune on enemy wheel (-); nudge your wheel -1; Mirror Flip on enemy wheel (+). RAM 6. End Turn: you deal 24, take 0 (Billing D — *combat: value 67.0 (deal 24, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1013 [combat] Brute Spin on your wheel (+); nudge your wheel +1. RAM 2. End Turn: you deal 18, take 0, 1 kill(s) (Billing Daemon 18->0). Pointers: Breaker pointer 0: tick 0 - — *combat: value 1043.0 (deal 18, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1013 [combat] nudge your wheel +1; Overdrive on your wheel (+); Brute Spin on enemy wheel (+). RAM 3. End Turn: you deal 36, take 0 (Collections Agent 40->4). Pointers: Break — *combat: value 65.0 (deal 36, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1013 [combat] Mirror Flip on your wheel (+). RAM 3. End Turn: you deal 4, take 0, 1 kill(s) (Collections Agent 4->0). Pointers: Breaker pointer 0: tick 26 -> Shim 6 (offset + — *combat: value 1029.0 (deal 4, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1013 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1013 [node] ROUTER at layer 5 (Heat +0) — *node: value 40.0 at 85% HP*
- seed 1013 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1013 [node] ROUTER at layer 2 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1013 [reward] Card Feather Touch: One +-1 nudge. — *reward: card feather_touch value 2.50*
- seed 1013 [reward] Card Cleanse: Remove CORRUPTED from a chosen slice. — *reward: card cleanse value 4.00*
- seed 1013 [reward] Skip this reward — *reward: nothing above the thresholds, skip*
- seed 1013 [reward] Card Fine Tune: Two +-1 nudges on one ring. — *reward: card fine_tune value 2.75*
- seed 1013 [event] Decline the terms — *event: the safest allowed choice*
- seed 1013 [event] Walk on — *event: the safest allowed choice*
- seed 1013 [event] Walk past — *event: the safest allowed choice*
- seed 1013 [event] Walk on — *event: the safest allowed choice*
- seed 1013 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1013 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 2*
- seed 1013 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 18*
- seed 1013 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 24, take the -5 Heat Site*
- seed 1013 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *raid: best exact projection (home 50 after)*
- seed 1013 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1013 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1013 [shop] Firmware Counterstrike for 93 Cycles: DETOUR slice also deals 4 damage to the pointer target. (into slot 5, Defrag 5) — *shop: buy firmware counterstrike (value 0.50)*
- seed 1013 [shop] Firmware Leech for 90 Cycles: SHIM slice restores 1 RAM on Good or better. (into slot 5, Defrag 5) — *shop: buy firmware leech (value 0.50)*
- seed 1013 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1013 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *hq: claim for 30 Schematics (45 held)*
- seed 1013 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1013 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *hq: repair_home for 5 Schematics (73 held)*
- seed 1014 [combat] nudge your wheel -1; nudge your wheel -1; nudge your wheel -1; Overdrive on your wheel (+). RAM 3. End Turn: you deal 36, take 3 (Collections Agent 40->4). Poin — *combat: value 56.6 (deal 36, take 3, 0 kill(s)) with 2-turn lookahead*
- seed 1014 [combat] Fine Tune on your wheel (-); Brute Spin on enemy wheel (+). RAM 3. End Turn: you deal 4, take 3, 1 kill(s) (Collections Agent 4->0). Pointers: Breaker pointer 0 — *combat: value 1024.8 (deal 4, take 3, 1 kill(s)) with 2-turn lookahead*
- seed 1014 [combat] Mirror Flip on your wheel (+); Jolt on your wheel (+); Overdrive on your wheel (+); nudge your wheel +1. RAM 5. End Turn: you deal 36, take 0 (Triage Unit 45->9 — *combat: value 70.0 (deal 36, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1014 [combat] Brute Spin on enemy wheel (+). RAM 2. End Turn: you deal 9, take 0, 1 kill(s) (Triage Unit 9->0). Pointers: Breaker pointer 0: tick 20 -> Shim 6 (offset +0, PER — *combat: value 1034.0 (deal 9, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1014 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1014 [node] ROUTER at layer 2 (Heat +0) — *node: value 40.0 at 90% HP*
- seed 1014 [node] ROUTER at layer 6 (Heat +0) — *node: value 40.0 at 60% HP*
- seed 1014 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1014 [reward] Card Flick: Spin a wheel 1 tick. — *reward: card flick value 3.00*
- seed 1014 [reward] Card Inner Drift: Move your inner ring 3 ticks. — *reward: card inner_drift value 2.50*
- seed 1014 [reward] Skip this reward — *reward: nothing above the thresholds, skip*
- seed 1014 [reward] Card Sanitize: Remove CORRUPTED from a chosen slice and gain 3 block. — *reward: card sanitize value 4.00*
- seed 1014 [event] Take the left route (+15 Cycles) (+15 Cycles) — *event: the safest allowed choice*
- seed 1014 [event] Trade gear (Asset: Flak Array) (-10 Cycles, Asset: Flak Array) — *event: the safest allowed choice*
- seed 1014 [event] Walk on — *event: the safest allowed choice*
- seed 1014 [event] Trade gear (Asset: Flak Array) (-10 Cycles, Asset: Flak Array) — *event: the safest allowed choice*
- seed 1014 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1014 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 2*
- seed 1014 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 19*
- seed 1014 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 22, take the -5 Heat Site*
- seed 1014 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *raid: best exact projection (home 50 after)*
- seed 1014 [shop] Firmware Nanite Mesh for 88 Cycles: HOTFIX slice: output +50%, and it cleanses itself after resolving. (into slot 5, Defrag 5) — *shop: buy firmware nanite_mesh (value 2.00)*
- seed 1014 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1014 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1014 [shop] Firmware Static Coat for 76 Cycles: DEFRAG slice also grants 2 shield. (into slot 6, Null) — *shop: buy firmware static_coat (value 0.50)*
- seed 1014 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1014 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *hq: claim for 30 Schematics (46 held)*
- seed 1014 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1014 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *hq: repair_home for 5 Schematics (77 held)*
- seed 1015 [combat] Brute Spin on your wheel (+); Jolt on your wheel (+); nudge your wheel -1; Overdrive on your wheel (+). RAM 4. End Turn: you deal 30, take 0 (Billing Daemon 42- — *combat: value 67.0 (deal 30, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1015 [combat] nudge your wheel +1; Brute Spin on your wheel (+). RAM 2. End Turn: you deal 12, take 0, 1 kill(s) (Billing Daemon 12->0). Pointers: Breaker pointer 0: tick 10  — *combat: value 1037.0 (deal 12, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1015 [combat] nudge your wheel -1; Overdrive on your wheel (+); nudge your wheel -1. RAM 2. End Turn: you deal 36, take 6 (Compliance Officer 50->14). Pointers: Breaker point — *combat: value 66.6 (deal 36, take 6, 0 kill(s)) with 2-turn lookahead*
- seed 1015 [combat] Fine Tune on your wheel (-); nudge your wheel -1. RAM 1. End Turn: you deal 14, take 0, 1 kill(s) (Compliance Officer 14->0). Pointers: Breaker pointer 0: tick  — *combat: value 1039.0 (deal 14, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1015 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1015 [node] ROUTER at layer 2 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1015 [node] ROUTER at layer 3 (Heat +0) — *node: value 40.0 at 90% HP*
- seed 1015 [node] MAINFRAME at layer 5 (Heat +0) — *node: value 60.0 at 85% HP*
- seed 1015 [reward] Card Mirror Flip: Flip a wheel. Blocked while the target has resistance. — *reward: card mirror_flip value 2.25*
- seed 1015 [reward] Firmware Patch+ into slot 2 (Shim 6): Slice output +50%. — *reward: firmware patch_plus value 5.00*
- seed 1015 [reward] Card Flick: Spin a wheel 1 tick. — *reward: card flick value 3.00*
- seed 1015 [reward] Firmware Overvolt into slot 3 (Shim 6): SHIM and OVERFLOW slices: output +25%. — *reward: firmware overvolt value 2.50*
- seed 1015 [event] Walk on — *event: the safest allowed choice*
- seed 1015 [event] Take the left route (+15 Cycles) (+15 Cycles) — *event: the safest allowed choice*
- seed 1015 [event] Walk on — *event: the safest allowed choice*
- seed 1015 [event] Leave it — *event: the safest allowed choice*
- seed 1015 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1015 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 2*
- seed 1015 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 8*
- seed 1015 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 16, take the -5 Heat Site*
- seed 1015 [raid] everything on the home server: projected lost, home 50 -> 35, threats destroyed 2, reached home 2, DOWN none, TAKEN none — *raid: best exact projection (home 35 after)*
- seed 1015 [shop] Card Heavy Spin for 65 Cycles: Spin a wheel 9 ticks. — *shop: buy card heavy_spin (value 4.00)*
- seed 1015 [shop] Firmware Recycler for 96 Cycles: The NULL slice restores 2 RAM when it resolves. (into slot 5, Defrag 5) — *shop: buy firmware recycler (value 0.50)*
- seed 1015 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1015 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1015 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1015 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1015 [hq] Scrub Heat for 25 Schematics (Heat now 18) — *hq: scrub for 25 Schematics (95 held)*
- seed 1015 [hq] Scrub Heat for 35 Schematics (Heat now 13) — *hq: scrub for 35 Schematics (70 held)*
- seed 1016 [combat] Overdrive on your wheel (+); Jolt on enemy wheel (+). RAM 2. End Turn: you deal 36, take 0 (Dosage Dispenser 38->2). Pointers: Breaker pointer 0: tick 0 -> Over — *combat: value 63.0 (deal 36, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1016 [combat] Brute Spin on enemy wheel (+); Fine Tune on your wheel (+). RAM 3. End Turn: you deal 2, take 0, 1 kill(s) (Dosage Dispenser 2->0). Pointers: Breaker pointer 0: — *combat: value 1027.0 (deal 2, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1016 [combat] Fine Tune on your wheel (+). RAM 1. End Turn: you deal 24, take 0 (Dosage Dispenser 38->14). Pointers: Breaker pointer 0: tick 0 -> Overflow 12 (offset +0, PERF — *combat: value 63.0 (deal 24, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1016 [combat] Overdrive on your wheel (+); nudge your wheel +1. RAM 1. End Turn: you deal 14, take 0, 1 kill(s) (Dosage Dispenser 14->0). Pointers: Breaker pointer 0: tick 29 — *combat: value 1039.0 (deal 14, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1016 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1016 [node] ROUTER at layer 3 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1016 [node] ELITE SERVER_RACK at layer 4 (Heat +2) — *node: value 44.0 at 100% HP*
- seed 1016 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1016 [reward] Card Encrypt: ENCRYPT a chosen slice: it absorbs the next status. — *reward: card encrypt value 4.25*
- seed 1016 [reward] Firmware Bulkhead into slot 2 (Shim 6): DEFRAG and SANDBOX slices: output +50%. — *reward: firmware bulkhead value 1.50*
- seed 1016 [reward] Card Shatter: Breach the target Hub for 1 turn and strip 1 resistance. — *reward: card shatter value 2.25*
- seed 1016 [reward] Firmware Patch+ into slot 2 (Shim 6): Slice output +50%. — *reward: firmware patch_plus value 5.00*
- seed 1016 [event] Decline the terms — *event: the safest allowed choice*
- seed 1016 [event] Walk on — *event: the safest allowed choice*
- seed 1016 [event] Purge it — *event: the safest allowed choice*
- seed 1016 [event] Walk on — *event: the safest allowed choice*
- seed 1016 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1016 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 5*
- seed 1016 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 19*
- seed 1016 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 29, take the -5 Heat Site*
- seed 1016 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *raid: best exact projection (home 50 after)*
- seed 1016 [shop] Card Whirl for 62 Cycles: Spin a wheel 7 ticks. — *shop: buy card whirl (value 4.00)*
- seed 1016 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1016 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1016 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1016 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1016 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *hq: claim for 30 Schematics (57 held)*
- seed 1016 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1016 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *hq: repair_home for 5 Schematics (69 held)*
- seed 1017 [combat] Mirror Flip on your wheel (+); nudge your wheel +1; Jolt on enemy wheel (+). RAM 4. End Turn: you deal 24, take 0 (Triage Unit 45->21). Pointers: Breaker pointe — *combat: value 42.0 (deal 24, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1017 [combat] Brute Spin on enemy wheel (+); nudge your wheel +1; Overdrive on your wheel (+); Fine Tune on enemy wheel (+). RAM 4. End Turn: you deal 18, take 0 (Triage Unit — *combat: value 46.0 (deal 18, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1017 [combat] Play nothing, end the turn. RAM 0. End Turn: you deal 3, take 0, 1 kill(s) (Triage Unit 3->0). Pointers: Breaker pointer 0: tick 29 -> Overflow 12 (offset -1, G — *combat: value 1028.0 (deal 3, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1017 [combat] Brute Spin on your wheel (+); Jolt on your wheel (+); Mirror Flip on your wheel (+). RAM 6. End Turn: you deal 24, take 0 (Billing Daemon 42->18). Pointers: Bre — *combat: value 61.4 (deal 24, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1017 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1017 [node] ROUTER at layer 2 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1017 [node] ROUTER at layer 4 (Heat +0) — *node: value 40.0 at 88% HP*
- seed 1017 [node] MAINFRAME at layer 5 (Heat +0) — *node: value 60.0 at 88% HP*
- seed 1017 [reward] Card Ring Tap: Two +-1 nudges on your inner ring. — *reward: card ring_tap value 2.50*
- seed 1017 [reward] Card Snap: Move your outer ring to the nearest slice centre (Perfect). — *reward: card snap value 2.00*
- seed 1017 [reward] Skip this reward — *reward: nothing above the thresholds, skip*
- seed 1017 [reward] Firmware Coolant Loop into slot 2 (Shim 6): Once per combat, a Perfect on this slice lowers Heat by 1. — *reward: firmware coolant_loop value 0.50*
- seed 1017 [event] Walk on — *event: the safest allowed choice*
- seed 1017 [event] Walk on — *event: the safest allowed choice*
- seed 1017 [event] Decline the terms — *event: the safest allowed choice*
- seed 1017 [event] Strip it for parts (+25 Cycles, +2 Heat) (+25 Cycles, +2 Heat) — *event: the safest allowed choice*
- seed 1017 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1017 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 4*
- seed 1017 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 11*
- seed 1017 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 25, take the -5 Heat Site*
- seed 1017 [raid] spread from home outward (default): projected lost, home 50 -> 35, threats destroyed 0, reached home 2, DOWN none, TAKEN none — *raid: best exact projection (home 35 after)*
- seed 1017 [raid] spread from home outward (default): projected lost, home 35 -> 30, threats destroyed 1, reached home 1, DOWN none, TAKEN none — *raid: best exact projection (home 30 after)*
- seed 1017 [shop] Card Micro-Adjust for 71 Cycles: Two +-1 nudges. Exhaust. — *shop: buy card micro_adjust (value 3.00)*
- seed 1017 [shop] Firmware Patch+ for 149 Cycles: Slice output +50%. (into slot 5, Defrag 5) — *shop: buy firmware patch_plus (value 5.00)*
- seed 1017 [shop] Firmware Nanite Mesh for 148 Cycles: HOTFIX slice: output +50%, and it cleanses itself after resolving. (into slot 6, Null) — *shop: buy firmware nanite_mesh (value 2.00)*
- seed 1017 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1017 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1017 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1017 [hq] Scrub Heat for 25 Schematics (Heat now 16) — *hq: scrub for 25 Schematics (67 held)*
- seed 1017 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1018 [combat] Play nothing, end the turn. RAM 0. End Turn: you deal 24, take 0 (Collections Agent 40->16). Pointers: Breaker pointer 0: tick 0 -> Overflow 12 (offset +0, PERF — *combat: value 60.8 (deal 24, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1018 [combat] Jolt on your wheel (+); Fine Tune on your wheel (+). RAM 2. End Turn: you deal 16, take 3, 1 kill(s) (Collections Agent 16->0). Pointers: Breaker pointer 0: tic — *combat: value 1036.8 (deal 16, take 3, 1 kill(s)) with 2-turn lookahead*
- seed 1018 [combat] Fine Tune on your wheel (+); Jolt on your wheel (+); Mirror Flip on your wheel (+). RAM 5. End Turn: you deal 24, take 0 (Dosage Dispenser 38->14). Pointers: Br — *combat: value 63.0 (deal 24, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1018 [combat] Brute Spin on your wheel (+); nudge your wheel -1; Overdrive on your wheel (+). RAM 3. End Turn: you deal 14, take 0, 1 kill(s) (Dosage Dispenser 14->0). Pointe — *combat: value 1039.0 (deal 14, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1018 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1018 [node] ELITE ROUTER at layer 3 (Heat +1) — *node: value 27.0 at 95% HP*
- seed 1018 [node] MAINFRAME at layer 5 (Heat +0) — *node: value 60.0 at 90% HP*
- seed 1018 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1018 [reward] Card Whirl: Spin a wheel 7 ticks. — *reward: card whirl value 4.00*
- seed 1018 [reward] Firmware Barbed Wire into slot 2 (Shim 6): DEFRAG slice also deals 2 damage to the pointer target. — *reward: firmware barbed_wire value 0.50*
- seed 1018 [reward] Card Twist: Spin a wheel 4 ticks. — *reward: card twist value 3.00*
- seed 1018 [reward] Card Inner Drift: Move your inner ring 3 ticks. — *reward: card inner_drift value 2.50*
- seed 1018 [event] Walk on — *event: the safest allowed choice*
- seed 1018 [event] Scrub your traces (-2 Heat) (-2 Heat) — *event: the safest allowed choice*
- seed 1018 [event] Walk on — *event: the safest allowed choice*
- seed 1018 [event] Walk on — *event: the safest allowed choice*
- seed 1018 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1018 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 5*
- seed 1018 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 10*
- seed 1018 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 17, take the -5 Heat Site*
- seed 1018 [shop] Card Whirl for 61 Cycles: Spin a wheel 7 ticks. — *shop: buy card whirl (value 4.00)*
- seed 1018 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1018 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1018 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1018 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1018 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1018 [hq] Scrub Heat for 25 Schematics (Heat now 20) — *hq: scrub for 25 Schematics (93 held)*
- seed 1018 [hq] Scrub Heat for 35 Schematics (Heat now 15) — *hq: scrub for 35 Schematics (68 held)*
- seed 1019 [combat] Jolt on your wheel (+); Overdrive on your wheel (+); nudge your wheel +1; Fine Tune on enemy wheel (+). RAM 3. End Turn: you deal 33, take 0 (Billing Daemon 42- — *combat: value 67.0 (deal 33, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1019 [combat] nudge your wheel +1; Brute Spin on your wheel (+). RAM 2. End Turn: you deal 9, take 0, 1 kill(s) (Billing Daemon 9->0). Pointers: Breaker pointer 0: tick 10 -> — *combat: value 1034.0 (deal 9, take 0, 1 kill(s)) with 2-turn lookahead*
- seed 1019 [combat] Jolt on your wheel (+); Fine Tune on your wheel (+); Brute Spin on enemy wheel (+); Overdrive on your wheel (+). RAM 5. End Turn: you deal 64, take 0 (Claims Ad — *combat: value 84.0 (deal 64, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1019 [combat] nudge enemy wheel -1. RAM 0. End Turn: you deal 20, take 0 (Claims Adjuster 48->28). Pointers: Breaker pointer 0: tick 5 -> Shim 6 (offset +0, PERFECT); Claims  — *combat: value 68.8 (deal 20, take 0, 0 kill(s)) with 2-turn lookahead*
- seed 1019 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1019 [node] ROUTER at layer 4 (Heat +0) — *node: value 40.0 at 95% HP*
- seed 1019 [node] ROUTER at layer 1 (Heat +0) — *node: value 40.0 at 100% HP*
- seed 1019 [node] ROUTER at layer 2 (Heat +0) — *node: value 40.0 at 85% HP*
- seed 1019 [reward] Card Jolt: Spin a wheel 3 ticks. — *reward: card jolt value 3.00*
- seed 1019 [reward] Card Double Jam: Nudge an enemy wheel +-1 twice, ignoring resistance. — *reward: card double_jam value 2.75*
- seed 1019 [reward] Firmware Coolant Loop into slot 2 (Shim 6): Once per combat, a Perfect on this slice lowers Heat by 1. — *reward: firmware coolant_loop value 0.50*
- seed 1019 [reward] Card Tap Tap: Three +-1 nudges on one ring. — *reward: card tap_tap value 2.75*
- seed 1019 [event] Walk on — *event: the safest allowed choice*
- seed 1019 [event] Scrub your traces (-2 Heat) (-2 Heat) — *event: the safest allowed choice*
- seed 1019 [event] Scrub your traces (-2 Heat) (-2 Heat) — *event: the safest allowed choice*
- seed 1019 [event] Take the left route (+15 Cycles) (+15 Cycles) — *event: the safest allowed choice*
- seed 1019 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *launch: expand the map, tier 1*
- seed 1019 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 2*
- seed 1019 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *launch: Exploit Site at Heat 8*
- seed 1019 [launch] Send Breaker 1 (R3) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *launch: Heat 31, take the -5 Heat Site*
- seed 1019 [raid] spread from home outward (default): projected CELL HOLDS, home 45 -> 45, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *raid: best exact projection (home 45 after)*
- seed 1019 [raid] spread from home outward (default): projected lost, home 45 -> 39, threats destroyed 1, reached home 1, DOWN t1_a, TAKEN none — *raid: best exact projection (home 39 after)*
- seed 1019 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1019 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1019 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1019 [shop] Leave (default: remove the Bug card first if affordable) — *shop: nothing worth the Cycles, leave*
- seed 1019 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1019 [hq] Done at HQ: launch the next netrun now — *hq: done, launch*
- seed 1019 [hq] Scrub Heat for 25 Schematics (Heat now 18) — *hq: scrub for 25 Schematics (111 held)*
- seed 1019 [hq] Scrub Heat for 35 Schematics (Heat now 13) — *hq: scrub for 35 Schematics (86 held)*

## Run logs

### seed 1000
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 3 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 53: Breaker 2 R24 T1 scrub_records -> COMPLETED, Heat 82, Exploits 2, home 50/50, Schematics 91, armory 6
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 1 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 2 turns, HP 60 -> 60
    run 54: Breaker 1 R28 T1 scrub_records -> COMPLETED, Heat 82, Exploits 2, home 50/50, Schematics 118, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 55: Breaker 2 R25 T1 scrub_records -> COMPLETED, Heat 86, Exploits 2, home 50/50, Schematics 156, armory 6
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 1 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 56: Breaker 1 R29 T1 scrub_records -> COMPLETED, Heat 82, Exploits 2, home 50/50, Schematics 193, armory 6
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 57: Breaker 2 R26 T1 scrub_records -> COMPLETED, Heat 77, Exploits 2, home 50/50, Schematics 57, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 1 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 58: Breaker 1 R30 T1 scrub_records -> COMPLETED, Heat 74, Exploits 2, home 50/50, Schematics 82, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 59: Breaker 2 R27 T1 scrub_records -> COMPLETED, Heat 77, Exploits 2, home 50/50, Schematics 116, armory 6
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 60: Breaker 1 R31 T1 scrub_records -> COMPLETED, Heat 73, Exploits 2, home 50/50, Schematics 155, armory 6
### seed 1001
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 53: Breaker 3 R21 T1 scrub_records -> COMPLETED, Heat 73, Exploits 3, home 50/50, Schematics 84, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 3 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 54: Breaker 4 R18 T1 scrub_records -> COMPLETED, Heat 73, Exploits 3, home 50/50, Schematics 120, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 4 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 55: Breaker 3 R22 T1 scrub_records -> COMPLETED, Heat 65, Exploits 3, home 50/50, Schematics 158, armory 6
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 56: Breaker 4 R19 T1 scrub_records -> COMPLETED, Heat 64, Exploits 3, home 50/50, Schematics 192, armory 6
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 57: Breaker 3 R23 T1 scrub_records -> COMPLETED, Heat 58, Exploits 3, home 50/50, Schematics 40, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 58
      FIGHT won vs claims_adjuster: 1 turns, HP 58 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 58: Breaker 4 R20 T1 scrub_records -> COMPLETED, Heat 61, Exploits 3, home 50/50, Schematics 80, armory 6
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 59: Breaker 3 R24 T1 scrub_records -> COMPLETED, Heat 57, Exploits 3, home 50/50, Schematics 104, armory 6
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 60: Breaker 4 R21 T1 scrub_records -> COMPLETED, Heat 58, Exploits 3, home 50/50, Schematics 143, armory 6
### seed 1002
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 17: Breaker 2 R6 T1 scrub_records -> COMPLETED, Heat 26, Exploits 2, home 50/50, Schematics 94, armory 6
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 1 turns, HP 60 -> 50
      FIGHT won vs claims_adjuster: 2 turns, HP 50 -> 54
      FIGHT won vs compliance_officer: 2 turns, HP 54 -> 58
      FIGHT won vs triage_unit: 2 turns, HP 58 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 18: Breaker 1 R10 T1 scrub_records -> COMPLETED, Heat 20, Exploits 2, home 50/50, Schematics 133, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 19: Breaker 2 R7 T1 scrub_records -> COMPLETED, Heat 10, Exploits 2, home 50/50, Schematics 63, armory 6
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 54
      FIGHT won vs dosage_dispenser: 1 turns, HP 54 -> 56
      FIGHT won vs account_manager: 3 turns, HP 56 -> 60
    run 20: Breaker 1 R11 T1 scrub_records -> COMPLETED, Heat 8, Exploits 2, home 50/50, Schematics 91, armory 6
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 21: Breaker 2 R8 T1 t1_b -> COMPLETED, Heat 8, Exploits 2, home 50/50, Schematics 132, armory 6
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 57
      FIGHT won vs account_manager: 3 turns, HP 57 -> 60
    run 22: Breaker 1 R12 T1 t1_c -> COMPLETED, Heat 0, Exploits 2, home 50/50, Schematics 150, armory 6
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 3 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 5 turns, HP 60 -> 60
    run 23: Breaker 1 R13 T2 t2_virus -> COMPLETED, Heat 10, Exploits 3, home 50/50, Schematics 195, armory 6
      FIGHT won vs collections_agent: 3 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 3 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 3 turns, HP 60 -> 48
      FIGHT won vs dosage_dispenser: 3 turns, HP 48 -> 58
      FIGHT won vs compliance_officer: 3 turns, HP 58 -> 60
      FIGHT won vs billing_daemon: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 7 turns, HP 60 -> 60
    run 24: Breaker 1 R14 T3 t3_b -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 153, armory 6
      boss loadout: R15 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,brute_spin,hot_patch,jolt,jolt,overdrive,gear_mesh | daemons zero_day,kernel_sync,botnet_seed,clean_signal,scrubber,adrenal_loop,cold_exit,field_medic | firmware ,patch_plus,patch_plus,overvolt,coolant_loop,recycler
      FIGHT won vs renewal_engine: 24 turns, HP 60 -> 42
    run 25: Breaker 1 R15 T4 the_genome_core -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 172, armory 6
### seed 1003
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 48: Breaker 1 R25 T1 scrub_records -> COMPLETED, Heat 46, Exploits 3, home 50/50, Schematics 193, armory 6
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 49: Breaker 2 R22 T1 scrub_records -> COMPLETED, Heat 36, Exploits 3, home 50/50, Schematics 67, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 50: Breaker 1 R26 T1 scrub_records -> COMPLETED, Heat 34, Exploits 3, home 50/50, Schematics 87, armory 6
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 51: Breaker 2 R23 T1 scrub_records -> COMPLETED, Heat 29, Exploits 3, home 50/50, Schematics 124, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 52: Breaker 1 R27 T1 scrub_records -> COMPLETED, Heat 28, Exploits 3, home 50/50, Schematics 164, armory 6
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 53: Breaker 2 R24 T1 scrub_records -> COMPLETED, Heat 22, Exploits 3, home 50/50, Schematics 205, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 4 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 54: Breaker 1 R28 T1 scrub_records -> COMPLETED, Heat 10, Exploits 3, home 50/50, Schematics 68, armory 6
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 55: Breaker 2 R25 T1 scrub_records -> COMPLETED, Heat 3, Exploits 3, home 50/50, Schematics 103, armory 6
      FIGHT won vs billing_daemon: 4 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 8 turns, HP 60 -> 51
      FIGHT won vs billing_daemon: 2 turns, HP 51 -> 59
      FIGHT won vs account_manager: 9 turns, HP 59 -> 60
    run 56: Breaker 1 R29 T3 t3_b -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 197, armory 6
      boss loadout: R30 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,flick,snap,brute_spin,sanitize,double_jam,leech_worm | daemons cold_exit,adrenal_loop,zero_day,idle_armor,field_medic,tuning_fork,log_wiper,fail_forward,scrubber,warm_boot,shield_cache,clean_signal,bounty_code | firmware ,overvolt,siphon,leech,bulkhead,patch_plus
      FIGHT won vs renewal_engine: 46 turns, HP 60 -> 47
    run 57: Breaker 1 R30 T4 the_genome_core -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 215, armory 6
### seed 1004
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 40
      FIGHT won vs billing_daemon: 3 turns, HP 40 -> 46
      FIGHT won vs care_swarm: 2 turns, HP 46 -> 49
      FIGHT won vs claims_adjuster: 4 turns, HP 49 -> 49
      FIGHT won vs account_manager: 8 turns, HP 49 -> 60
    run 45: Breaker 2 R20 T3 burn_the_ledger -> COMPLETED, Heat 89, Exploits 3, home 50/50, Schematics 239, armory 6
      FIGHT won vs collections_agent: 3 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 4 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 6 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 4 turns, HP 60 -> 39
      FIGHT won vs recall_unit: 8 turns, HP 39 -> 44
      FIGHT won vs account_manager: 7 turns, HP 44 -> 56
    run 46: Breaker 1 R24 T3 burn_the_ledger -> COMPLETED, Heat 67, Exploits 3, home 50/50, Schematics 360, armory 6
      FIGHT won vs billing_daemon: 4 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 3 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 3 turns, HP 60 -> 55
      FIGHT won vs recall_unit: 8 turns, HP 55 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 52
      FIGHT won vs account_manager: 7 turns, HP 52 -> 59
    run 47: Breaker 2 R21 T3 burn_the_ledger -> COMPLETED, Heat 72, Exploits 3, home 50/50, Schematics 219, armory 6
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 56
      FIGHT won vs dosage_dispenser: 2 turns, HP 56 -> 60
      FIGHT won vs dosage_dispenser: 3 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 9 turns, HP 60 -> 60
    run 48: Breaker 1 R25 T3 burn_the_ledger -> COMPLETED, Heat 49, Exploits 3, home 50/50, Schematics 284, armory 6
      FIGHT won vs billing_daemon: 3 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 3 turns, HP 60 -> 33
      FIGHT won vs recall_unit: 7 turns, HP 33 -> 47
      FIGHT won vs recall_unit: 8 turns, HP 47 -> 60
      FIGHT won vs compliance_officer: 4 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 7 turns, HP 60 -> 56
    run 49: Breaker 2 R22 T3 burn_the_ledger -> COMPLETED, Heat 50, Exploits 3, home 50/50, Schematics 106, armory 6
      FIGHT won vs collections_agent: 3 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 3 turns, HP 60 -> 50
      FIGHT won vs billing_daemon: 3 turns, HP 50 -> 60
      FIGHT won vs claims_adjuster: 3 turns, HP 60 -> 22
      FIGHT won vs care_swarm: 1 turns, HP 22 -> 25
      FIGHT won vs account_manager: 8 turns, HP 25 -> 27
    run 50: Breaker 1 R26 T3 burn_the_ledger -> COMPLETED, Heat 24, Exploits 3, home 50/50, Schematics 217, armory 6
      FIGHT won vs triage_unit: 3 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 3 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 4 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 4 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 4 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 3 turns, HP 60 -> 54
      FIGHT won vs account_manager: 9 turns, HP 54 -> 60
    run 51: Breaker 2 R23 T3 burn_the_ledger -> COMPLETED, Heat 32, Exploits 3, home 50/50, Schematics 311, armory 6
      FIGHT won vs billing_daemon: 3 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 8 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 7 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 7 turns, HP 60 -> 53
    run 52: Breaker 1 R27 T3 burn_the_ledger -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 147, armory 6
      boss loadout: R28 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,flip_switch,brute_spin,cleanse,shatter,ring_tap,encrypt | daemons log_wiper,adrenal_loop,rack_skimmer,kernel_sync,scrubber,cascade,warm_boot,field_medic,cold_exit,idle_armor,clean_signal,fail_forward,tuning_fork | firmware ,leech,patch_plus,skimmer,barbed_wire,recycler
      FIGHT won vs renewal_engine: 27 turns, HP 60 -> 41
    run 53: Breaker 1 R28 T4 the_genome_core -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 167, armory 6
### seed 1005
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 29: Breaker 2 R12 T1 scrub_records -> COMPLETED, Heat 23, Exploits 2, home 50/50, Schematics 116, armory 6
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 30: Breaker 1 R16 T1 scrub_records -> COMPLETED, Heat 20, Exploits 2, home 50/50, Schematics 155, armory 6
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 4 turns, HP 60 -> 59
      FIGHT won vs billing_daemon: 2 turns, HP 59 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 31: Breaker 2 R13 T1 scrub_records -> COMPLETED, Heat 6, Exploits 2, home 50/50, Schematics 47, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 32: Breaker 1 R17 T1 t1_b -> COMPLETED, Heat 0, Exploits 2, home 50/50, Schematics 82, armory 6
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 52
      FIGHT won vs compliance_officer: 2 turns, HP 52 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 54
    run 33: Breaker 2 R14 T1 t1_c -> COMPLETED, Heat 0, Exploits 2, home 50/50, Schematics 96, armory 6
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 58
      FIGHT won vs compliance_officer: 3 turns, HP 58 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 3 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 34: Breaker 1 R18 T2 t2_virus -> COMPLETED, Heat 10, Exploits 3, home 50/50, Schematics 157, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 54
      FIGHT won vs account_manager: 4 turns, HP 54 -> 60
    run 35: Breaker 2 R15 T1 scrub_records -> COMPLETED, Heat 4, Exploits 3, home 50/50, Schematics 183, armory 6
      FIGHT won vs collections_agent: 3 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 3 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 3 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 3 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 4 turns, HP 60 -> 60
      FIGHT won vs account_manager: 6 turns, HP 60 -> 51
    run 36: Breaker 1 R19 T3 t3_b -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 256, armory 6
      boss loadout: R20 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,spin_cycle,spin_cycle,double_jam,counter_spin,twist,shatter | daemons fail_forward,adrenal_loop,shield_cache,field_medic,tuning_fork,kernel_sync,log_wiper,clean_signal,cold_exit,scrubber,warm_boot | firmware ,patch_plus,leech,patch_plus,coolant_loop,patch_plus
      FIGHT won vs renewal_engine: 26 turns, HP 60 -> 12
    run 37: Breaker 1 R20 T4 the_genome_core -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 270, armory 6
### seed 1006
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 53: Breaker 2 R24 T1 scrub_records -> COMPLETED, Heat 58, Exploits 2, home 50/50, Schematics 187, armory 6
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 4 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 54: Breaker 1 R28 T1 scrub_records -> COMPLETED, Heat 57, Exploits 2, home 50/50, Schematics 229, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 55: Breaker 2 R25 T1 scrub_records -> COMPLETED, Heat 52, Exploits 2, home 50/50, Schematics 77, armory 6
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 56: Breaker 1 R29 T1 scrub_records -> COMPLETED, Heat 51, Exploits 2, home 50/50, Schematics 120, armory 6
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 57: Breaker 2 R26 T1 scrub_records -> COMPLETED, Heat 53, Exploits 2, home 50/50, Schematics 153, armory 6
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 58: Breaker 1 R30 T1 scrub_records -> COMPLETED, Heat 47, Exploits 2, home 50/50, Schematics 190, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 59: Breaker 2 R27 T1 scrub_records -> COMPLETED, Heat 45, Exploits 2, home 50/50, Schematics 223, armory 6
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 60: Breaker 1 R31 T1 scrub_records -> COMPLETED, Heat 40, Exploits 2, home 50/50, Schematics 61, armory 6
### seed 1007
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 47: Breaker 2 R21 T1 scrub_records -> COMPLETED, Heat 25, Exploits 2, home 50/50, Schematics 169, armory 6
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 1 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 48: Breaker 1 R25 T1 scrub_records -> COMPLETED, Heat 20, Exploits 2, home 50/50, Schematics 196, armory 6
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 49: Breaker 2 R22 T1 scrub_records -> COMPLETED, Heat 16, Exploits 2, home 50/50, Schematics 58, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 4 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 50: Breaker 1 R26 T1 scrub_records -> COMPLETED, Heat 8, Exploits 2, home 50/50, Schematics 101, armory 6
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 51: Breaker 2 R23 T1 t1_b -> COMPLETED, Heat 7, Exploits 2, home 50/50, Schematics 142, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 52: Breaker 1 R27 T1 t1_c -> COMPLETED, Heat 0, Exploits 2, home 50/50, Schematics 163, armory 6
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 4 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 53: Breaker 1 R28 T2 t2_virus -> COMPLETED, Heat 10, Exploits 3, home 50/50, Schematics 233, armory 6
      FIGHT won vs triage_unit: 3 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 6 turns, HP 60 -> 60
    run 54: Breaker 1 R29 T3 t3_b -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 120, armory 6
      boss loadout: R30 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,shatter,corrupt_packet,inner_snap,ratchet,backspin,ratchet | daemons adrenal_loop,rack_skimmer,log_wiper,static_field,cold_exit,clean_signal,zero_day,botnet_seed,field_medic,tuning_fork,scrubber,idle_armor,kernel_sync,fail_forward | firmware ,patch_plus,overvolt,patch_plus,barbed_wire,patch_plus
      FIGHT won vs renewal_engine: 25 turns, HP 60 -> 46
    run 55: Breaker 1 R30 T4 the_genome_core -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 137, armory 6
### seed 1008
      FIGHT won vs triage_unit: 1 turns, HP 55 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 26: Breaker 1 R14 T1 scrub_records -> COMPLETED, Heat 24, Exploits 2, home 50/50, Schematics 70, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 54
      FIGHT won vs dosage_dispenser: 1 turns, HP 54 -> 54
      FIGHT won vs triage_unit: 1 turns, HP 54 -> 54
      FIGHT won vs recall_unit: 3 turns, HP 54 -> 53
      FIGHT won vs compliance_officer: 2 turns, HP 53 -> 53
      FIGHT won vs account_manager: 4 turns, HP 53 -> 57
    run 27: Breaker 2 R11 T1 scrub_records -> COMPLETED, Heat 18, Exploits 2, home 50/50, Schematics 117, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 28: Breaker 1 R15 T1 scrub_records -> COMPLETED, Heat 14, Exploits 2, home 50/50, Schematics 156, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 57
      FIGHT won vs claims_adjuster: 2 turns, HP 57 -> 60
      FIGHT won vs claims_adjuster: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 29: Breaker 2 R12 T1 t1_b -> COMPLETED, Heat 3, Exploits 2, home 50/50, Schematics 75, armory 6
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 30: Breaker 1 R16 T1 t1_c -> COMPLETED, Heat 0, Exploits 2, home 50/50, Schematics 89, armory 6
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 4 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 5 turns, HP 60 -> 60
    run 31: Breaker 1 R17 T2 t2_virus -> COMPLETED, Heat 10, Exploits 3, home 50/50, Schematics 153, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 54
    run 32: Breaker 2 R13 T1 scrub_records -> COMPLETED, Heat 4, Exploits 3, home 50/50, Schematics 205, armory 6
      FIGHT won vs compliance_officer: 3 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 4 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 6 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 4 turns, HP 60 -> 60
      FIGHT won vs account_manager: 6 turns, HP 60 -> 60
    run 33: Breaker 1 R18 T3 t3_b -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 306, armory 6
      boss loadout: R19 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,counter_spin,spin_cycle,gear_shift,gear_mesh,jam,armor_plate | daemons adrenal_loop,shield_cache,field_medic,cold_exit,cascade,scrubber,botnet_seed,clean_signal,tuning_fork,log_wiper | firmware ,tracer,tracer,patch_plus,patch_plus,recycler
      FIGHT won vs renewal_engine: 46 turns, HP 60 -> 44
    run 34: Breaker 1 R19 T4 the_genome_core -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 325, armory 6
### seed 1009
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 58
      FIGHT won vs dosage_dispenser: 1 turns, HP 58 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 59
    run 9: Breaker 2 R2 T1 scrub_records -> COMPLETED, Heat 16, Exploits 2, home 50/50, Schematics 91, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 5 turns, HP 60 -> 60
    run 10: Breaker 1 R6 T1 scrub_records -> COMPLETED, Heat 12, Exploits 2, home 50/50, Schematics 43, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 56
      FIGHT won vs billing_daemon: 1 turns, HP 56 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 11: Breaker 2 R3 T1 scrub_records -> COMPLETED, Heat 11, Exploits 2, home 50/50, Schematics 82, armory 6
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 12: Breaker 1 R7 T1 scrub_records -> COMPLETED, Heat 12, Exploits 2, home 50/50, Schematics 108, armory 6
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 59
      FIGHT won vs triage_unit: 1 turns, HP 59 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 13: Breaker 2 R4 T1 t1_b -> COMPLETED, Heat 3, Exploits 2, home 50/50, Schematics 59, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 4 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 1 turns, HP 60 -> 54
      FIGHT won vs billing_daemon: 2 turns, HP 54 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 14: Breaker 1 R8 T1 t1_c -> COMPLETED, Heat 7, Exploits 2, home 45/50, Schematics 67, armory 6
      FIGHT won vs triage_unit: 3 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 53
      FIGHT won vs account_manager: 5 turns, HP 53 -> 60
    run 15: Breaker 1 R9 T2 t2_virus -> COMPLETED, Heat 10, Exploits 3, home 50/50, Schematics 131, armory 6
      FIGHT won vs compliance_officer: 3 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 4 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 6 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 3 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 7 turns, HP 60 -> 60
    run 16: Breaker 1 R10 T3 t3_b -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 124, armory 6
      boss loadout: R11 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,armor_plate,micro_adjust,counter_spin,jam,jam,fine_tune | daemons botnet_seed,scrubber,adrenal_loop,field_medic,bounty_code,clean_signal | firmware ,overvolt,tracer,patch_plus,bulkhead,patch_plus
      FIGHT won vs renewal_engine: 52 turns, HP 60 -> 9
    run 17: Breaker 1 R11 T4 the_genome_core -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 139, armory 6
### seed 1010
      FIGHT won vs billing_daemon: 2 turns, HP 47 -> 51
      FIGHT won vs recall_unit: 3 turns, HP 51 -> 57
      FIGHT won vs dosage_dispenser: 2 turns, HP 57 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 55
    run 37: Breaker 2 R16 T1 scrub_records -> COMPLETED, Heat 22, Exploits 2, home 50/50, Schematics 171, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 59
      FIGHT won vs claims_adjuster: 2 turns, HP 59 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 38: Breaker 1 R20 T1 scrub_records -> COMPLETED, Heat 13, Exploits 2, home 50/50, Schematics 66, armory 6
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 3 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 57
      FIGHT won vs triage_unit: 1 turns, HP 57 -> 59
      FIGHT won vs claims_adjuster: 2 turns, HP 59 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 39: Breaker 2 R17 T1 scrub_records -> COMPLETED, Heat 12, Exploits 2, home 50/50, Schematics 94, armory 6
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 40: Breaker 1 R21 T1 scrub_records -> COMPLETED, Heat 8, Exploits 2, home 50/50, Schematics 121, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 47
      FIGHT won vs triage_unit: 1 turns, HP 47 -> 49
      FIGHT won vs care_swarm: 1 turns, HP 49 -> 51
      FIGHT won vs account_manager: 3 turns, HP 51 -> 57
    run 41: Breaker 2 R18 T1 t1_b -> COMPLETED, Heat 5, Exploits 2, home 50/50, Schematics 146, armory 6
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 42: Breaker 1 R22 T1 t1_c -> COMPLETED, Heat 0, Exploits 2, home 50/50, Schematics 162, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 4 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 3 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 43: Breaker 1 R23 T2 t2_virus -> COMPLETED, Heat 10, Exploits 3, home 50/50, Schematics 233, armory 6
      FIGHT won vs dosage_dispenser: 3 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 4 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 5 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 3 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 6 turns, HP 60 -> 54
    run 44: Breaker 1 R24 T3 t3_b -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 192, armory 6
      boss loadout: R25 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,ratchet,heavy_spin,inner_drift,inner_drift,ratchet,encrypt | daemons adrenal_loop,field_medic,cascade,kernel_sync,zero_day,scrubber,fail_forward,clean_signal,salvager,tuning_fork,cold_exit,botnet_seed,warm_boot | firmware ,overvolt,patch_plus,overvolt,barbed_wire,patch_plus
      FIGHT won vs renewal_engine: 26 turns, HP 60 -> 47
    run 45: Breaker 1 R25 T4 the_genome_core -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 212, armory 6
### seed 1011
    run 52: Breaker 3 R17 T1 scrub_records -> COMPLETED, Heat 47, Exploits 3, home 50/50, Schematics 133, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 53: Breaker 4 R14 T1 scrub_records -> COMPLETED, Heat 48, Exploits 3, home 50/50, Schematics 170, armory 6
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 54: Breaker 3 R18 T1 scrub_records -> COMPLETED, Heat 45, Exploits 3, home 50/50, Schematics 194, armory 6
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 55: Breaker 4 R15 T1 scrub_records -> COMPLETED, Heat 39, Exploits 3, home 50/50, Schematics 46, armory 6
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 56: Breaker 3 R19 T1 scrub_records -> COMPLETED, Heat 40, Exploits 3, home 50/50, Schematics 70, armory 6
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 57: Breaker 4 R16 T1 scrub_records -> COMPLETED, Heat 41, Exploits 3, home 50/50, Schematics 99, armory 6
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 58: Breaker 3 R20 T1 scrub_records -> COMPLETED, Heat 41, Exploits 3, home 50/50, Schematics 125, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 59: Breaker 4 R17 T1 scrub_records -> COMPLETED, Heat 40, Exploits 3, home 50/50, Schematics 162, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 60: Breaker 3 R21 T1 scrub_records -> COMPLETED, Heat 40, Exploits 3, home 50/50, Schematics 188, armory 6
### seed 1012
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 42
      FIGHT won vs compliance_officer: 3 turns, HP 42 -> 42
      FIGHT won vs triage_unit: 2 turns, HP 42 -> 42
      FIGHT won vs dosage_dispenser: 2 turns, HP 42 -> 42
      FIGHT won vs account_manager: 7 turns, HP 42 -> 34
    run 5: Breaker 2 R0 T1 t1_c -> COMPLETED, Heat 31, Exploits 2, home 50/50, Schematics 34, armory 6
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 44
      FIGHT won vs recall_unit: 5 turns, HP 44 -> 40
      FIGHT won vs claims_adjuster: 3 turns, HP 40 -> 32
      FIGHT won vs claims_adjuster: 2 turns, HP 32 -> 32
      FIGHT won vs account_manager: 5 turns, HP 32 -> 32
    run 6: Breaker 1 R4 T2 t2_virus -> COMPLETED, Heat 41, Exploits 3, home 50/50, Schematics 98, armory 6
      FIGHT won vs compliance_officer: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 4 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 3 turns, HP 60 -> 48
      FIGHT won vs claims_adjuster: 4 turns, HP 48 -> 12
      FIGHT won vs recall_unit: 6 turns, HP 12 -> 12
      FIGHT won vs triage_unit: 3 turns, HP 12 -> 9
      FIGHT won vs account_manager: 8 turns, HP 9 -> 7
    run 7: Breaker 1 R5 T3 t3_b -> COMPLETED, Heat 37, Exploits 3, home 50/50, Schematics 129, armory 6
      FIGHT won vs triage_unit: 4 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 3 turns, HP 60 -> 57
      FIGHT won vs claims_adjuster: 4 turns, HP 57 -> 60
      FIGHT won vs dosage_dispenser: 4 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 6 turns, HP 60 -> 45
      FIGHT won vs account_manager: 6 turns, HP 45 -> 54
    run 8: Breaker 1 R6 T3 t3_c -> COMPLETED, Heat 34, Exploits 3, home 45/50, Schematics 142, armory 6
      FIGHT won vs billing_daemon: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 3 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 51
      FIGHT won vs recall_unit: 7 turns, HP 51 -> 60
      FIGHT won vs recall_unit: 6 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 6 turns, HP 60 -> 60
      FIGHT won vs account_manager: 7 turns, HP 60 -> 57
    run 9: Breaker 1 R7 T3 t3_core -> COMPLETED, Heat 28, Exploits 3, home 50/50, Schematics 142, armory 6
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 42
      FIGHT won vs dosage_dispenser: 2 turns, HP 42 -> 42
      FIGHT won vs collections_agent: 3 turns, HP 42 -> 30
      FIGHT won vs billing_daemon: 2 turns, HP 30 -> 30
      FIGHT won vs recall_unit: 5 turns, HP 30 -> 24
      FIGHT won vs account_manager: 6 turns, HP 24 -> 21
    run 10: Breaker 2 R1 T2 t2_d -> COMPLETED, Heat 27, Exploits 3, home 50/50, Schematics 100, armory 6
      FIGHT won vs triage_unit: 3 turns, HP 60 -> 56
      FIGHT won vs compliance_officer: 4 turns, HP 56 -> 60
      FIGHT won vs recall_unit: 7 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 7 turns, HP 60 -> 43
    run 11: Breaker 1 R8 T3 t3_d -> COMPLETED, Heat 27, Exploits 3, home 50/50, Schematics 165, armory 6
      FIGHT won vs compliance_officer: 3 turns, HP 60 -> 59
      FIGHT won vs care_swarm: 2 turns, HP 59 -> 57
      FIGHT won vs recall_unit: 7 turns, HP 57 -> 58
      FIGHT won vs collections_agent: 3 turns, HP 58 -> 60
      FIGHT won vs claims_adjuster: 4 turns, HP 60 -> 60
      FIGHT won vs account_manager: 7 turns, HP 60 -> 58
    run 12: Breaker 1 R9 T3 t3_e -> COMPLETED, Heat 15, Exploits 3, home 50/50, Schematics 172, armory 6
      boss loadout: R10 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,cleanse,brute_spin,hot_patch,spin_cycle,counter_spin,gear_shift | daemons zero_day,scrubber,idle_armor,adrenal_loop,tuning_fork,field_medic | firmware ,overvolt,siphon,coolant_loop,patch_plus,recycler
      FIGHT won vs renewal_engine: 51 turns, HP 60 -> 42
    run 13: Breaker 1 R10 T4 the_genome_core -> COMPLETED, Heat 9, Exploits 3, home 50/50, Schematics 85, armory 6
### seed 1013
    run 23: Breaker 2 R9 T1 scrub_records -> COMPLETED, Heat 21, Exploits 2, home 50/50, Schematics 117, armory 6
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 51
      FIGHT won vs billing_daemon: 2 turns, HP 51 -> 51
      FIGHT won vs recall_unit: 3 turns, HP 51 -> 51
      FIGHT won vs recall_unit: 3 turns, HP 51 -> 48
      FIGHT won vs care_swarm: 2 turns, HP 48 -> 45
      FIGHT won vs account_manager: 4 turns, HP 45 -> 45
    run 24: Breaker 1 R13 T1 scrub_records -> COMPLETED, Heat 17, Exploits 2, home 50/50, Schematics 154, armory 6
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 25: Breaker 2 R10 T1 scrub_records -> COMPLETED, Heat 12, Exploits 2, home 50/50, Schematics 63, armory 6
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 26: Breaker 1 R14 T1 scrub_records -> COMPLETED, Heat 10, Exploits 2, home 50/50, Schematics 87, armory 6
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 48
      FIGHT won vs recall_unit: 3 turns, HP 48 -> 48
      FIGHT won vs recall_unit: 3 turns, HP 48 -> 48
      FIGHT won vs recall_unit: 3 turns, HP 48 -> 47
      FIGHT won vs account_manager: 4 turns, HP 47 -> 47
    run 27: Breaker 2 R11 T1 scrub_records -> COMPLETED, Heat 9, Exploits 2, home 50/50, Schematics 114, armory 6
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 59
      FIGHT won vs collections_agent: 2 turns, HP 59 -> 59
      FIGHT won vs claims_adjuster: 2 turns, HP 59 -> 59
      FIGHT won vs claims_adjuster: 2 turns, HP 59 -> 59
      FIGHT won vs compliance_officer: 1 turns, HP 59 -> 60
      FIGHT won vs recall_unit: 4 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 28: Breaker 1 R15 T1 t1_b -> COMPLETED, Heat 6, Exploits 2, home 50/50, Schematics 154, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 54
      FIGHT won vs collections_agent: 2 turns, HP 54 -> 54
      FIGHT won vs care_swarm: 2 turns, HP 54 -> 51
      FIGHT won vs billing_daemon: 2 turns, HP 51 -> 51
      FIGHT won vs collections_agent: 2 turns, HP 51 -> 51
      FIGHT won vs account_manager: 3 turns, HP 51 -> 51
    run 29: Breaker 2 R12 T1 t1_c -> COMPLETED, Heat 5, Exploits 2, home 50/50, Schematics 156, armory 6
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 55
      FIGHT won vs claims_adjuster: 3 turns, HP 55 -> 60
      FIGHT won vs recall_unit: 4 turns, HP 60 -> 60
      FIGHT won vs account_manager: 5 turns, HP 60 -> 60
    run 30: Breaker 1 R16 T2 t2_virus -> COMPLETED, Heat 14, Exploits 3, home 50/50, Schematics 201, armory 6
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 5 turns, HP 60 -> 42
      FIGHT won vs claims_adjuster: 4 turns, HP 42 -> 47
      FIGHT won vs collections_agent: 3 turns, HP 47 -> 50
      FIGHT won vs account_manager: 7 turns, HP 50 -> 43
    run 31: Breaker 1 R17 T3 t3_b -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 175, armory 6
      boss loadout: R18 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,feather_touch,cleanse,fine_tune,feather_touch,spin_cycle,armor_plate | daemons kernel_sync,zero_day,log_wiper,scrubber,botnet_seed,tuning_fork,adrenal_loop,clean_signal | firmware ,leech,coolant_loop,tracer,bulkhead,recycler
      FIGHT won vs renewal_engine: 27 turns, HP 60 -> 56
    run 32: Breaker 1 R18 T4 the_genome_core -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 190, armory 6
### seed 1014
    run 20: Breaker 1 R11 T1 scrub_records -> COMPLETED, Heat 20, Exploits 2, home 50/50, Schematics 87, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 21: Breaker 2 R8 T1 scrub_records -> COMPLETED, Heat 19, Exploits 2, home 50/50, Schematics 109, armory 6
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 22: Breaker 1 R12 T1 scrub_records -> COMPLETED, Heat 16, Exploits 2, home 50/50, Schematics 135, armory 6
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 5 turns, HP 60 -> 60
    run 23: Breaker 2 R9 T1 scrub_records -> COMPLETED, Heat 12, Exploits 2, home 50/50, Schematics 58, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 55
      FIGHT won vs collections_agent: 2 turns, HP 55 -> 56
      FIGHT won vs recall_unit: 3 turns, HP 56 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 58
      FIGHT won vs account_manager: 4 turns, HP 58 -> 60
    run 24: Breaker 1 R13 T1 scrub_records -> COMPLETED, Heat 6, Exploits 2, home 50/50, Schematics 83, armory 6
      FIGHT won vs compliance_officer: 3 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 25: Breaker 2 R10 T1 t1_b -> COMPLETED, Heat 5, Exploits 2, home 50/50, Schematics 109, armory 6
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 59
    run 26: Breaker 1 R14 T1 t1_c -> COMPLETED, Heat 0, Exploits 2, home 50/50, Schematics 113, armory 6
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 4 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 56
      FIGHT won vs account_manager: 5 turns, HP 56 -> 60
    run 27: Breaker 1 R15 T2 t2_virus -> COMPLETED, Heat 10, Exploits 3, home 50/50, Schematics 161, armory 6
      FIGHT won vs compliance_officer: 3 turns, HP 60 -> 59
      FIGHT won vs care_swarm: 2 turns, HP 59 -> 49
      FIGHT won vs care_swarm: 2 turns, HP 49 -> 41
      FIGHT won vs triage_unit: 3 turns, HP 41 -> 51
      FIGHT won vs triage_unit: 4 turns, HP 51 -> 60
      FIGHT won vs account_manager: 6 turns, HP 60 -> 60
    run 28: Breaker 1 R16 T3 t3_b -> COMPLETED, Heat 2, Exploits 3, home 50/50, Schematics 103, armory 6
      boss loadout: R17 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,flick,inner_drift,sanitize,shatter,twist,spin_cycle | daemons adrenal_loop,cold_exit,kernel_sync,clean_signal,field_medic | firmware ,siphon,overvolt,patch_plus,coolant_loop,patch_plus
      FIGHT won vs renewal_engine: 26 turns, HP 60 -> 40
    run 29: Breaker 1 R17 T4 the_genome_core -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 118, armory 6
### seed 1015
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 57
    run 48: Breaker 1 R25 T1 scrub_records -> COMPLETED, Heat 22, Exploits 2, home 50/50, Schematics 221, armory 6
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 49: Breaker 2 R22 T1 scrub_records -> COMPLETED, Heat 14, Exploits 2, home 50/50, Schematics 92, armory 6
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 58
      FIGHT won vs compliance_officer: 2 turns, HP 58 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 55
      FIGHT won vs claims_adjuster: 1 turns, HP 55 -> 57
      FIGHT won vs billing_daemon: 1 turns, HP 57 -> 58
      FIGHT won vs dosage_dispenser: 2 turns, HP 58 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 50: Breaker 1 R26 T1 scrub_records -> COMPLETED, Heat 11, Exploits 2, home 50/50, Schematics 133, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 51: Breaker 2 R23 T1 scrub_records -> COMPLETED, Heat 8, Exploits 2, home 50/50, Schematics 167, armory 6
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 53
      FIGHT won vs recall_unit: 3 turns, HP 53 -> 59
      FIGHT won vs claims_adjuster: 2 turns, HP 59 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 52: Breaker 1 R27 T1 t1_b -> COMPLETED, Heat 7, Exploits 2, home 50/50, Schematics 217, armory 6
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 53: Breaker 2 R24 T1 t1_c -> COMPLETED, Heat 3, Exploits 2, home 50/50, Schematics 224, armory 6
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 55
      FIGHT won vs dosage_dispenser: 1 turns, HP 55 -> 56
      FIGHT won vs collections_agent: 2 turns, HP 56 -> 60
      FIGHT won vs recall_unit: 5 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 54: Breaker 1 R28 T2 t2_virus -> COMPLETED, Heat 10, Exploits 3, home 50/50, Schematics 278, armory 6
      FIGHT won vs billing_daemon: 3 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 3 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 7 turns, HP 60 -> 59
      FIGHT won vs recall_unit: 6 turns, HP 59 -> 58
      FIGHT won vs recall_unit: 6 turns, HP 58 -> 59
      FIGHT won vs account_manager: 7 turns, HP 59 -> 47
    run 55: Breaker 1 R29 T3 t3_b -> COMPLETED, Heat 1, Exploits 3, home 50/50, Schematics 195, armory 6
      boss loadout: R30 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,mirror_flip,flick,snap,hot_patch,heavy_spin,micro_adjust | daemons adrenal_loop,cascade,salvager,log_wiper,tuning_fork,warm_boot,bounty_code,rack_skimmer,clean_signal,cold_exit,idle_armor | firmware ,patch_plus,overvolt,patch_plus,static_coat,patch_plus
      FIGHT won vs renewal_engine: 35 turns, HP 60 -> 35
    run 56: Breaker 1 R30 T4 the_genome_core -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 216, armory 6
### seed 1016
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 47: Breaker 3 R10 T1 scrub_records -> COMPLETED, Heat 37, Exploits 3, home 50/50, Schematics 50, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 51
      FIGHT won vs compliance_officer: 1 turns, HP 51 -> 51
      FIGHT won vs claims_adjuster: 2 turns, HP 51 -> 51
      FIGHT won vs recall_unit: 3 turns, HP 51 -> 49
      FIGHT won vs claims_adjuster: 2 turns, HP 49 -> 41
      FIGHT won vs account_manager: 4 turns, HP 41 -> 41
    run 48: Breaker 4 R7 T1 scrub_records -> COMPLETED, Heat 36, Exploits 3, home 50/50, Schematics 89, armory 6
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 56
      FIGHT won vs recall_unit: 3 turns, HP 56 -> 56
      FIGHT won vs account_manager: 4 turns, HP 56 -> 60
    run 49: Breaker 3 R11 T1 scrub_records -> COMPLETED, Heat 33, Exploits 3, home 50/50, Schematics 117, armory 6
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 56
      FIGHT won vs collections_agent: 2 turns, HP 56 -> 56
      FIGHT won vs claims_adjuster: 2 turns, HP 56 -> 56
      FIGHT won vs billing_daemon: 2 turns, HP 56 -> 52
      FIGHT won vs claims_adjuster: 2 turns, HP 52 -> 52
      FIGHT won vs billing_daemon: 1 turns, HP 52 -> 45
      FIGHT won vs account_manager: 3 turns, HP 45 -> 45
    run 50: Breaker 4 R8 T1 scrub_records -> COMPLETED, Heat 30, Exploits 3, home 50/50, Schematics 145, armory 6
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 51: Breaker 3 R12 T1 scrub_records -> COMPLETED, Heat 29, Exploits 3, home 50/50, Schematics 176, armory 6
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 54
      FIGHT won vs care_swarm: 1 turns, HP 54 -> 48
      FIGHT won vs care_swarm: 1 turns, HP 48 -> 45
      FIGHT won vs recall_unit: 3 turns, HP 45 -> 45
      FIGHT won vs triage_unit: 2 turns, HP 45 -> 49
      FIGHT won vs billing_daemon: 2 turns, HP 49 -> 53
      FIGHT won vs account_manager: 3 turns, HP 53 -> 59
    run 52: Breaker 4 R9 T1 scrub_records -> COMPLETED, Heat 23, Exploits 3, home 50/50, Schematics 215, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 55
      FIGHT won vs care_swarm: 1 turns, HP 55 -> 57
      FIGHT won vs recall_unit: 4 turns, HP 57 -> 60
      FIGHT won vs recall_unit: 4 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 53: Breaker 3 R13 T1 scrub_records -> COMPLETED, Heat 12, Exploits 3, home 50/50, Schematics 75, armory 6
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 57
      FIGHT won vs triage_unit: 2 turns, HP 57 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 54
      FIGHT won vs triage_unit: 1 turns, HP 54 -> 56
      FIGHT won vs claims_adjuster: 2 turns, HP 56 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 54: Breaker 4 R10 T1 scrub_records -> COMPLETED, Heat 10, Exploits 3, home 50/50, Schematics 105, armory 6
      boss loadout: R14 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,leech_worm,micro_adjust,double_jam,gear_mesh,mirror_flip,jam | daemons zero_day,adrenal_loop,clean_signal,tuning_fork,scrubber | firmware ,siphon,siphon,siphon,bulkhead,recycler
      FIGHT won vs renewal_engine: 52 turns, HP 60 -> 18
    run 55: Breaker 3 R14 T4 the_genome_core -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 122, armory 6
### seed 1017
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 57
    run 24: Breaker 2 R9 T1 scrub_records -> COMPLETED, Heat 19, Exploits 3, home 50/50, Schematics 48, armory 6
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 25: Breaker 2 R10 T1 scrub_records -> COMPLETED, Heat 19, Exploits 3, home 50/50, Schematics 87, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 26: Breaker 1 R14 T1 scrub_records -> COMPLETED, Heat 21, Exploits 3, home 50/50, Schematics 126, armory 6
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 27: Breaker 2 R11 T1 scrub_records -> COMPLETED, Heat 21, Exploits 3, home 50/50, Schematics 167, armory 6
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 59
    run 28: Breaker 1 R15 T1 scrub_records -> COMPLETED, Heat 18, Exploits 3, home 50/50, Schematics 81, armory 6
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 29: Breaker 2 R12 T1 scrub_records -> COMPLETED, Heat 16, Exploits 3, home 50/50, Schematics 116, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 30: Breaker 1 R16 T1 scrub_records -> COMPLETED, Heat 12, Exploits 3, home 50/50, Schematics 153, armory 6
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 48
      FIGHT won vs care_swarm: 2 turns, HP 48 -> 36
      FIGHT won vs claims_adjuster: 4 turns, HP 36 -> 39
      FIGHT won vs recall_unit: 6 turns, HP 39 -> 51
      FIGHT won vs billing_daemon: 3 turns, HP 51 -> 60
      FIGHT won vs account_manager: 7 turns, HP 60 -> 60
    run 31: Breaker 1 R17 T3 t3_b -> COMPLETED, Heat 4, Exploits 3, home 50/50, Schematics 129, armory 6
      boss loadout: R18 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,ring_tap,snap,feather_touch,micro_adjust,ratchet,micro_adjust | daemons clean_signal,shield_cache,kernel_sync,adrenal_loop,warm_boot,zero_day,field_medic,salvager,cold_exit,log_wiper,idle_armor | firmware ,coolant_loop,overvolt,patch_plus,patch_plus,patch_plus
      FIGHT won vs renewal_engine: 25 turns, HP 60 -> 30
    run 32: Breaker 1 R18 T4 the_genome_core -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 147, armory 6
### seed 1018
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 4 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 30: Breaker 1 R16 T1 scrub_records -> COMPLETED, Heat 12, Exploits 2, home 50/50, Schematics 139, armory 6
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 4 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 31: Breaker 2 R13 T1 scrub_records -> COMPLETED, Heat 11, Exploits 2, home 50/50, Schematics 180, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 57
      FIGHT won vs compliance_officer: 2 turns, HP 57 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 32: Breaker 1 R17 T1 t1_b -> COMPLETED, Heat 6, Exploits 2, home 50/50, Schematics 70, armory 6
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 4 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 33: Breaker 2 R14 T1 t1_c -> COMPLETED, Heat 10, Exploits 2, home 45/50, Schematics 83, armory 6
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 5 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 3 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 6 turns, HP 60 -> 59
    run 34: Breaker 1 R18 T2 t2_virus -> COMPLETED, Heat 19, Exploits 3, home 50/50, Schematics 120, armory 6
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 52
      FIGHT won vs claims_adjuster: 2 turns, HP 52 -> 60
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 35: Breaker 2 R15 T1 scrub_records -> COMPLETED, Heat 17, Exploits 3, home 50/50, Schematics 168, armory 6
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 36: Breaker 1 R19 T1 scrub_records -> COMPLETED, Heat 5, Exploits 3, home 50/50, Schematics 59, armory 6
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 7 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 3 turns, HP 60 -> 58
      FIGHT won vs claims_adjuster: 4 turns, HP 58 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 51
      FIGHT won vs account_manager: 7 turns, HP 51 -> 60
    run 37: Breaker 1 R20 T3 t3_b -> COMPLETED, Heat 2, Exploits 3, home 50/50, Schematics 166, armory 6
      boss loadout: R21 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,whirl,twist,inner_drift,short_circuit,whirl,spin_cycle | daemons zero_day,cascade,scrubber,adrenal_loop,botnet_seed,field_medic,cold_exit,warm_boot,shield_cache | firmware ,skimmer,coolant_loop,overvolt,static_coat,recycler
      FIGHT won vs renewal_engine: 42 turns, HP 60 -> 59
    run 38: Breaker 1 R21 T4 the_genome_core -> COMPLETED, Heat 1, Exploits 3, home 50/50, Schematics 185, armory 6
### seed 1019
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 46: Breaker 1 R24 T1 scrub_records -> COMPLETED, Heat 24, Exploits 2, home 50/50, Schematics 186, armory 6
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 57
      FIGHT won vs recall_unit: 3 turns, HP 57 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 47: Breaker 2 R21 T1 scrub_records -> COMPLETED, Heat 17, Exploits 2, home 50/50, Schematics 48, armory 6
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 48: Breaker 1 R25 T1 scrub_records -> COMPLETED, Heat 10, Exploits 2, home 50/50, Schematics 85, armory 6
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 58
      FIGHT won vs claims_adjuster: 2 turns, HP 58 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 49: Breaker 2 R22 T1 scrub_records -> COMPLETED, Heat 6, Exploits 2, home 50/50, Schematics 122, armory 6
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 50: Breaker 1 R26 T1 t1_b -> COMPLETED, Heat 3, Exploits 2, home 50/50, Schematics 152, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 56
      FIGHT won vs account_manager: 3 turns, HP 56 -> 60
    run 51: Breaker 2 R23 T1 t1_c -> COMPLETED, Heat 0, Exploits 2, home 50/50, Schematics 169, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 52: Breaker 1 R27 T2 t2_virus -> COMPLETED, Heat 10, Exploits 3, home 50/50, Schematics 239, armory 6
      FIGHT won vs collections_agent: 3 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 3 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 4 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 3 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 6 turns, HP 60 -> 60
    run 53: Breaker 1 R28 T3 t3_b -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 140, armory 6
      boss loadout: R29 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,jolt,double_jam,tap_tap,whirl,overdrive,jam | daemons adrenal_loop,log_wiper,field_medic,kernel_sync,zero_day,feedback_loop,clean_signal,botnet_seed,scrubber,tuning_fork,shield_cache,warm_boot,cold_exit,bounty_code,idle_armor,cascade | firmware ,coolant_loop,patch_plus,patch_plus,bulkhead,recycler
      FIGHT won vs renewal_engine: 26 turns, HP 60 -> 58
    run 54: Breaker 1 R29 T4 the_genome_core -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 157, armory 6
