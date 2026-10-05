#!/bin/bash
# import + full suite (one run; RUNS=3 to repeat after a failure) + schema smoke + content validation.
# usage: bash docs/handoff/art_0/process/checks.sh   (logs in $SP, default %TEMP%\rebel_cell_checks)
cd "$(git rev-parse --show-toplevel)" || exit 1
SP="${SP:-$TEMP/rebel_cell_checks}"; mkdir -p "$SP"
timeout 900 godot --headless --path . --import > "$SP/import_c.log" 2>&1
echo "import=$?"
for i in $(seq 1 "${RUNS:-1}"); do
  timeout 1800 python tools/run_tests.py -j 4 > "$SP/runner_$i.log" 2>&1 < /dev/null
  echo "runner$i=$?"
  tail -n 3 "$SP/runner_$i.log"
done
timeout 300 godot --headless --path . -s tools/schema_smoke_test.gd > "$SP/smoke.log" 2>&1
r=$?
if [ $r -ne 0 ] && grep -q "SCHEMA SMOKE TEST: PASS" "$SP/smoke.log"; then
  timeout 300 godot --headless --path . -s tools/schema_smoke_test.gd > "$SP/smoke.log" 2>&1; r=$?
fi
echo "smoke=$r"; tail -n 2 "$SP/smoke.log"
timeout 300 godot --headless --path . -s tools/validate_content.gd > "$SP/validate.log" 2>&1
echo "validate=$?"; tail -n 2 "$SP/validate.log"
grep -E '"text_scale"|"keybinds"' "$APPDATA/Godot/app_userdata/REBEL_CELL/settings.json"
