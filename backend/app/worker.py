from rq import Worker
from .db import init_db
from .services.job_queue import get_queue

if __name__ == "__main__":
    init_db()
    queue = get_queue()
    worker = Worker([queue], connection=queue.connection)
    worker.work()
