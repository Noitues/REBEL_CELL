<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__hq__solace; status ok; tokens in 9581 cache-write 0 cache-read 32585 out 2152; cost $0.024. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: hq/solace

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 layer map vs the text.** The table has Layer 0 gate, rungs 1-9 and crown layer 10, which is 11 layers. The text says "9 rungs plus the crown (10 layers)". §5 says "Nodes on a path: 11". The art has 8 route floors (3..24). The draft tries to add a 9th rung at floor 27 and also place the crown there ("crown sits on the building's top floor"). Rung 9 and the crown cannot share floor 27. The fix ("the crown moves up one floor, or the preset gets 28 floors") is left undecided.
2. **BLOCKER, §2 mid-boss and rung 9 logic.** "The tower you are NOT standing in contains the Account Manager… cross ACROSS at 4→5 and you enter its tower and fight it." This makes the mini-boss exist in only one tower at rung 5. Rung 5 is also listed as "Rest / Fight". Rung 9 then says "one holds the Account Manager if it was not already faced". The draft says both "always fight it once" and "bypass by staying UP" (§2), and then Breach adds a duct that skips it (§4). These contradict each other. The Account Manager's own draft is a 2-phase mini-boss, so it cannot be skipped and still be "always fought once". Also, a 2-fight elite chain at rung 9 is a 12-turn gate directly before the boss, which stacks with the 30-minute estimate.
3. **BLOCKER, §3.3 and §4: "next_combat_overrides" as the pressure carrier, "Cache" as the Server Rack.** The Cache is described as both "optional cache" and "elite-strength combat" at rung 4 in the Ward tower only. The Cache (D4) is a ruled-in node but is not defined here. Pressure +10 % per win is applied to "enemy_damage_pct", which is not a listed field. Pressure also stacks on top of enrage steps with no cap interaction stated.
4. **MAJOR, §3.2 Toll.** "Referral: start your next fight with a CORRUPTED slice" is valid (R9 makes it a RAM debuff). "rung % 4" gives toll 0 at rungs 4 and 8 and 1 at rungs 1, 5 and 9. Rung 9 plus the crown makes the Co-pay toll land on the last crossing. The Audit toll adds Heat, and Heat gives no failure signal, so it is a dominated choice for a player already at Heat 75+. Rule 3.3 says "alternating towers resets neither pressure. It spreads it", so zig-zagging cancels the pressure and costs only tolls. Pressure has no real cost for crossing every rung.
5. **MAJOR, §3.1 / §4.** READ rule says each Exploit adds +1 to the horizon, and Intel "reads the full ladder". Key Fragments add another +1 horizon. Three overlapping systems for one information rule. Intel also "reveals pressure and every toll", whereas §3.2 says tolls are readable ahead. The tolls are already deterministic from rung, so this is redundant. The Virus Exploit effect ("rest removes pressure of the other tower by 1") is weak, and "countered if the Genome Core's Exploit list includes it" is not a coherent rule.
6. **MAJOR, §5 arithmetic.** 5/turn × 3.5 = 17.5, so it matches the "~18" figure. But "6 fights × 18 = 110 HP" against operative HP of 45-60 plus "2 rests of 30 % + events = 60-70 HP" only just covers it, with the elite and mini-boss intake excluded. The rest budget of 2 Ward rests contradicts the rung layout, where rests appear only at rungs 5 (shared with Fight) and 8 (shared with Elite).
7. **MAJOR, §3.4.** Tower weights are drawn from the `hq_graph` stream. But the retry rule gives a "fresh seeded graph" on every attempt, which conflicts with D10's unique-experience intent and removes the learning loop. Also, "Ward's fights use heal-flavoured normals (Triage Unit…)". The Triage Unit is flagged as the worst heal offender, so this is a hazard.
8. **NIT, §8.** "REST node (D4)" is tagged "NEW" but is a ruling, not an N#. Slot generation for 9 rungs is tagged NEW with no fallback. The draft mixes "Key Fragment" (a new currency) into N18 with no tag. §6 references "debts" through N16 only.
9. **NIT, §5.** The `enrage` row says "no change", yet the boss and mini-boss are fought at unspecified tiers. The HQ is T4, but mini-boss bands (R2) are "n/a" at T4. This is a rule gap the draft must acknowledge.

## Concrete fixes

- **Layers:** state "gate (L0) + 8 rungs (floors 3-24) + crown (L9) = 10 layers, 9 on the path", with the crown above floor 24 (an art ask for one extra crown floor, not a 9th rung). Rewrite §5: "Nodes on a path: 10".
- **Mini-boss:** fix it at rung 8 in both towers (one fight, either tower leads to it), delete the Breach duct and the "rung 9 chain". Replace the rung 5 Rest/Fight row with Rest in Ward and Shop in Billing.
- **Pressure:** cap at +30 % applied additively to the enemy's damage factor (R2 buff rule), and add "crossing adds +1 pressure to the destination tower".
- **Rests:** rungs 3 and 6 are a guaranteed Rest in Ward (A only), and Billing gets a Shop at rungs 3 and 6.
- **Read:** drop Key Fragments. Keep "+1 rung per Exploit owned; Intel reads all".

## Keep

The two-lane ladder with the toll is a strong, unique spine. Deterministic tolls from the rung are previewable. The art-state hooks table is clean.

## Q:

Q: Should crossing cost pressure or a toll, not both?
Q: Is a retry graph unique each time, or the same seed with the learned route?
Q: Is the mini-boss mandatory?
