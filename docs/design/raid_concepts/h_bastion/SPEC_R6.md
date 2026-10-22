# H: Bastion (round 6)

**The defense persists across the campaign; the depth is in investment.** Code: `tools/raid_concepts/concept_h6_bastion.py`;
the measurement is `bastion_campaign.py`. Every rule is a **designer decision**.

## Rules
- **No per-raid draft.** Every piece you buy stays where you put it, raid after raid. A TAKEN node destroys its pieces.
- **Each HQ visit before a raid:** buy up to 2 pieces and station the crew. Prices: Turret 6, Sentry 7, Railgun 10,
  ICE 5, Decoy 4.
- **All raids of the campaign leg are telegraphed** on the Heat bar from the first visit, with each roster and its
  corp entry site.
- **The shop shows a fortress forecast:** the current raid and every telegraphed raid after it, run with this fortress
  and no more buys. It is an honest projection, not a hint.
- **Payout per raid:**
  - +4 salvage per kill;
  - +6 if CLEAN;
  - minus the full repair bill;
  - +12 netrun income between raids.

  The bank can dip below zero (debt is paid from income).
- **Combat** is the round-5 package: fixed routes, home is never a corridor, the weaker tie-break, ICE blocks the
  strike, no cascade.
- **Execution** is hands-off: zero input, speed and skip only.

## Measured depth
Five seeded 3-raid campaigns of 2, 3 and 4 content threats:
- Planning for the whole leg beats playing each raid greedily by **14.8 Schematics on average** (37 at most).
- In **4 of 5** campaigns the right first purchase differs from the greedy one.

## Campaign shown (seeded campaign 1)
- **Raid 1:** Courier + Enforcer.
- **Raid 2:** Courier + Bailiff + Collector.
- **Raid 3:** Courier + Lockdown + Bailiff + Collector.

| Line | Buys | Bank after each raid |
|---|---|---|
| Home fortress | Railgun + Decoy at home and Firewall, then Turret + ICE, then Railgun + ICE | −1, 15, 34 (every raid CLEAN) |
| Forward fortress | Sentry + Decoy toward the Proxy | −1, −1, −3 |

## Frames
0. The campaign leg.
1. The shop and the fortress forecast for both lines.
2. Raid 1 forecast.
3. Raid 1 playout.
4. Raid 1 aftermath (pieces persist).
5. Visit 2.
6. Visit 3 (Lockdown freezes a home link).
7. The campaign record (bank line).
