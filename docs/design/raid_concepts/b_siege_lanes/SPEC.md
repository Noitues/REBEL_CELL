# B — SIEGE LANES (tower defense, wave preview, HP ledger)

**One line.** Read the network as a tower-defense map. Each threat's route is a wide lane with numbered step ticks. A wave
flag at every entry shows who is coming. An HP ledger along each lane shows the threat's integrity at every tick, so you can
see where it dies and what reaches your nodes.

## The decision
- **Where to build.** Place towers (turret, ICE Lock, Decoy, operative) on nodes.
- **What a tower covers.** A tower covers the lane segments within its reach. Hovering a card over a node lights the
  covered segments in yellow and names the coverage ("covers 3 lanes · 4 / step").
- **The trade.** Junction nodes cover more lanes but are often the targets themselves. A Decoy reroutes a lane; the lane
  redraws at once.

## The information shown
- **Wave flags** (Thronefall- and Kingdom Rush-style), one at each corp entry: a cobalt panel with the silhouettes and a count
  (×1, ×2).
- **Wave panel** (right). A row per threat type, all without words:
  - silhouette;
  - integrity number;
  - crossed swords and damage;
  - speed chevrons (one per link per step);
  - a routing hint.
- **Lanes.** A dark cobalt band with arrowheads per route; offset where two lanes share a link.
- **HP ledger chips** at each step tick. Each chip carries:
  - the step number;
  - a small bar of the threat's HP left;
  - a red skull where the threat dies.

  Grey chips are the raid as it stands; coloured chips are the plan.
- **Per-node tags** for the end of the raid (HOLDS / DOWN / TAKEN), with projected loss pips.
- **The result panel** ("IF THE RAID RUNS"):
  - the verdict word;
  - home before > after;
  - the TAKEN / DOWN nodes by icon;
  - threats stopped (skull 2 / 3);
  - **"CLEAN NEEDS"**: the gap to a clean defense ("Enforcer: 25 more damage"), with its +5 / +12 payout shown dimmed.

## Resolution
- **Commit**, then a hands-off playout. Tokens advance tick by tick along the lanes, and towers fire tracers.
- **The forecast stays visible.** The ledger chips remain as a faint ruler, so the player sees the forecast come true.
- **Step-locked, fixed camera.** The step ruler sits top-centre; 6 steps last about 25 s at 1x.

## Consequences
- **Verdict stamp** with its cost line.
- **TAKEN nodes keep the pencil X** and sprout a dashed "NEW ENTRY" lane stub toward their neighbour. That lane is part of the
  next raid's map.
- **A "LOST" card** names each loss once, with its fix: Proxy → reclaim netrun, ICE Lock → spent.

## Rule changes
None. This is a presentation of today's resolver: routes, steps, reach and HP.

## Key frames
`r1/mockups/`, `r1/scrambled/`.
