# L10 → L11 changes (from the L10 batch critic; applied in place to the l8 files)

## Rules (sweep_l8.py and l8_rules.gd change identically)
1. **Coverage cap: `MAX_PLACED` = 2.**
   - PLAN places at most 2 sentries, whatever the pool holds. Every route can no longer be covered before the reveal.
   - Sentries in the pool that are not placed are the **reserve**.
   - `placements()` enumerates up to `MAX_PLACED` sentries. Its order is: maps with fewer sentries first? No: keep the
     existing order rule (every possible map in the established enumeration order), filtered to maps with
     `size <= MAX_PLACED`.
2. **New response: DEPLOY t → c.**
   - It takes a spoof charge plus `SPOOF_HEAT`, like the other responses.
   - It places one reserve sentry of type t on an owned, non-TAKEN cell with no sentry, after beam 1 and the extras.
     It acts on the sealed beam and the hunter.
   - Response order: HOLD, every REDEPLOY (as now), every DEPLOY (types in D, N, E order, then target cells in cell
     order), then JAM.
   - JSON form: `["DEPLOY", type, [x, y]]`.
   - After the raid, the deployed sentry stays placed as part of `st.sentries`, like a redeployed one.
3. **A lost district returns its sentry.** When a cell becomes TAKEN (by a hit or by decay), its sentry goes back to
   the pool. The pool count stays the same and the sentry is only removed from the placement.
4. **`safe_next(leg, raid, st) -> bool`.** True if some capture option, then some placement (with the best response per
   candidate), keeps HOME above 0 on every sealed candidate of raid `raid`.
   - It runs on the post-decay state.
   - It returns True when `raid >= RAIDS`.
   - Used by the lab's between screen per option, and by the "decided" cut.
5. **`__main__` SUMMARY** adds:
   - `split_raids` and `response_decides` (already present);
   - `deploy_use`;
   - `decided_cuts`: legs where, after a between step, `safe_next` is False for every option.

   It writes `sweep_l11.json`.

## Golden (l8_golden.py)
- Each leg step with a between step records `"safe_next": {intensity: bool}` for the chosen repair and build, for each
  intensity. The value is `safe_next` on the next raid's state after decay.
- Random raids draw responses from `response_options`, so they include DEPLOY.

## Lab presentation
1. **Between screen:**
   - Every intensity card shows a SAFE / AT RISK badge from `safe_next`: a shield, or a skull. It updates live when
     the repair or build changes.
   - When every combination of intensity × the current repair and build shows a skull, check all between options.
     If none is safe, show "DECIDED: the cell falls next raid". The button then plays a short fall beat, and the
     record follows: no dead raid.
2. **The hunter is a creature:** a cobalt hound silhouette with glowing eyes, standing at the start of its street in
   PLAN and FORECAST (the selected route's HOLD hunter street). It runs the street in the playout.
3. **Intensity as pictograms:** one, two or three flames on each card, plus the next raid's known beams as small beam
   icons (counting the ghost's +5 as a second row).
4. **Response rows on the board:** hovering or selecting a row draws its effect.
   - REDEPLOY or DEPLOY: an arrow from the source (the sentry, or the reserve tray) to the target cell.
   - JAM: the hunter crossed out.
5. **Reserve tray** in the panel during PLAN: placed sentries 0/2, and the reserve by type.
6. **Leg value now** includes the ghost's Heat as soon as the ghost is placed.
