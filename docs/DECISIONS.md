# Decision Log

Append new entries at the top of the relevant section. Never delete entries; mark them
superseded instead.

## Locked design decisions (v0.9)
- Wheel is 30 ticks / 6 slices / 5 ticks per slice (was 24). Enables a true centre tick.
- No Miss precision tier; "Miss" means the Miss slice only.
- Enemy jitter replaced by spin resistance (passive trait or Hub-sourced). Flip and
  Respin are blocked while resistance > 0.
- Flip mirrors the wheel across the horizontal axis (opposite slice to the pointer).
- Triggering: every pointer triggers its slice on End Turn. Pointer attacks hit every
  pointer of the target wheel. Satellites act as bodyguards.
- Resolution order: defensive → offensive → statuses, simultaneous.
- Three-layer progression: netrun / campaign / profile. Class unlocks are profile-level.
- Rank (runs survived) replaces veterans/Trace: wheel upgrades, netrun tier access,
  station bonus scaling. Survivors keep everything; difficulty scales to match.
- Heat is one campaign meter. Threshold events fire once; modifiers apply while at/above.
- City Grid is one shared map for netruns, territory and raids; cleared Sites are used up
  and become claimable.
- Armory (cap 6) + persistent deployed assets resolves the audit's persistence question.
- Mainframe gate: minimum 3 Exploits (Intel, Breach, Virus); extras weaken the boss.
- Story paths: 5–6 per corporation, hidden and random; beats unlock in Exploit order.
- REBEL_CELL (the handler AI) is the final unlock corporation at ICE 10 on all others.
- ICE difficulty: 20 cumulative levels, ICE 5 is the average-player tuning target.
- Visual baseline: three worlds (cyberdeck / wireframe / zine), Cell colour hot pink.
- Full voice acting; fully solvable combat preview; rewind with checkpoints at random
  events.

## Implementation decisions
_(Claude Code: add entries here as you make them.)_

## Open questions for the designer
_(Claude Code: add questions here instead of guessing on design.)_
