"""Offline portfolio demonstration. Every input is synthetic; no model/API calls."""
from __future__ import annotations

import argparse
from datetime import date
from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def number(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("invalid numeric input") from exc
    if not result.is_finite() or result < 0:
        raise ValueError("numeric inputs must be finite and non-negative")
    return result


def process(nutrition, activity, assumptions, *, as_of):
    """Bind observations to a date before calculating an explicitly toy estimate."""
    if nutrition.get("error"):
        raise ValueError("nutrition parsing failed")
    report_date = date.fromisoformat(nutrition.get("report_date") or "")
    if report_date > as_of:
        raise ValueError("future report date")
    if activity.get("report_date") != report_date.isoformat():
        raise ValueError("nutrition and activity dates differ")
    if activity.get("synthetic") is not True or assumptions.get("synthetic") is not True:
        raise ValueError("demo requires explicitly synthetic fixtures")
    status = activity.get("status")
    if status not in {"available", "missing", "stale"}:
        raise ValueError("unsupported activity status")
    day = nutrition.get("day_total") or {}
    for key in ("kcal", "protein", "fat", "carbs"):
        if key not in day:
            raise ValueError("required nutrition field is missing")
        number(day[key])
    steps = activity.get("steps")
    if status == "available":
        if type(steps) is not int or steps < 0:
            raise ValueError("available steps must be a non-negative integer")
    estimate = None
    if status == "available":
        base = number(assumptions["base_kcal"])
        # This public toy model does NOT copy the private athlete's coefficients.
        activity_kcal = number(steps) * number(assumptions["kcal_per_step"])
        workout = number(assumptions["workout_kcal"])
        rate = number(assumptions["tef_rate"])
        if rate > 1:
            raise ValueError("invalid TEF fraction")
        tef = number(day["kcal"]) * rate
        total = base + activity_kcal + workout + tef
        estimate = {"base_kcal": float(base), "activity_kcal": float(activity_kcal),
                    "workout_kcal": float(workout), "tef_kcal": float(tef),
                    "estimated_expenditure_kcal": float(total),
                    "intake_minus_estimate_kcal": float(number(day["kcal"]) - total)}
    return {"synthetic": True, "mode": "offline_fixture_demo",
            "report_date": report_date.isoformat(), "nutrition": day,
            "macro_kcal_check": nutrition.get("check_kcal_from_macros"),
            "warnings": nutrition.get("warnings", []),
            "activity": {"status": status, "steps": steps if status == "available" else None,
                         "source": "synthetic Garmin-shaped fixture; not a Garmin API response"},
            "estimate": estimate,
            "model": {"mode": "deterministic_mock", "calls": 0},
            "next_action": "Review the synthetic report; no training or dietary prescription is generated."}


def render(result):
    day = result["nutrition"]
    lines = ["# Synthetic daily report", "", "Demo data only. No live API or model was called.", "",
             f"Date: {result['report_date']}", "",
             f"Logged intake: {day['kcal']:g} kcal; protein {day['protein']:g} g; "
             f"fat {day['fat']:g} g; carbohydrate {day['carbs']:g} g.",
             f"Macro arithmetic check: {result['macro_kcal_check']} kcal.",
             f"Activity status: {result['activity']['status']}."]
    if result["estimate"]:
        e = result["estimate"]
        lines += [f"Steps: {result['activity']['steps']} (synthetic).",
                  f"Toy estimate: {e['base_kcal']:g} + {e['activity_kcal']:g} + "
                  f"{e['workout_kcal']:g} + {e['tef_kcal']:g} = {e['estimated_expenditure_kcal']:g} kcal.",
                  f"Intake minus toy estimate: {e['intake_minus_estimate_kcal']:+g} kcal."]
    else:
        lines.append("Expenditure and balance withheld: current activity data is unavailable.")
    lines += ["", result["next_action"], "", "This is a reproducible software example, not a health assessment."]
    return "\n".join(lines) + "\n"


def upsert_journal(path, report_date, report):
    """Single-process demo upsert; not an atomic transaction across output files."""
    existing = json.loads(path.read_text()) if path.exists() else {}
    existing[report_date] = report
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".journal-")
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(existing, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=("complete", "missing", "stale", "date-mismatch"), default="complete")
    parser.add_argument("--output", type=Path, default=Path("demo-output"))
    args = parser.parse_args()
    fixture = ROOT / "examples/synthetic"
    parsed = subprocess.run([sys.executable, str(ROOT / "scripts/fatsecret_parse.py"),
                             "--file", str(fixture / "FoodDiary_240315_foods.csv")],
                            capture_output=True, text=True, check=True)
    activity = json.loads((fixture / "activity.json").read_text())
    if args.scenario in {"missing", "stale"}:
        activity["status"] = args.scenario
        activity["steps"] = None
    if args.scenario == "date-mismatch":
        activity["report_date"] = "2024-03-16"
    try:
        result = process(json.loads(parsed.stdout), activity,
                         json.loads((fixture / "assumptions.json").read_text()), as_of=date(2024, 3, 20))
    except ValueError as exc:
        print(json.dumps({"synthetic": True, "error": str(exc)}))
        return 2
    args.output.mkdir(parents=True, exist_ok=True)
    response = render(result)
    (args.output / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (args.output / "report.md").write_text(response)
    upsert_journal(args.output / "journal.json", result["report_date"], result)
    print(response, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
