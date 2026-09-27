"""
OpenRouter API 封裝
提供統一的模型呼叫介面, 並記錄耗時與 token 用量
"""

import os
import time
import requests
from dotenv import load_dotenv

# 從 .env 讀取 API key, 避免硬編碼在程式中
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise ValueError("找不到 OPENROUTER_API_KEY, 請確認 .env 檔案存在")

BASE_URL = "https://openrouter.ai/api/v1"


def ask(model, prompt, system=None, timeout=120):
    """
    向指定模型提問

    參數:
      model   : 模型代號, 例如 "mistralai/mistral-7b-instruct"
      prompt  : 使用者的問題
      system  : 系統提示詞, 用來指定回答格式或角色
      timeout : 最長等待秒數

    回傳 dict:
      ok      : 是否成功
      text    : 模型的回覆內容
      elapsed : 耗時 (秒)
      tokens  : 總 token 用量
    """
    # 組裝對話訊息
    # system 角色用來給模型指示, user 角色是實際問題
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    t0 = time.time()

    try:
        r = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"model": model, "messages": messages},
            timeout=timeout,
        )
        elapsed = time.time() - t0
        data = r.json()

        # API 可能回傳錯誤物件而非正常回覆, 需先檢查
        if "error" in data:
            return {"ok": False, "text": str(data["error"]),
                    "elapsed": elapsed, "tokens": 0}

        return {
            "ok": True,
            "text": data["choices"][0]["message"]["content"],
            "elapsed": elapsed,
            "tokens": data.get("usage", {}).get("total_tokens", 0),
        }

    except Exception as e:
        # 網路逾時或其他例外
        return {"ok": False, "text": f"Exception: {e}",
                "elapsed": time.time() - t0, "tokens": 0}


def list_free_models():
    """
    取得 OpenRouter 上所有免費模型的清單
    免費的定義是 prompt 和 completion 價格都是 0
    """
    
    r = requests.get(f"{BASE_URL}/models", timeout=30)
    models = r.json()["data"]

    # 把不用免費的模型都存起來
    free = [
        m for m in models
        if m["pricing"]["prompt"] == "0" and m["pricing"]["completion"] == "0"
    ]

    # 依 context 長度由大到小排序, 通常越大代表模型越新或越強
    return sorted(free, key=lambda m: -m["context_length"])