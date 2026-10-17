<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__17_ambush_orbital; status ok; tokens in 3601 cache-write 0 cache-read 32585 out 1799; cost $0.016. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/17_ambush_orbital

**Verdict:** FIX

## Issues

1. **BLOCKER, N16 / systems, "on_defeat_effects", "on_victory", "enemy_hp_by_tier read at the raised tier".** N16 lists only `starts_combat`, `combat_overrides`, `map_edits`. `on_defeat_effects` and `on_victory` are invented fields. The loss rule is also unclear: the operative dies on defeat (GDD 4.2), so a +4 Heat "stake paid on defeat" is mostly moot. `enemy_hp_by_tier` is not a field either; the real field is `hp_by_tier` (N2).
2. **BLOCKER, tags / existing systems, "(the relay starts frozen, using the existing FREEZE rule)".** FREEZE makes the target skip its next start-of-turn respin. It does not skip the enemy's turn. The text also says "first-turn burst", but the player resolves simultaneously with the enemy at End Turn, so the frozen relay still resolves. The effect as described does not exist. Also unclear is the Daemon "from the Server Rack rare pool", with random draw added to a checkpoint stream (fine, but no stream/checkpoint tag).
3. **MAJOR, R2 arithmetic, "At T+1 the relay is in the next band up".** Chase on a T2 node uses T3 values: Normal T3 band 44–56 HP. 14 × 3.5 = 49, which is correct. But the note says "T2 node: 44–56; T3 node: 56–70", which is wrong: T2 is 34–44. Also the note ignores that a node at T3 gives a T4 relay with 56–70 HP, about 63/14 ≈ 4.5 turns, out of the 3–4 target. Cap behavior is left open (Q2) and needs an answer.
4. **MAJOR, balance / dominance, Choice 2.** Verify costs 12 Cycles for a common Firmware, with no loss penalty and (if the freeze worked) an easier fight. Compared with Choice 1, there is no stake except the Heat. A common Firmware on a normal-tier fight is a reasonable reward, but the mismatch with Choice 1 (Daemon + 15 Cycles) is large, while Choice 1's risk is mostly "you may die". The loss is permadeath, and that is not weighed in the notes.
5. **MAJOR, template / R-scope, "uplink_relay".** Its design is not shown, so "Daemon from the rare pool" and "one-phase normal" can't be verified. The text claims the relay "is guarding a gift", but the enemy's Hub traits are not used at all. Also the "Billing Loop" comparison cites an event not in the provided list.
6. **NIT, template.** `dispatch_clue: false` should be an empty field since none exists. "Voice" should be `STREET_MERC` (enum OK). The one-line text "Rumors cost nothing until you act on one" is fine. The fallback ("HP-cost 8 for the Daemon at a 50 % lower reward") is incoherent: a Daemon cannot be 50 % lower.
7. **NIT, length.** About 760 words; OK.

## Concrete fixes

- **Issue 1:** Replace `on_defeat_effects` / `on_victory` with `combat_overrides` (N16) plus the existing win reward flow. Write: "(new) starts_combat: enemy `uplink_relay`, combat_overrides: {tier_delta +1, cap = run tier}; stake: `hp_cost` 8 paid on entry (not on loss); reward on win: Daemon + GAIN_CYCLES 15. Loss is the normal operative death." Drop the Heat-on-defeat stake or move it to a flee-free "fight is forced" statement.
- **Issue 2:** Replace the freeze line with: "combat_overrides: relay starts with 25 % less HP (`hp_pct` −25) and its first slice is NULL (wheel_override at start)". Tag: N16 + N3 (wheel_override), fallback: reduced `hp_by_tier` only.
- **Issue 3:** Replace the R2 check with: "Node T2: relay at T3, 44–56 HP, 49 ÷ 14 = 3.5 turns. Node T3: relay capped at T3 (cap = run tier), so 3.5 turns. T4 not reachable."
- **Issue 4:** Raise Choice 2's reward to an uncommon Firmware, and tie the cost to Cycles 12 plus HP 4. Alternatively, give Choice 1 a real stake via `hp_cost` 8 on entry.

## Keep
- The four choices cover distinct economic positions (fight, safer fight, sell, skip), and "sell for Cycles + Heat" is a clean alternative.
- The text voice is strong and fits the tone, with a rumor framing that explains why the fight happens.
- The Daemon draw on a win only, from the checkpointed `events` stream, is a good determinism call.

## Q:
- Q: Is the impromptu fight allowed to be lethal (operative death, GDD 4.2), or does a loss end the node with a retreat?
- Q: Should `uplink_relay` be a normal at all, or does an ambush merit an elite (2 phases) for a Daemon reward?
