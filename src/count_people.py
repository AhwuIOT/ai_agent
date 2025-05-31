# from .llm_handler import match_intent
from .capture_photo import capture_image_from_ffmpeg
from dotenv import load_dotenv
import requests
import time
load_dotenv()
import os
URL = os.getenv("API_URL")

    # prediction = match_intent(file_path, "count_people")
    # print(prediction)

def send_llm(IMAGE_PATH):
    with open(IMAGE_PATH, "rb") as image_file:
        files = {"image": ("image.jpg", image_file, "image/jpeg")}
        data = {"mode": "count_people"}
        response = requests.post(f"{URL}/ask", files=files, data=data)

    if response.status_code == 200:
        job_id = response.json()["job_id"]
        print(f"📤 LLM任務送出成功：{job_id}")
        return job_id
    else:
        print(f"❌ LLM任務送出失敗：{response.status_code}")
        return None

def poll_result(job_id):
    for _ in range(60):
        res = requests.get(f"{URL}/result/{job_id}")
        status = res.json()["status"]
        if status == "done":
            print(f"✅ 完成：{job_id} → {res.json()['result']}")
            return
        elif status == "failed":
            print(f"❌ 失敗：{job_id}")
            return
        time.sleep(1)
    print(f"⏰ 超時：{job_id}")

def capture_and_count_people():
    file_path = capture_image_from_ffmpeg(camera_name="USB2.0 PC CAMERA", save_dir="images")
    send_llm(file_path)
    job_id = send_llm(file_path)
    if job_id:  
        poll_result(job_id)


if __name__ == "__main__":
    capture_and_count_people()