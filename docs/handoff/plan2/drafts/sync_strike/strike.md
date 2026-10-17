<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01HFX5TWLWfqpfJ3uJgywfZs, custom_id sync__strike; status ok; tokens in 41074 cache-write 32585 cache-read 0 out 6235; cost $0.113. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# sync_strike: design options

## 1. Constraints

**What exists**
- A combat is one player wheel against one enemy side. `netrun_session` holds one operative. Nothing runs three wheels, and the Hub, RAM, hand and free nudge are all per-combatant.
- The round-1 HQ draft (REBEL_CELL) already proposes a three-lane run with a shared step clock and a synchronised kill-switch throw. Each operative has its own HP, RAM and deck, and a parked operative gives a passive and absorbs one hit per phase. That draft ends with "one operative enters DISPATCH core", which answers Q-B with "no rotating focus". This pass must either confirm or overturn that.
- The DISPATCH boss draft (5 phases, T4, 300–400 HP, 12–20 turns) is a one-wheel fight. A rotating-focus final fight would replace or wrap it.
- R1 gives an HQ boss 4–5 phases of 3–4 turns each. Normals are 1 phase and minis are 2–3. Sync Strike's "small fights" must fit those classes.
- Preview must equal the result, and undo and checkpoints are per turn. Any multi-wheel turn needs one checkpoint model.
- N6 (listeners), N3 (phases, parking), N13 (fixed satellites), N16 (`next_combat_overrides`) and N7 (locks) are the available tools.

**Operative counts**
- Campaign start is 2 rookies, and operatives die permanently. A strike that needs exactly three living operatives can soft-lock a campaign.
- Ruling: the fight is built for N = 1, 2 or 3 and never refuses to start. Fewer operatives means fewer mini fights and a different final shape, not a failed strike.
- Rule of thumb: one operative = the boss at its base shape (the existing DISPATCH draft, with a penalty for lacking support), two = a pair, three = the full form.
- The designer's "a small fight for each operative" is interpreted as per living operative.

**HQ length and uniqueness (G12, D10)**
- The HQ run may exceed 7 layers and every HQ is unique. REBEL_CELL's unique angle is "it knows you": the profile-built corporation.
- Mini fights should be inside the run (the end of each lane or a late layer), not a separate screen, so the run structure stays one netrun.

**Determinism**
- Mini-fight results become structured tallies, not RNG. The final fight's modifiers are a pure function of those results.

## 2. Three options

### Option A: Lock-Breaks (sequential, one wheel at a time)
Closest to NB-1 as originally written and to the round-1 HQ draft.

**Structure**
- N mini fights, then one final fight. Each mini fight is a Mirror "lock": a 1-phase elite-class enemy (3–4 turns) fought by that operative on its own wheel against a copy of that operative's own build (M11 Mirror at ×1.5 output, one pointer).
- R2 budget at T4: a lock has 56–70 HP (normal band; the Mirror has no sustain), so 18 × 3.5 = 63.
- Final fight: the DISPATCH core as one chosen operative (one wheel), 4 phases, with HP reduced by what the locks removed. Totals: 3 × 3.5 + 14 = about 24 turns, 12–20 for the boss alone.
- Final fight HP: 300 base minus 15 per clean lock, so it can drop below the phase budget; keep P1–P4 and let a lock remove a phase instead (see Q-A).

**Q-A: each lock removes one thing from the final**
- A lock won cleanly at 100 % HP removes a buff or phase; a lock won hurt removes less (a half removal).
- Breaker's lock removes the Forecast Strike double (P1).
- Ghost's lock removes the resistance and the Quorum buff.
- Rigger's lock removes the Late Fee listener (P2).
- A lost or skipped lock leaves the thing in. Archetype-to-removal pairing is fixed by class, so the player knows in advance what each operative buys.

