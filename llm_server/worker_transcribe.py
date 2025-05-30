import os
import sys

sys.path.append(os.path.abspath("."))
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from rq import SimpleWorker, Queue, Connection
from rq.timeouts import BaseDeathPenalty
import redis

class DummyDeathPenalty(BaseDeathPenalty):
    def setup_death_penalty(self):
        pass
    def cancel_death_penalty(self):
        pass

if __name__ == "__main__":
    redis_conn = redis.Redis(host="localhost", port=16379, db=0)
    with Connection(redis_conn):
        queue = Queue("transcribe")
        worker = SimpleWorker([queue], connection=redis_conn)
        worker.death_penalty_class = DummyDeathPenalty
        print("🚀 SimpleWorker 正在啟動...")
        worker.work()
