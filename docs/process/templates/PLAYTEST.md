# PT-<nnn> — <title>

gate/<tag> · main @ <sha> · <date> · build: run from the editor (F5) or `godot --path .`

## 1. Scope and changes (what is new for you)
- <screen or system>: <one line, user-visible> (<ART-n / H-n / DECISIONS anchor>)
- ...

Known limits (not FAILs): <list | none>
Settings touched: <text scale / pad / reduce effects / high contrast / skin | none>
Seed for the campaign steps: `<code>` (Title → NEW RUN → CODE → paste)

## 2. Playtest steps
| # | Where (reach it) | Do | Look for | PASS when | Time |
|---|---|---|---|---|---|
| 1 | <screen> → <path in ≤ 3 actions> | <one action> | <one observable> | <one judgeable sentence> | <min> |
| 2 | | | | | |

Total: ~<n> min

## 3. Expected vs actual (how to judge)
PASS = the "PASS when" sentence holds at first sight.
FAIL = it does not, or anything crashes, hangs, shows a `KEY_` / rules-English string, loses input,
or looks wrong for more than a second.
PARTIAL = passes with a nit you would still ship (say what).
SKIP = could not run the step (say why).

## 4. Feedback (paste back as is)
```
PLAYTEST: PT-<nnn>
STATUS: PASS | FAIL | PARTIAL
STEPS: <only the steps that are not PASS, e.g. "3 FAIL, 7 PARTIAL, 12 SKIP">
LOGS: <optional: path to the Godot log, or the ERROR lines>
NOTES: <optional: "<step>: <what you saw>" per line>
RULINGS: <optional: answers to CP-<nnn>, "1A 2C">
```
