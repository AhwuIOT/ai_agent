import requests
import concurrent.futures
import time
import random

AUDIO_PATH = "recordings/record_20250529_173349.wav"
IMAGE_PATH = "images/20250529_214712.jpg"
NUM_JOBS = 10  # 同時任務數量

def send_transcribe():
    with open(AUDIO_PATH, "rb") as audio_file:
        files = {"audio": ("record.wav", audio_file, "audio/wav")}
        response = requests.post("http://localhost:5000/transcribe", files=files)
        if response.status_code == 200:
            job_id = response.json()["job_id"]
            print(f"📤 語音任務送出成功：{job_id}")
            return job_id
        else:
            print(f"❌ 語音任務送出失敗：{response.status_code}")
            return None

def send_llm():
    with open(IMAGE_PATH, "rb") as image_file:
        files = {"image": ("image.jpg", image_file, "image/jpeg")}
        data = {"mode": "count_people"}
        response = requests.post("http://localhost:5000/ask", files=files, data=data)

    if response.status_code == 200:
        job_id = response.json()["job_id"]
        print(f"📤 LLM任務送出成功：{job_id}")
        return job_id
    else:
        print(f"❌ LLM任務送出失敗：{response.status_code}")
        return None

def poll_result(job_id):
    for _ in range(60):
        res = requests.get(f"http://localhost:5000/result/{job_id}")
        status = res.json()["status"]
        if status == "done":
            print(f"✅ 完成：{job_id} → {res.json()['result']}")
            return
        elif status == "failed":
            print(f"❌ 失敗：{job_id}")
            return
        time.sleep(1)
    print(f"⏰ 超時：{job_id}")

if __name__ == "__main__":
    jobs = []

    # 任意混合語音與LLM任務
    for _ in range(NUM_JOBS):
        if random.random() < 0.5:
            jobs.append(send_transcribe)
        else:
            jobs.append(send_llm)

    # 發送所有任務
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_JOBS) as executor:
        futures = [executor.submit(job) for job in jobs]
        job_ids = [f.result() for f in concurrent.futures.as_completed(futures) if f.result()]

    # 查詢所有結果
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_JOBS) as executor:
        executor.map(poll_result, job_ids)
