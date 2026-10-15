# Route map redesign: requirements checklist

The orchestrator ("Resume per HANDOFF.md") collected these on 2026-10-14 from:
- the designer's rulings in DECISIONS (2026-10-14; W3-ROUTE; ANIM-FLOW);
- the playtest findings PB-010 C7, PB-PT-003b and PT-003_steps.

Each requirement is followed by **Status in the chosen direction**: V3 dynamic side view with the AAA-2 r3 look; the Halcyon HQ variant is in progress.

## Graph
1. **Full graph always drawn.** Past and unreachable nodes are greyed and translucent; current and reachable nodes are in full colour; legend hover shows the whole graph at full opacity.
   - **Status:** done in V3/AAA-2 (grey wax past, white dashed ahead). The designer bent the full-graph rule for street-level views and the far side of the HQ: those parts may be hidden behind the camera, with legend hover or OVERVIEW showing them.
2. **The graph carries the choice information.** Every link is drawn, including the RACK and SHOP branches.
   - **Status:** the hover power-cut lights the whole branch to the TARGET. OVERVIEW shows every link.
3. **Node type reads from the node:** the sticker plus the room dressing, by shape and not by colour only.
   - **Status:** each type has its own room dressing plus a vinyl sticker. Corner badges are gone.
   - **Check in the build:** elite vs fight sticker shapes at 1280x720.

## Names and labels
4. **No tags at rest.** A tag shows only on hover; legend hover shows all tags.
   - **Status:** done.

## Interaction
5. **Selecting and travelling:**
   - click selects and the node file shows;
   - CONFIRM or Enter travels;
   - number keys travel at once;
   - pad or keyboard focus lights a node the same way hover does.
   - **Status:** in the concept UI. Focus uses the hover state.
6. **A clear pick prompt, and the TARGET explained by the graph.**
   - **Status:** the ROUTE panel "PICK A FLOOR" prompt and the red-pencil TARGET at the end of the street, or at the HQ apex.

## Information
7. **HP on arrival and heal points per node.** Heal or rest nodes must read at a glance along the path.
   - **Status:** HP on arrival is in the node file.
   - **GAP:** heal and rest points need an at-rest marker on the room, e.g. a medkit sticker plus warm room light. Add it to the tools spec.
8. **Heat per node (Rack Heat), plus the run's Heat-to-raid threshold if the route can cross it.**
   - **GAP:** show a Heat chip on the Rack room's sticker. Mark the threshold as a red pencil "RAID AT 30" tick on the link where cumulative Heat crosses it.
9. **The meaning of node numbers and layers must be self-evident.**
   - **Status:** the numbers are only on the current options (keys 1-n). Layers read as buildings left to right, or spiral turns on the HQ.
   - **GAP:** confirm in playtest. Consider a step ruler (V2's bubbles) in OVERVIEW only.

## Motion
10. **Token travel; the hover reach-out from node to building.**
    - **Status:** the token rides the link (step GIFs). The reach-out is replaced by the hover power-cut plus camera ease.
11. **Never an empty map frame.**
    - **Status:** the NIGHT_SKY hold is kept. The storyboard's jack-in dive covers loads.

## Context
12. **GRID VIEW and ROUTE VIEW share one graph language.**
    - **GAP:** the storyboard's HQ beats use the mainline City Grid. The tools spec must define the run path on GRID VIEW with the same wax, sticker and state language.
13. **The 3D city stays, and the screen is readable at 1.0, 1280x720 and 1920x1080 with mouse and keyboard.**
    - **Status:** the city stays.
    - **Check:** 1280x720 readability of the DECISION view in the build.
14. **Pencil never touches UI; toasts never cover controls.**
    - **Status:** the wax is erased around stickers, and the UI is kept clear in the concepts. The build must keep the rule.
