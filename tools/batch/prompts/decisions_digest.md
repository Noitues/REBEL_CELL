# Task: decision-log digest

The file is a slice of `docs/DECISIONS.md` (one milestone or date range). Produce a digest that
an agent can read instead of the slice. No patch: put the digest in RC_NOTES, status: ok.

Format:
```
## <section title as given>
- RULING <date> <topic>: <one line, the binding rule, with the superseding entry if any>
- DEFAULT <topic>: <value and where it lives (config file / const)>
- OPEN <topic>: <the question, who must answer, and the default taken meanwhile>
- SUPERSEDED <topic>: <by what>
```
Rules: keep every binding ruling and every open question; drop narrative, review sheets,
captures and per-pixel values unless a ruling depends on them; keep dates; never merge two
rulings into one line; keep names exactly as written (raid words, screen names, config keys).
Target: under 10 % of the input length.
