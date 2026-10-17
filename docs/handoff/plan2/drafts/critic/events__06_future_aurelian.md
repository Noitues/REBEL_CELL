<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__06_future_aurelian; status ok; tokens in 3644 cache-write 0 cache-read 32585 out 1646; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/06_future_aurelian

**Verdict:** FIX

## Issues

1. **BLOCKER, R2 / tier rules (choice 1, 3).** `enemy_hp_pct = -30` and `-15` are flat HP multipliers. R2 says "HP by band, not a multiplier", and the combat's HP band is validated per class. The draft never says how the percent interacts with `hp_by_tier`, phase thresholds (R3 floors are ceil(max HP × threshold)) or the validator. A -30 % cut on a normal gives about 31–49 HP at T3, below the 44 floor of the band. On an elite it breaks the 2-phase budget.

2. **BLOCKER, internal contradiction (choice 3).** "Next two fights easier" says `duration 2` and `-15 % each`, and its note says "half the loan's". The player-facing label and the result text are consistent, but choice 3 also adds `player_free_nudge = +1` with no stated duration (turn 1 only, in both fights). The label omits it, so the preview and the label do not match.

3. **MAJOR, text vs mechanic (choice 1).** The punishment (+25 % damage, no free nudge) is not in the label. That is deliberate, but the Q asks whether to hide it. Hiding it conflicts with "previews equal results". Put the penalty in the label. Also, `player_free_nudge = false` is a new field that is never listed, and "+25 % damage" duplicates the R4 enrage step in a way that is easy to confuse with it.

4. **MAJOR, existing systems reinvented.** `enemy_status_start = FROZEN` is not a status. Freeze is a Whole-wheel effect (the target skips its next start-of-turn respin). `reveal_phases` is tied to Chart Hidden, which is an N5 buff, not a general flag. `enemy_resistance = -1` is MODIFY_RESISTANCE and should say so, and Heat's ENEMY_RESISTANCE exists as a RuleModifierType. Reuse these.

5. **MAJOR, balance (choice 2 vs 3).** Choice 2 gives +20 Cycles for free, and its resistance -1 only matters against resistance enemies (Meridian, Halcyon, Compliance Lock). Against most Aurelian enemies it is pure free money, which makes it near-dominant over choice 4. Choice 3 buys -15 % twice for 30 Cycles, so it is also weak next to choice 2 on a net basis. Choice 1 is the only interesting choice.

6. **NIT, Sites and names.** "Lanista", "VERDICT chit" and "arena" are Aurelian lore invented without a source (no Aurelian content exists in the GDD). The draft uses US spelling, and the speaker enum is written as `(1)` (STREET_MERC is index 1, which is correct).

7. **NIT, dependency.** "No data-only fallback" is stated, but choice 2 could use a one-combat override via the existing `ENEMY_RESISTANCE` rule modifier.

## Concrete fixes

- **Fix 1:** replace both HP percents with a post-band reduction:
  `enemy_hp_pct = -20` (choice 1) and `-10` (choice 3), applied after `hp_by_tier`, clamped to 85 % of the class band minimum, with phase thresholds computed from the reduced max HP. State "normals and minis only; elites and bosses ignore it".
- **Fix 2:** choice 3 label: "Pay the toll (-30 Cycles; next two fights: enemy -10 % HP, +1 free nudge on turn 1)".
- **Fix 3:** choice 1 label: "Ride to the box seats (next fight: enemy -20 % HP, Frozen start, phases shown; the one after: enemy +25 % damage, no free nudge on turn 1)". Drop the hidden-penalty Q.
- **Fix 4:** use `start_effects: [FREEZE target TARGET_WHEEL]`, `[MODIFY_RESISTANCE amount -1]`, and `reveal_phases` as an N16 flag tagged "NEW: reveal flag" with its fallback of dropping it.
- **Fix 5:** choice 2 becomes `+10 Cycles` with resistance -1 and `enemy_damage_pct +10` on that fight (a small trade), so it is not free money.

## Keep

- The "loan" structure of choice 1 is a good risk/reward question, and a decision about which of the two fights to be strong for.
- The free "take the stairs" option, and the tone of the arena text.

## Q:
- Q: Should the second fight of choice 1 apply only to the next fight of the same class (normal vs elite), so the punishment isn't dodged by a path choice?
- Q: Do FUTURE overrides apply to Rack or boss fights, or only to Routers?
