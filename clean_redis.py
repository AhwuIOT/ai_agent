import schedule
import time
from rq.job import Job
from rq.registry import FinishedJobRegistry, FailedJobRegistry
from rq import Queue
import redis

# Redis 連線設定
redis_conn = redis.Redis(host="localhost", port=16379, db=0)

# 所有你有用的佇列名稱
QUEUE_NAMES = ["transcribe", "model_job_queue"]
DELETE_THRESHOLD_SECONDS = 600  # 刪除超過 10 分鐘的 job

def clean_jobs():
    for queue_name in QUEUE_NAMES:
        queue = Queue(queue_name, connection=redis_conn)

        # 清理已完成的任務
        finished_registry = FinishedJobRegistry(name=queue_name, connection=redis_conn)
        job_ids = finished_registry.get_job_ids()
        for job_id in job_ids:
            job = Job.fetch(job_id, connection=redis_conn)
            if job.ended_at and (time.time() - job.ended_at.timestamp()) > DELETE_THRESHOLD_SECONDS:
                job.delete()
                finished_registry.remove(job)

        # 清理已失敗的任務
        failed_registry = FailedJobRegistry(name=queue_name, connection=redis_conn)
        for job_id in failed_registry.get_job_ids():
            job = Job.fetch(job_id, connection=redis_conn)
            job.delete()
            failed_registry.remove(job)

        print(f"✅ 清理完成：{queue_name}，處理 {len(job_ids)} 筆完成任務")

# 每 10 分鐘跑一次
# schedule.every(10).minutes.do(clean_jobs)

# print("🚀 Redis 任務清理器已啟動，每 1 分鐘掃描一次")

clean_jobs()
    # schedule.run_pending()
    # time.sleep(1)
