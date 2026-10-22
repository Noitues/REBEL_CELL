# Round 6: measuring decision depth before drawing

The best score has run 36 → 35 → 35 → 32, and decision depth has stayed at 4–7 in every round and under every
critic. Round 6 therefore measures depth in code before any concept is drawn. Every core runs its whole plan space on
10 seeded raids drawn from content threats with random entries:
- `tools/raid_concepts/depth_harness.py`;
- `pareto_harness.py`;
- `bastion_campaign.py`.

## Is there one right answer? (single net = payout − full repair bill)

| Core | Rule toggles | Same best draft across raids | Drafts within 3 net of best | Fragility |
|---|---|---|---|---|
| **G5** (anchor: 3 of 5) | package + no cascade | **0.8** | 2.6 | 0.93 |
| J Switchyard (barriers close links, threats jam) | + jam, barriers | 0.9 | 2.3 | 0.83 |
| I Circuit (adjacency synergy, 4 of 5) | + circuit | 0.7 | 2.9 | 0.65 |
| K Counters (visible threat traits) | + traits | 0.8 | 2.7 | 0.93 |

Fragility is the share of one-piece moves that lose more than 3 net.

What the numbers show:
- **J:** barriers never appear in a best plan.
- **I:** every raid reaches the maximum payout.
- **K:** traits negate one piece each, but the ICE + Sentry + Railgun mix still covers everything.
- **The common cause:** a fixed pool of 5 on a 6-node map, scored by **one number**, always has a near-dominant
  answer. This is structural; no presentation fixes it.

## What breaks it

1. **Losses that are not folded into one number** (`pareto_harness.py`). Count the plans that are not beaten on every
   axis at once (home, each node, kills). With home untouched, **40 % of raids** have three or more of these plans,
   each giving up a different node (mean 2.4 distinct "what you give up" sets). The choice is real only if nodes
   matter differently. That means giving each node a distinct job in the run (Vault = Schematics, Relay = netrun
   reach, Safehouse = the crew, Firewall = home's gun, Proxy = a corp-side foothold).
2. **The draft comes from what this run has earned**, not a fixed pool. With a fixed pool, the same 3 pieces win
   8 times in 10.
3. **Investment across raids** (`bastion_campaign.py`, H Bastion: pieces persist, buy up to 2 per visit). See the
   numbers below.

## Numbers for the levers

### 1. Losses kept apart (`pareto_harness.py` on G's plan space)
Scuffs are folded into one patch-cost number. A front plan is one no other plan beats on every axis at once.

| Measure | Value |
|---|---|
| Front plans per raid (mean) | 4.7 |
| Distinct "what you give up" sets (mean) | 3.9 |
| Raids with 3 or more such sets | 60 % |

Example raid: Collector C1, Bailiff C2, Enforcer C2.

| Plan | What holds | Kills | Patch |
|---|---|---|---|
| A | all hold | 3 | 19 |
| B | PROXY DOWN | 3 | 10 |
| C | PROXY TAKEN | 2 | 0 |
| D | RELAY + PROXY DOWN | 3 | 9 |
| F | SAFE + PROXY DOWN | 3 | 0 |

### 3. Investment across raids (`bastion_campaign.py`, 5 seeded 3-raid campaigns)
GREEDY plays the best plan for the current raid only. PLANNED looks ahead across the campaign.

| Measure | Value |
|---|---|
| PLANNED beats GREEDY by | 14.8 Schematics on average (37 at most) |
| Right first purchase differs from the myopic one | 4 campaigns of 5 |

Campaign 1 (shown in the H mockups):
- **Raid 1:** both lines end at −1.
- **PLANNED** bought a Railgun + Decoy at home, every raid after is clean, and it ends at **34**.
- **GREEDY** bought a Sentry + Decoy forward, never recovers, and ends at **−3**.

## Round-6 set (from these numbers)
- **H Bastion:** the persistent fortress. Measured: depth across raids.
- **P Stakes:** each node has a distinct job, surviving threats return, and the forecast shows the front of plans
  instead of one net. Measured: real "what you give up" choices.
- **HP:** H and P merged.
- **G5:** the anchor.
- **Dropped by measurement:** J (route shaping), I (synergy) and K (traits). Each still had a near-dominant answer.
