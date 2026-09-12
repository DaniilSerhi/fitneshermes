#!/usr/bin/env python3
"""Deterministic FatSecret food-diary CSV parser.
Usage:  python3 fatsecret_parse.py --url "<export url>"   |   --file path.csv
Output: JSON {encoding, delimiter, totals_summed, file_total_row, check_kcal_from_macros, row_count, warnings}
Handles: UTF-16/UTF-16-LE/UTF-8-sig/cp1252, German+English headers, decimal commas, meal-section rows.
"""
import argparse, csv, io, json, re, sys, urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

COLMAP = {
    "kcal":    ["kalorien", "calories", "energie", "kcal"],
    "fat":     ["fett", "fat"],
    "carbs":   ["kohlenhydrate", "kohlh", "carbs", "carbohydrate"],
    "protein": ["eiwei", "eiw", "protein"],
    "na_mg":   ["natrium", "sodium", "na("],
    "k_mg":    ["kalium", "potassium"],
    "sugar":   ["zucker", "zuck", "sugar"],
    "chol_mg": ["cholesterin", "chol", "cholesterol"],
}
TOTAL_MARKERS = ["gesamt", "total", "summe"]
WEEKDAY_MARKERS = ["montag", "dienstag", "mittwoch", "donnerstag", "freitag", "samstag", "sonntag",
                   "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
MEAL_MARKERS = ["frühstück", "fruhstuck", "mittagessen", "abendessen", "snacks", "snack",
                "breakfast", "lunch", "dinner", "andere", "other"]


def report_date_from_source(source: str):
    """Extract the diary date from FatSecret's FoodDiary_YYMMDD filename."""
    parsed = urlparse(source)
    filename = Path(unquote(parsed.path if parsed.scheme else source)).name
    match = re.search(r"FoodDiary_(\d{6})_foods\.csv$", filename, re.IGNORECASE)
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%y%m%d").date().isoformat()
    except ValueError:
        return None

def decode(raw: bytes):
    for enc in ("utf-16", "utf-16-le", "utf-8-sig", "utf-8", "cp1252"):
        try:
            t = raw.decode(enc)
            if "alorien" in t or "alories" in t or "kcal" in t.lower():
                return t, enc
        except (UnicodeDecodeError, UnicodeError):
            continue
    return raw.decode("utf-8", errors="replace"), "utf-8(replace)"

def to_num(cell: str):
    if cell is None: return None
    c = cell.strip().replace(" ", "")
    if not c or c in ("-", "--"): return None
    c = re.sub(r"[^\d,.\-]", "", c)
    if not c: return None
    if "," in c and "." in c:
        c = c.replace(".", "").replace(",", ".")   # 1.234,56
    elif "," in c:
        c = c.replace(",", ".")
    try: return float(c)
    except ValueError: return None

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--url"); g.add_argument("--file")
    args = ap.parse_args()
    source = args.url or args.file
    report_date = report_date_from_source(source)
    if args.url:
        req = urllib.request.Request(args.url, headers={"User-Agent": "Mozilla/5.0"})
        raw = urllib.request.urlopen(req, timeout=30).read()
    else:
        raw = open(args.file, "rb").read()

    text, enc = decode(raw)
    delim = max([",", ";", "\t"], key=lambda d: text.count(d))
    rows = list(csv.reader(io.StringIO(text), delimiter=delim))

    header_i, cols = None, {}
    for i, row in enumerate(rows):
        low = [c.strip().lower() for c in row]
        if any("alorien" in c or "alories" in c or "kcal" in c for c in low):
            header_i = i
            for key, pats in COLMAP.items():
                for j, c in enumerate(low):
                    if any(p in c for p in pats):
                        cols[key] = j; break
            break
    if header_i is None:
        print(json.dumps({"error": "header row with Kalorien/Calories not found",
                          "encoding": enc, "first_rows": rows[:3]}, ensure_ascii=False)); sys.exit(1)

    totals = {k: 0.0 for k in cols}
    file_total, n_foods, warnings = None, 0, []
    for row in rows[header_i + 1:]:
        if not row or all(not c.strip() for c in row): continue
        first = row[0].strip().lower()
        kcal = to_num(row[cols["kcal"]]) if cols.get("kcal") is not None and len(row) > cols["kcal"] else None
        if any(first.startswith(m) for m in TOTAL_MARKERS) or any(first.startswith(w) for w in WEEKDAY_MARKERS):
            if file_total is None:
                file_total = {k: to_num(row[j]) for k, j in cols.items() if len(row) > j}
            continue
        if any(m in first for m in MEAL_MARKERS) and kcal is None:
            continue
        if kcal is None: continue
        n_foods += 1
        for k, j in cols.items():
            v = to_num(row[j]) if len(row) > j else None
            if v is not None: totals[k] += v

    t = {k: round(v, 1) for k, v in totals.items()}
    # Prefer the explicit day total to avoid counting nested subtotals twice.
    day = ({k: round(v, 1) for k, v in file_total.items() if v is not None}
           if file_total and file_total.get("kcal") else t)
    check = None
    if all(k in day for k in ("protein", "fat", "carbs")):
        check = round(day["protein"] * 4 + day["fat"] * 9 + day["carbs"] * 4)
        if day.get("kcal") and abs(check - day["kcal"]) > max(0.05 * day["kcal"], 60):
            warnings.append(f"macro-kcal check off by {abs(check - day['kcal']):.0f} — verify carbs column")
    if report_date is None:
        warnings.append("report date unavailable from FoodDiary_YYMMDD filename")
    print(json.dumps({"report_date": report_date,
                      "encoding": enc, "delimiter": delim, "row_count": n_foods,
                      "day_total": day, "totals_summed": t, "file_total_row": file_total,
                      "check_kcal_from_macros": check, "warnings": warnings},
                     ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
