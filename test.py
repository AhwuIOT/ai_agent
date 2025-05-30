from fastapi import FastAPI
from pydantic import BaseModel
from rq import Queue
import redis
import requests

app = FastAPI()

# Redis 設定
redis_conn = redis.Redis(host="localhost", port=16379, db=0)
q = Queue("model_job_queue", connection=redis_conn)

# 輸入模型格式
class PromptRequest(BaseModel):
    prompt: str

# 呼叫 LMStudio 的函數
def call_lmstudio(prompt):
    url = "http://localhost:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "google/gemma-3-12b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    res = requests.post(url, headers=headers, json=data)
    return res.json()["choices"][0]["message"]["content"]

# 建立任務
@app.post("/ask")
def ask_model(req: PromptRequest):
    job = q.enqueue(call_lmstudio, req.prompt)
    return {"job_id": job.id}

# 查詢結果
@app.get("/result/{job_id}")
def get_result(job_id: str):
    job = q.fetch_job(job_id)
    if job is None:
        return {"status": "not_found"}
    elif job.is_finished:
        return {"status": "done", "result": job.result}
    elif job.is_failed:
        return {"status": "failed"}
    return {"status": "processing"}
