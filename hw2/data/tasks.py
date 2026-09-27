"""
評測題庫
四種任務, 題目取自真實競程情境, 皆附標準答案以便客觀計分

Task A-C 為基礎題, 驗證模型對常見演算法的掌握
Task D 為進階題, 需要組合多種技巧或辨識陷阱, 用於拉開鑑別度
"""

# ──────────────────────────────────────────────────────────
# 任務 A: 題目標籤分類
# 給定題目敘述, 判斷屬於哪一類演算法
# 標準答案參考 Codeforces 官方 tag
# ──────────────────────────────────────────────────────────

TASK_A = [
    {
        "id": "A1",
        "desc": "給定一個長度 n 的陣列, 求最長的連續子陣列使其和不超過 K",
        "answer": "two pointers",
        "accept": ["two pointers", "two-pointer", "sliding window",
                   "雙指針", "双指针", "滑動視窗", "滑动窗口"],
    },
    {
        "id": "A2",
        "desc": "給定 n 個物品, 每個有重量和價值, 背包容量為 W, 求最大價值",
        "answer": "dp",
        "accept": ["dp", "dynamic programming", "動態規劃", "动态规划",
                   "knapsack", "背包"],
    },
    {
        "id": "A3",
        "desc": "給定一棵樹和 q 筆詢問, 每筆詢問兩個節點的最近共同祖先",
        "answer": "lca",
        "accept": ["lca", "binary lifting", "倍增", "二進位提升",
                   "最近共同祖先", "最近公共祖先", "tree"],
    },
    {
        "id": "A4",
        "desc": "有 n 個城市和 m 條雙向道路, 每條有長度, 求城市 1 到城市 n 的最短距離",
        "answer": "shortest path",
        "accept": ["dijkstra", "shortest path", "最短路", "graph", "圖論", "图论"],
    },
    {
        "id": "A5",
        "desc": "維護一個陣列, 支援區間加值和區間求和兩種操作, 各最多 10^5 次",
        "answer": "segment tree",
        "accept": ["segment tree", "線段樹", "线段树", "bit", "fenwick",
                   "樹狀陣列", "树状数组", "區間樹", "区间树", "data structure"],
    },
]

# ──────────────────────────────────────────────────────────
# 任務 B: 程式碼除錯
# 給定有 bug 的 code, 找出問題所在
# bug 都是競程常見的經典錯誤
# ──────────────────────────────────────────────────────────

TASK_B = [
    {
        "id": "B1",
        "code": """int sum = 0;
for (int i = 1; i <= n; i++) {
    sum += a[i] * a[i];
}
cout << sum;""",
        "bug": "整數溢位",
        "accept": ["overflow", "溢位", "溢出", "long long",
                   "int 範圍", "int 范围", "int64", "64 位", "64位"],
        "hint": "a[i] 最大 10^9, n 最大 10^5",
    },
    {
        "id": "B2",
        "code": """sort(v.begin(), v.end());
for (int i = 0; i < v.size() - 1; i++) {
    if (v[i] == v[i+1]) cnt++;
}""",
        "bug": "v 為空時 v.size()-1 會下溢",
        "accept": ["empty", "空", "size()", "unsigned",
                   "下溢", "underflow", "無符號", "无符号"],
        "hint": "v 可能是空的",
    },
    {
        "id": "B3",
        "code": """int binary_search(int l, int r, int target) {
    while (l < r) {
        int mid = (l + r) / 2;
        if (a[mid] < target) l = mid;
        else r = mid;
    }
    return l;
}""",
        "bug": "l = mid 造成無窮迴圈",
        "accept": ["infinite", "無窮", "无穷", "無限", "无限",
                   "死循環", "死循环", "l = mid + 1", "mid+1", "永久"],
        "hint": "當 l 和 r 相鄰時會發生什麼",
    },
    {
        "id": "B4",
        "code": """void dfs(int u) {
    for (int v : adj[u]) {
        dfs(v);
    }
}""",
        "bug": "沒有 visited 標記, 有環時會無窮遞迴",
        "accept": ["visited", "cycle", "環", "环", "無窮遞迴", "无穷递归",
                   "stack overflow", "標記", "标记"],
        "hint": "圖可能有環",
    },
    {
        "id": "B5",
        "code": """map<int, int> mp;
for (int i = 0; i < n; i++) {
    mp[a[i]]++;
}
for (auto it = mp.begin(); it != mp.end(); it++) {
    if (it->second == 1) mp.erase(it);
}""",
        "bug": "erase 後 iterator 失效",
        "accept": ["iterator", "失效", "invalidate", "erase", "it++",
                   "迭代器", "未定義", "未定义"],
        "hint": "erase 之後 it 還能用嗎",
    },
]

# ──────────────────────────────────────────────────────────
# 任務 C: 解題思路
# 給定題目, 看模型能否想出正確的演算法方向
# 評分: 演算法關鍵字 0.7 分 + 正確複雜度 0.3 分
# ──────────────────────────────────────────────────────────

