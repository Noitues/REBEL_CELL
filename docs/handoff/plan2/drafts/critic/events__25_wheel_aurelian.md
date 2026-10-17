<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__25_wheel_aurelian; status ok; tokens in 3891 cache-write 0 cache-read 32585 out 1917; cost $0.017. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/25_wheel_aurelian

**Verdict:** FIX

## Issues

1. **BLOCKER, arithmetic, wheel table:** The sizes sum to 4+5+6+7+3+5 = 30, which is correct. Choice 2 breaks it: "Arena Bout 6 → 3, Bread Dole 4 → 7" gives 4→7 (+3) and 6→3 (−3). The sum is still 30, but Bread Dole (7) now ties Fine Print for the largest slice. The note "widens the Bread" is fine. The real problem is that the bribe's EV swing is never computed against the new sizes. The "~+8 EV" figure is unsupported, and the unsteered EV line is incoherent: it omits the Null Clause slice, uses 20 % for Arena Bout, and mixes Cycles, HP and Heat with no conversion.
2. **BLOCKER, R11 and tier model:** "Perfect centre of Patron's Favor grants +10 Cycles; WEAK edges on Bread Dole pay 50 %." Under the R11 default map, a 3-tick slice is G P G, so Patron's Favor has a Perfect tick. A 4-tick slice (Bread Dole) is W G G W, so WEAK edges exist, which matches. The Perfect and WEAK riders are not listed in the slice outcome column, so the outcomes are incomplete. The "Patron's Favor is Perfect-only" claim in the notes is also false: its outcome fires on any tick.
3. **BLOCKER, ground rules, starts_combat on a slice:** Arena Bout is `station_commander`, an elite (154 HP at T3). A forced elite at low HP with no refusal is an unmanaged lethality spike. "flee/lose = standard death rules" has no flee mechanic in the GDD. Stakes must be explicit, so the combat needs a defined stake. Also, N16 (`starts_combat`) is not tagged anywhere. Only N17 is named, and only in the fallback.
4. **MAJOR, template and systems:** No N# tags appear anywhere. `event_wheel` needs N17, `starts_combat` and the size overrides need N16, and N12 (variable sizes) is optional for N17. The fallback "4-choice event with fixed outcomes" is stated, but a data-only version of the steering decision is not.
5. **MAJOR, economy and the nudge cost:** "Extra nudges cost 6 HP each... Max 5 extra" allows 30 HP of loss for a chance at a 12 HP heal. This is dominated, and the forge (+30 Cycles, +2 Heat, no variance) beats the unsteered wheel outright. The ability to pay HP *or* Heat is an undefined player pick with no UI spec. The Heat-for-nudge question also exposes an unspecified Heat-threshold timing.
6. **MAJOR, choice 2:** It cuts the budget to 1 nudge while costing 35 Cycles, so the bribe is both pricier and weaker at steering than choice 1. The EV difference comes mostly from removing Arena Bout, so the choice is "pay 35 to avoid the fight."
7. **NIT:** Fine Print is written as "DRAIN: hp_cost 8", but DRAIN_RAM is an existing EffectType for RAM, not HP. Use an HP-loss field. "Common Firmware" and "uncommon card" are unscaled. Spelling is OK.

## Concrete fixes

- **Fix 1:** Remove the EV sentence. Replace with: "Unsteered EV per spin (Cycle-equivalents, 1 Heat = 10, 1 HP = 3): Bread 4/30×40 + Circus 5/30×30 + Arena 6/30×(60−45 risk) + Fine Print 7/30×(−24−30) + Favor 3/30×(36+20) + Null 0 ≈ 5.3+5+3−12.6+5.6 = +6.3. Bribe: Arena 3, Bread 7 gives 7/30×40 = 9.3 and Arena 1.5 for a total ≈ +10.7, worth +4.4 for 35 Cycles, so the bribe is a bad deal unless the player fears the fight."
- **Fix 2:** The wheel table is the table to paste. Add the tier riders column: "Bread Dole: WEAK ×0.5 (+20); Patron's Favor: Perfect adds +10 Cycles; others tier-independent."
- **Fix 3:** Arena Bout stake: "Optional: the player may pay 20 Cycles to waive the fight (outcome becomes Null Clause). Win = common Firmware + 35 Cycles. Lose = normal death. (N16 `starts_combat`.)"
- **Fix 4:** Add "(N17, N12 optional, N16)" to the wheel and combat lines. Fallback: three fixed offers (Bread +25; card; gamble 50 %: elite fight).
- **Fix 5:** Extra nudge cost: "3 HP *or* 1 Heat each, max 3; track the choice per nudge via a prompt."
- **Fix 6:** Bribe: "Nudge budget stays 2; cost 25 Cycles."

## Keep

The uneven six-slice wheel with a tiny 3-tick favor slice is a good steering puzzle. The deterministic `events` stream with checkpoint and undo is stated correctly. The forge as a safe, inflationary baseline option is sound.

## Q:
- Q: Should the elite ever be forced, or always waivable?
- Q: Should Heat spent on nudges apply thresholds immediately, or at event end?
