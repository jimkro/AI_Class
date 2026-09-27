"""測試 API 是否正常運作, 並列出可用的免費模型"""

from openrouter import ask, list_free_models

print("=== 測試 1: 基本呼叫 ===")
r = ask("mistralai/mistral-7b-instruct", "用一句話說明什麼是二分搜尋")
print(f"成功: {r['ok']}")
print(f"回覆: {r['text'][:200]}")
print(f"耗時: {r['elapsed']:.2f}s, tokens: {r['tokens']}\n")

print("=== 測試 2: 列出免費模型 ===")
free = list_free_models()
print(f"共有 {len(free)} 個免費模型\n")

for m in free[:20]:
    print(f"  {m['id']}")
    print(f"    context: {m['context_length']:,}")