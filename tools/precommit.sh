#!/bin/bash
# Pre-commit checks for REBEL_CELL (docs/process/01_PROCESS_OPTIMIZATION_PLAN.md, "Diff-based testing").
# Cheap and local: parse-check every staged .gd, the schema smoke test only if scripts/data changed,
# content validation only if content/ changed, then the diff-selected tests. Never the full suite.
#
#   bash tools/precommit.sh            # staged files
#   bash tools/precommit.sh --base main  # everything changed vs main (hand-back)
#
# Logs go to $SP (default %TEMP%\rebel_cell_precommit). Prints one "name=<exit>" line per step;
# exits non-zero on the first red step. Install as a hook with:
#   printf 'bash tools/precommit.sh\n' > .git/hooks/pre-commit
cd "$(git rev-parse --show-toplevel)" || exit 1
SP="${SP:-$TEMP/rebel_cell_precommit}"; mkdir -p "$SP"
MODE="--staged"; BASE=""
if [ "$1" = "--base" ]; then MODE=""; BASE="--base $2"; fi

if [ -n "$MODE" ]; then
  FILES=$(git diff --name-only --cached)
else
  FILES=$( (git diff --name-only "${2:-main}...HEAD"; git diff --name-only; git ls-files --others --exclude-standard) | sort -u)
fi
[ -z "$FILES" ] && { echo "precommit: nothing changed"; exit 0; }

# 1. Parse check of changed scripts (seconds per file; catches typos before any test runs).
rc=0
for f in $(echo "$FILES" | grep -E '\.gd$' | grep -v '\.uid$'); do
  [ -f "$f" ] || continue
  timeout 120 godot --headless --path . --check-only -s "$f" > "$SP/check_$(basename "$f").log" 2>&1 || { echo "PARSE FAIL: $f"; tail -n 5 "$SP/check_$(basename "$f").log"; rc=1; }
done
echo "parse=$rc"; [ $rc -ne 0 ] && exit 1

# 2. Schema smoke test only when the schemas changed (CLAUDE.md rule 8).
if echo "$FILES" | grep -qE '^(scripts/data/|tools/schema_smoke)'; then
  timeout 300 godot --headless --path . -s tools/schema_smoke_test.gd > "$SP/smoke.log" 2>&1; r=$?
  if [ $r -ne 0 ] && grep -q "SCHEMA SMOKE TEST: PASS" "$SP/smoke.log"; then r=0; fi   # exit 139 after PASS is known
  echo "smoke=$r"; [ $r -ne 0 ] && { tail -n 5 "$SP/smoke.log"; exit 1; }
fi

# 3. Content validation only when content changed.
if echo "$FILES" | grep -qE '^content/'; then
  timeout 300 godot --headless --path . -s tools/validate_content.gd > "$SP/validate.log" 2>&1; r=$?
  echo "validate=$r"; [ $r -ne 0 ] && { tail -n 5 "$SP/validate.log"; exit 1; }
fi

# 4. Diff-selected tests (falls back to the fast tier when nothing maps).
python tools/select_tests.py $MODE $BASE -j "${JOBS:-2}" --out "$SP/tests" > "$SP/tests.log" 2>&1 < /dev/null; r=$?
echo "tests=$r"; tail -n 3 "$SP/tests.log"
exit $r
