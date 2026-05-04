from rq import Queue
from redis import Redis
from controllers.Repo_controller import upload_repo_on_qdrant


redis_con = Redis(host="localhost", port=6379)
q = Queue("default", connection=redis_con)


def enqueue_upload_repo(url: str):
    job = q.enqueue(upload_repo_on_qdrant, url)
    print(f"Job queued successfully")
    print(f"Job ID: {job.id}")
    print(f"Current Queue Count: {q.count}")
    return job.id




# rq worker --worker-class rq.worker.SimpleWorker