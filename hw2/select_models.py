"""
模型可用性測試
免費模型有 rate limit, 加入重試機制
"""

import time
from openrouter import ask

# 模型名稱 -> 特色
CANDIDATES = {
    "nvidia/nemotron-3-super-120b-a12b:free":
        "參數最大 120B, 測試規模是否等於能力",
    "cohere/north-mini-code:free":
        "程式專用模型",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free": # 沒選中
        "推理型模型, 測試 reasoning 是否有幫助",
    "qwen/qwen3.8-27b:free": # 沒選中
        "中文能力, 27B 中型模型",
    "google/gemma-4-31b-it:free": 
        "Google 開源, instruction-tuned",
    "inclusionai/ling-3.0-flash-sante:free":
        "flash 系列, 測試輕量模型",
    "thinkingmachines/inkling-small:free": # 沒選中
        "1M context 的小模型",
}

# 測試模型
def test_model(model, retries=3, wait=20):
    """
    測試單一模型是否可用
    遇到 429 (rate limit) 時等待後重試
    """
    for attempt in range(retries):
        r = ask(model, "回答一個數字就好: 2+2=?")

        if r["ok"]:
            return True, r

        # 429 代表配額限制, 等一下再試
        if "429" in r["text"]:
            if attempt < retries - 1:
                print(f"    rate limit, 等 {wait}s 後重試 ({attempt+1}/{retries})")
                time.sleep(wait)
                continue

        return False, r

    return False, r


# 測每個模型並記錄哪些是可用的
print("=" * 60)
print("模型可用性測試")
print("=" * 60)

available = []

for model, reason in CANDIDATES.items():
    print(f"\n[測試] {model}")
    print(f"  理由: {reason}")

    ok, r = test_model(model)

    if ok:
        preview = r["text"].strip().replace("\n", " ")[:60]
        print(f"  結果: 可用  ({r['elapsed']:.2f}s, {r['tokens']} tokens)")
        print(f"  回覆: {preview}")
        available.append(model)
    else:
        print(f"  結果: 不可用")
        print(f"  原因: {r['text'][:100]}")

    # 每個模型之間稍微間隔, 降低觸發 rate limit 的機率
    time.sleep(2)

print("\n" + "=" * 60)
print(f"可用模型: {len(available)} / {len(CANDIDATES)}")
for m in available:
    print(f"  {m}")
print("=" * 60)

# 把可用清單存起來, 後面評測直接讀
import json
with open("data/available_models.json", "w") as f:
    json.dump(available, f, indent=2)
print("\n已存入 data/available_models.json")