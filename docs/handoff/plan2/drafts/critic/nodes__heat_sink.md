<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__nodes__heat_sink; status ok; tokens in 7050 cache-write 0 cache-read 32585 out 1759; cost $0.019. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: nodes/heat_sink

**Verdict:** FIX

## Issues

1. **BLOCKER, §1 vs §2/§5, premise contradicts GDD 4.3.** The draft says it "pays most when it drops you back under a band" and builds the headline combo on that (Example A, the retaliation dodge). But GDD 4.4 says an Exploit extracted at Heat ≥ 50 provokes retaliation, and §5 says the Sink lets you "flush before extracting". That works only if the check reads Heat at extraction time. Heat also rises from the netrun's own gain before the Exploit is captured, and Example A admits "Heat rises by the netrun's own gain" without checking it. The dodge as written is unverified. Flush happens "between runs", so the combo needs Heat ≤ 49 minus the gain of the entire run, which the example never computes.

2. **BLOCKER, §2 band clamp is incoherent.** `sink_max_drop` = 8 is stated alongside "never below the floor of the band below the current one", and Example B contradicts itself: "79 to 74 would not" be allowed, yet it also says "Flush 8 → Heat 80". Two clamp rules exist with no defined precedence. Example B is also muddled: Heat 88 minus 8 is 80, not "79".

3. **MAJOR, §2 sums.** The launder fee after 20 Heat flushed: with +3 charge per netrun, 20 Heat is ~7 netruns, which is nearly the whole 8-run minimum path. The fee almost never triggers, so it is a dead brake. Example C ("flushed 20 across the campaign") is therefore a rare state.

4. **MAJOR, §8 numbers.** "A typical run gains about 4–9 Heat" is unsourced. 70 Heat over 8 runs is ~9 per run, so 3 per run offsets about a third, not "a third to a half". The sim target (70 → 50–60) needs 10–20 Heat of flushing, which is more than 8 runs × 3 = 24 minus the per-run fee. Plausible, but not shown.

5. **MAJOR, §6 invented systems.** `ON_RAID_END` and `GAIN_SINK_CHARGE` are invented, with the fallback only half-stated. Also `adjacency_bonuses`, `partner_type`, `raid_priority`, `triggers_raid` and `profile_unlock_required` are cited as "existing" with no source; the GDD lists none of them. Also `HEAT_SINK_PCT` is hedged in the draft itself ("check whether it already scales"), so the multiplication rule is unresolved.

6. **MAJOR, Site names and the rulings.** Heat Sink and Heat objective Site are grid-view nodes per the D4 ruling ("Safehouse and Heat Sink: grid-view nodes, not netrun nodes"). OK. But the "found Sink from an objective Site" conversion invents a claim variant beyond GDD 4.1 (objective Sites are used up).

7. **NIT, §3.** "campaign stream read only when the Site is generated" is hand-waved; the found-Sink needs no RNG at all, so drop it.

8. **NIT, §5.** PURGE exclusion is stated in prose and in Q3 inconsistently ("not preventable" vs asking).

## Concrete fixes

- **Issue 1:** add to §2: "`sink_extraction_guard`: the Exploit retaliation check reads Heat at Rack capture. Example A must be rewritten: Heat 44, run gain +6 expected, so the player flushes before the run only if Heat stays ≤ 49 after capture. Preview shows 'projected Heat at capture'." Alternatively add the rule that flushing is also allowed at a Rack mid-run (HQ-only today; NEW: in-run flush).
- **Issues 2:** single clamp: "A flush can never reduce Heat by more than `sink_max_drop` = 8 AND may not cross more than one band floor." Redo Example B: Heat 88, flush 8 → 80, still HUNTED; a further flush needs 6 more (75 → FLAGGED at 74).
- **Issue 3:** set `sink_free_flush_total` = 12, so the fee matters by mid-campaign.
- **Issue 4:** replace with "70 Heat over 8 runs ≈ 9 per run; one Sink offsets ≈ 3 (a third)".
- **Issue 5:** make the raid-held bonus resolver-direct (no ON_RAID_END), store charge in a dict, tag "NEW: Sink charge state (S–M)", and mark the `adjacency_bonuses` fields as "verify exists, else add to NetworkNodeData".

## Keep
Charge-and-flush timing distinct from the Proxy Relay and the objective Site; the pure `preview_flush` twin; the preview listing which modifiers switch off and which threshold events will not re-fire; the sim metrics list.

## Q:
Q: Is the retaliation check evaluated at Rack capture or at run end, and does the run's own Heat gain count?
Q: Does a flush happen only at HQ, or may it be allowed mid-run at a Rack?
