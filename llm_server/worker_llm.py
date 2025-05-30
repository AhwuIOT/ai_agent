import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from rq import SimpleWorker, Queue, Connection
from rq.timeouts import BaseDeathPenalty
import redis

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

class DummyDeathPenalty(BaseDeathPenalty):
    def setup_death_penalty(self):
        pass
    def cancel_death_penalty(self):
        pass

if __name__ == "__main__":
    redis_conn = redis.Redis(host="localhost", port=16379, db=0)
    with Connection(redis_conn):
        queue = Queue("model_job_queue")
        worker = SimpleWorker([queue], connection=redis_conn)
        worker.death_penalty_class = DummyDeathPenalty
        print("🚀 SimpleWorker 正在啟動...")
        worker.work()
