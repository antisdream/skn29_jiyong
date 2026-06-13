import argparse
import json
import os
import time
import zipfile
import unicodedata
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(r"C:\python-src\3rd_PROJECT\third_project\SKN29-3rd-4Team")
ROOT = PROJECT_DIR / "data" / "processed" / "unihan_maping"

SOURCE_JSON = ROOT / "hanja_unicode_ohaeng_verified_corrected.json"
HIGH_RISK_JSON = ROOT / "sound_meaning_split_reports" / "sound_meaning_split_high_risk_review.json"
UNIHAN_ZIP = Path(r"C:\python-src\3rd_PROJECT\Data\Unihan.zip")

OUT_DIR = ROOT / "sound_meaning_split_reports" / "api_review"
OUT_RESULTS_JSON = OUT_DIR / "sound_meaning_high_risk_api_review_results.json"
OUT_SUMMARY_MD = OUT_DIR / "SOUND_MEANING_HIGH_RISK_API_REVIEW_SUMMARY.md"
OUT_FAILED_JSON = OUT_DIR / "sound_meaning_high_risk_api_failed_batches.json"

SYSTEM_PROMPT = """
너는 한국 인명용 한자 데이터 정제 검수자다.

목표:
- hangul 필드는 한자의 음이다.
- sound_meaning 필드는 뜻만 남아야 한다.
- 단, 뜻 자체에 hangul 음절이 포함된 경우 절대 자르면 안 된다.

반드시 지킬 규칙:
1. '누각', '원고', '수건', '사건', '호걸', '지경', '성곽', '학교', '화로', '인륜', '관리', '유리', '기린', '사막', '일만', '중매', '근본', '왕비', '역사', '항상', '조정', '수정', '정성', '기세', '보살', '인삼', '형상', '은혜', '산호'처럼 뜻 자체가 완성된 한국어 단어라면 그대로 둔다.
2. '옷의', '뜻의', '두이', '더할익', '우물정', '맑을정', '날일', '한일', '집옥', '쓸용'처럼 뜻 뒤에 음이 붙은 구조라면 음을 제거한다.
3. sound_meaning 전체가 hangul과 같은 경우에는 비워두지 말고 원래 값을 유지한다.
4. hangul이 명백히 틀린 경우에는 final_hangul을 수정한다. 예: 凈, 맑을정이면 final_hangul은 정이다.
5. 확신이 낮거나 뜻인지 음인지 애매하면 NEED_MANUAL로 둔다.
6. 출력은 JSON만 한다. 설명 문장, 마크다운, 코드블록은 쓰지 않는다.

출력 형식:
{
  "items": [
    {
      "profile_id": "...",
      "hanja": "...",
      "final_hangul": "...",
      "final_sound_meaning": "...",
      "action": "KEEP_ORIGINAL|SPLIT_READING|FIX_HANGUL_AND_SPLIT|FIX_HANGUL_KEEP_MEANING|NEED_MANUAL",
      "confidence": 0.0,
      "reason_ko": "짧은 판단 근거"
    }
  ]
}
"""

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def unicode_key_from_char(ch):
    if len(ch) != 1:
        return ""
    return f"U+{ord(ch):04X}"

def load_unihan_khangul(path):
    result = {}
    if not path.exists():
        return result

    with zipfile.ZipFile(path) as zf:
        readings_name = None
        for name in zf.namelist():
            if name.endswith("Unihan_Readings.txt"):
                readings_name = name
                break

        if not readings_name:
            return result

        with zf.open(readings_name) as f:
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

                result[code] = sorted({token.split(":")[0] for token in value.split()})

    return result

def get_unihan_candidates(row, unihan):
    keys = set()

    unicode_value = str(row.get("unicode", "")).strip().upper()
    if unicode_value:
        keys.add(unicode_value)

    hanja = str(row.get("hanja", "")).strip()
    if len(hanja) == 1:
        keys.add(unicode_key_from_char(hanja))
        norm = unicodedata.normalize("NFKC", hanja)
        if len(norm) == 1:
            keys.add(unicode_key_from_char(norm))

    candidates = set()
    for key in keys:
        candidates.update(unihan.get(key, []))

    return sorted(candidates)

