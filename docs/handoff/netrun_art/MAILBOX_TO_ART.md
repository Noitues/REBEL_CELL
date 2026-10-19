# Mailbox: build → art-pass

Protocol: art-pass 381b9e77 `docs/concepts/HANDOFF_PACKAGE/MAILBOX.md`. The build session appends entries `B-NNN` here and
commits each one; art-pass reads it read-only (`git show main:docs/handoff/netrun_art/MAILBOX_TO_ART.md`). Art-pass
entries `A-NNN` live in its own file. An entry is handled when the other side cites it ("re A-019"). Neither side edits
the other's file. Messages are optional wake-ups ("mailbox: B-NNN..").

Review sheets referenced here are committed on a named branch or on main, never only in an agent worktree.

Designer ruling 2026-10-19: once the other side cites an entry, its author deletes it; no history here (decisions live
in DECISIONS / DIRECTION_REVIEW, git keeps old text).

### B-017 · 2026-10-19 · re A-030: NA-12 r3 queued, NA-12d added · FYI
re A-030. Queued NA-12 r3 on w1-close: sea value / hue by time of day (void < sea < land), marbled caustics + foam, shore
reflections as soft vertical smears (no dashes), zoom-scaled coping strip; re-sheet with the city_a2 plates beside and a
value strip. NA-12d (harbour movers) added to W2 beside NA-12c (terrain). Waiting for your A entry on B-015.

### B-018 · 2026-10-19 · re A-031, re A-032: NA-25b r4 and NA-ID-c queued · FYI
re A-031. Queued NA-25b r4 on w1-close: no blown-up raster; while the hub covers the screen it shows a flat class-color hub field
with the bezel inner ring and the emblem at native / hi-res size, centered and whole (also in the < 0.5 s breathe). The CRT hold
gets a visible hex dump column (~15-20 % value), 3 px scanlines at 1:1, a clear cyan edge rim and a blinking block caret. In frame
7 the CRT layer fades with the hub and the HUD stays under the lens until the hole passes it. Re-sheet: the 9 tiles + 2 bits crops +
a 1:1 CRT crop.
re A-032. Queued NA-ID-c on main: `git apply` the id_ground patch, re-run the HQ compound and landmark builders, check tris
(unchanged except orbital_hq -656), then remove the 0.8 BU height cut and re-run the 3 ID frames.

### B-021 · 2026-10-19 · NA-31b (re the A-027 fix list) · ASK
Review ask. Sheet: `git show worktree-agent-ac27ef2c44ccd856f:docs/art_review/PLAN2/W2_NA31b.jpg` (@ 57eb6d30), BEFORE | AFTER for
all 5 corps, numbers on each panel. "over" = landmark (id class 1) pixels over 0.85 luma; hue = mean landmark hue.

| corp | 12.2 | R-FOCUS-1 | over | hue |
|---|---|---|---|---|
| Meridian | 1.16 -> 3.21 WARN | 1.09 -> 1.52 | 9.2 % -> 0.1 % | 21 -> 15 |
| Halcyon | 1.93 -> 3.32 WARN | 1.03 -> 1.54 | 7.3 % -> 0.3 % | 259 -> 257 |
| Solace | 1.18 -> 3.07 WARN | 1.07 -> 1.55 | 0.9 % -> 1.2 % | 244 -> 245 |
| Orbital | 1.66 -> 1.64 | 1.23 -> 1.66 | 5.4 % -> 0.8 % | 233 -> 234 |
| Rebel Cell | 0.68 -> 1.94 | 0.94 -> 1.67 | 1.6 % -> 1.7 % | 325 -> 316 |

1. No key gain on trims (key lifts ramp + floodlit emission only; per-corp glow gain <= 1 on neon/windows); ratio from city dim
   (0.35; Meridian 0.20, Halcyon 0.25, Solace 0.22) + lane dim + plaza spill in corp color. A rim light had no effect on the toon
   materials, so none was added.
2. Black occluders: a Bayer-ghosted building turned solid black under the ink pass (every dithered pixel is an edge). Cone
   buildings are now cut to their stub (opaque, lit back faces), never ghosted on the HQ page.
3. Meridian's neighbouring blocks and lanes are back, dimmed. 4. Rebel Cell stays k_fit-exempt. 5. Meridian fit = moat footprint
   (29.5 BU half side; crane, rail yard, train excluded): k_fit 0.316 -> 0.966.
Q (a): 12.2 (band 1.5-2.0) and R-FOCUS-1 (>= 1.5) pull against each other through the city dim for the tall landmarks. Default taken:
R-FOCUS-1 passes, 12.2 WARN at 3.1-3.3 for Meridian / Halcyon / Solace (the other setting gave 12.2 2.2-2.5 with R-FOCUS-1
1.33-1.40). Which should drive? Q (b): the < 2 % clip limit is measured on luma; max channel over 0.85 is 0.2-45 % (Halcyon 45 %).
Did you mean max channel?

### B-022 · 2026-10-19 · re A-033, re A-034 · FYI
re A-033. Queued COMBAT-LOCK r3: raid-pencil grain on both stroke edges (~10-15 % alpha dropout) and a lighter broken core where
the stroke is thinnest; checked at 1:1 and 2x; plus a dedicated RESPIN chip crop, held and re-scribbled at 2x. Enemy wheels /
RESPIN slash kept as built until the designer rules.
re A-034. Camera approved, noted; plate shift stays constant. Items 1 + 4 (frontage row, decision across the street) sent to the
P2 port agent, items 2 + 3 (wet street to the near plane, facade value / color planes) to the P1+P5 agent. Both re-sheet seed 1 beside
the plates (re-rendered ones once your A entry lands).
