from rq import Queue
from redis import Redis
from controllers.Repo_controller import upload_repo_on_qdrant
from rq.job import Job

redis_con = Redis(host="localhost", port=6379)
q = Queue("default", connection=redis_con)


def enqueue_upload_repo(url: str):
    job = q.enqueue(upload_repo_on_qdrant, url)
    print(f"Job queued successfully")
    print(f"Job ID: {job.id}")
    print(f"Current Queue Count: {q.count}")
    return job.id


def get_job_status(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_con)
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