**Q-B: no rotating focus**
- One wheel is live in the final. The other living operatives are parked: a class passive plus one absorbed hit per phase (the HQ draft's rule). Focus is chosen once, before the final.
- Turn UI is the normal one. Preview and undo are unchanged.

**Teaches:** each class's identity against a mirror of itself, then a single clean boss puzzle.

**Readability:** excellent. Nothing new on screen except parked tokens.

**Failure and retry**
- Death of the chosen operative in the final: the next parked operative takes over at the current phase with fresh HP (a "handoff"), and the boss keeps its HP. Strike fails only when all are dead.
- A lost lock leaves that operative alive with half HP and no removal.
- Fewer than three: only living operatives fight a lock. One operative = one lock, then the boss alone.

**Narrative:** the Cell's tools are used against it one at a time, and DISPATCH admits each lock fell.

**Total:** about 24 turns, in four fights.

**Weakness:** it does not use the designer's rotating-focus idea. Three of the four fights are a single wheel, so the strike is "more fights", not a new question.

### Option B: Rotating Focus (all three wheels in one fight)
The literal Q-B reading.

**Fight structure**
- N mini fights (a lock each, as in A, but each is 1 phase, 3 turns; N × about 3 = 9 turns), then one **Convergence** fight: all living operatives against DISPATCH at once.
- The boss has 4 phases of 3–4 turns (R1), 12–16 turns total. HP is budgeted against the combined damage of all focused hits, with one damage-dealing focus per turn.
- Total about 24 turns.
- At 3 operatives the damage budget is `reference_dpt` × 3.5 per phase for one focus-turn hit, so the HP stays at 300–360. Extra wheels do not raise DPT; they raise options and defence.

**Turn UI: what "focus" means**
- Three wheels are on screen: the focused one large, the other two docked small. Each operative has its own wheel, RAM pool (+4 per turn, max 12, start 6), hand (draw to 5) and free nudge.
- **One focus is the actor per turn. Every wheel still resolves at End Turn.** The focus decides where your actions go.
- **Swap:** a free "focus" action selects another wheel. Actions (cards, nudges, spins) apply to the focused wheel only and spend that operative's RAM and cards.
- **Budget:** each operative's free nudge and RAM are tracked separately. A shared **Command budget** of 3 swaps per turn keeps the turn bounded. The 4th swap costs 1 shared RAM from the focused operative.
- **Resolution:** at End Turn all pointers on all three wheels resolve at once, following the existing order (defence, offence, statuses). Each operative's own wheel hits the boss. DISPATCH's pointers hit one operative each according to a **Target rule**: a boss pointer at tick t targets operative (t mod N), deterministic and shown before End Turn.
- **Preview:** a per-operative chip shows its damage dealt and taken. A boss pointer is drawn with a line to its target operative.
- **Undo and checkpoints:** a single turn timeline. Undo and rewind run back to the start-of-turn respin across all three wheels; swaps are part of the staged action list, so they undo with it.
- **Random events:** one respin per turn covers all wheels, in operative order (L, C, R) on one named stream.
- **Boss damage and parking:** the boss HP floor applies to the sum of all three hits in one resolve (R3), so burst is lost at thresholds as normal.

**Q-A**
- A mini fight sets that operative's **starting state in the Convergence**, not a removal.
- A clean win banks a **Charge**: a one-use boosted action in the final (Breaker: one slice resolves ×2; Ghost: strips the boss's resistance for a phase; Rigger: +4 RAM to any operative).
- A hurt win carries HP over; a loss means no Charge.
- Charges are visible chips, spent from the large focus view, so the minis are an investment.

**What it teaches:** triage across three wheels, operative roles (who needs RAM, who is under fire), and the class kit as a team.

**Readability:** the main risk. Three wheels plus a hand per operative is a lot, and the HUD v4 layout has room for two wheels. The docked wheels must show a one-line result chip (slice, tier, damage). Needle geometry (uneven needles) gets hard to read across wheels, so P3 and P5 must keep pointers on the focused wheel readable.

**Failure and retry**
- An operative at 0 HP goes dark for the rest of the fight (its wheel stops resolving and its Charges are lost). The fight continues with the others; DISPATCH's pointers are retargeted by (t mod living).
- A fail needs all dead.
- A retry is a fresh Convergence after the minis, which re-arm.

**Fewer operatives:** two wheels (a pair fight), one wheel (the Option A final). HP is re-banded per N (300 → about 270 → 240 so a lone operative faces the normal boss draft).

**Narrative:** "DISPATCH sees one hand at a time; you move three." The boss line breaks when the third wheel acts.

**Total:** about 24 turns; the turn count per operative action is high, so real time is longer.

**Weakness:** the largest UI, preview and RAM build, and the highest interaction cost per turn. It may feel like management rather than the core wheel puzzle (pillar 1).

### Option C: Relay Strike (rotating focus across phases, one wheel live per turn)
The hybrid: keeps the rotating-focus identity without making the player operate three wheels in one turn.

**Fight structure**
- N mini fights as in A (3.5 turns, one wheel each), then the final fight: DISPATCH, 4 phases.
- **Each phase is fought by a different operative** (the one the player assigns to that phase from the living roster). The other two are on the bench: their wheels are shown small and their hands are frozen.
- A phase is 3–4 turns (R1). Total final: 12–16 turns, with three of the four phases handled by different people.

**Turn UI**
- One live wheel, the normal UI. At the phase boundary (parking is the handoff moment), the player picks who steps in. HP, RAM, deck and Firmware belong to that operative.
- **Benched operatives are not idle:** each benched operative contributes its **Overwatch**, a class passive from the HQ draft, plus it absorbs the first hit per turn that would reach the live operative (its HP pays).
- **Swap mid-phase:** one "Tag in" per phase, costing the bench operative 3 RAM. The incoming operative takes the same turn's remaining actions. The hand is unchanged.
- Undo and checkpoints are normal within a turn. The tag-in is a staged action.
- End Turn, preview and RNG are the existing single-wheel ones. The live operative's RAM and nudges refresh only when it is live; benched RAM does not accrue (so tagging in does not double the economy).

**Q-A**
- Each mini fight picks that phase's **variant**: the boss phase that operative is assigned to is *the same phase the lock modelled*. If operative X won its lock, its phase's strongest rule is off (Forecast double for Breaker's phase, Late Fee for Rigger's, resistance for Ghost's).
- The three minis are literally the three phases' previews: P1 mirrors Breaker's lock, P2 Rigger's, P3 Ghost's, P4 and P5 are the full strike.
- Concrete: Breaker wins its lock cleanly and enters P1 with Forecast off. Ghost loses its lock and enters P3 with resistance 2 on (and a free first nudge ignoring it from the class core).

**What it teaches:** class identity against its own counter, then the handoff as a decision (who takes the burst phase).

**Readability:** high. One wheel at a time, so the existing UI works. New: roster strip, bench tokens, tag-in button.

**Failure and retry**
- A dead live operative is replaced at the next boundary or immediately by a free tag-in at half RAM; the benched operatives keep HP.
- Fewer operatives: one operative runs all phases, with no tag-in and no bench passives (the boss at its base draft). Two operatives alternate phases.

**Narrative:** a relay: "DISPATCH planned for one of you. It did not plan for the handoff."

**Total:** about 4 × 3.5 + 14 ≈ 28 minutes of play; about 24 turns.

**Weakness:** it is a rotating focus by phase, not by turn. The designer may read this as a diluted Q-B.

## 3. Comparison

| | A Lock-Breaks | B Rotating Focus | C Relay Strike |
|---|---|---|---|
| Final-fight wheels live | 1 | 3 at once | 1, rotates per phase |
| Q-A answer | Removes buffs | Banks Charges | Strips that phase's rule |
| Q-B answer | No | Yes, literal | Yes, per phase |
| New UI | Parked tokens | Three-wheel HUD, target lines | Roster strip, tag-in |
| Preview and undo risk | Low | High | Low |
| Fewer than 3 operatives | Easy | Needs re-banding per N | Easy |
| Core pillar fit | Strong | Weak (management) | Strong |
| Build size | M | L+ | M–L |
| Turns | ~24 | ~24, longer real time | ~24 |

## Recommendation

**Build Option C, with Option B reserved as a later "full strike" variant.**
- It is the only option that keeps one wheel puzzle per turn (pillar 1) while giving the three operatives a real role in the final and answering both of the designer's questions.
- Q-A ties each mini fight to a specific phase, which gives the minis a reason to exist and makes failure partial rather than binary.
- Q-B is answered by rotation at phase boundaries, which are already the natural pause points under R3 parking.
- It degrades cleanly to 2 and 1 operatives, which Option B does not.
- The B preview and undo risk (a multi-wheel staged-action model with one checkpoint) is the largest source of determinism bugs in the plan. Defer it until C has playtests.

## 4. Systems and data

**Existing systems used:** N3 (phases and parking, the handoff moment), N4 (enrage), N5 (boss buffs; the Q-A removals are runtime buff-offs), N6 (listeners), N13 (fixed satellites), N16 (`next_combat_overrides`, the lock results), N11 and N12 for the boss layouts.

**NEW systems**
1. **NEW: multi-combat boss run (NB-1, size L).** A run-level strike state: a list of mini fights, per-operative results, and a final fight started with `strike_modifiers`. Minimum data-only version: a fixed sequence of three scripted nodes at the end of the HQ route, each a normal combat with an authored override.
2. **NEW: operative handoff.** A combat-level swap of the player combatant (wheel, deck, RAM, HP, Firmware) at a phase boundary or on a tag-in. Medium. The phase boundary is already a safe, checkpointed point. A mid-phase tag-in is the risk; ship boundary-only first.
3. **NEW: bench state and Overwatch.** Per-operative `parked_support` data rows, plus a redirect-one-hit-per-turn rule. The HQ draft already needs this.
4. **NEW: strike results.** A small record per lock: `clean`, `hp_lost_pct`, `lost`, written by N16 and read by the final. A pure function, saved.
5. **N19 sim metrics:** turns per phase per operative, and removals fired.

**Data-only minimum (no handoff code)**
- One operative runs the whole final. The three locks run as ordinary Mirror elites before it, and each clean win removes its rule through `next_combat_overrides`. This is Option A with C's Q-A mapping. It is a valid first ship.

**Build order**
1. N3, N4, N5, N16 and the DISPATCH boss draft (one wheel).
2. The data-only strike: locks plus removals.
3. Strike results record and the roster strip.
4. Phase-boundary handoff and bench Overwatch.
5. Mid-phase tag-in. Then re-evaluate B.

**Dependency on the route/HQ redesign (G12):** the locks live at the end of each lane in the HQ draft, so the strike needs the HQ graph to place three scripted nodes. The data-only strike can ship before the full three-lane run if the HQ route has any late slot for them.

**Test list**
- A strike with N = 1, 2 and 3 completes with the correct number of locks and phases.
- Lock results are identical across save and reload at every boundary.
- Handoff at a phase boundary preserves each operative's HP, RAM, deck and Firmware, and the boss HP floor is not reset.
- Preview equals result across a handoff, and undo cannot cross a phase boundary.
- A dead live operative triggers the correct replacement and no state leak.
- Removals apply only to the intended phase, and a lost lock leaves the rule on.
- Enrage steps count across handoffs (the turn counter is the boss's).

## 5. Open questions

Q: Is phase-boundary rotation (Option C) enough of a "rotating focus" for the designer, or is per-turn swapping across three live wheels (Option B) a requirement?

Q: Should a lost lock cost the operative anything permanent (HP only, or a possible death), or only deny the removal?

Q: With one operative, does the strike run at all, or is DISPATCH a plain boss fight on that route?

Q: Should the locks be tied to class (each class gets its own phase rule) or to the operative's equipped Firmware (the profile-built Mirror idea from GDD 8.5)?

Q: Does a benched operative's HP pay for absorbed hits, risking a permanent death off-screen, or is the bench absorption capped at their HP floor of 1?
