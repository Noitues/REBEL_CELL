# Handoff — REBEL_CELL (build session, W1 of REPLAN_2026-10-16)

| | |
|---|---|
| Written | 2026-10-18 (evening) |
| Branch | main (pushed at gate/PT-004 b98e1def; later W1 merges are local until the PT-005 gate) |

## State
- Plan 2 / W0 closed: PT-004 automated gate passed and pushed (playtest skipped by designer).
- **Overnight directive (designer):** don't wait for decisions: take defaults, log them in DECISIONS. If PT-005 is
  reached before 07:00 2026-10-19, run its automated gate (full suite once, smoke, validate, push gate), then go to W2
  unless a replan is needed (themes, WATER LEVEL, exploit buildings, Q24.1 death likely need one: Batch-draft it, then
  start the next wave). Memory: `overnight-run-2026-10-18`.
- Defaults already logged: DECISIONS "Overnight: defaults taken on open calls".

## W1 status (briefs: `docs/handoff/plan2/drafts/briefs_w1/` + README queue rows)
- Merged: NA-21, NA-22/22b/22c/22d, NA-23, NA-24, NA-25 (+fix), NA-11, NA-11b, NA-04b/c, OCCBAND, OCC-OUTLINE,
  LAMPSHIFT, N8, N9, N20, N6, N7, N12. Replan draft for W2+: `docs/handoff/gates/REPLAN_2026-10-19.md`.
- NA-04d merged (a35b41b0): 12.6 by depth.png, R-REP-1 facade band, drift vs art-pass 7772e6ba = 0 DRIFT (sent to art-pass).
- Merged 2026-10-19 (all art-pass APPROVED where visual): NA-26, NA-11c, RULE5-CMO, MOTION-TIMINGS, NA-23b (61029e84),
  CAP-W1/N12b, NA-24c (c983ca7b), NA-23c (fd0c9aa7). DECISION R-REP-1 ~0.62 accepted as warn (art-pass owns the 8 px lag).
- Merged later 2026-10-19: Q19-PREVIEW (3f4e1d46), NA-24b, NA-ID (093308f9), W2 drafts WH-01/EX-01 (b946de66).
- Integration branch `w1-close` (worktree .claude/worktrees/w1-close) = main + NA-25b + NA-12; merge to main when
  art-pass approves both. Agents based on it: street-on-generated-city fix, WH-02 (Opus), NA-31.
- Art-pass held replies 15-18 (art-pass b4a8cb42, docs/concepts/HANDOFF_PACKAGE/PENDING_TO_BUILD.md) = OPEN fix lists:
  - 15 NA-ID-b (QUEUED): ground drawn as class 4 (not hidden), ground-lying compound parts (plaza, aprons, rails) class 4
    via `id_ground` group / glb role, capture.json 1-space indent + sorted + LF + `time` night|day; re-run 3 frames.
  - 16 NA-25b r3 (QUEUED, base branch worktree-agent-a81de4284bc1f9b35 @ bad12255; worktree removed): chain order, bits,
    toggle APPROVED. Fix: (1) the real class wheel (D4 bezel + glass crescent, slices with read blocks, cream blades, class
    hub core 3.3) for slap (sticker overshoot/settle, spin-up) and lens (hub core opening); (2) hub hold > 0.5 s = CRT
    terminal (navy glass, 3 px scanlines, scrolling hex dump, edge glow, type-on `> routing ... building street_<bid>` +
    caret); (3) HQ-side switch frame: normal city material if ever visible (no neon wireframe), else say it is covered;
    (4) black windowless prism in bits frames = 7.1 ghost stub (see-through + outline) or missing material. Re-send
    frames 4-6, HQ-side, bits frame. Sheet W1_NA25b_r3.jpg.
  - 17 NA-12 r2 (RUNNING, agent adf53274290f3bfd9): water material, sea wall, piers, darker void, day blue; concave bay +
    noise; city.json `coast` + `terrain.hills` (additive); CENTRAL SERVER chip clear of pins. Sheet W1_NA12_r2.jpg.
    Terrain rendering = new slice NA-12c in W2 (before NA-32 HQ scenes).
  - 18.1+18.2 COMBAT-LOCK (QUEUED, on main): nudge lock = wax circle-slash per designer ruling (DECISIONS 34069fe7), word
    chips + toast removed, slash on locked RESPIN; Q19 respin ghost = 9 x 46 px chevrons chasing outside the rim (3.17),
    no dashed ring. Re-send CAP_W1 panel 3 and Q19 panel 2.
  - 18.3 NA-24d: folded into parity P3 (A-021).
