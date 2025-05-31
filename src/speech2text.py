# from faster_whisper import WhisperModel
import speech_recognition as sr
import requests
import os
from dotenv import load_dotenv
import time
load_dotenv()
URL = os.getenv("API_URL") 
# 初始化 Faster-Whisper 模型
# model = WhisperModel("base", device="cpu", compute_type="int8")  

# # 使用 Whisper 模型轉換文字
# def transcribe_audio(file_path):
#     print("🧠 開始語音辨識...")
#     segments, _ = model.transcribe(file_path, beam_size=5)
#     full_text = "".join([seg.text for seg in segments])
#     # print("📝 原始輸出：", full_text)
#     return full_text
def send_transcribe(AUDIO_PATH):
    with open(AUDIO_PATH, "rb") as audio_file:
        files = {"audio": ("record.wav", audio_file, "audio/wav")}
        response = requests.post(f"{URL}/transcribe", files=files)
        if response.status_code == 200:
            job_id = response.json()["job_id"]
            print(f"📤 語音任務送出成功：{job_id}")
            return job_id
        else:
            print(f"❌ 語音任務送出失敗：{response.status_code}")
            return None
        
def poll_result(job_id):
    for _ in range(20):
        res = requests.get(f"{URL}/result/{job_id}")
        status = res.json()["status"]
        if status == "done":
            print(f"✅ 完成：{job_id} → {res.json()['result']}")
            return res.json()['result']
        elif status == "failed":
            print(f"❌ 失敗：{job_id}")
            return
        time.sleep(1)
    print(f"⏰ 超時：{job_id}")

def transcribe_audio(file_path):
    send_transcribe(file_path)
    job_id = send_transcribe(file_path)
    if job_id:
        return poll_result(job_id) 


def send_llm_transcribe(text):
           
    data = {"mode": "instruction", "text": text}
    response = requests.post(f"{URL}/ask", data=data)

    if response.status_code == 200:
        job_id = response.json()["job_id"]
        print(f"📤 LLM任務送出成功：{job_id}")
        return job_id
    else:
        print(f"❌ LLM任務送出失敗：{response.status_code}")
        return None

    


def instruct_speech_to_text(file_path):
    # 建立辨識器與麥克風來源
    
    recognizer = sr.Recognizer()

    with sr.AudioFile(file_path) as source:
        print("🔊 載入音訊中...")
        audio = recognizer.record(source)

    print("🧠 開始語音辨識...")
    try:
        text = recognizer.recognize_google(audio, language="zh-TW")
        print("✅ 辨識結果：", text)
        job_id = send_llm_transcribe(text)
        print("🔗 LLM任務 ID：", job_id)
        if job_id:
            return poll_result(job_id) 
            
        return text
    except sr.UnknownValueError:
        print("❌ 無法辨識語音")
        return ""
    except sr.RequestError as e:
        print(f"❌ 語音 API 發生錯誤：{e}")
        return ""
    
if __name__ == "__main__":
    AUDIO_PATH = "recordings/record.wav"
    # text = transcribe_audio(AUDIO_PATH)
    text = instruct_speech_to_text(AUDIO_PATH)
    print("📝 最終辨識文字：", text)