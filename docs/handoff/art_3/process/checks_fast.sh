#!/bin/bash
# Per-merge / per-hand-back checks (designer 2026-10-05): import + fast tier + schema smoke + content validation.
# The full suite (checks.sh, one run) runs once per ART group, at its end, in isolation (no agents running).
# usage: bash docs/handoff/art_3/process/checks_fast.sh   (logs in $SP, default %TEMP%\rebel_cell_checks)
cd "$(git rev-parse --show-toplevel)" || exit 1
SP="${SP:-$TEMP/rebel_cell_checks}"; mkdir -p "$SP"
timeout 900 godot --headless --path . --import > "$SP/import_c.log" 2>&1
echo "import=$?"
timeout 1200 python tools/run_tests.py --tier fast -j "${JOBS:-2}" > "$SP/fast.log" 2>&1 < /dev/null
echo "fast=$?"; tail -n 3 "$SP/fast.log"
timeout 300 godot --headless --path . -s tools/schema_smoke_test.gd > "$SP/smoke.log" 2>&1
r=$?
if [ $r -ne 0 ] && grep -q "SCHEMA SMOKE TEST: PASS" "$SP/smoke.log"; then
  timeout 300 godot --headless --path . -s tools/schema_smoke_test.gd > "$SP/smoke.log" 2>&1; r=$?
fi
echo "smoke=$r"; tail -n 2 "$SP/smoke.log"
timeout 300 godot --headless --path . -s tools/validate_content.gd > "$SP/validate.log" 2>&1
echo "validate=$?"; tail -n 2 "$SP/validate.log"
