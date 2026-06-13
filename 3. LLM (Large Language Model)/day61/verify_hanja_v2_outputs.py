import csv
import json
import sys
import zipfile
import unicodedata
from collections import Counter
from pathlib import Path

PROJECT_DIR = Path(r"C:\python-src\3rd_PROJECT\third_project\SKN29-3rd-4Team")
ROOT = PROJECT_DIR / "data" / "processed" / "unihan_maping"
REPORT_DIR = ROOT / "hanja_rebuild_v2_reports"
SPLIT_DIR = ROOT / "profile_split_v2"
UNIHAN_ZIP = Path(r"C:\python-src\3rd_PROJECT\Data\Unihan.zip")

CORRECTED_JSON = ROOT / "hanja_unicode_ohaeng_verified_corrected.json"
CORRECTED_CSV = ROOT / "hanja_unicode_ohaeng_verified_corrected.csv"
VALIDATION_REPORT = REPORT_DIR / "v2_validation_report.csv"
REVIEW_NEEDED = REPORT_DIR / "v2_review_needed.csv"
SAFE_FIXES = REPORT_DIR / "v2_safe_fixes.csv"
SUMMARY_OUT = REPORT_DIR / "FINAL_CROSSCHECK_SUMMARY.txt"
ISSUES_OUT = REPORT_DIR / "final_crosscheck_issues.csv"

REQUIRED_FIELDS = [
    "profile_id",
    "hangul",
    "hanja",
    "unicode",
    "sound_meaning",
    "strokes",
    "sound_ohaeng",
    "resource_ohaeng",
]

EXPECTED_SPLIT = {
    "profile_ids.csv": "profile_id",
    "profile_hangul.csv": "hangul",
    "profile_hanja.csv": "hanja",
    "profile_unicode.csv": "unicode",
    "profile_sound_meaning.csv": "sound_meaning",
    "profile_strokes.csv": "strokes",
    "profile_sound_ohaeng.csv": "sound_ohaeng",
    "profile_resource_ohaeng.csv": "resource_ohaeng",
}

issues = []
warnings = []

def add_issue(kind, profile_id="", message="", value="", expected=""):
    issues.append({
        "kind": kind,
        "profile_id": profile_id,
        "message": message,
        "value": value,
        "expected": expected,
    })

def add_warning(kind, profile_id="", message="", value="", expected=""):
    warnings.append({
        "kind": kind,
        "profile_id": profile_id,
        "message": message,
        "value": value,
        "expected": expected,
    })

def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def load_unihan_khangul(path):
    result = {}
    with zipfile.ZipFile(path) as zf:
        name = None
        for n in zf.namelist():
            if n.endswith("Unihan_Readings.txt"):
                name = n
                break
        if not name:
            raise RuntimeError("Unihan_Readings.txt not found in Unihan.zip")

        with zf.open(name) as f:
            for raw in f:
                line = raw.decode("utf-8", errors="replace").strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) < 3:
                    continue
                code, field, value = parts[0].upper(), parts[1], parts[2]
                if field != "kHangul":
                    continue

                readings = set()
                for token in value.split():
                    readings.add(token.split(":")[0])

                result[code] = readings
    return result

def unicode_key_from_char(ch):
    if len(ch) != 1:
        return ""
    return f"U+{ord(ch):04X}"

def get_unihan_candidates(row, unihan):
    keys = set()

    u = str(row.get("unicode", "")).strip().upper()
    if u:
        keys.add(u)

    h = str(row.get("hanja", "")).strip()
    if len(h) == 1:
        keys.add(unicode_key_from_char(h))
        norm = unicodedata.normalize("NFKC", h)
        if len(norm) == 1:
            keys.add(unicode_key_from_char(norm))

    candidates = set()
    for key in keys:
        candidates.update(unihan.get(key, set()))
    return candidates

