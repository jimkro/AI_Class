"""
評分模組
三種任務各有不同的計分邏輯, 但都基於關鍵字比對, 避免主觀判斷
"""

import re

def normalize(text):
    """
    正規化文字以利比對
    轉小寫並去除多餘空白, 讓 "Two Pointers" 和 "two pointers" 視為相同
    """
    return re.sub(r"\s+", " ", text.lower().strip())


def score_task_a(reply, item):
    """
    任務 A: 題目標籤分類
    只要回覆中出現任一可接受的標籤就算對
    回傳 (得分 0 或 1, 命中的關鍵字)
    """
    text = normalize(reply)
    for kw in item["accept"]:
        if normalize(kw) in text:
            return 1, kw
    return 0, None


def score_task_b(reply, item):
    """
    任務 B: 程式碼除錯
    同樣用關鍵字比對, 模型只要指出 bug 的本質即可
    """
    text = normalize(reply)
    for kw in item["accept"]:
        if normalize(kw) in text:
            return 1, kw
    return 0, None


def score_task_c(reply, item):
    """
    任務 C: 解題思路
    演算法 0.7 分, 複雜度 0.3 分
    複雜度比對需容忍多種寫法: O(nlogn), O(n log n), O(n·log n), O(NlogN)
    """
    text = normalize(reply)

    hit_algo = [kw for kw in item["key"] if normalize(kw) in text]
    algo_score = 0.7 if hit_algo else 0.0

    # 把所有非字母數字的符號去掉再比對, 讓各種寫法都能命中
    def strip_all(s):
        return re.sub(r"[^a-z0-9]", "", s.lower())

    target = strip_all(item["complexity"])
    has_complexity = target in strip_all(text)

    comp_score = 0.3 if has_complexity else 0.0

    return algo_score + comp_score, {
        "algo_hit": hit_algo,
        "has_complexity": has_complexity,
    }

def score_task_d(reply, item):
    """
    任務 D: 進階題
    需同時命中兩組關鍵字才算完全答對

    計分:
      兩組都中      1.0 分   完整解法
      只中一組      0.5 分   方向對但不完整
      都沒中        0.0 分
      中陷阱答案    0.0 分   並標記 trapped

    回傳 (得分, 詳細資訊)
    """
    text = normalize(reply)

    # 先檢查有沒有掉進陷阱
    # 陷阱題若模型給出錯誤方向, 即使後面補對也不給分
    trapped = False
    if "trap_answer" in item:
        for kw in item["trap_answer"]:
            if normalize(kw) in text:
                trapped = True
                break

    hit1 = [kw for kw in item["key1"] if normalize(kw) in text]
    hit2 = [kw for kw in item["key2"] if normalize(kw) in text]

    # 掉進陷阱且沒給出正解, 直接 0 分
    if trapped and not hit1:
        return 0.0, {"hit1": [], "hit2": hit2, "trapped": True}

    score = 0.0
    if hit1:
        score += 0.5
    if hit2:
        score += 0.5

    return score, {"hit1": hit1, "hit2": hit2, "trapped": trapped}