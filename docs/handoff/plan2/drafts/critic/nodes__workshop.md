<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__nodes__workshop; status ok; tokens in 7184 cache-write 0 cache-read 32585 out 1804; cost $0.019. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: nodes/workshop

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 vs §3, "layers 1–3 → I" and "Count: 0–1 per netrun at layers 3–5".** The gating contradicts the placement. A layer-3 Workshop can only offer Level I, and the layer-6 Workshop is the only one that reaches III. The ~0.9 per run figure also conflicts with "T2+ gets at least one, T1 none": T1 netruns get 0, so T2+ must average well above 1. The "~7 visits per campaign" arithmetic is unsupported. Placement is internally inconsistent, so the economy can't be judged.

2. **BLOCKER, §2 and §5, GDD 4.2 and "Schematics are not spent at the node".** Cycles → Schematics converts at 10:1 on completion. The cost table (40–160 Cycles) is therefore 4–16 Schematics, and a full-price Level IV rivals a class unlock. It is never compared against the Cycles earned per run, so the costs can't be judged.

3. **MAJOR, §5, "Workshop License" gating.** It makes the node dead weight on the first run after a campaign starts. It also contradicts §3 ("a netrun on T2+ gets at least one Workshop") and the 3-greyed-offers example. A guaranteed node that is locked is a wasted route. It also uses `profile_unlock_required` while saying it is a campaign unlock. Pick one layer: profile (permanent) or campaign (Schematics).

4. **MAJOR, §3, "A new named stream `workshop`" and "weight eligible targets".** The draft doesn't say how a stream seed is derived. The offers must be generated on entry from checkpointed state. Reload-safe is claimed, but a rewind or abandon path isn't covered. Also "Daemons: Overclock Bench … CORRUPTED for the next combat" makes up a CORRUPTED rule on a whole slice. Under R9, CORRUPTED is a RAM debuff, so this is fine mechanically, but it needs a note. Pending the slice pass, the Daemons are invented content. Mark them as examples, not ids.

5. **MAJOR, §6, "Fallback ... +25 % output (FLAT +1 minimum)".** It mixes PERCENT and FLAT with no amount_mode stated. It also says "scaled down Patch+", but Patch+ is a Firmware that exists. Does Level stack with it? The order is defined only in §5. "−1 RAM card" ignores that the card pass is separate.

6. **MAJOR, §5, "enemy scaling … upgrades do not raise ICE damage".** R2's phase budgets depend on `reference_dpt_by_tier`. Upgrades raise player dpt over the run, so N2 bands drift. The draft only defers this to the sim. It needs a stated dpt cap or per-level ceiling (e.g., a whole run of upgrades ≤ +25 % dpt).

7. **NIT.** "Heat NOTICED+ already raises Cycle prices" is unsupported: GDD 4.3 lists no such modifier. "Never adjacent in the same layer to a Mainframe" is meaningless, since nodes in a layer aren't adjacent. "Rack flash" for Level IV depends on N18, which is unbuilt. Example 2's quote is filler. Example 2's "Heat 30" implies a MINOR complication, but the complication only fires on first crossing.

## Concrete fixes

- **Placement:** replace the count with "1 per netrun at layer 3–5 on T2+ targets (replaces one Terminal slot), 0 on T1; second at layer 6 only on T3+. Mean ≈ 1.2 per T2+ run." Fix the gating: `workshop_max_level_by_layer` = layers 3 → I, 4–5 → II, 6–7 → III.
- **Costs:** state `cycles_per_netrun_estimate` and cap the Workshop at 35–45 % of it (per §8). Rescale the table to e.g. slice 25/45/70/100 pending the economy sim.
- **License:** drop the lock. Make the Workshop License an optional Schematics purchase that adds +1 offer (3 → 4) or −15 % cost. The node stays usable without it.
- **DPT:** add "`workshop_dpt_ceiling`: full upgrades must keep the reference dpt ≤ reference × 1.25; slice pass lints it."
- **Fallback:** "generic_level: slice output +1 (FLAT, amount_mode FLAT); card −1 RAM (min 0). Order: base → Level → Firmware."

## Keep

- One decision per visit, exact before/after preview with the real wheel position, and a CONFIRM step before paying.
- Offers generated on entry from saved stream state, so reload can't reroll them.
- Splitting node rules from slice/card level content via `levels` data, with a data-only fallback.

## Q:

- Q1: Is Cycles → Schematics conversion (10:1) meant to compete with Workshop spending?
- Q2: Do upgrades persist for a surviving operative (the draft's Q5), and is that consistent with "dies with the operative"?
- Q3: Should the Workshop be T1-available for teaching, with only Levels II+ gated?
