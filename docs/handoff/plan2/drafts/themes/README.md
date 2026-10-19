# Corporation-wide theme drafts (round THEMES)

Drafted on the Message Batches API (Sonnet 5.5) by `tools/batch/build_themes.py`. Drafts only: the designer picks; rules land beside each HQ in W2.
Each file: rules (street / HQ / raid), state + save, preview, numbers (config placeholders), tests, art answers, reuse, `Q-DESIGNER:` lines.

| Corp | File | Status | Q-DESIGNER |
|---|---|---|---|
| Solace: THE BLOOM | solace.md | settled | 6 |
| Halcyon: the Eye | halcyon.md | settled | 5 |
| REBEL_CELL: DISPATCH | rebel_cell.md | settled (reconciled with Q34) | 5 |
| Aurelian: colosseum rings | aurelian.md | settled | 6 |
| Tethys: THE WATER LEVEL | tethys.md | settled (extends HQ sections 1-3) | 6 |
| Meridian | meridian.md | OPTIONS (4, designer chooses) | 5 |
| Orbital | orbital.md | OPTIONS (4, designer chooses) | 6 |

Total Q-DESIGNER: 39.

Cost: first batch (7 requests, max_tokens 14000) 0.645 USD; three of them (aurelian, halcyon, orbital) hit the cap and were re-run
with max_tokens 30000 (0.287 USD), so the kept drafts cost about 0.65 USD and the whole spend is about 0.93 USD.
