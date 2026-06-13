import json
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(r"C:\python-src\3rd_PROJECT\third_project\SKN29-3rd-4Team")
ROOT = PROJECT_DIR / "data" / "processed" / "unihan_maping"

HIGH_RISK_JSON = ROOT / "sound_meaning_split_reports" / "sound_meaning_split_high_risk_review.json"

OUT_DIR = ROOT / "sound_meaning_split_reports" / "api_review_filtered"
OUT_TARGET_JSON = OUT_DIR / "sound_meaning_api_targets_filtered.json"
OUT_SAMPLE_JSON = OUT_DIR / "sound_meaning_api_targets_filtered_sample.json"
OUT_SUMMARY_MD = OUT_DIR / "SOUND_MEANING_API_TARGET_FILTER_SUMMARY.md"

PRIORITY_IDS = [
    "OHE-01548",  # 옷의
    "OHE-01552",  # 뜻의
    "OHE-01561",  # 두이
    "OHE-01577",  # 더할익 계열 확인용
    "OHE-01583",  # 사람인 계열 확인용
    "OHE-01592",  # 한일
    "OHE-01740",  # 凈 / 맑을정 / hangul 오류
    "OHE-01295",  # 너여
    "OHE-01302",  # 끌연
    "OHE-01405",  # 쓸용
    "OHE-01420",  # 또우
    "OHE-01476",  # 달월
    "OHE-01688",  # 밭전
    "OHE-01733",  # 못정
    "OHE-01739",  # 뜻정
]

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def should_include(row):
    decision = str(row.get("decision", "")).strip()
    reasons = row.get("risk_reasons", []) or []
    reason_text = " ".join(str(x) for x in reasons)

    # 명백한 한글음 오류 후보는 무조건 포함
    if "known hangul mismatch candidate" in reason_text:
        return True, "HANGUL_MISMATCH_CANDIDATE"

    # 단순 규칙이 실제로 자르려고 한 행은 API 판단 대상으로 포함
    if decision == "SPLIT_BY_TRAILING_HANGUL":
        return True, "RULE_SPLIT_CANDIDATE"

    # 자르면 빈 값이 되는 행은 유지/수동검수 판단 대상으로 포함
    if decision == "TRAILING_HANGUL_BUT_EMPTY_MEANING":
        return True, "EMPTY_AFTER_SPLIT_CANDIDATE"

    # KEEP_AS_IS + already marked only는 너무 넓게 잡힌 false-positive라 제외
    if decision == "KEEP_AS_IS":
        if reasons == ["already marked as needs_review"]:
            return False, "EXCLUDED_KEEP_FALSE_POSITIVE"

    return False, "EXCLUDED_OTHER"

def main():
    if not HIGH_RISK_JSON.exists():
        raise FileNotFoundError(HIGH_RISK_JSON)

    rows = load_json(HIGH_RISK_JSON)

    targets = []
    excluded = []
    group_counts = {}

    for row in rows:
        include, group = should_include(row)
        group_counts[group] = group_counts.get(group, 0) + 1

        item = dict(row)
        item["api_target_group"] = group

        if include:
            targets.append(item)
        else:
            excluded.append(item)

    # 대표 샘플 구성: 우선순위 ID 먼저 넣고, 나머지는 뒤쪽까지 섞이도록 균등 샘플링
    by_id = {row.get("profile_id"): row for row in targets}

    sample = []
    seen = set()

    for pid in PRIORITY_IDS:
        if pid in by_id and pid not in seen:
            sample.append(by_id[pid])
            seen.add(pid)

    remaining = [row for row in targets if row.get("profile_id") not in seen]

    if remaining:
        step = max(1, len(remaining) // 35)
        for idx in range(0, len(remaining), step):
            if len(sample) >= 50:
                break
            sample.append(remaining[idx])

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    save_json(OUT_TARGET_JSON, {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source": str(HIGH_RISK_JSON),
        "total_high_risk_rows": len(rows),
        "target_rows": len(targets),
        "excluded_rows": len(excluded),
        "group_counts": group_counts,
        "items": targets,
    })

    save_json(OUT_SAMPLE_JSON, {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source": str(OUT_TARGET_JSON),
        "sample_rows": len(sample),
        "items": sample,
    })

    with OUT_SUMMARY_MD.open("w", encoding="utf-8") as f:
        f.write("# Sound Meaning API Target Filter Summary\n\n")
        f.write(f"- created_at: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"- total_high_risk_rows: {len(rows)}\n")
        f.write(f"- api_target_rows: {len(targets)}\n")
        f.write(f"- excluded_rows: {len(excluded)}\n")
        f.write(f"- target_json: {OUT_TARGET_JSON}\n")
        f.write(f"- sample_json: {OUT_SAMPLE_JSON}\n")

        f.write("\n## Group Counts\n\n")
        for key, value in sorted(group_counts.items()):
            f.write(f"- {key}: {value}\n")

        f.write("\n## Policy\n\n")
        f.write("- This step does not create CSV files.\n")
        f.write("- This step does not overwrite source JSON.\n")
        f.write("- KEEP_AS_IS rows that were only caught because the reading syllable appears inside the meaning are excluded.\n")
        f.write("- Actual rule-split candidates, empty-after-split candidates, and hangul mismatch candidates are retained for API review.\n")

    print("========== FILTERED API TARGETS CREATED ==========")
    print(f"total_high_risk_rows: {len(rows)}")
    print(f"api_target_rows: {len(targets)}")
    print(f"excluded_rows: {len(excluded)}")
    print("group_counts:")
    for key, value in sorted(group_counts.items()):
        print(f"- {key}: {value}")
    print(f"target_json: {OUT_TARGET_JSON}")
    print(f"sample_json: {OUT_SAMPLE_JSON}")
    print(f"summary_md: {OUT_SUMMARY_MD}")

if __name__ == "__main__":
    main()