TASK_C = [
    {
        "id": "C1",
        "problem": "給定 n (n <= 10^5) 個區間, 選出最多的互不重疊區間",
        "key": ["greedy", "貪心", "贪心", "sort", "排序", "右端點", "右端点", "end"],
        "complexity": "O(n log n)",
    },
    {
        "id": "C2",
        "problem": "給定長度 n (n <= 2*10^5) 的陣列, 求有多少對 (i, j) 使得 i < j 且 a[i] > a[j]",
        "key": ["逆序對", "逆序对", "inversion", "merge sort", "合併排序", "归并排序",
                "bit", "樹狀陣列", "树状数组", "fenwick"],
        "complexity": "O(n log n)",
    },
    {
        "id": "C3",
        "problem": "n 個點 m 條邊的無向圖, 判斷是否存在一條路徑經過每條邊恰好一次",
        "key": ["euler", "歐拉", "欧拉", "度數", "度数", "degree", "連通", "连通"],
        "complexity": "O(n + m)",
    },
]

# ──────────────────────────────────────────────────────────
# 任務 D: 進階題
# Task A-C 的鑑別度不足 (三個模型在 B 全數滿分)
# 原因是那些都是訓練資料中的常見模板題
# Task D 設計三類難度來源:
#   D1 D2  需要組合兩種以上技巧
#   D3 D4  陷阱題, 看起來像經典題但套模板會錯
#   D5     程式碼正確但複雜度不符題目限制
# 評分: 需同時命中 key1 與 key2 才滿分, 只中一半得 0.5
# ──────────────────────────────────────────────────────────

TASK_D = [
    {
        "id": "D1",
        "type": "combo",
        "problem": "給定 n <= 2*10^5 個點的樹, 每個點有權值。"
                   "q <= 2*10^5 筆詢問, 每筆給 (u, v, k), "
                   "求 u 到 v 路徑上第 k 小的權值。",
        # 需要同時想到可持久化資料結構與 LCA, 缺一不可
        "key1": ["主席樹", "主席树", "persistent", "可持久化",
                 "chairman", "persistent segment tree"],
        "key2": ["lca", "倍增", "binary lifting", "最近公共祖先", "最近共同祖先"],
        "note": "可持久化線段樹 + LCA, 兩者缺一不可",
    },
    {
        "id": "D2",
        "type": "combo",
        "problem": "給定長度 n <= 10^5 的字串 s 和 m <= 10^5 個模式串, "
                   "所有模式串總長 <= 10^6。"
                   "求每個模式串在 s 中出現幾次。",
        # 單用 KMP 逐一比對是 O(nm) 會 TLE, 要用 AC 自動機
        "key1": ["ac自動機", "ac自动机", "aho-corasick", "aho corasick", "ac 自動機"],
        "key2": ["trie", "字典樹", "字典树", "fail", "失配"],
        "note": "AC 自動機, 單用 KMP 會 TLE",
    },
    {
        "id": "D3",
        "type": "trap",
        "problem": "給定 n <= 40 個物品, 每個有重量 w[i] 和價值 v[i], "
                   "背包容量 W <= 10^18, 求不超過容量的最大價值。",
        # 陷阱: 看起來是背包 DP, 但 W 高達 10^18 無法開陣列
        # 正解是 meet in the middle, 利用 n 很小的特性
        "key1": ["meet in the middle", "折半", "折半搜索", "雙向搜尋",
                 "双向搜索", "2^(n/2)", "2^20"],
        "key2": ["排序", "sort", "二分", "binary search", "雙指針", "双指针"],
        "trap_answer": ["動態規劃", "动态规划", "dp", "背包dp"],
        "note": "陷阱題: 答 DP 即中陷阱, W 太大無法開陣列",
    },
    {
        "id": "D4",
        "type": "trap",
        "problem": "給定 n <= 10^5 個正整數, 求最大的子集合使得子集合內"
                   "任兩數的最大公因數都大於 1。",
        # 陷阱: 直觀想法是建圖跑最大團, 但那是 NP-hard
        # 正解是質因數分解 + 並查集或 DP, 利用數字範圍有限
        "key1": ["質因數", "质因数", "prime", "因數分解", "因数分解", "篩法", "筛法"],
        "key2": ["並查集", "并查集", "union find", "dsu", "dp", "動態規劃"],
        "trap_answer": ["最大團", "最大团", "maximum clique", "建圖", "建图"],
        "note": "陷阱題: 答最大團即中陷阱, 那是 NP-hard",
    },
    {
        "id": "D5",
        "type": "complexity",
        "code": """// n <= 10^5, Q <= 10^5, 時限 1 秒
for (int q = 0; q < Q; q++) {
    int l, r;
    cin >> l >> r;
    int mx = 0;
    for (int i = l; i <= r; i++)
        mx = max(mx, a[i]);
    cout << mx << "\\n";
}""",
        # 程式邏輯完全正確, 問題在於複雜度不符題目限制
        # 測試模型會不會只檢查語法錯誤而忽略效率
        "key1": ["tle", "超時", "超时", "複雜度", "复杂度",
                 "o(nq)", "o(n*q)", "時間限制", "时间限制", "太慢"],
        "key2": ["sparse table", "st表", "st 表", "線段樹", "线段树",
                 "segment tree", "稀疏表", "rmq"],
        "note": "程式碼正確但 O(nQ) 會 TLE, 需要 sparse table 或線段樹",
    },
]