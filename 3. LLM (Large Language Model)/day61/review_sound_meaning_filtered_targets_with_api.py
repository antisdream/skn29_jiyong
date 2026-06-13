import argparse
import json
import os
import time
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

PROJECT_DIR = Path(r"C:\python-src\3rd_PROJECT\third_project\SKN29-3rd-4Team")
ROOT = PROJECT_DIR / "data" / "processed" / "unihan_maping"

DEFAULT_TARGET_JSON = ROOT / "sound_meaning_split_reports" / "api_review_filtered" / "sound_meaning_api_targets_filtered_sample.json"

OUT_DIR = ROOT / "sound_meaning_split_reports" / "api_review_filtered"
OUT_RESULTS_JSON = OUT_DIR / "sound_meaning_filtered_api_review_results.json"
OUT_SUMMARY_MD = OUT_DIR / "SOUND_MEANING_FILTERED_API_REVIEW_SUMMARY.md"
OUT_FAILED_JSON = OUT_DIR / "sound_meaning_filtered_api_failed_batches.json"

SYSTEM_PROMPT = """
너는 한국 인명용 한자 데이터 정제 검수자다.

목표:
- hangul 필드는 한자의 음이다.
- sound_meaning 필드는 뜻만 남아야 한다.
- final_sound_meaning은 반드시 뜻만 적는다.
- 뜻 자체에 음절이 포함된 완성된 한국어 단어는 절대 자르면 안 된다.

판단 기준:
1. 완성된 뜻 단어는 KEEP_ORIGINAL:
   누각, 원고, 수건, 사건, 호걸, 지경, 성곽, 학교, 화로, 인륜, 관리, 유리, 기린, 사막, 일만, 중매, 근본, 왕비, 역사, 항상, 조정, 수정, 정성, 기세, 보살, 인삼, 형상, 은혜, 산호, 강철, 경사, 계수나무 등.

2. 뜻 뒤에 한자음이 붙은 구조는 SPLIT_READING:
   옷의 -> 옷
   뜻의 -> 뜻
   두이 -> 두
   귀이 -> 귀
   한일 -> 한
   날일 -> 날
   우물정 -> 우물
   맑을정 -> 맑을
   쓸용 -> 쓸
   달월 -> 달
   집옥 -> 집
   밭전 -> 밭
   못정 -> 못

3. sound_meaning 전체가 hangul과 같으면 비우지 말고 KEEP_ORIGINAL:
   강/강, 복/복, 법/법, 학/학 같은 경우.

4. hangul이 명백히 틀리면 수정한다:
   예: hanja=凈, original_sound_meaning=맑을정, current_hangul=업이면 final_hangul=정, final_sound_meaning=맑을.

5. 확신이 낮으면 NEED_MANUAL.

출력은 JSON만 한다:
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

def chunked(items, size):
    for i in range(0, len(items), size):
        yield i, items[i:i+size]

def to_api_rows(target_items):
    rows = []

    for row in target_items:
        rows.append({
            "profile_id": row.get("profile_id", ""),
            "current_hangul": row.get("hangul", ""),
            "hanja": row.get("hanja", ""),
            "unicode": row.get("unicode", ""),
            "original_sound_meaning": row.get("before_sound_meaning", ""),
            "rule_candidate_sound_meaning": row.get("after_sound_meaning", ""),
            "rule_decision": row.get("decision", ""),
            "api_target_group": row.get("api_target_group", ""),
            "risk_reasons": row.get("risk_reasons", []),
        })

    return rows

def call_api(client, model, rows, retry=3, sleep=2):
    payload = {"rows": rows}
    last_error = None

    for attempt in range(1, retry + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )

            parsed = json.loads(response.choices[0].message.content)

            if "items" not in parsed or not isinstance(parsed["items"], list):
                raise ValueError("API response does not contain items list")

            return parsed["items"]

        except Exception as e:
            last_error = str(e)
            print(f"[WARN] API batch failed attempt={attempt}/{retry}: {last_error}")
            time.sleep(sleep * attempt)

    raise RuntimeError(last_error)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--target-file", default=str(DEFAULT_TARGET_JSON))
    parser.add_argument("--env", default=".env")
    args = parser.parse_args()

    load_dotenv(args.env)

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is missing. Check .env file.")

    target_path = Path(args.target_file)

    if not target_path.exists():
        raise FileNotFoundError(target_path)

    target_data = load_json(target_path)
    target_items = target_data.get("items", target_data if isinstance(target_data, list) else [])

    api_rows = to_api_rows(target_items)

    client = OpenAI()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_results = []
    failed_batches = []

    print("========== FILTERED API REVIEW START ==========")
    print(f"target_file: {target_path}")
    print(f"target_rows: {len(api_rows)}")
    print(f"model: {args.model}")
    print(f"batch_size: {args.batch_size}")

    for start, batch in chunked(api_rows, args.batch_size):
        print(f"Reviewing rows {start + 1} - {start + len(batch)} / {len(api_rows)}")

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
        "target_file": str(target_path),
        "reviewed_rows": len(all_results),
        "failed_batches": len(failed_batches),
        "action_counts": action_counts,
        "items": all_results,
    })

    save_json(OUT_FAILED_JSON, failed_batches)

    with OUT_SUMMARY_MD.open("w", encoding="utf-8") as f:
        f.write("# Sound Meaning Filtered API Review Summary\n\n")
        f.write(f"- created_at: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"- model: {args.model}\n")
        f.write(f"- target_file: {target_path}\n")
        f.write(f"- target_rows: {len(api_rows)}\n")
        f.write(f"- reviewed_rows: {len(all_results)}\n")
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

    print("========== FILTERED API REVIEW COMPLETE ==========")
    print(f"reviewed_rows: {len(all_results)}")
    print(f"failed_batches: {len(failed_batches)}")
    print(f"action_counts: {action_counts}")
    print(f"results_json: {OUT_RESULTS_JSON}")
    print(f"summary_md: {OUT_SUMMARY_MD}")

if __name__ == "__main__":
    main()
