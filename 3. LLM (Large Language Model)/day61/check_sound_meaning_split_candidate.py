import json
from pathlib import Path

PROJECT_DIR = Path(r"C:\python-src\3rd_PROJECT\third_project\SKN29-3rd-4Team")
ROOT = PROJECT_DIR / "data" / "processed" / "unihan_maping"

CANDIDATE_JSON = ROOT / "sound_meaning_split_candidate" / "hanja_unicode_ohaeng_verified_corrected_sound_split_candidate.json"
REPORT_JSON = ROOT / "sound_meaning_split_reports" / "sound_meaning_split_report.json"

OUT_REVIEW_JSON = ROOT / "sound_meaning_split_reports" / "sound_meaning_split_high_risk_review.json"
OUT_SUMMARY_MD = ROOT / "sound_meaning_split_reports" / "SOUND_MEANING_SPLIT_REVIEW_SUMMARY.md"

SAMPLE_IDS = [
    "OHE-01548",
    "OHE-01552",
    "OHE-01561",
    "OHE-01577",
    "OHE-01583",
    "OHE-01592",
    "OHE-01740",
    "OHE-00014",
    "OHE-00021",
    "OHE-00050",
    "OHE-00083",
    "OHE-00171",
]

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def is_high_risk(row):
    before = str(row.get("before_sound_meaning", "")).strip()
    after = str(row.get("after_sound_meaning", "")).strip()
    hangul = str(row.get("hangul", "")).strip()
    decision = str(row.get("decision", "")).strip()
    reason = []

    if row.get("profile_id") == "OHE-01740":
        reason.append("known hangul mismatch candidate: hangul=업 but sound_meaning suggests 정")

    if decision == "SPLIT_BY_TRAILING_HANGUL":
        if len(after) <= 1:
            reason.append("after_sound_meaning is too short after split")

        if "," in before or " " in before or "·" in before or "/" in before:
            reason.append("before_sound_meaning contains separator or compound meaning")

        if before.endswith(hangul) and after and after[-1] in {"고", "각", "건", "강", "경", "구", "과", "단", "도", "라", "로", "력", "령", "정"}:
            reason.append("trailing syllable may be part of the Korean meaning word, not only the reading")

    if decision == "TRAILING_HANGUL_BUT_EMPTY_MEANING":
        reason.append("meaning becomes empty if reading is removed")

    if row.get("needs_review"):
        reason.append("already marked as needs_review")

    return reason

def main():
    if not CANDIDATE_JSON.exists():
        raise FileNotFoundError(CANDIDATE_JSON)

    if not REPORT_JSON.exists():
        raise FileNotFoundError(REPORT_JSON)

    candidate = load_json(CANDIDATE_JSON)
    report = load_json(REPORT_JSON)

    by_id_candidate = {row.get("profile_id"): row for row in candidate}
    by_id_report = {row.get("profile_id"): row for row in report}

    print("========== SAMPLE CHECK ==========")
    for pid in SAMPLE_IDS:
        c = by_id_candidate.get(pid)
        r = by_id_report.get(pid)

        if not c or not r:
            print(pid, "NOT_FOUND")
            continue

        print(
            pid,
            "hangul=" + str(c.get("hangul", "")),
            "hanja=" + str(c.get("hanja", "")),
            "before=" + str(r.get("before_sound_meaning", "")),
            "after=" + str(c.get("sound_meaning", "")),
            "decision=" + str(r.get("decision", "")),
            "needs_review=" + str(r.get("needs_review", "")),
        )

    high_risk = []
    for row in report:
        reasons = is_high_risk(row)
        if reasons:
            high_risk.append({
                "profile_id": row.get("profile_id", ""),
                "hangul": row.get("hangul", ""),
                "hanja": row.get("hanja", ""),
                "unicode": row.get("unicode", ""),
                "before_sound_meaning": row.get("before_sound_meaning", ""),
                "after_sound_meaning": row.get("after_sound_meaning", ""),
                "decision": row.get("decision", ""),
                "needs_review": row.get("needs_review", ""),
                "risk_reasons": reasons,
            })

    OUT_REVIEW_JSON.parent.mkdir(parents=True, exist_ok=True)

    with OUT_REVIEW_JSON.open("w", encoding="utf-8") as f:
        json.dump(high_risk, f, ensure_ascii=False, indent=2)

    decision_counts = {}
    for row in report:
        decision = row.get("decision", "")
        decision_counts[decision] = decision_counts.get(decision, 0) + 1

    with OUT_SUMMARY_MD.open("w", encoding="utf-8") as f:
        f.write("# Sound Meaning Split Review Summary\n\n")
        f.write("## Current Decision Counts\n\n")
        for key, value in sorted(decision_counts.items()):
            f.write(f"- {key}: {value}\n")

        f.write("\n## Review Result\n\n")
        f.write(f"- total_rows: {len(report)}\n")
        f.write(f"- high_risk_rows: {len(high_risk)}\n")
        f.write(f"- high_risk_json: {OUT_REVIEW_JSON}\n")

        f.write("\n## Important Note\n\n")
        f.write("- This step does not create CSV files.\n")
        f.write("- This step does not overwrite the source JSON.\n")
        f.write("- The current candidate JSON must not be used as final data until high-risk rows are reviewed.\n")

    print("========== HIGH RISK REVIEW CREATED ==========")
    print(f"total_rows: {len(report)}")
    print(f"high_risk_rows: {len(high_risk)}")
    print(f"review_json: {OUT_REVIEW_JSON}")
    print(f"summary_md: {OUT_SUMMARY_MD}")

if __name__ == "__main__":
    main()