def main():
    required_paths = [
        CORRECTED_JSON,
        CORRECTED_CSV,
        VALIDATION_REPORT,
        REVIEW_NEEDED,
        SAFE_FIXES,
        UNIHAN_ZIP,
    ]

    for path in required_paths:
        if not path.exists():
            add_issue("MISSING_FILE", "", f"Required file not found: {path}", str(path), "")

    if issues:
        write_outputs([], Counter())
        return 1

    with CORRECTED_JSON.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        if "records" in data:
            rows = data["records"]
        elif "data" in data:
            rows = data["data"]
        else:
            rows = list(data.values())
    else:
        rows = data

    if len(rows) != 2420:
        add_issue("ROW_COUNT_MISMATCH", "", "Corrected JSON row count is not 2420.", str(len(rows)), "2420")

    ids = []
    for row in rows:
        pid = str(row.get("profile_id", "")).strip()
        ids.append(pid)

        for field in REQUIRED_FIELDS:
            if field not in row or str(row.get(field, "")).strip() == "":
                add_issue("MISSING_REQUIRED_FIELD", pid, f"Missing or empty field: {field}", str(row.get(field, "")), field)

        h = str(row.get("hanja", "")).strip()
        u = str(row.get("unicode", "")).strip().upper()
        if len(h) == 1 and u.startswith("U+"):
            actual_u = unicode_key_from_char(h)
            if actual_u != u:
                norm = unicodedata.normalize("NFKC", h)
                norm_u = unicode_key_from_char(norm) if len(norm) == 1 else ""
                if norm_u != u:
                    add_issue("UNICODE_HANJA_MISMATCH", pid, "Unicode does not match hanja or normalized hanja.", f"{h}/{u}", f"{actual_u} or {norm_u}")

    duplicated = [pid for pid, c in Counter(ids).items() if c > 1]
    for pid in duplicated:
        add_issue("DUPLICATE_PROFILE_ID", pid, "Duplicate profile_id found.", pid, "unique profile_id")

    row_by_id = {str(row.get("profile_id", "")).strip(): row for row in rows}

    unihan = load_unihan_khangul(UNIHAN_ZIP)
    no_unihan_count = 0
    unihan_mismatch_count = 0

    for row in rows:
        pid = str(row.get("profile_id", "")).strip()
        current = str(row.get("hangul", "")).strip()
        candidates = get_unihan_candidates(row, unihan)

        if not candidates:
            no_unihan_count += 1
            add_warning("NO_UNIHAN_EVIDENCE", pid, "No Unihan kHangul evidence found.", current, "")
            continue

        if current not in candidates:
            unihan_mismatch_count += 1
            add_issue("UNIHAN_MISMATCH", pid, "Final hangul is not included in Unihan kHangul candidates.", current, ";".join(sorted(candidates)))

    for filename, field in EXPECTED_SPLIT.items():
        path = SPLIT_DIR / filename
        if not path.exists():
            add_issue("MISSING_SPLIT_FILE", "", f"Split file not found: {filename}", str(path), "")
            continue

        split_rows = read_csv(path)
        if len(split_rows) != len(rows):
            add_issue("SPLIT_ROW_COUNT_MISMATCH", "", f"{filename} row count mismatch.", str(len(split_rows)), str(len(rows)))
            continue

        for idx, split_row in enumerate(split_rows):
            expected_id = ids[idx]
            split_id = str(split_row.get("profile_id", "")).strip()
            if split_id != expected_id:
                add_issue("SPLIT_ID_ORDER_MISMATCH", split_id, f"{filename} profile_id order mismatch.", split_id, expected_id)
                break

            if filename == "profile_ids.csv":
                continue

            expected_value = str(row_by_id[expected_id].get(field, "")).strip()
            actual_value = str(split_row.get(field, "")).strip()
            if actual_value != expected_value:
                add_issue("SPLIT_VALUE_MISMATCH", expected_id, f"{filename} value mismatch for field {field}.", actual_value, expected_value)
                break

    validation_rows = read_csv(VALIDATION_REPORT)
    decision_counts = Counter(row.get("decision", "") for row in validation_rows)

    if len(validation_rows) != len(rows):
        add_issue("VALIDATION_REPORT_COUNT_MISMATCH", "", "Validation report row count mismatch.", str(len(validation_rows)), str(len(rows)))

    review_rows = read_csv(REVIEW_NEEDED)
    if review_rows:
        add_warning("REVIEW_NEEDED_REMAINS", "", "Some rows still require manual/API review.", str(len(review_rows)), "0")

    write_outputs(rows, decision_counts)

    hard_issue_count = len(issues)
    print("========== FINAL HANJA V2 CROSSCHECK ==========")
    print(f"Corrected JSON rows: {len(rows)}")
    print(f"Decision counts: {dict(decision_counts)}")
    print(f"Hard issues: {hard_issue_count}")
    print(f"Warnings: {len(warnings)}")
    print(f"Unihan mismatches: {unihan_mismatch_count}")
    print(f"No Unihan evidence warnings: {no_unihan_count}")
    print(f"Summary: {SUMMARY_OUT}")
    print(f"Issues: {ISSUES_OUT}")

    if hard_issue_count == 0:
        print("FINAL STATUS: PASS")
        return 0

    print("FINAL STATUS: FAIL")
    return 1

def write_outputs(rows, decision_counts):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with ISSUES_OUT.open("w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["level", "kind", "profile_id", "message", "value", "expected"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in issues:
            writer.writerow({"level": "ERROR", **row})
        for row in warnings:
            writer.writerow({"level": "WARNING", **row})

    with SUMMARY_OUT.open("w", encoding="utf-8") as f:
        f.write("# Final Hanja V2 Crosscheck Summary\n\n")
        f.write(f"- Corrected JSON rows: {len(rows)}\n")
        f.write(f"- Decision counts: {dict(decision_counts)}\n")
        f.write(f"- Hard issues: {len(issues)}\n")
        f.write(f"- Warnings: {len(warnings)}\n")
        f.write(f"- Issues CSV: {ISSUES_OUT}\n")
        f.write("\n## Status\n\n")
        f.write("PASS\n" if not issues else "FAIL\n")

if __name__ == "__main__":
    sys.exit(main())