- STREET LOOK PARITY (A-020 designer ruling, blocks w1-close; plan B-002, answers A-021 art-pass 3dccef4e). Every netrun /
  city sheet = golden plate + Godot at the same camera AND the §12 numbers. Queue (serial on city_building.gdshader):
  - P0 parity harness (READY): tools/netrun_art/parity_sheet.py, plate via git show to %TEMP%, Godot at plate camera
    (plate cams: art-pass golden_plates/street_*_capture.json, 1920x1080); publish our cameras in B-003.
  - P1+P5 (A-022 CORRECTION): netrun street = AAA-2 realistic night (PBR, volumetric fog + FogVolumes, emissive-lit), NOT
    toon/ink; keep the smooth look_blend 1. Port art-pass HANDOFF_PACKAGE/street_kit/MATERIAL_SPEC.md (read §0 and "What
    makes the look" first): exposure solve to median 0.14 FIRST; layered colored volume fog (0.152/BU cores, aniso 0.45,
    ground band 0-2.2 BU 0.12/BU); wet street rough 0.03-0.30, spec IOR level 0.7, SSR; emissive hierarchy (hero 4.0 ...
    lamp heads 8.0), 3-radius bloom, ACES hue-preserving + teal shadow / warm-pink highlight grade, vignette 0.38, CA, grain.
    Facet grit is geometry (fgrid, cell 1.7 BU). No sky gradient, no bokeh pass (P6 bokeh = rough reflections).
  - P2+P3+P4: PORT art-pass street_r2/scripts r2_config (-> .tres), r2_facade, r2_kits (code), r2_rules plan_pass /
    layout_pass / checks, r2_signs as Python twin + GDScript at the same art_seed (fnv64). Props glb + roles.json from
    street_kit/ (A-NNN). Cut the ~8 tall yellow-green/teal glow bars -> blade signs + lit_atrium slots. Words = r2_config
    WORDS / SUBS as is. Absorbs NA-24d. Props KIT DELIVERED (A-024): 32 glb + roles.json in art-pass
    HANDOFF_PACKAGE/street_kit/ (wall plane z=0, +Z out, metres=BU, COLOR_0 sRGB, emissive x MATERIAL_SPEC hierarchy,
    sign_board UV quad for r2_signs textures); import into assets/ per D8 (glb only, no concept images).
  - P6 street (wet reflections, trails, lamp pools, bokeh; post per MATERIAL_SPEC); P7 decision (ghost only 7.1 stubs,
    route rooms read as storefronts, no light columns).
