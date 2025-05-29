import os
import requests
import base64
import json
# 共用 prompt 生成函數
def generate_prompt_instruct(text):
    return f"""
        你是一個語意分類助手，請你根據使用者輸入的內容，判斷他想要執行哪一種功能。
        以下是功能與對應的語意範例：

        1. 播放聲音（play_sound）：例如「播放聲音」、「讓喇叭響一下」、「播個音效」
        2. 語音轉文字（record）：例如「語音轉文字」、「STT」、「開始錄音並轉成文字」
        3. 相機辨識人數（camera）：例如「現場人數」、「鏡頭中有幾個人」、「偵測鏡頭中的人數」

        使用者說了這句話：
        「{text}」

        請你判斷他想要的功能，並回傳下列三個字串之一："play_sound"、"record"、"camera"。
        若無法判斷請回傳 "unknown"。請只回傳上述其中一個字串，不要多加說明。
        """

def generate_prompt_long_speech(text):
    return f"""
        以下是一段由語音轉換而來的中文文字，但語句結構可能不完整或有錯字，請你幫我將它還原成一段通順的語句。

            原文：
            {text}

            請只回傳還原後的內容，不用說明。
        """

# 主函式：呼叫本地 LLM（OpenAI API 相容）
def match_intent(text, mode):
    headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.getenv('LOCAL_LLM_API_KEY', 'none')}"  # 若沒用 auth 可略過驗證
            }
    url = "http://127.0.0.1:1234/v1/chat/completions"
    if mode == "instruction":
        prompt = generate_prompt_instruct(text)
        try:

            data = {
                "model": "lmstudio-community/gemma-3-12B-it-qat-GGUF",  # 可寫成你自己模型的名稱（如 "gpt-3.5-turbo"）
                "messages": [
                    {"role": "system", "content": "你是一個語意分類助手。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0,
                "max_tokens": 64
            }

            response = requests.post(url=url,headers=headers, json=data, timeout=10)
            result = response.json()
            reply = result["choices"][0]["message"]["content"].strip().lower()
            if reply in ["play_sound", "record", "camera"]:
                return reply
        except Exception as e:
            print(f"❌ 本地 LLM API 失敗：{e}")
    elif mode == "long_speech":
        prompt = generate_prompt_long_speech(text)
        try:

            data = {
                "model": "lmstudio-community/gemma-3-12B-it-qat-GGUF",  # 可寫成你自己模型的名稱（如 "gpt-3.5-turbo"）
                "messages": [
                    {"role": "system", "content": "You are a language expert who can polish what you hear into a suitable sentence. Please do not translate it"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0,
                "max_tokens": 8192
            }

            response = requests.post(url=url,headers=headers, json=data)
            result = response.json()
            reply = result["choices"][0]["message"]["content"]
            return reply
        except Exception as e:
            print(f"❌ 本地 LLM API 失敗：{e}")
    elif mode == "count_people":
        IMAGE_PATH = text
        try:
            with open(IMAGE_PATH, "rb") as image_file:
                base64_str = base64.b64encode(image_file.read()).decode("utf-8")
                image_data_url = f"data:image/png;base64,{base64_str}"
                payload = {
                "model": "ibm-granite_granite-vision-3.2-2b",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "How many people?Just give me a number."},
                            {"type": "image_url", "image_url": {"url": image_data_url}}
                        ]
                    }
                ],
                "temperature": 0.7,
                "max_tokens": -1,
                "stream": False
            }

                # 發送 POST 請求
                headers = {"Content-Type": "application/json"}
                response = requests.post(url=url, headers=headers, data=json.dumps(payload))
                return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"❌ 本地 LLM API 失敗：{e}")

    return "unknown"
