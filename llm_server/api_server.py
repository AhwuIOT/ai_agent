from fastapi import FastAPI, UploadFile, File, HTTPException
from rq import Queue
from rq.job import Job
import redis
import os
from .transcriber import transcribe_audio
from .llm_handler import call_lmstudio_job, LLMRequest

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
    path = os.path.join("uploads", audio.filename)
    with open(path, "wb") as buffer:
        buffer.write(await audio.read())

    job = transcribe_queue.enqueue(transcribe_audio, path)
    return {"job_id": job.get_id(), "type": "transcribe"}

# --------- LLM 模型請求 API ---------
@app.post("/ask")
def ask_model(req: LLMRequest):
    job = model_queue.enqueue(call_lmstudio_job, req.model_dump())
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