- QUEUED from A-025..A-027 (art-pass c8d2f67e):
  - STREET-CAM (on w1-close): (b) rig distance / shift to plate values in config (overview dist 114.62, shift -0.0548/0.1172;
    decision 42.10, 0.0345/0.0002) AND the plate camera rule: look along the street face's normal at the frontage (r2_onecity
    rule 6), frontage a wall across the frame, never down a cross street. TARGET pencil word + circle inside the safe frame
    (seed 3 overview clipped "TAR"). Derive output logs `retry: leg_extend`. Then publish the seed-1 pose + derive export
    (city.json + derive json) in a B-entry so art-pass re-renders the plates on our street (a); old plates -> `_r2ref`.
  - NA-31b (base branch worktree-agent-a16cf8a4620fba449 @ ce69287e): no landmark channel clips (< 2 % over 0.85, hue
    within ±10° of BEFORE; Meridian orange steel, Solace leaf-green glass, Rebel red #E8141E); ratio from city dim + rim/key
    light + plaza spill instead of key gain; cone occluders ghosted like 7.1 stubs (never black); Meridian's neighbouring
    blocks back (dimmed); Rebel Cell stays k_fit-exempt; Meridian fit = moat compound footprint (exclude crane, rail yard,
    train). Re-sheet BEFORE|AFTER x5 with numbers + mean-hue check.
  - COMBAT-LOCK r2 (A-028; base branch worktree-agent-a78ccb5cfc9d0147e @ 5de0313f): slash drawn with the raid-pencil
    GreasePencilMark stroke (wobble, varying width, wax grain, alpha 0.96, no highlight; ring = one stroke overshooting its
    start, slash = second stroke TL->BR past the ring); re-sheet a re-scribble mid-frame; chase ~1.2 s/lap (3.17: 900-1500 ms);
    Q/E key labels unclipped in the locked state. Re-sheet: 2x held slash, re-scribble mid-frame, chase at new speed.
  - NA-12 r3 (A-030, base w1-close): sea look vs city_a2 plates: night sea deep teal-blue between void and land (median
    value strip void < sea < land), day saturated mid-blue + lighter shallows; marbled caustics + foam; shore reflections =
    soft short vertical smears under each shore light broken by ripple (never regular dashes = grease-pencil vocabulary);
    coping strip brighter/wider scaled by zoom. Re-sheet with plates beside: whole city seed 1 night + day, bay crop, value strip.
  - NA-12 r3 RUNNING (on w1-close). COMBAT-LOCK r2 DONE (branch worktree-agent-aa06f4192301aa04a @ d029c896, review B-019).
  - 2026-10-19 later: STREET-CAM APPROVED (A-034) and merged into w1-close (ab1d758a). P2 step 1 (exact r2 rules port, data
    only) merged to main 2325c775 (pytest 223, precommit green). RUNNING: P2 step 2 (frontage row render, A-034 items 1+4),
    P1+P5 (+ A-034 items 2+3), NA-12 r3, NA-25b r4, NA-ID-c. NA-31b in review (B-021, branch worktree-agent-ac27ef2c44ccd856f
    @ 57eb6d30, not on w1-close). QUEUED: COMBAT-LOCK r3 (A-033: 10-15 % alpha dropout on stroke edges + lighter broken thin
    core, 1:1 + 2x; RESPIN chip crop held + re-scribbled 2x; base branch worktree-agent-aa06f4192301aa04a @ d029c896).
  - Later still: P1+P5 merged into w1-close (ac54140d; fix: bits use nr_clock(anim_t) not TIME, building mat joins the rig
    clock; test_city_shaders had been red on w1-close since NA-25b r2). NA-ID-c merged to main (a8e8c70d). COMBAT-LOCK r3 in
    review (B-025, branch worktree-agent-acf2da816a329ac10 @ b7bb01a6). RUNNING: P2 step 2, P6 (+P7 items, lit-haze sky),
    NA-12 r3, NA-25b r4, W2 WH-11 Solace rules (on w1-close). Defaults: fog body multiplier 0.12 + light unit factors kept.
    Scratch left by agents (blocked rm): D:/rc_tmp, D:/tmp_r3, D:/r3pc.log.
  - QUEUED COMBAT-LOCK r4 (A-036; wheel mark APPROVED): RESPIN chip mark = oval hugging the chip outline (8-12 % margin, same
    wobble/overshoot), slash corner to corner 25 % past the ring, RESPIN + RAM cost readable through it, clamped in the safe frame;
    capture in a taller viewport so the chip is whole. Base branch worktree-agent-acf2da816a329ac10 @ b7bb01a6.
  - QUEUED NA-31c (A-035 CORRECTION: HQ netrun view = AAA-2 chain like the street, NOT cel; only the mainline city map is cel).
    Fixes 1-5 of NA-31b APPROVED, carry over. Base NA-31b branch; starts after P1+P5 lands AND art-pass's HQ addendum to
    MATERIAL_SPEC (own A entry). Targets: 12.2 = each corp's plate ratio_median (hq_<corp>_overview_values.json) +-0.3, R-FOCUS-1
    >= 1.5 drives; clip on luma < 2 % + hue +-10°. Re-sheet AFTER x5 beside hq_<corp>_overview plates. Log the ruling in DECISIONS.
  - (was) QUEUED (A-031): NA-25b r4 on w1-close: no 25x raster (flat class-color hub field + bezel inner ring + emblem native/hi-res,
    centered, whole; same in < 0.5 s breathe); CRT hold: visible hex dump column 15-20 % value, 3 px scanlines at 1:1, cyan edge
    rim, blinking block caret; frame 7: CRT fades with the hub, HUD stays under the lens until the hole passes. Re-sheet 9 tiles +
    2 bits crops (1:1 at 0.55 / 0.30) + 1:1 CRT crop.
  - QUEUED (A-032): NA-ID-c on main: `git apply` art-pass HANDOFF_PACKAGE/id_ground/id_ground.patch, re-run the hq compound +
    landmark builders, tris unchanged except orbital_hq -656, remove the 0.8 BU height cut, re-run the 3 ID frames.
  - W2 adds: NA-12c terrain (hills heightfield render, coastlines, marinas, lighthouse, islands), NA-12d harbour movers (boats
    on the bay, ships at piers, lit offshore platforms).
- PT-005 waits for: w1-close merged, 15, 18.1-18.3 merged.
- Gotcha: TaskStop on a backgrounded `git commit` leaves its run_tests/godot children alive; they race the next
  precommit in %TEMP%/precommit_rebel_cell. Kill them (Get-CimInstance Win32_Process match precommit_rebel_cell).

## Art-pass session
`local_9bc8d6cd-...` ("Resume Art-Pass"); reads spec from art-pass and re-import text into
`docs/handoff/netrun_art/`. Pending from it: W1_NA22 approval after NA-22c; W1_NA23 sheet review. Theme rules drafts
(`docs/handoff/plan2/drafts/themes/`) answer its corp_themes questions; send it rulings as they land.

## How to work
Lanes: Batch for drafts; fix-rules defaults to Sonnet (Opus only with OPUS-BECAUSE); 2 Godot + 1 Python slots.
Merge: union `tests/test_manifest.json` (stages :2/:3), keep both in DECISIONS, smoke-check chain line + both funcs
(check every func still ends with `return fails`), import after new class_names, never a bare `.sort()` on ids
(`IdSort.sort_ids`; allowlist int sorts in `tests/unit/test_no_bare_id_sort.gd`).

## Art-pass mailbox (since 2026-10-19; the app holds cross-session messages after ~10 sends)
- Read art -> build at the start of EVERY turn: `git -C D:/rc_art/art-pass show art-pass:docs/concepts/HANDOFF_PACKAGE/MAILBOX.md` (entries A-NNN).
- Prune: delete your own B entries once art-pass cites them (designer ruling); no history kept.
- Write build -> art: append `### B-NNN · date · topic · VERDICT|RULING|ASK|FYI` to `docs/handoff/netrun_art/MAILBOX_TO_ART.md` on main, commit each; cite "re A-NNN" to mark handled. Sheets must be committed on a branch or main (not only in an agent worktree). A message "mailbox: B-NNN" is an optional wake-up.
