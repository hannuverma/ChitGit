from controllers.Repo_controller import upload_repo_on_qdrant

# Lazy import and initialization to avoid failing at module import time
_redis_con = None
_queue = None

def _get_redis_con():
    global _redis_con
    if _redis_con is None:
        from redis import Redis
        from config.config import REDIS_URL
        if REDIS_URL:
            _redis_con = Redis.from_url(REDIS_URL)
        else:
            _redis_con = Redis()
    return _redis_con

def _get_queue():
    global _queue
    if _queue is None:
        from rq import Queue
        _queue = Queue("default", connection=_get_redis_con())
    return _queue


def enqueue_upload_repo(url: str):
    q = _get_queue()
    job = q.enqueue(upload_repo_on_qdrant, url)
    print(f"Job queued successfully")
    print(f"Job ID: {job.id}")
    try:
        count = q.count
    except Exception:
        count = None
    print(f"Current Queue Count: {count}")
    return job.id


def get_job_status(job_id: str):
    try:
        from rq.job import Job
        job = Job.fetch(job_id, connection=_get_redis_con())
        return {
            "job_id": job.id,
            "status": job.get_status(),
            "result": job.result,
        }
    except Exception as e:
        return {
            "error": str(e)
        }


# rq worker --worker-class rq.worker.SimpleWorker