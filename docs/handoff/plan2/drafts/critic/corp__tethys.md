<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__corp__tethys; status ok; tokens in 29232 cache-write 0 cache-read 32585 out 2856; cost $0.047. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: corporation tethys

**Verdict:** FIX

## Roster variety

| draft | class | the one question | hook relied on |
|---|---|---|---|
| Pump Warden | normal | hit at LOW, since the wall doubles at HIGH | TIDE shield mult |
| Diver Drone | normal | is the Torpedo live this turn? | TIDE `tide_mask` |
| Buoy Tender | normal | dig through the bodyguard or steer round it? | fixed satellite (N13) |
| Kelp Crawler | normal | rotate off the stack or Cleanse? | OUTPUT_DOWN ×N (N8/N9) |
| Pressure Sentinel | normal | nudge at LOW, since HIGH locks it | tide-linked resistance |
| Lamprey | normal | kill it before it latches, or pay a Cleanse? | parasite ring (N10) |
| Siphonophore | elite | which chain link do you cut, then steer around the replacements | satellites + REPLACE |
| Angler | elite | plan two turns ahead of the orbit, then pick a rhythm | ORBIT + `tide_mask` |
| Harbourmaster | mini-boss | when does the wall stand, how do you take the tide, how do you play a double-speed tide? | TIDE (rate, hold) + satellite |
| Black Smoker | boss | tide, then half-wheel, ink, chain, fuse | TIDE + overclock + parasite + tier-down |

Overlaps:
- Pump Warden, Diver Drone and Pressure Sentinel all ask "read the tide, act at LOW". They differ only in which field the tide drives. Rework the Sentinel: make its question non-tide, e.g. a resistance wall that is lifted by a card-based Freeze, so Tethys has one normal that works without the clock.
- Buoy Tender and Siphonophore P1 are both "bodyguard satellite". Keep the Buoy Tender as the single-guard teacher and give the Siphonophore a different P1 hook.
- The Kelp Crawler and the Lamprey both put a debuff on your slice. They are distinguishable (slice status vs ring segment), but the Lamprey would be a poor first parasite lesson without a prior teacher.

## Phase and hook overlap

- TIDE appears in all ten drafts, because the enemy `tide_mask`, `tide_mult` and tide-linked resistance are all one system. The Harbourmaster P3, Angler P2 and Smoker P2 all use "dead at a tide step". The same question is therefore asked five times.
- Satellite-on-Breakwater appears in the Harbourmaster P2, the Buoy Tender and the Siphonophore.
- TIER_DOWN on the player's slice (Ink, Lure, Lamprey) appears in the Angler, the Lamprey and the boss, but it is never taught by a normal, and it ramps from L3 straight to the boss.
- No normal teaches uneven needles (N11) or the Overclock chain. The boss P3 to P5 mechanics (two needles, chain, Fuse) are met for the first time at the boss.
- Both HQ and boss have a "reset or cleanse" beat, but the HQ's Surge ("respin first needle") is a separate mechanic that conflicts with the Harbourmaster/boss tide rules; it is not part of the roster.

## Systems used

- **Shared (build once):** N1–N4, N5, N8, N9, N10, N11, N12, N13, N14, N19, and the TIDE clock plus tide-conditioned fields (NEW).
- **Single-use:** the status-conditioned chain (boss P4), round-fired flags (boss P5), and the HQ's `netrun_head`, `sluice_node` and `netrun_modifiers`, plus the `hq_graph_spec` ring.
- Event drafts need N7, N16 and N17-style event overrides, and `map_edits` (new).
- This is too many new systems. The TIDE clock is a single point of failure, which the draft itself admits. The HQ adds a second tide, the Head, which is a separate system from the combat TIDE. Merge them: one clock concept (TIDE) gives the Head its tick rule, not a second implementation.

## Difficulty curve

- L1–2 is well taught: Pump Warden, Diver Drone and Buoy Tender are data-only once the clock exists.
- L3–6 jumps to statuses, resistance and parasites at once (Kelp Crawler, Sentinel, Lamprey). Parasite ring is the hardest system and it arrives at L3–5 with no preceding teach.
- Elites are balanced, with matching 114 T4 HP, but the Siphonophore (hit satellites, then steer around) and the Angler (orbit, then a tide mask) are both more complex than a standard elite.
- Harbourmaster 10.5 turns (3 phases, ok). Boss 17.5 turns at the 400 band, but ~23 at the 530 band, which exceeds the 12–20 target. The enrage steps (turn 10 and 15) land in P3 and P5, and the Fuse adds to that, so P5 is a spike. At high ICE the player faces ~7 turns of enrage damage.
- The HQ run is 11 layers and ~30 min. It adds Pressure (−RAM) on top of R9's corruption RAM tax, plus an enrage-like Lockkeeper clock. The boss exam stacks three RAM or time pressures.
- The roster does prepare the player for tide and satellite play, but not for the chain or Fuse.

## Identity

Strong. The tide, "we never attack, we lower the water", lowercase advisories, and the BREATHE PLAN are consistent across the corp, boss, HQ and events. Weak points: the event drafts (Pressure Rumor, Hatch Fault, Pressure Courier) use generic "pressure" and "hull" language and no tide. The Courier uses `last_mile_enforcer` and `customs_scanner`, which are Meridian enemies, not Tethys ones. Hatch Fault also uses `last_mile_enforcer` (a Meridian elite). None of the events references TIDE or the Breathe Plan. Boss P2's coral/arms/ink art mapping is fine.

## Concrete fixes

1. **Events/ambush and paths:** replace `last_mile_enforcer` and `customs_scanner` with Tethys enemies (Angler, Siphonophore, Diver Drone, Pump Warden).
2. **Events/future (Pressure Rumor):** make the rumor about the tide (Tide Tables), and add a tide-step condition to one outcome; "true/false" should key off the `events` stream, which is already specified.
3. **HQ:** drop `netrun_head` as a separate clock. Reuse the combat TIDE (same four steps) with a node-count advance. Remove the Surge respin and the Dry free-nudge penalty, which clash with the combat tide rules.
4. **HQ Pressure:** cap the RAM penalty at −2 total and exclude it from the boss fight, or drop it. It stacks with R9's tax.
5. **Pressure Sentinel:** rework as a tide-free resistance puzzle.
6. **Siphonophore P1:** swap the satellite chain for a different hook, e.g. an uneven second needle or shield-sharing via the status. Keep REPLACE in P2.
7. **Add an L3–4 normal that teaches a latch before the Lamprey**, or give the Lamprey a status fallback in L3 and the ring only from L4 onward.
8. **Boss:** add a normal or elite that previews the OVERCLOCK chain, or drop Chain Eruption and keep the Fuse. At the 440+ bands cut P1–P2 HP to hold ≤20 turns.
9. **Harbourmaster P2:** note that "tide frozen at HIGH" cuts the clock the player learned. It is fine, but add it to the Intel tooltip.

## Q:
Q: Should Tethys be allowed to ship with the TIDE clock as its only dependency, with the parasite ring, chain and Fuse deferred?
Q: Is the HQ's Head the same clock as combat TIDE, or a separate one?
Q: Does Sea Wall at HIGH (20 and 24 shield) need its own cap, given the player's cap of 15?
Q: Should event drafts for Tethys reference tide at all, or stay system-light?
