# E — COUNTDOWN + ALLOCATION (Frostpunk-style storm)

**One line.**
- **The warning is early.** The raid is announced **two netruns ahead**, with a top-centre countdown and a visible front at
  the map edge.
- **The strike is known.** Each target node shows a gauge with a cobalt notch: the strike it will take.
- **The response is spread over time.** Between netruns you spend a scarce pool to fill gauges, or you make a hard call.
- **The strike auto-resolves.**

## The decision
- **Allocation under scarcity.**
  - **Crew-hours.** 6 a raid, from stationed operatives plus Schematics converted 3:1.
  - **Filling a gauge.** Each crew-hour put into a node adds +2 DEF.
  - **Armory pieces** add fixed DEF: turret +6, ICE Lock "cancel the first strike", Decoy "move this node's notch to the Decoy node".
- **Hard calls** (Frostpunk's laws as one-off triage):
  - **Evacuate** a node. It is TAKEN for sure, but its install cost is refunded at half.
  - **Go dark.** The countdown is delayed by one netrun, at +4 Heat.
- **The netrun in between matters.** You choose where to fight, aware that a Safehouse stationing or a Schematics windfall
  fills gauges.

## The information shown
- **Countdown dial**, top-centre: the netruns left, as segmented arcs.
- **The front.** A hatched cobalt band at the map edge that moves in each netrun.
- **Per target node, a vertical gauge.**
  - The yellow fill is your defense; the cobalt notch with its number is the strike.
  - While you allocate, the added fill shows pale, with a tag ("6 + 6 = 12 : HOLDS").
- **A hard-calls card** with each option's exact effect.
- **The forecast panel** ("IF IT STRIKES NOW"). It gives the verdict, the trades taken, the clean or not clean result with
  its Heat, and the netruns to go.
- **Why.** The Heat crossing (51 > 50) in the warning card.

## Resolution
- **The front sweeps** across the map, right to left. As it crosses a node, that node's gauge drains by its notch.
  - At or above the notch: HOLDS.
  - Below the notch: DOWN.
  - Empty, or evacuated: TAKEN.
- **Home** loses integrity equal to the shortfall; 0 = BREACHED.
- **Timing.** About 20 s, with no input.

## Consequences
- **Stamp** with the cost line.
- **The trades you chose are named** ("Proxy TAKEN · refund +6").
- **The next strike is foreshadowed** ("next strike at Heat 75").
- **Marks persist** on the map, as in the other concepts.

## Rule changes (each is a designer decision)
1. **Raids are announced N netruns ahead** instead of striking on the next return. **Designer decision.**
2. **A new resource (crew-hours) and gauge DEF replace** asset reach and targeting; a node's outcome is a threshold check.
   **Designer decision.**
3. **The hard calls are new mechanics**: Evacuate refunds; Go dark trades Heat for time. **Designer decision.**
4. **Routes and steps disappear**; D26's step-locked playout becomes a single sweep. **Designer decision.**

## Key frames
`r1/mockups/`, `r1/scrambled/`.
