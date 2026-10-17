<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__corp__solace; status ok; tokens in 63144 cache-write 0 cache-read 32585 out 3006; cost $0.081. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: corporation solace

**Verdict:** FIX

## Roster variety

| draft | class | the one question | hook relied on |
|---|---|---|---|
| billing_daemon | normal | what is your RAM worth? | N6 Late Fee (paid nudge → BLOCK), RAM drain slices |
| compliance_officer | normal | what does your landing cost? | N6 Audit (paid nudge → BLOCK), resistance 2 |
| collections_agent | normal | which slice reads, can you get past the guard? | satellite on Dose, Overflow |
| care_swarm | normal | steer onto the core or a drone? | 2 fixed satellites, Tend |
| dosage_dispenser | normal | which slice is it dosing? | CORRUPTED RAM x2, hub dose |
| triage_unit | normal | can you keep the needle off Hotfix? | 4-tick Hotfix, conditional hub heal |
| claims_adjuster | elite | which needle reads the danger / deny its Perfect? | 2 needles, TIER_DOWN, listeners |
| recall_unit | elite | read an orbit, then pay for Perfects | ORBIT, Recall Tag (ON_PERFECT) |
| account_manager | mini | steer vs pay, then pay for Perfects | Late Fee, fixed guards, Clawback |
| renewal_engine | boss | corruption spiral, 2 needles | N5, N12, N20, N9 |

**Too similar:**
- billing_daemon, compliance_officer and account_manager P1 all use the same listener: a paid nudge gives the enemy BLOCK 2–4. That is three copies of one idea, and compliance_officer even renames its own Heat effect "Late Fee" to avoid clashing. Rework compliance_officer to a pure resistance and lockout question: no Audit listener, resistance 3 with a Flip/Respin block and a large Defrag-free window. It is the only resistance enemy and should stay data-only.
- account_manager P2 Clawback and recall_unit P2 Recall Tag both tax Perfects with a flat 4 damage, and claims_adjuster P2 Fine Print is a third Perfect punisher. Keep Clawback (mini-boss). Rework recall_unit P2 to a tracking question: Lock-On plus no defence, with no Tag. Rework claims_adjuster Fine Print to a different hook, such as the TIER_DOWN Denial slice alone.
- collections_agent and care_swarm are both "bodyguard on an attack slice". Make collections_agent about the Overflow/Null spin (its good 15-tick swap idea) and drop its drone, or move the drone to the Overflow so it teaches something different.

## Phase and hook overlap
- The "Perfect tax" appears in four drafts and "paid-nudge tax" in three, so listeners are the Solace signature. That is acceptable only if each is distinct.
- Elites use two phases with a Perfect gimmick in both. Put a different question in each: recall_unit P1 ORBIT (kept), P2 non-Perfect.
- No normal teaches a status stack (OUTPUT_DOWN) or the parasite ring. Solace never introduces the Perfect-denial 1-tick nudge cleanly before the boss, though P2 of the boss relies on it. The Triage Unit's 4-tick slices are the only place that teaches "no Perfect". Add an early denial lesson to claims_adjuster P1, since its Overflow is 3 ticks.
- The Genome Core's corruption spiral is taught only by dosage_dispenser. Good, but the Dispenser needs N9. Without it, the teaching step is missing.

## Systems used
- N1, N2 are used by all. N12 is used by 9 of 10 drafts, so it is the central dependency; most fallbacks lose their core read without it.
- N6 is used by billing_daemon, compliance_officer, account_manager, claims_adjuster, recall_unit and care_swarm (Tend), but not by the boss. Shared, so it is worth building.
- N9 is used by dosage_dispenser, collections_agent, claims_adjuster, account_manager and the boss. N3 and N4 are used by every elite and above.
- Single-use or NEW: recall_unit's `lock_on_nudge`, triage_unit's `hub_condition`, boss's `inert_pointers`, dosage_dispenser's end-of-turn hub dose (RNG preview). The HQ adds a ladder generator, read horizon, tolls, tower pressure and a REST node. That is too many for one corporation; Solace as the first corporation should lean on shared systems.
- Events need N16/N17 (wheel, paths, ambush). The ambush also needs `win_condition_min_hp_pct`. Note that events 1–3 each require a different N16 field.

## Difficulty curve
- Normals target 3–4 turns at tier bands, fine. The Triage Unit at T4 predicts 4.5 turns and the Dispenser 4.3, slightly high.
- Elites at 6–8 turns; claims_adjuster T4 at 85 % win and recall_unit T4 at 75 % are low next to the ≥ 90 % criterion at T3. Recall_unit T3 at 92 % is borderline.
- The mini-boss is placed at HQ rung 5 and rung 9. The HQ draft uses T4 for all, so Account Manager (T1–T3 only, with no T4 hp entry other than a copy) is out of band in the HQ. Fix.
- The boss costs about 55 HP net against a 45–60 HP operative. That is near-lethal without a rest, and the HQ's Ward path gives only about 60–70 HP. Combine with tower pressure up to +40 % and the run is unbalanced. The roster's teaching of corruption (Dispenser) and Perfect denial is thin for a boss that needs both.

## Identity
- Billing, collections, compliance, triage and recall read strongly as Solace. The care_swarm and dosage_dispenser fit. The Genome Core's doctor/disease concept is excellent.
- The HQ is the weakest fit: the two towers, tolls and read horizon are structural, with little medical or billing flavour. Toll names (Co-pay, Referral, Audit) help. The event `ev_sol_payment_plan` and `ev_witness_statement` are on theme; `ev_sol_courtesy_waiver` is generic.
- The old GDD "Compliance Lock" is now only compliance_officer's resistance. Good.

## Concrete fixes
1. compliance_officer: remove the Audit listener and rename nothing; restore resistance 3 and keep the 3-tick Overflow and 7-tick Shim. Question: "can you work around a lock?"
2. recall_unit: drop Recall Tag; P2 becomes undefended with Lock-On (or the data-only orbit-2 fallback). Keep P1 as is.
3. claims_adjuster: drop Fine Print and Audit listeners; keep two phases on uneven needles (0/15 → 0/11) and TIER_DOWN. This removes N6 from the elite.
4. collections_agent: dock the drone on Overflow, not Dose. Add a note that it is the first drone teaching.
5. dosage_dispenser: replace the hub dose with a third Dose slice (its stated fallback), to avoid a preview-with-odds hub rule and `hub_condition`-type fields. Cap CORRUPTED at 3 slices.
6. triage_unit: use an unconditional 2 % heal (its fallback) instead of NEW `hub_condition`. Trim T4 HP to 54.
7. account_manager: author a T4 entry in the HQ run or restrict the HQ to its elite chain. Keep Late Fee as the one paid-nudge listener, and do not use it on billing_daemon (change billing to pure RAM-drain slices).
8. renewal_engine: confirm `inert_pointers` goes into N11. Reduce net intake so a full fight costs about 40 HP.
9. hq/solace: cut tower pressure and the Waiting Room; keep the two lanes, tolls and rests. Use T4 enemies only from rung 5 onward, with T3 earlier. Make the mini-boss appear once.
10. events: unify the event override fields into one N16 list. Move the wheel event off the "free Heat and Cycles" template, and set an explicit stake loss for the ambush.

## Q:
Q: Is the paid-nudge tax meant to be one shared Solace listener (build once, three users), or per enemy?
Q: Should the HQ lower enemy tier to T3 early to preserve the teaching curve?
Q: Should the boss's net lethality be set from the Q12 win-rate target before the HQ pressure rules are written?
Q: Is "Perfect tax" reserved for the mini-boss only so the boss can subvert it?
