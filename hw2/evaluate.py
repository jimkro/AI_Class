"""
主評測腳本
對每個模型跑完四種任務, 記錄正確率、耗時與 token 用量
"""

import json
import time
from datetime import datetime

from openrouter import ask
from scorer import score_task_a, score_task_b, score_task_c, score_task_d

import sys
sys.path.insert(0, "data")
from tasks import TASK_A, TASK_B, TASK_C, TASK_D # type: ignore


# ──────────────────────────────────────────────────────────
# System prompt
# 限制回答長度, 避免模型長篇大論影響 token 比較的公平性
# ──────────────────────────────────────────────────────────

SYS_A = "你是競程教練。只回答演算法類型名稱, 不要解釋, 不超過 10 個字。"
SYS_B = "你是 code reviewer。用一句話指出程式碼的 bug, 不要改寫程式碼。"
SYS_C = "你是競程教練。用三句話內說明解法, 並明確寫出時間複雜度。"
SYS_D = ("你是競程教練。這題可能需要組合多種技巧, 或是有陷阱。"
         "請仔細看資料範圍, 用三句話內說明完整解法。")

def run_task_a(model):
    """任務 A: 題目標籤分類"""
    results = []
    for item in TASK_A:
        prompt = f"這題應該用什麼演算法?\n\n{item['desc']}"
        r = ask(model, prompt, system=SYS_A)

        if not r["ok"]:
            results.append({
                "id": item["id"], "score": 0, "ok": False,
                "elapsed": r["elapsed"], "tokens": 0,
                "reply": r["text"][:100],
            })
            continue

        score, hit = score_task_a(r["text"], item)
        results.append({
            "id": item["id"], "score": score, "ok": True,
            "elapsed": r["elapsed"], "tokens": r["tokens"],
            "reply": r["text"].strip()[:150],
            "hit": hit,
        })
        time.sleep(1)     # 避免觸發 rate limit
    return results


def run_task_b(model):
    """任務 B: 程式碼除錯"""
    results = []
    for item in TASK_B:
        prompt = (f"以下程式碼有 bug, 請指出問題。\n"
                  f"提示: {item['hint']}\n\n```cpp\n{item['code']}\n```")
        r = ask(model, prompt, system=SYS_B)

        if not r["ok"]:
            results.append({
                "id": item["id"], "score": 0, "ok": False,
                "elapsed": r["elapsed"], "tokens": 0,
                "reply": r["text"][:100],
            })
            continue

        score, hit = score_task_b(r["text"], item)
        results.append({
            "id": item["id"], "score": score, "ok": True,
            "elapsed": r["elapsed"], "tokens": r["tokens"],
            "reply": r["text"].strip()[:150],
            "hit": hit,
        })
        time.sleep(1)
    return results


def run_task_c(model):
    """任務 C: 解題思路"""
    results = []
    for item in TASK_C:
        prompt = f"請說明這題的解法和時間複雜度。\n\n{item['problem']}"
        r = ask(model, prompt, system=SYS_C)

        if not r["ok"]:
            results.append({
                "id": item["id"], "score": 0, "ok": False,
                "elapsed": r["elapsed"], "tokens": 0,
                "reply": r["text"][:100],
            })
            continue

        score, detail = score_task_c(r["text"], item)
        results.append({
            "id": item["id"], "score": score, "ok": True,
            "elapsed": r["elapsed"], "tokens": r["tokens"],
            "reply": r["text"].strip()[:200],
            "detail": detail,
        })
        time.sleep(1)
    return results

