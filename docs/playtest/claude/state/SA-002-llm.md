# State playtest SA-002-llm — intermediate tier, persona strategist, ICE 0, breaker vs solace

Cost: $10.22 (4981 LLM calls). Option 0 of every menu = the built-in policy (greedy CombatBot).

| Seed | Outcome | Runs | Completed | Deaths | Raids (won) | Heat peak | Breach Heat | Fights | Decisions off-default |
|---|---|---|---|---|---|---|---|---|---|
| 1000 | NONE | 60 | 57 | 3 | 9 (7) | 58 | 11 | 339 | 269 of 2284 |
| 1001 | NONE | 60 | 60 | 0 | 4 (1) | 96 | -1 | 347 | 265 of 1886 |
| 1002 | NONE | 60 | 54 | 6 | 9 (4) | 100 | 31 | 330 | 345 of 2246 |
| 1003 | NONE | 60 | 57 | 3 | 7 (6) | 52 | 25 | 335 | 265 of 1938 |
| 1004 | NONE | 60 | 56 | 4 | 5 (4) | 64 | 35 | 324 | 278 of 2006 |

## Reasons by decision kind (sample)

- seed 1000 [combat] Jolt on your wheel (+); Fine Tune on your wheel (+); Overdrive on your wheel (+). RAM 3. End Turn: you deal 36, take 0 (Triage Unit 45->9). Pointers: Breaker po — *dominant: deals the most, takes the least, kills the most*
- seed 1000 [combat] Play nothing, end the turn. RAM 0. End Turn: you deal 9, take 0, 1 kill(s) (Triage Unit 9->0). Pointers: Breaker pointer 0: tick 5 -> Shim 6 (offset +0, PERFECT — *dominant: deals the most, takes the least, kills the most*
- seed 1000 [combat] Jolt on enemy wheel (+); Overload on enemy wheel (+). RAM 4. End Turn: you deal 20, take 0 (Claims Adjuster 102->82). Pointers: Breaker pointer 0: tick 5 -> Shi — *Option 2 deals the most damage (20 to the adjuster, leaving it at 82) while taking zero, using Overload's burst for the best trade; the other zero-damage options deal less, and passing (option 5) lets*
- seed 1000 [combat] Jolt on your wheel (+); Jolt on your wheel (+); nudge your wheel +1; Overdrive on your wheel (+). RAM 3. End Turn: you deal 72, take 8 (Claims Adjuster 82->10). — *Option 0 kills the Claims Adjuster outright from 82 down to 10 in the preview's damage math, dealing 72 for 8 taken, and it leaves RAM at 3, a healthier spend than option 1 for the same result; the ri*
- seed 1000 [node] ROUTER at layer 1 (Heat +0) — *All three ROUTER nodes at layer 1 carry identical Heat +0 and no visible difference, so I take the first to keep the run moving; with Heat at 0 there's no pressure to split hairs, and I'll keep watchi*
- seed 1000 [node] ROUTER at layer 4 (Heat +0) — *Heat is at 1 and I want to keep it low for the long game, so I take the Heat +0 ROUTER over the elite Server Rack that would push Heat to 3, avoiding a raid threshold while HP sits at 48/60 with no he*
- seed 1000 [node] ROUTER at layer 1 (Heat +0) — *Both routers are identical at Heat +0 with no preview difference, so I take the first and keep the run moving toward EXPLOIT objectives while holding Heat low for later raids.*
- seed 1000 [node] ROUTER at layer 2 (Heat +0) — *Both routers are identical at Heat +0 with no preview difference, so I take the first and keep the run moving toward the EXPLOIT objective while HP sits at 44/60 and Heat stays low.*
- seed 1000 [reward] Card Overload: Deal 10 damage to the target and take 4. Exhaust. — *Overload adds real burst damage for a deck of mostly basic Jolts; the 4 self-damage is affordable at 60 HP and Exhaust limits the cost, while Inner Drift and Flick are marginal manipulation that would*
- seed 1000 [reward] Card Patch Up: Heal 6. Exhaust. — *Heal 6 on exhaust recovers HP at 48/60 without permanently bloating the deck; Gear Shift and another Jolt add little, and skipping forgoes a free sustain tool for later fights.*
- seed 1000 [reward] Firmware Leech into slot 2 (Shim 6): SHIM slice restores 1 RAM on Good or better. — *Heat is only 1, so Coolant Loop's Heat reduction has little value now; Leech's RAM restore on Good or better helps every fight, and putting it on a Shim 6 slice replaces a modest slice rather than the*
- seed 1000 [reward] Card Stim Patch: Heal 12. Exhaust. — *Stim Patch heals 12 on Exhaust, which fixes HP at 48/60 without permanently bloating the deck. I already have one Overdrive, and Reroll is random and adds little. Keeping the operative healthy matters*
- seed 1000 [event] Copy the index (+2 Schematics banked) (+2 Schematics) — *Heat is already 0 so wiping debt buys nothing and costs 5 HP; copying the index banks two Schematics at no risk, which feeds long-term campaign upgrades without drawing down the operative's health bef*
- seed 1000 [event] Scrub your traces (-2 Heat) (-2 Heat) — *At Heat 23 with HP 27/60 and a raid threshold to protect, I'd rather spend the event on lowering Heat than take +2 Heat for 30 Cycles, since the long game depends on staying clear of raids even though*
- seed 1000 [event] Cash them out (+20 Cycles) (+20 Cycles) — *Heat is 19 and Schematics are nearly spent, so the 20 Cycles from cashing out the expiring points is a clear, low-risk gain with no Heat cost, which I'd rather bank than let lapse at midnight.*
- seed 1000 [event] Copy the index (+2 Schematics banked) (+2 Schematics) — *Copying the index banks +2 Schematics at no HP or Heat cost, and at Heat 2 the Heat reduction from option 1 is not worth 5 HP, so I take the free long-term resource while avoiding the risk of an unnec*
- seed 1000 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *All sites are tier 1 with no objective and +0 Heat, so there's no real differentiator; Heat is 0 and home is full, so I send Breaker 1 to the first site to start gathering Schematics and Exploits at n*
- seed 1000 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *Heat is only 5 so scrubbing is wasteful, and exploits are the win condition (0 so far). The Pricing Memo Archive is the only EXPLOIT objective, and the R1 Breaker is the stronger operative to send. Th*
- seed 1000 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *Kill-Switch Authority is the only objective that yields an Exploit, which we need to win. The Heat change is +0 and Heat is 23, so there's no pressure to scrub. Sending the stronger R2 Breaker (60 HP)*
- seed 1000 [launch] Send Breaker 2 (R0) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *Heat is 19 and Schematics are nearly spent, so a tier 1 Scrub Records run (-5 Heat) is the cheapest way to lower Heat. I send Breaker 2 (R0) because it is the less experienced operative and the safer *
- seed 1000 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *All three plans project an identical outcome (cell holds, 2 threats destroyed, no losses), so I take the default spread. It keeps coverage on the outer nodes while still protecting home, and it avoids*
- seed 1000 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 2, reached home 0, DOWN t1_a, TAKEN none — *All three plans project the same result (cell holds, home 50->50, 2 threats destroyed), though each now downs t1_a, so I take the default spread, which keeps coverage across outer nodes and home in ca*
- seed 1000 [raid] spread from home outward (default): projected lost, home 50 -> 45, threats destroyed 2, reached home 1, DOWN none, TAKEN none — *Options 0 and 2 have identical projections (home 50->45, 2 threats destroyed, 1 reaches home), so I take the default spread from home outward, which keeps defenders where they thin threats earliest; s*
- seed 1000 [shop] Leave (default: remove the Bug card first if affordable) — *With 125 Cycles and HP 27/60, the shop's firmware and card removals cost 50 to 123 Cycles each, and none addresses the survival gap, so I leave to keep Cycles for a later Server Rack heal and avoid di*
- seed 1000 [shop] Firmware Patch+ for 84 Cycles: Slice output +50%. (into slot 2, Shim 6) — *Patch+ at 84 Cycles gives +50% slice output into a Shim 6 slot, a strong firmware upgrade for 93 Cycles, and I avoid spending on removals or cheap cards because the deck already has a working core and*
- seed 1000 [shop] Leave (default: remove the Bug card first if affordable) — *With 74 Cycles and a 15-card deck that already works, spending on a card or removal gives marginal value; I keep Cycles banked for a future upgrade and avoid diluting or thinning the core while Heat s*
- seed 1000 [shop] Leave (default: remove the Bug card first if affordable) — *With 110 Cycles and a working 15-card deck, buying a card or firmware or paying to remove a card adds dilution or cost without a clear gain, so I leave the shop and keep Cycles in reserve for a strong*
- seed 1000 [hq] Default upkeep: repair DOWN nodes and home, recruit to two operatives, scrub Heat at 40+ keeping a reserve, claim one Firewall Relay when rich — *Heat is 0 and home is full, so the default upkeep covers what the campaign needs: both operatives are already recruited and nothing is damaged. It keeps Schematics in reserve for a future Firewall Rel*
- seed 1000 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *Heat is only 5 so scrubbing is wasteful, and with 2 operatives already recruited, 50 Schematics is best spent on long-term defense: a Firewall Relay for 30 improves raid resilience, which matters most*
- seed 1000 [hq] Done at HQ: launch the next netrun now — *Heat is only 5 and home is full, so there is nothing to repair or scrub. With 20 Schematics and two operatives, I'd keep the reserve for future Relay claims and launch now rather than spend on one-run*
- seed 1000 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *Patching the home server to full for just 5 Schematics is cheap insurance against a raid, since a lost raid ends the campaign. Heat 23 is still well below the 40+ scrub threshold, so I'm saving the 62*
- seed 1001 [combat] Jolt on your wheel (+); nudge your wheel +1; Brute Spin on enemy wheel (+). RAM 3. End Turn: you deal 22, take 6 (Care Swarm 25->3). Pointers: Breaker pointer 0 — *dominant: deals the most, takes the least, kills the most*
- seed 1001 [combat] nudge enemy wheel +1. RAM 0. End Turn: you deal 3, take 6, 1 kill(s) (Care Swarm 3->0). Pointers: Breaker pointer 0: tick 15 -> Shim 6 (offset +0, PERFECT); Car — *dominant: deals the most, takes the least, kills the most*
- seed 1001 [combat] nudge your wheel -1; Jolt on enemy wheel (+). RAM 1. End Turn: you deal 12, take 3 (Care Swarm 25->13). Pointers: Breaker pointer 0: tick 15 -> Shim 6 (offset + — *dominant: deals the most, takes the least, kills the most*
- seed 1001 [combat] nudge your wheel -1. RAM 0. End Turn: you deal 13, take 9, 1 kill(s) (Care Swarm 13->0). Pointers: Breaker pointer 0: tick 0 -> Overflow 12 (offset +0, PERFECT) — *dominant: deals the most, takes the least, kills the most*
- seed 1001 [node] ROUTER at layer 1 (Heat +0) — *Both routers are identical at layer 1 with Heat +0 and no visible objective, so I take the first to keep Heat at zero and preserve the run's options without guessing at hidden differences.*
- seed 1001 [node] TERMINAL at layer 2 (Heat +0) — *Both layer-2 nodes show Heat +0 with no visible objective, so I'm taking the Terminal to vary the route and gather information about its contents while keeping Heat at zero, avoiding another Router th*
- seed 1001 [node] ROUTER at layer 3 (Heat +0) — *Both layer-3 nodes show Heat +0 with no visible objective, so I stay consistent with the Heat-zero routing that has protected the run and take the Router without new information to justify a change.*
- seed 1001 [node] ROUTER at layer 5 (Heat +0) — *At 30/60 HP with Heat at 1, the elite's Heat +1 and likely harder fight risk a raid threshold and an operative loss, so I take the Heat-zero router to keep the long game safe and repair HP before faci*
- seed 1001 [reward] Card Deep Strip: Remove 4 resistance from the target. — *Deep Strip gives a concrete, reliable effect (removing 4 resistance) that boosts damage from my Jolt-heavy deck. Reroll and Malware Drop are random and add little to a deck this small, so Deep Strip i*
- seed 1001 [reward] Card Data Surge: Draw 3 cards. — *Deck is 11 cards with 4 Jolts; Data Surge's draw 3 adds consistency and cycling without risking Heat, while Sanitize is situational and a third Brute Spin adds little. Skipping is viable but a draw ca*
- seed 1001 [reward] Firmware Patch+ into slot 5 (Defrag 5): Slice output +50%. — *Firmware Patch+ gives a flat +50% slice output with no positional dependency, so it is the safer pick. I put it on Defrag 5, which is likely a useful slice, rather than replacing a Shim 6 or the Null *
- seed 1001 [reward] Skip this reward — *The deck is already 12 cards with 4 Jolts and 2 Brute Spins, so another copy adds little. Power Tap costs HP at 30/60, which I can't afford. Skipping keeps the deck lean and consistent without adding *
- seed 1001 [event] Decline the terms — *Copying a clause that lets Solace suspend cardiac pacing for non-payment is a hostage-style trap; 15 Cycles is trivial against the risk to the operative and the long-run trust cost, so I decline the t*
- seed 1001 [event] Scrub your traces (-2 Heat) (-2 Heat) — *Heat is at 8 and climbing toward raid thresholds, and the campaign layer matters more than 30 Cycles here, so I take the quiet line to cut Heat by 2 and avoid feeding a raid that could cost the home s*
- seed 1001 [event] Wipe a street's debt (-2 Heat, 5 damage) (-5 HP, -2 Heat) — *Heat is 14 and climbing toward raid thresholds, and as the campaign strategist I'd rather spend 5 HP on a run that's easy to heal than let Heat accumulate; -2 Heat now is worth more over the long game*
- seed 1001 [event] Ask for help (+15 HP) (+15 HP) — *At 42/60 HP with Heat already at 14 and a long campaign ahead, the guaranteed +15 HP restores a buffer against upcoming fights without adding Heat, whereas Lock On is a marginal card that doesn't fit *
- seed 1001 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *All tier 1 sites show Heat +0 and no objective, so they're interchangeable on the information given. I'm sending Breaker 1 to the first site as a low-risk scouting run, keeping Breaker 2 safe in reser*
- seed 1001 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *Heat is only 3, so Scrub Records (-5) would be wasted. The Pricing Memo Archive is the only EXPLOIT objective, and with 0 Exploits we need them to win. It adds no Heat, and the stronger R1 Breaker is *
- seed 1001 [launch] Send Breaker 2 (R0) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *Heat is 14 and I have only 24 Schematics, so Scrub Records (-5 Heat) is the safe campaign move. I send the weaker R0 Breaker 2 on a tier 1 site, which keeps the stronger R2 Breaker 1 safe from permade*
- seed 1001 [launch] Send Breaker 1 (R2) to Scrub Records: tier 1, objective PATROL (no objective), Heat change -5 — *Heat is 6, so a -5 Scrub Records patrol is cheap insurance against raids. The home server has already fallen once (raids_lost 1), so I send the higher-rank Breaker 1 on a low-tier run to keep Heat low*
- seed 1001 [raid] outer nodes first, home last: projected CELL HOLDS, home 50 -> 50, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *Outer nodes first is the only plan projected to hold the cell: it destroys both threats, none reach home, and home stays at 50/50, whereas the other two plans lose the raid. Losing a raid risks the ho*
- seed 1001 [raid] everything on the home server: projected lost, home 50 -> 39, threats destroyed 3, reached home 1, DOWN t1_a, TAKEN t1_a — *All three allocations project the same loss (home 50->39, t1_a taken), so the choice barely matters; I concentrate defenses on the home server because losing it ends the campaign, and it avoids splitt*
- seed 1001 [shop] Leave (default: remove the Bug card first if affordable) — *With 56 Cycles and a lean 12-card deck that is working, buying Snap or Nudge Driver would dilute draws, and removing any core card like Jolt or Fine Tune risks weakening the engine, so I keep Cycles b*
- seed 1001 [shop] Leave (default: remove the Bug card first if affordable) — *With 55 Cycles I can afford one removal, but the deck is already lean at 12 cards and every card is doing work, so removing one dilutes the wheel mix; I'd rather bank Cycles for a future Server Rack o*
- seed 1001 [shop] Remove Jolt from the deck for 50 Cycles — *Cycles are plentiful at 123 and the deck has four Jolts, so thinning the most redundant card for 50 Cycles sharpens draws without spending on firmware I can't yet slot well; I avoided the 99-Cycle Pow*
- seed 1001 [shop] Leave (default: remove the Bug card first if affordable) — *With 73 Cycles spent on a Jolt removal already and no clear upgrade in the shop, leaving keeps Cycles for later and avoids buying marginal cards like Bulwark or Strip that would dilute a deck already *
- seed 1001 [hq] Default upkeep: repair DOWN nodes and home, recruit to two operatives, scrub Heat at 40+ keeping a reserve, claim one Firewall Relay when rich — *Heat is 0, home is full and the roster already has two operatives, so default upkeep is cheap and safe. It keeps the 20 Schematics in reserve for later raid defense instead of spending them on one-run*
- seed 1001 [hq] Default upkeep: repair DOWN nodes and home, recruit to two operatives, scrub Heat at 40+ keeping a reserve, claim one Firewall Relay when rich — *Heat is only 3, so scrubbing it for 25 Schematics would be wasted. Default upkeep covers the useful HQ work: the home is at 50/50, two operatives are already recruited, and one Firewall Relay gets cla*
- seed 1001 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *Home is 45/50 and raids_lost is already 1, so patching to full for 5 Schematics is cheap insurance against another lost raid. I'm keeping the other 49 Schematics in reserve for Heat scrubbing later; H*
- seed 1001 [hq] Scrub Heat for 25 Schematics (Heat now 19) — *Heat is 19 and climbing toward raid thresholds, and with 49 Schematics I can afford to scrub it for 25 while still keeping a reserve. Home is already patched to full, and a lost raid has already happe*
- seed 1002 [combat] Jolt on your wheel (+); Overdrive on your wheel (+); Brute Spin on enemy wheel (+). RAM 4. End Turn: you deal 18, take 6 (Care Swarm 25->7). Pointers: Breaker p — *dominant: deals the most, takes the least, kills the most*
- seed 1002 [combat] nudge enemy wheel -1; nudge your wheel +1. RAM 1. End Turn: you deal 7, take 9, 1 kill(s) (Care Swarm 7->0). Pointers: Breaker pointer 0: tick 15 -> Shim 6 (off — *Options 0, 1, 2, 3 and 4 all kill Care Swarm and take the same 9 damage, so I pick the cheapest line: option 2 spends only 1 RAM and still lands a PERFECT Breaker hit, while option 0 burns 3 RAM and o*
- seed 1002 [combat] nudge enemy wheel +1; nudge your wheel +1. RAM 1. End Turn: you deal 20, take 0 (Claims Adjuster 112->92). Pointers: Breaker pointer 0: tick 10 -> Shim 6 (offse — *dominant: deals the most, takes the least, kills the most*
- seed 1002 [combat] nudge your wheel -1; Overdrive on your wheel (+); nudge enemy wheel -1. RAM 2. End Turn: you deal 36, take 8 (Claims Adjuster 92->56). Pointers: Breaker pointer — *Option 2 deals 36 damage for only 8 taken and 2 RAM, keeping HP at 45 with Heat at 0, while option 0 and 1 deal similar damage with zero incoming but cost 3 RAM, and option 4 takes 16 for the same 36;*
- seed 1002 [node] ROUTER at layer 1 (Heat +0) — *All three ROUTER nodes are identical at layer 1 with Heat +0 and no objective, so I take the first to keep the run moving; there is no campaign-layer difference to weigh, and picking any of them avoid*
- seed 1002 [node] TERMINAL at layer 5 (Heat +0) — *Heat is at 2 and the campaign layer matters most to me, so I take the TERMINAL at layer 5 with Heat +0 rather than the Elite ROUTER that adds Heat; I accept forgoing the elite's possible reward since *
- seed 1002 [node] ROUTER at layer 6 (Heat +0) — *Heat is at 2 and HP is 37/60, so the Elite ROUTER's +1 Heat is a campaign cost I won't take for a fight-heavy node when I'm already low on HP; the plain ROUTER keeps Heat flat and lets me recover befo*
- seed 1002 [node] ROUTER at layer 1 (Heat +0) — *All four options are identical ROUTER nodes at layer 1 with Heat +0, so I take the first without changing the campaign position; the duplicates show the menu offers no real Heat or roster trade-off to*
- seed 1002 [reward] Card Pull: Draw 2 cards. — *Card Pull adds draw to a 10-card deck that already has duplicate Jolts and Brute Spins; extra draw improves consistency without bloating the deck with another wheel manipulator, and skipping gains not*
- seed 1002 [reward] Firmware Hardened into slot 5 (Defrag 5): Slice permanently ENCRYPTED. — *Barbed Wire only helps on a DEFRAG slice, and the only Defrag is in slot 5, so Hardened there is the more useful pick. Making that slice permanently ENCRYPTED protects the wheel at no cost and no Heat*
- seed 1002 [reward] Card Scrap Code: Gain 1 RAM and draw 1 card. Exhaust. — *Scrap Code is a cheap cantrip that adds RAM and draw without bloating the deck much. Deep Calibrate is situational, and Arc Flash's 3 damage is weak. It also supports the nudge-heavy plans I've been u*
- seed 1002 [reward] Daemon Rack Skimmer: Capturing a Server Rack banks 3 extra Schematics. — *Skimmer gives a guaranteed campaign payoff (3 extra Schematics per captured Rack) with no Heat cost, while the other daemons depend on NULL slices my wheel may not even contain; skipping gives up free*
- seed 1002 [event] Copy the clause (+15 Cycles) (+15 Cycles) — *Heat is 0 and HP is 45/60, so the event's +15 Cycles is a clear campaign gain with no Heat cost; the risk of 'suspended licensed features' is a narrative flavor here, and I'd rather bank Cycles for th*
- seed 1002 [event] Sell the parcel (+25 Cycles) (+25 Cycles) — *Heat is at 2 and the campaign layer is my priority, so I avoid the -4 HP and unknown Overvolt firmware that could compound risk on a 37/60 HP run; selling for +25 Cycles is a clean, Heat-free gain tha*
- seed 1002 [event] Walk on — *Heat is 0 and the van's loot costs +4 Heat for 35 Cycles, while stripping the tracker costs HP and gains an asset I can't evaluate; as a campaign strategist I'd rather keep Heat clean and walk on, sin*
- seed 1002 [event] Kill the loop (-1 Heat) (-1 Heat) — *Heat is at 20 and raids fire at thresholds, so spending a little to drop Heat to 19 is the long-game move; redirecting adds 3 Heat for 30 Cycles, which trades campaign safety for a short-term gain I d*
- seed 1002 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *All sites are tier 1 with no objective and +0 Heat, so there is no real difference between them. I'm sending Breaker 1 to the first one and keeping Breaker 2 in reserve in case a permadeath loss force*
- seed 1002 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *Heat is already 0, so the Heat-reduction site (-5) would be wasted. The Pricing Memo Archive is the only site with an EXPLOIT objective, which is needed to win, and it adds no Heat. I send Breaker 1 (*
- seed 1002 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *Heat is only 15, so scrubbing isn't needed. Kill-Switch Authority is the only Exploit objective, and Exploits are what win the campaign. The R2 Breaker is the stronger operative for a tier 2 run, and *
- seed 1002 [launch] Send Breaker 2 (R0) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *Heat is 25 and Scrub Records cuts it by 5 at tier 1, which suits a Heat-first strategist. I send the weaker R0 Breaker 2 so the stronger R3 Breaker 1 isn't risked, and a tier 1 site is a safe run for *
- seed 1002 [raid] spread from home outward (default): projected CELL HOLDS, home 45 -> 45, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *Both spread options hold the cell with home intact at 45 and destroy 2 threats; 'everything on home' loses the raid. With raids_lost at 1 I take the default spread, which defends from home outward and*
- seed 1002 [raid] spread from home outward (default): projected lost, home 50 -> 21, threats destroyed 0, reached home 4, DOWN none, TAKEN none — *All three plans project an identical loss (home 50 -> 21, 4 threats reaching home), so the choice is cosmetic; I take the default and flag that the real lesson is to cut Heat before it reaches the 75 *
- seed 1002 [raid] spread from home outward (default): projected lost, home 50 -> 31, threats destroyed 4, reached home 2, DOWN t1_g,t1_e, TAKEN none — *All options project a lost raid, but spreading from home outward destroys 4 threats and leaves home at 31 HP, the most survivable result, and nothing is taken. Option 2 projects the same outcome, so I*
- seed 1002 [shop] Remove Jolt from the deck for 50 Cycles — *With four Jolts diluting draws, removing one Jolt for 50 Cycles trims the most redundant card while keeping Overdrive and the Brute/Fine Tune core; I avoided the 136-Cycle Burner since its per-trigger*
- seed 1002 [shop] Leave (default: remove the Bug card first if affordable) — *With 124 Cycles and a deck already crowded with redundant Jolts, the cheapest useful move is to hold funds rather than pay 75 to trim one card or 81 for a Firmware Mirror whose slice position is uncle*
- seed 1002 [shop] Card Flip Switch for 58 Cycles: Flip your own wheel. — *With 128 Cycles and a lean 13-card deck, Flip Switch at 58 adds a cheap self-wheel flip that improves pointer control without diluting the deck; I avoided the 125-Cycle Siphon since healing 2 on Good *
- seed 1002 [shop] Leave (default: remove the Bug card first if affordable) — *With 70 Cycles, removal at 50 would leave little margin, and my deck is already lean at 14 cards where every card carries weight; no single removal clearly improves the build enough to justify spendin*
- seed 1002 [hq] Default upkeep: repair DOWN nodes and home, recruit to two operatives, scrub Heat at 40+ keeping a reserve, claim one Firewall Relay when rich — *Heat is 0 and home is full, so default upkeep is safe: it keeps the roster at two and holds the 20 Schematics reserve instead of spending on one-run boosts, which don't help the long game.*
- seed 1002 [hq] Scrub Heat for 25 Schematics (Heat now 4) — *As a campaign strategist I'd rather spend the 58 Schematics on Heat now: scrubbing costs 25 and drops Heat from 4 to a lower, safer level, which keeps raids off the home server. It still leaves a rese*
- seed 1002 [hq] Done at HQ: launch the next netrun now — *Heat is 0 and home is at full health with 33 Schematics. Two operatives are already recruited, so there is nothing to scrub, repair or recruit. A 30-Schematic relay would drain the reserve, and the bo*
- seed 1002 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *With 96 Schematics, Heat is only 15 (no scrub needed) and the roster is already at two operatives, so the best long-game investment is a Firewall Relay to protect home against future raids; boosts are*
- seed 1003 [combat] Mirror Flip on your wheel (+); nudge your wheel -1; Overdrive on your wheel (+). RAM 4. End Turn: you deal 36, take 0 (Compliance Officer 50->14). Pointers: Bre — *dominant: deals the most, takes the least, kills the most*
- seed 1003 [combat] Brute Spin on enemy wheel (+); nudge your wheel -1; Fine Tune on enemy wheel (-). RAM 3. End Turn: you deal 9, take 0 (Compliance Officer 14->5). Pointers: Brea — *dominant: deals the most, takes the least, kills the most*
- seed 1003 [combat] Mirror Flip on your wheel (+); Brute Spin on enemy wheel (+). RAM 5. End Turn: you deal 5, take 0, 1 kill(s) (Compliance Officer 5->0). Pointers: Breaker pointe — *dominant: deals the most, takes the least, kills the most*
- seed 1003 [combat] Fine Tune on enemy wheel (+); Overdrive on your wheel (+); Mirror Flip on enemy wheel (+). RAM 5. End Turn: you deal 18, take 9 (Care Swarm 25->7). Pointers: Br — *dominant: deals the most, takes the least, kills the most*
- seed 1003 [node] ROUTER at layer 1 (Heat +0) — *All three ROUTER options are identical at layer 1 with Heat +0, so I take the first to keep the run moving; with Heat at 0 there's no campaign cost to weigh, and I'd rather spend my deliberation on th*
- seed 1003 [node] ROUTER at layer 2 (Heat +0) — *Both ROUTER options are identical at Heat +0 with no visible objective difference, so I take the first to keep the run moving and stay deliberate on the map without spending attention on a coin flip.*
- seed 1003 [node] ELITE ROUTER at layer 4 (Heat +1) — *Heat is at 1 and the campaign layer matters most to me, so I take the ELITE ROUTER at +1 Heat over the ELITE SERVER_RACK at +2, keeping Heat low for the long game even though the Server Rack's healing*
- seed 1003 [node] TERMINAL at layer 5 (Heat +0) — *Both options are identical TERMINAL nodes at Heat +0, so I take the first; with Heat already managed, a zero-Heat node is the clean long-game pick and there is no difference to weigh between them.*
- seed 1003 [reward] Card Bulwark: Gain 12 block. — *Bulwark gives solid defense for a deck that's all offense and spin-tuning, helping preserve HP and avoid a failed run that could cost Heat or the operative; Feather Touch and Flick are marginal and wo*
- seed 1003 [reward] Card Snap: Move your outer ring to the nearest slice centre (Perfect). — *Snap turns a near-miss into a guaranteed Perfect, which is the strongest result on the wheel and makes the whole deck's spin outcomes more reliable. That keeps fights short, protects HP, and lowers th*
- seed 1003 [reward] Skip this reward — *The deck is already 12 cards with 4 Jolts and 2 Brute Spins, and none of these options clearly improves it. Duck is situational, a third Brute Spin adds more variance, and Static Shock is just another*
- seed 1003 [reward] Firmware Static Coat into slot 5 (Defrag 5): DEFRAG slice also grants 2 shield. — *Firmware is free and permanent, and slot 5 is the only existing Defrag slice, so Static Coat there gives immediate 2 shield value; the other slots are Shim or Null and would not trigger the DEFRAG eff*
- seed 1003 [event] Pay 20 Cycles for a patch-up (+20 HP) (-20 Cycles, +20 HP) — *At 45/60 HP with Heat only at 2 and 117 Cycles banked, paying 20 Cycles for +20 HP is cheap insurance for the next fights, and keeping operatives alive matters more to the long game than the Cycles I'*
- seed 1003 [event] Not today — *With 99 Cycles in hand, buying Patch+ for 30 would be affordable, but the deck is already working and Heat is 22, so I'd rather hold Cycles as a reserve for a Scrub Records or emergency Firmware later*
- seed 1003 [event] Add your tag (-1 Heat) (-1 Heat) — *Heat is at 25 and raids fire at thresholds, so spending the event to shed 1 Heat (-1 Heat) protects the long game more than walking on or taking two Feather Touch cards that would dilute my lean deck.*
- seed 1003 [event] Take the batteries (+2 Schematics banked) (+2 Schematics) — *Two banked Schematics feed the campaign layer at zero Heat cost and no HP risk, while a second Bulwark would only dilute the lean 10-card deck I've been protecting.*
- seed 1003 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *All sites are tier 1 with no objective and +0 Heat, so there is no real difference. With Heat at 0 and a full home server, I'll send Breaker 1 to the first site to gain Schematics and info while keepi*
- seed 1003 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *Exploits are 0 and winning requires enough of them. The Pricing Memo Archive is the only EXPLOIT objective and adds no Heat. Heat is only 4, so Scrub Records would be wasted, and sending the stronger *
- seed 1003 [launch] Send Breaker 1 (R2) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *Heat is 22, below the 40 scrub threshold, so Scrub Records isn't needed yet. The Kill-Switch Authority run is the only one that advances the win condition by earning an Exploit, and Breaker 1 (R2) is *
- seed 1003 [launch] Send Breaker 2 (R0) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *Heat is 25 and a raid was already lost, so a Heat reduction site is the best campaign value. Sending the lower-rank Breaker 2 (R0) on a tier 1 Scrub Records run risks little if it dies, and it keeps t*
- seed 1003 [raid] everything on the home server: projected CELL HOLDS, home 50 -> 50, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *Both options 0 and 1 hold with no losses, but concentrating everything on home gives the safest guarantee given one raid already lost; option 2 lets a threat reach home and loses the run, so avoid it.*
- seed 1003 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 1, reached home 0, DOWN none, TAKEN none — *All three deployments project the same outcome (cell holds, home stays 50/50, one threat destroyed), so I take the default spread from home outward, which keeps defenders balanced across the network w*
- seed 1003 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 3, reached home 0, DOWN none, TAKEN none — *All three deployments project an identical result (cell holds, 3 threats destroyed, none reach home, no operatives down), so I take the default spread from home outward, which gives the most layered c*
- seed 1003 [shop] Remove Jolt from the deck for 50 Cycles — *With 120 Cycles and a 12-card deck heavy on Jolt, removing one Jolt for 50 Cycles thins the deck for more consistent wheel results without spending on a firmware or card that adds little, and avoids t*
- seed 1003 [shop] Leave (default: remove the Bug card first if affordable) — *With 70 cycles spent already the shop offers only marginal additions (Tap Tap, Twist) to a deck that already works, and Heat sits at 9 so I'd rather keep Cycles in reserve for a Schematic or healing a*
- seed 1003 [shop] Remove Jolt from the deck for 50 Cycles — *Jolt appears three times in an 11-card deck, so thinning one copy for 50 Cycles reduces redundant draws and keeps the deck lean without spending Heat or buying a card I don't need; I avoided the 99-Cy*
- seed 1003 [shop] Remove Jolt from the deck for 50 Cycles — *With 82 Cycles and Heat at 27, I'd rather spend on a cheap removal than add cards; trimming a duplicate Jolt (I already have two) keeps the lean deck sharp for 50 Cycles, while avoiding the 76-Cycle f*
- seed 1003 [hq] Default upkeep: repair DOWN nodes and home, recruit to two operatives, scrub Heat at 40+ keeping a reserve, claim one Firewall Relay when rich — *Heat is 0 and home is at full health, so default upkeep is safe and mostly a no-op. It keeps the 20 Schematics in reserve for a Firewall Relay or later raid repairs, instead of spending them on one-ru*
- seed 1003 [hq] Claim Continuum Billing Farm next to home as a Firewall Relay for 30 Schematics — *Heat is only 4 and home is full, so scrubbing is wasteful; with 45 Schematics, claiming a Firewall Relay for 30 is the best long-term investment for raid defense, leaving 15 in reserve, and we already*
- seed 1003 [hq] Done at HQ: launch the next netrun now — *Heat is only 4, home is full, and I already have two operatives plus a claimed Firewall Relay, so upkeep and recruiting add little. I'll keep the 15 Schematics as a reserve for raid prep and launch th*
- seed 1003 [hq] Patch the home server to full for 5 Schematics (now 45/50) — *Patching home to full costs only 5 Schematics and protects against the next raid, which matters since we've already lost one. Heat at 22 is well below the 40 scrub threshold, and 47 Schematics leaves *
- seed 1004 [combat] Jolt on enemy wheel (+); Overdrive on your wheel (+); nudge your wheel -1; nudge your wheel -1. RAM 3. End Turn: you deal 33, take 3 (Collections Agent 40->7).  — *dominant: deals the most, takes the least, kills the most*
- seed 1004 [combat] Brute Spin on enemy wheel (+); nudge your wheel +1; Jolt on enemy wheel (+). RAM 3. End Turn: you deal 7, take 3, 1 kill(s) (Collections Agent 7->0). Pointers:  — *dominant: deals the most, takes the least, kills the most*
- seed 1004 [combat] Jolt on enemy wheel (+); Mirror Flip on enemy wheel (+). RAM 4. End Turn: you deal 24, take 0 (Billing Daemon 42->18). Pointers: Breaker pointer 0: tick 0 -> Ov — *dominant: deals the most, takes the least, kills the most*
- seed 1004 [combat] Jolt on your wheel (+); Overdrive on your wheel (+); Fine Tune on enemy wheel (+). RAM 3. End Turn: you deal 18, take 0, 1 kill(s) (Billing Daemon 18->0). Point — *dominant: deals the most, takes the least, kills the most*
- seed 1004 [node] ROUTER at layer 1 (Heat +0) — *All three options are identical ROUTER nodes at layer 1 with Heat +0, so there is no campaign difference to weigh; I take the first to keep moving and avoid wasting deliberation on a meaningless choic*
- seed 1004 [node] ROUTER at layer 3 (Heat +0) — *Heat is 0 and the campaign layer favors keeping Heat flat; the Elite Router adds +1 Heat for an uncertain reward, and I'd rather bank a safe node while building the deck and roster for later raids.*
- seed 1004 [node] ELITE ROUTER at layer 4 (Heat +1) — *Heat is 0 and the campaign layer favors keeping it flat, so the ELITE ROUTER's +1 Heat is the smaller cost versus the Server Rack's +2, while still offering an elite fight for a possible reward; I'd a*
- seed 1004 [node] ROUTER at layer 5 (Heat +0) — *Heat is 1 and the campaign layer favors keeping it low, so the Router's +0 Heat beats the Elite's +1 for a safer path; I'm skipping the uncertain elite reward since my deck is already set and I want H*
- seed 1004 [reward] Card Deep Strip: Remove 4 resistance from the target. — *Deep Strip adds a useful offensive utility to a Jolt-heavy deck; Flip Switch and Ring Lock are situational and could clog the deck. Deck is only 10 cards, so one added card is low dilution risk and He*
- seed 1004 [reward] Skip this reward — *The deck is already 11 cards with a Jolt core and Deep Strip. Overload costs HP and Freeze/Momentum are situational, so none clearly improves it. Skipping keeps the deck lean and consistent, and it sa*
- seed 1004 [reward] Skip this reward — *The 11-card deck already has a solid Jolt core, and Micro-Adjust (exhaust), a third Brute Spin and Flick would dilute it more than they help. Skipping keeps draws consistent and costs no Heat or risk.*
- seed 1004 [reward] Skip this reward — *The 11-card deck already has a solid Jolt core, and Flick, Freeze and Cleanse are all situational and would dilute it, so skipping keeps the deck lean without costing any Heat.*
- seed 1004 [event] Split it (+20 Cycles) (+20 Cycles) — *Splitting gains 20 Cycles with no HP loss and no Heat or asset cost, keeping the 48/60 HP buffer intact for upcoming nodes while avoiding the 10 damage of Take it all and the Flak Array trade-off.*
- seed 1004 [event] Copy the index (+2 Schematics banked) (+2 Schematics) — *Heat is already low at 3 and HP is full at 60/60, so taking Copy the index banks 2 Schematics for free without spending HP or inviting raid pressure; Wipe a street's debt costs 5 HP for only -2 Heat, *
- seed 1004 [event] Sign it with your handle (-2 Heat) (-2 Heat) — *Signing the log drops Heat from 6 to 4, keeping the raid clock slow for the campaign, which outweighs the 25 Cycles from stripping the implant and its +2 Heat.*
- seed 1004 [event] Pop one (+6 HP) (+6 HP) — *HP is 36/60 with Heat at 4, so trading a Heat-raising resale for 6 HP keeps the raid clock flat while steadying the run; I avoid Resell because the +1 Heat would push me toward a raid threshold for on*
- seed 1004 [launch] Send Breaker 1 (R0) to Continuum Billing Farm: tier 1, objective NONE, Heat change +0 — *All sites are tier 1 with no objective and +0 Heat, so there is no real difference. I'm sending Breaker 1 to the first site to bank early rewards at zero Heat cost while Breaker 2 stays safe as roster*
- seed 1004 [launch] Send Breaker 1 (R1) to Pricing Memo Archive: tier 2, objective EXPLOIT, Heat change +0 — *Heat is only 3, so the Exploit objective is the real progress toward winning, and Pricing Memo Archive adds +0 Heat. Breaker 1 (R1) is the stronger operative for a tier 2 site. A -5 Heat scrub would b*
- seed 1004 [launch] Send Breaker 1 (R2) to Scrub Records: tier 1, objective HEAT_REDUCTION, Heat change -5 — *Heat is 12 and Scrub Records gives -5 Heat, which fits my priority of keeping the raid clock slow. I send Breaker 1 (R2) because the higher-rank operative is likelier to survive and finish a tier 1 ru*
- seed 1004 [launch] Send Breaker 1 (R3) to Kill-Switch Authority: tier 2, objective EXPLOIT, Heat change +0 — *Kill-Switch Authority is the only Site with an EXPLOIT objective, and we need Exploits to breach the central server. It adds no Heat, and Breaker 1 (R3) is the stronger operative for a tier 2 run. Hea*
- seed 1004 [raid] spread from home outward (default): projected CELL HOLDS, home 45 -> 45, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *Spreading from home outward is the only plan projected to hold the cell: it destroys both threats, keeps home at 45 and loses no operatives. The other two let a threat reach home and are projected as *
- seed 1004 [raid] spread from home outward (default): projected CELL HOLDS, home 45 -> 45, threats destroyed 2, reached home 0, DOWN none, TAKEN none — *All three plans project an identical hold (home 45, both threats destroyed, no losses), so I take the default spread: it defends outer nodes and home together, which gives the most margin if the proje*
- seed 1004 [raid] spread from home outward (default): projected CELL HOLDS, home 50 -> 50, threats destroyed 3, reached home 0, DOWN none, TAKEN none — *All three projections are identical (cell holds, home 50->50, 3 threats destroyed, nothing down or taken), so I take the default spread-from-home layout, which is the most robust if the projection is *
- seed 1004 [shop] Leave (default: remove the Bug card first if affordable) — *With 62 Cycles and Heat at 31, removing any card for 50 Cycles would leave me with almost nothing for future shops, and the 11-card deck is already lean and working, so I keep the Cycles and avoid thi*
- seed 1004 [shop] Leave (default: remove the Bug card first if affordable) — *With only 58 Cycles and removal costing 50, spending now would leave me almost broke for future shops, and the deck is already lean, so I keep the Cycles as runway and avoid trimming a working card th*
- seed 1004 [shop] Leave (default: remove the Bug card first if affordable) — *Heat is 17 and the lean deck is working, so I keep Cycles and avoid spending on purchases that could dilute draws; removing Jolt or Brute Spin would cut my core damage, and the shop cards add little o*
- seed 1004 [shop] Leave (default: remove the Bug card first if affordable) — *With 179 Cycles and a lean 11-card deck already working at Heat 13, none of the cards on offer clearly improves the deck, and removing a core attacker or Fine Tune for 50 Cycles would weaken the wheel*
- seed 1004 [hq] Default upkeep: repair DOWN nodes and home, recruit to two operatives, scrub Heat at 40+ keeping a reserve, claim one Firewall Relay when rich — *Heat is 0 and home is full, so default upkeep is safe: it keeps the 2-operative roster and preserves Schematics for later claims instead of spending them on one-run boosts. Long-game play favors durab*
- seed 1004 [hq] Done at HQ: launch the next netrun now — *Heat is only 3, well below the 40+ scrub threshold, and two operatives are already alive. I'm keeping the 46 Schematics as a reserve instead of spending 30 on a Relay or on one-run boosts, and launchi*
- seed 1004 [hq] Scrub Heat for 25 Schematics (Heat now 17) — *With 99 Schematics and Heat at 17, I'd spend 25 to scrub Heat first. That keeps the raid clock slow, which is my campaign priority. Schematics are plentiful enough that I can still afford boosts or a *
- seed 1004 [hq] Done at HQ: launch the next netrun now — *Heat is already down to 12 and I have 74 Schematics with two operatives, so more scrubbing at 35 is poor value; keeping a reserve for raid repairs matters more, so I launch the next netrun now.*

## Run logs

### seed 1000
      FIGHT won vs claims_adjuster: 1 turns, HP 48 -> 48
      FIGHT won vs account_manager: 4 turns, HP 48 -> 43
    run 51: Breaker 2 R12 T1 t1_j -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 419, armory 6
      FIGHT won vs compliance_officer: 3 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 6 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 8 turns, HP 60 -> 40
    run 52: Breaker 2 R13 T2 t2_f -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 468, armory 6
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 3 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 55
      FIGHT won vs billing_daemon: 2 turns, HP 55 -> 55
      FIGHT won vs claims_adjuster: 2 turns, HP 55 -> 53
      FIGHT won vs account_manager: 5 turns, HP 53 -> 60
    run 53: Breaker 3 R1 T1 purge_camera_logs -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 495, armory 6
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 56
      FIGHT won vs compliance_officer: 3 turns, HP 56 -> 54
      FIGHT won vs dosage_dispenser: 2 turns, HP 54 -> 54
      FIGHT won vs claims_adjuster: 3 turns, HP 54 -> 49
      FIGHT won vs recall_unit: 5 turns, HP 49 -> 34
      FIGHT won vs dosage_dispenser: 1 turns, HP 34 -> 34
      FIGHT won vs account_manager: 8 turns, HP 34 -> 14
    run 54: Breaker 2 R14 T2 t2_g -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 552, armory 6
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 55
      FIGHT won vs triage_unit: 3 turns, HP 55 -> 55
      FIGHT won vs collections_agent: 3 turns, HP 55 -> 50
      FIGHT won vs claims_adjuster: 3 turns, HP 50 -> 40
      FIGHT won vs compliance_officer: 3 turns, HP 40 -> 37
      FIGHT won vs claims_adjuster: 3 turns, HP 37 -> 37
      FIGHT won vs account_manager: 6 turns, HP 37 -> 37
    run 55: Breaker 2 R15 T2 t2_h -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 609, armory 6
      FIGHT won vs triage_unit: 5 turns, HP 60 -> 55
      FIGHT won vs care_swarm: 3 turns, HP 55 -> 43
      FIGHT won vs care_swarm: 3 turns, HP 43 -> 18
      FIGHT won vs claims_adjuster: 6 turns, HP 18 -> 2
      FIGHT won vs claims_adjuster: 10 turns, HP 2 -> 3
      FIGHT won vs billing_daemon: 4 turns, HP 3 -> 3
      FIGHT won vs account_manager: 12 turns, HP 3 -> 4
    run 56: Breaker 2 R16 T3 t3_b -> COMPLETED, Heat 0, Exploits 3, home 50/50, Schematics 725, armory 6
      boss loadout: R17 HP 60 deck jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,scrap_code,corrupt_packet,lock_on,stim_patch,lock_on,snap,sanitize | daemons clean_signal,bounty_code,scrubber,log_wiper,feedback_loop | firmware ,patch_plus,coolant_loop,overvolt,patch_plus,recycler
      FIGHT died vs renewal_engine: 41 turns, HP 60 -> 60
    run 57: Breaker 2 R17 T4 the_genome_core -> DIED, Heat 14, Exploits 3, home 50/50, Schematics 725, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 48
      FIGHT won vs claims_adjuster: 3 turns, HP 48 -> 44
      FIGHT won vs claims_adjuster: 3 turns, HP 59 -> 60
      FIGHT won vs account_manager: 6 turns, HP 60 -> 54
    run 58: Breaker 3 R2 T2 wipe_biometrics -> COMPLETED, Heat 11, Exploits 3, home 50/50, Schematics 750, armory 6
      boss loadout: R3 HP 60 deck jolt,jolt,jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,leech_worm,deep_calibrate | daemons field_medic | firmware ,patch_plus,siphon,overvolt,,
      FIGHT died vs renewal_engine: 36 turns, HP 60 -> 60
    run 59: Breaker 3 R3 T4 the_genome_core -> DIED, Heat 25, Exploits 3, home 50/50, Schematics 750, armory 6
      FIGHT won vs collections_agent: 3 turns, HP 60 -> 54
      FIGHT won vs dosage_dispenser: 2 turns, HP 54 -> 54
      FIGHT won vs claims_adjuster: 3 turns, HP 54 -> 38
      FIGHT won vs billing_daemon: 2 turns, HP 38 -> 35
      FIGHT won vs account_manager: 6 turns, HP 35 -> 30
    run 60: Breaker 4 R0 T1 purge_camera_logs -> COMPLETED, Heat 28, Exploits 3, home 50/50, Schematics 767, armory 6
### seed 1001
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 48
      FIGHT won vs triage_unit: 2 turns, HP 48 -> 52
      FIGHT won vs recall_unit: 2 turns, HP 52 -> 50
      FIGHT won vs account_manager: 5 turns, HP 50 -> 57
    run 52: Breaker 1 R49 T1 scrub_records -> COMPLETED, Heat 91, Exploits 2, home 50/50, Schematics 186, armory 6
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 54
    run 53: Breaker 1 R50 T1 scrub_records -> COMPLETED, Heat 91, Exploits 2, home 50/50, Schematics 227, armory 6
      FIGHT won vs compliance_officer: 1 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 51
      FIGHT won vs account_manager: 3 turns, HP 51 -> 60
    run 54: Breaker 1 R51 T1 scrub_records -> COMPLETED, Heat 90, Exploits 2, home 50/50, Schematics 104, armory 6
      FIGHT won vs compliance_officer: 1 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 57
      FIGHT won vs care_swarm: 2 turns, HP 57 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 5 turns, HP 60 -> 54
    run 55: Breaker 1 R52 T1 scrub_records -> COMPLETED, Heat 93, Exploits 2, home 50/50, Schematics 139, armory 6
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 57
    run 56: Breaker 1 R53 T1 scrub_records -> COMPLETED, Heat 96, Exploits 2, home 50/50, Schematics 182, armory 6
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 57: Breaker 1 R54 T1 scrub_records -> COMPLETED, Heat 91, Exploits 2, home 50/50, Schematics 36, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 57
      FIGHT won vs compliance_officer: 1 turns, HP 57 -> 58
      FIGHT won vs claims_adjuster: 2 turns, HP 58 -> 58
      FIGHT won vs dosage_dispenser: 2 turns, HP 58 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 58: Breaker 1 R55 T1 scrub_records -> COMPLETED, Heat 91, Exploits 2, home 50/50, Schematics 65, armory 6
      FIGHT won vs triage_unit: 1 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 60
    run 59: Breaker 1 R56 T1 scrub_records -> COMPLETED, Heat 93, Exploits 2, home 50/50, Schematics 89, armory 6
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 58
      FIGHT won vs triage_unit: 2 turns, HP 58 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 44
    run 60: Breaker 1 R57 T1 scrub_records -> COMPLETED, Heat 95, Exploits 2, home 50/50, Schematics 116, armory 6
### seed 1002
      FIGHT won vs account_manager: 5 turns, HP 48 -> 52
    run 52: Breaker 7 R8 T2 wipe_biometrics -> COMPLETED, Heat 86, Exploits 3, home 50/50, Schematics 50, armory 6
      FIGHT won vs compliance_officer: 3 turns, HP 60 -> 54
      FIGHT won vs dosage_dispenser: 1 turns, HP 54 -> 54
      FIGHT won vs dosage_dispenser: 1 turns, HP 54 -> 54
      FIGHT won vs claims_adjuster: 2 turns, HP 54 -> 50
      FIGHT won vs dosage_dispenser: 2 turns, HP 50 -> 50
      FIGHT won vs recall_unit: 6 turns, HP 50 -> 58
      FIGHT won vs account_manager: 5 turns, HP 58 -> 56
    run 53: Breaker 7 R9 T2 wipe_biometrics -> COMPLETED, Heat 87, Exploits 3, home 50/50, Schematics 99, armory 6
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 4 turns, HP 60 -> 58
      FIGHT won vs billing_daemon: 2 turns, HP 58 -> 58
      FIGHT won vs collections_agent: 3 turns, HP 58 -> 58
      FIGHT won vs account_manager: 5 turns, HP 58 -> 44
    run 54: Breaker 7 R10 T2 wipe_biometrics -> COMPLETED, Heat 84, Exploits 3, home 50/50, Schematics 137, armory 6
      FIGHT won vs billing_daemon: 3 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 58
      FIGHT won vs recall_unit: 5 turns, HP 58 -> 58
      FIGHT won vs billing_daemon: 3 turns, HP 58 -> 55
      FIGHT won vs account_manager: 5 turns, HP 55 -> 32
    run 55: Breaker 7 R11 T2 wipe_biometrics -> COMPLETED, Heat 80, Exploits 3, home 50/50, Schematics 195, armory 6
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 53
      FIGHT won vs care_swarm: 1 turns, HP 53 -> 53
      FIGHT won vs dosage_dispenser: 2 turns, HP 53 -> 53
      FIGHT won vs billing_daemon: 3 turns, HP 53 -> 57
      FIGHT won vs dosage_dispenser: 2 turns, HP 57 -> 57
      FIGHT won vs account_manager: 7 turns, HP 57 -> 47
    run 56: Breaker 7 R12 T2 wipe_biometrics -> COMPLETED, Heat 73, Exploits 3, home 50/50, Schematics 57, armory 6
      FIGHT won vs triage_unit: 3 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 6 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 3 turns, HP 60 -> 54
      FIGHT won vs claims_adjuster: 3 turns, HP 54 -> 48
      FIGHT won vs account_manager: 4 turns, HP 48 -> 48
    run 57: Breaker 7 R13 T2 wipe_biometrics -> COMPLETED, Heat 73, Exploits 3, home 50/50, Schematics 102, armory 6
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 58
      FIGHT won vs care_swarm: 1 turns, HP 58 -> 58
      FIGHT won vs care_swarm: 2 turns, HP 58 -> 56
      FIGHT won vs recall_unit: 7 turns, HP 56 -> 60
      FIGHT won vs billing_daemon: 3 turns, HP 60 -> 57
      FIGHT won vs collections_agent: 2 turns, HP 57 -> 57
      FIGHT won vs account_manager: 4 turns, HP 57 -> 52
    run 58: Breaker 7 R14 T2 wipe_biometrics -> COMPLETED, Heat 70, Exploits 3, home 50/50, Schematics 168, armory 6
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 54
      FIGHT won vs care_swarm: 2 turns, HP 54 -> 52
      FIGHT won vs recall_unit: 6 turns, HP 52 -> 46
      FIGHT won vs billing_daemon: 2 turns, HP 46 -> 46
      FIGHT won vs recall_unit: 7 turns, HP 46 -> 50
      FIGHT won vs account_manager: 6 turns, HP 50 -> 40
    run 59: Breaker 7 R15 T2 wipe_biometrics -> COMPLETED, Heat 70, Exploits 3, home 50/50, Schematics 217, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 58
      FIGHT won vs care_swarm: 2 turns, HP 58 -> 54
      FIGHT won vs dosage_dispenser: 3 turns, HP 54 -> 58
      FIGHT won vs recall_unit: 7 turns, HP 58 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 52
      FIGHT won vs account_manager: 7 turns, HP 52 -> 34
    run 60: Breaker 7 R16 T2 wipe_biometrics -> COMPLETED, Heat 65, Exploits 3, home 50/50, Schematics 87, armory 6
### seed 1003
      FIGHT won vs compliance_officer: 3 turns, HP 60 -> 49
      FIGHT won vs claims_adjuster: 4 turns, HP 49 -> 41
      FIGHT won vs care_swarm: 1 turns, HP 41 -> 36
      FIGHT won vs dosage_dispenser: 2 turns, HP 36 -> 36
      FIGHT won vs claims_adjuster: 3 turns, HP 36 -> 36
      FIGHT won vs account_manager: 7 turns, HP 36 -> 27
    run 52: Breaker 4 R0 T1 scrub_records -> COMPLETED, Heat 43, Exploits 3, home 50/50, Schematics 378, armory 3
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 57
      FIGHT won vs care_swarm: 1 turns, HP 57 -> 51
      FIGHT won vs compliance_officer: 3 turns, HP 51 -> 51
      FIGHT won vs account_manager: 4 turns, HP 51 -> 54
    run 53: Breaker 4 R1 T1 scrub_records -> COMPLETED, Heat 34, Exploits 3, home 50/50, Schematics 78, armory 5
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs account_manager: 5 turns, HP 60 -> 56
    run 54: Breaker 4 R2 T1 scrub_records -> COMPLETED, Heat 39, Exploits 3, home 50/50, Schematics 112, armory 6
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 54
      FIGHT won vs collections_agent: 2 turns, HP 54 -> 58
      FIGHT won vs recall_unit: 4 turns, HP 58 -> 60
      FIGHT won vs recall_unit: 2 turns, HP 60 -> 51
      FIGHT won vs collections_agent: 1 turns, HP 51 -> 51
      FIGHT won vs account_manager: 4 turns, HP 51 -> 47
    run 55: Breaker 4 R3 T1 scrub_records -> COMPLETED, Heat 43, Exploits 3, home 50/50, Schematics 139, armory 6
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 56
      FIGHT won vs claims_adjuster: 2 turns, HP 56 -> 40
      FIGHT won vs account_manager: 3 turns, HP 40 -> 36
    run 56: Breaker 4 R4 T1 scrub_records -> COMPLETED, Heat 48, Exploits 3, home 50/50, Schematics 173, armory 6
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 4 turns, HP 60 -> 56
    run 57: Breaker 4 R5 T1 scrub_records -> COMPLETED, Heat 50, Exploits 3, home 50/50, Schematics 193, armory 6
      raid raid_heat_50: won, home 50/50
      FIGHT won vs compliance_officer: 1 turns, HP 60 -> 60
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 3 turns, HP 60 -> 55
      FIGHT won vs dosage_dispenser: 1 turns, HP 55 -> 55
      FIGHT won vs account_manager: 2 turns, HP 55 -> 50
    run 58: Breaker 4 R6 T1 scrub_records -> COMPLETED, Heat 48, Exploits 3, home 50/50, Schematics 57, armory 3
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 58
      FIGHT won vs dosage_dispenser: 1 turns, HP 58 -> 58
      FIGHT won vs care_swarm: 1 turns, HP 58 -> 55
      FIGHT won vs care_swarm: 1 turns, HP 55 -> 49
      FIGHT won vs account_manager: 5 turns, HP 49 -> 57
    run 59: Breaker 4 R7 T1 scrub_records -> COMPLETED, Heat 49, Exploits 3, home 50/50, Schematics 77, armory 4
      FIGHT won vs triage_unit: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 60: Breaker 4 R8 T1 scrub_records -> COMPLETED, Heat 52, Exploits 3, home 50/50, Schematics 99, armory 4
### seed 1004
      FIGHT won vs account_manager: 3 turns, HP 36 -> 36
    run 51: Breaker 4 R2 T1 scrub_records -> COMPLETED, Heat 35, Exploits 3, home 50/50, Schematics 227, armory 6
      boss loadout: R3 HP 60 deck jolt,jolt,brute_spin,brute_spin,fine_tune,fine_tune,mirror_flip,overdrive,ring_tap,jolt,jolt | daemons tuning_fork | firmware ,patch_plus,overvolt,patch_plus,patch_plus,recycler
      FIGHT died vs renewal_engine: 29 turns, HP 60 -> 60
    run 52: Breaker 4 R3 T4 the_genome_core -> DIED, Heat 49, Exploits 3, home 50/50, Schematics 227, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 54
      FIGHT won vs collections_agent: 1 turns, HP 54 -> 54
      FIGHT won vs claims_adjuster: 3 turns, HP 54 -> 58
      FIGHT won vs billing_daemon: 2 turns, HP 58 -> 58
      FIGHT won vs claims_adjuster: 1 turns, HP 58 -> 58
      FIGHT won vs account_manager: 5 turns, HP 58 -> 54
    run 53: Breaker 5 R2 T1 scrub_records -> COMPLETED, Heat 48, Exploits 3, home 50/50, Schematics 84, armory 6
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 1 turns, HP 60 -> 60
      FIGHT won vs recall_unit: 4 turns, HP 60 -> 60
      FIGHT won vs billing_daemon: 1 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 2 turns, HP 60 -> 54
      FIGHT won vs account_manager: 5 turns, HP 54 -> 53
    run 54: Breaker 5 R3 T1 scrub_records -> COMPLETED, Heat 51, Exploits 3, home 50/50, Schematics 108, armory 6
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 2 turns, HP 60 -> 55
      FIGHT won vs claims_adjuster: 3 turns, HP 55 -> 45
      FIGHT won vs claims_adjuster: 1 turns, HP 45 -> 45
      FIGHT won vs account_manager: 4 turns, HP 45 -> 45
    run 55: Breaker 5 R4 T1 scrub_records -> COMPLETED, Heat 56, Exploits 3, home 50/50, Schematics 135, armory 6
      FIGHT won vs billing_daemon: 2 turns, HP 60 -> 60
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 51
      FIGHT won vs dosage_dispenser: 2 turns, HP 51 -> 55
      FIGHT won vs recall_unit: 6 turns, HP 55 -> 59
      FIGHT won vs compliance_officer: 2 turns, HP 59 -> 60
      FIGHT won vs account_manager: 5 turns, HP 60 -> 55
    run 56: Breaker 5 R5 T1 scrub_records -> COMPLETED, Heat 59, Exploits 3, home 50/50, Schematics 160, armory 6
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 60
      FIGHT won vs collections_agent: 2 turns, HP 60 -> 54
      FIGHT won vs compliance_officer: 2 turns, HP 54 -> 54
      FIGHT won vs recall_unit: 3 turns, HP 54 -> 60
      FIGHT won vs account_manager: 3 turns, HP 60 -> 60
    run 57: Breaker 5 R6 T1 scrub_records -> COMPLETED, Heat 59, Exploits 3, home 50/50, Schematics 181, armory 6
      FIGHT won vs care_swarm: 1 turns, HP 60 -> 54
      FIGHT won vs compliance_officer: 2 turns, HP 54 -> 54
      FIGHT won vs recall_unit: 2 turns, HP 54 -> 54
      FIGHT won vs recall_unit: 4 turns, HP 54 -> 53
      FIGHT won vs claims_adjuster: 2 turns, HP 53 -> 53
      FIGHT won vs account_manager: 4 turns, HP 53 -> 48
    run 58: Breaker 5 R7 T1 scrub_records -> COMPLETED, Heat 64, Exploits 3, home 50/50, Schematics 208, armory 6
      FIGHT won vs care_swarm: 3 turns, HP 60 -> 46
      FIGHT won vs compliance_officer: 2 turns, HP 46 -> 42
      FIGHT won vs billing_daemon: 2 turns, HP 42 -> 46
      FIGHT won vs claims_adjuster: 3 turns, HP 46 -> 38
      FIGHT won vs billing_daemon: 2 turns, HP 38 -> 42
      FIGHT won vs collections_agent: 2 turns, HP 42 -> 42
      FIGHT won vs account_manager: 4 turns, HP 42 -> 32
    run 59: Breaker 5 R8 T1 scrub_records -> COMPLETED, Heat 62, Exploits 3, home 50/50, Schematics 70, armory 6
      FIGHT won vs dosage_dispenser: 2 turns, HP 60 -> 60
      FIGHT won vs compliance_officer: 2 turns, HP 60 -> 60
      FIGHT won vs claims_adjuster: 1 turns, HP 60 -> 52
      FIGHT won vs care_swarm: 1 turns, HP 52 -> 43
      FIGHT won vs account_manager: 4 turns, HP 43 -> 42
    run 60: Breaker 5 R9 T1 scrub_records -> COMPLETED, Heat 62, Exploits 3, home 50/50, Schematics 86, armory 6
