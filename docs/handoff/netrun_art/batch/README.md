DRAFT for the art-pass session; unverified (no render).

# Netrun art batch round 1 (BATCH_ART1)

Drafts for the art-pass session, made with the Message Batches API (Sonnet 5.5; asset_coverage on Haiku 4.5). Plan and surface only:
nothing here was rendered or run. Built by `tools/batch/build_art_drafts.py` from the read-only art-pass clone
(`docs/concepts`, branch `art-pass`). Images were downscaled to <= 1568 px (JPEG q85) before sending, so fine detail may be missed.

Total cost (batch price, all attempts including retries): **$2.53**.

| item | file | status | out tokens | cost |
|---|---|---|---|---|
| lm__halcyon | [landmarks/halcyon_landmark.py](landmarks/halcyon_landmark.py) | ok | 7,403 | $0.221 |
| lm__solace | [landmarks/solace_landmark.py](landmarks/solace_landmark.py) | ok | 17,729 | $0.132 |
| lm__orbital | [landmarks/orbital_landmark.py](landmarks/orbital_landmark.py) | ok | 21,566 | $0.228 |
| lm__aurelian | [landmarks/aurelian_landmark.py](landmarks/aurelian_landmark.py) | ok | 10,237 | $0.074 |
| lm__rebel_cell | [landmarks/rebel_cell_landmark.py](landmarks/rebel_cell_landmark.py) | ok | 14,197 | $0.254 |
| audit__contradictions | [spec_audit/contradictions.md](spec_audit/contradictions.md) | ok | 39,162 | $0.488 |
| audit__naming_open_numbers | [spec_audit/naming_and_open_numbers.md](spec_audit/naming_and_open_numbers.md) | ok | 6,167 | $0.046 |
| vis__halcyon | [vision_review/halcyon.md](vision_review/halcyon.md) | ok | 4,121 | $0.034 |
| vis__orbital | [vision_review/orbital.md](vision_review/orbital.md) | ok | 5,457 | $0.051 |
| vis__rebel_cell | [vision_review/rebel_cell.md](vision_review/rebel_cell.md) | ok | 3,985 | $0.113 |
| vis__solace | [vision_review/solace.md](vision_review/solace.md) | ok | 3,345 | $0.041 |
| vis__meridian | [vision_review/meridian.md](vision_review/meridian.md) | ok | 6,273 | $0.124 |
| vis__tethys | [vision_review/tethys.md](vision_review/tethys.md) | ok | 4,405 | $0.033 |
| vis__summary | [vision_review/SUMMARY.md](vision_review/SUMMARY.md) | ok | 4,227 | $0.125 |
| aur__design | [aurelian_design/DESIGN.md](aurelian_design/DESIGN.md) | ok | 9,225 | $0.117 |
| tsh__shots | [tethys_shots/SHOTS.md](tethys_shots/SHOTS.md) | ok | 9,603 | $0.110 |
| gold__spec | [golden_plates/SPEC_SECTION.md](golden_plates/SPEC_SECTION.md) | ok | 38,404 | $0.200 |
| cov__a_f | [asset_coverage/MATRIX_A_F.md](asset_coverage/MATRIX_A_F.md) | ok | 12,942 | $0.072 |
| cov__g_m | [asset_coverage/MATRIX_G_M.md](asset_coverage/MATRIX_G_M.md) | ok | 11,723 | $0.071 |

Caveats:
- `landmarks/*.py` were checked with `ast.parse` only (see the provenance comment); they have never run against the city namespace.
- `vision_review` is a read of downscaled stills by a model: treat each finding as a lead to verify, not a verdict.
- `asset_coverage` is Haiku: spot-check NONE/PARTIAL rows before using the counts.
- Contradiction rows in `spec_audit` quote the spec as of art-pass@7f021c21 (working tree of the clone when built).
