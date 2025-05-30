from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from rq import Queue
from rq.job import Job
import redis
import os
from transcriber import transcribe_audio

app = FastAPI()
redis_conn = redis.Redis(host="localhost", port=16379, db=0)
q = Queue("transcribe", connection=redis_conn)

@app.post("/transcribe")
async def handle_audio(audio: UploadFile = File(...)):
    if not audio:
        raise HTTPException(status_code=400, detail="需要 audio 音訊檔")

    os.makedirs("uploads", exist_ok=True)
    path = os.path.join("uploads", audio.filename)
    with open(path, "wb") as buffer:
        buffer.write(await audio.read())

    job = q.enqueue(transcribe_audio, path)
    return {"job_id": job.get_id()}

@app.get("/result/{job_id}")
def get_result(job_id: str):
    job: Job = q.fetch_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="任務不存在")
    if job.is_finished:
        return {"status": "finished", "text": job.result}
    elif job.is_failed:
        return {"status": "failed"}
    else:
        return {"status": "processing"}
