#!/bin/bash
# Pre-commit checks for REBEL_CELL (docs/process/01_PROCESS_OPTIMIZATION_PLAN.md, "Diff-based testing").
# Cheap and local: parse-check every staged .gd, the schema smoke test only if scripts/data changed,
# content validation only if content/ changed, then the diff-selected tests. Never the full suite.
#
#   bash tools/precommit.sh            # staged files
#   bash tools/precommit.sh --base main  # everything changed vs main (hand-back)
#
# Logs go to $SP (default %TEMP%\precommit_<worktree folder name>: one per worktree, so runs in two
# worktrees at once never share or overwrite each other's logs and test shards). Prints one "name=<exit>" line per step;
# exits non-zero on the first red step. Install as a hook with:
#   printf '#!/bin/sh\nbash tools/precommit.sh\n' > .git/hooks/pre-commit   (the shebang is required; git cannot spawn the hook without it)
cd "$(git rev-parse --show-toplevel)" || exit 1
SP="${SP:-$TEMP/precommit_$(basename "$PWD")}"; mkdir -p "$SP"   # $PWD is the worktree root (cd above)
MODE="--staged"; BASE=""
if [ "$1" = "--base" ]; then MODE=""; BASE="--base $2"; fi

if [ -n "$MODE" ]; then
  FILES=$(git diff --name-only --cached)
else
  FILES=$( (git diff --name-only "${2:-main}...HEAD"; git diff --name-only --cached; git diff --name-only; git ls-files --others --exclude-standard) | sort -u)  # committed, staged, unstaged, new
fi
[ -z "$FILES" ] && { echo "precommit: nothing changed"; exit 0; }

# 1. Parse check of changed scripts: ONE Godot process for all of them (D15; ~6 s start-up per file before).
# tools/parse_check.gd, not --check-only: that stops before the autoloads' names exist (Dialogue, Settings).
rc=0
GD=""
for f in $(echo "$FILES" | grep -E '\.gd$' | grep -v '\.uid$'); do
  [ -f "$f" ] && GD="$GD $f"
done
if [ -n "$GD" ]; then
  timeout 600 godot --headless --path . -s tools/parse_check.gd -- $GD >"$SP/check.log" 2>&1 || { rc=1; grep "PARSE CHECK FAIL" "$SP/check.log" | sed 's/^/PARSE FAIL: /'; tail -n 5 "$SP/check.log"; }
fi
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

# 4. Suite-rule tests (D18): always run, in QUICK mode too (cheap; they caught 7 of the PT-003 merge-only reds).
RULES="--select test_suite_integrity --select test_visual_lint_static --select test_vfx_tiers --select test_art0_kit_words --select test_art12b_skin_chrome --select test_anim_r6_rules"
# 5. Tests. QUICK=1 (agent commits and hand-backs, designer 2026-10-13): only the changed test scripts themselves,
# minutes not tens of minutes; the orchestrator runs ONE full diff-selected check per wave batch.
if [ "${QUICK:-0}" = "1" ]; then
  SEL="$RULES"
  for f in $(echo "$FILES" | grep -E '^tests/.*\.gd$' | grep -v '\.uid$'); do
    [ -f "$f" ] && SEL="$SEL --select $(basename "$f" .gd)"
  done
  python tools/run_tests.py -j "${JOBS:-4}" --out "$SP/tests" $SEL > "$SP/tests.log" 2>&1 < /dev/null; r=$?
  echo "tests=$r"; tail -n 3 "$SP/tests.log"
  exit $r
fi
python tools/run_tests.py -j "${JOBS:-4}" --out "$SP/rules" $RULES > "$SP/rules.log" 2>&1 < /dev/null; r=$?
echo "rules=$r"; [ $r -ne 0 ] && { tail -n 5 "$SP/rules.log"; exit 1; }
# Diff-selected tests (falls back to the fast tier when nothing maps).
python tools/select_tests.py $MODE $BASE -j "${JOBS:-4}" --out "$SP/tests" > "$SP/tests.log" 2>&1 < /dev/null; r=$?
echo "tests=$r"; tail -n 3 "$SP/tests.log"
exit $r
