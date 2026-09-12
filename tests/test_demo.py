from datetime import date
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("demo", ROOT / "scripts/run_demo.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.nutrition = {"report_date": "2024-03-15", "day_total": {
            "kcal": 2220, "protein": 115, "fat": 80, "carbs": 260},
            "check_kcal_from_macros": 2220, "warnings": []}
        fixture = ROOT / "examples/synthetic"
        self.activity = json.loads((fixture / "activity.json").read_text())
        self.assumptions = json.loads((fixture / "assumptions.json").read_text())

    def run_case(self):
        return demo.process(self.nutrition, self.activity, self.assumptions, as_of=date(2024, 3, 20))

    def test_complete_arithmetic(self):
        result = self.run_case()
        self.assertEqual(result["estimate"]["estimated_expenditure_kcal"], 2222)
        self.assertEqual(result["estimate"]["intake_minus_estimate_kcal"], -2)
        self.assertEqual(result["model"]["calls"], 0)

    def test_missing_and_stale_withhold_estimate(self):
        for status in ("missing", "stale"):
            with self.subTest(status=status):
                self.activity["status"] = status
                result = self.run_case()
                self.assertIsNone(result["estimate"])
                self.assertIsNone(result["activity"]["steps"])
                self.assertIn("withheld", demo.render(result))

    def test_real_zero_steps_is_distinct_from_missing(self):
        self.activity["steps"] = 0
        self.assertEqual(self.run_case()["estimate"]["activity_kcal"], 0)

    def test_date_mismatch_rejected(self):
        self.activity["report_date"] = "2024-03-14"
        with self.assertRaisesRegex(ValueError, "dates differ"):
            self.run_case()

    def test_future_date_rejected(self):
        with self.assertRaisesRegex(ValueError, "future"):
            demo.process(self.nutrition, self.activity, self.assumptions, as_of=date(2024, 3, 1))

    def test_missing_nutrition_rejected(self):
        del self.nutrition["day_total"]["protein"]
        with self.assertRaisesRegex(ValueError, "missing"):
            self.run_case()

    def test_invalid_steps_rejected(self):
        for value in (-1, None, True, 1.5):
            with self.subTest(value=value):
                self.activity["steps"] = value
                with self.assertRaises(ValueError):
                    self.run_case()

    def test_nonfinite_and_negative_coefficients_rejected(self):
        for value in ("NaN", "Infinity", -1):
            with self.subTest(value=value):
                self.assumptions["base_kcal"] = value
                with self.assertRaises(ValueError):
                    self.run_case()

    def test_fixture_label_required(self):
        self.activity["synthetic"] = False
        with self.assertRaisesRegex(ValueError, "synthetic"):
            self.run_case()

    def test_journal_replay_and_correction(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "journal.json"
            first = self.run_case()
            for _ in range(2):
                demo.upsert_journal(path, first["report_date"], first)
            self.assertEqual(len(json.loads(path.read_text())), 1)
            self.activity["steps"] = 8000
            corrected = self.run_case()
            demo.upsert_journal(path, corrected["report_date"], corrected)
            stored = json.loads(path.read_text())
            self.assertEqual(len(stored), 1)
            self.assertEqual(stored[corrected["report_date"]]["activity"]["steps"], 8000)


class CommandTests(unittest.TestCase):
    def test_end_to_end_expected_artifacts_and_repeat(self):
        with tempfile.TemporaryDirectory() as folder:
            command = [sys.executable, str(ROOT / "scripts/run_demo.py"), "--output", folder]
            for _ in range(2):
                run = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
            for name in ("report.md", "result.json"):
                self.assertEqual((Path(folder) / name).read_bytes(),
                                 (ROOT / "examples/expected" / name).read_bytes())
            self.assertEqual(len(json.loads((Path(folder) / "journal.json").read_text())), 1)

    def test_cli_mismatch_writes_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "uncreated"
            run = subprocess.run([sys.executable, str(ROOT / "scripts/run_demo.py"),
                                  "--scenario", "date-mismatch", "--output", str(output)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertFalse(output.exists())

    def test_german_utf16_decimal_comma(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "FoodDiary_240315_foods.csv"
            path.write_bytes("Name;Kalorien;Fett;Kohlenhydrate;Eiweiß\nDemo;100;2,5;10;9,4\nGesamt;100;2,5;10;9,4\n".encode("utf-16"))
            run = subprocess.run([sys.executable, str(ROOT / "scripts/fatsecret_parse.py"),
                                  "--file", str(path)], capture_output=True, text=True, check=True)
            result = json.loads(run.stdout)
            self.assertEqual(result["day_total"]["fat"], 2.5)
            self.assertEqual(result["day_total"]["kcal"], 100)

    def test_day_total_not_double_counted(self):
        run = subprocess.run([sys.executable, str(ROOT / "scripts/fatsecret_parse.py"), "--file",
                              str(ROOT / "examples/synthetic/FoodDiary_240315_foods.csv")],
                             capture_output=True, text=True, check=True)
        result = json.loads(run.stdout)
        self.assertEqual(result["day_total"]["kcal"], 2220)
        self.assertEqual(result["totals_summed"]["kcal"], 2220)
        self.assertEqual(result["row_count"], 3)

    def test_bad_header_reports_error(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "FoodDiary_240315_foods.csv"
            path.write_text("Synthetic;unknown\nExample;12\n")
            run = subprocess.run([sys.executable, str(ROOT / "scripts/fatsecret_parse.py"),
                                  "--file", str(path)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            self.assertIn("error", json.loads(run.stdout))


if __name__ == "__main__":
    unittest.main()
