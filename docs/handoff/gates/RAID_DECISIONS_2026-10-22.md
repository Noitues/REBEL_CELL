# Raid decisions for the designer (2026-10-22)

From the Opus raid review (`docs/reviews/RAID_REVIEW_2026-10-21.md`). Each question shows the options and my recommendation (★). Answer with
a code, for example "R1 b, R2 a, R3 a".

## R1: what is the playout? (review #5)
Today it runs 1-15 s, against GDD 7.2's 30-60 s. The result is visible from the first frame, the feed runs ahead of the map, and 1×/2×/4×
does nothing useful on a 1-step raid.
- **a ★ Readable step-locked fight.** One beat per step, with hits drawn on the map and the feed in sync. The verdict is hidden until the
  end, and it lasts about 20-40 s at 1×, with skip and speed kept. This matches the GDD, and the forecast still promises the outcome, so it
  is suspense without surprise.
- **b 3-second summary.** Threats move, the stamp lands, and that's it. The speed buttons are removed and the GDD's 30-60 s is cut.
- **c As now, with only the spoilers fixed** (the verdict hidden until the end, the feed synced). The least work, but still short.

## R2: first-raid winnability (review #6)
In the lab state, 2 Collectors with 12 HP each reach home in one step, while the turret hits for 4-6. The first raid is lost, +5 Heat
(26 → 31) crosses the 30 complication, and no fixture seed wins a raid. The testers called this "piling on" (D-07).
- **a ★ Tune the first raid (Heat 25) so the starting armory can repel it.** For example, Collector HP or the first raid's unit count, as
  config only. Later raids keep their bite.
- **b No Heat for a survived but unrepelled raid** (OVERRUN costs Heat only if a node is TAKEN). The first raid stays hard but stops
  feeding the spiral.
- **c Both a and b.**
- **d Keep it as is.** The first raid teaches you to station and build, but the loss and its Heat stay.

## R3: CELL HOLDS wording (agent A's open question; GDD 7.2 line 413)
The GDD says "a survived raid ends CELL HOLDS". The game now shows REPELLED / OVERRUN / BREACHED, and the CELL HOLDS sticker only on a win.
- **a ★ GDD 7.2 says "a repelled raid ends CELL HOLDS"**, and OVERRUN gets its own sticker (amber, the cost on it). I edit the GDD and log
  the change.
- **b CELL HOLDS for any survived raid** (OVERRUN included), with the verdict word underneath.

## Not a decision: repair costs and new entry points (review #10)
The GDD already rules both: repair costs 50 % of the install cost, and a TAKEN Site next to your territory becomes an entry point. The
rules exist, but the report doesn't show them. **I'll add them to the after-action report and the HQ** (a DOWN badge with its repair
price, a new-entry marker), unless you say otherwise.
