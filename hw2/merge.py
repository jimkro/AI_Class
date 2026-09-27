"""
合併 Task A-C 與 Task D 的評測結果
兩次評測分別執行, 此腳本合併後計算最終總分
"""

import json
import glob

# 找最新的兩份結果檔
eval_files = sorted(glob.glob("results/eval_*.json"))
taskd_files = sorted(glob.glob("results/task_d_*.json"))

if not eval_files or not taskd_files:
    raise FileNotFoundError("找不到 eval_*.json 或 task_d_*.json")

print(f"讀取 Task A-C: {eval_files[-1]}")
print(f"讀取 Task D  : {taskd_files[-1]}\n")

with open(eval_files[-1]) as f:
    abc = json.load(f)
with open(taskd_files[-1]) as f:
    d = json.load(f)

# 以模型名稱為 key 建立索引, 方便對應
d_map = {r["model"]: r for r in d}

merged = []
for r in abc:
    model = r["model"]
    if model not in d_map:
        print(f"警告: {model} 沒有 Task D 資料, 跳過")
        continue

    dr = d_map[model]

    # 四個任務各佔 1/4 權重
    total = (
        r["task_a_score"] / 5
        + r["task_b_score"] / 5
        + r["task_c_score"] / 3
        + dr["task_d_score"] / 5
    ) / 4 * 100

    merged.append({
        "model": model,
        "a": r["task_a_score"],
        "b": r["task_b_score"],
        "c": r["task_c_score"],
        "d": dr["task_d_score"],
        "total": total,
        "elapsed": r["total_elapsed"] + dr["task_d_elapsed"],
        "tokens": r["total_tokens"] + dr["task_d_tokens"],
    })

# 輸出總表
print(f"{'='*82}")
print("最終總表")
print(f"{'='*82}")
print(f"{'模型':<44} {'A':>5} {'B':>5} {'C':>5} {'D':>5} {'總分':>7} {'耗時':>8}")
print("-" * 82)

for r in sorted(merged, key=lambda x: -x["total"]):
    print(f"{r['model']:<44} "
          f"{r['a']:>4.0f}/5 {r['b']:>4.0f}/5 "
          f"{r['c']:>4.1f}/3 {r['d']:>4.1f}/5 "
          f"{r['total']:>6.1f} {r['elapsed']:>7.1f}s")

# 鑑別度分析: 標準差越大代表越能區分模型
print(f"\n{'='*82}")
print("各任務鑑別度 (分數全距, 越大代表越能區分模型)")
print(f"{'='*82}")

for key, name, total in [("a", "Task A 分類", 5),
                          ("b", "Task B 除錯", 5),
                          ("c", "Task C 解題", 3),
                          ("d", "Task D 進階", 5)]:
    scores = [r[key] for r in merged]
    rng = max(scores) - min(scores)
    avg = sum(scores) / len(scores)
    print(f"  {name}  平均 {avg:.2f}/{total}  "
          f"最高 {max(scores):.1f}  最低 {min(scores):.1f}  "
          f"全距 {rng:.1f}")

with open("results/final.json", "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"\n已存入 results/final.json")