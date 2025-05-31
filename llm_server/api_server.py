from fastapi import FastAPI, UploadFile, File, HTTPException,Form
from rq import Queue
import redis
import os
from .transcriber import transcribe_audio
from .llm_handler import call_lmstudio_job, LLMRequest
import uuid

filename = f"{uuid.uuid4().hex}.wav"
path = os.path.join("uploads", filename)

app = FastAPI()

# Redis 連線設定（共用同一個）
redis_conn = redis.Redis(host="localhost", port=16379, db=0)

# 任務佇列設定（可依類型拆開佇列名稱）
transcribe_queue = Queue("transcribe", connection=redis_conn)
model_queue = Queue("model_job_queue", connection=redis_conn)





# --------- 音檔上傳 + 語音辨識任務 ---------
@app.post("/transcribe")
async def handle_audio(audio: UploadFile = File(...)):
    if not audio:
        raise HTTPException(status_code=400, detail="需要 audio 音訊檔")

    os.makedirs("uploads", exist_ok=True)
    filename = f"{uuid.uuid4().hex}.wav"
    path = os.path.join("uploads", filename)

    content = await audio.read()
    if not content:
        raise HTTPException(status_code=400, detail="音訊內容為空")
    with open(path, "wb") as buffer:
        buffer.write(content)

    print(f"✅ 已儲存音訊檔：{path}")
    job = transcribe_queue.enqueue(transcribe_audio, path)
    return {"job_id": job.get_id(), "type": "transcribe"}

# --------- LLM 模型請求 API ---------
# @app.post("/ask")
# def ask_model(req: LLMRequest):
#     job = model_queue.enqueue(call_lmstudio_job, req.model_dump())
#     return {"job_id": job.get_id(), "type": "lmstudio"}



@app.post("/ask")
async def ask_model_v2(
    mode: str = Form("count_people"),  # 預設就是 count_people
    image: UploadFile = File(None),
    text: str = Form("")
):
    if mode == "count_people" and image is None:
        return {
            "status": "skipped",
            "reason": "🛑 預設模式為 count_people，但沒有提供圖片，因此已跳過任務"
        }
    else:
        image_path = None
        if image:
            if image.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(status_code=400, detail="❌ 不支援的圖片格式")

            os.makedirs("uploads", exist_ok=True)
            filename = f"{uuid.uuid4().hex}.jpg"
            image_path = os.path.join("uploads", filename)

            content = await image.read()
            with open(image_path, "wb") as f:
                f.write(content)

            print(f"✅ 已儲存圖片檔：{image_path}")

        request_payload = {
            "text": image_path if image_path else "",
            "mode": mode
        }

        job = model_queue.enqueue(call_lmstudio_job, request_payload)
        
    if mode == "instruction":
        request_payload = {
            "text": text if text else "",
            "mode": mode
        }

        job = model_queue.enqueue(call_lmstudio_job, request_payload)
    return {"job_id": job.get_id(), "type": "lmstudio"}

# --------- 共用查詢任務結果 API ---------
@app.get("/result/{job_id}")
def get_result(job_id: str):
    job = transcribe_queue.fetch_job(job_id) or model_queue.fetch_job(job_id)

    if job is None:
        return {"status": "not_found"}
    elif job.is_finished:
        return {"status": "done", "result": job.result}
    elif job.is_failed:
        return {"status": "failed"}
    return {"status": "processing"}
