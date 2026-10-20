# Solace vertical: one corporation to finished quality, then the next

Designer, 2026-10-19: once we reach a stopping point, work on a single corporation until its gameplay, visuals and balance are crisp
and clean. Start with Solace, then bring each corp to the same polish, one after another. Building seven corps in parallel means
carrying the same bugs seven times.

## Stopping point (now)
- **Finish what is in flight:**
  - Halcyon rules (branch `halcyon-v2`): finish, then **park on its branch**, unmerged. It returns at Halcyon's turn and is rebased then.
  - Run graph v2 / REST / WORKSHOP / CACHE (`rg-v2`): shared plumbing Solace uses, so it merges.
- **Start nothing new for other corps.** On hold until Solace is done:
  - REBEL_CELL, Orbital, Meridian, Tethys and Aurelian rules;
  - raid-operative rules RD-02;
  - other corps' exploit buildings and events.
- Shared systems are built only where Solace needs them.

## Solace definition of done
1. **Gameplay (build).** A full Solace-only campaign plays start to finish with no blockers:
   - street runs with THE BLOOM v2;
   - the Solace HQ ladder (WARD / BILLING, the Genome Core boss, the Account Manager mini-boss);
   - the raid with campaign infection, decay and cures;
   - the Solace exploit building (EX-11, the culture garden: Virus);
   - Solace events (EV-01 schema + the Solace drafts: future, paths, ambush, wheel, raidwin);
   - REST / WORKSHOP / CACHE;
   - preview == result everywhere;
   - no known-red tests in its area.
2. **Visuals (art-pass).**
   - the Solace district and landmark;
   - the HQ scene (NA-32/33 Solace);
   - the TIDE gauge, Bloom and infection looks;
   - the culture garden;
   - the whole-city plate parity.
   Every Solace screen is approved by art-pass's blind review.
3. **Balance (build, W4 scoped to Solace).**
   - BAL-02: tester logs on Solace fights.
   - BAL-03 / 04 / 05: the Solace boss and mini-boss, elites and normals, against the reference policy.
   - The Solace theme numbers.
   - Target: boss win about 50 % at ICE 0 for the reference policy, inside the tester band.
4. **Play (Claude playtesters).** Black-box runs of a Solace campaign. Findings are triaged per CP-002 and fixed.
5. **Bug sweep.** Every finding gets a slice. The bugs fixed in shared systems stay fixed for the next corps.

## Order after Solace
Halcyon (the rules are already on `halcyon-v2`), then REBEL_CELL, then Orbital, then Meridian, then Tethys and Aurelian (the corp wave).
Each corp gets the same definition of done.
