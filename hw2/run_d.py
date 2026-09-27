"""
Task D 獨立評測腳本

Task A-C 已於前次評測完成, 本腳本只跑 Task D
用途: 免費額度有限時分批執行, 或單獨補測進階題
輸出獨立存檔, 不覆蓋原有結果
"""

import json
import time
from datetime import datetime

from openrouter import ask
from scorer import score_task_d

import sys
sys.path.insert(0, "data")
from tasks import TASK_D # type: ignore


SYS_D = ("你是競程教練。這題可能需要組合多種技巧, 或是有陷阱。"
         "請仔細看資料範圍, 用三句話內說明完整解法。")


def run_one(model):
    """對單一模型跑完 Task D 的所有題目"""
    print(f"\n{'='*60}")
    print(f"模型: {model}")
    print(f"{'='*60}")

    results = []

    for item in TASK_D:
        # complexity 型給 code, 其餘給文字題目
        if item["type"] == "complexity":
            prompt = f"以下程式碼有什麼問題?\n\n```cpp\n{item['code']}\n```"
        else:
            prompt = f"請說明這題的完整解法。\n\n{item['problem']}"

        r = ask(model, prompt, system=SYS_D)

        if not r["ok"]:
            print(f"\n[X] {item['id']} ({item['type']})  API 失敗")
            print(f"    {r['text'][:100]}")
            results.append({
                "id": item["id"], "type": item["type"],
                "score": 0, "ok": False,
                "elapsed": r["elapsed"], "tokens": 0,
                "reply": r["text"][:200],
            })
            continue

        score, detail = score_task_d(r["text"], item)

        mark = "O" if score >= 1.0 else ("~" if score > 0 else "X")
        trap = "  [中陷阱]" if detail.get("trapped") else ""

        print(f"\n[{mark}] {item['id']} ({item['type']})  "
              f"{score:.1f}分  {r['elapsed']:.1f}s  {r['tokens']}tok{trap}")
        print(f"    預期: {item['note']}")
        print(f"    key1 命中: {detail['hit1'] or '無'}")
        print(f"    key2 命中: {detail['hit2'] or '無'}")
        print(f"    回覆: {r['text'].strip()[:200]}")

        results.append({
            "id": item["id"], "type": item["type"],
            "score": score, "ok": True,
            "elapsed": r["elapsed"], "tokens": r["tokens"],
            "reply": r["text"].strip()[:400],
            "detail": detail,
        })

        time.sleep(2)     # 題目之間間隔, 降低 rate limit 風險

    total = sum(r["score"] for r in results)
    elapsed = sum(r["elapsed"] for r in results)
    tokens = sum(r["tokens"] for r in results)

    print(f"\n小計: {total:.1f} / {len(TASK_D)}  "
          f"耗時 {elapsed:.1f}s  tokens {tokens}")

    return {
        "model": model,
        "task_d": results,
        "task_d_score": total,
        "task_d_elapsed": elapsed,
        "task_d_tokens": tokens,
        "task_d_pct": total / len(TASK_D) * 100,
    }


if __name__ == "__main__":
    with open("data/available_models.json") as f:
        models = json.load(f)

    print(f"Task D 評測")
    print(f"模型數: {len(models)}")
    print(f"題數: {len(TASK_D)}")
    print(f"預計呼叫: {len(models) * len(TASK_D)} 次")

    all_results = []
    for m in models:
        all_results.append(run_one(m))
        time.sleep(5)     # 模型之間多等一下

    # 存檔
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"results/task_d_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # 排行
    print(f"\n{'='*70}")
    print("Task D 排行")
    print(f"{'='*70}")
    print(f"{'模型':<48} {'得分':>8} {'耗時':>8}")
    print("-" * 70)
    for r in sorted(all_results, key=lambda x: -x["task_d_score"]):
        print(f"{r['model']:<48} "
              f"{r['task_d_score']:>5.1f}/{len(TASK_D)} "
              f"{r['task_d_elapsed']:>7.1f}s")

    # 各題型分析, 看哪種難度來源最有鑑別度
    print(f"\n{'='*70}")
    print("各題型表現")
    print(f"{'='*70}")

    types = {}
    for r in all_results:
        for item in r["task_d"]:
            types.setdefault(item["type"], []).append(item["score"])

    type_name = {
        "combo": "組合技巧",
        "trap": "陷阱題",
        "complexity": "複雜度",
    }

    for t, scores in types.items():
        avg = sum(scores) / len(scores)
        print(f"  {type_name.get(t, t):<10} 平均 {avg:.2f} / 1.0  "
              f"({len(scores)} 次作答)")

    # 陷阱題中招統計
    trapped = [
        (r["model"], item["id"])
        for r in all_results
        for item in r["task_d"]
        if item.get("detail", {}).get("trapped")
    ]

    if trapped:
        print(f"\n中陷阱記錄:")
        for model, qid in trapped:
            print(f"  {qid}  {model}")

    print(f"\n結果已存入 {path}")