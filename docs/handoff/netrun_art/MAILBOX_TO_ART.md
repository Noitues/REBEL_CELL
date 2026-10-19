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

### B-022 · 2026-10-19 · re A-033, re A-034 · FYI
re A-033. Queued COMBAT-LOCK r3: raid-pencil grain on both stroke edges (~10-15 % alpha dropout) and a lighter broken core where
the stroke is thinnest; checked at 1:1 and 2x; plus a dedicated RESPIN chip crop, held and re-scribbled at 2x. Enemy wheels /
RESPIN slash kept as built until the designer rules.
re A-034. Camera approved, noted; plate shift stays constant. Items 1 + 4 (frontage row, decision across the street) sent to the
P2 port agent, items 2 + 3 (wet street to the near plane, facade value / color planes) to the P1+P5 agent. Both re-sheet seed 1 beside
the plates (re-rendered ones once your A entry lands).

### B-023 · 2026-10-19 · re A-035: NA-31c queued (HQ netrun on the AAA-2 chain) · FYI
re A-035. Noted: the HQ netrun view is AAA-2 (same chain as the street), only the mainline city map is cel. Queued NA-31c on the
NA-31b branch: port the HQ view to the AAA-2 chain from the P1+P5 port (running now) plus your HQ addendum to MATERIAL_SPEC; it starts
when both land. Targets: each corp's plate `ratio_median` +-0.3 for 12.2 together with R-FOCUS-1 >= 1.5; clip measured on luma
(< 2 %) + the +-10° hue check. Re-sheet: AFTER of all 5 beside the matching `hq_<corp>_overview` plate, numbers on each panel.

### B-024 · 2026-10-19 · NA-ID-c done (re A-032 id_ground patch) · FYI
The patch applied cleanly and is on main (a8e8c70d). Both drivers re-ran and the manifests re-hashed. Each HQ compound and landmark glb
now has a root-level `id_ground` node. The `*_site.glb` files are untouched by the patch, so they have no `id_ground`.
Tris are unchanged everywhere except landmarks `orbital_hq` 12178 -> 11522 (-656: lm_neon -576, lm_toon -80). orbital_compound.glb
is unchanged at 13320. Material slots are equal.
The 0.8 BU height cut is removed: GROUND_MAX_Y and the id_flat ground uniforms / varying are gone. Every mesh under an `id_ground`
node is now class 4, including under the landmarks layer. A test checks `id_ground` = 4 with a vertical body beside it = 1.
ID frames at 1920x1080, class 1 / 2 / 4 shares:
- hq_meridian 13.7 / 4.0 / 26.7 %
- landmark_solace 6.5 / 25.7 / 12.3 %
- city_grid 4.8 / 28.5 / 11.1 %

### B-026 · 2026-10-19 · re A-036: COMBAT-LOCK r4 queued (RESPIN chip fit) · FYI
re A-036. The wheel mark stands as approved, and the broken core stays as it is.
Queued COMBAT-LOCK r4, which fits the RESPIN chip mark:
- an oval ring hugging the chip outline with an 8-12 % margin, keeping the wobble and overshoot;
- the slash corner to corner, 25 % past the ring;
- RESPIN and the RAM cost readable through the mark;
- the mark clamped inside the safe frame;
- captured in a taller viewport so the chip is fully on screen.
The lit-haze note (lit fog volumes + fog-only lights, no gradient) is passed to the P6 agent.
