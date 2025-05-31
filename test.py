from fastapi.testclient import TestClient
from llm_server import api_server
import os
import time

client = TestClient(api_server.app)

def send_transcribe_job(audio_path):
    assert os.path.exists(audio_path), f"檔案不存在：{audio_path}"
    with open(audio_path, "rb") as audio_file:
        files = {"audio": ("record.wav", audio_file, "audio/wav")}
        response = client.post("/transcribe", files=files)
    res_json = response.json()
    print("📤 音檔送出回應：", res_json)
    return res_json["job_id"]

def send_llm_job(image_path):
    assert os.path.exists(image_path), f"圖片不存在：{image_path}"
    payload = {
        "text": image_path,
        "mode": "count_people"
    }
    response = client.post("/ask", json=payload)
    res_json = response.json()
    print("📤 圖片分析任務送出：", res_json)
    return res_json["job_id"]

def wait_for_result(job_id, timeout_sec=15):
    for _ in range(timeout_sec):
        res = client.get(f"/result/{job_id}").json()
        status = res["status"]
        print(f"🔍 任務狀態：{status}")
        if status == "done":
            return res["result"]
        elif status == "failed":
            raise RuntimeError("❌ 任務執行失敗")
        time.sleep(1)
    raise TimeoutError("⌛ 任務逾時未完成")

# 🚀 主程式測試
if __name__ == "__main__":
    # ✅ 1. 測試語音轉文字 + 修辭
    audio_job_id = send_transcribe_job("recordings/test.mp3")
    audio_result = wait_for_result(audio_job_id)
    print("📝 語音最終文字結果：", audio_result)

    # ✅ 2. 測試圖片人數辨識
    image_job_id = send_llm_job("images/20250529_214712.jpg")
    image_result = wait_for_result(image_job_id)
    print("🧍‍♂️ 圖片人數分析結果：", image_result)