def run_task_d(model):
    """
    任務 D: 進階題
    依題型組裝不同的 prompt
    """
    results = []
    for item in TASK_D:
        # complexity 型的題目是給 code, 其餘是給文字題目
        if item["type"] == "complexity":
            prompt = (f"以下程式碼有什麼問題?\n\n```cpp\n{item['code']}\n```")
        else:
            prompt = f"請說明這題的完整解法。\n\n{item['problem']}"

        r = ask(model, prompt, system=SYS_D)

        if not r["ok"]:
            results.append({
                "id": item["id"], "score": 0, "ok": False,
                "elapsed": r["elapsed"], "tokens": 0,
                "reply": r["text"][:100],
            })
            continue

        score, detail = score_task_d(r["text"], item)
        results.append({
            "id": item["id"], "score": score, "ok": True,
            "elapsed": r["elapsed"], "tokens": r["tokens"],
            "reply": r["text"].strip()[:250],
            "detail": detail,
            "type": item["type"],
        })
        time.sleep(1)
    return results

def evaluate_model(model):
    """對單一模型執行完整評測"""
    print(f"\n{'='*60}")
    print(f"評測模型: {model}")
    print(f"{'='*60}")

    out = {"model": model}

    for name, runner, total in [
        ("task_a", run_task_a, len(TASK_A)),
        ("task_b", run_task_b, len(TASK_B)),
        ("task_c", run_task_c, len(TASK_C)),
        ("task_d", run_task_d, len(TASK_D)),          # 新增
    ]:
        print(f"\n--- {name.upper()} ---")
        res = runner(model)
        out[name] = res

        score = sum(r["score"] for r in res)
        elapsed = sum(r["elapsed"] for r in res)
        tokens = sum(r["tokens"] for r in res)

        for r in res:
            mark = "O" if r["score"] > 0 else "X"
            # 陷阱題若中招要標示出來
            extra = ""
            if r.get("detail", {}).get("trapped"):
                extra = "  [中陷阱]"
            print(f"  [{mark}] {r['id']}  {r['score']:.1f}分  "
                  f"{r['elapsed']:.1f}s  {r['tokens']}tok{extra}")
            print(f"      {r['reply'][:80]}")

        print(f"  小計: {score:.1f} / {total}  "
              f"耗時 {elapsed:.1f}s  tokens {tokens}")

        out[f"{name}_score"] = score
        out[f"{name}_elapsed"] = elapsed
        out[f"{name}_tokens"] = tokens

    # 總分, 四個任務各佔 1/4 權重
    out["total_score"] = (
        out["task_a_score"] / len(TASK_A)
        + out["task_b_score"] / len(TASK_B)
        + out["task_c_score"] / len(TASK_C)
        + out["task_d_score"] / len(TASK_D)
    ) / 4 * 100

    out["total_elapsed"] = sum(
        out[f"task_{x}_elapsed"] for x in "abcd")
    out["total_tokens"] = sum(
        out[f"task_{x}_tokens"] for x in "abcd")

    print(f"\n總分: {out['total_score']:.1f} / 100")
    print(f"總耗時: {out['total_elapsed']:.1f}s")
    print(f"總 tokens: {out['total_tokens']}")

    return out


if __name__ == "__main__":
    with open("data/available_models.json") as f:
        models = json.load(f)

    print(f"共 {len(models)} 個模型待評測")
    print(f"每個模型 {len(TASK_A)+len(TASK_B)+len(TASK_C)+len(TASK_D)} 題")

    all_results = []
    for m in models:
        all_results.append(evaluate_model(m))
        time.sleep(3)   # 模型之間間隔, 降低 rate limit 風險

    # 存檔, 檔名帶時間戳記避免覆蓋
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"results/eval_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # 排行榜
    print(f"\n{'='*60}")
    print("總排行")
    print(f"{'='*60}")
    print(f"{'模型':<50} {'總分':>6} {'耗時':>8} {'tokens':>8}")
    print("-" * 76)
    for r in sorted(all_results, key=lambda x: -x["total_score"]):
        print(f"{r['model']:<50} {r['total_score']:>6.1f} "
              f"{r['total_elapsed']:>7.1f}s {r['total_tokens']:>8}")

    print(f"\n結果已存入 {path}")