def build_review_rows(high_risk_rows, source_rows, unihan):
    source_by_id = {row.get("profile_id"): row for row in source_rows}
    review_rows = []

    for row in high_risk_rows:
        pid = row.get("profile_id")
        source = source_by_id.get(pid, {})

        review_rows.append({
            "profile_id": pid,
            "current_hangul": source.get("hangul", row.get("hangul", "")),
            "hanja": source.get("hanja", row.get("hanja", "")),
            "unicode": source.get("unicode", row.get("unicode", "")),
            "original_sound_meaning": source.get("sound_meaning", row.get("before_sound_meaning", "")),
            "rule_candidate_sound_meaning": row.get("after_sound_meaning", ""),
            "rule_decision": row.get("decision", ""),
            "risk_reasons": row.get("risk_reasons", []),
            "unihan_candidates": get_unihan_candidates(source or row, unihan),
        })

    return review_rows

def chunked(items, size):
    for i in range(0, len(items), size):
        yield i, items[i:i+size]

def call_api(client, model, rows, retry=3, sleep=2):
    user_payload = {
        "rows": rows
    }

    last_error = None

    for attempt in range(1, retry + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": json.dumps(user_payload, ensure_ascii=False)
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)

            if "items" not in parsed or not isinstance(parsed["items"], list):
                raise ValueError("API response does not contain items list")

            return parsed["items"]

        except Exception as e:
            last_error = str(e)
            print(f"[WARN] API batch failed. attempt={attempt}/{retry} error={last_error}")
            time.sleep(sleep * attempt)

    raise RuntimeError(last_error)

def write_summary(path, args, total, reviewed_count, failed_batches, action_counts):
    with path.open("w", encoding="utf-8") as f:
        f.write("# Sound Meaning High Risk API Review Summary\n\n")
        f.write(f"- created_at: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"- model: {args.model}\n")
        f.write(f"- high_risk_rows_input: {total}\n")
        f.write(f"- reviewed_rows: {reviewed_count}\n")
        f.write(f"- failed_batches: {len(failed_batches)}\n")
        f.write(f"- results_json: {OUT_RESULTS_JSON}\n")
        f.write(f"- failed_json: {OUT_FAILED_JSON}\n")

        f.write("\n## Action Counts\n\n")
        for key, value in sorted(action_counts.items()):
            f.write(f"- {key}: {value}\n")

        f.write("\n## Important Note\n\n")
        f.write("- This step does not create CSV files.\n")
        f.write("- This step does not overwrite source JSON.\n")
        f.write("- This step creates API review suggestions only.\n")
        f.write("- Final JSON must be generated only after reviewing these suggestions.\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--env", default=".env")
    args = parser.parse_args()

    load_dotenv(args.env)

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is missing. Check .env file.")

    if not SOURCE_JSON.exists():
        raise FileNotFoundError(SOURCE_JSON)

    if not HIGH_RISK_JSON.exists():
        raise FileNotFoundError(HIGH_RISK_JSON)

    source_rows = load_json(SOURCE_JSON)
    high_risk_rows = load_json(HIGH_RISK_JSON)
    unihan = load_unihan_khangul(UNIHAN_ZIP)

    review_rows = build_review_rows(high_risk_rows, source_rows, unihan)

    if args.limit and args.limit > 0:
        review_rows = review_rows[:args.limit]

    client = OpenAI()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_results = []
    failed_batches = []

    print("========== HIGH RISK API REVIEW START ==========")
    print(f"target_rows: {len(review_rows)}")
    print(f"model: {args.model}")
    print(f"batch_size: {args.batch_size}")

    for start, batch in chunked(review_rows, args.batch_size):
        print(f"Reviewing rows {start + 1} - {start + len(batch)} / {len(review_rows)}")

        try:
            items = call_api(client, args.model, batch)
            all_results.extend(items)
        except Exception as e:
            failed_batches.append({
                "start_index": start,
                "batch_size": len(batch),
                "error": str(e),
                "rows": batch,
            })

    action_counts = {}
    for item in all_results:
        action = item.get("action", "UNKNOWN")
        action_counts[action] = action_counts.get(action, 0) + 1

    save_json(OUT_RESULTS_JSON, {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "model": args.model,
        "limit": args.limit,
        "batch_size": args.batch_size,
        "reviewed_rows": len(all_results),
        "items": all_results,
    })

    save_json(OUT_FAILED_JSON, failed_batches)

    write_summary(
        OUT_SUMMARY_MD,
        args,
        len(review_rows),
        len(all_results),
        failed_batches,
        action_counts,
    )

    print("========== HIGH RISK API REVIEW COMPLETE ==========")
    print(f"reviewed_rows: {len(all_results)}")
    print(f"failed_batches: {len(failed_batches)}")
    print(f"results_json: {OUT_RESULTS_JSON}")
    print(f"summary_md: {OUT_SUMMARY_MD}")

if __name__ == "__main__":
    main()
