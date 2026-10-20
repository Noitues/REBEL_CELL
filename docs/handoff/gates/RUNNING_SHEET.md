# Running decisions and questions sheet

The designer reviews this on request. Each line is a call I made without waiting for a ruling. Answer by code, for example
"D3 B" or "Q2 no"; a line with no answer stands. Newest entries go at the top of each section. Full reasoning is in
`docs/DECISIONS.md`.

Standing directive (designer, 2026-10-19):
- Skip the PT gates. Work through W1 to W4 and Later until all content is in.
- Use the Batch API and cheaper models.
- Art-pass does all visual work; this session keeps game code only.
- Make the calls and log them here.

## Calls made (revisit any)
| Code | Date | Call | Alternative |
|---|---|---|---|
| D3 | 10-19 | Every THEMES2 follow-up (ME1-5, OR1-6, SO1-4, HA1-6, RC1-5, AU1-3, TE1-4) took its recommended default, so W2 builds from the v2 drafts. The list is in `THEMES2_FOLLOWUP_2026-10-19.md`. | Answer any code to change it |
| D2 | 10-19 | Old route window: the fallback page stays (a street that can't be derived still gets a route page; GRID VIEW and boss runs use the same code). Only the test-only `street_route` flag is removed. | B: drop the fallback and show an error page, removing about 200 lines |
| D1 | 10-19 | PT gates are skipped per wave. Before every push of main, the user-ready gate still runs the full suite once, plus smoke and validate (CLAUDE.md). | none |

## Open questions (a default is taken; answer to change it)
| Code | Date | Question | Default taken |
|---|---|---|---|
| Q1 | 10-19 | Solace v2: infection decay after a held raid: partial (flat amount plus kills), or a full reset to 0? | Partial decay |
| Q2 | 10-19 | Solace v2: do Heat objective Sites and Proxy Relay completions also cure infection? | Yes, both cure |
| Q3 | 10-19 | Solace v2: cap the combined Exploit slowdown when all three are stacked? | No cap; tune after the sim |
| Q4 | 10-19 | Solace v2: does Heat pace reach 160 % at PURGE? | Yes, 160 % |
