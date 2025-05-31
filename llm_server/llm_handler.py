import os
import requests
import base64
import json
from typing import Optional
from pydantic import BaseModel

class LLMRequest(BaseModel):
    text: str
    mode: str
    model: Optional[str] = "lmstudio-community/gemma-3-12B-it-qat-GGUF"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024

def generate_prompt_long_speech(text):
    return f"""
        以下是一段由語音轉換而來的中文文字，但語句結構可能不完整或有錯字，請你幫我將它還原成一段通順的語句。

            原文：
            {text}

            請只回傳還原後的內容，不用說明。
        """
def call_lmstudio(req: LLMRequest):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('LOCAL_LLM_API_KEY', 'none')}"
    }
    url = "http://localhost:1234/v1/chat/completions"

    if req.mode == "long_speech":
        prompt = generate_prompt_long_speech(req.text)
        try:
            data = {
                "model": req.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a language expert who can polish what you hear into a suitable sentence. Please do not translate it"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": req.temperature,
                "max_tokens": req.max_tokens
            }
            response = requests.post(url=url, headers=headers, json=data)
            result = response.json()
            result = result["choices"][0]["message"]["content"].strip()
            return result
        except Exception as e:
            print(f"❌ long_speech 模式失敗：{e}")
            return "error"
        
    
    elif req.mode == "count_people":
        try:
            with open(req.text, "rb") as image_file:
                base64_str = base64.b64encode(image_file.read()).decode("utf-8")
                image_data_url = f"data:image/png;base64,{base64_str}"
                payload = {
                    "model": req.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "How many people? Just give me a number."},
                                {"type": "image_url", "image_url": {"url": image_data_url}}
                            ]
                        }
                    ],
                    "temperature": req.temperature,
                    "max_tokens": req.max_tokens,
                    "stream": False
                }
                
                response = requests.post(url, headers=headers, data=json.dumps(payload))

                result = response.json()["choices"][0]["message"]["content"].strip()
                
                return result
        except Exception as e:
            print(f"❌ count_people 模式失敗：{e}")
            return "error"
        finally:
            if os.path.exists(req.text):
                try:
                    os.remove(req.text)
                    print(f"🗑️ 已刪除檔案：{req.text}")
                except Exception as e:
                    print(f"⚠️ 刪除失敗：{e}")
            

    return "unknown"

def call_lmstudio_job(raw_dict):
    req = LLMRequest(**raw_dict)
    return call_lmstudio(req)


if __name__ == "__main__":
    req = LLMRequest(
        text="images/20250529_185657.jpg",
        mode="count_people")
    result = call_lmstudio_job(req.model_dump())
    
    print(f"Result: {result}")