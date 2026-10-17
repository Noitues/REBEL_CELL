# Netrun art: batch drafts for the art-pass session, round 1

Lane: Message Batches API (text + images). Plan and surface only. Spend cap: $10.
Source (READ ONLY, never write, checkout, stage or commit there):
`C:/Users/noitu/Documents/Godot/rebel_cell/.claude/worktrees/art-pass` (branch `art-pass`); `docs/concepts/` paths below
are relative to it. Package index: `docs/concepts/HANDOFF_PACKAGE/README.md`. Main-side copies:
`docs/handoff/netrun_art/` (PIPELINE_SPEC, ART_DECISIONS, DIRECTION_REVIEW, INDEX).
Output: `docs/handoff/netrun_art/batch/<item>/` on this worktree, plus `batch/README.md` (index, cost, caveats).
Every output file starts with "DRAFT for the art-pass session; unverified (no render)."

Images: copy to the scratchpad, downscale to at most 1568 px on the long edge (PIL), JPEG q85, then base64. Never
send `docs/concepts` wholesale (4 GB). Reuse the `tools/batch/` builder/submit/ingest pattern; new builder
`tools/batch/build_art_drafts.py`. Put the shared spec context before the cache point.

## Items

1. **landmarks/** (Sonnet, 64k max_tokens): standalone `<corp>_landmark.py` with `build(ctx)` for every corp that lacks
   one (templates: `route_map_graph/hq_meridian_v3/scripts/meridian_landmark.py`,
   `route_map_graph/hq_tethys/scripts/tethys_landmark.py`; per-corp DESIGN/NOTES under `route_map_graph/hq_*/`,
   `new_corps/roman/identity.md` for Aurelian). Same API and conventions as the templates; one file per corp plus a
   notes file listing assumptions.
2. **spec_audit/** (Sonnet): contradictions, missing cross-references, stale names (THE PANOPTICON, not Civic
   Core), and the open numbers N1-N5 across PIPELINE_SPEC, DIRECTION_REVIEW, `route_map_graph/decisions/`, and the GDD
   naming sections. A table with section refs and a suggested fix each.
3. **vision_review/** (Sonnet, images): one request per corp with its OVERVIEW / DECISION / HOVER finals (list in
   the package README section 8) plus the ART_BIBLE v2 rules; findings per frame (rule breaks, readability, how the set
   holds together), then a cross-corp summary request built from those findings.
4. **aurelian_design/** (Sonnet): a DESIGN.md draft for the Aurelian Concord HQ, following the existing
   `hq_*/DESIGN.md` pattern and designer ruling D10 (every HQ netrun unique, may exceed 7 layers; see
   `docs/handoff/gates/REPLAN_2026-10-16.md` and `docs/DECISIONS.md` 2026-10-16).
5. **tethys_shots/** (Sonnet, images): shot and state specs (camera, framing, states shown) for the missing Tethys
   DECISION and HOVER finals, matched to the other corps' finals.
6. **golden_plates/** (Sonnet): a draft spec section for golden plates and Python/GDScript parity (spec sections 8,
   11, 12, esp. 12.6).
7. **asset_coverage/** (Haiku): a matrix from main's `docs/art_asset.md` against the approved-image index: which image
   covers each asset, and the gaps.

## Finish

Commit only `docs/handoff/netrun_art/batch/**` and `tools/batch/build_art_drafts.py` (message lists items and
cost); run `QUICK=1 bash tools/precommit.sh --base main`; tag `art-batch-1`. Payloads and ids stay in the scratchpad.
Retry truncated requests alone at a higher max_tokens.
