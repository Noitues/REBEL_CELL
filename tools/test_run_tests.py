"""Unit tests for tools/run_tests.py (ANIM-R6 D4; docs/TEST_SUITE.md "The runner's own tests").

    python tools/test_run_tests.py

Standard library only (unittest). Written as a file on purpose: never run Python from stdin
on this machine. tests/unit/test_anim_r6_rules.gd runs this file too, so the full suite
covers the runner.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True  # no __pycache__ in the project
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_tests  # noqa: E402

GOOD = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="GutTests" failures="1" tests="2">
  <testsuite name="tests/unit/test_a.gd" tests="2" failures="1">
    <testcase name="test_one" assertions="1" status="pass" classname="tests/unit/test_a.gd" time="0.5"></testcase>
    <testcase name="test_two" assertions="1" status="fail" classname="tests/unit/test_a.gd" time="0.25">
      <failure message="failed">it broke</failure>
    </testcase>
  </testsuite>
</testsuites>
"""


class ReadResults(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory(prefix="rebel_cell_runner_test_")
        self.path = Path(self.dir.name) / "results.xml"

    def tearDown(self) -> None:
        self.dir.cleanup()

    def test_good_results_are_read(self) -> None:
        self.path.write_text(GOOD, encoding="utf-8")
        res, why = run_tests.read_results(self.path)
        self.assertEqual(why, "")
        self.assertEqual(res["tests"], 2)
        self.assertEqual(len(res["failures"]), 1)
        self.assertAlmostEqual(res["times"]["res://tests/unit/test_a.gd"], 0.75)

    def test_missing_results_are_a_problem_not_a_crash(self) -> None:
        res, why = run_tests.read_results(self.path)
        self.assertIsNone(res)
        self.assertIn("no results", why)

    def test_empty_results_are_a_problem_not_a_crash(self) -> None:
        self.path.write_text("", encoding="utf-8")
        res, why = run_tests.read_results(self.path)
        self.assertIsNone(res)
        self.assertIn("empty", why)

    def test_truncated_results_are_a_problem_not_a_crash(self) -> None:
        # The disk-full case: the file stops mid-element.
        self.path.write_text(GOOD[: len(GOOD) // 2], encoding="utf-8")
        res, why = run_tests.read_results(self.path)
        self.assertIsNone(res)
        self.assertIn("cut short", why)


class RerunAndDisk(unittest.TestCase):
    def test_not_run_scripts_are_rerun_with_the_failing_ones(self) -> None:
        failures = [("res://tests/unit/test_b.gd", "test_x", "msg"), ("res://tests/unit/test_b.gd", "test_y", "msg")]
        again = run_tests.rerun_list(failures, ["res://tests/unit/test_c.gd", "res://tests/unit/test_a.gd"])
        self.assertEqual(again, ["res://tests/unit/test_a.gd", "res://tests/unit/test_b.gd", "res://tests/unit/test_c.gd"])

    def test_the_disk_check_fails_warns_and_passes(self) -> None:
        self.assertEqual(run_tests.disk_check(0.5, 1.0, 5.0)[0], "fail")
        self.assertIn("free some disk space", run_tests.disk_check(0.5, 1.0, 5.0)[1])
        self.assertEqual(run_tests.disk_check(3.0, 1.0, 5.0)[0], "warn")
        self.assertEqual(run_tests.disk_check(20.0, 1.0, 5.0)[0], "ok")

    def test_the_suite_guards_findings_are_read_from_the_log(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rebel_cell_runner_test_") as d:
            log = Path(d) / "gut.log"
            log.write_text("* test_a\n\x1b[0mSETTINGS LEAK res://tests/unit/test_a.gd: tutorial_done\nORPHAN LEFT <Control#1> (Label)\nok\n",
                           encoding="utf-8")
            self.assertEqual(run_tests.guard_lines(log), ["SETTINGS LEAK res://tests/unit/test_a.gd: tutorial_done",
                                                          "ORPHAN LEFT <Control#1> (Label)"])
            self.assertEqual(run_tests.guard_lines(Path(d) / "missing.log"), [])
            log.write_text("WARNING: 213 ObjectDB instances were leaked at exit (run with `--verbose` for details).\n"
                           "WARNING: 3 RIDs of type \"CanvasItem\" were leaked.\nfine\n", encoding="utf-8")
            self.assertEqual(len(run_tests.guard_lines(log)), 2, "the engine's exit leaks are problems too")

    def test_free_space_is_read_for_a_folder_not_made_yet(self) -> None:
        self.assertGreater(run_tests.free_gb(Path(tempfile.gettempdir()) / "not" / "made" / "yet"), 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=1)
