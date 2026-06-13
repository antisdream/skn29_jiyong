import json
from pathlib import Path
from copy import deepcopy
from datetime import datetime

PROJECT_DIR = Path(r"C:\python-src\3rd_PROJECT\third_project\SKN29-3rd-4Team")
ROOT = PROJECT_DIR / "data" / "processed" / "unihan_maping"

SRC_JSON = ROOT / "hanja_unicode_ohaeng_verified_corrected.json"

OUT_DIR = ROOT / "sound_meaning_split_candidate"
REPORT_DIR = ROOT / "sound_meaning_split_reports"

OUT_JSON = OUT_DIR / "hanja_unicode_ohaeng_verified_corrected_sound_split_candidate.json"
REPORT_JSON = REPORT_DIR / "sound_meaning_split_report.json"
SUMMARY_MD = REPORT_DIR / "SOUND_MEANING_SPLIT_SUMMARY.md"

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

def load_rows(path):
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data, "list"

    if isinstance(data, dict) and "records" in data:
        return data["records"], "records"

    if isinstance(data, dict) and "data" in data:
        return data["data"], "data"

    raise RuntimeError("Unsupported JSON structure")

def save_rows(path, rows, structure):
    path.parent.mkdir(parents=True, exist_ok=True)

    if structure == "list":
        data = rows
    elif structure == "records":
        data = {"records": rows}
    elif structure == "data":
        data = {"data": rows}
    else:
        raise RuntimeError("Unsupported JSON structure")

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def split_meaning(sound_meaning, hangul):
    sm = str(sound_meaning or "").strip()
    hg = str(hangul or "").strip()

    if not sm or not hg:
        return sm, "EMPTY_OR_MISSING"

    # 예: 옷의 -> 옷, 더할익 -> 더할, 우물정 -> 우물
    if sm.endswith(hg):
        meaning = sm[:-len(hg)].strip()
        if meaning:
            return meaning, "SPLIT_BY_TRAILING_HANGUL"

        return sm, "TRAILING_HANGUL_BUT_EMPTY_MEANING"

    # 예: 이미 뜻만 들어있는 경우
    return sm, "KEEP_AS_IS"

def main():
    if not SRC_JSON.exists():
        raise FileNotFoundError(f"Source JSON not found: {SRC_JSON}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    rows, structure = load_rows(SRC_JSON)
    new_rows = deepcopy(rows)

    report = []
    changed = 0
    kept = 0
    needs_review = 0
    missing_required = 0

    for row in new_rows:
        pid = str(row.get("profile_id", "")).strip()
        hangul = str(row.get("hangul", "")).strip()
        before = str(row.get("sound_meaning", "")).strip()

        missing = [field for field in REQUIRED_FIELDS if field not in row or str(row.get(field, "")).strip() == ""]
        if missing:
            missing_required += 1

        after, decision = split_meaning(before, hangul)

        # hangul이 sound_meaning 내부에 남아 있으면 검수 대상으로 남김
        # 단, 끝 음 제거 후에도 의미 단어 자체에 같은 글자가 들어가는 경우가 있을 수 있으므로 자동수정은 하지 않고 리포트만 남김
        review_reason = ""
        if decision == "SPLIT_BY_TRAILING_HANGUL":
            row["sound_meaning"] = after
            changed += 1
        elif decision == "KEEP_AS_IS":
            kept += 1
            if hangul and hangul in before:
                needs_review += 1
                review_reason = "hangul appears inside sound_meaning but not as a clean trailing suffix"
        else:
            needs_review += 1
            review_reason = decision

        if missing:
            review_reason = (review_reason + "; " if review_reason else "") + "missing required fields: " + ",".join(missing)

        report.append({
            "profile_id": pid,
            "hangul": hangul,
            "hanja": row.get("hanja", ""),
            "unicode": row.get("unicode", ""),
            "before_sound_meaning": before,
            "after_sound_meaning": row.get("sound_meaning", ""),
            "decision": decision,
            "needs_review": bool(review_reason),
            "review_reason": review_reason,
        })

    save_rows(OUT_JSON, new_rows, structure)

    with REPORT_JSON.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    summary = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source_json": str(SRC_JSON),
        "candidate_json": str(OUT_JSON),
        "report_json": str(REPORT_JSON),
        "source_rows": len(rows),
        "candidate_rows": len(new_rows),
        "split_by_trailing_hangul": changed,
        "kept_as_is": kept,
        "needs_review": needs_review,
        "missing_required_field_rows": missing_required,
    }

    with SUMMARY_MD.open("w", encoding="utf-8") as f:
        f.write("# Sound Meaning Split Summary\n\n")
        for key, value in summary.items():
            f.write(f"- {key}: {value}\n")
        f.write("\n## Policy\n\n")
        f.write("- This step does not create final CSV files.\n")
        f.write("- This step does not overwrite the source JSON.\n")
        f.write("- Only a candidate JSON and JSON review report are generated.\n")
        f.write("- A value is changed only when sound_meaning ends with the same reading as hangul.\n")

    print("========== SOUND_MEANING SPLIT CANDIDATE COMPLETE ==========")
    for key, value in summary.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
